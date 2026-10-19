---
name: auditoria-entrega-mereo
description: >
  Auditoria de entrega do case Mereo (Grupo Aurora — Analytics Engineer
  Pleno) contra os 6 critérios e pesos exatos do enunciado, com o
  contexto real da vaga e do produto Mereo incorporado. Lê o repositório
  inteiro e devolve score por critério, gaps priorizados por impacto na
  nota e um veredito de prontidão. Use quando: "tô pronto pra entregar?",
  "o que tá faltando?", "audita o case", "me dá uma nota".
---

# /auditoria-entrega-mereo

Skill de auditoria específica para este case — não um checklist genérico
de hackathon ou processo seletivo. Conhece os 6 critérios e pesos exatos
do enunciado (`material_original/ENUNCIADO.docx`/`.pdf`), as regras de
negócio R1-R11, e o contexto real da vaga e do produto da Mereo (ver
`references/contexto-mereo.md`) — usa tudo isso para calibrar o que conta
como gap grave vs. detalhe.

---

## Pré-requisitos

Repositório com ao menos:
- `README.md`
- `sql/`, `respostas/`, `painel/`, `agente/` conforme estrutura pedida
- `material_original/ENUNCIADO.docx` ou `.pdf` (para conferir o texto
  literal do enunciado quando houver dúvida de regra)

---

## Ambientes de execução

### Modo com acesso a filesystem (Claude Code ou device bridge)
- Input: leio automaticamente o repositório inteiro — README, sql/,
  respostas/, painel/, agente/, qualidade (ou `etl/verificacao/` após
  reorganização).
- Output: salvo em `./_review/entrega_audit_YYYYMMDD.md`.

### Modo Claude.ai Web (upload)
- Input: usuário sobe o README.md e os CSVs de `respostas/` no mínimo;
  idealmente o repositório zipado.
- Output: arquivo `.md` como artifact para download.

---

## Processo

**1. Ler o contexto do case**
Ler `references/contexto-mereo.md` — isso calibra o rigor da auditoria
(ver seção "o que isso muda na auditoria" naquele arquivo).

**2. Mapear os entregáveis**
Verificar existência e conteúdo real (não apenas existência do arquivo)
de:
- [ ] `respostas/p1_score_colaborador.csv`, `p2_score_area.csv`, `p3_gestores.csv`
- [ ] `etl/verificacao_independente.py` (ou caminho atualizado)
- [ ] Relatório de achados de qualidade
- [ ] `agente/` com código e `respostas.md` preenchido
- [ ] `painel/` com PDF/print + fonte
- [ ] Seção de Parte 5 (perguntas abertas) no README
- [ ] Estrutura de pastas conforme pedido

**3. Avaliar cada critério**
Ler `references/criterios-corretude-qualidade.md` (critérios 1+2, 50% da
nota — auditar com mais rigor),
`references/criterios-agente-perguntas.md` (critérios 3+5, 30%) e
`references/criterios-painel-organizacao.md` (critérios 4+6, 20%).
Para cada critério, atribuir nota parcial (0-10) e listar gaps.

**4. Calcular score final**
```
score = nota_corretude×0.30 + nota_qualidade×0.20 + nota_agente×0.20
      + nota_painel×0.15 + nota_perguntas×0.10 + nota_org×0.05
```
(cada nota em escala 0-10, score final em escala 0-100)

- Score ≥ 85 → `FORTE — pronto para submeter`
- Score 70-84 → `BOM — gaps pontuais, corrigíveis`
- Score 55-69 → `MÉDIO — lacunas relevantes antes de submeter`
- Score < 55 → `FRACO — revisão estrutural necessária`

**5. Gerar output**
Usar `templates/entrega-audit.md` como estrutura. Salvar como
`./_review/entrega_audit_YYYYMMDD.md`.

**6. Resumo no chat**
- Score final + label
- Top 3 gaps com maior impacto na nota (peso do critério × gravidade)
- Tempo estimado para corrigir cada gap, dado que o prazo é curto

---

## Reprovação imediata — verificar primeiro

Antes de qualquer nota, checar os bloqueadores binários:

1. Algum dos 3 CSVs de `respostas/` ausente ou vazio.
2. `etl/verificacao_independente.py` ausente, ou reusa view/SQL do
   projeto (não é independente de verdade).
3. Estrutura de pastas não bate com `README.md`/`sql/`/`respostas/`/
   `painel/`/`agente/`.
4. `agente/respostas.md` (ou equivalente) com placeholder não preenchido.
5. Nenhuma das 3 perguntas abertas respondida.

Se qualquer um desses for verdadeiro → **BLOQUEADO — resolver antes de
qualquer outra correção, independente do score calculado**.

---

## Tom do output

Direto e orientado a ação, calibrado pelo contexto real da vaga (ver
`references/contexto-mereo.md`): decisão sem justificativa pesa mais
aqui do que em auditoria genérica, porque fere os valores declarados
("Excelência" = nunca fazer "mais ou menos"). Não elogiar o que já
funciona sem necessidade — focar no que muda a nota.

- ✅ "R7 aplicado corretamente no código, mas o README generaliza a regra
  sem citar que o peso vem da meta compartilhada, não da referenciada —
  um avaliador que conhece a regra de cor vai notar a imprecisão. Risco:
  -1 a -2 pontos no critério de corretude, mesmo com o número certo."
- ❌ "O projeto demonstra boa aplicação das regras de negócio."

---

## Output: sempre .md

Nunca gerar HTML ou artifact visual para este output — `.md` direto no
repositório, consistente com a preferência de entrega deste case.

---

## Versão

`v2.0` — Case Mereo (Grupo Aurora), Analytics Engineer Pleno, Out/2026.
Estrutura modular (`references/` + `templates/`) inspirada no padrão
`/hackathon-project-audit` (Hackathon Seazone Jovens Talentos), adaptada
com contexto específico da vaga e do produto real da Mereo.
