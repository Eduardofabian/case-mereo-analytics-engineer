USE CaseMereo;
GO

-- marts (ordem nao importa pra DROP, views sem SCHEMABINDING nao bloqueiam)
IF OBJECT_ID('marts.vw_score_gestor', 'V') IS NOT NULL DROP VIEW marts.vw_score_gestor;
IF OBJECT_ID('marts.vw_score_area', 'V') IS NOT NULL DROP VIEW marts.vw_score_area;
IF OBJECT_ID('marts.vw_score_colaborador', 'V') IS NOT NULL DROP VIEW marts.vw_score_colaborador;
IF OBJECT_ID('marts.fact_meta_valor_mensal', 'V') IS NOT NULL DROP VIEW marts.fact_meta_valor_mensal;
IF OBJECT_ID('marts.dim_meta', 'V') IS NOT NULL DROP VIEW marts.dim_meta;
IF OBJECT_ID('marts.dim_colaborador', 'V') IS NOT NULL DROP VIEW marts.dim_colaborador;
IF OBJECT_ID('marts.dim_area', 'V') IS NOT NULL DROP VIEW marts.dim_area;
GO

-- intermediate
IF OBJECT_ID('intermediate.area_descendentes', 'V') IS NOT NULL DROP VIEW intermediate.area_descendentes;
IF OBJECT_ID('intermediate.vw_nota_meta', 'V') IS NOT NULL DROP VIEW intermediate.vw_nota_meta;
IF OBJECT_ID('intermediate.meta_resolvida', 'V') IS NOT NULL DROP VIEW intermediate.meta_resolvida;
IF OBJECT_ID('intermediate.lancamento_rejeitado', 'V') IS NOT NULL DROP VIEW intermediate.lancamento_rejeitado;
IF OBJECT_ID('intermediate.lancamento_valido', 'V') IS NOT NULL DROP VIEW intermediate.lancamento_valido;
GO

-- staging
IF OBJECT_ID('staging.meta_valor_mensal', 'U') IS NOT NULL DROP TABLE staging.meta_valor_mensal;
IF OBJECT_ID('staging.meta', 'U') IS NOT NULL DROP TABLE staging.meta;
IF OBJECT_ID('staging.colaborador', 'U') IS NOT NULL DROP TABLE staging.colaborador;
IF OBJECT_ID('staging.ciclo', 'U') IS NOT NULL DROP TABLE staging.ciclo;
IF OBJECT_ID('staging.area', 'U') IS NOT NULL DROP TABLE staging.area;
GO