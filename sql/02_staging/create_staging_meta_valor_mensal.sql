IF OBJECT_ID('staging.meta_valor_mensal', 'U') IS NOT NULL DROP TABLE staging.meta_valor_mensal;
GO

CREATE TABLE staging.meta_valor_mensal (
    id_lancamento     INT             NOT NULL PRIMARY KEY,
    id_meta           INT             NULL,
    mes               TINYINT         NULL,
    previsto          DECIMAL(18,4)   NULL,
    realizado         DECIMAL(18,4)   NULL,
    nao_se_aplica     BIT             NULL,
    data_lancamento   DATE            NULL
);
GO