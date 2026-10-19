# Auditoria de Entrega · Case Mereo (Grupo Aurora) · case-mereo-analytics-engineer
> Score estimado: **93/100 — FORTE — pronto para submeter**
> Gerado por `/auditoria-entrega-mereo` em 2026-10-19, 5ª rodada (HEAD `91edeeb`, sincronizado com `origin/main`, working tree limpo). Rodadas anteriores: [1ª](entrega_audit_20261019.md) 84 · [2ª](entrega_audit_20261019_v2.md) 91 · [3ª](entrega_audit_20261019_v3.md) 92 · [4ª](entrega_audit_20261019_v4.md) 92.

---

## Veredicto

Pronto para submeter, sem gap de impacto alto ou médio. Os três achados da 4ª rodada estão fechados e conferidos:

- A **Parte 5 é idêntica, byte a byte, à do `8696d4f`**: 10/10/10 linhas, sem as emendas com vírgula da edição do GitHub.
- O **Top 5 não usa mais cor do semáforo**: Logística passou de `#1BAF7A` para `#64748B`. Print e PDF foram reexportados, e o `powerbi_construcao_painel.md` foi atualizado (paleta, aviso de contraste e tabela de divergências).
- Os **relatórios v3/v4 estão versionados** em `_review/`.

Reexecutado nesta rodada: `verificacao_independente.py` deu "TUDO CONFERE" e não há chave de API no repositório.

O que sobra são as decisões já declaradas em "Limitações conhecidas" (recuo da matriz, gestores fixos por nome, caminho absoluto no `.pbip`, acento no resolver do agente) e a proposta opcional de colocar R6 no system prompt. O enunciado pede exatamente que o incompleto seja declarado, e está.

---

## Score por critério (pesos exatos do enunciado)

| Critério | Peso | Nota estimada | Pontos | Gaps críticos | Δ vs 4ª rodada |
|---|---|---|---|---|---|
| Corretude dos números (Parte 1) | 30% | 9.5/10 | 28.5/30 | 0 | = |
| Problemas de qualidade | 20% | 9.5/10 | 19.0/20 | 0 | = |
| Agente de IA | 20% | 9.0/10 | 18.0/20 | 0 | = |
| Painel | 15% | 9.5/10 | 14.25/15 | 0 | = |
| Perguntas abertas | 10% | 9.0/10 | 9.0/10 | 0 | +1.0 |
| Organização e README | 5% | 9.0/10 | 4.5/5 | 0 | = |
| **TOTAL** | **100%** | — | **93/100** | — | **+1** |

Por que não sobe além disso:
- **Corretude (9.5):** risco residual de a conferência automática ter outra leitura em peso negativo e denominador zero. Ambos estão documentados e medidos; é um risco que nenhuma correção remove.
- **Agente (9.0):** a variância de explicação na pergunta 4 tem causa conhecida e correção proposta, mas não aplicada.
- **Painel (9.5):** duas limitações visuais declaradas, não corrigidas.

---

## Verificação de reprovação imediata

| Critério | Status |
|---|---|
| `respostas/p1_*`, `p2_*`, `p3_*` presentes e com conteúdo | ✅ |
| `verificacao_independente.py` existe e é independente | ✅ TUDO CONFERE |
| Estrutura bate com README.md / sql/ / respostas/ / painel/ / agente/ | ✅ |
| `agente/respostas.md` sem placeholder | ✅ |
| As 3 perguntas abertas respondidas | ✅ 10/10/10 linhas |

Nenhum bloqueador.

---

## Status dos gaps da 4ª rodada

| # | Gap | Status | Evidência |
|---|---|---|---|
| 1 | Parte 5 com 11 linhas na resposta 3 + emendas com vírgula | ✅ | `diff` contra `8696d4f:README.md`: idêntico |
| 2 | Verde do semáforo reaproveitado no Top 5 | ✅ | `visual.json`: `#64748B`; print reexportado |
| 3 | Relatórios v3/v4 não versionados | ✅ | `f8906ec` |

---

## Gaps por impacto na nota

### Impacto alto

Nenhum.

### Impacto médio

Nenhum.

### Impacto baixo (nice to have)

**1. Rodada de auditoria citada errada no doc do painel** — Painel · ~1 min

`painel/powerbi/powerbi_construcao_painel.md:351-352` e `:376` atribuem a troca do verde-água por cinza-azulado a um achado da "segunda rodada" / "2ª rodada". O achado veio da **4ª** rodada da auditoria de entrega (`_review/entrega_audit_20261019_v4.md`, gap 2). A 2ª rodada não fala dessa cor. Como os relatórios são citados como evidência do processo, a referência deveria apontar para o arquivo certo.

**2. R6 no system prompt** — Agente · ~10 min, opcional

Igual às rodadas anteriores: transforma a melhoria proposta em melhoria aplicada. Exigiria rodar `run_perguntas.py` de novo e atualizar o comentário 4. Só vale se houver tempo e chave de API à mão.

---

## Checklist final antes de submeter

**Corretude (30%)**
- [x] Verificação independente pandas (0.0000) + T-SQL contra `staging` (PASS)
- [x] R6, R7, R10, R11 conferidos contra o enunciado

**Qualidade (20%)**
- [x] Achados com contagem real e reconciliados
- [x] Toda decisão justificada e medida

**Agente de IA (20%)**
- [x] Tools fixas, `respostas.md` real, sem alucinação, sem chave no repo

**Painel (15%)**
- [x] PDF + print + `.pbip`, uma página, justificativa no README
- [x] Semáforo usado só para faixa de score; categorias fora da paleta
- [x] Limitações restantes declaradas

**Perguntas abertas (10%)**
- [x] 3 respostas, 10 linhas cada, pontuação revisada, exemplos concretos do case

**Organização e README (5%)**
- [x] Estrutura, caminhos, reprodução e pendências consistentes
- [x] Relatórios de auditoria versionados

---

## Como re-auditar

```
claude "/auditoria-entrega-mereo"
```

---

*Case Mereo (Grupo Aurora) · /auditoria-entrega-mereo v2.0*
