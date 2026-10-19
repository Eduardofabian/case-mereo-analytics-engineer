/* ============================================================================
   VERIFICAÇÃO INDEPENDENTE — SQL Server (banco CaseMereo)

   Recalcula P1/P2/P3 lendo APENAS staging.* (nenhuma view de intermediate/
   marts é usada no cálculo) e só no final compara com marts.*. Mesma lógica
   do etl/verificacao_independente.py (que bate com os CSVs com diff 0.0000).

   Rodar o script inteiro no SSMS (Ctrl+E). Resultados:
     1) contagens de staging  2) resumo PASS/FAIL  3) divergências (vazio = ok)

   Critério de PASS: |diff| <= 0.005 (mesma tolerância do script Python).
   ============================================================================ */
USE CaseMereo;
GO
SET NOCOUNT ON;

/* ---------- limpeza de temporárias (compatível com versões antigas) -------- */
IF OBJECT_ID('tempdb..#lanc')   IS NOT NULL DROP TABLE #lanc;
IF OBJECT_ID('tempdb..#meta')   IS NOT NULL DROP TABLE #meta;
IF OBJECT_ID('tempdb..#nota')   IS NOT NULL DROP TABLE #nota;
IF OBJECT_ID('tempdb..#score')  IS NOT NULL DROP TABLE #score;
IF OBJECT_ID('tempdb..#elig')   IS NOT NULL DROP TABLE #elig;
IF OBJECT_ID('tempdb..#desc')   IS NOT NULL DROP TABLE #desc;
IF OBJECT_ID('tempdb..#v_p1')   IS NOT NULL DROP TABLE #v_p1;
IF OBJECT_ID('tempdb..#v_p2')   IS NOT NULL DROP TABLE #v_p2;
IF OBJECT_ID('tempdb..#v_p3')   IS NOT NULL DROP TABLE #v_p3;

/* ---------- R2 + R3: lançamentos --------------------------------------------
   R2: por (id_meta, mes) vale o data_lancamento mais recente (desempate: maior
       id_lancamento). A deduplicação vem ANTES do filtro de R3.
   R3: conta se nao_se_aplica = 0 E previsto e realizado preenchidos.        */
SELECT id_meta, mes,
       CAST(previsto  AS FLOAT) AS previsto,
       CAST(realizado AS FLOAT) AS realizado
INTO #lanc
FROM (
    SELECT l.*,
           ROW_NUMBER() OVER (PARTITION BY l.id_meta, l.mes
                              ORDER BY l.data_lancamento DESC, l.id_lancamento DESC) AS rn
    FROM staging.meta_valor_mensal l
) x
WHERE x.rn = 1
  AND x.nao_se_aplica = 0
  AND x.previsto  IS NOT NULL
  AND x.realizado IS NOT NULL;

/* ---------- R1 + R7: metas do ciclo 2025 -------------------------------------
   Compartilhada usa lançamentos/polaridade/acumulação da meta referenciada;
   o peso é da própria meta. Peso negativo -> ABS (decisão documentada).     */
SELECT m.id_meta,
       m.id_colaborador,
       ABS(CAST(m.peso AS FLOAT)) AS peso,
       r.id_meta                  AS id_lanc,
       LTRIM(RTRIM(r.polaridade))      AS polaridade,
       LTRIM(RTRIM(r.tipo_acumulacao)) AS tipo_acumulacao
INTO #meta
FROM staging.meta m
JOIN staging.meta r
  ON r.id_meta = CASE WHEN m.tipo_meta = 'Compartilhada' THEN m.id_meta_referencia
                      ELSE m.id_meta END
WHERE m.id_ciclo = 2025;

/* ---------- R4 + R5 + R6 + R8: atingimento e nota por meta ------------------
   Razão mensal: cima = realizado/previsto ; baixo = previsto/realizado
   (denominador 0 -> NULL).
   Soma  : razão calculada sobre soma(realizado) e soma(previsto).
   Média : média das razões mensais (AVG ignora NULL).
   Meta sem mês que conta não aparece no GROUP BY (R8).                       */
;WITH mes AS (
    SELECT m.id_meta, m.peso, m.id_colaborador, m.polaridade, m.tipo_acumulacao,
           l.previsto, l.realizado,
           CASE WHEN m.polaridade = 'Melhor para cima'
                THEN l.realizado / NULLIF(l.previsto,  0)
                ELSE l.previsto  / NULLIF(l.realizado, 0) END AS razao_mes
    FROM #meta m
    JOIN #lanc l ON l.id_meta = m.id_lanc
),
ating AS (
    SELECT id_meta, id_colaborador, peso,
           CASE WHEN MAX(tipo_acumulacao) = 'Soma' THEN
                    CASE WHEN MAX(polaridade) = 'Melhor para cima'
                         THEN SUM(realizado) / NULLIF(SUM(previsto),  0)
                         ELSE SUM(previsto)  / NULLIF(SUM(realizado), 0) END
                ELSE AVG(razao_mes) END AS atingimento
    FROM mes
    GROUP BY id_meta, id_colaborador, peso
)
SELECT id_meta, id_colaborador, peso, atingimento,
       CASE WHEN atingimento IS NULL THEN NULL
            WHEN atingimento < 0.8   THEN 0.0
            WHEN atingimento <= 1.2  THEN atingimento * 100.0
            ELSE 120.0 END AS nota
INTO #nota
FROM ating;

/* ---------- R9: score do colaborador (só metas com nota) ------------------- */
SELECT id_colaborador,
       SUM(nota * peso) / NULLIF(SUM(peso), 0) AS score
INTO #score
FROM #nota
WHERE nota IS NOT NULL
GROUP BY id_colaborador;

/* ---------- R10: elegibilidade ---------------------------------------------- */
SELECT c.id_colaborador, c.id_area, c.id_gestor, c.data_desligamento
INTO #elig
FROM staging.colaborador c
WHERE c.data_admissao <= '2025-09-30'
  AND (c.data_desligamento IS NULL OR c.data_desligamento >= '2025-07-01');

/* ---------- R11: descendentes de cada área (inclui a própria) -------------- */
;WITH h AS (
    SELECT id_area AS raiz, id_area AS id_area FROM staging.area
    UNION ALL
    SELECT h.raiz, a.id_area
    FROM h JOIN staging.area a ON a.id_area_pai = h.id_area
)
SELECT raiz, id_area INTO #desc FROM h;

/* ============================== RESULTADOS INDEPENDENTES ================== */
-- P1
SELECT e.id_colaborador, s.score
INTO #v_p1
FROM #elig e JOIN #score s ON s.id_colaborador = e.id_colaborador;

-- P2
SELECT a.id_area,
       (SELECT AVG(s.score) FROM #elig e JOIN #score s ON s.id_colaborador = e.id_colaborador
         WHERE e.id_area = a.id_area)                                   AS score_direto,
       (SELECT AVG(s.score) FROM #elig e JOIN #score s ON s.id_colaborador = e.id_colaborador
         WHERE e.id_area IN (SELECT d.id_area FROM #desc d WHERE d.raiz = a.id_area)) AS score_consolidado
INTO #v_p2
FROM staging.area a;

-- P3: gestor ativo em 31/12/2025 (sem desligamento ou desligado depois) e
--     >= 3 subordinados diretos elegíveis (com score)
SELECT e.id_gestor, AVG(s.score) AS score_medio_time, COUNT(*) AS n_sub
INTO #v_p3
FROM #elig e
JOIN #score s ON s.id_colaborador = e.id_colaborador
JOIN staging.colaborador g ON g.id_colaborador = e.id_gestor
WHERE g.data_desligamento IS NULL OR g.data_desligamento > '2025-12-31'
GROUP BY e.id_gestor
HAVING COUNT(*) >= 3;

/* ============================== 1) CONTAGENS ============================== */
SELECT 'staging.area' AS tabela, COUNT(*) AS linhas FROM staging.area
UNION ALL SELECT 'staging.colaborador',        COUNT(*) FROM staging.colaborador
UNION ALL SELECT 'staging.meta',               COUNT(*) FROM staging.meta
UNION ALL SELECT 'staging.meta_valor_mensal',  COUNT(*) FROM staging.meta_valor_mensal
UNION ALL SELECT 'esperado: area=11, colaborador=81, meta=376', NULL;

/* ============================== 2) RESUMO ================================= */
SELECT 'P1 colaboradores elegíveis (independente)'  AS verificacao,
       (SELECT COUNT(*) FROM #v_p1) AS independente,
       (SELECT COUNT(*) FROM marts.dim_colaborador dc
          JOIN marts.vw_score_colaborador sc ON sc.id_colaborador = dc.id_colaborador
         WHERE dc.flag_elegivel_r10 = 1) AS marts,
       CAST(NULL AS FLOAT) AS max_abs_diff, CAST(NULL AS VARCHAR(10)) AS resultado
UNION ALL
SELECT 'P1 score: maior |diff|', NULL, NULL,
       (SELECT MAX(ABS(CAST(v.score AS FLOAT) - CAST(sc.score AS FLOAT)))
          FROM #v_p1 v JOIN marts.vw_score_colaborador sc ON sc.id_colaborador = v.id_colaborador),
       CASE WHEN (SELECT COUNT(*) FROM #v_p1 v
                    LEFT JOIN marts.vw_score_colaborador sc ON sc.id_colaborador = v.id_colaborador
                   WHERE sc.id_colaborador IS NULL
                      OR ABS(CAST(v.score AS FLOAT) - CAST(sc.score AS FLOAT)) > 0.005) = 0
             THEN 'PASS' ELSE 'FAIL' END
UNION ALL
SELECT 'P2 áreas', (SELECT COUNT(*) FROM #v_p2), (SELECT COUNT(*) FROM marts.vw_score_area), NULL, NULL
UNION ALL
SELECT 'P2 score_direto + consolidado: maior |diff|', NULL, NULL,
       (SELECT MAX(d) FROM (
            SELECT ABS(CAST(v.score_direto AS FLOAT) - CAST(m.score_direto AS FLOAT)) AS d
              FROM #v_p2 v JOIN marts.vw_score_area m ON m.id_area = v.id_area
            UNION ALL
            SELECT ABS(CAST(v.score_consolidado AS FLOAT) - CAST(m.score_consolidado AS FLOAT))
              FROM #v_p2 v JOIN marts.vw_score_area m ON m.id_area = v.id_area) t),
       CASE WHEN (SELECT COUNT(*) FROM #v_p2 v
                    LEFT JOIN marts.vw_score_area m ON m.id_area = v.id_area
                   WHERE m.id_area IS NULL
                      OR ABS(CAST(v.score_direto AS FLOAT) - CAST(m.score_direto AS FLOAT)) > 0.005
                      OR ABS(CAST(v.score_consolidado AS FLOAT) - CAST(m.score_consolidado AS FLOAT)) > 0.005) = 0
             THEN 'PASS' ELSE 'FAIL' END
UNION ALL
SELECT 'P3 gestores válidos (esperado 9)', (SELECT COUNT(*) FROM #v_p3), (SELECT COUNT(*) FROM marts.vw_score_gestor), NULL,
       CASE WHEN (SELECT COUNT(*) FROM #v_p3) = (SELECT COUNT(*) FROM marts.vw_score_gestor) THEN 'PASS' ELSE 'FAIL' END
UNION ALL
SELECT 'P3 score_medio_time: maior |diff|', NULL, NULL,
       (SELECT MAX(ABS(CAST(v.score_medio_time AS FLOAT) - CAST(m.score_medio_time AS FLOAT)))
          FROM #v_p3 v JOIN marts.vw_score_gestor m ON m.id_gestor = v.id_gestor),
       CASE WHEN (SELECT COUNT(*) FROM #v_p3 v
                    LEFT JOIN marts.vw_score_gestor m ON m.id_gestor = v.id_gestor
                   WHERE m.id_gestor IS NULL
                      OR ABS(CAST(v.score_medio_time AS FLOAT) - CAST(m.score_medio_time AS FLOAT)) > 0.005) = 0
             THEN 'PASS' ELSE 'FAIL' END;

/* ============================== 3) DIVERGÊNCIAS (vazio = tudo certo) ====== */
SELECT 'P1' AS nivel, v.id_colaborador AS id, v.score AS independente, sc.score AS marts
FROM #v_p1 v LEFT JOIN marts.vw_score_colaborador sc ON sc.id_colaborador = v.id_colaborador
WHERE sc.id_colaborador IS NULL OR ABS(CAST(v.score AS FLOAT) - CAST(sc.score AS FLOAT)) > 0.005;

SELECT 'P2' AS nivel, v.id_area AS id,
       v.score_direto AS direto_indep, m.score_direto AS direto_marts,
       v.score_consolidado AS consol_indep, m.score_consolidado AS consol_marts
FROM #v_p2 v LEFT JOIN marts.vw_score_area m ON m.id_area = v.id_area
WHERE m.id_area IS NULL
   OR ABS(CAST(v.score_direto AS FLOAT) - CAST(m.score_direto AS FLOAT)) > 0.005
   OR ABS(CAST(v.score_consolidado AS FLOAT) - CAST(m.score_consolidado AS FLOAT)) > 0.005;

SELECT 'P3' AS nivel, COALESCE(v.id_gestor, m.id_gestor) AS id,
       v.score_medio_time AS independente, m.score_medio_time AS marts
FROM #v_p3 v FULL OUTER JOIN marts.vw_score_gestor m ON m.id_gestor = v.id_gestor
WHERE v.id_gestor IS NULL OR m.id_gestor IS NULL
   OR ABS(CAST(v.score_medio_time AS FLOAT) - CAST(m.score_medio_time AS FLOAT)) > 0.005;
