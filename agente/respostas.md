# Respostas do agente -- case Mereo

## 1. Qual o score da Gerência de Marketing?

A **Gerência de Marketing** tem score **84,43**.

Como essa área não possui subáreas (tem_filhas=false), o score direto e o consolidado são iguais por construção — ou seja, o valor reflete apenas o desempenho direto da própria gerência, sem agregação de áreas subordinadas.

**Comentario:** Na primeira rodada essa pergunta falhou — mas por um bug meu no roteiro de teste, não do agente: eu tinha escrito a pergunta sem o acento ("Gerencia"), e a área no banco é "Gerência de Marketing", com acento. ILIKE ignora maiúsculas/minúsculas, mas não ignora acento, então o nome sem acento não encontrava a área. O comportamento do agente diante da falha foi o certo mesmo assim: não achou, não chutou uma área parecida, pediu confirmação do nome — o mesmo padrão correto da pergunta 5, só que aqui o erro de origem era meu. Corrigi o roteiro e a resposta ficou certa: score_direto = score_consolidado = 84,43 (conferido direto no CSV), área sem subárea. Lição: a resolução de nome por ILIKE é sensível a acento — registrado em "Limitações conhecidas" no README, com a melhoria proposta (normalizar acento antes de comparar).

## 2. Quais colaboradores do time da Sofia Oliveira ficaram com score abaixo de 90?

Os colaboradores do time da **Sofia Oliveira** com score abaixo de 90 foram:

| Colaborador | Score | Elegível R10 |
|---|---|---|
| Sabrina Cardoso | 54,85 | Sim |
| Manuela Oliveira | 63,67 | Sim |
| Gabriela Ferraz | 89,30 | Sim |

**Comentario:** Acertou. Conferi contra os CSVs de forma independente: a Sofia Oliveira tem 12 subordinados diretos, e exatamente 3 ficaram abaixo de 90 (Sabrina Cardoso 54,85, Manuela Oliveira 63,67, Gabriela Ferraz 89,30), valores batendo na casa decimal. Depois da auditoria, a tool passou a filtrar só colaboradores elegíveis (R10) por padrão -- esses três já vêm filtrados por construção da query, não por uma flag que o agente precisasse interpretar.

## 3. Qual diretoria teve o melhor resultado consolidado?

A diretoria com o melhor resultado consolidado foi a **Diretoria Financeira**, com score consolidado de aproximadamente **103,30**.

**Comentario:** Acertou. Diretoria Financeira (103,30) na frente de Comercial (95,08) e Operações (93,19), conferido direto no vw_score_area.csv. Pergunta sem ambiguidade (já pede "consolidado" explicitamente), e o ranking_areas resolveu em uma chamada.

## 4. Quais metas do Nicolas Vasconcelos ficaram abaixo de 80% de atingimento?

Encontrei **Nicolas Vasconcelos** na base. As metas com atingimento abaixo de 80% foram:

| Meta | Atingimento | Nota | Peso |
|---|---|---|---|
| Número de reuniões qualificadas | 70,2% | 0,0 | 30 |
| Leads gerados | 77,1% | 0,0 | 35 |

Ambas tiveram atingimento insuficiente, resultando em nota truncada para 0,0.

**Comentario:** Os dados estão certos nas três rodadas que rodei (2 metas, atingimento e peso batendo com vw_nota_meta.csv), mas a EXPLICAÇÃO mudou entre uma rodada e outra pro mesmo resultado: numa vez o agente disse "nota zero... provavelmente por estarem abaixo de algum limiar mínimo" (tratando como suposição uma regra determinística), e noutra citou a R6 explicitamente e com certeza. Mesmos dados, mesma tool, explicação diferente -- porque o system prompt nunca deu as regras de negócio ao agente, só os números já calculados; quando ele tenta explicar o porquê, às vezes acerta por inferência, às vezes especula. Melhoria clara: colocar um resumo das regras-chave (pelo menos R6) no system prompt, pra tirar essa variância e ele responder com certeza sempre, não por sorte.

## 5. Qual o score da área Vendas Oeste?

A área "Vendas Oeste" não existe na base de dados — não encontrei nenhum registro com esse nome.

Se puder confirmar o nome exato (ou parte dele), posso buscar novamente. Caso tenha alguma variação em mente, me diga e eu verifico.

**Comentario:** Acertou, e é o teste mais importante dos 5. "Vendas Oeste" não existe na base -- as áreas de Vendas reais são Coordenação Vendas Sul e Coordenação Vendas Norte (conferido direto contra área no SQL Server e contra area.csv). O agente não alucinou um número pra Sul ou Norte, não arredondou pro nome mais parecido -- disse que não encontrou e, numa das rodadas, foi ainda mais conservador: disse explicitamente que não tinha como sugerir um nome parecido "com segurança" porque não tinha consultado as outras áreas de vendas naquela conversa, em vez de supor Sul/Norte/Leste sem checar. É a prova de que a decisão de desenho (resolver_por_nome nunca "pega o primeiro", status nao_encontrado tratado explicitamente no prompt) funciona na prática.
