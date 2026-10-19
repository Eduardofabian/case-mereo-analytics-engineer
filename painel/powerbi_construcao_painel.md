# Construção do Painel no Power BI — Resultado do Ciclo 2025 (Grupo Aurora)

Guia de construção card a card: visual, campos, medidas DAX e formatação. Assume o modelo com as tabelas `dim_area`, `dim_colaborador`, `dim_meta`, `fact_meta_valor_mensal` e as views `vw_score_colaborador`, `vw_score_area`, `vw_score_gestor`, relacionadas conforme já fechado na conversa anterior.

## Atenção antes de tudo: `vw_score_colaborador` não vem pré-filtrada

Conferi linha a linha: `vw_score_colaborador` tem **81 linhas** (um score pra cada colaborador, incluindo os 9 inelegíveis pela R10), não 72. Isso significa que **qualquer medida que agregue direto essa view sem filtrar por elegibilidade dá um número errado**, silenciosamente — testei:

- Média dos 81 (sem filtro): **94.32**
- Média dos 72 elegíveis (com filtro): **95.74** ✅ (o número validado)

Toda medida abaixo que usa `vw_score_colaborador` já vem com o filtro de elegibilidade embutido. Não omita isso ao adaptar — é o erro mais fácil de cometer aqui.

`vw_score_area` e `vw_score_gestor` **já vêm prontas e filtradas** (são o resultado final das regras R9-R11 aplicadas lá na origem) — pra essas duas, agregação direta funciona sem filtro adicional.

---

## Medidas DAX base (criar primeiro, uma vez só)

```dax
Score Médio Ciclo =
CALCULATE(
    AVERAGE ( vw_score_colaborador[score] ),
    dim_colaborador[flag_elegivel_r10] = 1
)
```

```dax
Score Mediano Ciclo =
CALCULATE(
    MEDIAN ( vw_score_colaborador[score] ),
    dim_colaborador[flag_elegivel_r10] = 1
)
```

```dax
Elegiveis =
CALCULATE(
    COUNTROWS ( dim_colaborador ),
    dim_colaborador[flag_elegivel_r10] = 1
)
```

```dax
Total Colaboradores = COUNTROWS ( dim_colaborador )
```

```dax
Zona Critica Qtd =
CALCULATE(
    COUNTROWS ( vw_score_colaborador ),
    dim_colaborador[flag_elegivel_r10] = 1,
    vw_score_colaborador[score] < 80
)
```

```dax
Zona Critica Pct =
DIVIDE ( [Zona Critica Qtd], [Elegiveis] )
```

```dax
Intermediario Qtd =
CALCULATE(
    COUNTROWS ( vw_score_colaborador ),
    dim_colaborador[flag_elegivel_r10] = 1,
    vw_score_colaborador[score] >= 80,
    vw_score_colaborador[score] < 100
)
```

```dax
Intermediario Pct = DIVIDE ( [Intermediario Qtd], [Elegiveis] )
```

```dax
Acima Meta Qtd =
CALCULATE(
    COUNTROWS ( vw_score_colaborador ),
    dim_colaborador[flag_elegivel_r10] = 1,
    vw_score_colaborador[score] >= 100
)
```

```dax
Acima Meta Pct = DIVIDE ( [Acima Meta Qtd], [Elegiveis] )
```

```dax
Abaixo Meta Qtd = [Zona Critica Qtd] + [Intermediario Qtd]
```

```dax
Abaixo Meta Pct = DIVIDE ( [Abaixo Meta Qtd], [Elegiveis] )
```

Checagem rápida depois de criar: `[Score Médio Ciclo]` = 95.74 · `[Elegiveis]` = 72 · `[Zona Critica Qtd]` = 9 · `[Intermediario Qtd]` = 26 · `[Acima Meta Qtd]` = 37 · `[Abaixo Meta Pct]` = 48.6%. Se bater diferente, o filtro de elegibilidade não está entrando — confira o relacionamento `dim_colaborador ↔ vw_score_colaborador`.

---

## KPI 1 — Score Médio do Ciclo

**Visual:** Cartão (Card) — não Multi-row Card, porque é um valor só com um subtítulo, e Card deixa o número grande dominar.

**Campos:**
- Valor principal: medida `[Score Médio Ciclo]`
- Formato: número com 2 casas decimais (configurar na própria medida: `FORMAT([Score Médio Ciclo], "0.00")` se quiser forçar string, ou formatação do card em Opções de Formato → Dados → Casas decimais = 2)

**Subtítulo (abaixo do número):** o Card nativo do Power BI não tem campo de "subtítulo" livre — pra reproduzir "Mediana 100.36" embaixo do valor, duas opções:
1. Usar um **Cartão Multilinha (Multi-row Card)** com dois campos: `[Score Médio Ciclo]` e `[Score Mediano Ciclo]`, cada um com seu rótulo.
2. Ou criar uma medida de texto combinando os dois e usar um visual de Texto (Card com `displayed as text`), se quiser o controle visual exato do HTML.

Recomendo a opção 1 (Multi-row Card) — é nativa, sem gambiarra, e já aceita formatação condicional por medida.

**Cor de destaque (borda roxa):** Power BI Card/Multi-row Card não tem "borda superior colorida" nativa até versões recentes — se seu Power BI Desktop for atualizado, use o formato "Borda" do card (Formato → Efeitos → Borda → cor `#6227EA`, espessura maior só no topo não é configurável separadamente; a alternativa visual é colocar um retângulo fino roxo atrás/acima do card, ou aceitar borda única na cor de marca).

---

## KPI 2 — Elegíveis

**Visual:** Multi-row Card (pra manter consistência com o KPI 1 e permitir o subtítulo "de 81 colaboradores").

**Campos:**
- `[Elegiveis]` → valor principal (72)
- Subtítulo via segunda linha de texto: medida auxiliar
  ```dax
  Elegiveis Subtitulo = "de " & [Total Colaboradores] & " colaboradores"
  ```
- Cor de destaque: neutra (cinza `#9CA3AF`), sem semântica de bom/ruim.

---

## KPI 3 — Zona Crítica (<80)

**Visual:** Multi-row Card.

**Campos:**
- `[Zona Critica Qtd]` (9)
- `[Zona Critica Pct]` formatado como percentual com 1 casa decimal (12.5%)
- Subtítulo: "ação individual imediata" — texto fixo, pode ir como título do card ou em uma caixa de texto sobreposta (Power BI não tem campo de subtítulo fixo arbitrário em cartão nativo; se precisar do texto fixo exato, use uma **Caixa de Texto** posicionada logo abaixo do card).
- Cor de destaque: vermelho `#E5484D` — aplicar via formatação condicional na medida, ou fixo no card já que esse KPI é sempre "alerta".

---

## KPI 4 — Abaixo da Meta (100)

**Visual:** Multi-row Card.

**Campos:**
- `[Abaixo Meta Pct]` formatado como percentual (48.6%)
- Subtítulo via medida de texto:
  ```dax
  Abaixo Meta Subtitulo =
  [Zona Critica Qtd] & " críticos + " & [Intermediario Qtd] & " intermediários"
  ```
- "quase metade" como rótulo textual fixo (caixa de texto, ou pill de formatação condicional se o visual suportar).
- Cor de destaque: laranja `#FF5C39`.

---

## Barra de Distribuição de Score

**Visual:** Gráfico de Barras 100% Empilhadas (**Stacked Bar Chart 100%**), orientação horizontal, uma única categoria.

**Campos:**
- Eixo Y (categoria): uma coluna com valor fixo único (ex.: criar uma tabela calculada de 1 linha, ou usar qualquer coluna textual constante) — o gráfico vai ter uma barra só, cheia.
- Legenda / Valores: três medidas, uma por faixa:
  ```dax
  Pct Critico Label = [Zona Critica Pct]
  Pct Intermediario Label = [Intermediario Pct]
  Pct Acima Label = [Acima Meta Pct]
  ```
  Coloque as três no campo "Valores" do visual — o Power BI empilha automaticamente e, como é 100%-empilhado, normaliza a proporção.
- Cores por série: vermelho `#E5484D` (Crítico), laranja `#FF5C39` (80–100), verde `#1F9254` (≥100) — definir em Formato → Cores dos Dados, uma por série.
- Rótulos de dados: ativar, formato percentual 1 casa.
- Legenda: posicionar embaixo ou à direita, com os textos "Crítico <80 (9)" etc. — como o Power BI não escreve o "(9)" sozinho na legenda (só mostra o nome da série), se quiser esse detalhe exato, renomeie a própria série/medida para já incluir o "(9)" no nome, ou aceite que a contagem fica só nos rótulos de dados dos KPIs acima.

---

## Card do Grid 1 — Score por Área (Direto vs. Consolidado)

Esse é o mais trabalhoso dos quatro porque resolve a ambiguidade que você apontou (folha vs. não-folha).

**Visual:** Matriz (Matrix) — única opção nativa que faz drill hierárquico com indentação automática.

**Campos:**
- **Linhas:** hierarquia de `dim_area`: arraste `dim_area[nome]` como primeiro nível. Pra hierarquia multi-nível de verdade (Diretoria → Gerência → Coordenação) baseada em `id_area_pai`, você tem duas opções:
  1. **Caminho rápido:** já que são só 3 níveis fixos e 11 linhas, crie 3 colunas calculadas em `dim_area` (`Nível 0`, `Nível 1`, `Nível 2`) via `PATH()`/`PATHITEM()` sobre `id_area_pai`, e arraste as 3 como hierarquia de linhas na matriz.
  2. **Caminho simples (recomendado pro seu caso, com só 11 áreas):** não vale o esforço do `PATH()` pra 3 níveis fixos — monte a hierarquia manualmente como 3 colunas calculadas simples (Diretoria, Gerência, Coordenação) com `LOOKUPVALUE` subindo o `id_area_pai` duas vezes. Mais rápido de construir e debugar com 11 linhas.
- **Colunas/Valores:**
  ```dax
  Score Direto = SUM ( vw_score_area[score_direto] )
  Score Consolidado = SUM ( vw_score_area[score_consolidado] )
  ```
- **Resolvendo a ambiguidade folha vs. não-folha:** crie uma medida que só mostra "Consolidado" quando ele for diferente de "Direto" (ou seja, quando a área tiver subordinadas):
  ```dax
  Score Consolidado Exibir =
  VAR Direto = [Score Direto]
  VAR Consolidado = [Score Consolidado]
  RETURN
  IF (
      ROUND ( Direto, 2 ) = ROUND ( Consolidado, 2 ),
      BLANK(),          -- é folha: não repete o valor na coluna Consolidado
      Consolidado
  )
  ```
  Use `[Score Direto]` na coluna "Direto" (sempre preenchida) e `[Score Consolidado Exibir]` na coluna "Consolidado" (só preenchida nas 5 áreas não-folha). Pra quando for folha, considere ocultar visualmente a coluna repetida ou aceitar o branco — visualmente já resolve a ambiguidade sem precisar de lógica condicional de layout (que a Matrix nativa não permite fazer "célula mesclada" como no HTML).
- **Formatação condicional:** nas duas colunas de valor, Formato → Formatação Condicional → Escalas de Cor ou Regras, usando os mesmos cortes de faixa (vermelho <80, laranja 80–100, verde ≥100).

---

## Card do Grid 2 — Zona Crítica

**Visual:** Tabela (Table) simples — não Matrix, porque não tem hierarquia aqui, é lista plana.

**Campos:**
- `dim_colaborador[nome]`
- `vw_score_colaborador[score]`

**Filtro do visual:**
- Painel de Filtros → `vw_score_colaborador[score]` → "é menor que" → 80
- Painel de Filtros → `dim_colaborador[flag_elegivel_r10]` → "é" → 1

**Ordenação:** clique no cabeçalho da coluna Score → ordem crescente (do menor pro maior, como você pediu).

**Formatação condicional:** coluna Score → Formatação Condicional → Cor de fundo ou fonte fixa vermelha (`#E5484D`), já que aqui 100% das linhas são críticas por definição do filtro.

---

## Card do Grid 3 — Gestores (Top 3 / Bottom 3)

**Visual:** dois visuais de **Tabela** lado a lado (um "Top 3", outro "Bottom 3") dentro do mesmo card/área do canvas — ou um único visual de Tabela com um slicer acima alternando entre os dois. Recomendo os dois visuais lado a lado fixos (mais parecido com o que você aprovou no mockup, e não depende de interação do usuário).

**Campos (ambas as tabelas):**
- `dim_colaborador[nome]` (nome do gestor — vem do relacionamento `vw_score_gestor[id_gestor] → dim_colaborador[id_colaborador]`, já fechado antes)
- `vw_score_gestor[score_medio_time]`
- `vw_score_gestor[n_subordinados_diretos_elegiveis]`

**Filtro "Top 3":**
- Painel de Filtros → no campo `score_medio_time` → Tipo de filtro "Top N" → 3 → Por valor: `score_medio_time` (critério: maior).

**Filtro "Bottom 3":**
- Mesmo campo, Top N → 3 → critério: **menor**. (O Power BI usa "Top N" pros dois casos — pra pegar os menores, basta inverter a direção dentro da configuração do próprio filtro Top N, não precisa duplicar medida.)

**Ordenação dentro de cada tabela:** Bottom 3 ordenado crescente por `score_medio_time` (pior primeiro — Olívia Queiroz 83.57 → Rafael Jardim 91.41 → Sofia Oliveira 93.30, como já validado). Top 3 ordenado decrescente.

**Formatação condicional:** Top 3 com fundo/fonte verde, Bottom 3 com vermelho/laranja conforme faixa (igual ao HTML: Olívia e Rafael em vermelho por estarem abaixo de 100 "mais fundo", Sofia Oliveira em laranja por estar entre 80-100... na prática os 3 do Bottom já ficaram todos abaixo de 100, então pode usar vermelho pros dois primeiros e laranja só no 93.30 se quiser manter a distinção fina que o HTML tinha).

---

## Card do Grid 4 — Top 5 Colaboradores

**Visual:** Tabela (Table).

**Campos:**
- `dim_colaborador[nome]`
- `dim_area[nome]` (nome da área do colaborador — vem do relacionamento `dim_colaborador[id_area] → dim_area[id_area]`, já fechado antes)
- `vw_score_colaborador[score]`

**Filtros do visual:**
- `dim_colaborador[flag_elegivel_r10]` → "é" → 1 (obrigatório — sem isso o Top N pode trazer alguém inelegível com score alto mas fora de regra)
- `vw_score_colaborador[score]` → Tipo de filtro "Top N" → 5 → por valor `score` (maior)

**Ordenação:** decrescente por score (117.72 no topo).

**Numeração (1-5 visual, como o badge roxo do mockup):** o Power BI Table não numera linhas nativamente. Se quiser o número exato como no HTML, crie uma coluna calculada com `RANKX`:
```dax
Rank Top5 =
RANKX (
    FILTER ( vw_score_colaborador, RELATED ( dim_colaborador[flag_elegivel_r10] ) = 1 ),
    vw_score_colaborador[score]
)
```
E arraste essa coluna como primeira da tabela.

**Formatação condicional:** coluna Score em verde (`#1F9254`), já que por definição são os melhores.

---

## Resumo de visuais (tabela de referência rápida)

| Elemento | Visual Power BI |
|---|---|
| 4 KPIs do topo | Multi-row Card (um por KPI) |
| Barra de distribuição | Gráfico de Barras 100% Empilhadas (horizontal) |
| Score por Área | Matriz (Matrix) com hierarquia e medida condicional Direto/Consolidado |
| Zona Crítica | Tabela (Table) com filtro `score < 80` |
| Gestores Top/Bottom | 2× Tabela (Table) com filtro Top N (3 maior / 3 menor) |
| Top 5 Colaboradores | Tabela (Table) com filtro Top N (5 maior) + coluna RANKX |

## Paleta de cores (igual ao HTML, pra manter consistência visual)

| Uso | Cor |
|---|---|
| Primária / destaque roxo | `#6227EA` |
| Destaque laranja | `#FF5C39` |
| Crítico / vermelho | `#E5484D` |
| Intermediário / laranja (mesma do destaque) | `#FF5C39` |
| Bom / verde | `#1F9254` |
| Fundo escuro (topbar) | `#212529` |
| Texto secundário | `#6B7280` |
