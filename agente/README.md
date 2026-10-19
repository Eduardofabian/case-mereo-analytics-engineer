# Agente de IA -- Case Mereo (Grupo Aurora)

## Arquitetura

Tool-calling com funcoes Python fixas e parametrizadas (Pydantic AI + API
Anthropic), **nunca** text-to-SQL. O agente decide qual ferramenta chamar
e com quais argumentos; a query em si esta sempre escrita de antemao em
`tools.py`. A unica coisa que varia por chamada e: um nome (resolvido via
busca parcial, nunca interpolado em SQL fora de um placeholder `?`), um
limite numerico, ou um enum fechado (`"abaixo"/"acima"`,
`"direto"/"consolidado"`, `"melhor"/"pior"`) que mapeia pra um fragmento
de SQL fixo escolhido em Python -- nunca pra uma string de operador/coluna
vinda livre do texto da pergunta.

Arquivos:
- `db.py` -- conexao singleton com o SQL Server + `resolver_por_nome`,
  a funcao compartilhada por todas as tools que recebem nome de pessoa
  ou area. Trata 3 casos: nao encontrado, um match, varios matches --
  nunca "pega o primeiro".
- `tools.py` -- as 6 consultas fixas (ver tabela abaixo).
- `agent.py` -- define o `Agent` do Pydantic AI, registra as 6 tools via
  `@agent.tool`, e o system prompt com as regras de como reagir a cada
  status (nao_encontrado, multiplos_candidatos, sem_score, etc.).
- `run_perguntas.py` -- roda as 5 perguntas obrigatorias do case e grava
  `respostas.md`.

## Tools

| Tool | Parametros | Cobre |
|---|---|---|
| `score_colaborador` | `nome_colaborador` | variacao livre |
| `score_area` | `nome_area` | Q1, Q5 |
| `score_gestor` | `nome_gestor` | variacao livre |
| `colaboradores_do_time_por_score` | `nome_gestor`, `limite`, `comparador` | Q2 |
| `ranking_areas` | `nivel`, `criterio`, `ordem`, `top_n` | Q3 |
| `metas_colaborador_por_atingimento` | `nome_colaborador`, `limite`, `comparador` | Q4 |

## Decisoes a documentar no README geral / comentario

- **"Time de um gestor" = `id_gestor` direto** (campo da tabela
  colaborador), nao hierarquia de area.
- **`score_area` sempre devolve `score_direto` e `score_consolidado`**
  juntos, nunca um default escolhido pelo codigo -- quem decide o que
  destacar na resposta final e o prompt do agente, caso a caso.
- **Q4 filtra por `atingimento`** (fracao bruta), nao por `nota` (ja
  truncada pela R6) -- sao equivalentes no resultado final pra essa
  pergunta especifica, mas a tool consulta o campo certo, nao um efeito
  colateral.
- **"Vendas Oeste" (Q5) nao existe na base** -- as areas de Vendas reais
  sao "Coordenacao Vendas Sul" e "Coordenacao Vendas Norte" (confirmado
  contra `area` real e contra `area.csv`). E um teste de honestidade do
  agente: a tool devolve `status="nao_encontrado"` e o prompt instrui o
  agente a dizer isso claramente, nunca a "arredondar" pra Sul ou Norte.

## Como rodar

```bash
pip install -r requirements.txt
set ANTHROPIC_API_KEY=sua-chave-aqui      # PowerShell: $env:ANTHROPIC_API_KEY="..."
python agent.py "Qual o score da Gerencia de Marketing?"
python run_perguntas.py                    # roda as 5 obrigatorias, gera respostas.md
```

Pre-requisito: SQL Server local com o banco `CaseMereo` carregado
(staging/intermediate/marts), ODBC Driver 17 instalado, autenticacao
Windows (mesma string de conexao do `etl/extract_load.py`).

Se `agent.py` reclamar do nome do modelo (`anthropic:claude-sonnet-5`),
defina a env var `MEREO_AGENT_MODEL` com o nome correto pra versao do
pydantic-ai instalada -- nomenclatura de modelo muda com frequencia.

## Comentario do Eduardo (onde acertou / errou / o que melhoraria)

_[Preencher depois de rodar `run_perguntas.py` e revisar `respostas.md`
-- o enunciado pede esse comentario explicitamente, nao e opcional.]_
