IF OBJECT_ID('marts.dim_meta', 'V') IS NOT NULL DROP VIEW marts.dim_meta;
GO

-- repasse direto de intermediate.meta_resolvida: nao reimplementa a logica de R7 aqui,
-- so expoe a mesma coisa no schema de consumo
CREATE VIEW marts.dim_meta AS
SELECT id_meta, id_ciclo, id_colaborador, nome_meta, tipo_meta,
       polaridade_efetiva, tipo_acumulacao_efetiva, id_meta_lancamentos, peso_efetivo
FROM intermediate.meta_resolvida;
GO