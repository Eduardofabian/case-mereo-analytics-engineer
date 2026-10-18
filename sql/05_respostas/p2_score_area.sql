-- gera respostas/p2_score_area.csv — colunas: id_area,score_direto,score_consolidado
-- elegibilidade ja fica resolvida dentro de vw_score_area
SELECT
    id_area,
    CAST(ROUND(score_direto, 2)      AS DECIMAL(10,2)) AS score_direto,
    CAST(ROUND(score_consolidado, 2) AS DECIMAL(10,2)) AS score_consolidado
FROM marts.vw_score_area
ORDER BY id_area;