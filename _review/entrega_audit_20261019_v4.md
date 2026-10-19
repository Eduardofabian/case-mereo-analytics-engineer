# Auditoria de Entrega · Case Mereo (Grupo Aurora) · case-mereo-analytics-engineer
> Score estimado: **92/100 — FORTE — pronto para submeter após 1 ajuste de formato**
> Gerado por `/auditoria-entrega-mereo` em 2026-10-19, 4ª rodada (HEAD `c117fdd`, sincronizado com `origin/main`). Rodadas anteriores: [1ª](entrega_audit_20261019.md) 84 · [2ª](entrega_audit_20261019_v2.md) 91 · [3ª](entrega_audit_20261019_v3.md) 92.

---

## Veredicto

Os 3 gaps da 3ª rodada estão fechados. O README não se contradiz mais sobre a matriz sem recuo, o "3588" agora diz "após R2 (3633 − 45)", e o painel ganhou "Área" com acento e "Mediana 100,36" no formato pt-BR, com print e PDF reexportados. Os números seguem idênticos: `verificacao_independente.py` dá "TUDO CONFERE". Não há chave de API no repositório.

**Uma regressão nova, de formato, que o enunciado pede explicitamente.** O commit `0a16313` ("Refine descriptions...", editado direto no GitHub) reescreveu a Parte 5. A **resposta 3 voltou a ter 11 linhas** (a 100 colunas), e o enunciado diz "até 10 linhas cada". A mesma edição reintroduziu emendas com vírgula que o commit `8696d4f` tinha acabado de reverter. Por isso o score fica parado em 92 em vez de subir: o ganho no painel é anulado pela perda nas perguntas abertas. ~10 min para corrigir.

---

## Score por critério (pesos exatos do enunciado)

| Critério | Peso | Nota estimada | Pontos | Gaps críticos | Δ vs 3ª rodada |
|---|---|---|---|---|---|
| Corretude dos números (Parte 1) | 30% | 9.5/10 | 28.5/30 | 0 | = |
| Problemas de qualidade | 20% | 9.5/10 | 19.0/20 | 0 | = |
| Agente de IA | 20% | 9.0/10 | 18.0/20 | 0 | = |
| Painel | 15% | 9.5/10 | 14.25/15 | 0 | +0.5 |
| Perguntas abertas | 10% | 8.0/10 | 8.0/10 | 1 | −1.0 |
| Organização e README | 5% | 9.0/10 | 4.5/5 | 0 | +0.5 |
| **TOTAL** | **100%** | — | **92/100** | — | **=** |

Com o gap 1 corrigido, Perguntas volta a 9.0 e o score vai a **93**.

---

## Verificação de reprovação imediata

| Critério | Status |
|---|---|
| `respostas/p1_*`, `p2_*`, `p3_*` presentes e com conteúdo | ✅ |
| `verificacao_independente.py` existe e é independente | ✅ reexecutado: TUDO CONFERE |
| Estrutura bate com README.md / sql/ / respostas/ / painel/ / agente/ | ✅ |
| `agente/respostas.md` sem placeholder | ✅ |
| As 3 perguntas abertas respondidas | ✅ (mas a 3 passou do limite de linhas, gap 1) |

Nenhum bloqueador.

---

## Status dos gaps da 3ª rodada

| # | Gap | Status | Evidência |
|---|---|---|---|
| 1 | README contradizia "Limitações conhecidas" sobre a matriz | ✅ | `README.md` agora diz o que foi corrigido e o que ficou em Limitações |
| 2 | "3588 = total de lançamentos" ambíguo | ✅ | "após R2, ou seja, 3633 brutos menos 45 duplicados" |
| 3 | "Area" sem acento + "Mediana 100.36" en-US | ✅ | `displayName: "Área"`; `FORMAT(..., "pt-BR")`; print mostra "Mediana 100,36" |
| 4 | R6 no system prompt (opcional) | ⚠️ não aplicado, segue como proposta (ok) |

---

## Gaps por impacto na nota

### Impacto alto (corrigir agora)

**1. Parte 5, resposta 3 com 11 linhas, e emendas com vírgula de volta nas três respostas** — Perguntas abertas (10%) · ~10 min

O enunciado limita as respostas a "até 10 linhas cada". Medido a 100 colunas, que é a mesma régua das rodadas anteriores: **10 / 10 / 11**. A resposta 3 cresceu na edição do GitHub (`0a16313`).

A mesma edição trocou pontos e dois-pontos por vírgulas, emendando frases independentes. Para quem avalia "explicar resultados para pessoas não técnicas", que é responsabilidade descrita na vaga, isso pesa. Trechos:

- R1: *"...quem valida e carrega**,** um endpoint de API..."* e *"...com motivo registrado**,** a carga em staging..."*
- R2: *"...errado na cara"**,** os sinais reais são mais sutis **como exemplo** um usuário reformulando..."* ("como exemplo" ficou sem a preposição: "por exemplo") e *"...essa segunda camada já existe**,** cada resposta do golden set..."*
- R3: *"...pode ser o contrário**,** onde a planilha reflete..."* e *"...checagem técnica**,** aqui no projeto essa checagem já existe**,** `verificacao_independente.py`..."*

Correção: voltar ao texto da Parte 5 do `8696d4f`, que tinha 10/10/10 e pontuação revisada (`git show 8696d4f:README.md`). Se alguma mudança de conteúdo do `0a16313` era intencional, reaplicar só ela. Na resposta 3, cortar "aqui no projeto essa checagem já existe," já devolve a 10 linhas.

### Impacto médio

Nenhum.

### Impacto baixo (nice to have)

**2. Verde reaparece no Top 5 como cor de categoria** — Painel · ~2 min, opcional

No Top 5, a Gerência de Logística ficou verde (`#1BAF7A`), e verde é "≥100" no semáforo. Aqui não engana, porque os 5 têm score ≥100 de qualquer jeito. Mesmo assim, é a única cor do semáforo ainda reaproveitada como categoria. Trocar por um tom fora da paleta (ex.: âmbar escuro ou cinza) fecha o achado da auditoria do painel por completo.

**3. Relatório da 3ª rodada não versionado** — Organização · ~1 min

`_review/entrega_audit_20261019_v3.md` está como não rastreado. O README cita os relatórios em `_review/` como evidência do processo, então vale commitar o v3 (e este v4) junto com a correção do gap 1.

---

## Checklist final antes de submeter

**Corretude (30%)**
- [x] Verificação independente pandas (0.0000) + T-SQL contra `staging` (PASS)
- [x] R6, R7, R10, R11 conferidos contra o enunciado

**Qualidade (20%)**
- [x] Achados com contagem real e reconciliados (3633 / 3588 / 181)
- [x] Toda decisão justificada e medida

**Agente de IA (20%)**
- [x] Tools fixas, `respostas.md` real e sincronizado, sem alucinação, sem chave no repo

**Painel (15%)**
- [x] PDF + print + `.pbip`, uma página, justificativa no README
- [x] Rótulos e formatação consistentes (Área, vírgula decimal)
- [x] Limitações restantes declaradas (recuo, gestores por nome)

**Perguntas abertas (10%)**
- [ ] 3 respostas, até 10 linhas cada. **A 3 tem 11 (gap 1)**
- [ ] Texto sem emendas com vírgula (gap 1)

**Organização e README (5%)**
- [x] Narrativa das auditorias consistente com "Limitações conhecidas"
- [ ] Relatórios v3/v4 versionados (gap 3)

---

## Como re-auditar

```
claude "/auditoria-entrega-mereo"
```

---

*Case Mereo (Grupo Aurora) · /auditoria-entrega-mereo v2.0*
