# Relatório de diagnóstico de qualidade — Case Mereo

## 🔴 Lançamento válido APÓS desligamento — colaborador ELEGÍVEL (R10) (24 linha(s))
afeta diretamente P1/P2/P3 — decisão: manter literal no cálculo, documentar no README (ver análise de sensibilidade)

|   id_lancamento |   id_meta |   mes |   previsto |   realizado | nao_se_aplica   | data_lancamento   |   id_ciclo |   id_colaborador | data_admissao   | data_desligamento   | elegivel   | valido   |
|----------------:|----------:|------:|-----------:|------------:|:----------------|:------------------|-----------:|-----------------:|:----------------|:--------------------|:-----------|:---------|
|          900395 |      5046 |    11 |         45 |          44 | False           | 2025-12-07        |       2025 |              113 | 2016-09-14      | 2025-10-02          | True       | True     |
|          900396 |      5046 |    12 |         41 |          38 | False           | 2026-01-05        |       2025 |              113 | 2016-09-14      | 2025-10-02          | True       | True     |
|          900407 |      5047 |    11 |        155 |         202 | False           | 2025-12-13        |       2025 |              113 | 2016-09-14      | 2025-10-02          | True       | True     |
|          900408 |      5047 |    12 |        146 |         177 | False           | 2026-01-15        |       2025 |              113 | 2016-09-14      | 2025-10-02          | True       | True     |
|          901079 |      5125 |    11 |        205 |         227 | False           | 2025-12-14        |       2025 |              134 | 2021-09-16      | 2025-10-21          | True       | True     |
|          901080 |      5125 |    12 |        188 |         190 | False           | 2026-01-14        |       2025 |              134 | 2021-09-16      | 2025-10-21          | True       | True     |
|          901091 |      5126 |    11 |         97 |         121 | False           | 2025-12-10        |       2025 |              134 | 2021-09-16      | 2025-10-21          | True       | True     |
|          901092 |      5126 |    12 |         86 |         102 | False           | 2026-01-12        |       2025 |              134 | 2021-09-16      | 2025-10-21          | True       | True     |
|          901116 |      5129 |    12 |         99 |         115 | False           | 2026-01-04        |       2025 |              135 | 2020-08-25      | 2025-11-13          | True       | True     |
|          901209 |      5140 |     9 |         26 |          28 | False           | 2025-10-03        |       2025 |              138 | 2017-04-15      | 2025-08-08          | True       | True     |

## 🔴 Meta com denominador=0 em Acumulação Soma (R4 — divisão por zero) (1 linha(s))
soma(previsto) ou soma(realizado)=0 dependendo da polaridade — atingimento indefinido, tratado como sem nota (extensão de R8, não regra literal)

|   id_meta | nome_meta     |   colaborador | polaridade       | denominador   |   soma |
|----------:|:--------------|--------------:|:-----------------|:--------------|-------:|
|      5094 | Leads gerados |           125 | Melhor para cima | previsto      |      0 |

## 🔴 PK duplicada em area (0 linha(s))
id_area deveria ser único em area


## 🔴 PK duplicada em ciclo (0 linha(s))
id_ciclo deveria ser único em ciclo


## 🔴 PK duplicada em colaborador (0 linha(s))
id_colaborador deveria ser único em colaborador


## 🔴 PK duplicada em meta (0 linha(s))
id_meta deveria ser único em meta


## 🔴 PK duplicada em meta_valor_mensal (0 linha(s))
id_lancamento deveria ser único em meta_valor_mensal


## 🔴 area.id_area_pai órfão (0 linha(s))
área pai inexistente


## 🔴 colaborador.id_area órfão (0 linha(s))
área inexistente


## 🔴 colaborador.id_gestor órfão (0 linha(s))
gestor inexistente


## 🔴 meta.id_colaborador órfão (0 linha(s))
colaborador inexistente


## 🔴 meta_valor_mensal.id_meta órfão (0 linha(s))
meta inexistente


## 🔴 Ciclo na cadeia de gestores (multi-nível) (0 linha(s))
colaborador é seu próprio gestor em algum nível acima


## 🔴 Auto-gestor direto (0 linha(s))
id_gestor = id_colaborador


## 🔴 Compartilhada apontando p/ outra Compartilhada (0 linha(s))
R7 assume referência direta a uma Individual


## 🔴 Compartilhada sem id_meta_referencia (0 linha(s))
quebra o join de R7


## 🔴 Mês com denominador=0 dentro de meta Acumulação Média (0 linha(s))
um mês específico tem o lado-denominador zerado — atingimento daquele mês fica indefinido


## 🔴 mes fora de 1-12 (0 linha(s))



## 🔴 Lançamento válido ANTES da admissão (colaborador elegível) (0 linha(s))
mês de referência é anterior ao mês de admissão — afeta o score se não tratado


## 🟡 Meta Compartilhada com lançamento mensal PRÓPRIO (60 linha(s))
R7: deveria usar só os lançamentos da referência. Ignorado no cálculo, mas é achado de carga a documentar

|   id_lancamento |   id_meta |   mes |   previsto |   realizado | nao_se_aplica   | data_lancamento   |
|----------------:|----------:|------:|-----------:|------------:|:----------------|:------------------|
|          903574 |      5278 |     1 |        100 |       101.1 | False           | 2025-02-05        |
|          903575 |      5278 |     2 |        100 |        95.2 | False           | 2025-03-08        |
|          903576 |      5278 |     3 |        100 |        88.8 | False           | 2025-04-05        |
|          903577 |      5278 |     4 |        100 |        80.3 | False           | 2025-05-06        |
|          903578 |      5278 |     5 |        100 |       105.7 | False           | 2025-06-05        |
|          903579 |      5278 |     6 |        100 |       131.9 | False           | 2025-07-06        |
|          903580 |      5278 |     7 |        100 |        87.2 | False           | 2025-08-05        |
|          903581 |      5278 |     8 |        100 |        66.8 | False           | 2025-09-05        |
|          903582 |      5278 |     9 |        100 |        99.5 | False           | 2025-10-06        |
|          903583 |      5278 |    10 |        100 |       135.6 | False           | 2025-11-05        |

## 🟡 nao_se_aplica=0 mas previsto/realizado nulo (43 linha(s))
R3 já exclui do cálculo, mas documentar

|   id_lancamento |   id_meta |   mes |   previsto |   realizado | nao_se_aplica   | data_lancamento   |
|----------------:|----------:|------:|-----------:|------------:|:----------------|:------------------|
|          900203 |      5023 |    11 |         83 |         nan | False           | 2025-12-04        |
|          900204 |      5023 |    12 |         91 |         nan | False           | 2026-01-13        |
|          900504 |      5058 |    12 |         40 |         nan | False           | 2026-01-05        |
|          900657 |      5077 |     9 |         33 |         nan | False           | 2025-10-10        |
|          900658 |      5077 |    10 |         31 |         nan | False           | 2025-11-15        |
|          900659 |      5077 |    11 |         32 |         nan | False           | 2025-12-14        |
|          900660 |      5077 |    12 |         35 |         nan | False           | 2026-01-06        |
|          900718 |      5084 |    10 |         99 |         nan | False           | 2025-11-11        |
|          900719 |      5084 |    11 |        111 |         nan | False           | 2025-12-04        |
|          900720 |      5084 |    12 |        104 |         nan | False           | 2026-01-12        |

## 🟡 Meta sem NENHUM lançamento mensal (zero linhas) (4 linha(s))
R8 cobre o efeito (sem nota, fora do score), mas aqui não há lançamento algum, nem inválido — diferente do caso de lançamento nulo. Checado contra o id_meta_lancamentos resolvido (R7), não o id_meta bruto

|   id_meta |   id_ciclo |   id_colaborador | nome_meta                           | tipo_meta   |   id_meta_referencia | polaridade        | tipo_acumulacao   |   peso | polaridade_efetiva   | acumulacao_efetiva   |   id_meta_lancamentos |
|----------:|-----------:|-----------------:|:------------------------------------|:------------|---------------------:|:------------------|:------------------|-------:|:---------------------|:---------------------|----------------------:|
|      5014 |       2025 |              104 | Prazo médio de fechamento (dias)    | Individual  |                  nan | Melhor para baixo | Média             |      5 | Melhor para baixo    | Média                |                  5014 |
|      5063 |       2025 |              118 | Receita de novos contratos (R$ mil) | Individual  |                  nan | Melhor para cima  | Soma              |     10 | Melhor para cima     | Soma                 |                  5063 |
|      5146 |       2025 |              139 | Pedidos expedidos                   | Individual  |                  nan | Melhor para cima  | Soma              |     30 | Melhor para cima     | Soma                 |                  5146 |
|      5188 |       2025 |              149 | Índice de devoluções (%)            | Individual  |                  nan | Melhor para baixo | Média             |     15 | Melhor para baixo    | Média                |                  5188 |

## 🟡 meta.peso negativo (1 linha(s))
ABS() aplicado em intermediate

|   id_meta |   id_ciclo |   id_colaborador | nome_meta         | tipo_meta   |   id_meta_referencia | polaridade        | tipo_acumulacao   |   peso |
|----------:|-----------:|-----------------:|:------------------|:------------|---------------------:|:------------------|:------------------|-------:|
|      5286 |       2025 |              174 | Inadimplência (%) | Individual  |                  nan | Melhor para baixo | Média             |     -5 |

## 🟡 Gestor fora da hierarquia de área do subordinado (0 linha(s))
área do gestor não é a mesma nem ancestral da área do subordinado


## 🟡 area.nome com espaço extra (0 linha(s))
nome com espaço no início/fim ou duplo espaço interno


## 🟡 colaborador.nome com espaço extra (0 linha(s))
nome com espaço no início/fim ou duplo espaço interno


## 🟡 meta.nome_meta com espaço extra (0 linha(s))
nome com espaço no início/fim ou duplo espaço interno


## 🟡 Compartilhada referenciando outro ciclo (0 linha(s))
referência cruzada de ciclo


## 🟡 Compartilhada com nome_meta divergente da referência (0 linha(s))
nome deveria ser igual ao da meta referenciada


## 🟡 Individual com id_meta_referencia preenchido (0 linha(s))
campo deveria ser nulo


## 🟡 previsto negativo (0 linha(s))



## 🟡 realizado negativo (0 linha(s))



## ⚪ Lançamento válido APÓS desligamento — colaborador NÃO elegível (R10) (138 linha(s))
não afeta P1/P2/P3 (colaborador já sai por R10 de qualquer forma), mas é o mesmo padrão de dado — registrado por completude

|   id_lancamento |   id_meta |   mes |   previsto |   realizado | nao_se_aplica   | data_lancamento   |   id_ciclo |   id_colaborador | data_admissao   | data_desligamento   | elegivel   | valido   |
|----------------:|----------:|------:|-----------:|------------:|:----------------|:------------------|-----------:|-----------------:|:----------------|:--------------------|:-----------|:---------|
|          900411 |      5049 |     3 |         23 |          15 | False           | 2025-04-10        |       2025 |              114 | 2017-05-19      | 2025-02-12          | False      | True     |
|          900412 |      5049 |     4 |         24 |          17 | False           | 2025-05-06        |       2025 |              114 | 2017-05-19      | 2025-02-12          | False      | True     |
|          900413 |      5049 |     5 |         23 |          15 | False           | 2025-06-07        |       2025 |              114 | 2017-05-19      | 2025-02-12          | False      | True     |
|          900414 |      5049 |     6 |         25 |          20 | False           | 2025-07-09        |       2025 |              114 | 2017-05-19      | 2025-02-12          | False      | True     |
|          900415 |      5049 |     7 |         24 |          16 | False           | 2025-08-10        |       2025 |              114 | 2017-05-19      | 2025-02-12          | False      | True     |
|          900416 |      5049 |     8 |         23 |          18 | False           | 2025-09-09        |       2025 |              114 | 2017-05-19      | 2025-02-12          | False      | True     |
|          900417 |      5049 |     9 |         25 |          16 | False           | 2025-10-07        |       2025 |              114 | 2017-05-19      | 2025-02-12          | False      | True     |
|          900418 |      5049 |    10 |         23 |          17 | False           | 2025-11-15        |       2025 |              114 | 2017-05-19      | 2025-02-12          | False      | True     |
|          900419 |      5049 |    11 |         23 |          15 | False           | 2025-12-07        |       2025 |              114 | 2017-05-19      | 2025-02-12          | False      | True     |
|          900420 |      5049 |    12 |         22 |          14 | False           | 2026-01-12        |       2025 |              114 | 2017-05-19      | 2025-02-12          | False      | True     |

## ⚪ lançamento duplicado (id_meta, mes) (90 linha(s))
R2 resolve via data_lancamento mais recente — aqui é só a contagem bruta

|   id_lancamento |   id_meta |   mes |   previsto |   realizado | nao_se_aplica   | data_lancamento   |
|----------------:|----------:|------:|-----------:|------------:|:----------------|:------------------|
|          900158 |      5019 |     2 |        142 |        75.3 | False           | 2025-03-05        |
|          900360 |      5041 |    12 |         40 |        43   | False           | 2026-01-03        |
|          900364 |      5043 |     4 |         23 |        22   | False           | 2025-05-13        |
|          900367 |      5043 |     7 |         25 |        22   | False           | 2025-08-13        |
|          900383 |      5044 |    11 |        116 |       105   | False           | 2025-12-03        |
|          900390 |      5046 |     6 |         44 |        44.2 | False           | 2025-07-04        |
|          900402 |      5047 |     6 |        152 |       174   | False           | 2025-07-16        |
|          900411 |      5049 |     3 |         23 |        15   | False           | 2025-04-10        |
|          900486 |      5057 |     6 |        112 |       115   | False           | 2025-07-11        |
|          900583 |      5069 |     7 |        122 |        94.7 | False           | 2025-08-03        |

## ⚪ soma de peso por colaborador != 100 (7 linha(s))
não quebra R9 (normaliza por soma de peso), mas documentar

|   id_colaborador |   peso |
|-----------------:|-------:|
|              102 |    120 |
|              105 |     85 |
|              115 |    120 |
|              126 |    110 |
|              132 |     90 |
|              149 |    110 |
|              174 |     90 |

## ⚪ meta.tipo_meta com valor fora do esperado (0 linha(s))
valores encontrados: {'Individual', 'Compartilhada'}


## ⚪ meta.polaridade com valor fora do esperado (0 linha(s))
valores encontrados: {None, 'Melhor para baixo', 'Melhor para cima'}


## ⚪ meta.tipo_acumulacao com valor fora do esperado (0 linha(s))
valores encontrados: {None, 'Média', 'Soma'}


## ⚪ colaborador.nome duplicado (0 linha(s))
mesmo nome em mais de um colaborador

