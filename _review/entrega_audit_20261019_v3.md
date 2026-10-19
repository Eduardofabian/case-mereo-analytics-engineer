# Auditoria de Entrega · Case Mereo (Grupo Aurora) · case-mereo-analytics-engineer
> Score estimado: **92/100 — FORTE — pronto para submeter**
> Gerado por `/auditoria-entrega-mereo` em 2026-10-19, 3ª rodada (HEAD `8696d4f`, sincronizado com `origin/main`). Rodadas anteriores: [1ª](entrega_audit_20261019.md) 84/100 · [2ª](entrega_audit_20261019_v2.md) 91/100.

---

## Veredicto

Pronto para submeter. Desde a 2ª rodada, a entrega fechou as duas pendências que estavam declaradas:

- `sql/06_verificacao/verificacao_independente_staging.sql` foi rodado contra o banco atual. Dá **PASS** nos três níveis, com diferença máxima de 1e-14 (ponto flutuante). Agora P1/P2/P3 têm **duas** confirmações independentes: pandas a partir do SQLite e T-SQL a partir de `staging`.
- O protótipo Streamlit foi validado visualmente, e o comando do docstring virou `python -m streamlit run ...`, que funciona sem PATH configurado.

Reexecutado nesta rodada: `verificacao_independente.py` deu "TUDO CONFERE" (0.0000); as 5 respostas do agente batem via tools; zero caminhos antigos; zero chaves de API no repositório; Parte 5 com 10/10/10 linhas.

Resta um ponto de precisão no texto (gap 1): uma frase do README diz que um achado foi corrigido, mas a seção "Limitações conhecidas" do próprio README diz que não foi. ~2 min.

---

## Score por critério (pesos exatos do enunciado)

| Critério | Peso | Nota estimada | Pontos | Gaps críticos | Δ vs 2ª rodada |
|---|---|---|---|---|---|
| Corretude dos números (Parte 1) | 30% | 9.5/10 | 28.5/30 | 0 | +0.5 |
| Problemas de qualidade | 20% | 9.5/10 | 19.0/20 | 0 | = |
| Agente de IA | 20% | 9.0/10 | 18.0/20 | 0 | = |
| Painel | 15% | 9.0/10 | 13.5/15 | 0 | = |
| Perguntas abertas | 10% | 9.0/10 | 9.0/10 | 0 | = |
| Organização e README | 5% | 8.5/10 | 4.25/5 | 0 | = |
| **TOTAL** | **100%** | — | **92/100** | — | **+1** |

Corretude sobe para 9.5 com a segunda verificação independente em T-SQL. Não vai a 10 pelo mesmo motivo da 2ª rodada: a conferência automática pode ter adotado outra leitura nos dois casos que o enunciado não cobre (peso negativo e denominador zero), apesar de ambos estarem documentados e medidos.

---

## Verificação de reprovação imediata

| Critério | Status |
|---|---|
| `respostas/p1_*`, `p2_*`, `p3_*` presentes e com conteúdo | ✅ 72 / 11 / 6 |
| `etl/verificacao/verificacao_independente.py` existe e é independente | ✅ reexecutado: 0.0000 |
| Estrutura bate com README.md / sql/ / respostas/ / painel/ / agente/ | ✅ |
| `agente/respostas.md` sem placeholder | ✅ 5 respostas + 5 comentários, sincronizados com `COMENTARIOS` |
| As 3 perguntas abertas respondidas | ✅ 10 linhas cada |

Nenhum bloqueador.

---

## Status dos gaps da 2ª rodada

| # | Gap (2ª rodada) | Status |
|---|---|---|
| 1 | README afirmava ter rodado as duas skills sem relatório da segunda | ✅ `_review/dashboard_audit_20261019.md` existe; o texto descreve as duas rodadas com precisão |
| 2 | Matriz sem recuo hierárquico | ⚠️ não corrigido, **declarado** em "Limitações conhecidas" (ok pelo enunciado) |
| 3 | Comentários 2–5 sem acento | ✅ reescritos |
| 4 | Comentário 4 falava em "duas rodadas" | ✅ "três rodadas" |
| 5 | R6 fora do system prompt | ⚠️ não aplicado, mantido como proposta de melhoria (opcional) |

Pendências declaradas na 1ª/2ª rodada, agora **resolvidas**: `sql/06_verificacao` revisado e rodado; UI do Streamlit validada.

---

## Gaps por impacto na nota

### Impacto alto (corrigir agora)

Nenhum.

### Impacto médio (corrigir se houver tempo)

**1. O README diz que um achado foi corrigido, e a seção de limitações diz que não** — Organização (5%) · ~2 min

`README.md:68-70`: *"a segunda rodada confirmou 91/100, com os três achados remanescentes também corrigidos antes do commit final."* Os três achados de maior impacto da 2ª rodada eram: afirmação sobre as skills, **matriz sem recuo** e comentários sem acento. O segundo não foi corrigido. O próprio README o lista em "Limitações conhecidas" ("não aplicada por tempo"), e o `visual.json` segue com `steppedLayoutIndentation = 0D`. São dois parágrafos do mesmo documento se contradizendo, num ponto que o avaliador pode conferir abrindo `_review/entrega_audit_20261019_v2.md`.

Correção sugerida: *"...confirmou 91/100; dos achados restantes, corrigi os comentários do agente e a evidência das skills, e a matriz sem recuo ficou registrada em 'Limitações conhecidas'."*

### Impacto baixo (nice to have)

**2. "Total de lançamentos" ambíguo** — Qualidade · ~1 min

`README.md:257` chama 3588 de "total de lançamentos", e a seção de validação em T-SQL (`README.md:380`) cita `staging.meta_valor_mensal = 3633`. Os dois estão certos (conferido no SQLite: 3633 brutos − 45 duplicados de R2 = 3588), mas um leitor que cruza os dois números vê uma divergência de 45. Trocar por "3588 = total de lançamentos após R2 (3633 brutos − 45 duplicados)".

**3. Dois ajustes leves do painel que não estão nem corrigidos nem declarados** — Painel · ~5 min no Desktop

Da auditoria do painel: o cabeçalho "Area" sem acento (`displayName` no `visual.json`) e a "Mediana 100.36" com ponto no card ao lado de "95,74" (`FORMAT(..., "en-US")` em `Medidas.tmdl`). Não justificam entrar em Limitações; ou se corrigem, ou ficam como estão.

**4. R6 no system prompt** — Agente · ~10 min, opcional

Igual à 2ª rodada: a melhoria que o próprio README propõe para a variância de explicação na pergunta 4 continua sem aplicar. Aplicar converte "o que eu faria" em "o que eu fiz", mas o enunciado só pede o comentário, e o comentário está bom.

---

## Checklist final antes de submeter

**Corretude (30%)**
- [x] `verificacao_independente.py` reimplementa R1-R11 sem reusar view do projeto
- [x] Diferença 0.0000 confirmada (pandas) + PASS em T-SQL contra `staging`
- [x] R6, R7, R10, R11 conferidos contra o enunciado

**Qualidade (20%)**
- [x] Achados com contagem real, consistentes com o SQLite (3633 / 3588 / 181 = 138 + 43 reconciliados nesta rodada)
- [x] Toda decisão de tratamento justificada, incluindo `ABS(peso)`
- [x] Sensibilidade para pós-desligamento e peso negativo

**Agente de IA (20%)**
- [x] Ferramentas fixas parametrizadas, sem SQL livre
- [x] `respostas.md` real, regenerado via LLM, comentários sincronizados
- [x] Testado com nome inexistente, sem alucinação
- [x] Instruções da chave de API documentadas, sem chave no repositório

**Painel (15%)**
- [x] PDF + print + `.pbip`, uma página
- [x] Justificativa da escolha no início da seção
- [x] Limitações restantes do painel declaradas

**Perguntas abertas (10%)**
- [x] 3 respostas, 10 linhas cada, com exemplos concretos do case

**Organização e README (5%)**
- [x] Estrutura, caminhos e comandos de reprodução corretos
- [x] Pendências declaradas batem com o estado real do repositório
- [ ] Narrativa das auditorias consistente com "Limitações conhecidas" (gap 1)

---

## Como re-auditar

```
claude "/auditoria-entrega-mereo"
```

---

*Case Mereo (Grupo Aurora) · /auditoria-entrega-mereo v2.0*
