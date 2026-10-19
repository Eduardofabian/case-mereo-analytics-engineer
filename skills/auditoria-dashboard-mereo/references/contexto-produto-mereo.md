# Contexto de produto — como a Mereo já resolve isso

O avaliador deste painel muito provavelmente é alguém que vê o produto
real da Mereo todo dia. O módulo Metas (confirmado por vocabulário
idêntico ao do case — ver `MEREO CASE/md/pesquisa-mereo.md`) já tem três
telas reais que são o ponto de comparação implícito do painel entregue.
Usar isso para calibrar o que é "lacuna visual" vs. "escolha de design
razoável".

## Painel de performance (real, screenshot confirmado)

Tabela hierárquica por pessoa (CEO no topo → Diretores abaixo):
- Colunas "Pontual" e "Acumulado", cada uma com dois números empilhados:
  `P: <previsto>` e `R: <realizado>`.
- Célula de cada meta **colorida por faixa de atingimento** — verde
  (≥~100%), amarelo (~80-99%), vermelho (<~80%). Compatível direto com
  R6 do case (<80%→0, 80-120%→nota, >120%→cap 120).
- Coluna "Nota" com badge colorido à direita de cada linha.
- Linha expansível por pessoa.

## Árvore de performance (real, screenshot confirmado)

Visualização em árvore/cards conectados por linhas, nível por nível de
hierarquia — cor do card = tier de score (vermelho/amarelo/verde). É
literalmente R11 (Direto/Consolidado) desenhado como árvore.

## Dashboard Analytics (real, screenshot confirmado)

Esse é um painel de **qualidade/completude de dado**, não de resultado
de performance: tabela por colaborador (metas, peso distribuído,
situação, status) + 4 donut charts de completude ("% com valor
previsto", "% com ação cadastrada" etc.). Não é o que o painel final
precisa replicar, mas é relevante pra avaliar se a narrativa de
qualidade de dados do case (R2, R3, R8) está documentada com o mesmo
nível de granularidade que o produto real já oferece.

## O que isso implica para a auditoria

Dois elementos, se ausentes no painel entregue, vão parecer lacuna de
design e não escolha deliberada, porque são o padrão visual que o
avaliador usa todo dia:

1. **Semáforo por faixa de atingimento** (verde/amarelo/vermelho) nas
   células de nota — não precisa ser elaborado, mas precisa existir.
   Ausência total → reporte como gap de prioridade média-alta mesmo que
   os números estejam corretos, porque é convenção visual do próprio
   produto, não gosto pessoal de BI.
2. **Alguma representação hierárquica do resultado** conectando com R11
   (Direto vs. Consolidado) — não precisa ser árvore gráfica, uma tabela
   indentada por nível hierárquico já resolve. Ausência total → mesmo
   tratamento do item 1.

Se ambos estiverem presentes e bem aplicados, isso é um diferencial
concreto a destacar no veredito — mostra que quem fez o case pesquisou o
produto, não só o enunciado isolado.
