IF OBJECT_ID('staging.colaborador', 'U') IS NOT NULL DROP TABLE staging.colaborador;
GO

CREATE TABLE staging.colaborador (
    id_colaborador     INT           NOT NULL PRIMARY KEY,
    nome                NVARCHAR(200) NOT NULL,
    id_area             INT           NULL,
    id_gestor           INT           NULL,   -- auto-relacionamento, hierarquia de gestor
    data_admissao       DATE          NULL,
    data_desligamento   DATE          NULL    -- NULL = colaborador ativo
);
GO