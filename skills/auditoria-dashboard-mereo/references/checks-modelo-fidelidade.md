# Fidelidade ao modelo de dados e aos números de origem

## O modelo de dados esperado

- `dim_area`, `dim_colaborador`, `dim_meta` (dimensões)
- `fact_meta_valor_mensal` (fato, grão = lançamento mensal por meta)
- `vw_score_colaborador`, `vw_score_area`, `vw_score_gestor` (camadas de
  score já calculadas — o painel deve **consumir essas views prontas**,
  não recalcular R1-R11 em DAX)

Se o `.pbip` (ou equivalente) recalcula nota, atingimento ou elegibilidade
em medida DAX em vez de ler o valor já resolvido de `vw_score_*`, isso é
risco real de inconsistência com os CSVs de `respostas/` — duas
implementações da mesma regra (uma em SQL/pandas, outra em DAX) podem
divergir silenciosamente sem que ninguém perceba até um número bater
errado em produção. **Reporte como achado de alta prioridade se
encontrar**, independente de o número bater hoje — o risco é estrutural,
não pontual.

## Fidelidade ao dado de origem

- Os totais/scores exibidos no painel batem com
  `respostas/p1_score_colaborador.csv`, `p2_score_area.csv`,
  `p3_gestores.csv`? Pegue 3 valores aleatórios do painel (um
  colaborador, uma área, um gestor) e confira contra o CSV
  correspondente.
- O painel distingue score direto vs. consolidado (R11) quando a área
  tem subárea? Mostrar só um dos dois sem indicar qual é ambíguo e é
  erro de clareza, não só de dado — a vaga descreve explicitamente
  "explicar resultados para pessoas não técnicas", e um número sem
  rótulo falha exatamente nisso.
- Elegibilidade (R10) está refletida — o painel exclui colaboradores não
  elegíveis do cálculo, ou mistura todos silenciosamente?

## Qualidade técnica do modelo (quando for `.pbip`/Power BI)

- Relacionamentos entre as tabelas são 1-para-muitos na direção esperada
  (dimensão → fato), sem relação bidirecional desnecessária que possa
  causar ambiguidade de filtro.
- Medidas usam `CALCULATE`/filtros de contexto corretos para granularidade
  de área vs. consolidado — confirme que não há duplicação de linha ao
  cruzar `fact_meta_valor_mensal` com `dim_area` via `dim_colaborador`
  (join incorreto nessa cadeia é a causa mais comum de número inflado em
  um painel de RH/performance).
- `ISINSCOPE` ou equivalente usado corretamente para alternar entre
  granularidades (célula de área vs. célula de colaborador na mesma
  visual) — se o README já documenta um "caso de borda ISINSCOPE"
  resolvido, confirme que a correção está de fato refletida no arquivo
  entregue, não só descrita em texto.
