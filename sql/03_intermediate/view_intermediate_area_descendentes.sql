IF OBJECT_ID('intermediate.area_descendentes', 'V') IS NOT NULL DROP VIEW intermediate.area_descendentes;
GO

-- fechamento de hierarquia: pra cada area, todas as areas abaixo dela em qualquer
-- profundidade, incluindo ela mesma (distancia 0). Usado no score consolidado (R11)
-- e reutilizavel pelo agente de IA depois, tipo "quais areas ficam sob a Comercial".
CREATE VIEW intermediate.area_descendentes AS
WITH closure AS (
    SELECT id_area AS id_area_ancestral, id_area AS id_area_descendente, 0 AS distancia
    FROM staging.area
    UNION ALL
    SELECT c.id_area_ancestral, a.id_area, c.distancia + 1
    FROM closure c
    JOIN staging.area a ON a.id_area_pai = c.id_area_descendente
)
SELECT id_area_ancestral, id_area_descendente, distancia
FROM closure;
GO