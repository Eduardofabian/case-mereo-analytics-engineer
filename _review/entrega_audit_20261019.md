# Auditoria de Entrega · Case Mereo (Grupo Aurora) · case-mereo-analytics-engineer
> Score estimado: **84/100 — BOM — gaps pontuais, corrigíveis**
> Gerado por `/auditoria-entrega-mereo` em 2026-10-19 (HEAD `6cdb45d`)

---

## Veredicto

Os números da Parte 1 estão sólidos. Rodei `etl/verificacao/verificacao_independente.py` nesta auditoria e P1 (72), P2 (11) e P3 (6) bateram com `respostas/` com diferença máxima de 0.0000. Conferi R6, R7, R10 e R11 no código contra o texto literal do enunciado. Os casos de borda que testei por fora estão limpos: zero empate de `data_lancamento` em R2, previsto 0 só em meta Soma, 81 − 3 − 6 = 72 elegíveis. Nenhum bloqueador.

O que separa o score de "FORTE" são três pontos de precisão, e nenhum deles é de cálculo:

1. Há uma decisão de qualidade não medida (`ABS(peso)`) cujo impacto é **maior** que o do pior caso da decisão que o README mediu com cuidado.
2. O print do painel corta a tabela de áreas, e quem lê não vê a área que responde à pergunta 3 do agente.
3. Sobram caminhos antigos da reorganização no README e nos scripts.

Tudo corrigível em cerca de 2h. Diferenciais da vaga atendidos de forma explícita: Pydantic AI + API Anthropic no agente e Azure Blob Storage + Azure Function na Parte 5.

---

## Score por critério (pesos exatos do enunciado)

| Critério | Peso | Nota estimada | Pontos | Gaps críticos |
|---|---|---|---|---|
| Corretude dos números (Parte 1) | 30% | 9.0/10 | 27.0/30 | 0 |
| Problemas de qualidade | 20% | 8.5/10 | 17.0/20 | 1 |
| Agente de IA | 20% | 8.5/10 | 17.0/20 | 0 |
| Painel | 15% | 7.5/10 | 11.25/15 | 1 |
| Perguntas abertas | 10% | 8.0/10 | 8.0/10 | 0 |
| Organização e README | 5% | 8.0/10 | 4.0/5 | 0 |
| **TOTAL** | **100%** | — | **84/100** | — |

---

## Verificação de reprovação imediata

| Critério | Status |
|---|---|
| `respostas/p1_score_colaborador.csv`, `p2_*`, `p3_*` presentes e com conteúdo | ✅ 72 / 11 / 6 linhas, cabeçalho exato, 2 casas decimais com ponto |
| `etl/verificacao/verificacao_independente.py` existe e é independente (não reusa view) | ✅ lê só `case_metas.db` via `sqlite3`, nenhuma referência a `sql/` ou `marts`; rodado nesta auditoria: 0.0000 |
| Estrutura bate com README.md / sql/ / respostas/ / painel/ / agente/ | ✅ |
| `agente/respostas.md` sem placeholder | ✅ 5 respostas reais + comentário em cada |
| As 3 perguntas abertas respondidas | ✅ |

Nenhum bloqueador.

---

## Gaps por impacto na nota

### Impacto alto (corrigir agora)

**1. `ABS(peso)` é a decisão de maior impacto numérico do case, e é a única sem medição nem alternativa discutida** — Qualidade (20%) · ~30 min

O README justifica só com "inverteria o peso da meta no cálculo". Não diz por que ABS e não excluir a meta 5286 (tratá-la como sem peso válido, no espírito de R8). Medi nesta auditoria com o próprio `verificacao_independente.py`, trocando ABS por exclusão:

| Nível | Com ABS (entregue) | Excluindo meta 5286 | Δ |
|---|---|---|---|
| Colaborador 174 (Quésia Nogueira) | 51.42 | 49.14 | **2.28** |
| Área 11 (direto e consolidado) | — | — | 0.228 |
| Gestor 171 (Sofia Queiroz, **top 1 de P3**) | 102.00 | — | 0.253 |
| Ranking top 3 / bottom 3 de P3 | — | — | inalterado |

2.28 pontos é **maior** que o pior caso da sensibilidade de pós-desligamento (1.64), que ganhou uma seção inteira no README. Um avaliador que lê as duas decisões lado a lado vê rigor aplicado de forma desigual. É o caso de "decisão executada, mas não testada" que `contexto-mereo.md` marca como alta prioridade (valor "Excelência"). A colaboradora 174 também aparece nominalmente na Zona Crítica do painel (51), então o número é visível para a diretoria.

Correção: uma linha a mais na tabela de achados ou um parágrafo curto com: alternativa considerada (excluir), por que ABS (o sinal parece erro de digitação de importação, já que a magnitude 5 é coerente com os outros pesos), impacto medido (tabela acima) e "P3 não muda".

**2. O print do painel corta a tabela de áreas** — Painel (15%) · ~30–45 min

Em `painel/entrega/Mereo_Case_Dashboard_Pwbi.png`, a matriz "Score por Área" tem barra de rolagem: mostra só Comercial e Operações e corta a Gerência de Logística no meio. A **Diretoria Financeira (103.30), melhor consolidado e resposta da pergunta 3 do agente, não aparece**. O print é o entregável que o enunciado pede ("PDF ou print"), e um visual com scroll num print estático é informação que a diretoria não vê. Na mesma tabela:

- os cabeçalhos expõem nomes internos de medida ("Score Direto (Matriz)", "Score Consolidado **Exibir** (Matriz)", "Area Nivel 0");
- há uma linha "Total" sem valor, que não tem significado para score.

Correção: reduzir altura de linha/fonte ou recolher o nível 2 para caber as 3 diretorias e 5 gerências sem scroll, renomear os cabeçalhos para "Direto"/"Consolidado"/"Área", desligar o total e reexportar o print. Se possível, exportar também em PDF ("Arquivo → Exportar → PDF"), que é o formato citado primeiro no enunciado.

### Impacto médio (corrigir se houver tempo)

**3. Parte 5, pergunta 1: a frase final descreve o projeto de forma imprecisa** — Perguntas (10%) · ~5 min

"staging alimenta as views de intermediate e marts via stored procedure ou task agendada." O projeto não tem stored procedure nem agendamento: são views orquestradas por `etl/run_pipeline.py`. Como a frase diz que isso "já está validada na prática", fica uma afirmação verificável e falsa. Trocar por "via `etl/run_pipeline.py` (hoje manual; em produção, disparado pela própria Function ou por um agendador)". Opcional: citar `diag_qualidade.py` como o conjunto de regras que a Function de validação reaproveitaria, o que amarra a resposta ao case.

**4. Parte 5, pergunta 3: faltam as causas prováveis específicas deste modelo** — Perguntas (10%) · ~10 min

A resposta é boa no processo (conversar com o RH antes, `verificacao_independente.py` depois), mas não nomeia as três divergências mais prováveis *neste* case, que são as primeiras coisas que um avaliador da Mereo checaria:

- planilha usando Consolidado e painel mostrando Direto, ou o contrário (R11);
- planilha incluindo colaboradores que R10 exclui (9 dos 81);
- média ponderada por peso em vez de média simples de scores na área.

Cabe numa frase, dentro do limite de 10 linhas.

**5. Tool `listar_colaboradores_time_por_score` não filtra elegibilidade R10** — Agente (20%) · ~10 min

`vw_score_colaborador` tem score para os 81 colaboradores, inclusive os 9 não elegíveis, e a tool lista todos (só marca `elegivel_r10`). Testado: "time da Karina Oliveira abaixo de 90" devolveria Gustavo Esteves (33.72, **não elegível**). Para a Sofia Oliveira (pergunta 2) não muda nada, porque os 3 retornados são elegíveis, então a resposta entregue está certa. O risco é a próxima pergunta. Correção: `AND dc.flag_elegivel_r10 = 1` na query, ou documentar a escolha.

**6. Comentário da pergunta 1 em `agente/respostas.md` ficou ilegível e desatualizado** — Agente (20%) · ~10 min

O comentário foi escrito sem acentos, então a frase-chave virou *"'Gerencia' nunca batia com 'Gerencia'"*, que o avaliador lê como contradição. Termina ainda com "devia estar no README", mas já está (seção "Limitações conhecidas"). Corrigir no dict `COMENTARIOS` de `run_perguntas.py` (fonte do texto) e regenerar, ou editar os dois.

### Impacto baixo (nice to have / diferencial da vaga não atendido)

**7. Caminhos antigos que sobraram da reorganização** — Organização (5%) · ~10 min

O grep de validação do commit 4 procurou só `qualidade/`. Ainda há:
- `README.md:292` → `etl/sensibilidade_matriz.py` (atual: `etl/verificacao/`)
- `README.md:302` → `etl/verificacao_independente.py` (atual: `etl/verificacao/`)
- `etl/verificacao/verificacao_independente.py:9` e `etl/verificacao/sensibilidade_matriz.py:1-2` (docstrings de uso)
- `painel/streamlit/prototipo_streamlit.py:21` → `streamlit run painel/prototipo_streamlit.py`
- `verificar_ambiente.py:5,144` → `painel/prototipo_streamlit.py`

São justamente os scripts que o README manda o avaliador rodar.

**8. `painel/dados/*.csv` está no `.gitignore`, mas 7 arquivos seguem rastreados** — Organização (5%) · ~5 min

O `.gitignore` (linha 44) diz "ignorado de propósito", mas os 7 CSVs já estavam no índice e continuam versionados, enquanto `vw_nota_meta.csv`, que só existe localmente, ficou de fora. Escolher um lado. Manter versionado é defensável, porque permite abrir o `.pbip` sem rodar o pipeline. Nesse caso, remover a regra e o comentário. Do contrário, `git rm --cached painel/dados/*.csv`.

**9. Status `sem_score` declarado, mas inalcançável com os dados atuais** — Agente (20%) · ~5 min

Zero colaboradores sem score em `vw_score_colaborador`. Os outros três status foram testados nesta auditoria e funcionam: `nao_encontrado` ("Vendas Oeste"), `multiplos_candidatos` ("Oliveira") e `nao_atende_criterio_gestor` ("Nicolas Duarte"). Basta uma linha no `agente/README` dizendo que `sem_score` é defensivo (dado novo sem meta com nota), não um caso exercitado.

**10. Modelo default do agente** — Agente · ~2 min

`agent.py` usa `anthropic:claude-sonnet-5` como default. O `agente/README` já documenta o override via `MEREO_AGENT_MODEL`, mas vale confirmar que o default resolve na API, já que é a primeira coisa que quebra para quem roda sem ler o README.

**11. A explicação da escolha do painel está diluída** — Painel (15%) · ~10 min

O enunciado pede "explique a escolha em poucas linhas". A justificativa existe e é boa (5 blocos, o que ficou de fora e por quê, o caso Olívia Queiroz), mas está dentro de uma narrativa de processo em 3 etapas. Um parágrafo de 4–5 linhas logo no início da seção "Painel", com "o que mostra e por quê", atende o pedido literal antes da história do processo.

---

## Pontos que sustentam a nota (não mexer)

- Terminologia do enunciado usada com precisão (polaridade, atingimento, elegibilidade, direto/consolidado), sem paráfrase.
- R7 no código: `peso_ef` vem da própria meta, e lançamentos, polaridade e acumulação vêm da referência, exatamente como o enunciado diz.
- Sensibilidade de pós-desligamento com 4 definições, pior caso reportado primeiro, e a correção da versão anterior (owner → holder) assumida no texto.
- Painel com semáforo verde/amarelo/vermelho e matriz hierárquica Direto/Consolidado, o padrão "Árvore de Performance" do produto.
- Agente com ferramentas fixas, enums mapeados para fragmentos de SQL fixos e nomes via placeholder. A pergunta 5 não alucina.
- 11 commits organizados por frente, não um commit único.

---

## Checklist final antes de submeter

**Corretude (30%)**
- [x] `verificacao_independente.py` reimplementa R1-R11 sem reusar view do projeto
- [x] Diferença 0.0000 confirmada entre pandas e os 3 CSVs de resposta (rodado em 2026-10-19)
- [x] R6, R7, R10, R11 conferidos linha a linha contra o enunciado

**Qualidade (20%)**
- [x] Relatório de achados com contagem numérica real, não vago
- [ ] Toda decisão de tratamento tem justificativa, não só descrição. **Falta: `ABS(peso)` (gap 1)**
- [ ] Análise de sensibilidade para decisões que mantiveram dado "sujo". **Falta: `ABS(peso)` (gap 1)**

**Agente de IA (20%)**
- [x] Ferramentas fixas parametrizadas, sem SQL livre
- [x] `respostas.md` com as 5 respostas e comentários reais, sem placeholder (ajustar o comentário da pergunta 1, gap 6)
- [x] Testado com nome inexistente, sem alucinação

**Painel (15%)**
- [x] PDF/print + fonte, ambos presentes
- [x] Uma página só
- [ ] Print legível por completo. **Falta: matriz de áreas cortada (gap 2)**
- [x] Justificativa da escolha do que mostrar, por escrito (destacar, gap 11)

**Perguntas abertas (10%)**
- [x] 3 respostas, até 10 linhas cada (~9–10 linhas a 100 colunas, no limite)
- [x] Cada resposta usa exemplo concreto deste projeto (corrigir a afirmação da pergunta 1, gap 3)

**Organização e README (5%)**
- [x] Estrutura de pastas conforme pedido
- [x] README cobre decisões, qualidade, uso de IA, Parte 5, pendências ("Limitações conhecidas")
- [ ] Comando de reprodução documentado e testado. **Caminhos antigos em README e docstrings (gap 7)**

---

## Como re-auditar

```
claude "/auditoria-entrega-mereo"
```

---

*Case Mereo (Grupo Aurora) · /auditoria-entrega-mereo v2.0*
