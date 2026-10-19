# Case Mereo: Grupo Aurora (Analytics Engineer Pleno)

Resultado de cada colaborador, área e gestor do ciclo 2025, a partir da base
`case_metas.db` fornecida, com os problemas de qualidade da base mapeados e
as decisões de tratamento justificadas.

## Uso de IA neste case

Usei o Claude (Anthropic) como par técnico durante todo o desenvolvimento:
modelagem das camadas SQL (staging/intermediate/marts), tradução das regras
de negócio do enunciado em T-SQL, geração da bateria de checagens de
qualidade em `etl/verificacao/diag_qualidade.py`, e revisão crítica dos resultados:
cada número de P1/P2/P3 foi conferido manualmente (recálculo de média
ponderada na mão, verificação de hierarquia de área contra `staging.area`,
contagem de gestores válidos, simulação de sensibilidade excluindo os
lançamentos pós-desligamento) antes de aceitar como correto, não só aceito
porque o SQL rodou sem erro. A revisão também encontrou um script Python
(`etl/load.py`) que ficou desatualizado em relação à estrutura final do
banco (referenciava um schema `dbo.stg_*` de uma arquitetura anterior,
substituída durante o desenvolvimento), identificado e removido do
repositório. As decisões de tratamento de
dado (peso negativo, denominador zero, lançamento pós-desligamento, meta
compartilhada com lançamento próprio) foram meu julgamento, documentado
abaixo caso a caso: a IA ajudou a identificar o padrão e propor a regra,
mas a decisão de qual regra aplicar foi minha.

O mesmo processo se repetiu nas outras frentes do case: o protótipo HTML/Figma, os tropeços reais de Power BI documentados na seção **Painel: processo de decisão**, a arquitetura do agente (ferramentas fixas em vez de SQL livre, como a Parte 4 explica) e as três respostas da Parte 5 foram todos desenvolvidos com o Claude como par técnico: proposta de abordagem seguida de teste e crítica, não aceitação automática. Como artefato adicional de uso de IA, este repositório também inclui duas
skills de auditoria específicas deste case (`skills/`), detalhadas a seguir.

### Skills de auditoria customizadas

Já tinha duas skills genéricas de auditoria de hackathon disponíveis, mas
elas avaliam contra critérios genéricos de datathon, não contra os 6
critérios e pesos exatos deste enunciado (30/20/20/15/10/5), nem contra
as regras de negócio específicas (R1-R11) ou o padrão visual real do
produto Mereo (semáforo, matriz Direto/Consolidado). Usar a skill
genérica teria produzido uma auditoria superficial, sem citar números
reais do projeto nem confrontar a Parte 1 com uma reimplementação
independente.

Por isso criei duas skills específicas deste case:

- `auditoria-entrega-mereo`: lê o repositório inteiro, reexecuta
  `verificacao_independente.py` e compara número a número contra
  `respostas/`, e audita contra os 6 critérios e pesos exatos do
  enunciado.
- `auditoria-dashboard-mereo`: audita fidelidade do painel ao star
  schema e ao padrão visual real do produto Mereo.

Rodei a `auditoria-entrega-mereo` duas vezes: a primeira apontou 84/100
com gaps específicos (peso negativo não documentado, matriz de áreas
cortada, caminhos obsoletos da reorganização, comentários do agente
desatualizados); apliquei as correções e a segunda rodada confirmou
91/100, com os três achados remanescentes também corrigidos antes do
commit final. Os dois relatórios ficam versionados em `_review/` como
evidência do processo.

A `auditoria-dashboard-mereo` foi rodada ao final, depois de várias
correções manuais feitas junto com o par técnico durante a tarde
(hierarquia de área, ausência de scroll, consistência dos rótulos). Deu 84/100 (bom, sem bloqueadores), com 3 achados médios: a colisão
de cor (vermelho/laranja com dois significados) foi corrigida em `10c1453`;
os outros dois (matriz sem recuo hierárquico, Top/Bottom de gestores fixo
por nome) seguem registrados em "Limitações conhecidas" por decisão de
tempo. O relatório está em `_review/dashboard_audit_20261019.md`.

## Estrutura do repositório

```
README.md
requirements.txt           -- dependências dos 3 componentes (pipeline/agente/painel), 3 blocos comentados
verificar_ambiente.py      -- confere o que está instalado antes de rodar, aponta o que falta
sql/
  00_drop_all.sql          -- reset completo (view + tabela), útil em re-execução
  01_setup/                -- CREATE DATABASE, CREATE SCHEMA
  02_staging/               -- tabelas cruas, espelho do SQLite
  03_intermediate/          -- resolução de regra (R2, R3, R7, hierarquia de área)
  04_marts/                 -- camada gold, o que Dashboard/Agente consomem
  05_respostas/              -- as 3 queries finais que geram os CSVs
respostas/
  p1_score_colaborador.csv
  p2_score_area.csv
  p3_gestores.csv
etl/
  extract_load.py           -- carga de staging.* a partir do SQLite
  export_marts.py           -- exporta marts.* para CSV (painel/dados/, agente/dados/)
  export_respostas.py       -- roda as 3 queries de P1/P2/P3 e exporta CSV (script correto)
  run_pipeline.py           -- entrypoint: staging -> intermediate -> marts -> export, ponta a ponta
  verificacao/
    diag_qualidade.py         -- gera verificacao/relatorio_diagnostico.md
    relatorio_diagnostico.md  -- 38 checagens sistemáticas rodadas contra o banco
    achados_qualidade_chat1.md -- achados da primeira varredura (Python/pandas), ver nota abaixo
    verificacao_independente.py -- recomputa P1/P2/P3 em pandas direto do SQLite e compara com os CSVs
    sensibilidade_matriz.py   -- sensibilidade pós-desligamento em 4 definições (colaborador/área/gestor)
material_original/
  ENUNCIADO.pdf, ENUNCIADO.docx, dados/  -- material recebido, como veio
painel/
  streamlit/prototipo_streamlit.py  -- protótipo 1: 3 layouts, só pra decidir ESCOPO (conteúdo)
  html/painel_mereo_final.html      -- protótipo 2: mockup fixo 1280x720, decidir APARÊNCIA (ponte pro Figma)
  powerbi/                          -- entrega final
    Dashboard/Dashboard_case_mereo.pbip  -- projeto Power BI (formato .pbip, versionável)
    powerbi_construcao_painel.md    -- construção completa: modelo, paleta/tipografia, DAX e visual card a card
                                       (como ficou de fato no .pbip, com o que divergiu do plano original)
    assets/                         -- imagem de fundo e logo usados no import do Figma pro Power BI
  dados/                            -- CSVs que o Power BI consome por caminho absoluto (não mover);
                                       versionados de propósito, pra abrir o .pbip sem rodar o pipeline
  entrega/Mereo_Case_Dashboard_Pwbi.png  -- print final do painel (entregável da Parte 3)
  analise_resultados.md             -- interpretação dos resultados, insumo comum às 3 etapas
  diagramas/Mereo_Grupo_Aurora.{sql,svg,png}  -- diagrama ER do modelo (star schema que o painel consome)
agente/                    -- agente de IA (Parte 4, ver seção própria abaixo)
  db.py                    -- conexão DuckDB singleton + resolução de nome (ILIKE, 3 casos)
  tools.py                 -- as 6 consultas fixas e parametrizadas
  agent.py                 -- Agent do Pydantic AI, registra as 6 tools, system prompt
  run_perguntas.py         -- roda as 5 perguntas obrigatórias, grava respostas.md
  respostas.md             -- as 5 respostas reais + comentário de acerto/erro/melhoria
  dados/                   -- 8 CSVs (marts.*), tornam o agente self-contained, sem SQL Server
skills/
  auditoria-entrega-mereo/    -- skill de auditoria da entrega (Claude Code), critérios e pesos exatos do enunciado
  auditoria-dashboard-mereo/  -- skill de auditoria do painel, star schema e padrão visual real do produto Mereo
```

**Nota histórica, `etl/load.py` (removido):** o repositório teve, numa fase
anterior, um segundo script de carga (`load.py`) que referenciava uma
estrutura de schema antiga (`dbo.stg_area`, `dbo.stg_colaborador` etc.) e
pastas `sql/staging/`, `sql/intermediate/`, `sql/marts/` no formato antigo,
uma arquitetura substituída durante o desenvolvimento. Rodar esse script
hoje falharia (arquivos que ele procura não existem mais) ou, pior,
escreveria num schema `dbo.stg_*` desconectado do pipeline validado em
`staging/intermediate/marts`. Removido do repositório; `extract_load.py` é
e sempre foi o script correto para esse passo (carga de `staging.*`).

**Nota sobre `etl/verificacao/achados_qualidade_chat1.md` vs `etl/verificacao/relatorio_diagnostico.md`:**
o primeiro foi gerado numa fase inicial, validado em Python/pandas direto
sobre os CSVs, sem rodar contra o SQL Server de fato (diz isso explicitamente
no próprio arquivo). O segundo é uma bateria de 38 checagens sistemáticas
rodada depois, contra o banco. Os números que os dois têm em comum (lançamento
duplicado, nulo, peso negativo) foram conferidos neste README contra o banco
real e batem exatamente. Os achados abaixo usam o relatório de diagnóstico
como fonte primária.

## Arquitetura dos dados

Três camadas, cada uma um schema no SQL Server:

- **staging**: espelho cru do SQLite, sem tratamento nenhum.
- **intermediate**: resolve as regras de negócio (dedup R2/R3, resolução de
  meta compartilhada R7, fechamento de hierarquia de área). Não é consumido
  fora do pipeline.
- **marts**: camada final. `dim_area`, `dim_colaborador`, `dim_meta`,
  `fact_meta_valor_mensal`, e as três views de score
  (`vw_score_colaborador`, `vw_score_area`, `vw_score_gestor`); é daqui que
  Dashboard, Agente de IA e os CSVs de `respostas/` leem.

### Processo: Discovery, Design, Develop, Delivery

- **Discovery**: exploração inicial da base (`material_original/dados/`):
  volumetria, hierarquia de área, tipos de meta, e a bateria de checagens
  de qualidade que gerou os achados documentados abaixo.
- **Design**: modelagem do star schema (`dim_area`, `dim_colaborador`,
  `dim_meta`, `fact_meta_valor_mensal` + as 3 views de score) e o diagrama
  ER em `painel/diagramas/Mereo_Grupo_Aurora.{sql,svg,png}`, desenhado no
  [dbdiagram.io](https://dbdiagram.io).
- **Develop**: implementação em T-SQL puro das camadas
  `staging → intermediate → marts`, no padrão de modelagem em camadas
  popularizado pelo dbt, não a ferramenta dbt em si (não usada neste
  case; orquestração é manual, via `etl/run_pipeline.py`).
- **Delivery**: export para os CSVs de `respostas/` (Parte 1), `painel/dados/`
  (Power BI) e `agente/dados/` (agente de IA), todos na mesma rodada de
  `run_pipeline.py`.

### Próximo passo: ingestão via API (arquitetura futura)

O pipeline atual é batch, a partir do SQLite fornecido. Se o Grupo Aurora
passar a enviar dados diariamente via API (ver Parte 5, pergunta 1, para a
justificativa completa), o próximo passo seria: endpoint de API →
Azure Blob Storage (grava o payload bruto, permite reprocessar sem pedir
reenvio) → Azure Function (valida schema/regras básicas, separa quarentena)
→ carga em `staging` via merge/upsert → `intermediate`/`marts` como já
validado hoje. Não implementado neste case; é a evolução natural do
pipeline batch atual, não uma mudança de modelo de dados.

Ordem de execução dos scripts em `sql/`: `00_drop_all.sql` (opcional, só se
já existir algo no banco) → `01_setup/` → `02_staging/` (+ carga dos dados
via `etl/extract_load.py`) → `03_intermediate/` → `04_marts/` → `05_respostas/`.
Cada view usa `IF OBJECT_ID(...) IS NOT NULL DROP VIEW` + `CREATE VIEW`, então
é seguro rodar de novo sem duplicar objeto.

## Regras de negócio: decisões de interpretação

A maioria das 11 regras (R1-R11) é direta. As que exigiram uma decisão
porque o enunciado não cobre o caso exato da base:

- **R6/R8, denominador zero:** regra não prevê atingimento indefinido
  (`soma(previsto)=0` numa meta de Acumulação Soma, por exemplo). Tratado
  como extensão de R8: sem nota, meta não entra no score. Aplicado de
  forma genérica no SQL (`CASE WHEN ... <> 0 THEN ... ELSE NULL END`), não
  hardcoded para um id específico, então qualquer dado novo com o mesmo
  problema cai no mesmo tratamento automaticamente.
- **Peso negativo:** nenhuma regra prevê peso negativo (inverteria o peso
  da meta no cálculo). Decisão: `peso_efetivo = ABS(peso)`. Alternativa
  considerada: excluir a meta, no espírito de R8 (tratar como meta sem
  peso válido). Escolhi ABS porque os dados apontam para erro de sinal na
  importação, não para regra de negócio: a meta 5286 ("Inadimplência (%)",
  colaborador 174) é o único peso negativo entre as 376 metas; as 4 metas
  do 174 têm pesos 20, -5, 50 e 25, que somam 90 com o sinal e exatamente 100
  com +5; e a mesma meta "Inadimplência (%)" aparece para outros 8
  colaboradores em 2025 (168, 169, 172, 176, 178, 179, 180, 181), todos com
  peso positivo (30, 20, 20, 10, 35, 75, 50, 25). A soma 100 por
  colaborador é o padrão dominante, não universal: 75 dos 81 colaboradores
  de 2025 somam 100 (contando o 174 com ABS) e os 30 de 2024 também; os 6
  restantes somam entre 85 e 120 (ver achado de soma de peso ≠ 100 abaixo).
  Por isso trato como erro provável, não comprovado. Impacto medido
  (`verificacao_independente.py` com a meta 5286 excluída): colaborador 174
  vai de 51.42 (ABS, entregue) para 49.14 (2.28 pontos); área 11 varia
  0.23 e o gestor 171 (top 1 de P3) 0.25; top 3/bottom 3 de P3 não mudam.
- **Lançamento em mês posterior ao desligamento:** o enunciado não pede
  exclusão desses lançamentos, e R3/R8 não cobrem esse caso, só olham
  `nao_se_aplica`/`previsto`/`realizado`. Decisão: manter literal no
  cálculo (não inventar uma regra de corte que o enunciado não pede),
  documentando esses lançamentos à parte para auditoria. Validado por
  simulação: ver análise de sensibilidade abaixo; o impacto é pequeno.
- **Meta compartilhada com lançamento mensal próprio:** R7 é explícito:
  usa lançamentos da referência, não os próprios. Mesmo havendo lançamento
  próprio na base (achado abaixo), ele é ignorado por construção: o join
  da camada de nota é feito por `id_meta_lancamentos`, que para toda meta
  Compartilhada aponta pra referência, nunca pro próprio id. Confirmado
  com query direta contra o banco que zero desses lançamentos vazam no
  cálculo.

## Achados de qualidade

Validado contra o banco real nesta sessão (não só contra CSV/pandas):

**Nota de processo, quase-regressão pega antes da entrega:** durante o
ajuste da definição de "pós-desligamento" (fim de mês → início de mês, ver
view de quarentena abaixo), uma versão intermediária de
`intermediate.lancamento_valido` acabou embutindo a exclusão de
pós-desligamento direto no `flag_valido`, que `marts.fact_meta_valor_mensal`
lê de forma direta. Isso teria revertido silenciosamente a decisão já
fechada ("manter literal no cálculo"), sem nenhum erro de sintaxe pra
avisar. Rodando a query de verificação com essa versão (com o bug ainda
ativo) nesta sessão, o resultado real era `flag_valido`: 343 inválidos /
3245 válidos (343 = 181 originais + 162 pós-desligamento recém-excluídos,
3245 + 343 = 3588 = total de lançamentos). Em algum ponto da conversa esse
número foi transcrito incorretamente como "362" ao resumir o resultado em
texto: um erro de leitura da tela, não um terceiro número real nem
inconsistência do pipeline. Revertido antes de gerar qualquer CSV nesse
estado, e reconfirmado nesta sessão contra o banco ao vivo: `flag_valido`
hoje é **181 inválidos / 3407 válidos**, só R2+R3, sem a condição de
desligamento, exatamente como antes do incidente: 181 + 162 = 343
(inválido sobe ao aplicar o bug) e 3407 - 162 = 3245 (válido desce na
mesma proporção), consistente nos dois sentidos. Separadamente, a
contagem de `lancamento_rejeitado` por categoria foi recalculada e
confere: `duplicado_perdedor`=45, `lancamento_pos_desligamento`=162 (=24
elegíveis + 138 não elegíveis), `previsto_ou_realizado_nulo`=43; bate com
a tabela abaixo e com os achados já documentados.

| Achado                                                                                         | Qtd                            | Decisão                                                                                                           |
| ---------------------------------------------------------------------------------------------- | ------------------------------ | ------------------------------------------------------------------------------------------------------------------ |
| Lançamento duplicado (id_meta, mês)                                                          | 45 pares (90 registros brutos) | R2: mantido o de `data_lancamento` mais recente                                                                  |
| `nao_se_aplica=0` mas previsto/realizado nulo                                                | 43                             | R3 já exclui do cálculo                                                                                          |
| Lançamento em mês pós-desligamento, colaborador elegível (R10)                             | 24                             | Mantido literal no cálculo; impacto medido (ver sensibilidade abaixo)                                             |
| Lançamento em mês pós-desligamento, colaborador não elegível                              | 138                            | Não afeta P1/P2/P3 (colaborador já sai por R10), documentado por completude                                      |
| Meta com denominador=0 (meta 5094, "Leads gerados", colaborador 125, previsto=0 o ano inteiro) | 1                              | Extensão de R8: sem nota                                                                                        |
| Meta com peso negativo (meta 5286, "Inadimplência (%)", colaborador 174)                      | 1                              | `peso_efetivo = ABS(peso)`: provável erro de sinal; alternativa e impacto (2.28 pts no colab. 174) acima       |
| Meta Compartilhada com lançamento mensal próprio (ids 5066, 5156, 5219, 5231, 5278)          | 60 registros                   | Ignorado por construção (ver acima); confirmado 0 vazamento no cálculo                                          |
| Meta Individual sem nenhum lançamento mensal (ids 5014, 5063, 5146, 5188)                     | 4                              | R8 cobre: sem nota, fora do score                                                                                |
| Colaborador com soma de peso das metas != 100 (varia entre 85 e 120)                           | 7                              | R9 normaliza por soma de peso, não quebra o cálculo; só não assumir 100 no Dashboard/Agente                  |
| `polaridade`/`tipo_acumulacao` nulos na própria linha de meta Compartilhada               | presente                       | Esperado: R7 resolve via `COALESCE` com a referência, o valor próprio nunca é usado quando é Compartilhada |

Checado e confirmado limpo (sem achado): PK duplicada em todas as 5 tabelas,
FK órfã em todas as relações, ciclo na cadeia de gestores, auto-gestor,
gestor fora da hierarquia de área do subordinado, lançamento antes da
admissão, mês fora de 1-12, espaço extra em nome/nome_meta, valores fora do
domínio esperado em tipo_meta/polaridade/tipo_acumulacao.

### Análise de sensibilidade: lançamento pós-desligamento

**Pergunta:** manter literais os lançamentos feitos depois do desligamento
distorce o score de quem está sendo avaliado? O enunciado não define
"pós-desligamento" nem pede exclusão, então testei quatro leituras e
reporto primeiro a mais severa.

Duas escolhas independentes na definição:

- *De quem é o desligamento?* **holder** = o colaborador cuja nota está
  sendo calculada (a pergunta de robustez do score é sobre ele) vs.
  **owner** = o dono da meta que carrega o lançamento. Só divergem nas metas
  Compartilhadas, que usam lançamentos da meta referenciada (R7).
- *Qual a fronteira?* **fim** = o mês termina depois do desligamento
  (mais agressiva) vs. **início** = o mês começa depois (a implementada na
  quarentena).

**Resultado principal, pior caso das quatro testadas (holder / fim):**
a **maior** variação encontrada é de **1.64 ponto** no score de um colaborador, **0.113** no score de uma área (o máximo entre as 11 áreas) e **0.125** no score médio do time de um gestor (o máximo entre os 9). São valores máximos, não médias. O **top 3 / bottom 3 de P3 não muda**, nem a elegibilidade de ninguém.

| Definição                        | colab. que mudam | máx \|Δ\| colaborador | máx \|Δ\| área | máx \|Δ\| gestor (9) | top 3 / bottom 3 de P3 |
| ---------------------------------- | ---------------- | ----------------------- | ----------------- | ---------------------- | ---------------------- |
| **holder / fim (pior caso)** | 4                | 1.64                    | 0.113             | 0.125                  | inalterado             |
| holder / início                   | 4                | 0.96                    | 0.054             | 0.060                  | inalterado             |
| owner / fim                        | 3                | 1.41                    | 0.043             | 0.047                  | inalterado             |
| owner / início (a da quarentena)  | 3                | 0.68                    | 0.007             | 0.007                  | inalterado             |

Detalhe do pior caso (holder / fim; Δ = score atual − score sem os
lançamentos pós-desligamento):

| id_colaborador | Δ score |
| -------------- | -------- |
| 134            | -1.64    |
| 138            | +0.85    |
| 113            | -0.40    |
| 135            | -0.34    |

Nota sobre o 113: ele é o único que diminui ao passar de holder / início
(-0.54) para holder / fim (-0.40). Não é erro de sinal: é efeito do corte
de R6 e de a acumulação por Soma ser razão de somas. Na meta compartilhada
5045 (lançamentos do 101, desligamento do 113 em 02/10/2025), excluir só
nov-dez tira dois meses fracos (atingimento ~82%) e sobe a nota para 92.57;
excluir também outubro tira um mês bom (~97%) e a nota volta a 92.02. As
outras duas metas ficam em 106-107 e 120 (travada em R6), então a diferença
vem toda da 5045. Conferido à mão: 109.93 → 110.47 → 110.32.

Áreas afetadas: 5 (-0.113), 3 (-0.040) e, no consolidado, 1 (-0.046) e
2 (-0.019). Gestores afetados: 129 (-0.125) e 106 (-0.044); todos os
outros dos 9 oficiais em 0. "Pior caso" vale para as quatro leituras
testadas, não para toda definição concebível.

**Por que a view de quarentena usa owner (e a sensibilidade não):** são
duas perguntas diferentes. `intermediate.lancamento_rejeitado` é um
achado de qualidade de dado na origem: "esse lançamento é anômalo porque
foi feito por alguém que já tinha saído", e isso é propriedade do evento
de lançamento, ou seja, do dono da meta que o carrega (owner). Já a
sensibilidade pergunta se o score de quem está sendo avaliado é distorcido,
e isso é propriedade do colaborador pontuado (holder). Em versões
anteriores deste README a sensibilidade herdou o owner da quarentena e
reportou 0.68 como número principal; isso subestimava o efeito e foi
corrigido aqui. Nada em P1/P2/P3 depende dessa escolha: os três usam os
lançamentos literais.

A discussão numérica anterior que citava 0.05 / 1.41 / 0.99 corresponde
à variante owner / fim (mesmos colaboradores, sinal da diferença invertido).

**Universo do gestor:** as comparações usam os 9 gestores oficiais de P3
(ativos em 31/12/2025 e ≥3 subordinados diretos elegíveis). Uma checagem
ad hoc anterior usou 10 por omitir `flag_ativo_fim_2025 = 1`; foi refeita
com o filtro correto (`etl/verificacao/sensibilidade_matriz.py`).

A diluição pela média (de todos os elegíveis da área, ou dos subordinados
diretos do gestor) absorve o desvio pontual do colaborador isolado.
Conclusão: o "raio de dano" da decisão fica contido mesmo na leitura mais
severa; não há necessidade de reportar uma segunda versão de P2/P3.

## Validação de P1/P2/P3

- **Recomputação independente (pandas, sem usar nenhuma view/SQL do
  projeto):** `etl/verificacao/verificacao_independente.py` reimplementa R1-R11 direto
  do SQLite original e compara com os três CSVs de `respostas/`. Resultado:
  P1 (72 linhas), P2 (11) e P3 (6) idênticos, diferença máxima 0.0000, e
  universo de P3 = 9 gestores. Foi a primeira confirmação que não vinha de
  auto-relato do pipeline SQL.
- **Recomputação independente em T-SQL contra `staging` (SQL Server,
  SSMS):** `sql/06_verificacao/verificacao_independente_staging.sql`
  recalcula P1/P2/P3 lendo só `staging.*` (nenhuma view de
  intermediate/marts entra na conta) e compara com `marts.*` no final.
  Rodado após a reorganização final de pastas, contra o banco atual:
  contagens batem (`staging.area`=11, `staging.colaborador`=81,
  `staging.meta`=376, `staging.meta_valor_mensal`=3633), os três níveis
  dão PASS (72 colaboradores elegíveis, 11 áreas, 9 gestores válidos) e a
  diferença máxima fica na casa de 1e-14, erro de arredondamento de ponto
  flutuante, não divergência real; as três tabelas de divergência vêm
  vazias. Segunda confirmação independente, desta vez em T-SQL puro.
- **P1 (score por colaborador):** 72 de 81 colaboradores elegíveis (R10),
  scores no intervalo [0, 120] como R6 define. Recalculei a média ponderada
  na mão para os 5 scores mais baixos (18.17 a 54.85); bateram exatos com
  o SQL. A causa não é dado esparso (10-12 meses válidos em todos os
  casos), é o corte duro de R6 em 80%: quando a meta de maior peso da
  pessoa fica logo abaixo do corte, a nota inteira dela zera.
- **P2 (score por área):** confirmado que `score_direto = score_consolidado`
  exatamente nas 6 áreas-folha da hierarquia (sem área abaixo) e diferem
  nas 5 áreas com filhos; bate 100% com a estrutura real de
  `staging.area` (Diretoria → Gerência → Coordenação).
- **P3 (top/bottom gestores):** os dois filtros (gestor ativo em 31/12/2025
  e ≥3 subordinados diretos elegíveis) **não são decisão nossa, são texto
  literal do enunciado**: "Considere apenas gestores ativos em 31/12/2025
  com pelo menos 3 subordinados diretos elegíveis." (Parte 1, P3). 9
  gestores no total atendem aos dois critérios; top 3 e bottom 3 cobrem 6
  dos 9, sem sobreposição. O filtro de "pelo menos 3" inclui corretamente o
  caso-limite de exatamente 3 subordinados.

## Painel: processo de decisão

**O que o painel mostra e por quê.** A diretoria precisa de três respostas
em uma página: como foi o ciclo (score médio, mediana e elegíveis), onde
está o risco (distribuição por faixa em semáforo: crítico <80, 80-100,
≥100; e a lista nominal da zona crítica), e quem puxa o resultado pra
cima ou pra baixo (área Direto vs Consolidado, Top 5 colaboradores, Top 3 /
Bottom 3 gestores de P3). Ficou de fora o que exigiria contexto que um
painel não dá, por exemplo, destacar a pior gestora, quando metade do efeito vem
de um único desligamento (§2 de `painel/analise_resultados.md`).

O enunciado pede só um painel de uma página, em qualquer ferramenta, com
PDF/print e código-fonte se possível (`painel/entrega/Mereo_Case_Dashboard_Pwbi.png`

+ `painel/powerbi/Dashboard/Dashboard_case_mereo.pbip`). O caminho até a
  entrega final passou por três etapas, cada uma validando algo diferente
  antes de comprometer tempo na próxima: não foi refação, foi sequenciamento
  deliberado de risco.

### Etapa 1. Protótipo Streamlit (`painel/streamlit/`): decidir o quê mostrar

Antes de discutir pixel, cor ou ferramenta, a pergunta era "quais métricas
entram e quais não". O protótipo monta os dados em runtime, fazendo merge de
`painel/dados/vw_score_*.csv` com `dim_*.csv` dentro do próprio script
(sem arquivo intermediário materializado), sem compromisso visual nenhum,
e existe só pra isso: 3 opções de
layout/conteúdo (cards executivos, narrativa vertical, grade densa) pra
comparar o que fazia sentido mostrar pra diretoria. O que essa etapa
resolveu: fechar a lista de 5 blocos de `analise_resultados.md` (score
médio + cobertura, distribuição por faixa, Direto vs Consolidado por área,
Top/Bottom 5 colaboradores, Top/Bottom 3 gestores) e decidir explicitamente
o que **não** entra, por exemplo, o destaque nominal da Olívia Queiroz
como "pior gestora" foi descartado nessa fase porque quase metade do
efeito vem de um desligamento isolado (Paula Cardoso), não de desempenho
sustentado do time (ver §2 de `analise_resultados.md`).

Para rodar o protótipo:

```powershell
python -m streamlit run painel/streamlit/prototipo_streamlit.py
```

(usa `python -m` em vez do comando `streamlit` direto, que depende do
Scripts/ do Python estar no PATH; `python -m` funciona com qualquer
Python ativo que já tenha o pacote instalado). Abre no navegador em
`localhost:8501`; o layout muda pela barra lateral ou por `?opcao=final`,
`?opcao=a` ou `?opcao=b` na URL.

### Etapa 2. Protótipo HTML/Figma (`painel/html/`): decidir a aparência

Com o escopo fechado, o problema virou visual: layout fixo de página única
(1280×720, sem scroll, estilo "painel de sala"), tipografia, paleta,
hierarquia visual dos 6 blocos. Streamlit não dá esse controle fino de
pixel, então `painel_mereo_final.html` serviu de mockup de alta
fidelidade, usado como referência pra um design no Figma. Essa etapa
validou espaçamento, tamanho de fonte por elemento e paleta de cor
(semáforo vermelho/amarelo/verde consistente com a distribuição de score),
documentados em `painel/powerbi/powerbi_construcao_painel.md`: esse
arquivo único substitui as duas specs que existiram antes (uma pré-build,
outra escrita durante a construção): ele documenta o que foi de fato
implementado no `.pbip`, conferido linha a linha no modelo, com os pontos
em que o plano original e o resultado final divergiram marcados
explicitamente (por exemplo: Zona Crítica e Top 5 viraram gráfico de
barras em vez de tabela; Gestores Top/Bottom usam filtro básico manual em
vez do Top N nativo, que nunca funcionou de forma confiável).

### Etapa 3. Power BI (`painel/powerbi/`): a entrega real

O painel final (`Dashboard_case_mereo.pbip`, formato de projeto, versionável
em texto) roda sobre o star schema já validado (`marts`: `dim_area`,
`dim_colaborador`, `vw_score_colaborador/area/gestor`, consumidos via
`painel/dados/*.csv`), sem recalcular nada, só consumindo as views.
Streamlit e HTML foram protótipo de decisão (conteúdo e aparência); Power
BI é a ferramenta de BI de verdade, com modelo de dados, medidas DAX e
Matrix hierárquica real: é o que demonstra a competência que o case
avalia, não o protótipo.

**Tropeços reais na construção do Power BI** (documentados com a mesma
honestidade dos achados de qualidade acima):

- **Linhas fantasma em branco na Matrix de Área (Direto/Consolidado):**
  bug de design meu: a Matrix agrupava a própria linha da área-pai como
  um nível hierárquico "vazio" separado. Corrigido com uma coluna `Is Leaf`
  + medida `Area Atual` + filtro visual.
- **Caso de borda "pai com filho único" (Gerência de Logística):** mesmo
  depois do fix acima, essa área específica continuava perdendo o valor
  Consolidado. Causa: a medida `Area Atual` usava `SELECTEDVALUE`/`COALESCE`,
  que não distingue "nível de grupo ativo" quando o pai tem exatamente um
  filho (sem ambiguidade pra forçar branco). Corrigido trocando para
  `ISINSCOPE`.
- **Top 3/Bottom 3 de gestores:** três bugs encadeados: agregação errada
  no eixo (Contagem em vez de Média), campo "Por valor" do filtro Top N
  configurado com a mesma agregação errada (é um campo separado do eixo,
  fácil de não notar), e uma coluna calculada `Nome do Gestor` construída
  na tabela errada (`dim_colaborador` em vez de `vw_score_gestor`) e na
  direção errada (nome do gestor de cada subordinado, não o nome do
  próprio gestor). Mesmo depois de corrigir os três, o filtro Top N nativo
  nunca funcionou de forma confiável. Decisão final: abandonar o Top N
  nativo e usar filtro básico manual com os 6 nomes exatos de
  `vw_score_gestor.csv`.
- **Katina Oliveira e Nicolas Duarte sem "Score Médio Time":** investigado
  contra `marts.vw_score_gestor` antes de assumir bug: são exclusões
  corretas da própria regra do enunciado (gestor precisa estar ativo em
  31/12/2025 e ter ≥3 subordinados diretos elegíveis); Nicolas falha o
  primeiro filtro, Katina o segundo. Não é falha de dado nem de modelo.

## Parte 4: Agente de IA

Código completo, instruções de uso e decisões de arquitetura estão em
`agente/README.md`. Aqui vai o resumo que a rubrica do enunciado pede
direto: arquitetura de ferramentas, como rodar, respostas às 5 perguntas
obrigatórias, e onde o agente acertou/errou.

### Ferramentas

Requisito do enunciado: "o agente deve usar ferramentas (funções que
executam consultas definidas por você) em vez de gerar SQL livre a cada
pergunta." O agente (Pydantic AI + API Anthropic) nunca gera SQL a
partir do texto da pergunta: ele escolhe entre 6 funções Python fixas
(`score_colaborador`, `score_area`, `score_gestor`,
`colaboradores_do_time_por_score`, `ranking_areas`,
`metas_colaborador_por_atingimento`), cada uma com uma query pré-escrita
em `agente/tools.py`. O único espaço de variação por chamada é um nome
(resolvido por busca parcial via placeholder `?`, nunca interpolado em
SQL), um limite numérico, ou um enum fechado (`"abaixo"/"acima"`,
`"direto"/"consolidado"`) que mapeia para um fragmento de SQL fixo
escolhido em Python. As tools leem as views `marts.*` já validadas (via
CSVs materializados + DuckDB em memória, não conexão direta ao SQL
Server), e nunca recalculam R4-R11 em Python.

### Como rodar

```powershell
cd agente
pip install -r requirements.txt
$env:ANTHROPIC_API_KEY="sua-chave-aqui"
python run_perguntas.py
```

Gera `agente/respostas.md` com as 5 respostas reais. Não depende de SQL
Server, driver ODBC nem autenticação Windows, só Python e os CSVs já
inclusos em `agente/dados/` (self-contained por decisão de arquitetura;
ver `agente/README.md`, seção "Fonte de dados").

### Respostas às 5 perguntas obrigatórias

| # | Pergunta                                        | Resposta                                                                                    |
| - | ----------------------------------------------- | ------------------------------------------------------------------------------------------- |
| 1 | Score da Gerência de Marketing?                | 84,43 (área sem subárea, direto = consolidado)                                            |
| 2 | Time da Sofia Oliveira com score < 90?          | Sabrina Cardoso (54,85), Manuela Oliveira (63,67), Gabriela Ferraz (89,30)                  |
| 3 | Diretoria com melhor consolidado?               | Diretoria Financeira (103,30)                                                               |
| 4 | Metas do Nicolas Vasconcelos < 80% atingimento? | "Número de reuniões qualificadas" (70,19%), "Leads gerados" (77,07%), nota 0,0 nas duas |
| 5 | Score da área Vendas Oeste?                    | Não existe na base; áreas de Vendas reais são Coordenação Vendas Sul e Norte         |

Texto completo de cada resposta (como o agente respondeu, não resumido)
em `agente/respostas.md`.

### Onde acertou, onde errou, o que eu melhoraria

**Acertou nas 5/5.** Números conferidos de forma independente contra os
CSVs, não só aceito porque o agente disse que estava certo. A Q5 é o
teste mais importante: "Vendas Oeste" não existe na base, e o agente não
alucinou um número para Vendas Sul ou Norte, disse que não encontrou e
pediu confirmação do nome. É a prova de que a decisão de design
(`resolver_por_nome` nunca "pega o primeiro", status `nao_encontrado`
tratado explicitamente no prompt) funciona na prática.

**Errou uma vez, mas por bug meu de teste, não do agente**: na primeira
rodada, a Q1 falhou porque escrevi "Gerencia" sem acento no roteiro de
perguntas: `ILIKE` é case-insensitive mas não remove acento, então não
bateu com "Gerência" no banco. O comportamento do agente diante da falha
foi o correto mesmo assim (não achou, não chutou, pediu confirmação); o
erro de origem era meu, não dele. Corrigido.

**Inconsistência real encontrada, essa sim do agente**: a explicação da
Q4 mudou entre rodadas para o mesmo resultado numérico: uma vez tratou
"nota zero" como suposição ("provavelmente por estarem abaixo de algum
limiar mínimo"), outra vez citou a regra R6 com certeza. Mesmos dados,
mesma tool, explicação diferente, porque o system prompt nunca deu as
regras de negócio ao agente, só os números já calculados; quando ele
tenta explicar o *porquê*, às vezes acerta por inferência, às vezes
especula.

O que eu faria para melhorar: (1) colocar um resumo das regras-chave
(pelo menos R6) no system prompt, para tirar essa variância de
explicação; (2) normalizar acento na resolução de nome, para "Gerencia"
bater com "Gerência" sem exigir grafia exata; (3) um golden set de
regressão automatizado rodando as tools direto contra os CSVs, sem LLM:
foi esse tipo de checagem (não uma chamada de API) que usei para validar
a migração de `intermediate.vw_nota_meta` para `marts.vw_nota_meta` sem
gastar tempo nem custo de token.

## Dependências

Um único `requirements.txt` na raiz, dividido em blocos comentados por
componente; só o primeiro é obrigatório pra gerar P1/P2/P3:

- **Pipeline SQL** (obrigatório): `pyodbc`, `pandas`, `numpy`
- **Agente de IA** (`agente/`): `pydantic-ai`, `duckdb`
- **Painel** (`painel/streamlit/prototipo_streamlit.py`): `streamlit`

`pip install -r requirements.txt` instala os três blocos. Pra instalar só
o necessário pro pipeline: `pip install pyodbc pandas numpy`.

`python verificar_ambiente.py` confere o que está instalado: Python,
pacotes dos três blocos, driver ODBC, conexão com o SQL Server e presença
do dado de origem, e diz exatamente o que falta e o comando pra resolver.
Falta de algo do pipeline bloqueia (`exit code 1`, porque impede gerar
P1/P2/P3); falta de algo do agente ou do painel só avisa, porque são
opcionais dependendo do que se quer rodar.

## Como reproduzir

0. Colocar os arquivos de dados recebidos no case em
   `material_original/dados/` (não versionado neste repo, é dado de
   origem fornecido no próprio enunciado, arquivo `.db`/`.xlsx` volumoso;
   ver `.gitignore` e a seção **Limitações conhecidas** no final deste
   README).
1. `pip install -r requirements.txt` (instala os três blocos: pipeline,
   agente e painel). Opcional: `python verificar_ambiente.py` pra conferir
   o ambiente antes de rodar.
2. `python etl/run_pipeline.py`: cria banco e schemas no SQL Server (se
   não existirem), roda `staging → intermediate → marts` na ordem certa de
   dependências, carrega os dados do SQLite e exporta os CSVs de
   `marts.*` para `painel/dados/` e `agente/dados/`.
3. `python etl/export_respostas.py`: gera os três CSVs oficiais da
   entrega em `respostas/` (`p1_score_colaborador.csv`,
   `p2_score_area.csv`, `p3_gestores.csv`).

Pra resetar o banco do zero antes do passo 2, rodar `sql/00_drop_all.sql`
no SSMS primeiro.

Para rodar só o diagnóstico de qualidade (gera
`etl/verificacao/relatorio_diagnostico.md`):

```
python etl/verificacao/diag_qualidade.py
```

## Parte 5: Perguntas abertas

### 1. O Grupo Aurora quer enviar os dados de colaboradores todos os dias via API. Como você desenharia essa integração e o pipeline até o Data Warehouse?

O primeiro cuidado é separar quem recebe o dado de quem valida e carrega: um endpoint de API com contrato formal contendo schema versionado, autenticação e idempotência por chave de negócio recebe o payload diário e grava no Azure Blob Storage, o que permite reprocessar um lote problemático sem pedir reenvio. O evento de blob criado dispara uma Azure Function que valida schema e regras básicas, separando o que passa do que vai para quarentena com motivo registrado. A carga em staging no SQL Server precisa ser merge/upsert, porque dado do mundo real repete e corrige registros com frequência maior do que se espera. Dali em diante, o pipeline segue em camadas versionadas, com log de execução e alerta por etapa. Neste projeto essa parte já roda: `etl/run_pipeline.py` leva staging a intermediate e marts (hoje manual; em produção, disparado pela Function ou por um agendador), e as checagens de `diag_qualidade.py` viram as regras da Function de validação.

### 2. O agente da Parte 4 entrou em produção. Como você saberia que ele está respondendo errado?

Sem alguém testando cada resposta, o erro raramente aparece como "o agente disse algo errado na cara". Os sinais reais são mais sutis: usuário reformulando a mesma pergunta várias vezes seguidas, taxa de respostas com status de erro da ferramenta subindo num período, ou negócio reclamando de um número que deveria ter sido pego antes de chegar até ele. Eu cobriria isso com duas camadas: regressão automática, rodando um golden set de perguntas com resposta conhecida sempre que prompt, modelo ou dados mudarem; e revisão qualitativa, porque número certo não garante raciocínio certo, e uma explicação que muda entre rodadas pro mesmo resultado é erro tanto quanto um número errado, só mais difícil de perceber se ninguém registrar. Neste projeto, essa segunda camada já existe: cada resposta do golden set de 5 perguntas é gravada junto com um comentário manual específico (dict `COMENTARIOS`), registrando onde o agente acertou, onde errou e por quê.

### 3. O RH diz que o score de uma área no painel não bate com a planilha deles. Por onde você começa?

Antes de abrir qualquer query, eu faria perguntas para a pessoa: quem mantém essa planilha, com que frequência atualiza, e se ela segue a mesma definição de regra que o painel usa ou nasceu de outro processo, com um critério nunca documentado. Divergência não significa que o painel está certo. Pode ser o contrário: a planilha reflete um ajuste manual que o RH faz há meses e que virou prática sem virar regra escrita, e nesse caso o problema é de negócio. Presumir que o sistema é a fonte de verdade antes dessa conversa é um tipo de erro; depois eu partiria para a checagem técnica. Aqui essa checagem já existe: `verificacao_independente.py` reimplementa as regras em pandas direto do SQLite, sem nenhuma view do projeto, e isola se a causa é regra de cálculo ou dado de origem. Suspeitas mais prováveis neste case: Consolidado vs. Direto (R11), planilha incluindo os 9 colaboradores que R10 exclui, ou média ponderada por peso no lugar da média simples da área.


## Limitações conhecidas

- **Resolução de nome no agente (`resolver_por_nome`):** usa `ILIKE`, que é
  case-insensitive mas não remove acento: "Gerencia" não bate com
  "Gerência" sem grafia exata. Documentado e testado na Parte 4; melhoria
  proposta lá (normalizar acento antes de comparar).
- **Caminho absoluto no `.pbip`:** o modelo Power BI lê os CSVs de
  `painel/dados/` por caminho absoluto Windows
  (`C:\Users\Fabian\Desktop\MEREO CASE\painel\dados\*.csv`). Abrir o
  projeto numa outra máquina exige reapontar a fonte de dados no Power BI
  antes de atualizar o modelo. Decisão aceita por tempo, não um bug não
  percebido.
- **`material_original/` fora do versionamento:** é o dado de origem
  fornecido no enunciado (`.db`/`.xlsx`), não código produzido neste case;
  mantido fora do git por ser volumoso e já estar anexado ao material
  original. O arquivo continua presente no disco, só não é rastreado.
- **Matriz "Score por Área" sem recuo hierárquico:** diretorias e
  gerências aparecem com o mesmo recuo (`steppedLayoutIndentation = 0D`
  no visual) e o mesmo negrito; só a ordem das linhas indica o que está
  dentro do quê. Correção é visual (Power BI Desktop), não afeta os
  números; não aplicada por tempo.
- **Top/Bottom de gestores fixo por nome:** o filtro do visual usa uma
  lista fixa de nomes, não um cálculo dinâmico sobre `vw_score_gestor`.
  Se os dados do ciclo forem recarregados, o painel continua mostrando
  os mesmos nomes em vez de reordenar pelos novos valores. Correção
  ideal seria mover o ranking pra uma medida/view; registrado aqui como
  a alternativa mínima, por tempo.
