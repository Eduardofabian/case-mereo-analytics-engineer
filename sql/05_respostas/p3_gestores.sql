-- gera respostas/p3_gestores.csv — colunas: grupo,posicao,id_gestor,score_medio_time
-- filtros de P3 ja ficam resolvidos em vw_score_gestor, aqui so ranqueia e empacota
-- no formato pedido
WITH ranked AS (
    SELECT id_gestor, score_medio_time,
           ROW_NUMBER() OVER (ORDER BY score_medio_time DESC) AS rn_top,
           ROW_NUMBER() OVER (ORDER BY score_medio_time ASC)  AS rn_bottom
    FROM marts.vw_score_gestor
)
SELECT 'top' AS grupo, rn_top AS posicao, id_gestor,
       CAST(ROUND(score_medio_time, 2) AS DECIMAL(10,2)) AS score_medio_time
FROM ranked WHERE rn_top <= 3

UNION ALL

SELECT 'bottom' AS grupo, rn_bottom AS posicao, id_gestor,
       CAST(ROUND(score_medio_time, 2) AS DECIMAL(10,2)) AS score_medio_time
FROM ranked WHERE rn_bottom <= 3

ORDER BY grupo DESC, posicao ASC;