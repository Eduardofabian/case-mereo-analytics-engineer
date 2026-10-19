# Contexto do case — vaga, empresa e produto Mereo

Este arquivo existe porque o case não é um exercício genérico de SQL: é a
simulação mais próxima possível do trabalho real do cargo, e quem avalia
muito provavelmente é quem descreveu esse trabalho (pesquisa feita sobre
a vaga e o produto real da Mereo, ver fonte completa em
`MEREO CASE/md/pesquisa-mereo.md`). Usar este contexto para calibrar o
rigor da auditoria, não para decorar o texto no README.

## A vaga (Analytics Engineer Pleno, Mereo, remota BR)

Trechos literais da descrição, relevantes porque mostram o que o
avaliador reconhece como "dia a dia do cargo", não como exercício
acadêmico isolado:

> "Construir e evoluir aplicações com agentes de IA... preparando e
> validando os dados e as consultas que os alimentam e acompanhando a
> qualidade das respostas e o consumo das soluções"

> "Modelar e documentar tabelas e regras de negócio do Data Warehouse,
> cuidando da qualidade e da governança dos dados"

> "Capacidade analítica para traduzir perguntas de negócio em dados e
> explicar resultados para pessoas não técnicas"

Implicação direta: a Parte 5 (perguntas abertas) e os achados de
qualidade não são seção de preenchimento burocrático — são literalmente
duas das responsabilidades descritas na vaga. Uma resposta genérica ali
pesa mais negativamente aqui do que pesaria em outro processo seletivo,
porque o avaliador está comparando contra o que a pessoa vai fazer de
fato no cargo.

Stack citado na vaga, em ordem de menção (primeira menção = preferência
implícita quando o case permite ambiguidade): SQL Server antes de outro
SGBD; Metabase antes de Power BI (Power BI é citado e aceito, não é
exclusão); Python; Pydantic AI/LangChain/API OpenAI ou Anthropic
(diferencial, não obrigatório); Azure Functions ou AWS Lambda
(diferencial); Streamlit (diferencial); Git com fluxo de PR e revisão.

## Valores declarados pela empresa (tom da página da vaga, mais
horizontal/startup que o institucional)

Meritocracia, Inovação, Potencial, Ética, Comprometimento, Excelência —
com a frase "a escolha consciente de nunca fazer 'mais ou menos'"
descrevendo Excelência. Esse é o padrão de rigor esperado: uma decisão
de qualidade de dados executada mas não justificada é "mais ou menos",
mesmo que o número final esteja certo.

## O produto real que o case espelha: módulo Metas

Confirmado por evidência direta (vocabulário idêntico entre o case e o
produto), não suposição:

- R11 (score Direto/Consolidado por hierarquia) = feature **"Árvore de
  Performance"** do produto real da Mereo, nome idêntico.
- R9 (score ponderado por colaborador) = feature **"Painel de
  performance"** real, pessoa → metas → nota.
- Polaridade, tipo de acumulação, peso (R4-R7) = vocabulário do módulo
  Metas, não aparece em outros módulos da Mereo (OKR, Competências).

Isso significa que o avaliador reconhece visualmente o padrão esperado de
layout (detalhado em `auditoria-dashboard-mereo/references/contexto-produto-mereo.md`)
e também reconhece o vocabulário de regra de negócio — um README que
troca "polaridade" por "direção da meta" ou generaliza o nome das regras
perde precisão terminológica que o avaliador tende a notar.

## O que isso muda na auditoria

- Decisão de qualidade sem justificativa específica → gap de alta
  prioridade, não "detalhe a melhorar": fere Excelência e Meritocracia
  diretamente, não é só estilo de escrita.
- Resposta de Parte 5 que soa genérica (poderia ser copiada de qualquer
  outro case de dados, sem menção a scripts/regras/achados reais deste
  projeto) → gap de alta prioridade, porque a vaga pede exatamente essa
  tradução de "pergunta de negócio real" em resposta concreta.
- Uso da terminologia do enunciado (polaridade, atingimento, elegibilidade,
  consolidado, direto) em vez de paráfrase genérica → sinal positivo a
  reconhecer explicitamente, não é só preferência de estilo.
- Menção a Pydantic AI/LangChain no agente, ou a Azure Functions/AWS
  Lambda na resposta de integração via API → tratar como atendimento de
  diferencial explícito da vaga, vale nota no veredito, não só "bônus
  genérico de usar IA".
