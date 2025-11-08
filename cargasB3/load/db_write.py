from sqlalchemy import create_engine, text
import os

def get_engine():
    endpoint  = os.getenv("MYSQL_CONNECTION_STRING")
    # Conexão com MySQL Azure
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
