# Case Mereo — Grupo Aurora (Analytics Engineer Pleno)

Resultado de cada colaborador, área e gestor do ciclo 2025, a partir da base
`case_metas.db` fornecida, com os problemas de qualidade da base mapeados e
as decisões de tratamento justificadas.

## Status atual

| Parte | Status |
|---|---|
| Parte 1 — SQL (P1/P2/P3) | **Concluída e validada** contra o banco real |
| Problemas de qualidade | **Concluído** — 38 checagens sistemáticas + achados confirmados abaixo |
| Painel (`painel/`) | Pendente |
| Agente de IA (`agente/`) | Pendente |
| Perguntas abertas | Pendente |

## Uso de IA neste case

Usei o Claude (Anthropic) como par técnico durante todo o desenvolvimento:
modelagem das camadas SQL (staging/intermediate/marts), tradução das regras
de negócio do enunciado em T-SQL, geração da bateria de checagens de
qualidade em `etl/diag_qualidade.py`, e revisão crítica dos resultados —
cada número de P1/P2/P3 foi conferido manualmente (recálculo de média
ponderada na mão, verificação de hierarquia de área contra `staging.area`,
contagem de gestores válidos, simulação de sensibilidade excluindo os
lançamentos pós-desligamento) antes de aceitar como correto, não só aceito
porque o SQL rodou sem erro. A revisão também encontrou um script Python
(`etl/load.py`) que ficou desatualizado em relação à estrutura final do
banco (referenciava um schema `dbo.stg_*` de uma arquitetura anterior,
substituída durante o desenvolvimento) — identificado e removido do
repositório. As decisões de tratamento de
dado (peso negativo, denominador zero, lançamento pós-desligamento, meta
compartilhada com lançamento próprio) foram meu julgamento, documentado
abaixo caso a caso — a IA ajudou a identificar o padrão e propor a regra,
mas a decisão de qual regra aplicar foi minha.

## Estrutura do repositório

```
README.md
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
qualidade/
  relatorio_diagnostico.md  -- 38 checagens sistemáticas rodadas contra o banco
  achados_qualidade_chat1.md -- achados da primeira varredura (Python/pandas), ver nota abaixo
etl/
  extract_load.py           -- carga de staging.* a partir do SQLite
  diag_qualidade.py         -- gera qualidade/relatorio_diagnostico.md
  export_respostas.py       -- roda as 3 queries de P1/P2/P3 e exporta CSV (script correto)
  verificacao_independente.py -- recomputa P1/P2/P3 em pandas direto do SQLite e compara com os CSVs
  sensibilidade_matriz.py   -- sensibilidade pós-desligamento em 4 definições (colaborador/área/gestor)
diagramas/
  Mereo_Grupo_Aurora.{sql,svg,png}  -- diagrama ER do modelo
material_original/
  ENUNCIADO.pdf, ENUNCIADO.docx, dados/  -- material recebido, como veio
painel/                    -- pendente
agente/                    -- pendente
```

**Nota histórica — `etl/load.py` (removido):** o repositório teve, numa fase
anterior, um segundo script de carga (`load.py`) que referenciava uma
estrutura de schema antiga (`dbo.stg_area`, `dbo.stg_colaborador` etc.) e
pastas `sql/staging/`, `sql/intermediate/`, `sql/marts/` no formato antigo —
uma arquitetura substituída durante o desenvolvimento. Rodar esse script
hoje falharia (arquivos que ele procura não existem mais) ou, pior,
escreveria num schema `dbo.stg_*` desconectado do pipeline validado em
`staging/intermediate/marts`. Removido do repositório; `extract_load.py` é
e sempre foi o script correto para esse passo (carga de `staging.*`).

**Nota sobre `qualidade/achados_qualidade_chat1.md` vs `qualidade/relatorio_diagnostico.md`:**
o primeiro foi gerado numa fase inicial, validado em Python/pandas direto
sobre os CSVs, sem rodar contra o SQL Server de fato (diz isso explicitamente
no próprio arquivo). O segundo é uma bateria de 38 checagens sistemáticas
rodada depois, contra o banco. Os números que os dois têm em comum (lançamento
duplicado, nulo, peso negativo) foram conferidos neste README contra o banco
real e batem exatamente. Os achados abaixo usam o relatório de diagnóstico
como fonte primária.

## Arquitetura dos dados

Três camadas, cada uma um schema no SQL Server:

- **staging** — espelho cru do SQLite, sem tratamento nenhum.
- **intermediate** — resolve as regras de negócio (dedup R2/R3, resolução de
  meta compartilhada R7, fechamento de hierarquia de área). Não é consumido
  fora do pipeline.
- **marts** — camada final. `dim_area`, `dim_colaborador`, `dim_meta`,
  `fact_meta_valor_mensal`, e as três views de score
  (`vw_score_colaborador`, `vw_score_area`, `vw_score_gestor`) — é daqui que
  Dashboard, Agente de IA e os CSVs de `respostas/` leem.

Ordem de execução dos scripts em `sql/`: `00_drop_all.sql` (opcional, só se
já existir algo no banco) → `01_setup/` → `02_staging/` (+ carga dos dados
via `etl/extract_load.py`) → `03_intermediate/` → `04_marts/` → `05_respostas/`.
Cada view usa `IF OBJECT_ID(...) IS NOT NULL DROP VIEW` + `CREATE VIEW`, então
é seguro rodar de novo sem duplicar objeto.

## Regras de negócio — decisões de interpretação

A maioria das 11 regras (R1–R11) é direta. As que exigiram uma decisão
porque o enunciado não cobre o caso exato da base:

- **R6/R8, denominador zero:** regra não prevê atingimento indefinido
  (`soma(previsto)=0` numa meta de Acumulação Soma, por exemplo). Tratado
  como extensão de R8 — sem nota, meta não entra no score. Aplicado de
  forma genérica no SQL (`CASE WHEN ... <> 0 THEN ... ELSE NULL END`), não
  hardcoded para um id específico, então qualquer dado novo com o mesmo
  problema cai no mesmo tratamento automaticamente.
- **Peso negativo:** nenhuma regra prevê peso negativo (inverteria o peso
  da meta no cálculo). Decisão: `peso_efetivo = ABS(peso)`.
- **Lançamento em mês posterior ao desligamento:** o enunciado não pede
  exclusão desses lançamentos, e R3/R8 não cobrem esse caso — só olham
  `nao_se_aplica`/`previsto`/`realizado`. Decisão: manter literal no
  cálculo (não inventar uma regra de corte que o enunciado não pede),
  documentando esses lançamentos à parte para auditoria. Validado por
  simulação: ver análise de sensibilidade abaixo — o impacto é pequeno.
- **Meta compartilhada com lançamento mensal próprio:** R7 é explícito —
  usa lançamentos da referência, não os próprios. Mesmo havendo lançamento
  próprio na base (achado abaixo), ele é ignorado por construção: o join
  da camada de nota é feito por `id_meta_lancamentos`, que para toda meta
  Compartilhada aponta pra referência, nunca pro próprio id. Confirmado
  com query direta contra o banco que zero desses lançamentos vazam no
  cálculo.

## Achados de qualidade

Validado contra o banco real nesta sessão (não só contra CSV/pandas):

**Nota de processo — quase-regressão pega antes da entrega:** durante o
ajuste da definição de "pós-desligamento" (fim de mês → início de mês, ver
view de quarentena abaixo), uma versão intermediária de
`intermediate.lancamento_valido` acabou embutindo a exclusão de
pós-desligamento direto no `flag_valido` — que `marts.fact_meta_valor_mensal`
lê de forma direta. Isso teria revertido silenciosamente a decisão já
fechada ("manter literal no cálculo"), sem nenhum erro de sintaxe pra
avisar. Rodando a query de verificação com essa versão (com o bug ainda
ativo) nesta sessão, o resultado real era `flag_valido`: 343 inválidos /
3245 válidos (343 = 181 originais + 162 pós-desligamento recém-excluídos,
3245 + 343 = 3588 = total de lançamentos). Em algum ponto da conversa esse
número foi transcrito incorretamente como "362" ao resumir o resultado em
texto — um erro de leitura da tela, não um terceiro número real nem
inconsistência do pipeline. Revertido antes de gerar qualquer CSV nesse
estado, e reconfirmado nesta sessão contra o banco ao vivo: `flag_valido`
hoje é **181 inválidos / 3407 válidos**, só R2+R3, sem a condição de
desligamento — exatamente como antes do incidente: 181 + 162 = 343
(inválido sobe ao aplicar o bug) e 3407 - 162 = 3245 (válido desce na
mesma proporção), consistente nos dois sentidos. Separadamente, a
contagem de `lancamento_rejeitado` por categoria foi recalculada e
confere: `duplicado_perdedor`=45, `lancamento_pos_desligamento`=162 (=24
elegíveis + 138 não elegíveis), `previsto_ou_realizado_nulo`=43 — bate com
a tabela abaixo e com os achados já documentados.

| Achado | Qtd | Decisão |
|---|---|---|
| Lançamento duplicado (id_meta, mês) | 45 pares (90 registros brutos) | R2: mantido o de `data_lancamento` mais recente |
| `nao_se_aplica=0` mas previsto/realizado nulo | 43 | R3 já exclui do cálculo |
| Lançamento em mês pós-desligamento, colaborador elegível (R10) | 24 | Mantido literal no cálculo; impacto medido (ver sensibilidade abaixo) |
| Lançamento em mês pós-desligamento, colaborador não elegível | 138 | Não afeta P1/P2/P3 (colaborador já sai por R10), documentado por completude |
| Meta com denominador=0 (meta 5094, "Leads gerados", colaborador 125, previsto=0 o ano inteiro) | 1 | Extensão de R8 — sem nota |
| Meta com peso negativo (meta 5286, "Inadimplência (%)", colaborador 174) | 1 | `peso_efetivo = ABS(peso)` |
| Meta Compartilhada com lançamento mensal próprio (ids 5066, 5156, 5219, 5231, 5278) | 60 registros | Ignorado por construção (ver acima); confirmado 0 vazamento no cálculo |
| Meta Individual sem nenhum lançamento mensal (ids 5014, 5063, 5146, 5188) | 4 | R8 cobre — sem nota, fora do score |
| Colaborador com soma de peso das metas != 100 (varia entre 85 e 120) | 7 | R9 normaliza por soma de peso, não quebra o cálculo — só não assumir 100 no Dashboard/Agente |
| `polaridade`/`tipo_acumulacao` nulos na própria linha de meta Compartilhada | presente | Esperado — R7 resolve via `COALESCE` com a referência, o valor próprio nunca é usado quando é Compartilhada |

Checado e confirmado limpo (sem achado): PK duplicada em todas as 5 tabelas,
FK órfã em todas as relações, ciclo na cadeia de gestores, auto-gestor,
gestor fora da hierarquia de área do subordinado, lançamento antes da
admissão, mês fora de 1–12, espaço extra em nome/nome_meta, valores fora do
domínio esperado em tipo_meta/polaridade/tipo_acumulacao.

### Análise de sensibilidade — lançamento pós-desligamento

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

**Resultado principal — pior caso das quatro testadas (holder / fim):**
a **maior** variação encontrada é de **1.64 ponto** no score de um colaborador, **0.113** no score de uma área (o máximo entre as 11 áreas) e **0.125** no score médio do time de um gestor (o máximo entre os 9). São valores máximos, não médias. O **top 3 / bottom 3 de P3 não muda**, nem a elegibilidade de ninguém.

| Definição | colab. que mudam | máx \|Δ\| colaborador | máx \|Δ\| área | máx \|Δ\| gestor (9) | top 3 / bottom 3 de P3 |
|---|---|---|---|---|---|
| **holder / fim (pior caso)** | 4 | 1.64 | 0.113 | 0.125 | inalterado |
| holder / início | 4 | 0.96 | 0.054 | 0.060 | inalterado |
| owner / fim | 3 | 1.41 | 0.043 | 0.047 | inalterado |
| owner / início (a da quarentena) | 3 | 0.68 | 0.007 | 0.007 | inalterado |

Detalhe do pior caso (holder / fim; Δ = score atual − score sem os
lançamentos pós-desligamento):

| id_colaborador | Δ score |
|---|---|
| 134 | -1.64 |
| 138 | +0.85 |
| 113 | -0.40 |
| 135 | -0.34 |

Nota sobre o 113: ele é o único que diminui ao passar de holder / início
(-0.54) para holder / fim (-0.40). Não é erro de sinal — é efeito do corte
de R6 e de a acumulação por Soma ser razão de somas. Na meta compartilhada
5045 (lançamentos do 101, desligamento do 113 em 02/10/2025), excluir só
nov–dez tira dois meses fracos (atingimento ~82%) e sobe a nota para 92.57;
excluir também outubro tira um mês bom (~97%) e a nota volta a 92.02. As
outras duas metas ficam em 106–107 e 120 (travada em R6), então a diferença
vem toda da 5045. Conferido à mão: 109.93 → 110.47 → 110.32.

Áreas afetadas: 5 (-0.113), 3 (-0.040) e, no consolidado, 1 (-0.046) e
2 (-0.019). Gestores afetados: 129 (-0.125) e 106 (-0.044); todos os
outros dos 9 oficiais em 0. "Pior caso" vale para as quatro leituras
testadas, não para toda definição concebível.

**Por que a view de quarentena usa owner (e a sensibilidade não):** são
duas perguntas diferentes. `intermediate.lancamento_rejeitado` é um
achado de qualidade de dado na origem — "esse lançamento é anômalo porque
foi feito por alguém que já tinha saído" — e isso é propriedade do evento
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
com o filtro correto (`etl/sensibilidade_matriz.py`).

A diluição pela média (de todos os elegíveis da área, ou dos subordinados
diretos do gestor) absorve o desvio pontual do colaborador isolado.
Conclusão: o "raio de dano" da decisão fica contido mesmo na leitura mais
severa — não há necessidade de reportar uma segunda versão de P2/P3.

## Validação de P1/P2/P3

- **Recomputação independente (pandas, sem usar nenhuma view/SQL do
  projeto):** `etl/verificacao_independente.py` reimplementa R1–R11 direto
  do SQLite original e compara com os três CSVs de `respostas/`. Resultado:
  P1 (72 linhas), P2 (11) e P3 (6) idênticos, diferença máxima 0.0000, e
  universo de P3 = 9 gestores. Foi a primeira confirmação que não vinha de
  auto-relato do pipeline SQL.

- **P1 (score por colaborador):** 72 de 81 colaboradores elegíveis (R10),
  scores no intervalo [0, 120] como R6 define. Recalculei a média ponderada
  na mão para os 5 scores mais baixos (18.17 a 54.85) — bateram exatos com
  o SQL. A causa não é dado esparso (10–12 meses válidos em todos os
  casos), é o corte duro de R6 em 80%: quando a meta de maior peso da
  pessoa fica logo abaixo do corte, a nota inteira dela zera.
- **P2 (score por área):** confirmado que `score_direto = score_consolidado`
  exatamente nas 6 áreas-folha da hierarquia (sem área abaixo) e diferem
  nas 5 áreas com filhos — bate 100% com a estrutura real de
  `staging.area` (Diretoria → Gerência → Coordenação).
- **P3 (top/bottom gestores):** os dois filtros (gestor ativo em 31/12/2025
  e ≥3 subordinados diretos elegíveis) **não são decisão nossa — são texto
  literal do enunciado**: "Considere apenas gestores ativos em 31/12/2025
  com pelo menos 3 subordinados diretos elegíveis." (Parte 1, P3). 9
  gestores no total atendem aos dois critérios — top 3 e bottom 3 cobrem 6
  dos 9, sem sobreposição. O filtro de "pelo menos 3" inclui corretamente o
  caso-limite de exatamente 3 subordinados.

## Como reproduzir

1. Rodar `sql/01_setup/` e `sql/02_staging/` no SSMS (cria banco, schemas
   e tabelas).
2. `pip install pyodbc` e `python etl/extract_load.py` (carrega `staging.*`
   a partir do SQLite).
3. Rodar `sql/03_intermediate/` e `sql/04_marts/` no SSMS, na ordem dos
   arquivos (cria as views).
4. `python etl/export_respostas.py` (gera os três CSVs em `respostas/`).

Para rodar só o diagnóstico de qualidade (gera
`qualidade/relatorio_diagnostico.md`):

```
python etl/diag_qualidade.py
```
