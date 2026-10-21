# OP-6. Facturación y cobros

> Manual funcional · Borrador v0.1 · 2026-10-21 · Las marcas **[PREGUNTA On]** se resuelven en la ronda de preguntas y desaparecen de la versión final.

## 6.1 Propósito

Este capítulo explica qué se factura, quién lo emite, cuándo lo hace el sistema solo y qué tiene que hacer el personal: facturas, recibos y rectificativas; cobros con tarjeta, domiciliación, transferencia y otros medios; avisos de impago; management fees; y envío y archivo de las facturas.

## 6.2 Conceptos

| Concepto | Qué es |
|---|---|
| **Emisor** | Proveedor que emite el documento: Cotown, el **propietario** o el **prestador de servicios**. Cada uno tiene su propia numeración. |
| **Factura / recibo** | El propietario puede emitir **recibo** en lugar de factura si así está configurado en su ficha. La garantía es siempre recibo. |
| **Rectificativa** | Factura en negativo que anula otra ya emitida. Una factura emitida no se modifica ni se borra: se rectifica. |
| **Cobro** | Importe que el cliente debe pagar. Puede liquidar una o varias facturas del mismo mes (por ejemplo, la de renta del propietario y la de servicios del prestador). |
| **Tipo de cobro** | Membership fee, garantía, servicios (mensualidades y extras), check-in o check-out. |
| **Medio de pago** | Cómo paga el cliente. El de sus cobros sale de su ficha (por defecto, tarjeta); en grupos, transferencia. |
| **Terminal (TPV)** | Terminal de Redsys por el que se cobra con tarjeta: el del propietario, *Cotown*, *Vandor* o *delegado* (cuando un cobro reúne renta y servicios de emisores con terminales distintos). |
| **Producto** | Concepto facturable, con su tipo (renta, servicios mensuales, servicios adicionales, refacturación, fee, garantía) y su IVA. |
| **Management fee** | Comisión de Cotown sobre cada línea que facturan los propietarios. Su porcentaje sale del recurso según la frecuencia de limpieza de la reserva, o el de marketplace si la reserva viene de uno. |

### Medios de pago

| Medio | Uso |
|---|---|
| **Tarjeta/TPV** | Pago con tarjeta desde el portal (Redsys). Medio por defecto. |
| **Domiciliación** | Cargo en la cuenta del cliente. |
| **Transferencia** | Transferencia del cliente. Medio por defecto de los grupos. |
| **TPV/Cotown BCN, MAD, VLC** y **TPV/Vandor MAD, VLC, BCN** | Cobro con tarjeta en un terminal físico de la oficina. |
| **De la garantía** | Se cobra de la garantía depositada (retenciones al salir). |
| **Garantía trasladada** | Garantía que se traspasa de otra reserva (cambio de habitación o extensión). |
| **Rectificativa** | Cobro anulado por una rectificativa. |
| **Varios medios de pago** | Cobro pagado en parte por medios distintos. |
| **Otros** (*Portal*, *Portal - Pendiente*, *Garantía diferencia*, *Validación en curso*, *Transferencia - Servicios B2B*, *Domiciliación - Puiggali i Dosta*) | Casos particulares que gestiona Administración. |
## 6.3 Qué factura el sistema y cuándo

El proceso de facturación se ejecuta **cada 15 minutos** y factura todo lo que haya vencido:

| Qué | Cuándo | Qué genera |
|---|---|---|
| **Membership fee** | Al pagarse | Factura de **Cotown**. |
| **Garantía** | Al pagarse | **Recibo del propietario**. En Barcelona, con una línea aparte para la fianza INCASÒL. |
| **Check-in / check-out** de pago | Al crearse el cobro (aunque no esté pagado) | Factura de **Cotown**. |
| **Mensualidad B2C** | Al empezar cada mes de estancia, en reservas desde *firma de contrato* | Un **cobro** por el total del mes; una **factura o recibo del propietario** (renta, suministros, gastos, mobiliario y extras de tipo renta) y una **factura del prestador** (servicios y extras). Si propietario y prestador son el mismo, un solo documento. |
| **Mensualidad de grupo** | Al empezar cada mes, en grupos confirmados o en curso | Lo mismo, al pagador, con una línea por piso y número de plazas; cobro por transferencia. |
| **Servicios adicionales** | En la próxima facturación, en su fecha o mes a mes entre dos fechas, según el tipo | Un cobro y una factura del emisor del servicio por cada extra. |
| **Limpieza de salida de grupos** | Al salir los residentes de cada piso | Factura de Cotown al pagador. |
| **Contratos LAU y otros** | Cada mes | Ver *Contratos LAU y otros*. |
| **Facturas manuales** | Al emitirlas | Crea su cobro si no lo tienen. |

**IVA de la renta**: el de la reserva; si no tiene, el del tipo de edificio; si tampoco, exento. Los servicios y los extras, el de su producto.

**Al emitirse un documento**, el sistema le asigna número según el patrón del emisor (en su ficha: uno para facturas, otro para recibos y otro para rectificativas, con el año y un correlativo de 5 dígitos) y un contador por emisor y año, fija la fecha de emisión y lo bloquea. Después genera el **PDF** y lo guarda en la factura.

## 6.4 Tareas

### Seguir los cobros con tarjeta

- Al crearse un cobro mensual con tarjeta, el residente recibe el email *pago* con el enlace al portal y, si no paga, un recordatorio a los 6 días (el de los 11 días no se envía mientras no tenga plantilla).
- El residente paga desde el portal. Redsys confirma el pago y el sistema lo registra (fecha, pedido y código de autorización). Una confirmación repetida no tiene efecto.
- Si el pago se deniega, el cobro sigue pendiente y el residente puede reintentarlo.
- Para pagar, el residente debe tener completos sus datos fiscales.

### Registrar un cobro manual

**Cuándo**: el cliente paga por transferencia, domiciliación, en la oficina o por cualquier medio distinto de la tarjeta en el portal.

**Cómo**: en el cobro, indicar el **medio de pago** y la **fecha de pago** (y el importe pagado si es distinto).

**Qué hace el sistema**: genera una referencia de pago con autorización *MANUAL* y, según el tipo de cobro:

- **Membership fee**: avanza la reserva (*solicitud pagada*, *alternativas pagada* o *confirmada*).
- **Garantía**: registra la garantía depositada y avanza la reserva a *firma de contrato* si corresponde.

Si la reserva no puede avanzar (por ejemplo, por una validación), el pago se guarda igualmente y el problema queda en el registro de la reserva.

### Gestionar las domiciliaciones

**Generar la remesa**: el informe Excel **SEPA** (*Procesos › Informes*) lista todos los cobros domiciliados **sin pagar**, en tres hojas según el terminal del cobro: *Cotown*, *Vandor* y *terceros* (delegado, los cobros por cuenta de los propietarios). Para cada cobro da el titular, el IBAN, la referencia del mandato (número de reserva), la secuencia (*RCUR*), la referencia de la orden (número de cobro), el importe y el concepto (*RENTA* y el mes, *BOOKING FEE*, *DEPOSITO*, *CHECKIN*). Con ese Excel se prepara la remesa en el banco.

**Marcar los cobros como pagados**: una vez cargada la remesa, se informa a mano la **fecha de pago** de cada cobro domiciliado.

**Recibos devueltos**: no se registran como tales; el cobro devuelto simplemente no se marca como pagado. Por eso sigue apareciendo en *Cobros pendientes* y vuelve a salir en el siguiente informe SEPA.

**Comprobar**: que el cliente tiene el **IBAN** informado; sin él, la línea de la remesa sale vacía.

### Seguir los impagos

- **Dashboard › Administración › Cobros pendientes**: lista los cobros sin pagar. El personal registra en cada uno las fechas del **aviso 1, 2 y 3** de impago.
- **Recargo por demora**: se factura como servicio adicional (productos *Recargo demora mes anterior* o *Recargo por demora Cotown*).
- En la salida, lo pendiente se puede cobrar **de la garantía** (ver *Reservas B2C*).

Los días entre avisos y el importe del recargo no son fijos: los decide Administración en cada caso.

### Facturar un concepto extra

**Cómo**: añadir un **servicio adicional** a la reserva (o al grupo, o al contrato LAU):

| Tipo | Se factura |
|---|---|
| **Próxima factura** | En la siguiente ejecución de la facturación. |
| **Puntual** | En la fecha indicada. |
| **Recurrente** | Cada mes entre la fecha de inicio y la de fin. |

Si no se indica, el emisor es Cotown (o el propietario, si el producto es de tipo renta), y el IVA y el concepto salen del producto.

### Crear una factura manual

**Cuándo**: conceptos que no encajan como servicio adicional o correcciones puntuales.

**Cómo**: crear la factura con tipo, emisor, cliente, reserva, medio de pago, concepto y líneas (producto, importe, recurso). Para partir de otra, indicarla en **Copiar de**: el sistema copia cabecera y líneas. Al marcarla como **emitida**, se numera y queda bloqueada, y el proceso de facturación crea su cobro.

**Reglas**: la factura debe tener reserva; sin recurso en una línea, se toma el piso de la reserva; el importe debe ser positivo.

### Rectificar una factura

**Cómo**: en la factura emitida, marcar **Rectificar**.

**Qué hace el sistema**: crea y emite la **rectificativa** con las mismas líneas en negativo, numerada con el patrón de rectificativas del emisor.

**Después**: si había que facturar otro importe, crear la factura correcta (puede partir de la original con *Copiar de*). Si el cobro ya estaba pagado, gestionar la devolución.

Los **recibos** sí se pueden borrar mientras no estén pagados; las facturas, nunca.

### Ajustar una mensualidad antes de facturarla

En el detalle de precios de la reserva, cada mes puede llevar un **descuento** sobre la renta o los servicios, en importe o en porcentaje (el sistema calcula el otro), siempre con su **motivo** (promoción, comercial, mantenimiento, upgrade, yield management, capex…). *Aplicar a todos* lo copia al resto de meses. Una vez facturado el mes, ya no se puede cambiar: hay que rectificar.

### Management fees

**Qué hace el sistema**: en cada línea de una factura de un propietario (no de Cotown), fija el porcentaje de management fee:

| Caso | Porcentaje del recurso que se aplica |
|---|---|
| Reserva de marketplace | *Marketplace* |
| Sin servicios de limpieza | *Sin servicios* |
| Limpieza semanal | *Servicio premium* |
| Limpieza quincenal (o sin indicar) | *Servicio estándar* |
| Limpieza mensual | *Servicio mensual* |
| Sin limpieza (*sin*) | *0 % Management fee* |

**Qué hacer**: mantener los porcentajes en cada piso (ver *Inventario y precios*) y la frecuencia de limpieza en cada reserva. Los management fees del mes se consultan en el informe de **management fees** y SAP los obtiene por la integración contable.

### Envío y archivo de facturas

- **B2C**: no se envían por email; el residente las tiene en el portal.
- **Grupos**: se envían por email desde Cotown a las direcciones de facturación del grupo (o del cliente), con copia al equipo de Cotown; pueden incluir la rooming list.
- **Contratos LAU** con envío activado: desde Vandor.
- **Archivo**: cada noche se copian a SharePoint (*DOC ACTUALIZADA › Departments › Financial › Documentación venta activos*), organizadas por tipo, emisor, año, mes y edificio.
- **Descargas**: el informe de facturas permite descargar en ZIP las facturas y recibos de un periodo.

### Contabilidad (SAP)

SAP obtiene cada día del sistema los clientes, facturas, cobros y management fees. Para que lleguen bien, hay que mantener en Airflows los **códigos SAP** de los proveedores (emisores), productos, recursos y medios de pago. Solo se envían los emisores, productos y medios de pago marcados para SAP.

## 6.5 Automático y manual

| Qué | A / M |
|---|---|
| Facturas, recibos y cobros de membership fee, garantía, check-in/out, mensualidades, extras y limpiezas de grupo | A |
| Numeración, PDF, envío a grupos y LAU, archivo en SharePoint | A |
| Email de pago y recordatorios de cobros con tarjeta | A |
| Registro de pagos con tarjeta | A |
| Registro de cobros manuales | M |
| Remesa de domiciliaciones (informe SEPA) | A (informe); M (remesa en el banco y marcar pagados) |
| Avisos de impago y recargos | M |
| Servicios adicionales, facturas manuales y rectificativas | M |
| Descuentos por mes | M |
| Management fee por línea | A |
| Envío a SAP | A (lo consulta SAP) |

## 6.6 Excepciones

| Situación | Qué pasa | Qué hacer |
|---|---|---|
| Hay que cambiar una factura emitida | No se puede modificar ni borrar. | Rectificarla y emitir otra. |
| El residente no puede pagar en el portal | Le faltan datos fiscales. | Completar sus datos o registrar el pago a mano. |
| Un mes no se ha facturado | La reserva no ha llegado a *firma de contrato*, o el mes aún no ha empezado. | Revisar el estado de la reserva. |
| Una factura de propietario lleva un management fee incorrecto | La frecuencia de limpieza de la reserva o el porcentaje del piso no son los correctos. | Corregirlos para las siguientes facturas; las emitidas, rectificarlas si hace falta. |
| Una factura no llega a SAP | Falta el código SAP del emisor, del producto o del medio de pago, o no están marcados para SAP. | Completar los códigos. |

## 6.7 Fuentes

| Tema | Dónde está |
|---|---|
| Facturación y cobros | Proceso automático de facturación (cada 15 minutos) |
| Numeración, rectificativas, copia y management fee | Reglas de la base de datos de las facturas |
| Registro de pagos | Reglas de la base de datos de los cobros; servicio de integración (Redsys) |
| PDF y envío | Proceso automático de PDF de facturas |
| Archivo en SharePoint | Proceso automático nocturno |
| Contabilidad | Integración contable del servicio de integración |

## 6.8 Pendiente de confirmar

| Tema | Quién o qué lo confirma |
|---|---|
| — | — |
