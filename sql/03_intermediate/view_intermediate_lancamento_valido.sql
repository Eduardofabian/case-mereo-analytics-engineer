IF OBJECT_ID('intermediate.lancamento_valido', 'V') IS NOT NULL DROP VIEW intermediate.lancamento_valido;
GO

-- R2: duplicata de (id_meta, mes) fica so com o lancamento de data_lancamento mais recente
-- R3: mes conta se nao_se_aplica = 0 e previsto/realizado preenchidos
-- literal, de proposito: nao exclui lancamento de mes pos-desligamento. Isso fica
-- documentado em intermediate.lancamento_rejeitado, sem afetar o calculo de score.
CREATE VIEW intermediate.lancamento_valido AS
WITH dedup AS (
    SELECT *,
        ROW_NUMBER() OVER (
            PARTITION BY id_meta, mes
            ORDER BY data_lancamento DESC, id_lancamento DESC
        ) AS rn
    FROM staging.meta_valor_mensal
)
SELECT
    id_meta,
    mes,
    previsto,
    realizado,
    nao_se_aplica,
    data_lancamento,
    CASE
        WHEN nao_se_aplica = 0 AND previsto IS NOT NULL AND realizado IS NOT NULL
        THEN 1 ELSE 0
    END AS flag_valido
FROM dedup
WHERE rn = 1;
GO