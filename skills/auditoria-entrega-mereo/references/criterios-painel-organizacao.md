# Critério 4 — Painel (15%) e Critério 6 — Organização da entrega e README (5%)

## Critério 4 — Painel (15%)

Auditoria detalhada de modelo e clareza fica em `auditoria-dashboard-mereo`
(skill irmã) — aqui, checar só a existência e o atendimento literal do
que o enunciado pede:

- PDF ou print do painel, mais o arquivo/código-fonte (se possível),
  ambos presentes em `painel/`, não só um dos dois.
- Painel de **uma página só**, como o enunciado pede explicitamente —
  mais de uma página/aba é desvio de formato, mesmo com conteúdo bom em
  cada página.
- Explicação curta de por que aqueles elementos foram escolhidos para
  mostrar — metade do critério "clareza e escolha do que mostrar" é a
  escolha ser explicada, não só executada.
- Produto real da Mereo (módulo Metas) tem padrão visual de semáforo
  verde/amarelo/vermelho por faixa de atingimento e alguma representação
  hierárquica (Árvore de Performance). Se o painel entregue não tiver
  nenhum dos dois elementos, reporte como lacuna visual concreta, porque
  é o padrão que o avaliador reconhece no próprio produto da empresa, não
  uma sugestão genérica de BI.

## Critério 6 — Organização da entrega e README (5%)

- Estrutura bate com o que o enunciado pede literalmente: `README.md`,
  `sql/`, `respostas/`, `painel/`, `agente/`.
- README cobre os temas que o enunciado pede explicitamente: decisões de
  interpretação de regra, qualidade dos dados, uso de IA, Parte 5,
  pendências. Falta de qualquer um desses é gap direto neste critério,
  mesmo que o conteúdo exista em outro lugar do repositório.
- README explica como reproduzir o pipeline do zero (comando a comando),
  e as dependências de cada componente (pipeline, agente, painel) estão
  documentadas sem estarem misturadas sem necessidade.
- Nenhum arquivo de dado sensível ou grande demais (ex. `.db` de origem)
  está sendo versionado sem necessidade, e isso está decidido e
  explicado, não deixado por acidente.
- A vaga cita explicitamente "Git e versionamento de código, com fluxo
  de pull requests e revisão" como requisito — se o repositório tiver
  histórico de commits organizado (não um único commit gigante), isso é
  sinal positivo a reconhecer; se for um único commit final, reporte como
  gap leve (o case não exige fluxo de PR, mas a vaga valoriza o hábito).
