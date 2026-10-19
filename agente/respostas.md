# Respostas do agente -- case Mereo

## 1. Qual o score da Gerência de Marketing?

A **Gerência de Marketing** tem score **84,43**.

Como essa área não possui subáreas (tem_filhas=false), o score direto e o consolidado são o mesmo valor por construção — não há diferença a explicar nesse caso.

**Comentario:** Na primeira rodada essa pergunta falhou -- mas por um bug meu no roteiro de teste, nao do agente: eu tinha escrito "Gerencia" sem o acento circunflexo aqui no script, e a area no banco e "Gerencia de Marketing". ILIKE normaliza maiusculas/minusculas mas nao remove acento, entao "Gerencia" nunca batia com "Gerencia". O comportamento do agente diante da falha foi o certo mesmo assim: nao achou, nao chutou pra area parecida, pediu confirmacao do nome -- o mesmo padrao correto da pergunta 5, so que aqui o erro de origem era meu. Corrigi o typo e a resposta ficou certa: score_direto = score_consolidado = 84,43 (conferido direto no CSV), area sem subarea. O que fica como licao: resolucao de nome por ILIKE e sensivel a acento, e isso nao estava documentado como limitacao conhecida -- devia estar no README.

## 2. Quais colaboradores do time da Sofia Oliveira ficaram com score abaixo de 90?

Os colaboradores do time da **Sofia Oliveira** com score abaixo de 90 são:

| Colaborador | Score | Elegível R10 |
|---|---|---|
| Sabrina Cardoso | 54,85 | Sim |
| Manuela Oliveira | 63,67 | Sim |
| Gabriela Ferraz | 89,30 | Sim |

**Comentario:** Acertou. Conferi contra os CSVs de forma independente: a Sofia Oliveira tem 12 subordinados diretos, e exatamente 3 ficaram abaixo de 90 (Sabrina Cardoso 54,85, Manuela Oliveira 63,67, Gabriela Ferraz 89,30), valores batendo na casa decimal. O agente tambem devolveu a elegibilidade R10 de cada um sem eu pedir -- a tool inclui esse campo de proposito, pra transparencia, e o agente usou bem.

## 3. Qual diretoria teve o melhor resultado consolidado?

A diretoria com o melhor resultado consolidado foi a **Diretoria Financeira**, com score consolidado de aproximadamente **103,30**.

**Comentario:** Acertou. Diretoria Financeira (103,30) na frente de Comercial (95,08) e Operacoes (93,19), conferido direto no vw_score_area.csv. Pergunta sem ambiguidade (ja pede "consolidado" explicitamente), e o ranking_areas resolveu em uma chamada.

## 4. Quais metas do Nicolas Vasconcelos ficaram abaixo de 80% de atingimento?

As metas de **Nicolas Vasconcelos** que ficaram abaixo de 80% de atingimento foram:

| Meta | Atingimento | Peso |
|---|---|---|
| Número de reuniões qualificadas | 70,19% | 30 |
| Leads gerados | 77,07% | 35 |

Ambas tiveram nota 0,0 nesse critério de corte.

**Comentario:** Os dados estao certos nas duas rodadas que rodei (2 metas, atingimento e peso batendo com vw_nota_meta.csv), mas a EXPLICACAO mudou entre uma rodada e outra pro mesmo resultado: numa vez o agente disse "nota zero... provavelmente por estarem abaixo de algum limiar minimo" (tratando como suposicao uma regra deterministica), e noutra citou a R6 explicitamente e com certeza. Mesmos dados, mesma tool, explicacao diferente -- porque o system prompt nunca deu as regras de negocio ao agente, so os numeros ja calculados; quando ele tenta explicar o porque, as vezes acerta por inferencia, as vezes specula. Melhoria clara: colocar um resumo das regras-chave (pelo menos R6) no system prompt, pra tirar essa variancia e ele responder com certeza sempre, nao por sorte.

## 5. Qual o score da área Vendas Oeste?

A área "Vendas Oeste" não existe na base de dados — não encontrei nenhum registro com esse nome.

Infelizmente não tenho outras consultas prévias que me permitam sugerir nomes parecidos com segurança. Você poderia conferir o nome exato da área (talvez algo como "Vendas Norte", "Vendas Sul" ou outra variação regional)? Se puder confirmar ou informar o nome correto, faço a consulta novamente.

**Comentario:** Acertou, e e o teste mais importante dos 5. "Vendas Oeste" nao existe na base -- as areas de Vendas reais sao Coordenacao Vendas Sul e Coordenacao Vendas Norte (conferido direto contra area no SQL Server e contra area.csv). O agente nao alucinou um numero pra Sul ou Norte, nao arredondou pro nome mais parecido -- disse que nao encontrou e, numa das rodadas, foi ainda mais conservador: disse explicitamente que nao tinha como sugerir um nome parecido "com seguranca" porque nao tinha consultado as outras areas de vendas naquela conversa, em vez de supor Sul/Norte/Leste sem checar. E a prova de que a decisao de desenho (resolver_por_nome nunca "pega o primeiro", status nao_encontrado tratado explicitamente no prompt) funciona na pratica.
