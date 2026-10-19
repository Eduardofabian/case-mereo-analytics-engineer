CREATE TABLE [dim_area] (
  [id_area] integer PRIMARY KEY,
  [nome] nvarchar(255),
  [id_area_pai] integer,
  [nivel] integer
)
GO

CREATE TABLE [dim_colaborador] (
  [id_colaborador] integer PRIMARY KEY,
  [nome] nvarchar(255),
  [id_area] integer,
  [id_gestor] integer,
  [data_admissao] date,
  [data_desligamento] date,
  [flag_elegivel_r10] bit
)
GO

CREATE TABLE [dim_meta] (
  [id_meta] integer PRIMARY KEY,
  [id_ciclo] integer,
  [id_colaborador] integer,
  [nome_meta] nvarchar(255),
  [tipo_meta] nvarchar(255),
  [polaridade_efetiva] nvarchar(255),
  [tipo_acumulacao_efetiva] nvarchar(255),
  [id_meta_lancamentos] integer,
  [peso_efetivo] decimal
)
GO

CREATE TABLE [fact_meta_valor_mensal] (
  [id_meta] integer,
  [mes] integer,
  [previsto] decimal,
  [realizado] decimal,
  [flag_valido] bit
)
GO

EXEC sp_addextendedproperty
@name = N'Column_Description',
@value = 'CTE recursiva, 0 = raiz',
@level0type = N'Schema', @level0name = 'dbo',
@level1type = N'Table',  @level1name = 'dim_area',
@level2type = N'Column', @level2name = 'nivel';
GO

EXEC sp_addextendedproperty
@name = N'Column_Description',
@value = 'degenerate dimension — 2024/2025, mantido mesmo filtrando por R1 no mart',
@level0type = N'Schema', @level0name = 'dbo',
@level1type = N'Table',  @level1name = 'dim_meta',
@level2type = N'Column', @level2name = 'id_ciclo';
GO

ALTER TABLE [dim_area] ADD FOREIGN KEY ([id_area_pai]) REFERENCES [dim_area] ([id_area])
GO

ALTER TABLE [dim_colaborador] ADD FOREIGN KEY ([id_area]) REFERENCES [dim_area] ([id_area])
GO

ALTER TABLE [dim_colaborador] ADD FOREIGN KEY ([id_gestor]) REFERENCES [dim_colaborador] ([id_colaborador])
GO

ALTER TABLE [dim_meta] ADD FOREIGN KEY ([id_colaborador]) REFERENCES [dim_colaborador] ([id_colaborador])
GO

ALTER TABLE [dim_meta] ADD FOREIGN KEY ([id_meta_lancamentos]) REFERENCES [dim_meta] ([id_meta])
GO

ALTER TABLE [fact_meta_valor_mensal] ADD FOREIGN KEY ([id_meta]) REFERENCES [dim_meta] ([id_meta])
GO
