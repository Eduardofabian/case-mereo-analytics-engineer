# Critério 3 — Agente de IA (20%) e Critério 5 — Perguntas abertas (10%)

Agrupados porque ambos são avaliados contra a mesma expectativa da vaga:
"acompanhar a qualidade das respostas" de um agente de IA é
responsabilidade #1 descrita na vaga, não exercício teórico.

## Critério 3 — Agente de IA (20%)

- `agente/` tem código real (`agent.py`, `tools.py` ou equivalente) —
  confirme lendo `tools.py` que as ferramentas são funções fixas
  parametrizadas, **não SQL livre gerado a cada pergunta**. Isso é
  decisão arquitetural central: um agente que gera SQL livre contra a
  base de performance de colaboradores é um risco real de alucinação e
  de exposição de dado sensível, e a vaga pede justamente "preparar e
  validar os dados e consultas que alimentam" os agentes — ferramenta
  fixa é a resposta correta a essa responsabilidade.
- `agente/respostas.md` (ou equivalente) tem as 5 respostas às perguntas
  do enunciado **com conteúdo real**, não placeholder (`_[completar]_`,
  `TODO`, comentário entre colchetes sem preenchimento) — isso é falha
  grave aqui, não detalhe.
- Cada resposta tem comentário de "onde acertou, onde errou, o que
  melhoraria" — exigência explícita do enunciado; sem isso o critério
  não é atendido mesmo que as respostas estejam tecnicamente certas.
- Teste ao menos 1 pergunta com nome que não existe na base (ex. uma
  área ou colaborador inventado) e confirme que o agente não aluciona —
  deve devolver status explícito tipo "não encontrado" ou pedir
  confirmação, nunca inventar o resultado mais parecido. Se o código
  tiver status explícitos (`nao_encontrado`, `multiplos_candidatos`,
  `sem_score`, `nao_atende_criterio_gestor` ou equivalentes), confirme
  que cada status realmente é alcançável e testado, não só declarado.
- Diferencial citado na vaga: uso de Pydantic AI, LangChain ou API da
  OpenAI/Anthropic. Se usado, vale nota explícita no veredito como
  atendimento de diferencial, não só "usou IA".

## Critério 5 — Perguntas abertas (10%)

As 3 perguntas do enunciado: envio de dados via API, como saber que o
agente está errando, RH reclamando de divergência de score.

- Cada resposta tem até 10 linhas, como pedido — resposta mais longa é
  desvio de formato, mesmo com conteúdo bom.
- As respostas usam o case como exemplo concreto: citam regra de negócio
  real (ex.: R1-R11), script real (ex.: `verificacao_independente.py`),
  achado real de qualidade — não teoria genérica de engenharia de dados
  que poderia vir de qualquer outro case. Isso é o que separa resposta
  boa de resposta genérica aqui.
- Pergunta "como saber que o agente de IA está errando" é literalmente a
  responsabilidade #1 da vaga ("acompanhando a qualidade das respostas").
  Uma resposta que não menciona nada do próprio agente implementado
  (status explícitos, teste com dado inexistente, log de resposta) é gap
  de alta prioridade — o enunciado está pedindo pra aplicar no próprio
  case, não discorrer em abstrato.
- Pergunta sobre integração via API: se mencionar Azure Functions/Blob
  Storage ou AWS Lambda nomeadamente (diferenciais da vaga), tratar como
  atendimento explícito, não só boa prática genérica de engenharia.
