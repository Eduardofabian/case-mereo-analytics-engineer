# Auditoria de Entrega · Case Mereo (Grupo Aurora) · case-mereo-analytics-engineer
> Score estimado: **91/100 — FORTE — pronto para submeter**
> Gerado por `/auditoria-entrega-mereo` em 2026-10-19, 2ª rodada (HEAD `0daa6c6`). 1ª rodada: [`entrega_audit_20261019.md`](entrega_audit_20261019.md) (84/100).

---

## Veredicto

Pronto para submeter. Os 11 gaps da 1ª rodada estão fechados, e os números não mudaram com as correções. Rodei de novo `etl/verificacao/verificacao_independente.py`: P1/P2/P3 continuam idênticos a `respostas/` (0.0000) e o universo de P3 segue com 9 gestores.

A decisão de `ABS(peso)`, que era o maior risco do critério de qualidade, agora tem alternativa, evidência e impacto medido, com o mesmo rigor da sensibilidade de pós-desligamento. O painel entregue mostra todas as diretorias e gerências, sem scroll. O agente foi re-executado de verdade contra o LLM (`claude-sonnet-5` resolveu), e as 5 respostas batem com as tools chamadas direto.

O que sobra é acabamento. O único ponto que vale corrigir antes de enviar é uma afirmação do README sobre a skill de auditoria do painel, que o repositório não comprova (gap 1 abaixo).

---

## Score por critério (pesos exatos do enunciado)

| Critério | Peso | Nota estimada | Pontos | Gaps críticos | Δ vs 1ª rodada |
|---|---|---|---|---|---|
| Corretude dos números (Parte 1) | 30% | 9.0/10 | 27.0/30 | 0 | = |
| Problemas de qualidade | 20% | 9.5/10 | 19.0/20 | 0 | +1.0 |
| Agente de IA | 20% | 9.0/10 | 18.0/20 | 0 | +0.5 |
| Painel | 15% | 9.0/10 | 13.5/15 | 0 | +1.5 |
| Perguntas abertas | 10% | 9.0/10 | 9.0/10 | 0 | +1.0 |
| Organização e README | 5% | 8.5/10 | 4.25/5 | 0 | +0.5 |
| **TOTAL** | **100%** | — | **91/100** | — | **+7** |

Por que Corretude continua em 9, e não 10: os números estão certos *dadas as decisões de interpretação*. A conferência automática do enunciado pode ter adotado outra leitura em dois pontos que o enunciado não cobre: peso negativo (meta 5286) e denominador zero (meta 5094). As duas decisões estão documentadas e medidas, mas o risco residual não é zero.

---

## Verificação de reprovação imediata

| Critério | Status |
|---|---|
| `respostas/p1_score_colaborador.csv`, `p2_*`, `p3_*` presentes e com conteúdo | ✅ 72 / 11 / 6 linhas |
| `etl/verificacao/verificacao_independente.py` existe e é independente (não reusa view) | ✅ só `sqlite3` + pandas; reexecutado: 0.0000, "TUDO CONFERE" |
| Estrutura bate com README.md / sql/ / respostas/ / painel/ / agente/ | ✅ |
| `agente/respostas.md` sem placeholder | ✅ regenerado via LLM, 5 respostas + 5 comentários |
| As 3 perguntas abertas respondidas | ✅ 10 linhas cada (a 100 colunas) |

Nenhum bloqueador.

---

## Status dos gaps da 1ª rodada

| # | Gap | Status | Evidência |
|---|---|---|---|
| 1 | `ABS(peso)` sem alternativa/medição | ✅ fechado | README: alternativa (excluir, R8), evidência (único peso negativo em 376; mesma meta positiva em 8 colaboradores; soma 100 em 75/81, redigido como "provável, não comprovado"), impacto 51.42 → 49.14, P3 inalterado |
| 2 | Print cortava a matriz de áreas | ✅ fechado | PNG e PDF novos: 3 diretorias + 5 gerências visíveis, sem scroll, sem linha Total |
| 3 | Parte 5 P1 citava stored procedure inexistente | ✅ fechado | cita `run_pipeline.py` e `diag_qualidade.py` |
| 4 | Parte 5 P3 sem causas específicas | ✅ fechado | R11, R10 (9 de 81), média ponderada vs simples |
| 5 | Tool do time sem filtro R10 | ✅ fechado | `flag_elegivel_r10 = 1`; Sofia Oliveira segue com 3 pessoas; não elegível não aparece mais |
| 6 | Comentário da pergunta 1 ilegível | ✅ fechado | reescrito com acentos, aponta para "Limitações conhecidas" |
| 7 | Caminhos antigos | ✅ fechado | `git grep` sem ocorrências (incluindo o extra em `sql/06_verificacao`) |
| 8 | `painel/dados` ignorado mas rastreado | ✅ fechado | versionado de propósito, registrado no `.gitignore` e no README |
| 9 | `sem_score` inalcançável | ✅ fechado | documentado como defensivo no `agente/README` |
| 10 | Modelo default não confirmado | ✅ fechado | `respostas.md` regenerado com `claude-sonnet-5`; código e `agente/README` alinhados |
| 11 | Justificativa do painel diluída | ✅ fechado | parágrafo "O que o painel mostra e por quê" no início da seção |

---

## Gaps por impacto na nota

### Impacto alto (corrigir agora)

Nenhum.

### Impacto médio (corrigir se houver tempo)

**1. O README afirma que as duas skills foram rodadas, mas só existe relatório de uma** — Organização (5%) e uso de IA · ~5 min (reescrever) ou ~30 min (rodar)

A seção "Skills de auditoria customizadas" diz *"Rodei as duas antes da entrega, apliquei as correções de maior impacto na nota e re-rodei para confirmar."* Em `_review/` só há relatórios de `auditoria-entrega-mereo`. Não há saída de `auditoria-dashboard-mereo`. O enunciado diz literalmente que valoriza "raciocínio claro e honesto", e essa é uma afirmação que o avaliador pode conferir abrindo a pasta. Duas saídas:

- rodar `/auditoria-dashboard-mereo` e salvar a saída em `_review/`; ou
- reescrever a frase: *"Rodei a de entrega duas vezes (antes e depois das correções, ambos os relatórios em `_review/`); a de painel orientou os ajustes visuais da matriz."* (só se isso for verdade).

### Impacto baixo (nice to have)

**2. A matriz de áreas não mostra a hierarquia visualmente** — Painel (15%) · ~5 min no Desktop

Com `steppedLayoutIndentation = 0` e todas as linhas em negrito, a Gerência de Controladoria aparece com o mesmo peso visual da Diretoria Financeira. Quem lê o print só deduz a hierarquia pela ordem das linhas. Um recuo de 12–16px no nível 1 deixa a "Árvore de Performance" legível sem texto extra. O cabeçalho "Area" também ficou sem acento ("Área").

**3. Comentários 2–5 de `run_perguntas.py` ainda estão sem acento** — Agente (20%) · ~10 min

O comentário 1 agora tem acentos e os outros quatro não ("Operacoes", "nao", "e o teste mais importante"). No `respostas.md` a diferença fica visível lado a lado. O comentário 2 também diz que o agente "devolveu a elegibilidade R10 sem eu pedir". Desde o filtro R10 na tool, todos os retornados são elegíveis por construção, então vale ajustar para "a tool só devolve elegíveis (R10), e o agente confirmou isso na resposta".

**4. O comentário 4 fala em "duas rodadas"** — Agente · ~2 min

Houve uma terceira rodada (a regeneração atual). Nela, a explicação da nota zero ficou neutra ("nesse critério"), sem especular e sem citar R6. Isso reforça o ponto do comentário. Uma frase a mais registra que a variância persiste enquanto R6 não estiver no system prompt.

**5. Melhoria proposta para o agente e não aplicada** — Agente · ~15 min

As três rodadas mostram a mesma causa: o system prompt não traz as regras de negócio. Colocar R6 (corte 80%/120%) e R10 em 3 linhas no `SYSTEM_PROMPT` custa pouco e transforma "o que eu faria para melhorar" em "o que eu fiz". É opcional, porque o enunciado só pede o comentário.

---

## Pendências já declaradas no README (não contam como gap)

Estão em "Limitações conhecidas", que é a forma que o enunciado pede para tratar o que ficou incompleto:
- `sql/06_verificacao/verificacao_independente_staging.sql` não revisado após a reorganização (só o comentário de caminho foi corrigido nesta rodada);
- UI do protótipo Streamlit não validada visualmente;
- caminho absoluto Windows no `.pbip`;
- resolução de nome sensível a acento.

---

## Checklist final antes de submeter

**Corretude (30%)**
- [x] `verificacao_independente.py` reimplementa R1-R11 sem reusar view do projeto
- [x] Diferença 0.0000 confirmada entre pandas e os 3 CSVs de resposta (2ª rodada)
- [x] R6, R7, R10, R11 conferidos linha a linha contra o enunciado

**Qualidade (20%)**
- [x] Relatório de achados com contagem numérica real
- [x] Toda decisão de tratamento tem justificativa (incluindo `ABS(peso)`)
- [x] Análise de sensibilidade para decisões que mantiveram dado "sujo" (pós-desligamento e peso negativo)

**Agente de IA (20%)**
- [x] Ferramentas fixas parametrizadas, sem SQL livre
- [x] `respostas.md` com as 5 respostas e comentários reais, regenerado via LLM
- [x] Testado com nome inexistente, sem alucinação

**Painel (15%)**
- [x] PDF + print + fonte (`.pbip`)
- [x] Uma página só
- [x] Print legível por completo
- [x] Justificativa da escolha em poucas linhas, no início da seção

**Perguntas abertas (10%)**
- [x] 3 respostas, até 10 linhas cada
- [x] Cada resposta usa exemplo concreto deste projeto

**Organização e README (5%)**
- [x] Estrutura de pastas conforme pedido
- [x] README cobre decisões, qualidade, uso de IA, Parte 5, pendências
- [x] Caminhos de reprodução corretos (grep sem ocorrências)
- [ ] Afirmação sobre as skills comprovável pelo repositório (gap 1)

---

## Como re-auditar

```
claude "/auditoria-entrega-mereo"
```

---

*Case Mereo (Grupo Aurora) · /auditoria-entrega-mereo v2.0*
