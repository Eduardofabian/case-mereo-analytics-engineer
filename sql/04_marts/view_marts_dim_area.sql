IF OBJECT_ID('marts.dim_area', 'V') IS NOT NULL DROP VIEW marts.dim_area;
GO

-- nivel pre-computado via recursao (0 = raiz: Comercial, Operacoes, Financeira),
-- assim ninguem precisa refazer a CTE toda vez que quiser ordenar por hierarquia
CREATE VIEW marts.dim_area AS
WITH raiz AS (
    SELECT id_area, nome, id_area_pai, 0 AS nivel
    FROM staging.area
    WHERE id_area_pai IS NULL
    UNION ALL
    SELECT a.id_area, a.nome, a.id_area_pai, r.nivel + 1
    FROM staging.area AS a
    INNER JOIN raiz AS r ON a.id_area_pai = r.id_area
)
SELECT id_area, nome, id_area_pai, nivel
FROM raiz;
GO