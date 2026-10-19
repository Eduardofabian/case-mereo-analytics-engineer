# Clareza e escolha do que mostrar (o critério literal do enunciado)

O painel é para a **diretoria**, não para o time de dados — isso muda
o que deveria estar nele:

- Visão agregada (áreas, consolidado) deveria dominar o espaço; detalhe
  por colaborador individual deveria ser secundário ou nem aparecer, a
  não ser que haja uma seção clara de "destaques" (top/bottom
  performers, por exemplo).
- É uma página só, como o enunciado pede. Mais de uma página/aba é
  desvio do formato pedido — reporte como gap mesmo que o conteúdo de
  cada página seja bom.
- Existe uma explicação curta (no README ou no próprio painel) de por
  que aqueles elementos foram escolhidos e outros não. Painel bonito sem
  essa justificativa não atende ao critério "clareza e escolha do que
  mostrar" por completo — metade do critério é a escolha ser explicada,
  não só executada.
- Ver `references/contexto-produto-mereo.md`: semáforo de nota e
  hierarquia visual (Direto/Consolidado) são o padrão que o avaliador
  reconhece do próprio produto — presença ou ausência pesa na nota deste
  critério especificamente, não é observação genérica de BI.

## Caminhos e portabilidade

- Se o modelo lê CSV por caminho absoluto (`File.Contents("C:\...")`),
  isso só funciona na máquina de quem construiu. Reporte como limitação
  conhecida a documentar no README — o enunciado aceita isso, mas só se
  estiver dito explicitamente, não como surpresa para o avaliador que
  abrir o arquivo numa máquina diferente.
- Se o projeto passou por reorganização de pastas (ex.: `painel/dados/`
  movido), confirme que o caminho referenciado no modelo bate com a
  estrutura atual do repositório — um `.pbip` aberto depois de mover
  pastas é um ponto real de quebra silenciosa.
