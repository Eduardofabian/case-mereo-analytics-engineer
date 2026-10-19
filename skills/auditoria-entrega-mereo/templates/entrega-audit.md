# Auditoria de Entrega · Case Mereo (Grupo Aurora) · {{PROJECT_NAME}}
> Score estimado: **{{SCORE}}/100 — {{SCORE_LABEL}}**
> Gerado por `/auditoria-entrega-mereo` em {{TIMESTAMP}}

---

## Veredicto

{{VERDICT}}

---

## Score por critério (pesos exatos do enunciado)

| Critério | Peso | Nota estimada | Pontos | Gaps críticos |
|---|---|---|---|---|
| Corretude dos números (Parte 1) | 30% | {{NOTA_CORRETUDE}}/10 | {{PONTOS_CORRETUDE}}/30 | {{N_GAPS_CORRETUDE}} |
| Problemas de qualidade | 20% | {{NOTA_QUALIDADE}}/10 | {{PONTOS_QUALIDADE}}/20 | {{N_GAPS_QUALIDADE}} |
| Agente de IA | 20% | {{NOTA_AGENTE}}/10 | {{PONTOS_AGENTE}}/20 | {{N_GAPS_AGENTE}} |
| Painel | 15% | {{NOTA_PAINEL}}/10 | {{PONTOS_PAINEL}}/15 | {{N_GAPS_PAINEL}} |
| Perguntas abertas | 10% | {{NOTA_PERGUNTAS}}/10 | {{PONTOS_PERGUNTAS}}/10 | {{N_GAPS_PERGUNTAS}} |
| Organização e README | 5% | {{NOTA_ORG}}/10 | {{PONTOS_ORG}}/5 | {{N_GAPS_ORG}} |
| **TOTAL** | **100%** | — | **{{SCORE}}/100** | — |

---

## Verificação de reprovação imediata

| Critério | Status |
|---|---|
| `respostas/p1_score_colaborador.csv`, `p2_*`, `p3_*` presentes e com conteúdo | {{STATUS_RESPOSTAS}} |
| `etl/verificacao_independente.py` existe e é independente (não reusa view) | {{STATUS_VERIFICACAO}} |
| Estrutura bate com README.md / sql/ / respostas/ / painel/ / agente/ | {{STATUS_ESTRUTURA}} |
| `agente/respostas.md` sem placeholder | {{STATUS_AGENTE_RESPOSTAS}} |
| As 3 perguntas abertas respondidas | {{STATUS_PERGUNTAS}} |

{{REPROVACAO_ALERTA}}

---

## Gaps por impacto na nota

### Impacto alto (corrigir agora)

{{GAPS_ALTO}}

### Impacto médio (corrigir se houver tempo)

{{GAPS_MEDIO}}

### Impacto baixo (nice to have / diferencial da vaga não atendido)

{{GAPS_BAIXO}}

---

## Checklist final antes de submeter

**Corretude (30%)**
- [ ] `verificacao_independente.py` reimplementa R1-R11 sem reusar view do projeto
- [ ] Diferença 0.0000 confirmada entre pandas e os 3 CSVs de resposta
- [ ] R6, R7, R10, R11 conferidos linha a linha contra o enunciado

**Qualidade (20%)**
- [ ] Relatório de achados com contagem numérica real, não vago
- [ ] Toda decisão de tratamento tem justificativa, não só descrição
- [ ] Análise de sensibilidade presente para decisões que mantiveram dado "sujo"

**Agente de IA (20%)**
- [ ] Ferramentas fixas parametrizadas, sem SQL livre
- [ ] `respostas.md` com as 5 respostas e comentários reais, sem placeholder
- [ ] Testado com nome inexistente, sem alucinação

**Painel (15%)**
- [ ] PDF/print + fonte, ambos presentes
- [ ] Uma página só
- [ ] Justificativa da escolha do que mostrar, por escrito

**Perguntas abertas (10%)**
- [ ] 3 respostas, até 10 linhas cada
- [ ] Cada resposta usa exemplo concreto deste projeto

**Organização e README (5%)**
- [ ] Estrutura de pastas conforme pedido
- [ ] README cobre decisões, qualidade, uso de IA, Parte 5, pendências
- [ ] Comando de reprodução do pipeline documentado e testado

---

## Como re-auditar

```
claude "/auditoria-entrega-mereo"
```

---

*Case Mereo (Grupo Aurora) · /auditoria-entrega-mereo v2.0*
