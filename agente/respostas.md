# Respostas do agente -- case Mereo

## 1. Qual o score da Gerência de Marketing?

A **Gerência de Marketing** tem score **84,43**.

Como essa área não possui áreas filhas (tem_filhas=false), o score direto e o consolidado são iguais por construção — ou seja, o valor reflete apenas a média dos colaboradores elegíveis diretamente ligados a essa gerência.

**Comentario:** Na primeira rodada essa pergunta falhou — mas por um bug meu no roteiro de teste, não do agente: eu tinha escrito a pergunta sem o acento ("Gerencia"), e a área no banco é "Gerência de Marketing", com acento. ILIKE ignora maiúsculas/minúsculas, mas não ignora acento, então o nome sem acento não encontrava a área. O comportamento do agente diante da falha foi o certo mesmo assim: não achou, não chutou uma área parecida, pediu confirmação do nome — o mesmo padrão correto da pergunta 5, só que aqui o erro de origem era meu. Corrigi o roteiro e a resposta ficou certa: score_direto = score_consolidado = 84,43 (conferido direto no CSV), área sem subárea. Lição: a resolução de nome por ILIKE é sensível a acento — registrado em "Limitações conhecidas" no README, com a melhoria proposta (normalizar acento antes de comparar).

## 2. Quais colaboradores do time da Sofia Oliveira ficaram com score abaixo de 90?

Encontrei 3 colaboradores do time da **Sofia Oliveira** com score abaixo de 90:

| Colaborador | Score | Elegível R10 |
|---|---|---|
| Sabrina Cardoso | 54,85 | Sim |
| Manuela Oliveira | 63,67 | Sim |
| Gabriela Ferraz | 89,30 | Sim |

Todos os três estão elegíveis para R10. Se quiser, posso detalhar as metas de algum deles para entender por que o score ficou baixo.

**Comentario:** Acertou. Conferi contra os CSVs de forma independente: a Sofia Oliveira tem 12 subordinados diretos, e exatamente 3 ficaram abaixo de 90 (Sabrina Cardoso 54,85, Manuela Oliveira 63,67, Gabriela Ferraz 89,30), valores batendo na casa decimal. Depois da auditoria, a tool passou a filtrar só colaboradores elegíveis (R10) por padrão -- esses três já vêm filtrados por construção da query, não por uma flag que o agente precisasse interpretar.

## 3. Qual diretoria teve o melhor resultado consolidado?

A diretoria com o melhor resultado consolidado foi a **Diretoria Financeira**, com score consolidado de **103,30**.

Esse valor representa a média de todos os colaboradores elegíveis da Diretoria Financeira somada às áreas hierarquicamente abaixo dela (gerências e coordenações vinculadas).

**Comentario:** Acertou. Diretoria Financeira (103,30) na frente de Comercial (95,08) e Operações (93,19), conferido direto no vw_score_area.csv. Pergunta sem ambiguidade (já pede "consolidado" explicitamente), e o ranking_areas resolveu em uma chamada.

## 4. Quais metas do Nicolas Vasconcelos ficaram abaixo de 80% de atingimento?

Encontrei o colaborador **Nicolas Vasconcelos**, e ele tem 2 metas com atingimento abaixo de 80%:

| Meta | Atingimento | Nota | Peso |
|---|---|---|---|
| Número de reuniões qualificadas | 70,19% | 0,0 | 30 |
| Leads gerados | 77,07% | 0,0 | 35 |

Como a regra de negócio diz que atingimento abaixo de 80% trava a nota em 0, essas duas metas entraram com nota 0 no cálculo do score dele — não é erro de lançamento, é consequência direta do atingimento ficar abaixo do limiar mínimo.

**Comentario:** Os dados continuam certos (2 metas, atingimento e peso batendo com vw_nota_meta.csv). MELHORIA APLICADA E VERIFICADA: o SYSTEM_PROMPT em agent.py passou a incluir um resumo das regras R6 (faixa de nota), R9 (score do colaborador) e R11 (score de área direto/consolidado) -- antes só os números calculados chegavam ao agente, nunca a regra por trás deles. Nesta rodada pós-mudança, a explicação citou a regra direto e com certeza ("a regra de negócio diz que atingimento abaixo de 80% trava a nota em 0... não é erro de lançamento, é consequência direta"), sem hedge -- antes da mudança, uma rodada tinha dito "provavelmente por estarem abaixo de algum limiar mínimo", tratando como suposição uma regra determinística. Ressalva honesta: só rodei uma vez depois da mudança, não várias -- não dá pra afirmar que a variância sumiu de forma definitiva, só que a causa raiz (agente sem acesso à regra, tendo que adivinhar) foi removida, o que deveria eliminar o problema por construção, não por sorte dessa rodada.

## 5. Qual o score da área Vendas Oeste?

Não encontrei nenhuma área chamada "Vendas Oeste" na base. Esse nome não existe no cadastro.

Se puder confirmar o nome exato, posso buscar novamente. Caso tenha dúvida sobre a grafia, me diga a região ou alguma parte do nome que eu tento localizar áreas parecidas (por exemplo, pode haver "Vendas Norte", "Vendas Sul" ou outra variação cadastrada).

**Comentario:** Acertou, e é o teste mais importante dos 5. "Vendas Oeste" não existe na base -- as áreas de Vendas reais são Coordenação Vendas Sul e Coordenação Vendas Norte (conferido direto contra área no SQL Server e contra area.csv). O agente não alucinou um número pra Sul ou Norte, não arredondou pro nome mais parecido -- disse que não encontrou e, numa das rodadas, foi ainda mais conservador: disse explicitamente que não tinha como sugerir um nome parecido "com segurança" porque não tinha consultado as outras áreas de vendas naquela conversa, em vez de supor Sul/Norte/Leste sem checar. É a prova de que a decisão de desenho (resolver_por_nome nunca "pega o primeiro", status nao_encontrado tratado explicitamente no prompt) funciona na prática. Ressalva: nesta rodada específica o agente sugeriu "Vendas Norte/Sul" sem ter consultado nenhuma tool antes -- o palpite acertou e veio com hedge, mas o prompt pede sugestão só a partir de nomes vistos em chamadas anteriores, e aqui ele não seguiu isso à risca.
