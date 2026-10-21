# OP-7. Operación diaria

> Manual funcional · Borrador v0.1 · 2026-10-21 · Las marcas **[PREGUNTA On]** se resuelven en la ronda de preguntas y desaparecen de la versión final.

## 7.1 Propósito

Este capítulo explica el trabajo diario con los residentes alojados o a punto de llegar o salir: preparar y confirmar entradas, atender incidencias, preparar y confirmar salidas, revisar los alojamientos, gestionar los cambios de fecha y revisar la documentación. También describe las pantallas de apoyo: planning, dashboards y cuestionarios.

Se aplica a las reservas B2C y a los residentes de grupos con **gestión B2C**. En los grupos sin gestión B2C, la entrada y la salida de los residentes las da por hechas el sistema (ver *Reservas de grupo B2B*).

## 7.2 Conceptos

| Concepto | Qué es |
|---|---|
| **Opción de check-in / check-out** | Servicio de entrada o salida que elige el residente (en oficina, en el piso, fuera de horario…). Su precio depende de la ciudad, del día (laborable, viernes, sábado, domingo o festivo) y de la franja horaria. Algunos son gratuitos. |
| **Keyless** | Acceso al piso con llave móvil, sin entrega física de llaves. |
| **Aviso a compañeros** | Email automático a los residentes del piso cuando va a llegar uno nuevo. |
| **Cuestionario** | Encuesta de check-in o de check-out que el residente responde en el portal: puntuaciones, sí/no, texto y fotos o vídeos. Sus respuestas pueden abrir **incidencias**. |
| **Incidencia** | Problema que el residente comunica al entrar (o en el cuestionario). Se gestiona y se marca como gestionada. |
| **Desperfecto** | Daño detectado al revisar el alojamiento tras la salida. Puede facturarse y cobrarse de la garantía. |
| **Margen** | Días laborables entre la salida de un residente y la entrada del siguiente en el mismo recurso, descontando fines de semana y festivos. |

## 7.3 Pantallas de trabajo

| Pantalla | Para qué |
|---|---|
| **Dashboard general** | Contadores de reservas por fase (solicitudes, alternativas, descartadas pagadas, recurso asignado, próximas entradas y salidas, devolver garantía). Al pulsar un contador se ve la lista y se descarga en Excel. Solo consulta. |
| **Dashboard de operaciones** | Pantalla de trabajo diaria, con pestañas: próximas entradas, entradas, incidencias, próximas salidas, salidas, revisiones y salidas anticipadas o extensiones. Filtros por ciudad, edificios, B2C/B2B y fechas. Cada fila muestra la salida anterior y la entrada siguiente en el mismo recurso, y resalta los márgenes de menos de 2 días laborables. Cada pestaña se descarga en Excel. |
| **Dashboard de documentos** | Documentación pendiente de subir o de aprobar, por reserva; resalta las entradas en menos de 14 días. Permite ver y aprobar cada documento. |
| **Planning** | Ocupación de pisos, habitaciones y plazas en el tiempo, con el color de cada estado, las marcas de check-in, check-out y limpiezas, y el régimen de renta de cada recurso. Solo consulta (salvo en modo selector, para asignar recurso). |

Colores del planning:

| Estado | Color |
|---|---|
| Grupo bloqueado / confirmado | Rosa claro / rosa |
| Pendiente de pago / confirmada | Naranja claro / naranja |
| Caducada | Negro |
| Firma de contrato / contrato | Amarillo claro / amarillo |
| Check-in confirmado / check-in / in house | Verdes, de claro a oscuro |
| Check-out / revisión / devolver garantía | Azules, de claro a oscuro |
| Finalizada | Gris |

## 7.4 Tareas

### Preparar las próximas entradas

**Cuándo**: a diario, con la pestaña **Próximas entradas** del dashboard de operaciones.

**Qué hace antes el sistema**:

- Desde 30 días antes de la entrada, pide al residente que complete el check-in en el portal (fecha, hora, transporte y opción de check-in), con recordatorios cada 5 días.
- Cuando el residente informa la fecha de llegada, la reserva pasa a *check-in confirmado*.
- Si elige una **opción de check-in de pago**, crea el cobro (y su factura de Cotown) según la ciudad, el día y la franja horaria. Si no hay precio para ese día y hora, el portal le avisa de que el servicio no está disponible.
- A 2 días o menos de la llegada, avisa por email a los compañeros de piso que estén alojados, y lo marca como hecho.

**Qué hacer** (marcando cada tarea en la fila y guardando):

- **Check-in solicitado**: el residente ha pedido la entrada.
- **Limpieza** del alojamiento antes de la llegada.
- **Llaves** preparadas o **keyless** dado de alta. Al marcar *Llaves keyless OK*, el residente recibe el email con las instrucciones de la llave móvil.
- Revisar el **margen** con la salida anterior: si es menor de 2 días laborables, coordinar limpieza y revisión.

### Confirmar la entrada

**Cuándo**: el día de entrada (pestaña **Entradas**). La reserva pasa sola a *check-in* en la fecha de check-in o, si no la hay, en la de inicio.

**Qué hacer**: comprobar la habitación y las llaves y marcar **Check-in** (o pulsar *Check-in OK* en la reserva).

**Qué hace el sistema**: la reserva pasa a **in house**, el residente recibe el email de bienvenida y se le abre el **cuestionario de check-in** en el portal. Si no lo responde en 7 días, se borra.

**Si se aplaza la llegada**: al cambiar la fecha de check-in a una fecha futura, la reserva vuelve a *contrato* o *check-in confirmado*.

### Atender las incidencias

**De dónde vienen**: de las respuestas del residente en el cuestionario de check-in (que se copian a la reserva) o las que registra el personal en la reserva.

**Qué hacer**: en la pestaña **Incidencias**, resolverlas y marcar **Incidencias gestionadas**.

### Preparar las próximas salidas

**Qué hace antes el sistema**:

- A 30 días de la salida, envía la invitación a dejar una reseña en Trustpilot.
- A 10 días, envía el aviso de salida y abre el **cuestionario de check-out**; el residente puede informar en el portal la fecha, la hora de recogida y la **opción de check-out** (con su cobro, como en la entrada).

**Qué hacer**: en la pestaña **Próximas salidas**, coordinar la recogida de llaves y la revisión.

### Confirmar la salida

**Cuándo**: el día de salida (pestaña **Salidas**). La reserva pasa sola a *check-out* en la fecha de check-out o, si no la hay, en la de fin.

**Qué hacer**: marcar **llaves devueltas**, **llave móvil desactivada** y **Check-out** (o pulsar *Check-out OK* en la reserva).

**Qué hace el sistema**: la reserva pasa a **revisión**.

### Revisar el alojamiento

**Cuándo**: después de cada salida (pestaña **Revisiones**).

**Qué hacer**:

1. Revisar el alojamiento y registrar los **desperfectos**.
2. Si hay que facturar algo (desperfectos, limpieza extra, mano de obra, material), añadirlo como servicio adicional a la reserva (ver *Facturación y cobros*).
3. Marcar **Desperfectos gestionados** y **Revisión OK**.

**Qué hace el sistema**: la reserva pasa a **devolver garantía** (su email no se envía mientras no tenga plantilla). La devolución está en *Reservas B2C*.

En los grupos con gestión B2C, la revisión de cada residente lo deja como *revisado*.

### Gestionar salidas anticipadas y extensiones

**Cuándo**: cuando se ha informado una nueva fecha de salida en una reserva (ver *Reservas B2C*). Aparecen en la pestaña **Salidas anticipadas / extensiones**.

**Qué hacer**: revisar los meses recalculados, actualizar la llave móvil (**Llave móvil actualizada**) y marcar **Cambio gestionado**.

### Revisar la documentación

**Cuándo**: a diario, con el **dashboard de documentos**, empezando por las entradas en menos de 14 días.

**Qué hacer**: ver cada documento subido por el residente y aprobarlo, o pedirle que lo sustituya. El residente puede cambiarlo en el portal hasta que se aprueba. La regla con la que avanza la reserva está en *Reservas B2C*.

### Limpieza final

En las reservas con limpieza final, el sistema crea automáticamente un servicio adicional *Limpieza de salida* por el importe de la reserva, que se factura al **inicio** de la estancia: se cobra por adelantado. En los grupos, la limpieza de salida se factura al pagador a medida que salen los residentes de cada piso.

### Mantener las opciones de check-in y check-out

En *Reservas › Servicios de check-in/check-out* se mantienen las opciones (nombre y descripción en los dos idiomas, tipo entrada o salida) y sus **precios por ciudad y franja horaria** (con horarios distintos para laborables, viernes, sábados y domingos o festivos). Los **festivos** se mantienen en *Auxiliares › Festivos*, generales o por ciudad.

### Mantener los cuestionarios

Las preguntas de los cuestionarios de check-in y check-out se mantienen en Airflows, agrupadas por tipo de cuestionario, con su orden, su tipo (puntuación, sí/no o texto) y su texto en los dos idiomas. Las respuestas se consultan en el informe **Cuestionarios**.

### Registrar las limpiezas de los recursos

Cada recurso tiene la fecha de **última limpieza** y de **última limpieza prevista**. Se informan a mano, desde el dashboard de operaciones o en la ficha del recurso, y se muestran en el planning y en el dashboard para coordinar las entradas.

## 7.5 Automático y manual

| Qué | A / M |
|---|---|
| Recordatorios para completar el check-in; cobro de las opciones de check-in/out | A |
| Paso a *check-in confirmado*, *check-in* y *check-out* | A |
| Aviso a compañeros de piso | A |
| Preparación de la entrada (limpieza, llaves, keyless) | M |
| Email de llave móvil | A (al marcar *keyless OK*) |
| Confirmación de entrada y de salida | M |
| Cuestionarios de check-in y check-out | A (se abren); el residente los responde |
| Incidencias y desperfectos | M |
| Revisión del alojamiento | M |
| Gestión de salidas anticipadas y extensiones | M |
| Aprobación de la documentación | M |
| Servicio de limpieza final | A |
| Fechas de última limpieza y limpieza prevista | M |

## 7.6 Excepciones

| Situación | Qué pasa | Qué hacer |
|---|---|---|
| Error "Servicio no disponible" al elegir una opción de check-in o check-out | No hay precio para ese día y franja en esa ciudad. | Elegir otra hora u opción, o dar de alta el precio. |
| Error "Debes indicar la fecha / hora de check-in" (o de recogida) | La opción de pago exige fecha y hora. | Completarlas. |
| La entrada se adelanta o retrasa | — | Cambiar la fecha de check-in: la reserva ajusta su estado. |
| El residente no completa el cuestionario de check-in | Se borra a los 7 días. | Ninguna. |
| Un margen entre salida y entrada es menor de 2 días | Se resalta en el dashboard. | Coordinar limpieza y revisión. |

## 7.7 Fuentes

| Tema | Dónde está |
|---|---|
| Estados de entrada y salida | Reglas y proceso programado de la base de datos de las reservas |
| Opciones de check-in y check-out | Reglas de la base de datos de las reservas y de la rooming list |
| Aviso a compañeros, recordatorios | Procesos programados de la base de datos |
| Dashboards y planning | Backoffice complementario |
| Cuestionarios | Portal del residente y servicio de integración |

## 7.8 Pendiente de confirmar

| Tema | Quién o qué lo confirma |
|---|---|
| — | — |
