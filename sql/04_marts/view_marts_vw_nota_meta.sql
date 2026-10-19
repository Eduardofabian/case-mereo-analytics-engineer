IF OBJECT_ID('marts.vw_nota_meta', 'V') IS NOT NULL DROP VIEW marts.vw_nota_meta;
GO

-- R4, R5, R6: atingimento e nota por meta. So olha ciclo 2025 (R1) e lancamento valido.
-- meta com denominador zero (achado: meta 5094, previsto=0 o ano inteiro) ou sem
-- nenhum mes valido cai em R8, nota NULL, nao em erro.
CREATE VIEW marts.vw_nota_meta AS
WITH lanc AS (
    SELECT dm.id_meta, dm.polaridade_efetiva, dm.tipo_acumulacao_efetiva,
           f.mes, f.previsto, f.realizado
    FROM marts.dim_meta dm
    JOIN marts.fact_meta_valor_mensal f ON f.id_meta = dm.id_meta_lancamentos
    WHERE f.flag_valido = 1
      AND dm.id_ciclo = 2025
),
mensal AS (
    SELECT *,
        CASE
            WHEN polaridade_efetiva = 'Melhor para cima' THEN
                CASE WHEN previsto <> 0 THEN CAST(realizado AS FLOAT) / previsto ELSE NULL END
            ELSE
                CASE WHEN realizado <> 0 THEN CAST(previsto AS FLOAT) / realizado ELSE NULL END
        END AS atingimento_mensal
    FROM lanc
),
agg AS (
    SELECT id_meta,
           MAX(tipo_acumulacao_efetiva) AS tipo_acumulacao_efetiva,
           MAX(polaridade_efetiva)      AS polaridade_efetiva,
           SUM(previsto)                AS soma_previsto,
           SUM(realizado)               AS soma_realizado,
           AVG(atingimento_mensal)      AS media_atingimento_mensal,   -- AVG ignora NULL
           COUNT(*)                     AS n_meses_validos
    FROM mensal
    GROUP BY id_meta
),
ating AS (
    SELECT id_meta, n_meses_validos,
        CASE
            WHEN tipo_acumulacao_efetiva = 'Soma' THEN
                CASE
                    WHEN polaridade_efetiva = 'Melhor para cima' THEN
                        CASE WHEN soma_previsto <> 0 THEN CAST(soma_realizado AS FLOAT)/soma_previsto ELSE NULL END
                    ELSE
                        CASE WHEN soma_realizado <> 0 THEN CAST(soma_previsto AS FLOAT)/soma_realizado ELSE NULL END
                END
            ELSE media_atingimento_mensal
        END AS atingimento
    FROM agg
)
SELECT
    dm.id_meta,
    ISNULL(a.n_meses_validos, 0) AS n_meses_validos,
    a.atingimento,
    CASE
        WHEN a.atingimento IS NULL THEN NULL          -- R8: sem mes valido ou denominador indefinido
        WHEN a.atingimento < 0.8  THEN 0
        WHEN a.atingimento <= 1.2 THEN a.atingimento * 100
        ELSE 120
    END AS nota
FROM marts.dim_meta dm
LEFT JOIN ating a ON a.id_meta = dm.id_meta
WHERE dm.id_ciclo = 2025;
GO