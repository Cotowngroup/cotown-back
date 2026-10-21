# OP-3. Reservas B2C

> Manual funcional · Borrador v0.1 · 2026-10-20 · Las marcas **[PREGUNTA On]** se resuelven en la ronda de preguntas y desaparecen de la versión final.

## 3.1 Propósito

Este capítulo explica el ciclo de vida de una reserva individual (B2C), desde la solicitud hasta la devolución de la garantía: qué estados atraviesa, qué hace el sistema solo en cada uno y qué tiene que hacer el personal para que avance. Incluye los cambios durante la estancia (salida anticipada, extensión y cambio de habitación), los descartes y las cancelaciones.

Algunos pasos tienen su propio capítulo, al que se remite: contratos y garantías (*Contratos, garantías e INCASÒL*), facturas y cobros (*Facturación y cobros*), entradas, salidas y revisiones (*Operación diaria*) y emails y portal (*Comunicación con el residente*).

## 3.2 Conceptos

| Concepto | Qué es |
|---|---|
| **Periodo contratado** | Fechas desde y hasta de la reserva. Es lo que se factura. |
| **Fechas reales** | Fechas de check-in y check-out: cuándo entra y sale realmente el residente. Deben estar dentro del periodo contratado. |
| **Recurso asignado** | Piso, habitación o plaza concretos. La solicitud pide una tipología en un edificio; el recurso lo asigna el personal. |
| **No cambiar asignación** | Marca que impide cambiar el recurso asignado (por ejemplo, porque se ha prometido una habitación concreta). |
| **Plazo de pago** (*válida hasta*) | Fecha límite para pagar el membership fee. Mínimo 2 días desde la asignación. |
| **Plazo de documentación** | Fecha límite para aportar la documentación: 14 días desde la confirmación. |
| **Garantía teórica / depositada / devuelta** | Importe que se pide, importe que ha pagado el residente e importe que se le devuelve. |
| **Tipo de reserva** (*limitada / recreativa*) | Obligatorio en recursos con renta limitada: *limitada* aplica las rentas máximas; *recreativa*, el precio libre (estancia vacacional). |
| **Lista negra** | Marca del cliente que impide que sus reservas avancen, salvo que la reserva marque *Ignorar lista negra*. |
| **Reserva origen / destino** | Enlace entre dos reservas de un cambio de habitación (*CHA*) o de una extensión registrada como reserva nueva (*EXT*). |

## 3.3 Estados

![Ciclo de vida de la reserva B2C](../diagramas/Ciclo%20reserva%20B2C%20v2.png)

| Estado | Significado | Cómo sale de él |
|---|---|---|
| **Solicitud** | Pedida, sin recurso. | Al asignar recurso → *pendiente de pago*. Al enviar alternativas → *alternativas*. |
| **Solicitud pagada** | Como la anterior, con el membership fee ya pagado. | Al asignar recurso → *confirmada*. |
| **Alternativas** (pagada o no) | Se han propuesto alternativas al cliente. | El cliente acepta una → vuelve a *solicitud* (o *solicitud pagada*). |
| **Pendiente de pago** | Recurso asignado; falta pagar el membership fee. | Pago → *confirmada*. Vence el plazo → *caducada*. Vence el plazo de documentación → *documentación KO*. |
| **Caducada** | No pagó a tiempo. | Ampliar el plazo → *pendiente de pago*. A los 5 días → *descartada*. |
| **Confirmada** | Membership fee pagado. | Documentación aprobada (o no exigida) → *documentación OK*. Vence el plazo → *documentación KO*. |
| **Documentación KO** | No aportó la documentación a tiempo. | Lo gestiona el personal a mano. |
| **Documentación OK** | Documentación aprobada. Se emite el cobro de la garantía. | Garantía pagada (o cero) → *firma de contrato*. |
| **Firma de contrato** | Contrato generado y enviado a firmar. | Firmado → *contrato*. |
| **Contrato** | Contrato firmado. | Se informa la fecha de llegada → *check-in confirmado*. Llega la fecha de entrada → *check-in*. |
| **Check-in confirmado** | Fecha y hora de llegada conocidas. | Llega la fecha → *check-in*. |
| **Check-in** | Día de entrada. | El personal confirma la entrada → *in house*. |
| **In house** | Residente alojado. | Llega la fecha de salida → *check-out*. |
| **Check-out** | Día de salida. | El personal confirma la salida → *revisión*. |
| **Revisión** | Pendiente de revisar el alojamiento. | Revisión correcta → *devolver garantía*. |
| **Devolver garantía** | Pendiente de devolver la garantía. | Se registra la devolución sin retención temporal → *finalizada*. |
| **Finalizada** | Reserva cerrada. | — |
| **Descartada pagada** | Descartada con el membership fee pagado. | Se registra la devolución del membership fee → *descartada*. |
| **Descartada** | Descartada. | *Reactivar* → *solicitud* (o *solicitud pagada*). |
| **Cancelada** | Anulada a mano. | — |

Los cambios por fecha (caducidad, documentación KO, descartes por impago, check-in y check-out) los hace un proceso automático **cada 15 minutos**. Cada cambio de estado queda en el registro de la reserva.

## 3.4 Tareas

### Atender una solicitud: asignar recurso

**Cuándo**: en cuanto llega una solicitud (dashboard general, contador *Solicitudes*).

**Cómo**: en la reserva, elegir el recurso. El **planning** en modo selector muestra en verde los recursos libres en esas fechas; si se elige uno de otra tipología, pide confirmación.

**Antes de asignar, comprobar**:

- Que el cliente tiene **datos fiscales** completos (tipo y número de documento y dirección). Sin ellos, la reserva solo puede quedarse en *pendiente de pago*.
- El **motivo de estancia**, con la escuela (estudios) o la empresa (trabajo o prácticas).
- Si el recurso tiene **renta limitada**, indicar el tipo de reserva: *limitada* o *recreativa*.

**Qué hace el sistema**:

- Valida que no haya **solapes** con otras reservas del recurso y que el cliente no esté en **lista negra**.
- Calcula los precios mes a mes, la garantía y, en Barcelona, la fianza INCASÒL (ver *Inventario y precios* y *Contratos, garantías e INCASÒL*).
- Si el membership fee no está pagado: pasa a **pendiente de pago**, con un plazo de pago de 2 días como mínimo, y envía el email *pendiente de pago*.
- Si ya estaba pagado (o lo cobró un marketplace): pasa a **confirmada**.
- Bloquea el recurso, su piso y sus plazas en la ocupación.

### Proponer alternativas

**Cuándo**: la solicitud no se puede atender tal cual (no hay recurso libre de esa tipología en ese edificio o fechas).

**Cómo**: añadir una o varias **alternativas** a la reserva (edificio, tipología y, si hace falta, otras condiciones) y pulsar **Enviar alternativas**. El botón aparece cuando hay alternativas sin aceptar.

**Qué hace el sistema**: la reserva pasa a **alternativas** y el cliente recibe el email *alternativas*. El cliente las ve en el portal y acepta una: la solicitud toma el edificio y la tipología de la alternativa y vuelve a **solicitud** para que se le asigne recurso. Al confirmarse la reserva, se borran las alternativas.

### Seguir el pago del membership fee

- El cliente paga con tarjeta desde el portal. Al registrarse el pago, la reserva pasa a **confirmada**, se fija el plazo de documentación (14 días) y se genera el email *confirmada* (hoy no se envía porque no tiene plantilla; ver *Comunicación con el residente*).
- Si vence el plazo sin pagar, la reserva pasa a **caducada** (email *caducada*). Para darle más tiempo, se amplía la fecha *válida hasta*: vuelve a *pendiente de pago*. Si nadie la amplía, a los 5 días pasa a **descartada** y libera el recurso.
- **Cambiar el importe**: si se cambia el membership fee antes de que se pague, el sistema sustituye el cobro por uno nuevo. Si ya está pagado, solo avisa.

### Revisar la documentación

**Qué se pide**: al crear la reserva, el sistema añade a la ficha del cliente los documentos que debe aportar: los de su **tipo de identificación** y los obligatorios de su **motivo de estancia** (por ejemplo, matrícula o contrato laboral). El cliente los sube desde el portal; recibe recordatorios si faltan a 20 días o menos de la entrada.

**Qué hacer**: revisar los documentos subidos (dashboard *Documentos*), incluido el de identidad, y aprobarlos o rechazarlos.

**Qué hace el sistema**: la reserva pasa a **documentación OK** y emite el **cobro de la garantía** a nombre del propietario cuando se cumple una de estas condiciones:

- la reserva tiene **al menos un documento del motivo de estancia aprobado**, o
- la reserva no tiene documentos del motivo de estancia (el motivo no exige ninguno).

Hay que tener en cuenta:

- Solo cuentan los documentos del **motivo de estancia**, que se piden por reserva. Hoy hay uno obligatorio por motivo, y dos en el motivo vacacional.
- El **documento de identidad** se pide en la ficha del cliente, una sola vez para todas sus reservas, y no interviene en el avance de la reserva. Su revisión es una comprobación del personal.
- Con **uno** de los documentos del motivo aprobado es suficiente: en las estancias vacacionales, la reserva avanza aunque el segundo documento esté pendiente.

**Documentación KO**: si vence el plazo de documentación (14 días desde la confirmación), la reserva pasa a *documentación KO*. El sistema no hace nada más: el personal reclama la documentación y amplía el plazo, o descarta la reserva.

### Seguir el pago de la garantía

- El cliente la paga desde el portal. Recibe el aviso de garantía a 40 días de la entrada y recordatorios cada 2 días a partir de 32 días.
- Con la garantía pagada (o si es cero), la reserva pasa a **firma de contrato** y el sistema genera el contrato y lo envía a firmar (ver *Contratos, garantías e INCASÒL*).
- **Descarte por impago**: si faltan menos de 30 días para la entrada, la reserva se confirmó hace más de 4 días y el cobro de la garantía lleva más de 4 días sin pagarse, pasa automáticamente a **descartada pagada**.
- **Cambiar el importe**: como con el membership fee, si no está pagada se sustituye el cobro; si ya está pagada, solo avisa.

### Seguir la firma del contrato

Cuando DocuSign notifica la firma, la reserva pasa a **contrato**. El residente firma desde el email que le envía DocuSign; el recordatorio de firma del sistema está hoy desactivado de forma temporal. Si la firma se anula, la reserva vuelve a *firma de contrato* y el contrato se regenera. Detalle en *Contratos, garantías e INCASÒL*.

### Preparar la entrada

- El residente indica en el portal la **fecha y hora de llegada**; la reserva pasa a **check-in confirmado**. Si elige una **opción de check-in** de pago (franja horaria o día), se le crea el cobro.
- El día de entrada (la fecha de check-in o, si no hay, la de inicio), la reserva pasa sola a **check-in**.
- Si se aplaza la llegada a una fecha futura, la reserva vuelve a *contrato* o *check-in confirmado*.

Las tareas del día de entrada (llaves, keyless, aviso a compañeros, *Check-in OK*) están en *Operación diaria*. Al confirmar la entrada, la reserva pasa a **in house**: el residente recibe el email de bienvenida (*in house*) y el cuestionario de check-in en el portal, que se borra si no lo completa en 7 días.

### Durante la estancia

- **Facturación mensual automática** de renta y servicios, con su cobro (ver *Facturación y cobros*).
- **Servicios adicionales**: conceptos extra que se facturan en la próxima factura, en una fecha concreta o de forma recurrente entre dos fechas. Si no se indica, el emisor es Cotown (o el propietario, para productos de renta), y el IVA y el concepto salen del producto.
- **Descuentos** sobre la renta o los servicios de un mes, en importe o en porcentaje (el sistema calcula el otro). *Aplicar a todos* copia el descuento a los demás meses. Todo descuento exige un motivo.
- **Nota en factura**: texto que se añade a las facturas de la reserva.

### Salida anticipada o extensión (ECO / EXT)

**Cómo**: informar la **nueva fecha de salida** en la reserva, y la penalización si la hay.

**Qué hace el sistema**:

- Borra los meses **no facturados** afectados y los recalcula hasta la nueva fecha. En una salida anticipada, el último mes se recalcula según la forma de facturación; en una extensión, se añaden los meses nuevos con los precios vigentes.
- La fecha de fin pasa a ser la nueva y guarda la anterior (*fecha original de check-out*).
- Marca el cambio como **pendiente de gestionar**.

**Qué hacer después**: revisar los meses recalculados (los ajustes manuales de esos meses se pierden), actualizar la llave móvil si la hay y marcar *Cambio gestionado* (dashboard de operaciones).

Una extensión también puede registrarse como una **reserva nueva** enlazada a la original (canal *Extensión*, tipo de relación *EXT*).

### Cambio de habitación (CHA)

**Cómo**:

1. Crear una **reserva nueva** para el recurso de destino, con canal *Cambio*, y enlazarla con la original indicando la reserva origen y el tipo de relación *CHA*. El sistema enlaza las dos en ambos sentidos.
2. En la reserva de destino, poner el **membership fee a 0** y la **garantía depositada** con el importe traspasado de la original.
3. Acortar la reserva original hasta la fecha del cambio (salida anticipada). La original no devuelve la garantía: pasa a la de destino.

**Qué hace el sistema**: la reserva de destino genera y envía a firmar su propio contrato. No envía los emails comerciales (solicitud, pendiente de pago, confirmada, keyless), para que el residente no los reciba dos veces.

Las extensiones registradas como reserva nueva (relación *EXT*, canal *Extensión*) siguen la misma práctica.

### Salida y revisión

- El día de salida (fecha de check-out o, si no hay, la de fin), la reserva pasa sola a **check-out**. Antes, el residente recibe el aviso de salida con el cuestionario de check-out (10 días antes) y la invitación a Trustpilot (30 días antes).
- El personal confirma la salida (*Check-out OK*): pasa a **revisión**.
- Tras revisar el alojamiento y registrar los desperfectos, se marca la revisión como correcta: pasa a **devolver garantía**.

Detalle de estas tareas en *Operación diaria*.

### Devolver la garantía

**Qué informar**: importe a devolver y fecha prevista; después, importe devuelto y fecha de devolución. Si hay que retener la garantía mientras se resuelve algo, marcar **Retenida temporalmente**.

**Qué hace el sistema**: con el importe devuelto informado y sin retención temporal, la reserva pasa a **finalizada**. No permite devolver más de lo depositado.

**Retención**: lo que se retiene de la garantía (desperfectos, limpieza extra, recargos, mensualidades pendientes) se **factura** al residente:

1. Registrar cada concepto como **servicio adicional** de la reserva (productos *Desperfectos*, *Limpieza extra*, *Mano de obra*, *Material*, *Garantía incautada*…), o usar las facturas pendientes de pago que ya existan.
2. Indicar en el cobro de esas facturas el medio de pago **De la garantía**.
3. Consultar el informe **Devoluciones**, que para cada reserva en salida calcula la garantía depositada, lo pendiente de pago y lo que se cobra de la garantía.
4. Devolver la diferencia e informar el importe devuelto.

En un cambio de habitación, la garantía de la reserva original no se devuelve: se traspasa a la de destino (medio de pago *Garantía trasladada*).

### Descartar una reserva

**Cómo**: botón **Descartar** (disponible en solicitud, alternativas y pendiente de pago). Si el membership fee está pagado, la reserva pasa a **descartada pagada**; si no, a **descartada**.

**Qué hace el sistema**: quita el recurso (lo libera), borra los cobros no pagados, desvincula la reserva de destino si la había y genera el email del estado (hoy no se envía porque no tiene plantilla).

**Descartada pagada**: hay que **devolver el membership fee**. Al registrar el importe devuelto, la reserva pasa a *descartada*. Si el cliente vuelve a reservar, la nueva reserva se registra con el canal *Descartada Pagada*.

### Reactivar una reserva descartada

**Cómo**: botón **Reactivar**. Vuelve a *solicitud* (o *solicitud pagada* si estaba descartada pagada).

**Qué hace el sistema**: vuelve a emitir el cobro del membership fee y envía de nuevo el email de *solicitud*. A partir de ahí, se atiende como una solicitud nueva.

### Cancelar una reserva

**Cómo**: cambiar el estado a **cancelada** a mano. Se puede hacer desde cualquier estado.

**Cuándo**: *descartar* es para solicitudes que no llegan a confirmarse; *cancelar*, para reservas ya confirmadas que se anulan (por ejemplo, el residente renuncia después de pagar).

**Qué hace el sistema**: borra los cobros no pagados. No envía email: el personal ya ha hablado con el residente.

**Qué hacer**: las devoluciones de lo cobrado (membership fee, garantía, mensualidades) y las rectificativas de lo facturado se hacen a mano (ver *Facturación y cobros*).

### Reservas de clientes en lista negra

La reserva no puede avanzar (asignar recurso, confirmarse…) mientras el cliente esté en lista negra; el sistema muestra el motivo. Para autorizarla, marcar **Ignorar lista negra** en la reserva.

## 3.5 Automático y manual

| Qué | A / M |
|---|---|
| Creación de la solicitud desde la web; cobro del membership fee y email | A |
| Asignación de recurso o envío de alternativas | M |
| Aceptación de alternativas | Cliente |
| Pago del membership fee y de la garantía | Cliente |
| Confirmación, caducidad, descarte de caducadas y descarte por garantía impagada | A |
| Documentos a aportar según identificación y motivo | A |
| Aprobación de la documentación | M |
| Gestión de *documentación KO* | M |
| Cobro de la garantía al aprobar la documentación | A |
| Contrato: generación, envío, recordatorios y paso a *contrato* | A |
| Paso a check-in y check-out por fecha | A |
| Confirmación de entrada, salida y revisión | M |
| Facturación mensual | A |
| ECO/EXT: recálculo de meses | A; la confirmación del cambio, M |
| Cambio de habitación | M |
| Devolución de garantía y de membership fee | M |
| Factura de la garantía retenida | M |
| Descartar, reactivar y cancelar | M |

## 3.6 Excepciones

| Situación | Qué pasa | Qué hacer |
|---|---|---|
| Error "Cliente sin datos fiscales" | No se puede confirmar la reserva. | Completar tipo y número de documento y dirección del cliente. |
| Error "Solapamiento con la reserva n" | El recurso está ocupado en esas fechas por otra reserva. | Elegir otro recurso o corregir fechas. Comprobar también en el planning grupos y bloqueos. |
| Error "Cliente en lista negra" | La reserva no avanza. | Valorar y, si procede, marcar *Ignorar lista negra*. |
| Error "Recurso con renta limitada" | Falta el tipo de reserva. | Indicar *limitada* o *recreativa*. |
| Error "Reserva bloqueada" | Tiene marcado *No cambiar asignación*. | Quitar la marca si de verdad hay que cambiar el recurso. |
| Error "Motivo no seleccionado", "Escuela no seleccionada" o "Compañía no indicada" | Faltan datos del motivo de estancia. | Completarlos. |
| Se cambian fechas o recurso de una reserva con meses ajustados a mano | Los meses no facturados se recalculan con los precios vigentes. | Volver a aplicar los ajustes manuales. |

## 3.7 Fuentes

| Tema | Dónde está |
|---|---|
| Estados, validaciones, cobros y emails de la reserva | Reglas de la base de datos de las reservas |
| Cambios por fecha | Proceso programado de la base de datos (cada 15 minutos) |
| Botones de la reserva | Reglas de la base de datos y servicio de integración |
| Alternativas | Reglas de la base de datos de las alternativas y portal del residente |
| Documentos a aportar | Reglas de la base de datos de las reservas |

## 3.8 Pendiente de confirmar

| Tema | Quién o qué lo confirma |
|---|---|
| — | — |
