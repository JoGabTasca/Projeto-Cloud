from sqlalchemy import create_engine, text
import os
import logging

def get_engine():
    endpoint = os.getenv("MYSQL_CONNECTION_STRING") or "mysql+mysqlconnector://ewjgmv:123senhaS%40@b3-bd-cloud-2025.mysql.database.azure.com:3306/b3_data"
    if not endpoint:
        raise RuntimeError("MYSQL_CONNECTION_STRING não está definido e nenhum fallback foi configurado.")
    logging.info(f"[DB] Usando connection string: {endpoint[:60]}...")
    print(f"[DB] Conectando ao MySQL: {endpoint[:60]}...")
    return create_engine(
        endpoint,
        echo=False,  # Desabilita echo para não poluir logs em produção
        pool_pre_ping=True,  # Valida conexões antes de usar
        pool_recycle=3600  # Recicla conexões a cada hora
    )

UPSERT_SQL = """
insert into cotacoes
(Ativo, DataPregao, Abertura, Fechamento, PrecoMin, PrecoMax, Volume)
values
(:Ativo, :DataPregao, :Abertura, :Fechamento, :PrecoMin, :PrecoMax, :Volume)
on duplicate key update
  Abertura = VALUES(Abertura),
  Fechamento = VALUES(Fechamento),
  PrecoMin = VALUES(PrecoMin),
  PrecoMax = VALUES(PrecoMax),
  Volume = VALUES(Volume);
"""

def persist_quotes(rows, batch=2000):
    if not rows:
        logging.warning("[DB] persist_quotes chamado com lista vazia")
        print("[DB] persist_quotes chamado com lista vazia")
        return
    
    logging.info(f"[DB] Iniciando persistência de {len(rows)} registros em lotes de {batch}")
    print(f"[DB] Iniciando persistência de {len(rows)} registros")
    
    try:
        eng = get_engine()
        logging.info("[DB] Conexão com banco estabelecida")
        print("[DB] Conexão estabelecida")
        
        with eng.begin() as con:
            total_batches = (len(rows) + batch - 1) // batch
            logging.info(f"[DB] Total de lotes a processar: {total_batches}")
            
            # grava em lotes para não mandar 30k+ linhas de uma vez
            for batch_num, i in enumerate(range(0, len(rows), batch), 1):
                batch_rows = rows[i:i+batch]
                logging.info(f"[DB] Processando lote {batch_num}/{total_batches} ({len(batch_rows)} registros)")
                print(f"[DB] Lote {batch_num}/{total_batches}")
                con.execute(text(UPSERT_SQL), batch_rows)
                logging.info(f"[DB] Lote {batch_num}/{total_batches} gravado com sucesso")
        
        logging.info(f"[DB] Persistência concluída: {len(rows)} registros gravados")
        print(f"[DB] ✓ {len(rows)} registros gravados com sucesso")
        
    except Exception as e:
        logging.error(f"[DB] ERRO ao persistir dados: {str(e)}")
        print(f"[DB] ERRO: {str(e)}")
        logging.exception(e)
        raise
