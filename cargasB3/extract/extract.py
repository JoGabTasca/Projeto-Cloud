from datetime import datetime, timedelta
from .helpers import yymmdd
import requests
import os
import zipfile
import shutil
import tempfile

from .load_azure import upload_to_azure

# Usa diretório temporário do sistema (funciona em Azure Functions)
PATH_TO_SAVE = os.path.join(tempfile.gettempdir(), "dados_b3")

def build_url_download(date_to_download):
    return f"https://www.b3.com.br/pesquisapregao/download?filelist=SPRE{date_to_download}.zip"

def try_http_download(url):
    session = requests.Session()
    try:
        print(f"[INFO] Tentando {url}")
        resp = session.get(url, timeout=30)
        if (resp.ok) and resp.content and len(resp.content) > 200:
            if (resp.content[:2] == b"PK"):
                return resp.content, os.path.basename(url)
    except requests.RequestException:
        print(f"[ERROR] Falha ao acessar a {url}")
        pass
    # Garantir retorno consistente como tupla
    return None, None

# FUNCAO para caso de falha no download pegar dias anteriores
def achar_zip_pregao_recente(max_days):
    for days_back in range(0, max_days):
        dt_obj = datetime.now() - timedelta(days=days_back)
        dt_str = yymmdd(dt_obj)
        url = build_url_download(dt_str)
        zip_bytes, zip_name = try_http_download(url)
        if zip_bytes:
            if days_back > 0:
                print(f"[INFO] Arquivo encontrado para {dt_str} (há {days_back} dias)")
            return dt_str, zip_bytes, zip_name
    return None, None, None

def run():
    print(f"[INFO] Iniciando extracao B3...")
    print(f"[INFO] Diretorio temporario: {PATH_TO_SAVE}")
    
    # 1) Procurar e baixar o zip a partir da data atual, recuando até MAX_DAYS
    MAX_DAYS = 7
    print(f"[INFO] Buscando arquivo dos ultimos {MAX_DAYS} dias...")
    dt, zip_bytes, zip_name = achar_zip_pregao_recente(MAX_DAYS)

    if not zip_bytes:
        error_msg = f"Não foi possível baixar o arquivo de cotações nos últimos {MAX_DAYS} dias. Verifique conexão / site da B3."
        print(f"[ERROR] {error_msg}")
        raise RuntimeError(error_msg)

    print(f"[OK] Baixado arquivo de cotaçoes: {zip_name}")

    # 2) Salvar o Zip
    try:
        #Cria o diretorio que ira salvar o arquivo zip do download
        os.makedirs(PATH_TO_SAVE, exist_ok=True)
        zip_path = f"{PATH_TO_SAVE}/pregao_{dt}.zip"
        with open(zip_path, "wb") as f:
            f.write(zip_bytes)

        print(f"[OK] Zip salvo em {zip_path}")
    except Exception as e:
        print(f"[ERROR] Falha ao salvar zip: {str(e)}")
        raise

    # 3) Extrair os arquivos do zip
    try:
        #Extrair a primeira pasta
        first_extract_dir = os.path.join(PATH_TO_SAVE, f"pregao_{dt}")
        os.makedirs(first_extract_dir, exist_ok=True)
        with zipfile.ZipFile(zip_path, "r") as zf:
            zf.extractall(first_extract_dir)

        #Extrair a segunda parte
        second_zip = os.path.join(first_extract_dir, f"SPRE{dt}.zip")
        second_extract_dir = os.path.join(PATH_TO_SAVE, f"ARQUIVOSPREGAO_SPRE{dt}")
        os.makedirs(second_extract_dir, exist_ok=True)
        with zipfile.ZipFile(second_zip, "r") as zf:
            zf.extractall(second_extract_dir)

        print(f"[OK] Arquivos extraidos do zip com sucesso")
    except Exception as e:
        print(f"[ERROR] Falha ao extrair arquivos: {str(e)}")
        raise

    # Subir APENAS o arquivo XML renomeado para o Azure Blob Storage
    try:
        arquivos = [f for f in os.listdir(f"{PATH_TO_SAVE}/ARQUIVOSPREGAO_SPRE{dt}") if f.endswith(".xml")]
        print(f"[INFO] Encontrados {len(arquivos)} arquivo(s) XML no diretório")
        
        if not arquivos:
            print(f"[WARN] Nenhum arquivo XML encontrado para upload")
            return
        
        # Formato do nome: YYYYMMDD-BolsaB3.xml
        # dt está no formato YYMMDD (ex: 251114), precisa converter para YYYYMMDD
        # Assumindo que 25 = 2025
        ano = "20" + dt[:2]  # 25 -> 2025
        mes = dt[2:4]        # 11
        dia = dt[4:6]        # 14
        novo_nome = f"{ano}{mes}{dia}-BolsaB3.xml"
        
        # Processa apenas o primeiro arquivo XML encontrado
        arquivo_original = arquivos[0]
        print(f"[INFO] Arquivo original encontrado: {arquivo_original}")
        print(f"[INFO] Será renomeado para: {novo_nome}")
        
        arquivo_local_original = f"{PATH_TO_SAVE}/ARQUIVOSPREGAO_SPRE{dt}/{arquivo_original}"
        
        # Envia direto e não duplica para evitar o erro de arquivo em uso (WinError 32) ao copiar.
        # Esse erro estava evitando o upload do arquivo em alguns computadores.
        print(f"[INFO] Enviando APENAS o arquivo renomeado ({novo_nome}) para Azure Blob Storage...")
        upload_to_azure(novo_nome, arquivo_local_original)
        
        print(f"[OK] Arquivo {novo_nome} enviado com sucesso para o Azure Blob Storage")
        print(f"[INFO] Arquivo original ({arquivo_original}) NÃO foi salvo no blob storage")
    except Exception as e:
        print(f"[ERROR] Falha ao enviar arquivos para Azure: {str(e)}")
        raise

    # Apagar as pastas locais
    try:
        shutil.rmtree(f"{PATH_TO_SAVE}", ignore_errors=True)
        print(f"[OK] Pastas locais apagadas com sucesso")
    except Exception as e:
        print(f"[WARNING] Falha ao apagar pastas temporarias: {str(e)}")
    
    print(f"[SUCCESS] Processo de extracao B3 concluido com sucesso!")

        


if __name__ == "__main__":
    run()
