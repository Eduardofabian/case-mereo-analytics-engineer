IF OBJECT_ID('marts.vw_score_area', 'V') IS NOT NULL DROP VIEW marts.vw_score_area;
GO

-- R11: score direto (so elegiveis da propria area) e consolidado (elegiveis da area
-- mais tudo que fica abaixo dela na hierarquia, via area_descendentes)
CREATE VIEW marts.vw_score_area AS
WITH direto AS (
    SELECT dc.id_area, AVG(sc.score) AS score_direto
    FROM marts.dim_colaborador dc
    JOIN marts.vw_score_colaborador sc ON sc.id_colaborador = dc.id_colaborador
    WHERE dc.flag_elegivel_r10 = 1
    GROUP BY dc.id_area
),
consolidado AS (
    SELECT ad.id_area_ancestral AS id_area, AVG(sc.score) AS score_consolidado
    FROM intermediate.area_descendentes ad
    JOIN marts.dim_colaborador dc ON dc.id_area = ad.id_area_descendente
    JOIN marts.vw_score_colaborador sc ON sc.id_colaborador = dc.id_colaborador
    WHERE dc.flag_elegivel_r10 = 1
    GROUP BY ad.id_area_ancestral
)
SELECT
    da.id_area,
    d.score_direto,
    c.score_consolidado
FROM marts.dim_area da
LEFT JOIN direto d ON d.id_area = da.id_area
LEFT JOIN consolidado c ON c.id_area = da.id_area;
GO