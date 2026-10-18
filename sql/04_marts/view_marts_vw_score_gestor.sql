IF OBJECT_ID('marts.vw_score_gestor', 'V') IS NOT NULL DROP VIEW marts.vw_score_gestor;
GO

-- score medio do time direto por gestor, ja com os dois filtros do enunciado de P3:
-- gestor ativo em 31/12/2025 e pelo menos 3 subordinados diretos elegiveis.
-- diferente de vw_score_colaborador, esses filtros ficam dentro da view, porque aqui
-- eles definem o que conta como "gestor valido pro ranking", nao so quem aparece.
CREATE VIEW marts.vw_score_gestor AS
SELECT
    g.id_colaborador AS id_gestor,
    AVG(sc.score)     AS score_medio_time,
    COUNT(*)          AS n_subordinados_diretos_elegiveis
FROM marts.dim_colaborador g
JOIN marts.dim_colaborador sub ON sub.id_gestor = g.id_colaborador
JOIN marts.vw_score_colaborador sc ON sc.id_colaborador = sub.id_colaborador
WHERE sub.flag_elegivel_r10 = 1
  AND g.flag_ativo_fim_2025 = 1
GROUP BY g.id_colaborador
HAVING COUNT(*) >= 3;
GO