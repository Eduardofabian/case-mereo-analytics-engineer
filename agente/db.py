"""
db.py -- Conexao com o SQL Server (singleton) + resolucao de nomes.

Conexao singleton: todas as tools reutilizam a mesma conexao pyodbc em
vez de abrir uma nova a cada chamada (regra tecnica padrao do Eduardo,
adaptada de DuckDB pra SQL Server aqui).

resolver_por_nome() e a funcao compartilhada usada por TODAS as tools
que recebem nome de pessoa/area como parametro. Ela trata os 3 casos
possiveis -- nenhum match, um match, varios matches -- e nunca "pega o
primeiro" silenciosamente. Importante: tabela/coluna_id/coluna_nome
SAO SEMPRE CONSTANTES FIXAS escolhidas em Python por quem chama (nunca
vindas do agente/LLM) -- apenas `nome_busca` e um valor de parametro
real, passado via placeholder `?` do pyodbc. Isso preserva a exigencia
do case: nenhuma parte da query e montada a partir do texto da pergunta.
"""
import pyodbc
from dataclasses import dataclass
from typing import Literal, Optional

CONN_STR = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=localhost;"
    "DATABASE=CaseMereo;"
    "Trusted_Connection=yes;"
)

_connection: Optional[pyodbc.Connection] = None


def get_connection() -> pyodbc.Connection:
    global _connection
    if _connection is None:
        _connection = pyodbc.connect(CONN_STR, autocommit=True)
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
    conn: pyodbc.Connection,
    tabela: str,
    coluna_id: str,
    coluna_nome: str,
    nome_busca: str,
) -> ResolverResultado:
    sql = f"SELECT {coluna_id}, {coluna_nome} FROM {tabela} WHERE {coluna_nome} LIKE ?"
    cur = conn.cursor()
    cur.execute(sql, f"%{nome_busca}%")
    rows = cur.fetchall()

    if len(rows) == 0:
        return ResolverResultado(status="nao_encontrado")
    if len(rows) > 1:
        return ResolverResultado(
            status="multiplos",
            candidatos=[Candidato(id=r[0], nome=r[1]) for r in rows],
        )
    return ResolverResultado(status="unico", id=rows[0][0], nome=rows[0][1])
