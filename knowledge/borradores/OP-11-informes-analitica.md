# OP-11. Informes y analítica

> Manual funcional · Borrador v0.1 · 2026-10-21 · Las marcas **[PREGUNTA On]** se resuelven en la ronda de preguntas y desaparecen de la versión final.

## 11.1 Propósito

Este capítulo explica qué información se puede sacar del sistema y de dónde: los **informes Excel** y las **descargas** del backoffice, los datos de previsión que alimentan la analítica (forecast, stabilised, valoraciones y Business Plan) y los informes de **Power BI** desde el punto de vista de quien los usa.

## 11.2 Conceptos

| Concepto | Qué es |
|---|---|
| **Informe Excel** | Extracción de datos de Airflows con formato fijo, que se descarga en *Procesos › Informes*. Muestra los datos del momento. |
| **Data warehouse** | Copia analítica de los datos de Airflows, que se recalcula entera a las 03:00 y cada 2 horas de 7:00 a 17:00. Alimenta Power BI. |
| **Cama-noche** | Unidad de la analítica: una cama disponible u ocupada durante una noche. |
| **Escenario** | Qué cifras se ven: *Real* (facturado u ocupado), *OTB* (reservado firme pendiente de facturar), *Tentative* (reservado no firme), *Rack rate* (a tarifa estándar), *Forecast*, *Stabilised*, *Business Plan*, *Budget* y *UW*. |
| **Forecast** | Previsión mensual por recurso: camas, ocupación, tarifas por duración, descuentos y otros ingresos. |
| **Stabilised** | Ocupación y reparto por duración que se espera de un recurso en régimen estable, por mes del año. |
| **Business Plan** | Foto fija de los escenarios estabilizados, que no cambia con cada carga. |

## 11.3 Informes Excel del backoffice

Se descargan en *Procesos › Informes*. Los que llevan filtro piden fechas, emisor, año o grupo antes de generarse.

| Área | Informe | Filtro | Para qué |
|---|---|---|---|
| Inventario | **Propietarios** | — | Listado de proveedores. |
| | **Edificios** | — | Listado de edificios. |
| | **Recursos, precios, tarifas** | — | Recursos con su configuración, tarifa y precios. Plantilla de la carga *Recursos*. |
| | **Inventario** | — | Mobiliario y enseres de los recursos. |
| | **Precios** | — | Precios base por año académico. Plantilla de la carga *Precios*. |
| | **Disponibilidad** | Fechas | Recursos libres y ocupados en un periodo. |
| Reservas | **Reservas** | Fechas | Reservas B2C de un periodo. |
| | **Reservas PowerBI** | — | Todas las reservas B2C con su perfil comercial (solicitante, cómo nos conoció, canal, marketplace, género, nacionalidad, continente, escuela, idioma), sus fechas (creación, solicitud, confirmación, entrada y salida, check-in y check-out), edificio, propietario, ciudad, tipología, renta, servicios y marca. Base del seguimiento comercial semanal; la plantilla añade columnas calculadas. |
| | **Docs reservas** | Fechas | Documentación de las reservas. |
| | **Cuestionarios de satisfacción** | — | Respuestas de los cuestionarios de check-in y check-out. |
| | **Descuentos** | Fechas | Descuentos aplicados por mes y motivo. |
| | **Marketplaces** | Fechas | Reservas traídas por marketplaces. |
| | **Contratos** | Fechas | Contratos de las reservas y su estado de firma. |
| | **Rooming list** | Grupo | Residentes de un grupo. Plantilla de la carga *Rooming*. |
| Facturación | **Pagos emitidos** | Fechas y emisor | Cobros emitidos. |
| | **Pagos recibidos** | Fechas | Cobros pagados. |
| | **Ingresos** | Fechas y emisor | Ingresos facturados. Los propietarios ven solo los suyos. |
| | **Management Fee** | Fechas y emisor | Management fee por propietario. |
| | **SEPA** | — | Cobros domiciliados pendientes, para preparar la remesa (ver *Facturación y cobros*). |
| | **Devoluciones** | — | Reservas en salida: garantía, lo pendiente y lo cobrado de la garantía, datos bancarios para la devolución. |
| | **Previsión de devoluciones** | — | Garantías que habrá que devolver próximamente. |
| LAU y otros | **Reservas LAU/Otros** | — | Contratos LAU, locales, parkings y coworking. |
| | **Análisis LT LAU** | — | Un contrato LAU por fila con lo necesario para negociar la salida del inquilino: edificio, recurso, superficie y plazas; inquilino, renta actual, género y fecha de nacimiento; situación, fechas de fin, tipo de contrato y subrogación pendiente; estado de la negociación, % de contribución, aportación recomendada (MAC), petición del inquilino y propuesta de Vandor; y valoraciones pre-capex (renta antigua y vacío), residencial, capex previsto y post-capex. La plantilla añade columnas calculadas. |
| Regulatorio | **INCASÒL** | Fechas | Altas y bajas de fianzas en el INCASÒL. |
| | **Datos formato N2** | Año | Datos para el registro único de arrendamientos (NRUA) de las estancias de un año. |
| Analítica | **Plantilla Forecast** | Fechas | Forecast actual, como plantilla para cargar uno nuevo. |
| | **Plantilla Stabilised** | — | Stabilised actual, como plantilla para cargar uno nuevo. |

**Descargas** (ZIP):

| Descarga | Filtro | Contenido |
|---|---|---|
| **Contratos** | Fechas, emisor, edificio | PDF de los contratos. |
| **Facturas y recibos** | Mes, emisor | PDF de las facturas y recibos. |
| **CSVs formato N2** | Año | Ficheros para el registro único de arrendamientos (NRUA). |
| **Declaraciones INCASÒL** | Fechas | Declaración responsable de devolución de fianza de cada reserva, en catalán. |

Los propietarios solo ven *Ingresos*, *Management Fee*, *Contratos* y *Facturas y recibos*, limitados a sus datos.

## 11.4 Tareas

### Subir una carga Excel

Las cargas masivas se suben en *Procesos › Cargas*: se crea una carga y se adjunta el Excel. El proceso de cargas la recoge en los siguientes 15 minutos, la marca como *Procesando…* y trata cada hoja según su nombre:

| Hoja | Qué carga | Se identifica por | Capítulo |
|---|---|---|---|
| **Recursos** | Pisos, habitaciones y plazas con su configuración (propietario, prestador, tipologías, tarifa, uso, marca, características, datos del último LAU…). Crea los nuevos y actualiza los existentes. | Código del recurso | *Inventario y precios* |
| **Precios** | Precios base por año académico. | Año, edificio, tipo de piso y tipo de plaza | *Inventario y precios* |
| **Rooming** | Residentes de un grupo. | Grupo, tanda y plaza | *Reservas de grupo B2B* |
| **Forecast** | Previsión mensual por recurso. | Recurso y mes | Este capítulo |
| **Stabilised** | Ocupación estabilizada por recurso y mes del año. | Recurso y mes | Este capítulo |

Las valoraciones y los bloqueos de disponibilidad se registran en la ficha del recurso, no con carga.

**Formato**: la cabecera va en la fila 2 y los datos empiezan en la fila 3. Las columnas de datos relacionados se indican con la forma `Tabla.Campo` (por ejemplo, el nombre del propietario) y el sistema las traduce. Las hojas cuyo nombre empieza por `_` y las de catálogos se ignoran. La forma más segura de obtener el formato correcto es descargar el informe Excel del mismo nombre y usarlo como plantilla.

**Resultado**: cada hoja se carga **entera o nada**: si una fila falla, no se carga ninguna fila de esa hoja. Al terminar, la carga queda como *Ok* o *Error*, con el detalle de los errores por fila. Corregir las filas indicadas y volver a subir el fichero.

### Mantener el forecast

**Cuándo**: cuando se revisa la previsión (por ejemplo, cada mes o cada trimestre).

**Cómo**: descargar la **Plantilla Forecast** de un periodo, actualizarla y subirla con la carga Excel **Forecast** (*Procesos › Cargas*). Cada fila es un recurso y un mes: camas, % de ocupación, tarifas por duración (corta, media, larga, grupo), % por duración, % de descuento, servicios, limpieza final, membership fee, refacturación y management fee.

**Reglas**: la ocupación no puede superar el 100 % y los porcentajes por duración no pueden sumar más de 100.

**Qué hace el sistema**: en la siguiente carga del data warehouse, el escenario *Forecast* de Power BI refleja los cambios.

### Mantener el stabilised

Igual que el forecast, con la **Plantilla Stabilised** y la carga **Stabilised**: por recurso y mes del año, % de ocupación, % por duración y % de *leakage*. Alimenta los escenarios *Stabilised*.

### Registrar valoraciones

En la ficha del recurso, apartado *Valoraciones*: una fila por fecha de tasación con los valores pre-capex (renta antigua y vacío), post-capex (cosharing) y residencial. La última valoración se copia a la ficha del recurso y la analítica la usa como valoración vigente. Las valoraciones de edificios (ECO, RICS…) se registran en la ficha del edificio.

### Tomar una nueva foto del Business Plan

**Cuándo**: al aprobarse un nuevo Business Plan.

**Cómo**: en *Administración › Parámetros*, vaciar el parámetro **COPY_STABILISED**.

**Qué hace el sistema**: en la siguiente carga del data warehouse copia los escenarios estabilizados como nuevo Business Plan, guarda una copia fechada del anterior y vuelve a rellenar el parámetro con la fecha.

### Cargar el presupuesto

El presupuesto (*Budget*) y el *underwriting* de locales se suben como fichero Excel en *Administración › Ficheros*, con un nombre que empiece por **Budget**. La siguiente carga del data warehouse lo incorpora.

### Consultar Power BI

Los informes se abren en el servicio de Power BI de Cotown. Todos usan el mismo modelo de datos, así que las cifras coinciden entre informes.

| Informe | Responde a |
|---|---|
| **Cosharing** | ¿Cuánto ingresamos por recurso, duración de estancia y canal? ¿Qué ocupación, RevPOB y RevPAB tenemos? ¿Cómo vamos frente a otro escenario y al año anterior? |
| **Charts** | Las mismas métricas en gráficos: evolución de renta, RevPOB, RevPAB, ocupación y camas. |
| **LAU** | ¿Cuánto ingresan los contratos LAU y otros? ¿Cuántas camas siguen en LAU? |
| **Marketplaces** | ¿Cuántas reservas y cuánto coste traen los marketplaces, por edificio y tipología? ¿Compensa su comisión? |
| **Profiling** | ¿Quiénes son nuestros residentes (edad, nacionalidad, motivo, universidad, tipología, canal)? |
| **SGR** | Visión general de la cartera: unidades, habitaciones, camas, superficies, ingresos y valoraciones por activo. |

**Selectores de escenario**: en cada página se elige el escenario a ver y el escenario con el que comparar. Casi todas las cifras muestran también la diferencia, el acumulado del año y el año anterior.

**Medidas clave**:

| Medida | Qué mide |
|---|---|
| **% RN Occupied / Sold** | Cama-noches ocupadas o vendidas sobre las disponibles. |
| **RevPOB** | Ingreso de renta por cama vendida. |
| **RevPAB** | Ingreso de renta por cama disponible. |
| **Management fee %** | Management fee sobre los ingresos de los propietarios terceros. |
| **Converted %** | Avance de la conversión de pisos LAU a cosharing. |

**Frescura**: los datos son los de la última carga del data warehouse (como mucho, unas 2 horas de retraso en horario laboral). Por la noche no se actualizan entre las 17:00 y las 03:00.

Los informes los mantienen Cotown y Oimbra conjuntamente. El detalle de cálculo de cada medida está en el *Manual técnico*.

## 11.5 Automático y manual

| Qué | A / M |
|---|---|
| Informes Excel y descargas | A (bajo demanda) |
| Forecast y stabilised | M (cargas Excel) |
| Valoraciones | M (en la ficha del recurso o del edificio) |
| Presupuesto | M (fichero Excel) |
| Foto del Business Plan | M (vaciar el parámetro); A (la copia) |
| Carga del data warehouse | A (03:00 y cada 2 horas de 7:00 a 17:00) |
| Informes de Power BI | A (se actualizan con el data warehouse) |

## 11.6 Excepciones

| Situación | Qué pasa | Qué hacer |
|---|---|---|
| Un informe Excel sale vacío o da error | Filtro sin datos o informe sin plantilla. | Revisar el filtro; si persiste, avisar a Oimbra. |
| Power BI no muestra un cambio reciente | La carga del data warehouse aún no ha pasado. | Esperar a la siguiente carga. |
| Una carga Excel termina en *Error* | Alguna fila tiene un dato incorrecto; la hoja no se carga entera. | Ver el detalle por fila en la carga, corregir y volver a subir. |

## 11.7 Fuentes

| Tema | Dónde está |
|---|---|
| Informes Excel y descargas | Backoffice complementario y servicio de integración |
| Cargas Excel | Proceso automático de cargas |
| Data warehouse | Proceso de carga del data warehouse |
| Power BI | Modelo central e informes de Power BI |

## 11.8 Pendiente de confirmar

| Tema | Quién o qué lo confirma |
|---|---|
| — | — |
