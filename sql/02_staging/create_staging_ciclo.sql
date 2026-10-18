IF OBJECT_ID('staging.ciclo', 'U') IS NOT NULL DROP TABLE staging.ciclo;
GO

CREATE TABLE staging.ciclo (
    id_ciclo     INT           NOT NULL PRIMARY KEY,
    nome         NVARCHAR(100) NOT NULL,
    data_inicio  DATE          NULL,
    data_fim     DATE          NULL
);
GO