IF OBJECT_ID('intermediate.lancamento_rejeitado', 'V') IS NOT NULL DROP VIEW intermediate.lancamento_rejeitado;
GO

-- quarentena: todo lancamento que nao entrou no calculo, com o motivo. Nao alimenta
-- marts, serve so pra documentar achado de qualidade no README.
-- motivo 'lancamento_pos_desligamento' usa inicio do mes, nao fim, de proposito:
-- R10 trabalha com data exata, entao o mes do proprio desligamento ainda conta
-- (o colaborador trabalhou parte dele). So os meses inteiramente depois saem.
CREATE VIEW intermediate.lancamento_rejeitado AS
WITH dedup AS (
    SELECT
        *,
        ROW_NUMBER() OVER (
            PARTITION BY id_meta, mes
            ORDER BY data_lancamento DESC, id_lancamento DESC
        ) AS rn
    FROM staging.meta_valor_mensal
)
SELECT id_lancamento, id_meta, mes, previsto, realizado, nao_se_aplica, data_lancamento,
       'duplicado_perdedor' AS motivo_rejeicao
FROM dedup
WHERE rn <> 1

UNION ALL

SELECT id_lancamento, id_meta, mes, previsto, realizado, nao_se_aplica, data_lancamento,
       'previsto_ou_realizado_nulo' AS motivo_rejeicao
FROM staging.meta_valor_mensal
WHERE nao_se_aplica = 0 AND (previsto IS NULL OR realizado IS NULL)

UNION ALL

SELECT d.id_lancamento, d.id_meta, d.mes, d.previsto, d.realizado,
       d.nao_se_aplica, d.data_lancamento,
       'lancamento_pos_desligamento' AS motivo_rejeicao
FROM dedup AS d
JOIN staging.meta AS m ON m.id_meta = d.id_meta
JOIN staging.colaborador AS c ON c.id_colaborador = m.id_colaborador
WHERE d.rn = 1
  AND d.nao_se_aplica = 0
  AND d.previsto IS NOT NULL AND d.realizado IS NOT NULL
  AND m.id_ciclo = 2025
  AND c.data_desligamento IS NOT NULL
  AND DATEFROMPARTS(2025, d.mes, 1) > c.data_desligamento;
GO