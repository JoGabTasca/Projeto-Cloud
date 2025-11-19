#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ALTERA PARA PEGAR SOMENTE DADOS DO PREGAO A VISTA - pegar a tag correta e carregar no banco de dados somente esses dados

from datetime import datetime, date
from decimal import Decimal, InvalidOperation
from io import BytesIO
import os
from typing import List, Dict, Optional

from lxml import etree
import logging
import re
from .db_write import persist_quotes
import time

import azure.storage.blob as BlobServiceClient

TICKER_REGEX = re.compile(r"^[A-Z]{4}[0-9]{1,2}$")
AZURE_CONNECTION_STRING = "DefaultEndpointsProtocol=https;AccountName=etlfunctioncloud;AccountKey=Q9nVeCulA2zhQ1VR4cIdKYiK1aM4Vr4fXN4+dVs5NoKBr8HvdFOtxfWRaCOeFJ495J6CHCHju6Ar+AStAw39pg==;EndpointSuffix=core.windows.net"

def eh_mercado_a_vista(ticker: str) -> bool:
    """Retorna True apenas para tickers no formato 4 letras + 1 ou 2 dígitos."""
    if not ticker:
        return False
    return bool(TICKER_REGEX.match(ticker.strip().upper()))

def to_decimal(x) -> Optional[Decimal]:
    if x is None:
        return None
    s = str(x).strip().replace(",", ".")
    if not s:
        return None
    try:
        return Decimal(s)
    except (InvalidOperation, ValueError):
        return None

def to_date(s: str) -> date:
    if "T" in s:
        s = s.split("T", 1)[0]
    return datetime.strptime(s, "%Y-%m-%d").date()

def parse_pricrpt(xml_bytes: bytes) -> List[Dict]:
    """Extrai 1 linha por <PricRpt> (namespace-agnóstico).
    FILTRA APENAS MERCADO À VISTA (TpMerc = 010).
    """
    tree = etree.parse(BytesIO(xml_bytes), etree.XMLParser(recover=True, huge_tree=True))
    pricrpts = tree.xpath('//*[local-name()="PricRpt"]')

    def first_text(node, xp: str) -> str:
        v = node.xpath(xp)
        if isinstance(v, list):
            v = v[0] if v else ""
        return (v or "").strip()

    rows: List[Dict] = []
    total_pricrpts = len(pricrpts)
    mercado_vista_count = 0
    ticker_format_count = 0
    
    for pr in pricrpts:
        # Extrai o tipo de mercado - pode estar em diferentes tags
        # Tentando várias possibilidades: MktTp, TpMerc, MktTpCd, etc.
        tp_merc = first_text(pr, './/*[local-name()="MktTp"][1]/text()') \
                 or first_text(pr, './/*[local-name()="TpMerc"][1]/text()') \
                 or first_text(pr, './/*[local-name()="MktTpCd"][1]/text()') \
                 or first_text(pr, './/*[local-name()="MktTp"][1]/*[local-name()="Cd"][1]/text()')
        
        # Filtra apenas mercado à vista (010)
        # Se não encontrar a tag, também aceita (pode ser que alguns XMLs não tenham)
        if tp_merc and tp_merc not in ['010', '10']:
            continue
        
        mercado_vista_count += 1
        
        ativo = first_text(pr, './/*[local-name()="TckrSymb"][1]/text()')
        dt    = first_text(pr, './/*[local-name()="TradDt"]/*[local-name()="Dt"][1]/text()') \
                or first_text(pr, './/*[local-name()="TradDt"][1]/text()')
        if not (ativo and dt):
            continue
        if not eh_mercado_a_vista(ativo):
            continue
        ticker_format_count += 1

        abertura   = to_decimal(first_text(pr, './/*[local-name()="FrstPric"][1]/text()'))
        fechamento = to_decimal(first_text(pr, './/*[local-name()="LastPric"][1]/text()'))
        precomin   = to_decimal(first_text(pr, './/*[local-name()="MinPric"][1]/text()'))
        precomax   = to_decimal(first_text(pr, './/*[local-name()="MaxPric"][1]/text()'))
        volume     = to_decimal(first_text(pr, './/*[local-name()="NtlFinVol"][1]/text()'))

        rows.append({
            "Ativo": ativo,
            "DataPregao": to_date(dt),
            "Abertura": abertura,
            "Fechamento": fechamento,
            "PrecoMin": precomin,
            "PrecoMax": precomax,
            "Volume": volume
        })
    
    logging.info(f"[INFO] Total de PricRpt encontrados: {total_pricrpts}")
    logging.info(f"[INFO] Registros de mercado à vista (010): {mercado_vista_count}")
    logging.info(f"[INFO] Registros com ticker formato vista: {ticker_format_count}")
    logging.info(f"[INFO] Registros válidos após filtro: {len(rows)}")
    print(f"[INFO] Total de PricRpt encontrados: {total_pricrpts}")
    print(f"[INFO] Registros de mercado à vista (010): {mercado_vista_count}")
    print(f"[INFO] Registros com ticker formato vista: {ticker_format_count}")
    print(f"[INFO] Registros válidos após filtro: {len(rows)}")
    
    return rows

def _get_connection_string():
    conn = os.getenv("AZURE_CONNECTION_STRING") or os.getenv("AzureWebJobsStorage")
    if not conn:
        # Fallback para connection string hardcoded (desenvolvimento local)
        conn = AZURE_CONNECTION_STRING
    if not conn:
        raise RuntimeError(
            "Defina AZURE_CONNECTION_STRING (ou AzureWebJobsStorage) para acessar o Blob Storage."
        )
    return conn


def _get_container_client():
    container_name = os.getenv("BLOB_CONTAINER_NAME") or "b3-dados-brutos"
    service = BlobServiceClient.BlobServiceClient.from_connection_string(
        _get_connection_string()
    )
    return service.get_container_client(container_name)

def _get_latest_blob_content():
    """Baixa o blob XML mais recente (do dia atual) do Azure Blob Storage."""
    container = _get_container_client()
    try:
        container.create_container() # Tenta criar o container
    except Exception:
        pass  # Container(Pasta) já existe

    dt = datetime.now().strftime("%y%m%d")
    # Exemplo: 251118 -> 20251118-BolsaB3.xml

    ano = "20" + dt[:2]  # 25 -> 2025
    mes = dt[2:4]        # 11
    dia = dt[4:6]        # 18
    blob_name = f"{ano}{mes}{dia}-BolsaB3.xml"

    logging.info(f"[INFO] Buscando blob: {blob_name}")
    print(f"[INFO] Buscando blob: {blob_name}")
    
    blob_client = container.get_blob_client(blob_name)

    try:
        download_stream = blob_client.download_blob()
        blob_content_bytes = download_stream.readall()
        logging.info(f"[OK] Blob {blob_name} baixado com sucesso. Tamanho: {len(blob_content_bytes)} bytes")
        print(f"[OK] Blob baixado: {len(blob_content_bytes)} bytes")
        return blob_content_bytes, blob_name
    except Exception as e:
        error_msg = f'[ERROR] Erro ao baixar blob {blob_name}: {e}'
        logging.error(error_msg)
        print(error_msg)
        raise RuntimeError(error_msg)

def run(myblob=None):
    """
    Processa dados B3 do blob storage.
    
    Args:
        myblob: InputStream do blob (quando chamado pelo Azure Function blob trigger).
                Se None, busca o blob mais recente do dia atual.
    """
    start_time = time.time()
    logging.info("=" * 80)
    logging.info(f"[START] Iniciando transformação e carga dos dados B3...")
    logging.info(f"[START] Tempo de início: {datetime.now().isoformat()}")
    print(f"[START] Iniciando transformação e carga dos dados B3...")
    print(f"[START] Tempo de início: {datetime.now().isoformat()}")

    # Se não recebeu o blob como parâmetro, busca o mais recente
    if myblob is None:
        logging.info("[INFO] Blob não fornecido. Buscando blob mais recente do dia atual...")
        print("[INFO] Buscando blob mais recente do dia atual...")
        try:
            xml_bytes, blob_name = _get_latest_blob_content()
            logging.info(f"[ETAPA 1/5] Processando blob baixado: {blob_name}")
            print(f"[ETAPA 1/5] Processando blob: {blob_name}")
        except Exception as e:
            logging.error(f"[ERROR] Falha ao buscar blob mais recente: {str(e)}")
            print(f"[ERROR] Falha ao buscar blob: {str(e)}")
            logging.exception(e)
            raise
    else:
        # Recebeu o blob do trigger - processa diretamente
        blob_name = myblob.name
        logging.info(f"[ETAPA 1/5] Processando blob do trigger: {blob_name}")
        print(f"[ETAPA 1/5] Processando blob do trigger: {blob_name}")
        
        try:
            logging.info(f"[ETAPA 2/5] Lendo arquivo blob...")
            print(f"[ETAPA 2/5] Lendo arquivo blob...")
            read_start = time.time()
            xml_bytes = myblob.read()
            read_time = time.time() - read_start
            logging.info(f"[ETAPA 2/5] Arquivo lido com sucesso. Tamanho: {len(xml_bytes)} bytes em {read_time:.2f}s")
            print(f"[ETAPA 2/5] Arquivo lido: {len(xml_bytes)} bytes em {read_time:.2f}s")
        except Exception as e:
            logging.error(f"[ERROR] Erro ao ler arquivo blob: {str(e)}")
            print(f"[ERROR] Erro ao ler arquivo blob: {str(e)}")
            logging.exception(e)
            raise
    
    # A partir daqui, xml_bytes está disponível em ambos os casos
    try:
        logging.info(f"[ETAPA 3/5] Iniciando parsing do XML e filtro de mercado à vista...")
        print(f"[ETAPA 3/5] Iniciando parsing do XML...")
        parse_start = time.time()
        rows = parse_pricrpt(xml_bytes)
        parse_time = time.time() - parse_start
        logging.info(f"[ETAPA 3/5] Parsing concluído. Extraídas {len(rows)} linha(s) em {parse_time:.2f}s")
        print(f"[ETAPA 3/5] Extraídas {len(rows)} linha(s) do XML em {parse_time:.2f}s")
        
        if not rows:
            logging.warning(f"[WARN] 0 linha(s) extraída(s) de {blob_name}")
            print(f"[WARN] 0 linha(s) extraída(s) de {blob_name}")
            return
    except Exception as e:
        logging.error(f"[ERROR] Erro ao fazer parsing do XML: {str(e)}")
        print(f"[ERROR] Erro ao fazer parsing do XML: {str(e)}")
        logging.exception(e)
        raise

    try:
        logging.info(f"[ETAPA 4/5] Iniciando persistência no banco de dados...")
        logging.info(f"[ETAPA 4/5] Total de registros para persistir: {len(rows)}")
        print(f"[ETAPA 4/5] Iniciando persistência no banco de dados...")
        print(f"[ETAPA 4/5] Total de registros: {len(rows)}")
        
        # Mostra uma amostra dos dados
        if len(rows) > 0:
            logging.info(f"[DEBUG] Amostra do primeiro registro: {rows[0]}")
            print(f"[DEBUG] Amostra: {rows[0]}")
        
        persist_start = time.time()
        logging.info(f"[ETAPA 4/5] Chamando persist_quotes()...")
        print(f"[ETAPA 4/5] Chamando persist_quotes()...")
        persist_quotes(rows)
        persist_time = time.time() - persist_start
        logging.info(f"[ETAPA 5/5] Gravadas {len(rows)} linha(s) no banco em {persist_time:.2f}s")
        print(f"[ETAPA 5/5] Gravadas {len(rows)} linha(s) no banco em {persist_time:.2f}s")
        
        total_time = time.time() - start_time
        logging.info(f"[SUCCESS] Processamento completo em {total_time:.2f} segundos")
        print(f"[SUCCESS] Processamento completo em {total_time:.2f} segundos")
        logging.info("=" * 80)
        
    except Exception as e:
        logging.error(f"[ERROR] Erro ao persistir dados no banco: {str(e)}")
        print(f"[ERROR] Erro ao persistir dados no banco: {str(e)}")
        import traceback
        logging.error(f"[ERROR] Traceback completo:")
        traceback.print_exc()
        logging.exception(e)
        raise

if __name__ == "__main__":
    run()
