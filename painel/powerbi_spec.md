# Spec do painel Power BI — Ciclo 2025 (Grupo Aurora)

## Limitação real, declarada antes de qualquer coisa

Power BI Desktop é um app Windows local — este sandbox não tem acesso a
ele, e a sessão não está com nenhuma pasta do seu computador conectada
agora (nem com acesso de tela via computer-use habilitado). Então eu não
construo o `.pbix` por você aqui. Duas opções:

1. **Você monta pelo spec abaixo** (mais rápido, sem risco de eu clicar
   errado num app que não vejo direito) — é literalmente copiar as medidas
   DAX e montar os visuais na ordem descrita.
2. Se quiser que eu opere o Power BI Desktop diretamente na sua tela, você
   conecta a pasta do projeto (ou habilita computer-use) e eu sigo via
   automação de tela — mas aviso: isso é mais lento e mais sujeito a erro
   de clique do que você mesmo montar pelo spec, numa ferramenta de UI
   densa como o Power BI. Com prazo até 20/10 08h, recomendo a opção 1.

## Fonte de dados

Aponte o Power BI para `respostas/p1_score_colaborador.csv`,
`p2_score_area.csv`, `p3_gestores.csv` — já reconciliados com o pipeline
oficial (`dim_colaborador`, `dim_area`, `vw_score_colaborador/area/gestor`
do Chat 1). Te mandei esses três no formato exato do enunciado; se os seus
`respostas/` locais já existem com esses nomes, confirme que os valores
batem (deveriam, é a mesma fonte) e use os seus. Traga
também `colaborador.csv` e `area.csv` para nome/hierarquia.

## Modelo de dados (estrela simples)

- `dim_colaborador` (colaborador.csv) — chave `id_colaborador`
- `dim_area` (area.csv) + coluna calculada de nível hierárquico
- `fact_score_colaborador` = p1_score_colaborador.csv, relacionado a
  `dim_colaborador` por `id_colaborador`
- `fact_score_area` = p2_score_area.csv, relacionado a `dim_area` por
  `id_area`
- `fact_score_gestor` = p3_gestores.csv (já vem agregado/filtrado, pode
  ficar solto ou relacionado a `dim_colaborador` via `id_gestor`)

## Medidas DAX

```dax
Score Médio = AVERAGE(fact_score_colaborador[score])

Score Mediano = MEDIAN(fact_score_colaborador[score])

Colaboradores Elegíveis = COUNTROWS(fact_score_colaborador)

Abaixo de 80 =
CALCULATE(
    COUNTROWS(fact_score_colaborador),
    fact_score_colaborador[score] < 80
)

Faixa de Score =
VAR s = fact_score_colaborador[score]
RETURN
SWITCH(
    TRUE(),
    s < 80, "Crítico (<80)",
    s < 100, "Abaixo da meta (80–100)",
    s < 120, "Dentro/acima da meta (100–120)",
    "Teto (≥120)"
)

Cor Semáforo =
VAR s = SELECTEDVALUE(fact_score_colaborador[score])
RETURN
SWITCH(
    TRUE(),
    s < 80, "#D64545",
    s < 100, "#E8B339",
    "#3FA66B"
)
```

Para P2, não precisa de medida calculada — `score_direto` e
`score_consolidado` já vêm prontos do CSV; só formate como número com 2
casas.

## Layout — página única, 4-6 visuais

```
┌─────────────────────────────────────────────────────────┐
│  Cards topo: Score médio | Mediana | 72/81 elegíveis     │
│              (nota pequena: "9 fora por elegibilidade")  │
├───────────────────────────┬───────────────────────────────┤
│ Gráfico de barras:        │ Tabela hierárquica:           │
│ Distribuição por faixa    │ Diretoria → Gerência →        │
│ (semáforo vermelho/       │ Coordenação, colunas          │
│ amarelo/verde)            │ Score Direto | Consolidado    │
├───────────────────────────┴───────────────────────────────┤
│ Top 5 / Bottom 5 colaboradores (duas tabelas lado a lado)  │
├─────────────────────────────────────────────────────────┤
│ Top 3 / Bottom 3 gestores (P3) — tabela única, coluna      │
│ "grupo" como categoria                                     │
└─────────────────────────────────────────────────────────┘
```

Isso cobre as 6 métricas descritas em `analise_resultados.md` §4. Se
precisar cortar uma pra caber na página, corte a última (destaque do
time da Olívia Queiroz) — as outras 5 são as que de fato respondem "quem
foi bem, quem foi mal, e por quê" pra diretoria. Se for incluir essa
última, mostre o score médio do time com e sem a colaboradora desligada
em 13/11 (83.56 vs 91.74) — o número isolado, sem essa nota, sugere um
problema de gestão maior do que o que os dados sustentam.

## Fundo customizado (Figma) — nota de prioridade

Só faça isso depois do painel funcionar com fundo neutro. Ordem certa:
1. Monta os 5-6 visuais com fundo cinza claro padrão do Power BI.
2. Confirma que os números batem com `respostas/*.csv`.
3. **Só então**, se sobrar tempo, exporta um PNG do Figma do tamanho exato
   do canvas (1280×720 ou o que você estiver usando) e aplica como imagem
   de fundo da página (Formatar página → Imagem). Isso é acabamento, pesa
   zero nos 15% do critério de avaliação ("clareza e escolha do que
   mostrar" — não "beleza do fundo").

## Export

`Arquivo → Exportar → PDF` para `painel/painel_grupo_aurora.pdf`, e salve o
`.pbix` em `painel/` junto. O parágrafo de 1 parágrafo (o que é realmente
avaliado, 15% do peso) deve explicar a escolha do §4 do
`analise_resultados.md` — já está redigido lá, adapte pro README.
