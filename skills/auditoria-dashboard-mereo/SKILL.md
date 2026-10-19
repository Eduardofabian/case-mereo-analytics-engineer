---
name: auditoria-dashboard-mereo
description: >
  Audita o painel/dashboard (Power BI .pbip, protótipo Streamlit ou HTML)
  do case Mereo contra o star schema do projeto, contra o padrão visual
  real do produto Mereo (módulo Metas) e contra o critério "clareza e
  escolha do que mostrar" do enunciado. Use quando: "audita o painel",
  "o dashboard tá bom?", "confere o pbip antes de entregar".
---

# /auditoria-dashboard-mereo

Específica para este projeto: conhece o star schema de `marts`, as
regras R1-R11 e o layout real do módulo Metas da Mereo (ver
`references/contexto-produto-mereo.md`) — não é um checklist genérico de
boas práticas de BI.

---

## Pré-requisitos

- `painel/` com PDF/print e, se possível, o arquivo-fonte (`.pbip`,
  código Streamlit/HTML)
- `respostas/p1_score_colaborador.csv`, `p2_score_area.csv`,
  `p3_gestores.csv` para conferência cruzada de números

---

## Ambientes de execução

### Modo com acesso a filesystem (Claude Code ou device bridge)
- Input: leio o arquivo-fonte do painel e os CSVs de `respostas/`
  diretamente do repositório.
- Output: salvo em `./_review/dashboard_audit_YYYYMMDD.md`.

### Modo Claude.ai Web (upload)
- Input: usuário sobe o PDF/print do painel e os 3 CSVs de `respostas/`.
- Output: arquivo `.md` como artifact para download.

---

## Processo

**1. Ler o contexto de produto**
Ler `references/contexto-produto-mereo.md` — define o padrão visual que
o avaliador reconhece do produto real (semáforo, hierarquia).

**2. Checar fidelidade e modelo**
Ler `references/checks-modelo-fidelidade.md`. Pegar 3 valores do painel
(um colaborador, uma área, um gestor) e conferir contra os CSVs de
`respostas/`. Verificar se o modelo consome `vw_score_*` ou recalcula
regra em DAX.

**3. Checar clareza e escolha do que mostrar**
Ler `references/checks-clareza-escolha.md`. Confirmar página única,
visão agregada dominante, justificativa escrita da escolha, e os dois
elementos visuais do produto real (semáforo, hierarquia).

**4. Checar qualidade técnica do modelo (se `.pbip`)**
Relacionamentos, direção de join, `ISINSCOPE`, duplicação de linha.

**5. Calcular score**
```
score = nota_fidelidade×0.40 + nota_clareza×0.40 + nota_tecnica×0.20
```
(pesos internos desta skill — o enunciado dá 15% agregado ao critério
"Painel" no case inteiro; não confundir os dois números)

- Score ≥ 85 → `FORTE`
- Score 70-84 → `BOM — gaps pontuais`
- Score 55-69 → `MÉDIO — lacunas relevantes`
- Score < 55 → `FRACO — revisão estrutural`

**6. Gerar output**
Usar `templates/dashboard-audit.md`. Salvar como
`./_review/dashboard_audit_YYYYMMDD.md`.

**7. Resumo no chat**
Score + label, divergências numéricas encontradas (se houver, com o
valor de cada lado), e avaliação de "clareza e escolha do que mostrar":
o que está bem escolhido, o que falta justificar, o que está em excesso
para uma única página de diretoria.

---

## Reprovação imediata — verificar primeiro

1. Nenhum PDF/print do painel entregue em `painel/`.
2. Painel com mais de uma página/aba.
3. Nenhuma justificativa escrita da escolha do que mostrar (nem no
   README, nem no próprio painel).

Se qualquer um desses for verdadeiro → **BLOQUEADO — resolver antes de
qualquer correção de detalhe**.

---

## Tom do output

Direto, tom de revisão técnica na véspera da entrega. Dizer o que falta,
o quanto impacta e como corrigir rápido. Quando relevante, ancorar a
crítica no padrão visual real do produto (não é opinião de design, é
comparação com o que a empresa já constrói).

- ✅ "Sem semáforo de atingimento nas células de nota — o Painel de
  Performance real da Mereo usa essa convenção (verde/amarelo/vermelho
  por faixa R6), e a ausência aqui lê como lacuna de pesquisa de
  produto, não só estética."
- ❌ "O painel poderia ter mais cores para ficar mais bonito."

---

## Output: sempre .md

Nunca gerar HTML para este output.

---

## Versão

`v2.0` — Case Mereo (Grupo Aurora), Analytics Engineer Pleno, Out/2026.
Estrutura modular (`references/` + `templates/`) inspirada no padrão
`/hackathon-tech-audit` (Hackathon Seazone Jovens Talentos), adaptada com
contexto específico do produto real da Mereo.
