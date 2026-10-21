# IT-8. Data warehouse y analítica

> Manual técnico · Borrador v0.1 · 2026-10-20 · Las marcas **[PREGUNTA Tn]** se resuelven en la ronda de preguntas y desaparecen de la versión final.

## 8.1 Propósito

Este capítulo describe el data warehouse de Cotown: qué datos contiene, de dónde salen, cómo se calculan los indicadores (camas, ocupación, ingresos, previsiones y escenarios) y cómo los consume Power BI. Es la referencia para interpretar los informes de dirección, operaciones, finanzas y booking, y para saber qué revisar cuando una cifra no cuadra.

## 8.2 Arquitectura

| Pieza | Descripción |
|---|---|
| **Servidor** | `data.cotown.com` (Azure). |
| **Base de datos** | PostgreSQL 16 en Docker, base `dw`, esquema `gold`. Se reinicia cada día a las 04:00. |
| **Proceso de carga (ETL)** | Programa Python (`etl.py`, con pandas) en `~/etl` del mismo servidor. Lee de la base de datos de Airflows (por un túnel SSH), de Airflows por GraphQL (ficheros Excel de forecast y presupuesto) y, para contabilidad, de SAP Business ByDesign. |
| **Programación** | `crontab` del servidor: a las 03:00 y cada 2 horas entre las 7:00 y las 17:00. |
| **Consumo** | Power BI, conectado directamente a las tablas del esquema `gold`. |

Cada ejecución **recalcula todo**: vacía cada tabla y la vuelve a cargar desde el origen, de modo que el data warehouse refleja siempre el estado actual de Airflows, con un retraso máximo de unas 2 horas en horario laboral.

## 8.3 Unidades y conceptos

| Concepto | Definición |
|---|---|
| **Cama-noche** | Unidad de medida de capacidad y de ocupación: una cama disponible (u ocupada) durante una noche. Las tablas de camas y de ocupación se expresan en cama-noches por recurso y mes. |
| **Recurso hoja** | La unidad que realmente se alquila: una plaza, una habitación sin plazas o un piso sin habitaciones. Camas y ocupación se calculan sobre recursos hoja. |
| **Tipo de dato** (`data_type`) | Distingue el origen o escenario de cada cifra: *Real* (facturado u ocupado), *OTB* (*on the books*: reservado y pendiente de facturar), *Tentative* (reservado pero aún no firme: reservas confirmadas sin firma de contrato, grupos bloqueados, ocupaciones sin contrato), *Forecast*, *Budget*, *UW* (*underwriting*), *Stabilised*, *MPR* y *Business Plan*. |
| **Duración de estancia** | SHORT (menos de 3 meses), MEDIUM (de 3 a 6), LONG (7 o más) y GROUP (reservas de grupo). En contratos LAU y otros: LTNC, LTC y FTC según tengan fecha de fin estimada o fija. |
| **Negocio** | B2C (reservas individuales, prefijo `C`), B2B (grupos, prefijo `B`) y LAU y otros (prefijo `L`). |

## 8.4 Modelo de datos

Esquema `gold`, en estrella: una tabla de recursos y unas dimensiones, alrededor de las que se organizan las tablas de hechos.

| Tabla | Tipo | Una fila por… | Contenido |
|---|---|---|---|
| `date` | Dimensión | Día (2024–2030) | Día, semana, mes, trimestre, semestre y año. |
| `location` | Dimensión | Localidad | Provincia y país. |
| `building` | Dimensión | Edificio | Ciudad, coordenadas y fecha de inicio de explotación. |
| `owner` | Dimensión | Propietario | Tipo: Vandor o terceros. |
| `flat_type`, `place_type` | Dimensión | Tipología | Tipologías de piso y de plaza (grupos: individual, doble, doble de uso individual, piso). |
| `product` | Dimensión | Producto | Productos facturables, más *Management fee*. |
| `resource` | Dimensión principal | Recurso (y una fila por edificio) | Edificio, piso, propietario, marca, tipologías, superficie, camas, régimen de renta y límites LAU. |
| `building_value` | Hecho | Valoración de edificio | Valores pre-capex, post-capex, ECO y RICS. |
| `resource_history` | Hecho | Recurso y mes | Situación del recurso (cosharing, LAU, pre-capex, capex, fuera de explotación…), superficie, unidades, habitaciones, camas y valoración vigente. |
| `beds` | Hecho | Recurso, mes y tipo de dato | Cama-noches disponibles, convertibles, potenciales, en capex y en pre-capex. |
| `occupancy` | Hecho | Recurso, mes y reserva (real) o duración (previsiones) | Cama-noches ocupadas y vendidas, firmes y tentativas. |
| `income` | Hecho | Línea de factura (real), mes de reserva (OTB) o recurso, mes y concepto (escenarios) | Importe neto (sin IVA), tarifa, precio estándar, producto, reserva, marketplace, tipo de dato y duración. |
| `booking` | Hecho | Reserva B2C | Cliente, motivo, escuela, canal, referencia, marketplace, fechas, importes, membership fee, management fee, régimen y fianza INCASÒL. |
| `marketplace` | Hecho | Factura de marketplace y reserva | Coste de la comisión repartido entre las reservas del periodo. |
| `gl` | Hecho | Apunte contable | Libro mayor de SAP (carga desactivada hoy). |

## 8.5 Proceso de carga

En producción se ejecutan, en este orden: **general → booking → forecast → income → beds → occupancy → history**.

### General (dimensiones)

Carga propietarios, tipologías, localidades, productos, edificios, valoraciones de edificios y recursos desde Airflows.

### Booking

- Una fila por reserva B2C con sus datos comerciales, importes y el porcentaje de management fee que le corresponde (por marketplace o por frecuencia de limpieza).
- Coste de marketplaces: cada factura de un marketplace se reparte a partes iguales entre las reservas que trajo en el periodo.

### Income (ingresos)

| Bloque | Origen | Cálculo |
|---|---|---|
| **Real** | Líneas de facturas emitidas desde 2024 | Importe sin IVA. Excluye los recibos de garantía. Incluye renta, servicios, extras y membership fee, por negocio (B2C, B2B, LAU y otros). |
| **OTB** | Precios mensuales de reservas aún no facturados, desde el mes actual | Renta, servicios y extras previstos. Las reservas no firmes se marcan como *Tentative*. Los contratos LAU y otros se proyectan mes a mes hasta 2030. |
| **Management fee** | Facturas reales y OTB de propietarios terceros | Importe neto × porcentaje de management fee. |
| **Forecast** | Forecast de cada recurso en Airflows (*Activos › Forecast*) | Camas × ocupación × renta × reparto por duración, menos descuentos; más servicios, limpieza, membership fee y management fee. |
| **Budget / UW** | Excel de presupuesto en Airflows (*Administración › Ficheros*, nombre "Budget…") | Presupuesto y *underwriting* de retail. |
| **Stabilised / MPR** | Camas reales, ocupación estabilizada (*Activos › Stabilised*) y precios base | *Stabilised*: ingreso esperado en régimen estabilizado, con camas disponibles o convertibles. *MPR*: ingreso potencial al 100 % de ocupación. |
| **Business Plan** | Foto congelada de los escenarios Stabilised | Ver más abajo. |

### Beds (camas)

Para cada recurso hoja y mes (2024–2030) se determina su situación según los bloqueos de disponibilidad del propio recurso, de su habitación o de su piso:

| Situación | Cuenta como |
|---|---|
| Antes del inicio de explotación del edificio o fuera de explotación | Sin camas |
| Contrato LAU | Cama potencial (y convertible, según el tipo de contrato) |
| Pre-capex / capex | Cama en pre-capex / en capex |
| Sin bloqueo | Cama disponible |

Además se cargan las camas del forecast y del Business Plan.

### Occupancy (ocupación)

- **Real**: a partir de la tabla de ocupación de Airflows (reservas B2C y residentes de grupos), cama-noches **ocupadas** (noches reales) y **vendidas** (según la forma de facturación: mes completo, quincena o proporcional). Las reservas no firmes se registran aparte como tentativas.
- **Forecast** y **Stabilised**: camas × ocupación prevista × días, por duración de estancia.

La tasa de ocupación se obtiene en Power BI relacionando las cama-noches ocupadas (o vendidas) con las disponibles.

### History (histórico de activos)

Para cada recurso y mes: situación (cosharing, LAU, pre-capex, capex, retail, parking, trastero, fuera de explotación), superficie, unidades, habitaciones, camas y valoración vigente (residencial, cosharing o la que corresponda a su situación).

### Business Plan

El Business Plan es una **foto fija** de los escenarios estabilizados (camas, ocupación e ingresos) que no cambia con cada carga. Para tomar una foto nueva, se vacía el parámetro `COPY_STABILISED` en Airflows (*Administración › Parámetros*): en la siguiente ejecución el ETL copia los escenarios estabilizados como Business Plan, guarda una copia fechada y vuelve a rellenar el parámetro con la fecha.

### Contabilidad (GL)

El ETL tiene un paso que descarga el libro mayor de SAP Business ByDesign (sociedad CTS00) y lo carga en `gold.gl`. Está desactivado temporalmente, mientras está en pausa el proyecto de analítica contable; la tabla existe pero está vacía.

## 8.7 Power BI

### Modelo central e informes

La analítica en Power BI se organiza en un **modelo central** (*Core Model*), que es el único que se conecta al data warehouse, y en **informes** conectados en directo a ese modelo. Así todas las cifras salen de las mismas medidas.

El modelo central:

- Lee las 16 tablas del esquema `gold` y renombra sus columnas a nombres de negocio en inglés (*Date*, *Resource*, *Data type*, *Sold beds*…).
- Relaciona los hechos (ingresos, ocupación, camas, histórico de activos, reservas, marketplaces) con las dimensiones (fecha, recurso, edificio, localidad, propietario, producto, tipologías).
- Define **145 medidas**, agrupadas en tablas `_kpis` (ingresos, ocupación, LAU, BGO y auxiliares).
- Incluye **selectores de escenario**, que permiten elegir qué datos ver y con cuáles comparar.

| Informe | Páginas | Contenido |
|---|---|---|
| **Cosharing** | 27 | Ingresos por recurso, duración de estancia y canal; management fee; ocupación; RevPOB y RevPAB; camas y cama-noches; comparativas con otro escenario y con el año anterior; BGO. |
| **Charts** | 15 | Las mismas métricas en formato gráfico: renta mensual, RevPOB, RevPAB, ocupación y camas, con comparativas y acumulados. |
| **LAU** | 3 | Ingresos de los contratos LAU y otros, comparativas y camas. |
| **Marketplaces** | 16 | Reservas, costes y comisiones por marketplace, edificio y tipología; coste frente a ingresos; comparativa interanual. |
| **Profiling** | 91 | Perfil de los clientes B2C: edad, nacionalidad, motivo, tipo de universidad, tipología de habitación, canal de entrada, tarifa; ingresos B2B y B2C; vistas por ciudad de la cartera de Vandor. |
| **SGR** (*Sistema General de Reporting*) | 4 | Informe general de la cartera: unidades, ingresos y cosharing por activo, con unidades, habitaciones, camas, superficies y valoraciones. |

### Escenarios

Las medidas se calculan según el escenario elegido en el selector de cada página:

| Escenario | Qué incluye |
|---|---|
| **Real** | Solo lo facturado (ingresos) u ocupado (ocupación). |
| **Real + OTB** | Lo facturado más lo reservado firme pendiente de facturar. |
| **Real + OTB + Tentative** | Además, lo reservado aún no firme. |
| **Rack rate** (y sus variantes con OTB) | Las mismas cifras a tarifa estándar, sin descuentos. |
| **Forecast** | Previsión por recurso. |
| **Stabilised Available / Convertible** | Régimen estabilizado con las camas disponibles o con las convertibles. |
| **Business Plan Available / Convertible** | Foto fija del Business Plan. |
| **Budget / UW** | Presupuesto y *underwriting* (contratos LAU y otros). |

Casi todas las medidas tienen una versión *to compare* (con el escenario del segundo selector), la diferencia absoluta y porcentual, el acumulado del año (*YTD*), el acumulado del periodo (*ACC*) y la del año anterior (*LY*).

### Medidas principales

| Medida | Definición |
|---|---|
| **Income value** | Suma de los importes netos de `income` en el escenario y tipo de ingreso (renta, servicios, fees) seleccionados; en los escenarios *Rack rate*, suma de la tarifa estándar. |
| **% RN Occupied** | Cama-noches ocupadas ÷ cama-noches disponibles. |
| **% RN Sold** | Cama-noches vendidas ÷ cama-noches disponibles. Las vendidas cuentan según la forma de facturación (mes completo, quincena o días). |
| **Occupancy beds rn** | Camas o cama-noches (disponibles, convertibles, potenciales, ocupadas, vendidas) por mes, según el selector. |
| **RevPOB** | Ingreso de renta ÷ camas vendidas: ingreso medio por cama ocupada. |
| **RevPAB** | Ingreso de renta ÷ camas disponibles (o convertibles, según el escenario): ingreso medio por cama disponible. |
| **MF Management fee** y **MF Management fee %** | Management fee del periodo y su porcentaje sobre los ingresos de propietarios terceros. |
| **Converted C% / P% / S%** | Camas en explotación sobre camas convertibles, potenciales o del escenario estabilizado: avance de la conversión de pisos LAU a cosharing. |
| **LAU beds**, **pre-capex** y **capex beds** | Camas medias por mes en cada situación. |
| **BGO** | Comparación por bloques de camas, ocupación, RevPOB e ingresos entre real, forecast, stabilised y Business Plan, con código de colores según la desviación. |
| **Booking RevPOB** | Renta bruta total ÷ meses de estancia, por reserva. |
| **Marketplace prorrated cost** | Coste de comisión de marketplace imputado a cada reserva. |

### Acceso y mantenimiento

El servicio de Power BI en la nube se conecta a la base de datos `dw` de `data.cotown.com` a través de una **puerta de enlace** (*gateway*) de datos local. Para acceder desde un puesto de trabajo (por ejemplo, con Power BI Desktop) se usa un túnel SSH al servidor (script `back/etl/tunnel`).

Los informes de Power BI los mantienen conjuntamente Cotown y Oimbra.

## 8.8 Fuentes

| Tema | Dónde está |
|---|---|
| Proceso de carga | `back/etl/etl.py` y `back/etl/library/business/` |
| Consultas de extracción | `back/etl/sql/` |
| Modelo del data warehouse | `back/etl/sql/_init.sql` |
| Programación | `crontab` del usuario `cotown` en `data.cotown.com` |
| Forecast, stabilised y presupuesto | Airflows: *Activos › Forecast*, *Activos › Stabilised*, *Administración › Ficheros* |
| Modelo e informes de Power BI | Ficheros `Core Model v1.0.pbix` y `Report - *.pbix` |

## 8.9 Pendiente de confirmar

| Tema | Quién o qué lo confirma |
|---|---|
| — | — |
