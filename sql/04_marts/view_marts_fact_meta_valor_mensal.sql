IF OBJECT_ID('marts.fact_meta_valor_mensal', 'V') IS NOT NULL DROP VIEW marts.fact_meta_valor_mensal;
GO

-- repasse direto de intermediate.lancamento_valido
CREATE VIEW marts.fact_meta_valor_mensal AS
SELECT id_meta, mes, previsto, realizado, flag_valido
FROM intermediate.lancamento_valido;
GO