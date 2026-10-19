# Auditoria de Dashboard · Case Mereo (Grupo Aurora) · Dashboard_case_mereo.pbip
> Score: **84/100 — BOM — gaps pontuais**
> Gerado por `/auditoria-dashboard-mereo` em 2026-10-19 (HEAD `0daa6c6`, print/PDF reexportados após a 1ª auditoria de entrega)

---

## Veredicto

Os números estão certos e o modelo está bem desenhado. Nenhuma medida DAX recalcula R1–R11: todas agregam `vw_score_*` já resolvidas e aplicam R10 via `dim_colaborador[flag_elegivel_r10]`. Os 3 valores sorteados batem com `respostas/`. Os dois elementos que o avaliador reconhece do produto real estão presentes: semáforo por faixa e matriz Direto/Consolidado no padrão da Árvore de Performance. Isso já é um diferencial.

O que segura a nota em "BOM" é de leitura, não de dado:

1. A **cor muda de significado** entre visuais da mesma página.
2. A **hierarquia da matriz não aparece** visualmente: recuo 0 e tudo em negrito.
3. O Top/Bottom de gestores depende de um **filtro manual por nome**, que congela o resultado.

Os três se corrigem em menos de 1h no Desktop.

| | |
|---|---|
| Issues totais | **7** |
| Críticos | **0** |
| Médios | **3** |
| Leves | **4** |

---

## Score por eixo (pesos internos desta auditoria — o enunciado dá 15% agregado para "Painel"; os pesos abaixo são como esta skill decompõe esse critério, não peso formal do enunciado)

| Eixo | Peso interno | Nota | Issues |
|---|---|---|---|
| Fidelidade ao dado de origem e ao modelo | 40% | 9.0/10 | 1 |
| Clareza e escolha do que mostrar | 40% | 8.0/10 | 4 |
| Qualidade técnica do modelo (DAX/relacionamentos) | 20% | 8.0/10 | 2 |

`score = 9.0×0.40 + 8.0×0.40 + 8.0×0.20 = 8.4 → 84/100`

---

## Verificação de reprovação imediata

| Critério | Status |
|---|---|
| PDF ou print do painel presente em `painel/` | ✅ `painel/entrega/Mereo_Case_Dashboard_Pwbi.png` + `Dashboard_case_mereo.pdf` |
| Arquivo/código-fonte presente em `painel/` | ✅ `painel/powerbi/Dashboard/Dashboard_case_mereo.pbip` |
| Painel é uma página só | ✅ `pages.json` com 1 página; PDF com 1 página |
| Justificativa da escolha do que mostrar, por escrito | ✅ README, parágrafo "O que o painel mostra e por quê" no início da seção Painel |

Nenhum bloqueador.

---

## Conferência numérica (3 valores do print contra `respostas/`)

| Nível | No painel | No CSV | Status |
|---|---|---|---|
| Colaborador — Paula Cardoso (135), Zona Crítica | 18 | `p1`: 18.17 | ✅ |
| Área — Diretoria Financeira (10) | Direto 104,33 / Consolidado 103,30 | `p2`: 104.33 / 103.30 | ✅ |
| Gestor — Sofia Queiroz (171), Top 1 | 102 | `p3`: top,1,171,102.00 | ✅ |

Também conferido: score médio 95,74, mediana 100,36, 72 elegíveis, 9 críticos e 26 intermediários (a distribuição 37/26/9 soma 72, ou seja, só elegíveis). Os 6 gestores de Top/Bottom batem com `p3_gestores.csv`. **Nenhuma divergência numérica.**

---

## Issues — ordem de impacto

### MÉDIO · Clareza · A mesma cor significa coisas diferentes na mesma página

**Onde:** `painel/entrega/*` — "Distribuição de Score", "Gestores — Top e Bottom", "Top 5 Colaboradores"

**Por que importa:**
A barra de distribuição define a legenda da página: verde ≥100, laranja 80–100, vermelho crítico <80. É o semáforo do Painel de Performance real da Mereo, e o leitor aprende essa convenção primeiro. Logo abaixo, dois visuais quebram a convenção:
- **Bottom 3 gestores em vermelho** com 84, 91 e 93. Pela legenda, vermelho é "<80". Rafael Jardim (91) e Sofia Oliveira (93) estão na faixa laranja, e um diretor lendo a página conclui que eles são críticos.
- **Top 5 colaboradores coloridos por gerência**: laranja = Gerência de Controladoria. As barras com 118 e 113 ficam da mesma cor da faixa "80–100".

O avaliador usa o semáforo do produto todo dia. Cor com dois significados na mesma tela lê como descuido de convenção, não como escolha.

**Como corrigir:**
- Bottom 3: cor neutra (cinza escuro) para Top e Bottom, deixando o contraste pela posição e pelo título. Outra opção é formatação condicional pelo próprio semáforo (Olívia 84 → laranja, não vermelho).
- Top 5: cor única neutra, ou semáforo (todos ≥100 → verde). A gerência vai para o rótulo do eixo ("Quésia Siqueira · Controladoria"), não para a cor.

---

### MÉDIO · Clareza · A matriz Direto/Consolidado não mostra a hierarquia que ela representa

**Onde:** `painel/powerbi/.../visuals/843c7382d78ecbee8b6b/visual.json` — `rowHeaders.steppedLayoutIndentation = 0D`

**Por que importa:**
Diretorias e gerências aparecem com o mesmo recuo e o mesmo negrito. "Gerência de Controladoria" fica visualmente no mesmo nível que "Diretoria Financeira", e só a ordem das linhas sugere que uma está dentro da outra. É justamente a matriz que espelha a Árvore de Performance (R11). Sem recuo, o leitor não entende por que algumas linhas têm Consolidado e outras não. O subtítulo explica em texto, mas a estrutura deveria dizer isso sozinha.

**Como corrigir:** Formatar → Cabeçalhos de linha → recuo em layout de nível = 12–16px. Opcional: tirar o negrito do nível 1. Reexportar o print/PDF.

---

### MÉDIO · Técnica/Fidelidade · Top 3 / Bottom 3 de gestores congelados por filtro manual de nome

**Onde:** visuais `1b114eec8ab83aede9df` (Top) e `91cdeaabdb88c1d9389c` (Bottom) — filtro básico em `Nome do Gestor` com 3 nomes fixos cada

**Por que importa:**
O README documenta a decisão: o Top N nativo nunca funcionou de forma confiável. Mas o efeito colateral não está dito. Se `vw_score_gestor` for reprocessada (dado novo, correção, a ingestão via API da Parte 5), o painel continua mostrando os mesmos 6 nomes, com o valor novo de cada um e **sem reordenar**. É exatamente a divergência silenciosa que o pipeline inteiro foi construído para evitar. Hoje bate; o risco é estrutural.

**Como corrigir (escolher um):**
- coluna `rank_top` / `rank_bottom` calculada na view `marts.vw_score_gestor` (SQL, onde a regra já mora) e filtro `rank <= 3` no visual. Robusto e coerente com "regra no SQL, painel só consome";
- ou uma frase no README, em "Limitações conhecidas", dizendo que os nomes estão fixos e precisam ser revisados a cada carga.

---

### LEVE · Clareza · Separador decimal inconsistente no mesmo card

**Onde:** card "Score Médio do Ciclo" — `95,74` (padrão pt-BR) e `Mediana 100.36` (medida `Score Mediano Ciclo (texto rodapé)` usa `FORMAT(..., "0.00", "en-US")`)

**Por que importa:** dois números do mesmo card com separadores diferentes. O resto do painel usa vírgula.

**Como corrigir:** trocar `"en-US"` por `"pt-BR"` na medida.

---

### LEVE · Clareza · Cabeçalho "Area" sem acento

**Onde:** matriz de áreas, `displayName` da linha. O Desktop sobrescreveu "Área" ao salvar.

**Como corrigir:** renomear o campo no visual para "Área".

---

### LEVE · Clareza · "Abaixo da meta (100)" sem âncora explícita

**Onde:** card "Abaixo da Meta (100)" e as faixas 80/100 da distribuição

**Por que importa:** o enunciado define o corte de 80% para a *nota da meta* (R6), não para o *score do colaborador*. Usar 80 e 100 como faixas de score é uma leitura razoável (score 100 ≈ atingimento médio de 100%), mas é uma decisão do painel, e o README só lista as faixas, sem dizer de onde vêm. Um avaliador atento a R6 pode perguntar.

**Como corrigir:** meia frase no parágrafo do painel no README: "faixas de score espelham os cortes de R6 (80%/100% de atingimento), aplicados ao score ponderado".

---

### LEVE · Técnica · Tabelas de data automáticas no modelo

**Onde:** `SemanticModel/definition/tables/LocalDateTable_*` e `DateTableTemplate_*`, criadas pela opção "Data/hora automática" para `data_admissao` e `data_desligamento`

**Por que importa:** nenhum visual usa data. São 3 tabelas ocultas que só aumentam o modelo e o diff do `.pbip`. Detalhe, mas um avaliador que abre o modelo vê.

**Como corrigir:** Arquivo → Opções → Carga de dados → desmarcar "Data/hora automática" para o arquivo atual.

---

## O que está bem (não mexer)

- **Zero regra de negócio em DAX.** Todas as medidas são `AVERAGE`/`MEDIAN`/`COUNTROWS`/`SUM` sobre `vw_score_*`, e R10 vem pronto de `flag_elegivel_r10`. É o padrão que `checks-modelo-fidelidade.md` pede.
- **R10 aplicado em todo visual individual:** Zona Crítica e Top 5 filtram `flag_elegivel_r10 = 1`. Testado: sem o filtro, Gustavo Esteves e Júlia Ferraz (33,72, não elegíveis) entrariam na Zona Crítica.
- **O `ISINSCOPE` que o README descreve está de fato no arquivo** (medida `Area Atual`), assim como o `Is Leaf` + filtro visual da correção das linhas fantasma.
- **R11 distinguível:** Direto e Consolidado lado a lado. Consolidado só aparece quando difere, com subtítulo explicando a convenção.
- **Relacionamentos:** dimensão → fato com cardinalidade correta. Os dois bidirecionais são 1:1 (`vw_score_*` ↔ dimensão) e não causam ambiguidade. `fact_meta_valor_mensal` não é usada em nenhum visual, então não há risco de duplicação na cadeia fato → colaborador → área.
- **Portabilidade:** o caminho absoluto em `File.Contents` aponta para `painel/dados/`, que bate com a estrutura atual e está documentado em "Limitações conhecidas".

---

## Checklist de entrega do painel

- [x] Totais batem com os 3 CSVs de `respostas/` (3 valores conferidos + KPIs e gestores)
- [x] `vw_score_*` consumido diretamente, sem recalcular R1-R11 em DAX
- [x] R11 (Direto vs. Consolidado) distinguível visualmente
- [x] Semáforo de nota (verde/amarelo/vermelho) presente, espelhando o produto real (mas com reuso de cor, ver issue 1)
- [ ] Hierarquia visual legível, espelhando a Árvore de Performance real. **Matriz sem recuo (issue 2)**
- [x] Uma página só, como pedido
- [x] Justificativa da escolha do que mostrar documentada
- [x] Caminhos absolutos documentados no README

---

## Como re-auditar

```
claude "/auditoria-dashboard-mereo"
```

---

*Case Mereo (Grupo Aurora) · /auditoria-dashboard-mereo v2.0*
