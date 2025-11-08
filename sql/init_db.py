# init_db.py
from sqlalchemy import text
from sql.db_write import get_engine

TABLE_SQL = """
create table if not exists cotacoes(
   id bigint auto_increment primary key,
   Ativo       varchar(20) not null,
   DataPregao  date        not null,
   Abertura    decimal(10,2),
   Fechamento  decimal(10,2),
   PrecoMin    decimal(10,2),
   PrecoMax    decimal(10,2),
   Volume      decimal(18,2),
   unique key uq_cotacoes_ativo_data (Ativo, DataPregao),
   index idx_cotacoes_datapregao (DataPregao)
);
"""

def main():
    eng = get_engine()
    with eng.begin() as con:
        con.execute(text(TABLE_SQL))

    print("[OK] Tabela e índices garantidos no MySQL Azure.")

if __name__ == "__main__":
    main()
