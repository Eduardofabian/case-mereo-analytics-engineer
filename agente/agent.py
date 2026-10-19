"""
agent.py -- Agente Pydantic AI (API Anthropic) para o case Mereo.

O agente escolhe QUAL tool chamar e com quais argumentos, nunca que SQL
executar. Cada @agent.tool abaixo e so uma casca fina sobre tools.py --
a logica de query fica la, nao aqui.

Modelo configuravel via env var MEREO_AGENT_MODEL (formato
"anthropic:<nome-do-modelo>"); default abaixo pode precisar de ajuste
se o nome do modelo mudar -- ver README.md deste diretorio.
"""
import os
from dataclasses import dataclass
from typing import Literal

import duckdb
from pydantic_ai import Agent, RunContext

import db
import tools as t

MODEL = os.environ.get("MEREO_AGENT_MODEL", "anthropic:claude-sonnet-5")


@dataclass
class Deps:
    conn: duckdb.DuckDBPyConnection


SYSTEM_PROMPT = """
Voce responde perguntas sobre os resultados do ciclo 2025 do Grupo
Aurora usando SOMENTE as ferramentas disponiveis. Nunca invente numeros,
nunca gere SQL, nunca responda sem checar a ferramenta correspondente.

Regras obrigatorias:
- Se uma ferramenta devolver status "nao_encontrado": diga explicitamente
  que esse nome nao existe na base. NUNCA escolha o resultado mais
  parecido como se fosse o que foi pedido -- isso e alucinacao. Se voce
  souber, a partir de outras chamadas, nomes parecidos que realmente
  existem, sugira-os.
- Se devolver "multiplos_candidatos": liste os nomes candidatos e peca
  pra pessoa confirmar qual delas quer dizer -- nunca escolha por conta
  propria.
- Se devolver "sem_score" ou "nao_atende_criterio_gestor": explique o
  motivo (sem meta com nota lancada; ou nao atende ao criterio de
  gestor do enunciado -- ativo em 31/12/2025 e >=3 subordinados diretos
  elegiveis), nao trate como erro generico.
- Em consulta de area (score_area): se tem_filhas=true, apresente
  score_direto e score_consolidado e explique a diferenca em uma frase;
  se tem_filhas=false, os dois valores sao iguais por construcao, pode
  citar so um.
- Sempre cite o nome exato encontrado na base (campo "nome" da resposta
  da tool), nao so repita o nome como foi perguntado.

Regras de negocio por tras dos numeros que as tools te devolvem (pra
voce EXPLICAR "por que" com certeza, nao por suposicao):
- Nota de uma meta: atingimento < 80% -> nota 0; entre 80% e 120% ->
  nota = atingimento x 100; acima de 120% -> nota travada em 120. Uma
  nota 0 quase sempre significa atingimento abaixo de 80%, nao erro.
- Score do colaborador: soma(nota x peso) / soma(peso), considerando so
  as metas que tem nota (uma meta sem lancamento valido no mes nao
  entra nem no numerador nem no denominador).
- Score de area: "direto" e a media dos colaboradores elegiveis so
  daquela area; "consolidado" e a media incluindo tambem as areas
  abaixo na hierarquia. Quando nao ha area filha, os dois valores sao
  iguais por construcao (nao e coincidencia nem erro de calculo).
"""

agent = Agent(MODEL, deps_type=Deps, instructions=SYSTEM_PROMPT)


@agent.tool
def score_colaborador(ctx: RunContext[Deps], nome_colaborador: str) -> t.ScoreColaborador:
    """Score (R9) de um colaborador pelo nome, com area, gestor e elegibilidade R10."""
    return t.consultar_score_colaborador(ctx.deps.conn, nome_colaborador)


@agent.tool
def score_area(ctx: RunContext[Deps], nome_area: str) -> t.ScoreArea:
    """Score direto e consolidado (R11) de uma area pelo nome. Sempre devolve os dois valores."""
    return t.consultar_score_area(ctx.deps.conn, nome_area)


@agent.tool
def score_gestor(ctx: RunContext[Deps], nome_gestor: str) -> t.ScoreGestor:
    """Score medio do time de um gestor -- so pros gestores que atendem o criterio do enunciado."""
    return t.consultar_score_gestor(ctx.deps.conn, nome_gestor)


@agent.tool
def colaboradores_do_time_por_score(
    ctx: RunContext[Deps], nome_gestor: str, limite: float, comparador: Literal["abaixo", "acima"]
) -> t.ListaTimePorScore:
    """Lista os subordinados diretos de um gestor com score abaixo ou acima de um limite."""
    return t.listar_colaboradores_time_por_score(ctx.deps.conn, nome_gestor, limite, comparador)


@agent.tool
def ranking_areas(
    ctx: RunContext[Deps],
    nivel: int,
    criterio: Literal["direto", "consolidado"],
    ordem: Literal["melhor", "pior"],
    top_n: int = 1,
) -> t.RankingAreas:
    """Ranking de areas por nivel hierarquico (0=diretoria, 1=gerencia, 2=coordenacao), por score direto ou consolidado, melhor ou pior, top N."""
    return t.ranking_areas_por_nivel(ctx.deps.conn, nivel, criterio, ordem, top_n)


@agent.tool
def metas_colaborador_por_atingimento(
    ctx: RunContext[Deps], nome_colaborador: str, limite: float, comparador: Literal["abaixo", "acima"]
) -> t.MetasPorAtingimento:
    """Metas de um colaborador com atingimento bruto (fracao, nao a nota truncada por R6) abaixo ou acima de um limite."""
    return t.metas_colaborador_por_atingimento(ctx.deps.conn, nome_colaborador, limite, comparador)


def main():
    import sys
    conn = db.get_connection()
    deps = Deps(conn=conn)
    pergunta = " ".join(sys.argv[1:]) or "Qual o score da Gerência de Marketing?"
    resultado = agent.run_sync(pergunta, deps=deps)
    print(resultado.output)


if __name__ == "__main__":
    main()
