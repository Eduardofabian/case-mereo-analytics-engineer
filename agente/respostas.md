# Respostas do agente -- case Mereo

## 1. Qual o score da Gerência de Marketing?

A **Gerência de Marketing** apresenta score **84,43**.

Como essa área não possui subáreas (tem_filhas=false), o score direto e o consolidado são iguais por construção, então não há distinção a ser feita nesse caso.

**Comentario:** Na primeira rodada essa pergunta falhou — mas por um bug meu no roteiro de teste, não do agente: eu tinha escrito a pergunta sem o acento ("Gerencia"), e a área no banco é "Gerência de Marketing", com acento. ILIKE ignora maiúsculas/minúsculas, mas não ignora acento, então o nome sem acento não encontrava a área. O comportamento do agente diante da falha foi o certo mesmo assim: não achou, não chutou uma área parecida, pediu confirmação do nome — o mesmo padrão correto da pergunta 5, só que aqui o erro de origem era meu. Corrigi o roteiro e a resposta ficou certa: score_direto = score_consolidado = 84,43 (conferido direto no CSV), área sem subárea. Lição: a resolução de nome por ILIKE é sensível a acento — registrado em "Limitações conhecidas" no README, com a melhoria proposta (normalizar acento antes de comparar).

## 2. Quais colaboradores do time da Sofia Oliveira ficaram com score abaixo de 90?

Encontrei o time da **Sofia Oliveira**. Os colaboradores com score abaixo de 90 são:

| Colaborador | Score | Elegível R10 |
|---|---|---|
| Sabrina Cardoso | 54,85 | Sim |
| Manuela Oliveira | 63,67 | Sim |
| Gabriela Ferraz | 89,30 | Sim |

Todos os três são elegíveis para o R10.

**Comentario:** Acertou. Conferi contra os CSVs de forma independente: a Sofia Oliveira tem 12 subordinados diretos, e exatamente 3 ficaram abaixo de 90 (Sabrina Cardoso 54,85, Manuela Oliveira 63,67, Gabriela Ferraz 89,30), valores batendo na casa decimal. O agente tambem devolveu a elegibilidade R10 de cada um sem eu pedir -- a tool inclui esse campo de proposito, pra transparencia, e o agente usou bem.

## 3. Qual diretoria teve o melhor resultado consolidado?

A diretoria com o melhor resultado consolidado foi a **Diretoria Financeira**, com score consolidado de aproximadamente **103,30**.

**Comentario:** Acertou. Diretoria Financeira (103,30) na frente de Comercial (95,08) e Operacoes (93,19), conferido direto no vw_score_area.csv. Pergunta sem ambiguidade (ja pede "consolidado" explicitamente), e o ranking_areas resolveu em uma chamada.

## 4. Quais metas do Nicolas Vasconcelos ficaram abaixo de 80% de atingimento?

Encontrei o colaborador **Nicolas Vasconcelos** na base. As metas dele com atingimento abaixo de 80% foram:

| Meta | Atingimento | Peso |
|---|---|---|
| Número de reuniões qualificadas | 70,19% | 30 |
| Leads gerados | 77,07% | 35 |

Ambas tiveram nota 0,0 nesse critério.

**Comentario:** Os dados estao certos nas duas rodadas que rodei (2 metas, atingimento e peso batendo com vw_nota_meta.csv), mas a EXPLICACAO mudou entre uma rodada e outra pro mesmo resultado: numa vez o agente disse "nota zero... provavelmente por estarem abaixo de algum limiar minimo" (tratando como suposicao uma regra deterministica), e noutra citou a R6 explicitamente e com certeza. Mesmos dados, mesma tool, explicacao diferente -- porque o system prompt nunca deu as regras de negocio ao agente, so os numeros ja calculados; quando ele tenta explicar o porque, as vezes acerta por inferencia, as vezes specula. Melhoria clara: colocar um resumo das regras-chave (pelo menos R6) no system prompt, pra tirar essa variancia e ele responder com certeza sempre, nao por sorte.

## 5. Qual o score da área Vendas Oeste?

Não encontrei nenhuma área chamada "Vendas Oeste" na base do Grupo Aurora. Esse nome não existe nos registros.

Infelizmente não tenho como sugerir um nome parecido com certeza, já que essa é a primeira consulta sobre áreas que fiz. Se você puder confirmar o nome exato da área (ou parte dele), eu consulto novamente. Caso queira, também posso buscar um ranking de áreas para te ajudar a identificar o nome correto.

**Comentario:** Acertou, e e o teste mais importante dos 5. "Vendas Oeste" nao existe na base -- as areas de Vendas reais sao Coordenacao Vendas Sul e Coordenacao Vendas Norte (conferido direto contra area no SQL Server e contra area.csv). O agente nao alucinou um numero pra Sul ou Norte, nao arredondou pro nome mais parecido -- disse que nao encontrou e, numa das rodadas, foi ainda mais conservador: disse explicitamente que nao tinha como sugerir um nome parecido "com seguranca" porque nao tinha consultado as outras areas de vendas naquela conversa, em vez de supor Sul/Norte/Leste sem checar. E a prova de que a decisao de desenho (resolver_por_nome nunca "pega o primeiro", status nao_encontrado tratado explicitamente no prompt) funciona na pratica.
