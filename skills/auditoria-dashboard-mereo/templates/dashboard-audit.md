# Auditoria de Dashboard · Case Mereo (Grupo Aurora) · {{PROJECT_NAME}}
> Score: **{{SCORE}}/100 — {{SCORE_LABEL}}**
> Gerado por `/auditoria-dashboard-mereo` em {{TIMESTAMP}}

---

## Veredicto

{{VERDICT}}

| | |
|---|---|
| Issues totais | **{{TOTAL_ISSUES}}** |
| Críticos | **{{CRITICAL_COUNT}}** |
| Médios | **{{MEDIUM_COUNT}}** |
| Leves | **{{LIGHT_COUNT}}** |

---

## Score por eixo (pesos internos desta auditoria — o enunciado dá 15%
## agregado para "Painel"; os pesos abaixo são como esta skill decompõe
## esse critério, não peso formal do enunciado)

| Eixo | Peso interno | Nota | Issues |
|---|---|---|---|
| Fidelidade ao dado de origem e ao modelo | 40% | {{NOTA_FIDELIDADE}}/10 | {{N_FIDELIDADE}} |
| Clareza e escolha do que mostrar | 40% | {{NOTA_CLAREZA}}/10 | {{N_CLAREZA}} |
| Qualidade técnica do modelo (DAX/relacionamentos) | 20% | {{NOTA_TECNICA}}/10 | {{N_TECNICA}} |

---

## Verificação de reprovação imediata

| Critério | Status |
|---|---|
| PDF ou print do painel presente em `painel/` | {{STATUS_PDF}} |
| Arquivo/código-fonte presente em `painel/` | {{STATUS_FONTE}} |
| Painel é uma página só | {{STATUS_UMA_PAGINA}} |
| Justificativa da escolha do que mostrar, por escrito | {{STATUS_JUSTIFICATIVA}} |

{{REPROVACAO_ALERTA}}

---

## Issues — ordem de impacto

{{ISSUES_BLOCKS}}

---

## Checklist de entrega do painel

- [ ] Totais batem com os 3 CSVs de `respostas/` (3 valores conferidos manualmente)
- [ ] `vw_score_*` consumido diretamente, sem recalcular R1-R11 em DAX
- [ ] R11 (Direto vs. Consolidado) distinguível visualmente
- [ ] Semáforo de nota (verde/amarelo/vermelho) presente, espelhando o produto real
- [ ] Alguma hierarquia visual presente, espelhando a Árvore de Performance real
- [ ] Uma página só, como pedido
- [ ] Justificativa da escolha do que mostrar documentada
- [ ] Caminhos relativos ou limitação de portabilidade documentada no README

---

## Formato de cada issue

```
### [SEVERIDADE] · [CATEGORIA] · Título

**Onde:** `caminho/arquivo` (página/visual quando aplicável)

**Por que importa:**
Explicação com nomes reais do projeto e, quando aplicável, referência ao
padrão do produto real da Mereo.

**Como corrigir:**
Passo prático.
```

---

## Como re-auditar

```
claude "/auditoria-dashboard-mereo"
```

---

*Case Mereo (Grupo Aurora) · /auditoria-dashboard-mereo v2.0*
