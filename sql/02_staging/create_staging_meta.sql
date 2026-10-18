IF OBJECT_ID('staging.meta', 'U') IS NOT NULL DROP TABLE staging.meta;
GO

CREATE TABLE staging.meta (
    id_meta              INT           NOT NULL PRIMARY KEY,
    id_ciclo             INT           NULL,
    id_colaborador       INT           NULL,
    nome_meta            NVARCHAR(200) NULL,
    tipo_meta            NVARCHAR(20)  NULL,   -- 'Individual' | 'Compartilhada'
    id_meta_referencia   INT           NULL,   -- preenchido so quando tipo_meta = 'Compartilhada'
    polaridade           NVARCHAR(20)  NULL,   -- 'Melhor para cima' | 'Melhor para baixo'
    tipo_acumulacao      NVARCHAR(10)  NULL,   -- 'Soma' | 'Media'
    peso                 INT           NULL    -- achado: 1 registro com peso negativo, tratado em intermediate
);
GO