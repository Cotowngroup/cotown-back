# Manual: transformación del Trial Balance SAP a TB

Este proceso convierte el export de Trial Balance de SAP en los movimientos mensuales de la TB de Cotown. Sustituye al trabajo que se hacía a mano en Excel: limpiar el export, BUSCARV, tabla dinámica, cuadre y pegado de valores.

Todo lo que es una decisión contable (cómo se llama cada edificio, qué líneas se reclasifican, qué categoría lleva cada combinación) está en tablas de configuración que se pueden editar. El programa no decide nada por su cuenta: si algo no se puede resolver con esas tablas, se para y dice qué falta.

Especificación técnica: `.backlog/tb/transformacion-tb.md` del repo de documentación `cotown`.

## Cargas en Airflows

Es la forma normal de uso. Cada export de SAP se sube a Airflows como una **carga del TB** (entidad `Batch.Tb_upload`, «Carga TB»), y un proceso del ETL la transforma y deja el resultado en la propia carga.

1. Exportar de SAP el Trial Balance de una sociedad, con uno o varios periodos mensuales, y no tocar el fichero.
2. En Airflows, crear una carga del TB y adjuntar el fichero en `File`. La carga nace en `pendiente`.
3. El proceso (`back/etl/batch_tb.py`) se ejecuta cada pocos minutos. Pone la carga en `procesando`, la transforma con la hoja maestra de su empresa y la deja en `ok` o en `error`.
4. Revisar la carga:
   - `Status`: `ok` si todo ha ido bien; `error` si hay algún problema.
   - `File`: en `ok`, el mismo fichero con una pestaña más, `TB`, con las filas del TB (las columnas de «Resultado»). Si se reprocesa, la pestaña se sustituye.
   - `Log`: en `ok`, el resumen (hoja maestra usada y su fecha, filas, claves y total de cada mes). En `error`, **todos** los errores a la vez y, si se llegó a leer, la hoja maestra usada.
   - `Company`, `Months`, `Rows`, `Totals` y `Processed_at`: empresa, meses del export, filas de salida, total de cada mes (debe ser 0) y cuándo se procesó.

Si sale `error`, se corrige la hoja maestra (o el export) y se **reprocesa**: se vuelve a poner la carga en `pendiente`. Lo mismo si una carga se queda en `procesando` porque el proceso se cayó a medias.

El proceso solo acepta exports de Trial Balance: comprueba que el fichero tenga el título «Trial Balance» y la fila «Cuenta de mayor».

**Instalación** (máquina del ETL, data.cotown.com): el script usa la configuración del ETL (`.settings.toml` y `.secrets.toml` de `back/etl`) y el paquete `tb` desde `back/etl/tb/src`, sin instalarlo. Se ejecuta desde `back/etl` con un cron, por ejemplo cada 5 minutos:

```
*/5 * * * * cd <ruta>/back/etl && python batch_tb.py
```

Dos ejecuciones a la vez no procesan la misma carga: cada una toma la suya de forma atómica. El registro del proceso queda en `back/etl/log/batch_tb.log`.

## Cargas desde SAP, sin export manual

`back/etl/sap_tb.py` genera el export de Trial Balance directamente desde el libro mayor de SAP (informe OData `SAPURL_GL`) y lo sube como carga. El fichero tiene las mismas columnas, el mismo orden de filas y el mismo formato que el export hecho a mano (título, bloque de selección, celdas grises de dimensiones, importes en EUR y columna `Resultado`). La única diferencia de forma buscada: la cabecera es una sola fila, en negrita y con los filtros; se quitan las dos filas de encima («Importe en moneda de empresa» y el año), que no aportan, así que la carga se procesa igual y guarda el fichero exacto que se transformó. Para agosto y septiembre de 2026 da el mismo TB, al céntimo, que el export manual (tests de oro con los apuntes de SAP guardados en `data/sap_gl_CTS00_2026-0*.json` y los maestros en `data/sap_maestros_2026-09.json`).

Desde `back/etl`:

```
python sap_tb.py --empresa CTS00 --meses 2026-08 --subir
python sap_tb.py --empresa CTS00 --meses 2026-08 --subir --carga 11
python sap_tb.py --empresa CTS00 --meses 2026-08 2026-09 --xlsx "TB - CTS00.xlsx"
```

- `--subir` crea la carga en Airflows (`TB - <empresa> - <meses> (SAP).xlsx`), en `pendiente`. `--xlsx` guarda el fichero en disco para revisarlo. Se puede usar uno de los dos o ambos.
- `--carga ID`, con `--subir`, sustituye el fichero de una carga que ya existe y la deja en `pendiente`, con `Log`, `Company`, `Months`, `Rows`, `Totals` y `Processed_at` vacíos. Sirve para regenerar un mes sin crear cargas repetidas.
- La sociedad tiene que estar en `SAPBOOKS` de `back/etl/.settings.toml`, con su libro contable (`CTS00 = 'ES02'`). El nombre del libro, para el bloque de selección, está en `SAPBOOKNAMES`.
- Columnas: empresa, cuenta, tipo de cuenta, producto, tarea de proyecto, centro de beneficio y centro de coste salen del libro mayor. La categoría de producto sale de los maestros de servicios y materiales (`RPSERVICE_Q0001`, `RPMATERIAL_Q0001`) y la unidad responsable de proyecto, del de tareas (`RPPROPRJU05_Q0007`). Los productos individuales (inmovilizado, como `100003019`) no están en esos maestros: su categoría sale vacía. El proceso no la usa.
- Diferencias de forma con el export manual que no afectan: un mes sin apuntes es una celda vacía (SAP escribe un texto vacío), y la altura de alguna fila puede variar.
- El código de producto sale de `CPRODUCT_UUID` y los textos se piden en español (`sap-language=ES`), como en el export manual.
- Se excluye el arrastre de saldos de apertura del ejercicio (tipo de documento `00058`, «Ejecución de transferencia de saldos»): no va a la TB.
- Si SAP no tiene apuntes de algún mes pedido, o la respuesta llega incompleta, no se genera nada y se informa del error.

Sirve también para el mes en curso antes del cierre. El TB de un mes abierto cambiará cuando se contabilice el resto: se vuelve a lanzar cuando haga falta.

## Uso en local

Para pruebas, o para revisar un export sin subirlo. Desde `back/etl/tb`, con el paquete instalado en el venv (`pip install -e .`):

```
python -m tb "TB - CTS - SEP.xlsx" --maestro maestro_tb_CTS00.xlsx --csv salida.csv
```

- El argumento es el export de SAP tal como sale, sin tocarlo.
- `--csv` guarda el resultado para revisarlo. Sin él, solo se muestra un resumen.
- `--maestro` es la hoja maestra de la empresa del export, con las tablas de configuración (ver «Hoja maestra de configuración»).

Si todo va bien, el programa termina con código 0 y muestra:

- el número de filas y de claves;
- el total de cada mes, que debe ser 0.

Si hay algún problema, no escribe nada, muestra **todos** los errores a la vez y termina con código 1. Se corrigen las tablas y se vuelve a lanzar.

## Qué hace, paso a paso

Ejemplo con una línea real del export:

| Cuenta | Producto | Centro de beneficio | 008.2026 | 009.2026 |
|---|---|---|---|---|
| 705000 LIMPIEZA… | S_70504 LIMPIEZA CHECK OUT | CTSBCNBAI0033_04.01 | -132,26 | -314,04 |

1. **Lee el export.** Busca la fila de cabecera ("Cuenta de mayor") y las columnas de periodo (`008.2026`, `009.2026`…). Puede haber uno o varios periodos. Las celdas vacías cuentan como 0. Solo se usan la empresa, la cuenta, el producto, el centro de beneficio y los importes.
2. **Comprueba la empresa.** El export debe ser de una sola empresa (aquí `CTS00`), y tiene que ser la misma que la de la hoja maestra (`maestro_tb_CTS00.xlsx`).
3. **Filtra.** Suma las líneas que solo se distinguen por columnas que la TB no usa (centro de coste, tarea…) y quita las que quedan con todos los meses a 0 y las cuentas marcadas como excluidas en `Cuentas`.
4. **Limpia el centro de beneficio.** Quita el prefijo `AT-` si lo hay.
5. **Calcula el servicio.** Si el producto empieza por `S_`, el servicio es ese código. Si no, es la cuenta. → `S_70504`
6. **Calcula la descripción.** El texto del producto si es un servicio `S_`. Si no, el texto de la cuenta. → `LIMPIEZA CHECK OUT`
7. **Calcula el asset** a partir del centro de beneficio (ver `Equivalencias` y `Reglas`). → `BAI0033`
8. **Reclasifica** si la línea está en `Reclasificaciones`.
9. **Asigna categoría, CCAA 1 y CCAA 2.** La categoría sale de `Categorias`: la fila de cuenta + servicio + asset si existe y, si no, la fila general de cuenta + servicio. CCAA 1 y CCAA 2 salen de la cuenta, en `Cuentas`. → `Checkout Cleaning Services (Final cleaning)`, `PL`
10. **Agrupa** por clave y mes y suma. La clave es la misma que la columna K de la TB:
    `705000 S_70504 BAI0033 Checkout Cleaning Services (Final cleaning)`
11. **Cuadra.** Cada mes debe sumar 0, y el total debe coincidir con el del export después del filtro.

## Resultado

Una fila por clave y mes, con estas columnas:

| Columna | Contenido | Ejemplo |
|---|---|---|
| `empresa` | Sociedad SAP | `CTS00` |
| `cuenta` | Cuenta de mayor | `705000` |
| `servicio` | Servicio `S_…` o la cuenta | `S_70504` |
| `descripcion` | Texto del servicio o de la cuenta | `LIMPIEZA CHECK OUT` |
| `asset` | Edificio, ciudad o `Manco` | `BAI0033` |
| `categoria` | Categoría de producto de la TB | `Checkout Cleaning Services (Final cleaning)` |
| `ccaa1`, `ccaa2` | Agrupación de cuentas anuales | |
| `budget` | Vacío de momento | |
| `clave` | Igual que la columna K de la TB | `705000 S_70504 BAI0033 Checkout…` |
| `mes` | Mes del movimiento | `2026-09` |
| `importe` | Movimiento del mes, no saldo, con el signo de SAP | `-1234,56` |

No hay filas con importe 0. El CSV se abre con doble clic en Excel (separador `;`, coma decimal).

## Hoja maestra de configuración

Toda la configuración de una empresa está en un único libro Excel, `maestro_tb_<empresa>.xlsx` (para CTS00, `maestro_tb_CTS00.xlsx`), con una pestaña por tabla. Hay un libro por empresa: la empresa la da el nombre del fichero, no una columna. Las pestañas que empiezan por `_` (por ejemplo, `_Notas`) se ignoran.

Las cabeceras en turquesa son columnas que usa el proceso. Las grises (`descripcion`) son informativas: el proceso no las usa para mapear y van al final de cada tabla. Cada cabecera lleva un comentario de Excel con su significado.

Los códigos (cuentas, servicios, centros, assets) tienen que ser celdas de texto: `0026` tiene que seguir siendo `0026`, y `705000` no puede convertirse en `705000.0`.

En Airflows, la hoja maestra de cada empresa está en **Ficheros** (`Admin.Files`), en el registro llamado `Maestro TB <empresa>` (por ejemplo, `Maestro TB CTS00`). El proceso la lee en cada carga. En local se pasa con `--maestro`.

**Cómo se cambia la configuración:**

1. En Airflows, en **Ficheros** (`Admin.Files`), descargar el fichero del registro `Maestro TB <empresa>`.
2. Editarlo.
3. Sustituir el fichero en ese mismo registro. Tiene que haber un único registro con ese nombre.

La hoja maestra no se comprueba al guardarla: si tiene algún error, aparece en el `Log` de la siguiente carga de un export de SAP. El `Log` de cada carga anota la fecha de modificación de la hoja maestra usada. No se guarda historial, así que conviene conservar una copia antes de cambiarla. Cambiar la hoja maestra **no cambia** los meses ya cargados: para aplicarla a un mes, hay que volver a procesar su export (ponerlo en `pendiente` o subirlo de nuevo).

### Pestaña `Reglas`: patrón de los centros de beneficio de edificio

Indica cómo se lee un centro de beneficio de edificio o de piso. Una sola fila. Para CTS00:

| patron_edificio | digitos_numero |
|---|---|
| `^CTS[A-Z]{3}(?P<edificio>[A-Z]{3})(?P<numero>\d{3,4})(_.*)?$` | `4` |

El centro de beneficio se lee en partes: `CTS` + ciudad (3 letras) + edificio (3 letras) + número [+ `_planta.puerta`]. El asset es edificio + número completado a 4 dígitos.

| Centro de beneficio | Asset |
|---|---|
| `CTSBCNBAI0033_04.01` | `BAI0033` |
| `CTSBCNBAI0033` | `BAI0033` |
| `CTSMADGTF038_PB.IZ` | `GTF0038` |

Solo se toca si SAP cambia la forma de codificar los centros.

### Pestaña `Equivalencias`: centros de beneficio con un asset distinto

| Columna | Contenido |
|---|---|
| `centro_beneficio` | Código SAP completo (fijos, ciudades) o base del edificio, sin `_planta.puerta` |
| `asset` | Asset en la TB |

Contenido de CTS00 (el motivo no está en la hoja):

| centro_beneficio | asset | Motivo |
|---|---|---|
| `CTS01` | `Manco` | Sociedad (fijo) |
| `CTS01_COSFIJ` | `Manco` | Costes fijos |
| `CTS0000BCN` | `BCN` | Ciudad |
| `CTS0000MAD` | `MAD` | Ciudad |
| `CTS0000VAL` | `VAL` | Ciudad |
| `CTS0000BIO` | `BIO` | Ciudad |
| `CTSBCNCON0012` | `CCD0012` | Concordia 12: SAP y la TB usan códigos distintos |
| `CTSBCNCOR0207` | `CSG0207` | Còrsega 207: ídem |
| `CTSBCNCOR0396` | `CSG0396` | Còrsega 396: ídem |
| `CTSBCNMAD0110` | `AVM0110` | Avenida Madrid 110: ídem |
| `CTSVLCFAC0002` | `PFC0002` | Paseo Facultades 2: ídem |
| `CTSMADDCT075` | `DCT075` | La TB usa 3 dígitos; la regla daría `DCT0075` |
| `CTSBCNROB067A` | `ROB067A` | La TB usa 3 dígitos y letra; la regla no admite la letra |
| `CTSBCNROB067B` | `ROB067B` | Ídem |

Se busca así:

1. El centro completo. Así se resuelven los fijos y las ciudades.
2. La base del centro, sin el sufijo de piso. Así una sola fila de edificio sirve para todos sus pisos: `CTSBCNCON0012_BJ.01` → `CCD0012`, `CTSMADDCT075_01.IZ` → `DCT075`.
3. Si la base no está en la tabla, se aplica la regla del patrón (pestaña `Reglas`).

**Cuándo editarla:** cuando aparezca un edificio nuevo cuyo código en la TB no coincida con el de SAP, o un nuevo centro fijo o de ciudad. Si un centro no encaja en nada, el programa da error y lo nombra.

### Pestaña `Cuentas`: CCAA de cada cuenta y cuentas excluidas

| Columna | Contenido |
|---|---|
| `cuenta` | Cuenta de mayor. Una fila por cuenta |
| `ccaa1`, `ccaa2` | Agrupación de cuentas anuales. Vale para todas las líneas de la cuenta |
| `excluida` | `sí` si la cuenta no pasa a la TB; vacío si pasa |
| `descripcion` | Informativa: texto de la cuenta en SAP |

- En la TB, las CCAA dependen solo de la cuenta: ninguna cuenta tiene dos. Por eso están aquí y no en cada combinación.
- Una cuenta que pasa a la TB necesita `ccaa1` y `ccaa2`. Si llega del export una cuenta que no está, el programa da error y la nombra con su texto.
- Una cuenta excluida no necesita CCAA. Se excluye porque neta 0 en el mes (en CTS00, `570000`, caja: se reparte por unidades). Si algún mes no neta 0, el programa da error en lugar de quitarla, porque quitarla descuadraría la TB.

Se generó una vez desde la TB de 09.2026 (CCAA de la pestaña `TB`) y la antigua pestaña `Excluidas`.

**Cuándo editarla:** cuando SAP empiece a usar una cuenta nueva.

### Pestaña `Reclasificaciones`: cambios de servicio

Algunas líneas llegan de SAP con un servicio que no encaja con la fila de la TB donde contablemente deben ir. Esta tabla les cambia el servicio.

| Columna | Contenido |
|---|---|
| `cuenta` | Cuenta de mayor |
| `servicio_sap` | Servicio calculado del export |
| `centro_beneficio` | Opcional. Si se rellena, solo afecta a ese centro (limpio, sin `AT-`) |
| `servicio_tb` | Servicio con el que debe quedar |

Contenido inicial de CTS00: **vacía**. Con los datos de septiembre de 2026, la TB no necesita ninguna reclasificación: todos los importes van con el servicio que trae SAP.

- Cada fila se aplica en todos los meses y en todas las ejecuciones. Si una reclasificación deja de valer, hay que borrar la fila.
- Una fila sin centro afecta a todas las líneas de esa cuenta y servicio. Una fila con centro gana a una sin centro.
- Son decisiones contables, no reglas: conviene dejar constancia fuera de la hoja de quién aprobó cada fila.

### Pestaña `Categorias`: categoría de cada cuenta + servicio

Sustituye al BUSCARV contra la columna K de la TB.

| Columna | Contenido |
|---|---|
| `cuenta` | Cuenta de mayor |
| `servicio` | Servicio, ya reclasificado |
| `asset` | Vacío en la fila general. Con asset, excepción solo para ese asset |
| `categoria` | Categoría de producto de la TB |
| `descripcion` | Informativa: texto del servicio |

- Cada cuenta + servicio tiene una **fila general**, sin asset, que vale para cualquier asset, también para los edificios nuevos.
- Cuando un asset lleva otra categoría, se añade una **excepción** con ese asset, que gana a la general. Por ejemplo, `629000 S_62901` es "Other expenses building" en general, pero "Other costs Valencia" en `VAL` y "Other expenses" en `Manco`.
- La categoría va por cuenta + servicio: un servicio conocido en una cuenta nueva necesita su fila.
- Si una línea no tiene fila (ni general ni de su asset), el programa da error y nombra el servicio, su texto y sus cuentas.

Se generó una vez desde la TB de 09.2026: la general de cada cuenta + servicio es la categoría que tienen más assets, y las excepciones son los assets con otra. Las 15 combinaciones con más de una categoría en la TB se resolvieron con la categoría que tenía importe en ago/sep-26 o, si no, la del último mes con importe. Con esta tabla, cada combinación existente en la TB conserva su categoría.

**Cuándo editarla:** cuando SAP empiece a usar un servicio nuevo (fila general), o cuando contabilidad quiera otra categoría para un asset (excepción) o para todos (cambiar la general).

## Errores habituales

| Error | Qué hacer |
|---|---|
| Centro de beneficio sin asset | Añadirlo a `Equivalencias` o revisar si es un error de SAP |
| Servicio sin categoría | Añadir a `Categorias` la fila general de cuenta + servicio |
| Cuenta sin CCAA | Añadir la cuenta a `Cuentas` con `ccaa1` y `ccaa2` |
| Fila incompleta o repetida en `Categorias` | Rellenar `cuenta`, `servicio` y `categoria`, y dejar una sola fila por cuenta + servicio + asset (una sola general) |
| Cuenta repetida, sin CCAA o con `excluida` no válido en `Cuentas` | Una fila por cuenta; `ccaa1` y `ccaa2` si no está excluida; `excluida` es `sí` o vacío |
| Cuenta excluida que no neta 0 | Revisar en SAP. Si debe pasar a la TB, quitar la marca `excluida` en `Cuentas` y darle CCAA |
| Reclasificación en conflicto | Una línea del export cae en dos filas de la misma cuenta y servicio, las dos con el mismo centro o las dos sin centro: dejar una |
| Fila incompleta en `Reclasificaciones` | Rellenar `cuenta`, `servicio_sap` y `servicio_tb`; solo `centro_beneficio` es opcional |
| Varias empresas en el export | Exportar de SAP una sola sociedad |
| La hoja maestra debe llamarse `maestro_tb_<empresa>.xlsx` | Renombrar el fichero: de su nombre sale la empresa |
| Periodo que no es un mes (`013.2026`…`016.2026`) | Exportar de SAP solo los periodos mensuales `001`-`012` |
| Importe no numérico | Revisar la celda que indica el mensaje: el export no se ha tocado a mano |
| Falta una columna, la fila «Cuenta de mayor» o el título «Trial Balance» | El fichero no es el export de Trial Balance de SAP, o le faltan dimensiones |
| No se puede abrir como libro Excel | El fichero adjunto no es un xlsx: subir el export tal como sale de SAP |
| No hay hoja maestra para la empresa | Crear en Airflows el registro `Maestro TB <empresa>` en Ficheros, partiendo de la hoja maestra de otra empresa. En local, `maestro_tb_<empresa>.xlsx` |
| Hay varios ficheros `Maestro TB <empresa>` | Dejar uno solo en Ficheros: el proceso no elige |
| El mes no suma 0 / no cuadra con el export | Revisar el export: suele faltar alguna cuenta o un periodo está incompleto |
