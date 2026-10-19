"""Exporta o schema marts (gold) do SQL Server para CSV, para uso no Power BI.

Saída: painel/dados/<tabela>.csv  (UTF-8 com BOM, separador vírgula, ponto decimal)
Uso:   python etl/export_marts.py
"""
import csv
from pathlib import Path

import pyodbc

PROJETO_ROOT = Path(__file__).resolve().parent.parent
SAIDA = PROJETO_ROOT / "painel" / "dados"
SAIDA.mkdir(parents=True, exist_ok=True)

SQLSERVER_CONN_STR = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=localhost;"
    "DATABASE=CaseMereo;"
    "Trusted_Connection=yes;"
)

TABELAS = [
    "marts.dim_area",
    "marts.dim_colaborador",
    "marts.dim_meta",
    "marts.fact_meta_valor_mensal",
    "marts.vw_score_colaborador",
    "marts.vw_score_area",
    "marts.vw_score_gestor",
    # Exportada pra alimentar a tool metas_colaborador_por_atingimento do
    # agente (Parte 4) -- sem isso, atingimento/nota so existiam dentro do
    # SQL Server, e o agente nao roda fora da sua maquina.
    "marts.vw_nota_meta",
]


def main():
    conn = pyodbc.connect(SQLSERVER_CONN_STR, autocommit=True)
    cur = conn.cursor()
    for tabela in TABELAS:
        cur.execute(f"SELECT * FROM {tabela}")
        cols = [c[0] for c in cur.description]
        linhas = cur.fetchall()
        destino = SAIDA / f"{tabela.split('.')[1]}.csv"
        with open(destino, "w", newline="", encoding="utf-8-sig") as f:
            w = csv.writer(f)
            w.writerow(cols)
            for r in linhas:
                w.writerow(["" if v is None else v for v in r])
        print(f"{tabela}: {len(linhas)} linhas -> {destino}")
    conn.close()


if __name__ == "__main__":
    main()
