# Achados de qualidade — Chat 1 (Engenharia de Dados)

Nota sobre como isso foi produzido: este sandbox não tem acesso ao SQL Server
que você instalou localmente (nem a um shell remoto na sua máquina — só a
leitura/escrita de arquivos). Não rodei nada contra o SQL Server de fato.
Toda a lógica abaixo foi construída e validada em Python/pandas aqui, direto
sobre os CSVs, e o SQL entregue em `sql/` é a tradução 1:1 dessa mesma lógica
em T-SQL para você rodar no seu ambiente (SSMS/VS Code). Os números do
P1/P2/P3 batem com o que o SQL deveria produzir, mas a correção dos arquivos
.sql em si (sintaxe, performance no SQL Server real) ainda depende de você
rodar `etl/load.py` localmente — eu não validei isso executando.

## Achados confirmados da varredura anterior

1. **45 pares (id_meta, mês) com lançamento duplicado** (90 registros).
   R2 resolve: mantido o de `data_lancamento` mais recente. Confirmado: não
   há empates de data entre os duplicados.

2. **43 lançamentos com `nao_se_aplica=0` mas `previsto`/`realizado` nulo.**
   R3 já exclui esses meses do cálculo. Mantidos no staging, descartados só
   no cálculo de atingimento.

3. **Meta 5094 (colaborador 125, "Leads gerados"), previsto=0 nos 12 meses
   de 2025** (Soma, Melhor para cima) → divisão por zero em R4.
   Decisão: tratar como R8 (sem nota, exclui do score).

4. **Meta 5286 (colaborador 174, "Inadimplência (%)"), peso=-5.**
   Nenhuma regra prevê peso negativo (inverteria o incentivo). Decisão:
   peso_efetivo = ABS(peso).

## Achados novos (não estavam na varredura anterior)

5. **5 metas Compartilhadas com lançamento mensal próprio inesperado**
   (ids 5066, 5156, 5219, 5231, 5278) — 60 registros no total. R7 é
   explícito: meta compartilhada usa os lançamentos **da referência**, não
   os próprios. Esses 5 casos têm `previsto=100` fixo em todos os meses e
   `realizado` variando, como se alguém tivesse carregado um "% de
   atingimento" pré-calculado direto na tabela de lançamentos — mas isso
   não é o que R7 pede. Decisão: esses lançamentos próprios foram
   **ignorados por completo** no cálculo; apenas os lançamentos da meta de
   referência contam. Vale confirmar com quem gerou a base se isso foi
   engano de carga ou se há uma regra não documentada aqui.

6. **4 metas Individuais do ciclo 2025 sem nenhum lançamento mensal**
   (ids 5014, 5063, 5146, 5188) — zero linhas em `meta_valor_mensal`, não
   apenas linhas inválidas. Diferente do achado #2 (que tem lançamento mas
   inválido). R8 cobre o caso (sem nota, fora do score), mas é bom deixar
   registrado: essas metas nunca tiveram lançamento algum, nem inválido.

7. **Mesmo problema de denominador zero do achado #3, generalizado:**
   qualquer meta com soma(previsto)=0 em Acumulação Soma, ou com um mês de
   previsto/realizado=0 no denominador em Acumulação Média, teria
   atingimento indefinido. Na base atual só a meta 5094 cai nesse caso, mas
   a regra de tratamento (R8) foi aplicada de forma genérica no SQL/Python,
   não só para esse id específico — então um dado novo com o mesmo
   problema já cairia no mesmo tratamento automaticamente.

8. **7 colaboradores com soma de peso das metas != 100** (variando entre 85
   e 120). Não quebra o cálculo (R9 já normaliza por soma de peso, não
   assume 100), mas é bom não assumir no painel/agente que peso sempre soma
   100.

## Checagens feitas sem achado adicional

PK duplicada (nenhuma tabela), FK órfã (colaborador→área, colaborador→
gestor, meta→colaborador, lançamento→meta — todas limpas), ciclo na
hierarquia de gestores (nenhum), auto-gestor, área pai órfã, datas de
desligamento anteriores à admissão, mês fora de 1–12, variação de grafia em
polaridade/tipo_acumulacao/tipo_meta (só os 2 valores esperados em cada
coluna, sem espaço/maiúscula inconsistente).

## Elegibilidade (R10) — números de referência

81 colaboradores no total, **72 elegíveis**, 9 inelegíveis (5 desligados
antes de 01/07/2025, 2 admitidos depois de 30/09/2025, mais 2 que também
caem numa das duas condições). Todos os 72 elegíveis têm pelo menos uma
meta com nota (nenhum caso de score 0/0 nesta base).

## Views de marts — reuso por Dashboard e Agente

`vw_score_colaborador` e `vw_score_area` são a fonte única de score já
pronta (nota, atingimento e score agregados) — Dashboard e Agente de IA só
precisam fazer SELECT/filtro em cima delas, sem recalcular nada. `dim_area`
já traz o nível hierárquico pré-computado (não precisa de recursão de novo
em cada consulta de R11).
