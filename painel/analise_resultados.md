# Análise dos resultados — Ciclo 2025 (Grupo Aurora)

## Proveniência dos números

Reconciliado contra o pipeline oficial: `dim_colaborador`, `dim_area`,
`vw_score_colaborador`, `vw_score_area`, `vw_score_gestor` (export do Chat
1, SQL Server/marts). Minha reconstrução independente em Python — feita
antes desses arquivos chegarem — bateu com o oficial em todos os pontos
checados (72 elegíveis, mesmos 5 piores scores, mesma distribuição, os 9
gestores de P3, diferença de 0.01 ponto em um gestor por arredondamento). Os
números abaixo usam o pipeline oficial como fonte; os CSVs finais
(`p1_score_colaborador.csv`, `p2_score_area.csv`, `p3_gestores.csv`) estão
no formato exato pedido no enunciado e derivados diretamente dessas views,
sem recálculo paralelo.

## 1. Leitura geral

- 81 colaboradores no total, **72 elegíveis** (R10) → **9 ficam de fora**
  só por elegibilidade, não por falta de meta ou lançamento. Isso precisa
  aparecer no painel de forma explícita (um rótulo "72 de 81 — 9
  inelegíveis por admissão/desligamento"), senão alguém vai interpretar
  como dado faltando.
- Score médio: **95.7**, mediana **100.4** — a mediana ficar acima da
  média indica cauda à esquerda: a maioria está em torno de 100, mas um
  grupo pequeno com score muito baixo puxa a média pra baixo.
- **9 colaboradores (12,5% dos elegíveis) abaixo de 80**, zona onde R6 zera
  a nota de qualquer meta individual que caia ali. Nenhum colaborador
  bateu o teto de 120 (máximo observado: 117.72) — o corte de baixo pesa
  mais na distribuição real do que o cap de cima.
- 316 metas no ciclo 2025, **5 sem nota** (R8: 4 sem nenhum lançamento, 1
  com previsto=0 o ano inteiro) — não entram no score de ninguém, como já
  documentado na Parte 1.

## 2. Quem se destaca (pra cima e pra baixo)

**Piores scores:**

| Colaborador | Área | Gestor | Score |
|---|---|---|---|
| Paula Cardoso | Gerência de Marketing (5) | Olívia Queiroz | 18.17 |
| Nicolas Vasconcelos | Gerência de Marketing (5) | Olívia Queiroz | 31.66 |
| Quésia Nogueira | Gerência de Controladoria (11) | Sofia Queiroz | 51.42 |
| Carla Rezende | Coordenação Vendas Sul (3) | Ana Holanda | 54.29 |
| Sabrina Cardoso | Coordenação de Transporte (8) | Sofia Oliveira | 54.85 |

Só **2 dos 5** piores scores são da Gerência de Marketing, não 3 — as
outras três vêm de áreas e gestores diferentes entre si (Controladoria,
Coord. Vendas Sul, Coord. Transporte). Não dá pra falar em "padrão de
área" nesse recorte: o que existe de fato é uma área (Marketing) com 2
casos extremos e um gestor específico (Olívia Queiroz) com o pior score
médio de time em P3 (83.56).

E mesmo esse ponto sobre a Olívia pede uma ressalva, não uma conclusão
fechada: Paula Cardoso (18.17, o pior score individual da base) foi
desligada em 13/11/2025, com lançamentos mantidos literais mesmo após o
desligamento — decisão já documentada na Parte 1, não um erro novo. O
time da Olívia tem 9 subordinados elegíveis, 3 deles desligados no
segundo semestre de 2025; removendo só a Paula desse cálculo, a média do
time sobe de 83.56 para **91.74** — o suficiente pra deixar de ser o pior
time (o segundo pior, Rafael Jardim, fica em 91.41). Ou seja: quase metade
do "pior gestor da empresa" é efeito de uma única saída recente, não de
desempenho do time como um todo. Isso não muda o cálculo de P3 — a Paula
é elegível por R10 e entra certo no score — mas muda o que se pode
afirmar a partir dele: é um sinal pra investigar, não uma conclusão pronta
pra plano de ação.

**Melhores scores**, por contraste, estão espalhados — Comercial, Operações
e Financeira aparecem igualmente no top 10, sem concentração em uma única
área ou gestor.

## 3. Padrão por hierarquia (R11 — Direto vs Consolidado)

| Diretoria | Direto | Consolidado | Nº elegíveis (consolidado) |
|---|---|---|---|
| Diretoria Financeira | 104.33 | **103.30** | 12 |
| Diretoria Comercial | 101.75 | 95.08 | 33 |
| Diretoria de Operações | 90.08 | 93.19 | 27 |

**Diretoria Financeira tem o melhor resultado consolidado** (103.30) — e é
a única das três onde direto e consolidado ficam próximos, porque a
estrutura abaixo dela é mais rasa. Comercial é o caso mais chamativo:
score direto de quem está lotado direto na diretoria (101.75, bom) cai pra
95.08 quando se agrega toda a estrutura abaixo — ou seja, os diretores
performam bem, mas o resultado se dilui pela base (puxado em parte pela
Gerência de Marketing, citada acima). Operações é o oposto: direto baixo
(90.08, só 2 pessoas) mas consolidado sobe pra 93.19 — a camada de baixo
performa melhor que o topo direto, que aqui é uma base pequena (n=2) então
qualquer leitura precisa vir com essa ressalva de tamanho de amostra.

Confirmação estrutural: as 6 áreas-folha (sem área abaixo) têm
`score_direto == score_consolidado` por definição — isso é checagem de
sanidade, não achado, mas vale validar no painel (se divergir ali, é bug
de hierarquia).

## 4. O que vai pro painel (proposta de 4–6 métricas)

Critério de corte: o que muda a decisão de alguém da diretoria, não o que
é só "mais um número correto".

1. **Score médio geral + nota de cobertura (72/81 elegíveis)** — contexto
   obrigatório, sem isso qualquer outro número é mal interpretado.
2. **Distribuição por faixa (<80 / 80–100 / 100–120 / ≥120)**, com
   semáforo vermelho/amarelo/verde — replica o padrão visual real do
   produto Mereo (ver seção 4 de `pesquisa-mereo.md`) e responde "foi bem
   no geral ou só alguns puxaram a média".
3. **Score por diretoria, Direto vs Consolidado** — é literalmente a R11 e
   a feature "Árvore de Performance" do produto; sem isso o painel não
   parece Mereo.
4. **Top 5 / Bottom 5 colaboradores** — pergunta mais óbvia de qualquer
   diretoria, com o aviso de elegibilidade ao lado.
5. **Top 3 / Bottom 3 gestores (P3)** — já vem pronto do enunciado, é
   direto para RH decidir ação.
6. (Se sobrar espaço) **Destaque do time da Olívia Queiroz (Gerência de
   Marketing)** — não como "vilã confirmada", mas como ponto de atenção
   que precisa de uma nota de contexto, não de um rótulo definitivo: é o
   pior score médio de time em P3 (83.56), mas quase metade disso é efeito
   de uma única desligada recente (ver §2) — sem ela, a média do time sobe
   a 91.74 e deixa de ser a pior. Se for pro painel, mostre as duas versões
   lado a lado (com e sem a colaboradora desligada) em vez de só o número
   bruto — é o tipo de contexto que evita a diretoria tomar uma decisão de
   RH em cima de um efeito estatístico pontual.

O que eu **não** colocaria: metas individuais detalhadas (isso é trabalho
do Agente de IA, Parte 4, não do painel de diretoria) e nenhum número que
dependa de "soma de peso = 100" (7 colaboradores quebram essa suposição —
qualquer gráfico auxiliar tipo "% do peso batido" precisa normalizar por
peso real, não por 100 fixo).
