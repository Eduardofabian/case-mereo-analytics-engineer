# Agente de IA -- Case Mereo (Grupo Aurora)

Parte 4 do case: agente que responde perguntas sobre os resultados do
ciclo 2025 em linguagem natural.

## Arquivos

Ordem de leitura/execução (pipeline, não alfabética):

| Arquivo | O que é |
|---|---|
| `requirements.txt` | dependências (`pydantic-ai`, `duckdb`) |
| `dados/` | 8 CSVs (`marts.*`) -- entrada, gerados por `etl/run_pipeline.py` |
| `db.py` | conexão DuckDB singleton + resolução de nome por `ILIKE` (3 casos) |
| `tools.py` | as 6 consultas fixas e parametrizadas (a camada que o LLM não escreve) |
| `agent.py` | `Agent` do Pydantic AI, registra as 6 tools, system prompt, CLI |
| `run_perguntas.py` | roda as 5 perguntas obrigatórias, grava `respostas.md` |
| `respostas.md` | saída -- as 5 respostas reais + comentário de acerto/erro/melhoria |
| `README.md` | este arquivo |

## Arquitetura

Tool-calling com funcoes Python fixas e parametrizadas (Pydantic AI + API
Anthropic), **nunca** text-to-SQL -- requisito explicito do enunciado
("o agente deve usar ferramentas... em vez de gerar SQL livre a cada
pergunta"). O agente decide qual ferramenta chamar e com quais
argumentos; a query em si esta sempre escrita de antemao em `tools.py`.
A unica coisa que varia por chamada e: um nome (resolvido via busca
parcial, nunca interpolado em SQL fora de um placeholder `?`), um limite
numerico, ou um enum fechado (`"abaixo"/"acima"`, `"direto"/"consolidado"`,
`"melhor"/"pior"`) que mapeia pra um fragmento de SQL fixo escolhido em
Python -- nunca pra uma string de operador/coluna vinda livre do texto
da pergunta.

**Fonte de dados: CSVs materializados, nao SQL Server.** A primeira
versao deste agente conectava direto no SQL Server local (`pyodbc`,
`Trusted_Connection=yes`) -- funcionava, mas so na maquina de quem montou
o pipeline, ninguem mais conseguiria rodar. A correcao: as tools leem os
CSVs em `dados/`, que sao a materializacao exata das views `marts.*`
ja validadas contra o SQL Server -- carregados num DuckDB em memoria na
inicializacao. As tools **nunca recalculam** regra de negocio (R4-R11) em
Python; so leem o resultado ja calculado e validado em SQL. Isso elimina
qualquer dependencia de SO/driver/instancia: Python + os CSVs (ja
inclusos nesta pasta) bastam, em qualquer maquina.

Arquivos:
- `db.py` -- conexao DuckDB singleton, registra uma view por CSV de
  `dados/`, + `resolver_por_nome`, a funcao compartilhada por todas as
  tools que recebem nome de pessoa ou area. Trata 3 casos: nao
  encontrado, um match, varios matches -- nunca "pega o primeiro".
- `tools.py` -- as 6 consultas fixas (ver tabela abaixo).
- `agent.py` -- define o `Agent` do Pydantic AI, registra as 6 tools via
  `@agent.tool`, e o system prompt com as regras de como reagir a cada
  status (nao_encontrado, multiplos_candidatos, sem_score, etc.).
- `run_perguntas.py` -- roda as 5 perguntas obrigatorias do case e grava
  `respostas.md`, com a resposta real da rodada + um comentario fixo
  (dict `COMENTARIOS`, embutido no script pra nao se perder a cada rerun,
  ja que `respostas.md` e sobrescrito toda vez).
- `respostas.md` -- gerado por `run_perguntas.py`: as 5 respostas reais +
  comentario de onde acertou/errou/o que melhoraria em cada uma.
- `dados/` -- 8 CSVs materializados das views `marts.*` (ver "Dados"
  abaixo).

## Tools

| Tool | Parametros | Cobre |
|---|---|---|
| `score_colaborador` | `nome_colaborador` | variacao livre |
| `score_area` | `nome_area` | Q1, Q5 |
| `score_gestor` | `nome_gestor` | variacao livre |
| `colaboradores_do_time_por_score` | `nome_gestor`, `limite`, `comparador` | Q2 |
| `ranking_areas` | `nivel`, `criterio`, `ordem`, `top_n` | Q3 |
| `metas_colaborador_por_atingimento` | `nome_colaborador`, `limite`, `comparador` | Q4 |

## Decisoes de design

- **"Time de um gestor" = `id_gestor` direto** (campo da tabela
  colaborador), nao hierarquia de area.
- **`score_area` sempre devolve `score_direto` e `score_consolidado`**
  juntos, nunca um default escolhido pelo codigo -- quem decide o que
  destacar na resposta final e o prompt do agente, caso a caso.
- **Q4 filtra por `atingimento`** (fracao bruta), nao por `nota` (ja
  truncada pela R6) -- sao equivalentes no resultado final pra essa
  pergunta especifica, mas a tool consulta o campo certo, nao um efeito
  colateral. Isso exigiu que `marts.vw_nota_meta` tambem fosse exportada
  (ver "Dados" abaixo) -- as outras 7 views de `marts.*` nao tem
  atingimento/nota.
- **"Vendas Oeste" (Q5) nao existe na base** -- as areas de Vendas reais
  sao "Coordenacao Vendas Sul" e "Coordenacao Vendas Norte" (confirmado
  contra `area` real no SQL Server e contra `area.csv`). E um teste de
  honestidade deliberado do enunciado: a tool devolve
  `status="nao_encontrado"` e o prompt instrui o agente a dizer isso
  claramente, nunca a "arredondar" pra Sul ou Norte.
- **Resolucao de nome (`ILIKE`) e case-insensitive mas sensivel a
  acento** -- "Gerencia" (sem acento) nao bate com "Gerência". Limitacao
  conhecida, nao corrigida (normalizar acento mudaria o comportamento de
  match de forma mais ampla do que o escopo deste case pede); documentada
  aqui pra quem for operar o agente depois.

## Dados (`dados/`)

8 CSVs, materializacao exata das views `marts.*` ja validadas no SQL
Server: `dim_area`, `dim_colaborador`, `dim_meta`,
`fact_meta_valor_mensal`, `vw_score_colaborador`, `vw_score_area`,
`vw_score_gestor` e `vw_nota_meta` (essa ultima exportada
especificamente pra alimentar a Q4 do agente).

Pra regerar, caso os dados do SQL Server mudem -- `etl/run_pipeline.py`
roda o pipeline inteiro (staging → intermediate → marts) e ja copia os
CSVs atualizados pra `agente/dados/` como ultimo passo, sem precisar de
copia manual:
```powershell
cd "C:\Users\Fabian\Desktop\MEREO CASE\etl"
python run_pipeline.py
```

## Como rodar

```bash
pip install -r requirements.txt
set ANTHROPIC_API_KEY=sua-chave-aqui      # PowerShell: $env:ANTHROPIC_API_KEY="..."
python agent.py "Qual o score da Gerência de Marketing?"
```

Rodar as 5 obrigatorias de uma vez (gera `respostas.md`):
```bash
python run_perguntas.py
```

Nao precisa de SQL Server, driver ODBC nem autenticacao Windows --
so Python 3.11+, as dependencias do `requirements.txt` e os CSVs de
`dados/` (ja inclusos nesta entrega).

Se `agent.py` reclamar do nome do modelo (`anthropic:claude-sonnet-5`),
defina a env var `MEREO_AGENT_MODEL` com o nome correto pra versao do
pydantic-ai instalada -- nomenclatura de modelo muda com frequencia.

## Limitacao conhecida: ninguem alem de mim roda isso com a chave default

O codigo nao executa sem uma `ANTHROPIC_API_KEY` valida -- isso e
universal pra qualquer agente baseado em LLM via API paga, e o proprio
enunciado ja assume isso ("se nao tiver acesso a uma API de LLM, use um
plano gratuito... entregue as ferramentas implementadas, o prompt e a
explicacao"). Nao e uma falha de arquitetura do agente: e a mesma
barreira que qualquer entrega desse tipo tem. Por isso as respostas reais
das 5 perguntas obrigatorias estao gravadas em `respostas.md` -- essa e
a evidencia de que o agente funciona, nao a expectativa de que quem
avalia va rodar o codigo com a propria chave.

## Onde acertou, onde errou, o que eu melhoraria

Resumo; o detalhe pergunta a pergunta esta nos comentarios de
`respostas.md` (gerados junto com cada resposta real, dict `COMENTARIOS`
em `run_perguntas.py`).

**Acertou nas 5/5**, numeros conferidos de forma independente contra os
CSVs (nao so "o agente disse que esta certo"):
- Q1 (score Gerencia de Marketing), Q2 (time Sofia Oliveira < 90), Q3
  (melhor diretoria consolidado) e Q4 (metas Nicolas Vasconcelos < 80%)
  bateram exatamente com os valores calculados direto dos CSVs.
- Q5 (Vendas Oeste) e o teste mais importante dos 5: a area nao existe
  na base, e o agente nao alucinou um numero pra Vendas Sul ou Norte --
  disse que nao encontrou e pediu confirmacao do nome. Prova que a
  decisao de design (`resolver_por_nome` nunca "pega o primeiro",
  `status="nao_encontrado"` tratado explicitamente no prompt) funciona
  na pratica, nao so na teoria.

**Errou uma vez, mas por bug meu de teste, nao do agente**: na primeira
rodada, Q1 falhou porque eu tinha escrito "Gerencia" sem acento no
roteiro de perguntas -- `ILIKE` e case-insensitive mas nao remove
acento. O comportamento do agente diante da falha foi o correto mesmo
assim (nao achou, nao chutou, pediu confirmacao); o erro de origem era
meu. Corrigido.

**Inconsistencia real encontrada**: a EXPLICACAO da Q4 mudou entre
rodadas pro mesmo resultado numerico -- uma vez o agente tratou "nota
zero" como suposicao ("provavelmente por estarem abaixo de algum limiar
minimo"), outra vez citou a regra R6 com certeza. Mesmos dados, mesma
tool, explicacao diferente, porque o system prompt nunca deu as regras
de negocio ao agente, so os numeros ja calculados -- quando ele tenta
explicar o *porque*, as vezes acerta por inferencia, as vezes especula.

**O que eu faria pra melhorar**:
1. Colocar um resumo das regras-chave (pelo menos R6, talvez R9-R11) no
   system prompt, pra tirar essa variancia de explicacao e o agente
   responder com certeza sempre, nao por sorte.
2. Normalizar acento na resolucao de nome (`unaccent` ou equivalente no
   DuckDB), pra "Gerencia" bater com "Gerência" sem exigir grafia exata.
3. Golden set de regressao automatizado: hoje a validacao das 5
   perguntas e manual (eu rodando e comparando a mao); um teste que roda
   as tools direto (sem LLM) contra os CSVs e falha se o numero mudar
   seria mais barato de manter que reler o `.md` toda vez -- foi
   exatamente esse tipo de checagem que usei pra validar a migracao de
   `intermediate.vw_nota_meta` pra `marts.vw_nota_meta` sem gastar
   chamada de API.
