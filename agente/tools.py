"""
tools.py -- As 6 consultas fixas e parametrizadas do agente, agora
sobre as views DuckDB registradas em db.py (que leem os CSVs de dados/).

Requisito nao-negociavel do enunciado: "o agente deve usar ferramentas
(funcoes que executam consultas definidas por voce) em vez de gerar SQL
livre a cada pergunta". Por isso, NENHUMA funcao aqui monta SQL a partir
do texto da pergunta -- cada uma roda uma query fixa, escrita neste
arquivo, parametrizada so por:
  (a) valores (nome buscado, limite numerico), via placeholder `?`; ou
  (b) enums fechados (Literal), que mapeiam para um fragmento de SQL
      fixo escolhido em Python (_OPERADOR_SQL, _ORDEM_SQL) -- nunca para
      uma string formatada a partir de texto livre do agente.

O agente (agent.py) decide QUAL tool chamar e com quais valores --
nunca decide QUE SQL rodar.
"""
from dataclasses import dataclass
from typing import Literal, Optional
import duckdb

from db import resolver_por_nome

Comparador = Literal["abaixo", "acima"]
Criterio = Literal["direto", "consolidado"]
Ordem = Literal["melhor", "pior"]

_OPERADOR_SQL = {"abaixo": "<", "acima": ">"}
_ORDEM_SQL = {"melhor": "DESC", "pior": "ASC"}


# ---------- tipos de retorno ----------

@dataclass
class ScoreColaborador:
    status: Literal["ok", "nao_encontrado", "multiplos_candidatos", "sem_score"]
    nome: Optional[str] = None
    score: Optional[float] = None
    area: Optional[str] = None
    gestor: Optional[str] = None
    elegivel_r10: Optional[bool] = None
    ativo_fim_2025: Optional[bool] = None
    candidatos: Optional[list] = None


@dataclass
class ScoreArea:
    status: Literal["ok", "nao_encontrado", "multiplos_candidatos"]
    nome: Optional[str] = None
    nivel: Optional[int] = None
    tem_filhas: Optional[bool] = None
    score_direto: Optional[float] = None
    score_consolidado: Optional[float] = None
    candidatos: Optional[list] = None


@dataclass
class ScoreGestor:
    status: Literal["ok", "nao_encontrado", "multiplos_candidatos", "nao_atende_criterio_gestor"]
    nome: Optional[str] = None
    score_medio_time: Optional[float] = None
    n_subordinados_diretos_elegiveis: Optional[int] = None
    candidatos: Optional[list] = None


@dataclass
class ColaboradorDoTime:
    nome: str
    score: float
    elegivel_r10: bool


@dataclass
class ListaTimePorScore:
    status: Literal["ok", "nao_encontrado", "multiplos_candidatos"]
    gestor: Optional[str] = None
    colaboradores: Optional[list] = None
    candidatos: Optional[list] = None


@dataclass
class AreaRanking:
    nome: str
    score: float


@dataclass
class RankingAreas:
    nivel: int
    criterio: str
    ordem: str
    areas: list


@dataclass
class MetaColaborador:
    nome_meta: str
    atingimento: float
    nota: float
    peso: float


@dataclass
class MetasPorAtingimento:
    status: Literal["ok", "nao_encontrado", "multiplos_candidatos"]
    colaborador: Optional[str] = None
    metas: Optional[list] = None
    candidatos: Optional[list] = None


# ---------- tools ----------

def consultar_score_colaborador(conn: duckdb.DuckDBPyConnection, nome_colaborador: str) -> ScoreColaborador:
    r = resolver_por_nome(conn, "dim_colaborador", "id_colaborador", "nome", nome_colaborador)
    if r.status == "nao_encontrado":
        return ScoreColaborador(status="nao_encontrado")
    if r.status == "multiplos":
        return ScoreColaborador(status="multiplos_candidatos", candidatos=[c.nome for c in r.candidatos])

    row = conn.execute(
        """
        SELECT vsc.score, da.nome, dg.nome, dc.flag_elegivel_r10, dc.flag_ativo_fim_2025
        FROM dim_colaborador dc
        LEFT JOIN vw_score_colaborador vsc ON vsc.id_colaborador = dc.id_colaborador
        LEFT JOIN dim_area da ON da.id_area = dc.id_area
        LEFT JOIN dim_colaborador dg ON dg.id_colaborador = dc.id_gestor
        WHERE dc.id_colaborador = ?
        """,
        [r.id],
    ).fetchone()
    if row is None or row[0] is None:
        return ScoreColaborador(status="sem_score", nome=r.nome)
    return ScoreColaborador(
        status="ok", nome=r.nome, score=row[0], area=row[1], gestor=row[2],
        elegivel_r10=bool(row[3]), ativo_fim_2025=bool(row[4]),
    )


def consultar_score_area(conn: duckdb.DuckDBPyConnection, nome_area: str) -> ScoreArea:
    r = resolver_por_nome(conn, "dim_area", "id_area", "nome", nome_area)
    if r.status == "nao_encontrado":
        return ScoreArea(status="nao_encontrado")
    if r.status == "multiplos":
        return ScoreArea(status="multiplos_candidatos", candidatos=[c.nome for c in r.candidatos])

    row = conn.execute(
        """
        SELECT da.nivel, vsa.score_direto, vsa.score_consolidado,
               (SELECT COUNT(*) FROM dim_area f WHERE f.id_area_pai = da.id_area) AS n_filhas
        FROM dim_area da
        LEFT JOIN vw_score_area vsa ON vsa.id_area = da.id_area
        WHERE da.id_area = ?
        """,
        [r.id],
    ).fetchone()
    nivel, score_direto, score_consolidado, n_filhas = row
    return ScoreArea(
        status="ok", nome=r.nome, nivel=nivel, tem_filhas=(n_filhas > 0),
        score_direto=score_direto, score_consolidado=score_consolidado,
    )


def consultar_score_gestor(conn: duckdb.DuckDBPyConnection, nome_gestor: str) -> ScoreGestor:
    r = resolver_por_nome(conn, "dim_colaborador", "id_colaborador", "nome", nome_gestor)
    if r.status == "nao_encontrado":
        return ScoreGestor(status="nao_encontrado")
    if r.status == "multiplos":
        return ScoreGestor(status="multiplos_candidatos", candidatos=[c.nome for c in r.candidatos])

    row = conn.execute(
        "SELECT score_medio_time, n_subordinados_diretos_elegiveis "
        "FROM vw_score_gestor WHERE id_gestor = ?",
        [r.id],
    ).fetchone()
    if row is None:
        # Pessoa existe, mas nao passa no filtro do enunciado (ativo em
        # 31/12/2025 + >=3 subordinados elegiveis) -- nao e "nao encontrado".
        return ScoreGestor(status="nao_atende_criterio_gestor", nome=r.nome)
    return ScoreGestor(
        status="ok", nome=r.nome,
        score_medio_time=row[0], n_subordinados_diretos_elegiveis=row[1],
    )


def listar_colaboradores_time_por_score(
    conn: duckdb.DuckDBPyConnection, nome_gestor: str, limite: float, comparador: Comparador
) -> ListaTimePorScore:
    r = resolver_por_nome(conn, "dim_colaborador", "id_colaborador", "nome", nome_gestor)
    if r.status == "nao_encontrado":
        return ListaTimePorScore(status="nao_encontrado")
    if r.status == "multiplos":
        return ListaTimePorScore(status="multiplos_candidatos", candidatos=[c.nome for c in r.candidatos])

    op = _OPERADOR_SQL[comparador]
    rows = conn.execute(
        f"""
        SELECT dc.nome, vsc.score, dc.flag_elegivel_r10
        FROM dim_colaborador dc
        JOIN vw_score_colaborador vsc ON vsc.id_colaborador = dc.id_colaborador
        WHERE dc.id_gestor = ? AND vsc.score {op} ?
        ORDER BY vsc.score
        """,
        [r.id, limite],
    ).fetchall()
    colaboradores = [
        ColaboradorDoTime(nome=row[0], score=row[1], elegivel_r10=bool(row[2]))
        for row in rows
    ]
    return ListaTimePorScore(status="ok", gestor=r.nome, colaboradores=colaboradores)


def ranking_areas_por_nivel(
    conn: duckdb.DuckDBPyConnection, nivel: int, criterio: Criterio, ordem: Ordem, top_n: int = 1,
) -> RankingAreas:
    coluna = "score_direto" if criterio == "direto" else "score_consolidado"
    direcao = _ORDEM_SQL[ordem]
    rows = conn.execute(
        f"""
        SELECT da.nome, vsa.{coluna}
        FROM dim_area da
        JOIN vw_score_area vsa ON vsa.id_area = da.id_area
        WHERE da.nivel = ? AND vsa.{coluna} IS NOT NULL
        ORDER BY vsa.{coluna} {direcao}
        LIMIT ?
        """,
        [nivel, top_n],
    ).fetchall()
    areas = [AreaRanking(nome=row[0], score=row[1]) for row in rows]
    return RankingAreas(nivel=nivel, criterio=criterio, ordem=ordem, areas=areas)


def metas_colaborador_por_atingimento(
    conn: duckdb.DuckDBPyConnection, nome_colaborador: str, limite: float, comparador: Comparador
) -> MetasPorAtingimento:
    r = resolver_por_nome(conn, "dim_colaborador", "id_colaborador", "nome", nome_colaborador)
    if r.status == "nao_encontrado":
        return MetasPorAtingimento(status="nao_encontrado")
    if r.status == "multiplos":
        return MetasPorAtingimento(status="multiplos_candidatos", candidatos=[c.nome for c in r.candidatos])

    op = _OPERADOR_SQL[comparador]
    rows = conn.execute(
        f"""
        SELECT dm.nome_meta, nm.atingimento, nm.nota, dm.peso_efetivo
        FROM dim_meta dm
        JOIN vw_nota_meta nm ON nm.id_meta = dm.id_meta
        WHERE dm.id_colaborador = ?
          AND nm.n_meses_validos > 0
          AND nm.atingimento IS NOT NULL
          AND nm.atingimento {op} ?
        ORDER BY nm.atingimento
        """,
        [r.id, limite],
    ).fetchall()
    metas = [
        MetaColaborador(nome_meta=row[0], atingimento=row[1], nota=row[2], peso=row[3])
        for row in rows
    ]
    return MetasPorAtingimento(status="ok", colaborador=r.nome, metas=metas)
