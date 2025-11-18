from sqlalchemy import create_engine, text
import os
import logging

def get_engine():
    endpoint = os.getenv("MYSQL_CONNECTION_STRING") or "mysql+mysqlconnector://ewjgmv:123senhaS%40@b3-bd-cloud-2025.mysql.database.azure.com:3306/b3_data"
    if not endpoint:
        raise RuntimeError("MYSQL_CONNECTION_STRING não está definido e nenhum fallback foi configurado.")
    logging.info(f"[DB] Usando connection string: {endpoint[:60]}...")
    return create_engine(
        endpoint,
        echo=True  # mostra os INSERT/UPDATE no terminal
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
    eng = get_engine()
    with eng.begin() as con:
        # grava em lotes para não mandar 30k+ linhas de uma vez
        for i in range(0, len(rows), batch):
            con.execute(text(UPSERT_SQL), rows[i:i+batch])
