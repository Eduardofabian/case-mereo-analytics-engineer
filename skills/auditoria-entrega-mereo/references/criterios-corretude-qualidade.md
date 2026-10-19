# Critério 1 — Corretude dos números (30%, o mais pesado) e
# Critério 2 — Problemas de qualidade (20%)

Juntos somam 50% da nota — metade da avaliação depende só destes dois.
Auditar primeiro e com mais rigor do que os demais.

## Critério 1 — Corretude dos números (30%)

- `respostas/p1_score_colaborador.csv`, `p2_score_area.csv`,
  `p3_gestores.csv` existem e têm conteúdo real (não vazios, não headers
  soltos).
- `etl/verificacao_independente.py` (ou caminho equivalente após
  reorganização) existe e reimplementa R1–R11 **sem usar nenhuma view do
  projeto** — reimplementação independente em pandas direto do SQLite
  original é o padrão esperado. Se o script importar de `sql/` ou reusar
  uma view de `marts`, a verificação não é independente de verdade e isso
  é um gap grave, porque anula o próprio propósito do script.
- Se o ambiente permitir rodar: `python etl/verificacao_independente.py`
  (ou caminho atualizado) precisa do `material_original/dados/case_metas.db`
  presente — confirme antes que ele não foi apagado por engano via
  `.gitignore` malconfigurado (já aconteceu neste projeto com
  `agente/dados/*.csv`, ver nota de processo no README). Resultado
  esperado: diferença máxima 0.0000 entre pandas e os CSVs de
  `respostas/`.
- Confira as regras de negócio aplicadas contra o texto literal do
  enunciado, regra por regra, não contra uma paráfrase do README. Atenção
  redobrada em:
  - R6 (corte 80%/120%) — erro comum é aplicar o corte antes de
    multiplicar por 100, ou aplicar só o teto sem o piso.
  - R7 (meta compartilhada usa lançamento/polaridade/acumulação da
    meta referenciada, mas o **peso é da própria meta compartilhada**) —
    erro comum é herdar o peso também, inflando ou reduzindo o score.
  - R10 (elegibilidade: admitido até 30/09/2025 E não desligado antes de
    01/07/2025) — confira as duas condições, não só uma.
  - R11 (score direto vs. consolidado) — confira que o painel/CSV deixa
    explícito qual dos dois está sendo mostrado quando a área tem
    subárea; "só um número" sem rótulo é ambíguo.
- Nos 3 filtros de P3 (gestor ativo em 31/12/2025 + ≥3 subordinados
  diretos elegíveis), confirme que os filtros foram aplicados
  literalmente (contagem exata de subordinados diretos elegíveis, não
  aproximada por "parece que tem bastante gente").

## Critério 2 — Problemas de qualidade (20%)

- O relatório de achados (`qualidade/relatorio_diagnostico.md` ou
  caminho atualizado após reorganização) existe e lista achados com
  contagem real (não "vários problemas encontrados" sem número).
- Cada achado tem uma decisão de tratamento justificada, não só
  descrita. "Decisão: X" sem explicar por que X e não Y é meio ponto,
  não ponto cheio — e pesa mais aqui do que em outro processo, ver
  `contexto-mereo.md` sobre o valor "Excelência".
- Cruze os achados contra os dados reais quando possível: se o relatório
  diz "N lançamentos duplicados", confirme que esse número aparece
  também no README de forma consistente (inconsistência entre os dois
  documentos pesa mais do que o número em si estar certo ou errado).
- Verifique se há análise de sensibilidade para decisões que mantiveram
  dado "sujo" no cálculo (ex.: lançamento pós-desligamento mantido
  literal) — decisão sem medir o impacto numérico é decisão não testada,
  reporte como gap mesmo que a decisão em si seja razoável.
- Lembre que a Mereo já tem um painel interno de qualidade de dados no
  próprio produto (o "Dashboard Analytics" do módulo Metas, com % de
  metas sem peso/valor previsto/ação cadastrada) — um relatório de
  qualidade bem estruturado aqui não é um exercício abstrato, é
  literalmente o tipo de output que o cargo produz no dia a dia. Falta de
  estrutura ou de número aqui é mais notável para quem já viu o padrão
  real da empresa.
