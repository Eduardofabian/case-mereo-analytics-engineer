import pyodbc
import csv
from pathlib import Path

PROJETO_ROOT = Path(__file__).resolve().parent.parent  # etl/ -> raiz do projeto
RESPOSTAS_DIR = PROJETO_ROOT / "respostas"
RESPOSTAS_DIR.mkdir(exist_ok=True)

SQLSERVER_CONN_STR = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=localhost;"
    "DATABASE=CaseMereo;"
    "Trusted_Connection=yes;"
)

QUERIES = {
    "p1_score_colaborador.csv": (
        ["id_colaborador", "score"],
        """
        SELECT dc.id_colaborador,
               CAST(ROUND(sc.score, 2) AS DECIMAL(10,2)) AS score
        FROM marts.dim_colaborador dc
        JOIN marts.vw_score_colaborador sc ON sc.id_colaborador = dc.id_colaborador
        WHERE dc.flag_elegivel_r10 = 1
        ORDER BY dc.id_colaborador
        """
    ),
    "p2_score_area.csv": (
        ["id_area", "score_direto", "score_consolidado"],
        """
        SELECT id_area,
               CAST(ROUND(score_direto, 2) AS DECIMAL(10,2)) AS score_direto,
               CAST(ROUND(score_consolidado, 2) AS DECIMAL(10,2)) AS score_consolidado
        FROM marts.vw_score_area
        ORDER BY id_area
        """
    ),
    "p3_gestores.csv": (
        ["grupo", "posicao", "id_gestor", "score_medio_time"],
        """
        WITH ranked AS (
            SELECT id_gestor, score_medio_time,
                   ROW_NUMBER() OVER (ORDER BY score_medio_time DESC) AS rn_top,
                   ROW_NUMBER() OVER (ORDER BY score_medio_time ASC)  AS rn_bottom
            FROM marts.vw_score_gestor
        )
        SELECT 'top' AS grupo, rn_top AS posicao, id_gestor,
               CAST(ROUND(score_medio_time, 2) AS DECIMAL(10,2)) AS score_medio_time
        FROM ranked WHERE rn_top <= 3
        UNION ALL
        SELECT 'bottom' AS grupo, rn_bottom AS posicao, id_gestor,
               CAST(ROUND(score_medio_time, 2) AS DECIMAL(10,2)) AS score_medio_time
        FROM ranked WHERE rn_bottom <= 3
        ORDER BY grupo DESC, posicao ASC
        """
    ),
}

def main():
    conn = pyodbc.connect(SQLSERVER_CONN_STR, autocommit=True)
    cur = conn.cursor()

    for filename, (header, query) in QUERIES.items():
        cur.execute(query)
        rows = cur.fetchall()
        path = RESPOSTAS_DIR / filename
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(header)
            writer.writerows(rows)
        print(f"{path}: {len(rows)} linhas")

    conn.close()

if __name__ == "__main__":
    main()