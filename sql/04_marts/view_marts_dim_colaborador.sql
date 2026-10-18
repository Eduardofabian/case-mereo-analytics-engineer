IF OBJECT_ID('marts.dim_colaborador', 'V') IS NOT NULL DROP VIEW marts.dim_colaborador;
GO

-- flag_elegivel_r10: R10, admitido ate 30/09/2025 e nao desligado antes de 01/07/2025
-- flag_ativo_fim_2025: nao e R10, e o criterio de P3 (gestor ativo em 31/12/2025)
CREATE VIEW marts.dim_colaborador AS
SELECT
    c.id_colaborador,
    c.nome,
    c.id_area,
    c.id_gestor,
    c.data_admissao,
    c.data_desligamento,
    CASE
        WHEN c.data_admissao <= '2025-09-30'
         AND (c.data_desligamento IS NULL OR c.data_desligamento >= '2025-07-01')
        THEN 1 ELSE 0
    END AS flag_elegivel_r10,
    CASE
        WHEN c.data_desligamento IS NULL OR c.data_desligamento > '2025-12-31'
        THEN 1 ELSE 0
    END AS flag_ativo_fim_2025
FROM staging.colaborador AS c;
GO