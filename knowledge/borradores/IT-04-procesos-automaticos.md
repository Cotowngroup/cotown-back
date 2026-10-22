# IT-4. Procesos automáticos, emails y documentos

> Manual técnico · Borrador v0.1 · 2026-10-20 · Las marcas **[PREGUNTA Tn]** se resuelven en la ronda de preguntas y desaparecen de la versión final.

## 4.1 Propósito

Este capítulo describe los procesos que se ejecutan solos en el servidor de servicios: la facturación, la generación de PDF de facturas y contratos, la firma electrónica, las cargas masivas desde Excel, el envío de emails, el cálculo de rentas máximas y el archivo en SharePoint. También explica cómo se generan los documentos (PDF y Excel). Los procesos programados que se ejecutan dentro de la base de datos de Airflows se describen en *Arquitectura y plataforma* y en el capítulo de triggers.

## 4.2 Ejecución y control

Cada proceso es un programa Python (`back/app/batch_<nombre>.py`) que el `crontab` del servidor lanza dentro del contenedor `back` mediante el script `dobatch.sh`. Ese script crea un fichero de bloqueo por proceso para que nunca haya dos ejecuciones simultáneas del mismo proceso, y lo borra al terminar. Una tarea diaria a las 03:00 elimina los bloqueos que hubieran quedado huérfanos.

| Proceso | Frecuencia | Log |
|---|---|---|
| Facturación (`billing`) | Cada 15 min (:00, :15, :30, :45) | `batch_billing.log` |
| PDF de facturas (`printbill`) | Cada 15 min (:03, :18…) | `batch_printbill.log` |
| Contratos (`printcontract`) | Cada 15 min (:06, :21…) | `batch_printcontract.log` |
| Cargas de Excel (`processload`) | Cada 15 min (:09, :24…) | `batch_processload.log` |
| Envío de emails (`sendemail`) | Cada 15 min (:12, :27…) | `batch_sendemail.log` |
| Comprobación de contratos (`checkcontract`) | Diario, 01:00 | `batch_printcontract.log` |
| Archivo de facturas (`sharepoint`) | Diario, 02:00 | `batch_sharepoint.log` |
| Copia a SharePoint (`rclone`) | Diario, 02:30 | `sharepoint.log` |
| Rentas máximas (`law`) | Diario, 05:00 | `batch_law.log` |
| Escucha de emails (`listen.py`) | Permanente | Salida del contenedor |

Los logs están en `~/app/log/` del servidor, rotan al llegar a 1 MB (se conservan 5 copias) y los recoge Promtail para consultarlos en Grafana. Cada proceso registra al final cuántos elementos ha procesado.

Todos los procesos son **reentrantes**: marcan lo que ya han tratado (una factura enlazada, un PDF guardado, una fecha de envío), de modo que si una ejecución falla, la siguiente retoma lo pendiente sin duplicar.

## 4.3 Facturación

Genera las facturas, recibos y cobros de todas las modalidades. Trabaja con SQL directo sobre la base de datos y confirma cada elemento por separado, de modo que un error en una reserva no impide facturar las demás. La fecha de corte inicial está en la configuración (`BILLDATE`): no se factura nada anterior.

Se ejecuta en este orden:

| Paso | Qué factura | Criterio | Resultado |
|---|---|---|---|
| **1. Cobros puntuales** | Membership fee, garantía, check-in y check-out | Cobros pagados (o de check-in y check-out, aunque no estén pagados) sin factura | Membership fee, check-in y check-out: **factura de Cotown**. Garantía: **recibo del propietario**; en Barcelona, con una línea aparte para la fianza legal INCASÒL. |
| **2. Mensualidades B2C** | Renta y servicios del mes | Meses vencidos (`Rent_date` hasta hoy) de reservas en firma de contrato o posteriores y no facturados | Un **cobro** por la suma de todo. Una **factura o recibo del propietario** con renta, suministros, gastos, mobiliario y extras de tipo renta. Una **factura del prestador de servicios** con servicios y extras. Si propietario y prestador son el mismo, todo va en un único documento. |
| **3. Mensualidades de grupos** | Renta y servicios de grupos B2B | Meses vencidos de grupos confirmados o en curso | Como el anterior, al pagador del grupo, con una línea por piso y el número de plazas; cobro por transferencia. |
| **4. Extras puntuales B2C** | Servicios adicionales con fecha | Extras cuya fecha ha llegado | Un cobro y una factura del proveedor del servicio por cada extra. |
| **5. Extras de grupos** | Servicios adicionales de grupos | Ídem | Ídem, al pagador del grupo. |
| **6. Contratos LAU y otros** | Renta mensual | Contratos vigentes con renta, sin factura en el mes en curso | Cobro por el terminal de Vandor y factura del propietario en la serie LAU, con "Renta mensual" o "Indemnización por ocupación inconsentida", más los extras pendientes. |
| **7. Facturas manuales** | Facturas creadas a mano en Airflows | Emitidas, con reserva y sin cobro | Crea el cobro correspondiente. |

**Reglas comunes:**

- **Factura o recibo**: el propietario emite recibo en lugar de factura si así está configurado en su ficha (`Receipt`). La garantía es siempre recibo; el membership fee y los servicios de check-in y check-out, siempre factura de Cotown.
- **IVA de la renta**: el de la reserva; si no tiene, el del tipo de edificio; si tampoco, exento.
- **Terminal del cobro**: el del propietario; *delegado* si renta y servicios son de emisores con terminales distintos.
- **Medio de pago**: el del cliente (por defecto, tarjeta); en grupos, transferencia.

**Lo que hacen los triggers al emitir** (no el proceso):

- **Numeración**: al marcar la factura como emitida, el trigger asigna el número según el patrón del emisor (facturas, recibos, rectificativas y sus variantes LAU) y un contador por emisor y año, y fija la fecha de emisión. Una factura emitida no se puede modificar ni borrar.
- **Rectificativas**: al marcar una factura como rectificada, el trigger crea automáticamente la rectificativa con las líneas en negativo.
- **Total y management fee**: cada línea recalcula el total de la factura y, si el emisor no es Cotown, el management fee de la línea según la frecuencia de limpieza de la reserva (la frecuencia `marketplace` usa el porcentaje de marketplace del recurso).

## 4.4 PDF de facturas

Para cada factura o recibo emitido que aún no tiene documento:

1. Lee los datos de la factura (emisor, cliente, líneas, impuestos).
2. Calcula el desglose de impuestos (los importes de las líneas incluyen IVA).
3. Genera el PDF con la plantilla `templates/other/bill.html` (WeasyPrint). Si el cliente lo tiene configurado, la factura incluye la *rooming list* del grupo.
4. Guarda el PDF en la factura en Airflows (atributo *Documento*).
5. Lo envía por email cuando corresponde:
   - **Grupos B2B**: desde Cotown, a las direcciones de facturación de la reserva o del cliente, con copia a las direcciones del parámetro `B2B_BILL_CC`.
   - **Contratos LAU** con envío activado: desde Vandor.

Las facturas B2C no se envían por email: el residente las tiene en el portal.

## 4.5 Contratos y firma electrónica

### Reservas B2C

Para las reservas en firma de contrato o posteriores que aún no tienen contrato (y con entrada posterior a la fecha de corte `CONTRACTDATE`):

1. Comprueba que el cliente tenga tipo de documento, documento y dirección; si no, la reserva espera a la siguiente ejecución.
2. Elige la **plantilla**: la del propietario (contrato de renta) y la del prestador de servicios (contrato de servicios), primero la de su ubicación y, si no hay, la genérica. El tipo de plantilla depende de la reserva: residencia, habitación o piso. Las plantillas están en Airflows (*Propietarios › Plantillas de contrato*), escritas en Markdown con variables; si el cliente es extranjero y la plantilla tiene anexo en inglés, se añade al final.
3. Genera el PDF, con la firma del representante del propietario incrustada y marcas invisibles para colocar la firma y la fecha del cliente.
4. **En Barcelona** añade al contrato los anexos documentales del edificio y del recurso (los documentos marcados como *anexo de contrato*).
5. El contrato de servicios solo se genera si el prestador es distinto del propietario y hay importe de servicios.
6. Guarda los PDF en la reserva (*Contrato de renta*, *Contrato de servicios*).
7. Si el edificio tiene **contrato digital**, envía un sobre a DocuSign con el cliente como único firmante. Si no, el contrato queda para firma manual.

Cuando el cliente firma, DocuSign avisa al servicio de integración y la reserva pasa a *contrato*. Si la firma se anula, la reserva vuelve a *firma de contrato* y el contrato se regenera.

### Grupos B2B

1. Para los grupos confirmados o en curso sin contrato, genera los PDF (plantilla de piso o de habitación según el grupo) con los anexos de Barcelona. **No los envía.**
2. El personal revisa el contrato en Airflows y marca *Contrato OK*.
3. En la siguiente ejecución se envía a DocuSign con el pagador del grupo como firmante.
4. Los **anexos** de grupo (`Booking_group_annex`, por ejemplo para incorporar residentes) se generan con la plantilla `templates/other/annex.html` y se envían a firmar automáticamente.

### Comprobación diaria

Cada noche se consulta en DocuSign el estado de todos los sobres pendientes (contratos B2C, contratos de grupo y anexos) y se actualiza su estado en Airflows. Complementa los avisos de DocuSign, que solo cubren las reservas B2C.

## 4.6 Cargas masivas desde Excel

El personal sube un Excel en *Procesos › Cargas*. El proceso lo recoge, lo marca como *Procesando…* y trata cada hoja según su nombre:

| Hoja | Qué carga | Clave |
|---|---|---|
| **Recursos** | Pisos, habitaciones y plazas: propietario, prestador, tipologías, tarifa, uso, marca y características | Código del recurso |
| **Estados** | Periodos de no disponibilidad (bloqueos) | Recurso y fecha de inicio |
| **Valoraciones** | Valoraciones de recursos | Recurso y fecha de valoración |
| **Forecast** | Previsión de ocupación | Recurso y mes |
| **Stabilised** | Ocupación estabilizada | Recurso y mes |
| **Precios** | Precios base | Año, edificio, tipología de piso y de plaza |
| **Rooming** | Residentes de un grupo B2B | Grupo, código de residente y plaza |

**Formato común**: la cabecera está en la fila 2 y los datos empiezan en la fila 3. Las columnas con forma `Tabla.Campo` (por ejemplo `Owner.Name`) se traducen al identificador correspondiente; el resto se copian tal cual. Las hojas que empiezan por `_` y las de catálogos se ignoran. Para obtener una plantilla con el formato correcto, se descarga el informe Excel del mismo nombre.

Cada hoja se carga **entera o nada**: si una fila falla, no se carga ninguna fila de esa hoja. Al terminar, el proceso escribe en la carga el resultado (*Ok* o *Error*) y el detalle por fila de los errores.

## 4.7 Emails

### Circuito

1. **Alta**: un trigger o un proceso programado de Airflows (o el personal, para emails manuales) inserta una fila en *Emails* del cliente con la plantilla y la entidad a la que se refiere (normalmente la reserva).
2. **Filtro**: un trigger descarta los emails a clientes empresa (salvo el aviso de IPC) y los de plantillas desactivadas, y añade las copias (CC y CCO) configuradas para la marca.
3. **Aviso**: al guardarse, la base de datos emite una notificación.
4. **Envío inmediato**: el proceso de escucha (`listen.py`), siempre activo, recibe la notificación y envía el email en segundos.
5. **Respaldo**: cada 15 minutos, `sendemail` envía los que hayan quedado pendientes.
6. **Marcado**: una vez enviado, se guardan en la fila el asunto y el cuerpo definitivos y la fecha de envío. Un email con fecha de envío no se vuelve a enviar.

### Composición

Las plantillas están en Airflows (*Administración › Plantillas de email*). Cada plantilla tiene:

- Asunto y cuerpo en español y en inglés (editor de texto enriquecido). Se usa el idioma del cliente.
- Una consulta GraphQL que obtiene los datos de la entidad (reserva, cliente, edificio…) para rellenar las variables del texto.
- El remitente: Cotown o Vandor.
- Un indicador de activa o inactiva.

El envío se hace por SMTP de Microsoft 365, con la cuenta de Cotown o la de Vandor según el remitente.

Además de los emails a clientes, el servicio envía por correo los avisos internos de nuevos leads y las facturas de grupos y contratos LAU.

## 4.8 Rentas máximas (Ley de vivienda)

Cada día a las 05:00 recalcula, para cada piso, el **régimen de renta** y las **rentas máximas**, y las reparte entre sus habitaciones y plazas según su peso.

**Régimen:**

| Régimen | Cuándo |
|---|---|
| **Libre** | Fuera de Barcelona y Bilbao; o con gran reforma hace menos de 5 años; o con 150 m² o más sin un contrato LAU en los últimos 5 años; o en régimen de índice sin índice de referencia informado. |
| **LAU** | Con un contrato LAU en los últimos 5 años. La renta máxima es la última renta de ese contrato actualizada por IPC (+10 % si hubo reforma en los últimos 2 años). |
| **Índice** | Sin contrato LAU reciente; o cuando el índice de referencia es menor que la renta LAU actualizada. La renta máxima es el índice de referencia del piso. |

**Resultados** (en cada recurso): régimen, renta LAU máxima, renta máxima, gastos máximos repercutibles (IBI y comunidad del edificio, prorrateados por el peso, solo si se repercuten) y fecha en que el piso sale del régimen LAU (5 años después del último contrato).

El **peso** de cada habitación o plaza es el porcentaje del piso que representa y se mantiene en la ficha del recurso.

## 4.9 Archivo de facturas en SharePoint

Cada noche:

1. A las 02:00, el proceso descarga los PDF de las facturas y recibos emitidos en los dos últimos días y los organiza en carpetas: `Facturas|Recibos / emisor / año / mes / edificio / <piso>-<número>.pdf`.
2. A las 02:30, `rclone` copia esa estructura a SharePoint, en *DOC ACTUALIZADA › Departments › Financial › Documentación venta activos*.

El solape de dos días cubre cualquier retraso; los ficheros que ya existen se sobrescriben.

## 4.10 Documentos

### PDF

Se generan con WeasyPrint a partir de plantillas HTML (Jinja):

| Documento | Plantilla |
|---|---|
| Factura, recibo o rectificativa | `templates/other/bill.html` |
| Contratos de renta y de servicios | Plantillas de cada proveedor en Airflows (Markdown con variables) |
| Anexo de contrato de grupo | `templates/other/annex.html` |
| Certificado de residencia | `templates/other/cert.html` |
| Ficha legal del edificio | `templates/other/legal.html` |
| Declaración de devolución de fianza (INCASÒL, en catalán) | `templates/other/incasol.html` |

Las plantillas de contrato admiten variables de la reserva, el cliente, el recurso y el propietario, y funciones para importes en letra, meses, edades y fracciones.

### Informes Excel

Los informes del backoffice se generan a partir de tres ficheros por informe en `templates/report/`:

- `<informe>.xlsx`: la plantilla con el formato. La última fila sirve de modelo: su estilo, sus formatos de fecha y sus fórmulas se copian en cada fila de datos.
- `<informe>.<hoja>.sql` o `.graphql`: la consulta que llena cada hoja, con los filtros que llegan desde la pantalla (fechas, proveedores, año, estado…).
- `<informe>.<hoja>.json`: el orden de las columnas.

Para añadir un informe basta con crear esos ficheros. Informes disponibles:

| Área | Informes |
|---|---|
| Reservas | reservas, bookings (por estado), entradas y salidas próximas, documentación de reservas, cuestionarios, descuentos, semanal, reservas LAU |
| Inventario | recursos, edificios, disponibilidad, inventario, precios, tarifas, LTC |
| Ocupación y previsión | ocupación, forecast, stabilised |
| Facturación | facturas, ingresos, ingresos por propietario, pagos emitidos, pagos recibidos, management fees, marketplaces, devoluciones de garantía, previsión de devoluciones, remesas SEPA (Cotown, Vandor y terceros) |
| Regulatorio | INCASÒL, NRUA |
| Otros | propietarios, países, rooming list de un grupo (plantilla de carga) |

## 4.11 Fuentes

| Tema | Dónde está |
|---|---|
| Procesos | `back/app/batch_*.py`, `back/app/listen.py`, `back/app/dobatch.sh` |
| Lógica de facturación | `back/app/batch_billing.py`; numeración y management fee en los triggers `Billing.Invoice_B2_validate` e `Invoice_line_B1_change` |
| Contratos | `back/app/library/business/contract.py` |
| Emails | `back/app/library/business/send_email.py`; triggers `Customer.Customer_email_*` |
| Cargas | `back/app/library/business/load_*.py` |
| Plantillas | `back/app/templates/other/`, `back/app/templates/report/` |
| Programación real | `crontab` del usuario `cotown` en `back.cotown.com` |

## 4.12 Pendiente de confirmar

No hay puntos pendientes.
