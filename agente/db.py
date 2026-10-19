"""
db.py -- Conexao DuckDB (singleton) lendo os CSVs materializados em
dados/ + resolucao de nomes.

Por que DuckDB e nao SQL Server: o agente nao pode depender de uma
instancia local de SQL Server com autenticacao Windows -- isso so
existe na maquina de quem montou o pipeline, ninguem mais consegue
rodar o codigo. Os CSVs em dados/ sao a materializacao exata das views
marts.* ja validadas contra o SQL Server (Chat 1) -- o
agente so LE esse resultado, nunca recalcula regra de negocio (R4-R11)
por conta propria. Isso elimina a dependencia de SO/driver/instancia e
deixa o diretorio self-contained: Python + os CSVs bastam.

Conexao singleton: todas as tools reutilizam a mesma conexao DuckDB em
vez de abrir uma nova a cada chamada.

resolver_por_nome() e a funcao compartilhada usada por TODAS as tools
que recebem nome de pessoa/area como parametro. Trata os 3 casos
possiveis -- nenhum match, um match, varios matches -- e nunca "pega o
primeiro" silenciosamente. Importante: tabela/coluna_id/coluna_nome SAO
SEMPRE CONSTANTES FIXAS escolhidas em Python por quem chama (nunca
vindas do agente/LLM) -- so `nome_busca` e um valor de parametro real,
passado via placeholder `?`. Busca e case-insensitive (ILIKE) pra
replicar o comportamento de collation padrao do SQL Server
(Latin1_General_CI_AS) que o pipeline original usava.
"""
import duckdb
from dataclasses import dataclass
from pathlib import Path
from typing import Literal, Optional

DADOS_DIR = Path(__file__).resolve().parent / "dados"

# nome do arquivo CSV -> nome da view DuckDB que as tools consultam
TABELAS = {
    "dim_area": "dim_area.csv",
    "dim_colaborador": "dim_colaborador.csv",
    "dim_meta": "dim_meta.csv",
    "fact_meta_valor_mensal": "fact_meta_valor_mensal.csv",
    "vw_score_colaborador": "vw_score_colaborador.csv",
    "vw_score_area": "vw_score_area.csv",
    "vw_score_gestor": "vw_score_gestor.csv",
    "vw_nota_meta": "vw_nota_meta.csv",
}

_connection: Optional[duckdb.DuckDBPyConnection] = None


def get_connection() -> duckdb.DuckDBPyConnection:
    global _connection
    if _connection is None:
        con = duckdb.connect()
        for view, arquivo in TABELAS.items():
            caminho = DADOS_DIR / arquivo
            if not caminho.exists():
                raise FileNotFoundError(
                    f"Faltando {caminho}. Rode etl/run_pipeline.py (ou export_marts.py) e copie os CSVs "
                    f"de painel/dados/ pra agente/dados/ (ver README.md)."
                )
            con.execute(f"CREATE VIEW {view} AS SELECT * FROM read_csv_auto('{caminho.as_posix()}')")
        _connection = con
    return _connection


@dataclass
class Candidato:
    id: int
    nome: str


@dataclass
class ResolverResultado:
    status: Literal["unico", "multiplos", "nao_encontrado"]
    id: Optional[int] = None
    nome: Optional[str] = None
    candidatos: Optional[list] = None


def resolver_por_nome(
    conn: duckdb.DuckDBPyConnection,
    tabela: str,
    coluna_id: str,
    coluna_nome: str,
    nome_busca: str,
) -> ResolverResultado:
    sql = f"SELECT {coluna_id}, {coluna_nome} FROM {tabela} WHERE {coluna_nome} ILIKE ?"
    rows = conn.execute(sql, [f"%{nome_busca}%"]).fetchall()

    if len(rows) == 0:
        return ResolverResultado(status="nao_encontrado")
    if len(rows) > 1:
        return ResolverResultado(
            status="multiplos",
            candidatos=[Candidato(id=r[0], nome=r[1]) for r in rows],
        )
    return ResolverResultado(status="unico", id=rows[0][0], nome=rows[0][1])
