-- gera respostas/p1_score_colaborador.csv — colunas: id_colaborador,score
-- R10 aplicado aqui: unico lugar nessa consulta que decide quem aparece no resultado final
SELECT
    dc.id_colaborador,
    CAST(ROUND(sc.score, 2) AS DECIMAL(10,2)) AS score
FROM marts.dim_colaborador dc
JOIN marts.vw_score_colaborador sc ON sc.id_colaborador = dc.id_colaborador
WHERE dc.flag_elegivel_r10 = 1
ORDER BY dc.id_colaborador;