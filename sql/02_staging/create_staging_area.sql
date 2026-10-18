IF OBJECT_ID('staging.area', 'U') IS NOT NULL DROP TABLE staging.area;
GO

CREATE TABLE staging.area (
    id_area      INT           NOT NULL PRIMARY KEY,
    nome         NVARCHAR(200) NOT NULL,
    id_area_pai  INT           NULL   -- raiz (Comercial, Operacoes, Financeira) fica NULL
);
GO