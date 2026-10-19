"""
run_pipeline.py — Case Mereo (Grupo Aurora)
Ponto único de entrada: do SQLite original até os CSVs consumidos por
painel/ e agente/. Reproduz do zero o que hoje é feito à mão em passos
separados (rodar os .sql no SSMS, rodar extract_load.py, rodar
export_marts.py, copiar CSV pra duas pastas).

Reaproveita a lógica já existente em vez de duplicá-la:
  - conexão e carga do staging: etl/extract_load.py (import, não subprocess)
  - export das views de marts:  etl/export_marts.py (import, não subprocess)
Este script só orquestra os passos, na ordem, e para no primeiro erro.

Uso:
    pip install pyodbc
    python etl/run_pipeline.py

Fora de escopo (de propósito — ver Parte 5, Pergunta Aberta 1 do README):
agendamento, containers, monitoramento, CI/CD. Isso aqui é execução única,
local, sob demanda.
"""
import shutil
import sys
from pathlib import Path

import pyodbc

PROJETO_ROOT = Path(__file__).resolve().parent.parent
SQL_DIR = PROJETO_ROOT / "sql"
PAINEL_DADOS = PROJETO_ROOT / "painel" / "dados"
AGENTE_DADOS = PROJETO_ROOT / "agente" / "dados"

CONN_MASTER = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=localhost;"
    "DATABASE=master;"
    "Trusted_Connection=yes;"
)
CONN_CASEMEREO = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=localhost;"
    "DATABASE=CaseMereo;"
    "Trusted_Connection=yes;"
)


def run_sql_batches(cur, sql_text, idempotente=False):
    """Executa um arquivo .sql batch por batch, dividindo nas linhas 'GO'
    (pyodbc não entende GO — é sintaxe do sqlcmd/SSMS, não T-SQL).

    idempotente=True: trata erro "already exists"/"já existe" como aviso
    e continua, em vez de propagar. Usado só pra create_db.sql e
    create_schemas.sql, que não têm guarda DROP-IF-EXISTS (ao contrário
    das tabelas/views de staging/intermediate/marts, que já têm).
    """
    batches = [b.strip() for b in sql_text.splitlines()]
    atual = []
    for linha in sql_text.splitlines():
        if linha.strip().upper() == "GO":
            if any(l.strip() for l in atual):
                _exec_batch(cur, "\n".join(atual), idempotente)
            atual = []
        else:
            atual.append(linha)
    if any(l.strip() for l in atual):
        _exec_batch(cur, "\n".join(atual), idempotente)


def _exec_batch(cur, batch, idempotente):
    try:
        cur.execute(batch)
    except pyodbc.Error as e:
        msg = str(e)
        if idempotente and ("already exists" in msg or "já existe" in msg.lower()):
            print(f"    (já existe, ok: {msg.splitlines()[0][:120]})")
            return
        raise


def run_sql_file(cur, path, idempotente=False):
    print(f"  - {path.relative_to(PROJETO_ROOT)}")
    texto = path.read_text(encoding="utf-8-sig")
    run_sql_batches(cur, texto, idempotente=idempotente)


def passo(titulo):
    print(f"\n=== {titulo} ===")


def falhou(titulo, erro):
    print(f"\n!!! FALHOU: {titulo}")
    print(f"    {erro}")
    print("\nPipeline interrompido — nada depois deste passo foi executado.")
    sys.exit(1)


def main():
    # --- 1) garante que o banco CaseMereo existe (sql/01_setup/create_db.sql) ---
    titulo = "1/8 — Banco de dados (sql/01_setup/create_db.sql)"
    passo(titulo)
    try:
        conn = pyodbc.connect(CONN_MASTER, autocommit=True)
        cur = conn.cursor()
        cur.execute("SELECT 1 FROM sys.databases WHERE name = 'CaseMereo'")
        if cur.fetchone():
            print("  - CaseMereo já existe, ok")
        else:
            run_sql_file(cur, SQL_DIR / "01_setup" / "create_db.sql", idempotente=True)
        conn.close()
    except Exception as e:
        falhou(titulo, e)

    # --- 2) schemas (sql/01_setup/create_schemas.sql) ---
    titulo = "2/8 — Schemas (sql/01_setup/create_schemas.sql)"
    passo(titulo)
    try:
        conn = pyodbc.connect(CONN_CASEMEREO, autocommit=True)
        cur = conn.cursor()
        run_sql_file(cur, SQL_DIR / "01_setup" / "create_schemas.sql", idempotente=True)
        conn.close()
    except Exception as e:
        falhou(titulo, e)

    # --- 3) staging: DDL (sql/02_staging/*.sql) ---
    titulo = "3/8 — Tabelas de staging (sql/02_staging/*.sql)"
    passo(titulo)
    try:
        conn = pyodbc.connect(CONN_CASEMEREO, autocommit=True)
        cur = conn.cursor()
        for f in sorted((SQL_DIR / "02_staging").glob("*.sql")):
            run_sql_file(cur, f)
        conn.close()
    except Exception as e:
        falhou(titulo, e)

    # --- 4) staging: carga de dados (etl/extract_load.py) ---
    titulo = "4/8 — Carga do SQLite pra staging (etl/extract_load.py)"
    passo(titulo)
    try:
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        import extract_load
        extract_load.main()
    except SystemExit as e:
        if e.code:
            falhou(titulo, f"extract_load.py saiu com código {e.code}")
    except Exception as e:
        falhou(titulo, e)

    # --- 5) intermediate (sql/03_intermediate/*.sql) ---
    titulo = "5/8 — Views de intermediate (sql/03_intermediate/*.sql)"
    passo(titulo)
    try:
        conn = pyodbc.connect(CONN_CASEMEREO, autocommit=True)
        cur = conn.cursor()
        for f in sorted((SQL_DIR / "03_intermediate").glob("*.sql")):
            run_sql_file(cur, f)
        conn.close()
    except Exception as e:
        falhou(titulo, e)

    # --- 6) marts (sql/04_marts/*.sql) ---
    # Ordem explícita, NÃO alfabética: dim_area/dim_colaborador (só leem
    # staging) -> dim_meta/fact_meta_valor_mensal (leem intermediate) ->
    # vw_nota_meta (lê dim_meta + fact_meta_valor_mensal) ->
    # vw_score_colaborador (lê vw_nota_meta) -> vw_score_area/vw_score_gestor
    # (leem vw_score_colaborador). CREATE VIEW falha na hora se o objeto que
    # ela referencia ainda não existe -- ao contrário de DROP VIEW, não há
    # resolução tardia que salve uma ordem errada aqui.
    ORDEM_MARTS = [
        "view_marts_dim_area.sql",
        "view_marts_dim_colaborador.sql",
        "view_marts_dim_meta.sql",
        "view_marts_fact_meta_valor_mensal.sql",
        "view_marts_vw_nota_meta.sql",
        "view_marts_vw_score_colaborador.sql",
        "view_marts_vw_score_area.sql",
        "view_marts_vw_score_gestor.sql",
    ]
    titulo = "6/8 — Views de marts (sql/04_marts/*.sql, ordem de dependência)"
    passo(titulo)
    try:
        conn = pyodbc.connect(CONN_CASEMEREO, autocommit=True)
        cur = conn.cursor()
        pasta = SQL_DIR / "04_marts"
        presentes = {f.name for f in pasta.glob("*.sql")}
        faltando_na_ordem = presentes - set(ORDEM_MARTS)
        if faltando_na_ordem:
            raise RuntimeError(
                f"arquivo(s) em {pasta} não listado(s) em ORDEM_MARTS: {sorted(faltando_na_ordem)} "
                "-- adicione à lista na posição certa da dependência antes de rodar."
            )
        for nome in ORDEM_MARTS:
            f = pasta / nome
            if f.exists():
                run_sql_file(cur, f)
        conn.close()
    except Exception as e:
        falhou(titulo, e)

    # --- 7) export dos CSVs (etl/export_marts.py) ---
    titulo = "7/8 — Export dos CSVs (etl/export_marts.py)"
    passo(titulo)
    try:
        import export_marts
        export_marts.main()
    except Exception as e:
        falhou(titulo, e)

    # --- 8) copia os CSVs pra agente/dados/ (painel/dados/ já é a saída do passo 7) ---
    titulo = "8/8 — Copiar CSVs pra agente/dados/"
    passo(titulo)
    try:
        AGENTE_DADOS.mkdir(parents=True, exist_ok=True)
        csvs = sorted(PAINEL_DADOS.glob("*.csv"))
        if not csvs:
            raise RuntimeError(f"nenhum CSV encontrado em {PAINEL_DADOS} (passo 7 não gerou nada?)")
        for f in csvs:
            destino = AGENTE_DADOS / f.name
            shutil.copyfile(f, destino)
            print(f"  - {f.name} -> {destino.relative_to(PROJETO_ROOT)}")
    except Exception as e:
        falhou(titulo, e)

    print("\n=== Pipeline concluído. painel/dados/ e agente/dados/ estão atualizados. ===")


if __name__ == "__main__":
    main()
