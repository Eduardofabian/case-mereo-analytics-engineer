-- staging    = espelho cru do SQLite original, sem limpeza nenhuma
-- intermediate = resolucao de regra (dedup, validade, R7, hierarquia); uso interno, nao e pra consumo externo
-- marts      = produto final, o star schema e as views de score que Dashboard, Agente e os CSVs consomem direto
CREATE SCHEMA staging;
GO
CREATE SCHEMA intermediate;
GO
CREATE SCHEMA marts;
GO