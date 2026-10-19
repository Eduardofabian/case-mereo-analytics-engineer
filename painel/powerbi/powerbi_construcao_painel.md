# Construção do Painel no Power BI — Resultado do Ciclo 2025 (Grupo Aurora)

Guia único de construção: modelo de dados, paleta/tipografia e cada card,
com o DAX e a configuração de visual **exatamente como ficaram no `.pbip`
final** (`Dashboard_case_mereo.pbip`), conferidos linha a linha no arquivo,
não reconstruídos de memória. Substitui os dois documentos anteriores
(`powerbi_spec.md`, pré-build, e a primeira versão deste arquivo, que
descrevia o plano antes de bater de frente com o Power BI de verdade) —
onde o plano original e o resultado final divergem, isso está marcado
explicitamente, porque a divergência em si é parte do que este case avalia
("problemas encontrados e decisões justificadas"). O processo de decisão
completo (por que Streamlit → HTML/Figma → Power BI) está no README
principal, seção "Painel — processo de decisão"; este arquivo é só a
construção técnica.

## Modelo de dados

Star schema já validado (`marts`), consumido via `painel/dados/*.csv`
(caminho absoluto no Power Query — não mover essa pasta):

- `dim_area`, `dim_colaborador`, `dim_meta`, `fact_meta_valor_mensal`
- `vw_score_colaborador`, `vw_score_area`, `vw_score_gestor`

**Atenção, confirmado no modelo:** `vw_score_colaborador` tem **81 linhas**
(um score por colaborador, incluindo os 9 inelegíveis por R10), não 72.
Qualquer medida que agregue essa view direto, sem filtrar
`dim_colaborador[flag_elegivel_r10] = 1`, dá número errado silenciosamente
(média dos 81 = 94.32 vs. média dos 72 elegíveis = 95.74, a validada).
Todas as medidas abaixo que usam essa view já têm o filtro embutido.
`vw_score_area` e `vw_score_gestor` já vêm prontas e filtradas pela origem
(R9–R11 aplicadas lá) — agregação direta funciona sem filtro adicional.

## Paleta e tipografia

Extraído diretamente do CSS de `painel/html/painel_mereo_final.html`
(`:root` + regras por elemento) — é a fonte de verdade de design, usada
tanto no mockup quanto no Power BI.

**Fonte:** `Inter`, fallback `Manrope`, `-apple-system`, `BlinkMacSystemFont`,
`Segoe UI`, sans-serif.

| Token | Cor | Uso |
|---|---|---|
| `--mereo-purple` | `#6227EA` | Destaque primário (KPI 1, topbar) |
| `--mereo-orange` | `#FF5C39` | Destaque / faixa intermediária (80–100) |
| `--good` | `#1F9254` | Faixa boa (≥100) |
| `--bad` | `#E5484D` | Faixa crítica (<80) |
| `#6227EA` (Top 3) / `#06B6D4` (Bottom 3) | — | Gestores Top/Bottom — comparação relativa, fora do semáforo acima (ver seção própria) |
| `#2A78D6` / `#64748B` / `#E87BA4` / `#EDA100` | — | Top 5 Colaboradores — categórico por área, fora do semáforo (ver seção própria) |
| `--ink` | `#1C1C1C` | Texto principal |
| `--ink-soft` | `#6B7280` | Texto secundário / rótulos |
| `--bg-page` | `#F7F7F9` | Fundo da página |
| `--bg-card` | `#FFFFFF` | Fundo dos cards |
| `--bg-dark` | `#212529` | Topbar |
| `--border` | `#ECECF0` | Bordas |

| Elemento | Tamanho | Peso |
|---|---|---|
| Título topbar | 13.5px | 700 |
| Rótulo de KPI (uppercase) | 10.5px | 700 |
| Valor de KPI | 23px | 800 |
| Rodapé de KPI | 11px | 400 |
| Título de painel/card | 12.5px | 700 |
| Subtítulo de painel | 10px | 400 |
| Cabeçalho de tabela (uppercase) | 8–8.5px | 700 |
| Linha de tabela/matriz | 8.5–10px | 600 |
| Badge de score | 8.5–10.5px | 800 |

Esses valores são os do mockup HTML (1280×720); no Power BI Desktop os
tamanhos de fonte foram ajustados para cima nos visuais (ex.: matriz em
11px, ver "Score por Área" abaixo) porque os valores originais, pensados
pra renderização de navegador em escala exata, ficam ilegíveis nos
controles nativos do Power BI — mesma lógica de cor e hierarquia visual,
tamanho recalibrado pra legibilidade real.

## Medidas DAX base

```dax
Score Médio Ciclo =
CALCULATE(
    AVERAGE ( vw_score_colaborador[score] ),
    dim_colaborador[flag_elegivel_r10] = 1
)

Score Mediano Ciclo (texto rodapé) =
VAR Mediana =
    CALCULATE (
        MEDIAN ( vw_score_colaborador[score] ),
        dim_colaborador[flag_elegivel_r10] = 1
    )
RETURN
"Mediana " & FORMAT ( Mediana, "0.00", "en-US" )

Elegiveis =
CALCULATE(
    COUNTROWS ( dim_colaborador ),
    dim_colaborador[flag_elegivel_r10] = 1
)

Total Colaboradores = COUNTROWS ( dim_colaborador )

Zona Critica Qtd =
CALCULATE(
    COUNTROWS ( vw_score_colaborador ),
    dim_colaborador[flag_elegivel_r10] = 1,
    vw_score_colaborador[score] < 80
)

Zona Critica Pct = DIVIDE ( [Zona Critica Qtd], [Elegiveis] )

Intermediario Qtd =
CALCULATE(
    COUNTROWS ( vw_score_colaborador ),
    dim_colaborador[flag_elegivel_r10] = 1,
    vw_score_colaborador[score] >= 80,
    vw_score_colaborador[score] < 100
)

Intermediario Pct = DIVIDE ( [Intermediario Qtd], [Elegiveis] )

Acima Meta Qtd =
CALCULATE(
    COUNTROWS ( vw_score_colaborador ),
    dim_colaborador[flag_elegivel_r10] = 1,
    vw_score_colaborador[score] >= 100
)

Acima Meta Pct = DIVIDE ( [Acima Meta Qtd], [Elegiveis] )

Abaixo Meta Qtd = [Zona Critica Qtd] + [Intermediario Qtd]
Abaixo Meta Pct = DIVIDE ( [Abaixo Meta Qtd], [Elegiveis] )

Elegiveis Subtitulo = "de " & [Total Colaboradores] & " colaboradores"

Abaixo Meta Subtitulo =
  [Zona Critica Qtd] & " críticos + " & [Intermediario Qtd] & " intermediários"

Rotulo Distribuicao = "Ciclo 2025"
```

Checagem: `[Score Médio Ciclo]` = 95.74 · `[Elegiveis]` = 72 ·
`[Zona Critica Qtd]` = 9 · `[Intermediario Qtd]` = 26 ·
`[Acima Meta Qtd]` = 37 · `[Abaixo Meta Pct]` = 48.6%.

---

## KPIs 1–4 (topo)

**Visual real:** `Card` (o novo visual nativo do Power BI, não
`Multi-row Card` como o plano original sugeria) — 7 cards no total: os 4
valores principais mais 3 rodapés/subtítulos como cards próprios
posicionados por baixo, porque o `Card` novo não tem campo de subtítulo
livre, só o `Multi-row Card` antigo teria — e mesmo esse não dá o controle
visual exato do HTML. Usar dois `Card`s empilhados (valor + rodapé)
funcionou melhor na prática do que forçar o `Multi-row Card`.

1. **Score médio do ciclo** — `[Score Médio Ciclo]` + rodapé
   `[Score Mediano Ciclo (texto rodapé)]`. Cor: roxo `#6227EA`.
2. **Elegíveis** — `[Elegiveis]` + rodapé `[Elegiveis Subtitulo]`. Cor:
   cinza neutro `#9CA3AF`.
3. **Zona crítica (<80)** — `[Zona Critica Qtd]` + `[Zona Critica Pct]`.
   Cor: vermelho `#E5484D`.
4. **Abaixo da meta (100)** — `[Abaixo Meta Pct]` + rodapé
   `[Abaixo Meta Subtitulo]`. Cor: laranja `#FF5C39`.

---

## Barra de Distribuição de Score

**Visual real:** `hundredPercentStackedBarChart` (100% Empilhada),
horizontal, confirmado no `.pbip`.

- Eixo Y (categoria): medida `[Rotulo Distribuicao]` = `"Ciclo 2025"`
  (texto fixo) — gera uma única barra cheia.
- Valores: `[Zona Critica Pct]`, `[Intermediario Pct]`, `[Acima Meta Pct]`.
- Cores por série: vermelho `#E5484D` / laranja `#FF5C39` / verde `#1F9254`.
- Correção de construção: o `COUNTROWS` das medidas de quantidade
  inicialmente dava 81 em vez de 72 por não filtrar `flag_elegivel_r10` —
  corrigido envolvendo em `CALCULATE(..., dim_colaborador[flag_elegivel_r10] = 1)`,
  já refletido acima.

---

## Score por Área — Direto vs. Consolidado

**Visual real:** `pivotTable` (Matriz), layout "Compact", com botões de
expandir/colapsar, fonte 11px nos cabeçalhos de linha.

**Hierarquia de linhas** — não são 3 colunas manuais com `LOOKUPVALUE`
subindo o pai (como o plano original sugeria): o `.pbip` usa `PATH()` +
`PATHITEM()` de verdade, resolvendo nome em cada nível:

```dax
'Area Path' = PATH ( dim_area[id_area], dim_area[id_area_pai] )

'Area Nivel 0' =
LOOKUPVALUE ( dim_area[nome], dim_area[id_area], PATHITEM ( dim_area[Area Path], 1, INTEGER ) )

'Area Nivel 1' =
VAR IdNivel1 = PATHITEM ( dim_area[Area Path], 2, INTEGER )
RETURN IF ( NOT ISBLANK ( IdNivel1 ), LOOKUPVALUE ( dim_area[nome], dim_area[id_area], IdNivel1 ) )

'Area Nivel 2' =
VAR IdNivel2 = PATHITEM ( dim_area[Area Path], 3, INTEGER )
RETURN IF ( NOT ISBLANK ( IdNivel2 ), LOOKUPVALUE ( dim_area[nome], dim_area[id_area], IdNivel2 ) )
```

Linhas da matriz: `Area Nivel 0` → `Area Nivel 1` → `Area Nivel 2`.

**Linhas fantasma em branco (bug real, corrigido):** a própria linha de
cada área-pai aparecia na matriz como um nível hierárquico "vazio"
separado. Corrigido com uma coluna booleana e um filtro de visual:

```dax
'Is Leaf' =
VAR MeuId = dim_area[id_area]
RETURN
    COUNTROWS ( FILTER ( dim_area, dim_area[id_area_pai] = MeuId ) ) = 0
```

Filtro de visual na matriz: `Is Leaf = TRUE`.

**Caso de borda "pai com filho único" (Gerência de Logística) — corrigido
com `ISINSCOPE`:** mesmo com o filtro acima, a medida que decidia "qual é
a área ativa nesta linha da matriz" usava `SELECTEDVALUE`/`COALESCE`
andando pelos 3 níveis — e isso falha quando um pai tem exatamente um
filho, porque não há ambiguidade suficiente pra forçar o nível certo.
A medida final usa `ISINSCOPE`, que detecta o nível de agrupamento
realmente ativo, não o valor mais "específico" disponível:

```dax
'Area Atual' =
SWITCH (
    TRUE (),
    ISINSCOPE ( dim_area[Area Nivel 2] ), SELECTEDVALUE ( dim_area[Area Nivel 2] ),
    ISINSCOPE ( dim_area[Area Nivel 1] ), SELECTEDVALUE ( dim_area[Area Nivel 1] ),
    SELECTEDVALUE ( dim_area[Area Nivel 0] )
)

'Score Direto (Matriz)' =
VAR AreaAtual = [Area Atual]
RETURN
    CALCULATE ( [Score Direto], REMOVEFILTERS ( dim_area ), dim_area[nome] = AreaAtual )

'Score Consolidado Exibir (Matriz)' =
VAR AreaAtual = [Area Atual]
VAR Direto = CALCULATE ( [Score Direto], REMOVEFILTERS ( dim_area ), dim_area[nome] = AreaAtual )
VAR Consolidado = CALCULATE ( [Score Consolidado], REMOVEFILTERS ( dim_area ), dim_area[nome] = AreaAtual )
RETURN
    IF ( ROUND ( Direto, 2 ) = ROUND ( Consolidado, 2 ), BLANK(), Consolidado )
```

(`Score Direto` e `Score Consolidado` são `SUM(vw_score_area[score_direto])`
e `SUM(vw_score_area[score_consolidado])`, somas simples — a view já vem
agregada por área.)

A ideia de "só mostrar Consolidado quando difere de Direto via `ROUND`
igual → `BLANK()`" **era** do plano original e se manteve — o que faltava
era resolver corretamente qual área está ativa em cada linha antes de
aplicar essa lógica, e isso é o que o `Area Atual`/`ISINSCOPE` resolve.

**Colunas:** `Score Direto (Matriz)` (sempre preenchida), `Score
Consolidado Exibir (Matriz)` (só preenchida nas 5 áreas não-folha).

---

## Zona Crítica

**Plano original:** Tabela simples. **Visual final (divergência real,
decisão de UX):** `clusteredBarChart` horizontal — tabela nativa do Power
BI lida mal com hierarquia visual e parecia "menos profissional" que o
mockup; gráfico de barras de uma métrica rankeada por pessoa é mais
legível nativamente.

- Categoria: `dim_colaborador[nome]`.
- Valor: soma de `vw_score_colaborador[score]` (cada colaborador tem uma
  linha só, então soma = o próprio score).
- Filtros do visual: `vw_score_colaborador[score] < 80` **e**
  `dim_colaborador[flag_elegivel_r10] = 1` (filtros avançados).

---

## Gestores — Top 3 / Bottom 3

**Plano original:** 2 Tabelas lado a lado com filtro nativo "Top N".
**Visual final:** 2× `clusteredBarChart`, com **filtro básico manual**
(não Top N) — decisão pragmática depois de 3 bugs encadeados que o Top N
nativo nunca resolveu de forma confiável:

1. Eixo com agregação "Contagem" em vez de "Média" de `score_medio_time`.
2. O campo "Por valor" do próprio filtro Top N (um well separado do eixo,
   fácil de não notar) com a mesma agregação errada.
3. A coluna `Nome do Gestor` estava calculada na tabela errada
   (`dim_colaborador`, na direção "gestor de cada subordinado") — a
   correta vive em `vw_score_gestor`, na direção "nome do próprio gestor":
   ```dax
   'Nome do Gestor' =
   LOOKUPVALUE ( dim_colaborador[nome], dim_colaborador[id_colaborador], vw_score_gestor[id_gestor] )
   ```

Mesmo depois de corrigir os três, o Top N nativo continuou não confiável
— decisão final foi abandoná-lo e aplicar um **filtro categórico básico**
com os nomes exatos de cada grupo (confirmado no `.pbip`):

- **Top 3:** categoria `vw_score_gestor[Nome do Gestor]` ∈
  {Gustavo Vasconcelos, Sofia Queiroz, Mariana Siqueira}.
- **Bottom 3:** ∈ {Olívia Queiroz, Sofia Oliveira, Rafael Jardim}.
- Valor em ambos: média de `vw_score_gestor[score_medio_time]`.

**Correção de paleta (auditoria `/auditoria-dashboard-mereo`):** o Bottom 3
usava vermelho só porque são os 3 piores do grupo — mas Rafael Jardim (91)
e Sofia Oliveira (93) não são críticos de verdade (faixa 80-100, que é
laranja na legenda de "Distribuição de Score"). Vermelho aqui colidia com
o significado fixado por essa legenda ("crítico, <80"). Trocado por um par
que não é do semáforo de score — é comparação relativa (melhor/pior do
grupo), não faixa de desempenho:

- **Top 3:** `#6227EA` (roxo Mereo).
- **Bottom 3:** `#06B6D4` (ciano).

Validado com `validate_palette.js` (skill `dataviz`), modo light,
superfície `#fcfcfb`: todos os checks duros passam — separação CVD 25,0
(deutan) / 26,7 (tritan), visão normal 33,1. Um WARN de contraste em
`#06B6D4` (2,36:1) — por isso o rótulo de valor na barra é obrigatório,
não só a cor (já coberto, o visual mostra o valor por cima da barra).

---

## Top 5 Colaboradores

**Plano original:** Tabela com coluna `RANKX` calculada (Power BI Table
não numera linha nativamente). **Visual final:** `barChart` horizontal —
mesma decisão de UX da Zona Crítica, mas aqui o **Top N nativo funcionou**
(diferença real: `vw_score_colaborador[score]` é uma linha por pessoa, sem
a ambiguidade de agregação que travou o Top N dos gestores).

- Categoria: `dim_colaborador[nome]`.
- Valor: soma de `vw_score_colaborador[score]`.
- Filtros do visual: `dim_colaborador[flag_elegivel_r10] = 1` **e** Top N
  = 5 por `score` (maior) — filtro nativo, sem workaround.

**Correção de paleta (auditoria `/auditoria-dashboard-mereo`):** a cor por
barra aqui é categórica (identifica a Gerência do colaborador — Controladoria,
Logística, Qualidade), não faixa de score. Antes usava laranja pra uma das
áreas, o mesmo tom que a legenda de "Distribuição de Score" usa pra faixa
80-100 — mesma cor, dois significados diferentes em dois gráficos da mesma
página. Trocado por uma paleta categórica sem vermelho/laranja/verde
(reservados pro semáforo de score):

- Controladoria: `#2A78D6` (azul).
- Logística: `#64748B` (cinza-azulado — trocado de `#1BAF7A` na
  quarta rodada de auditoria: mesmo sendo visualmente distinto do
  verde-semáforo `#1F9254`, ainda era um tom de verde reaproveitado
  como categoria, a última cor do semáforo ainda em uso fora dele).
- Qualidade: `#E87BA4` (magenta).
- 4ª área, se precisar: `#EDA100` (amarelo).

Validado com `validate_palette.js`, modo light: todos os checks duros
passam. Um WARN de contraste (`#E87BA4` abaixo de 3:1) — mesma regra
do Bottom 3: rótulo de valor visível na barra, não só a legenda de
cor.

---

## Resumo de visuais (final, confirmado no `.pbip`)

| Elemento | Visual planejado | Visual final | Motivo da divergência |
|---|---|---|---|
| 4 KPIs do topo | Multi-row Card | `Card` (× 7, valor + rodapé separados) | Card novo não tem subtítulo livre |
| Barra de distribuição | 100% Empilhada | igual ao plano | — |
| Score por Área | Matriz | igual ao plano, DAX diferente (`ISINSCOPE`) | Bug de "pai com filho único" |
| Zona Crítica | Tabela | `clusteredBarChart` | UX — tabela nativa parecia pouco profissional |
| Gestores Top/Bottom | Tabela + Top N | `clusteredBarChart` + filtro básico manual | Top N nativo nunca funcionou de forma confiável |
| Top 5 Colaboradores | Tabela + `RANKX` | `barChart` + Top N (funcionou) | UX, e aqui o Top N nativo não teve o mesmo bug |
| Cor do Bottom 3 (Gestores) | vermelho (semáforo) | `#06B6D4` ciano | Auditoria: vermelho colidia com "crítico" da legenda de score, mas 2 dos 3 gestores não são críticos |
| Cor por área (Top 5) | laranja (uma das áreas) | paleta categórica própria (`#2A78D6`/`#64748B`/`#E87BA4`) | Auditoria: laranja já significa "faixa 80-100" na legenda de score; depois trocou o verde-água por cinza-azulado (achado da 4ª rodada: verde ainda reaproveitado do semáforo) |
