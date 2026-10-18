IF OBJECT_ID('intermediate.meta_resolvida', 'V') IS NOT NULL DROP VIEW intermediate.meta_resolvida;
GO

-- R7: meta Compartilhada usa polaridade, acumulacao e lancamentos da meta referenciada
-- (o peso continua sendo o da propria meta compartilhada).
-- sem filtro de ciclo aqui de proposito: R1 e regra de consumo, nao de resolucao de meta.
-- quem filtra ciclo 2025 e quem usa essa view (intermediate.vw_nota_meta).
CREATE VIEW intermediate.meta_resolvida AS
SELECT
    m.id_meta,
    m.id_ciclo,
    m.id_colaborador,
    m.nome_meta,
    m.tipo_meta,
    m.id_meta_referencia,
    COALESCE(ref.polaridade, m.polaridade)             AS polaridade_efetiva,
    COALESCE(ref.tipo_acumulacao, m.tipo_acumulacao)   AS tipo_acumulacao_efetiva,
    CASE WHEN m.tipo_meta = 'Compartilhada'
         THEN m.id_meta_referencia
         ELSE m.id_meta
    END                                                 AS id_meta_lancamentos,
    ABS(m.peso)                                         AS peso_efetivo   -- achado: 1 meta com peso negativo
FROM staging.meta AS m
LEFT JOIN staging.meta AS ref
       ON ref.id_meta = m.id_meta_referencia;
GO