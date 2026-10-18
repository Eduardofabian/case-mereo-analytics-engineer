IF OBJECT_ID('marts.vw_score_colaborador', 'V') IS NOT NULL DROP VIEW marts.vw_score_colaborador;
GO

-- R9: soma(nota x peso) / soma(peso), so metas com nota.
-- calcula pra todo colaborador com meta com nota, elegivel ou nao. R10 nao entra aqui
-- de proposito: score e propriedade do colaborador, elegibilidade e filtro de quem
-- aparece no resultado final (aplicado na query de P1 e na contagem de P3).
CREATE VIEW marts.vw_score_colaborador AS
SELECT
    dm.id_colaborador,
    SUM(nm.nota * dm.peso_efetivo) / NULLIF(SUM(dm.peso_efetivo), 0) AS score
FROM marts.dim_meta dm
JOIN intermediate.vw_nota_meta nm ON nm.id_meta = dm.id_meta
WHERE dm.id_ciclo = 2025
  AND nm.nota IS NOT NULL
GROUP BY dm.id_colaborador;
GO