-- -------------------------------------
-- TB (Trial Balance de Cotown)
-- -------------------------------------
-- Una fila por empresa + clave + mes, en formato largo (ticket 09b).
-- La escribe batch_tb.py al procesar una carga del TB (Batch.Tb_upload)
-- que queda en ok: sustituye los meses de la carga en una transacción
-- (DELETE por empresa + mes, INSERT de sus filas).
-- No está en _init.sql: el paso init del ETL borra y recrea gold, y estas
-- filas no salen de la BD de la aplicación. Si hubiera que rehacerla, se
-- vuelven a poner en pendiente las cargas en ok.

CREATE TABLE IF NOT EXISTS gold.tb (
  "empresa" varchar NOT NULL,           -- Sociedad SAP, p. ej. CTS00
  "cuenta" varchar NOT NULL,            -- Cuenta de mayor, 6 dígitos
  "servicio" varchar NOT NULL,          -- Servicio S_... o la cuenta
  "descripcion" varchar NOT NULL,       -- Texto del servicio o de la cuenta
  "asset" varchar NOT NULL,             -- Edificio, ciudad o Manco
  "categoria" varchar NOT NULL,         -- Categoría de producto de la TB
  "ccaa1" varchar NOT NULL,             -- Agrupación de cuentas anuales, nivel 1
  "ccaa2" varchar NOT NULL,             -- Agrupación de cuentas anuales, nivel 2
  "budget" varchar NULL,                -- Vacío de momento
  "clave" varchar NOT NULL,             -- cuenta servicio asset categoria, igual que TB!K
  "mes" varchar(7) NOT NULL,            -- AAAA-MM, como gold.date.yearmonth
  "date" date NOT NULL,                 -- Primer día del mes, para cruzar con gold.date
  "importe" numeric(15,2) NOT NULL,     -- Movimiento del mes con el signo de SAP, nunca 0
  "tb_upload_id" int8 NOT NULL,         -- Carga de Airflows (Batch.Tb_upload) que generó la fila
  "ts" timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT tb_pk PRIMARY KEY ("empresa", "clave", "mes"),
  CONSTRAINT tb_cuenta_ck CHECK ("cuenta" ~ '^[0-9]{6}$'),
  CONSTRAINT tb_mes_ck CHECK ("mes" ~ '^[0-9]{4}-(0[1-9]|1[0-2])$'),
  CONSTRAINT tb_date_ck CHECK ("date" = to_date("mes", 'YYYY-MM')),
  CONSTRAINT tb_importe_ck CHECK ("importe" <> 0)
);

-- Meses de una empresa (sustitución de una carga) y filas de una carga (trazabilidad)
CREATE INDEX IF NOT EXISTS tb_empresa_mes_idx ON gold.tb ("empresa", "mes");
CREATE INDEX IF NOT EXISTS tb_upload_idx ON gold.tb ("tb_upload_id");
CREATE INDEX IF NOT EXISTS tb_date_idx ON gold.tb ("date");
