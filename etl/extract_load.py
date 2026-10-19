"""
extract_load.py — Case Mereo (Grupo Aurora)
Lê o case_metas.db (SQLite) e carrega as 5 tabelas em staging.* no SQL Server.
Não roda intermediate/marts, não exporta CSV — só a carga crua.

Uso:
    pip install pyodbc
    python etl/extract_load.py
"""
import sqlite3
import pyodbc
import pathlib
import sys
import datetime

SQLITE_PATH = pathlib.Path(__file__).resolve().parent.parent / "material_original" / "dados" / "case_metas.db"
# Corrigido (era um caminho absoluto hardcoded de uma pasta antiga que não existe
# mais nesta árvore: "Case Dados - Mereo (atual)\dados\case_metas.db"). Agora é
# relativo à raiz do projeto, como os outros scripts de etl/.
SQLSERVER_CONN_STR = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=localhost;"
    "DATABASE=CaseMereo;"
    "Trusted_Connection=yes;"
)

TABLES = {
    "area": {
        "cols": ["id_area", "nome", "id_area_pai"],
    },
    "ciclo": {
        "cols": ["id_ciclo", "nome", "data_inicio", "data_fim"],
    },
    "colaborador": {
        "cols": ["id_colaborador", "nome", "id_area", "id_gestor", "data_admissao", "data_desligamento"],
    },
    "meta": {
        "cols": ["id_meta", "id_ciclo", "id_colaborador", "nome_meta", "tipo_meta",
                 "id_meta_referencia", "polaridade", "tipo_acumulacao", "peso"],
    },
    "meta_valor_mensal": {
        "cols": ["id_lancamento", "id_meta", "mes", "previsto", "realizado",
                 "nao_se_aplica", "data_lancamento"],
    },
}


def load_table_bulk(table, sqlite_cur, cur):
    """Carga rápida via executemany — usada pras 4 tabelas que já carregaram sem erro."""
    cols = TABLES[table]["cols"]
    sqlite_cur.execute(f"SELECT {', '.join(cols)} FROM {table}")
    rows = sqlite_cur.fetchall()

    cur.execute(f"TRUNCATE TABLE staging.{table}")
    placeholders = ", ".join("?" for _ in cols)
    insert_sql = f"INSERT INTO staging.{table} ({', '.join(cols)}) VALUES ({placeholders})"
    cur.executemany(insert_sql, rows)

    cur.execute(f"SELECT COUNT(*) FROM staging.{table}")
    count = cur.fetchone()[0]
    print(f"staging.{table}: {len(rows)} lidas do SQLite -> {count} carregadas no SQL Server")


def load_meta_valor_mensal(sqlite_cur, cur):
    """Carga linha a linha, só pra essa tabela — pra isolar a linha que quebra a conversão de data."""
    cols = TABLES["meta_valor_mensal"]["cols"]
    sqlite_cur.execute(f"SELECT {', '.join(cols)} FROM meta_valor_mensal")
    rows = sqlite_cur.fetchall()

    cur.execute("TRUNCATE TABLE staging.meta_valor_mensal")
    placeholders = ", ".join("?" for _ in cols)
    insert_sql = f"INSERT INTO staging.meta_valor_mensal ({', '.join(cols)}) VALUES ({placeholders})"

    ok = 0
    falhas = []
    for row in rows:
        row = list(row)
        row[6] = datetime.datetime.strptime(row[6], "%Y-%m-%d").date()  # data_lancamento
        try:
            cur.execute(insert_sql, row)
            ok += 1
        except Exception as e:
            falhas.append((row, str(e)))

    print(f"staging.meta_valor_mensal: {ok}/{len(rows)} carregadas")
    if falhas:
        print(f"\n{len(falhas)} linha(s) falharam:")
        for row, err in falhas:
            print(f"  linha: {row}")
            print(f"  erro:  {err}\n")


def main():
    if not pathlib.Path(SQLITE_PATH).exists():
        print(f"ERRO: não encontrei o SQLite em {SQLITE_PATH}")
        sys.exit(1)

    sqlite_conn = sqlite3.connect(SQLITE_PATH)
    sqlite_cur = sqlite_conn.cursor()

    sqlserver_conn = pyodbc.connect(SQLSERVER_CONN_STR, autocommit=True)
    cur = sqlserver_conn.cursor()

    for table in ["area", "ciclo", "colaborador", "meta"]:
        load_table_bulk(table, sqlite_cur, cur)

    load_meta_valor_mensal(sqlite_cur, cur)

    sqlite_conn.close()
    sqlserver_conn.close()
    print("\nCarga concluída.")


if __name__ == "__main__":
    main()