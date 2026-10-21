# OP-5. Contratos, garantías e INCASÒL

> Manual funcional · Borrador v0.1 · 2026-10-21 · Las marcas **[PREGUNTA On]** se resuelven en la ronda de preguntas y desaparecen de la versión final.

## 5.1 Propósito

Este capítulo explica cómo se generan y se firman los contratos de las reservas B2C y de grupo, cómo se mantienen las plantillas de contrato, cómo se cobra la garantía y cómo se gestiona la fianza legal que, en Barcelona, se deposita en el INCASÒL.

La devolución de la garantía al terminar la estancia está en *Reservas B2C* y *Reservas de grupo B2B*. Los contratos LAU están en *Contratos LAU y otros*.

## 5.2 Conceptos

| Concepto | Qué es |
|---|---|
| **Contrato de renta** | Contrato de arrendamiento entre el **propietario** y el residente (o el pagador del grupo). Siempre se genera. |
| **Contrato de servicios** | Contrato entre el **prestador de servicios** y el residente. Solo se genera si el prestador es distinto del propietario y la reserva tiene importe de servicios. |
| **Plantilla de contrato** | Texto del contrato con variables (datos del residente, del recurso, importes, fechas…) que el sistema rellena. Cada proveedor tiene las suyas, por tipo de reserva y, si hace falta, por ciudad. Pueden llevar un **anexo en inglés**. |
| **Tipo de plantilla** | Residencia, habitación B2C, piso B2C, habitación B2B y piso B2B. |
| **Anexos documentales** | En Barcelona, documentos del edificio y del piso marcados *Adjuntar a contratos* (cédula, certificado energético…), que se añaden al final del contrato de renta. |
| **Firmante del propietario** | Contacto del proveedor de tipo *Apoderado*. Su firma escaneada se incrusta en el contrato. |
| **Contrato digital** | Edificio marcado *Emitir contratos*: sus contratos se envían a firmar por **DocuSign**. Sin la marca, el contrato se genera pero se firma fuera del sistema. Hoy varios edificios la tienen desactivada para no emitir contratos digitales mientras se aplican los decretos de vivienda. |
| **Garantía** | Importe que deposita el residente. Se emite como **recibo del propietario**. |
| **Fianza legal (INCASÒL)** | En Barcelona, parte de la garantía que debe depositarse en el Institut Català del Sòl. |

## 5.3 Tareas

### Mantener las plantillas de contrato

**Dónde**: *Propietarios › Plantillas de contrato* (el texto) y, en cada proveedor, sus **plantillas asignadas**: tipo, ciudad (o ninguna, para la genérica), plantilla de texto y si está activa.

**Reglas**:

- Para cada proveedor, tipo y ciudad solo hay una plantilla activa: al activar una, el sistema desactiva las demás de ese tipo y ciudad.
- El sistema busca primero la plantilla de la **ciudad del recurso** y, si no hay, la **genérica** (sin ciudad).
- El **tipo** sale de la reserva: *residencia* si el edificio es una residencia de estudiantes; si no, *habitación* o *piso* según el recurso (B2C) o el grupo (B2B).
- Si el residente tiene el **inglés** como idioma y la plantilla tiene anexo en inglés, se añade al final del contrato.

**Comprobar**: al dar de alta un propietario o prestador, que tiene plantillas activas para todos los tipos de reserva que va a tener y un contacto **apoderado** con su firma. Si falta la plantilla, el contrato no se genera (queda en el registro del proceso) y la reserva se queda esperando en *firma de contrato*.

**Servicios del edificio en el contrato**: los servicios del edificio marcados *Incorporar en contrato* se listan en el contrato.

### Contrato de una reserva B2C

**Cuándo se genera**: en cuanto la reserva llega a **firma de contrato** (garantía pagada o cero, o membership fee cobrado por un marketplace), el proceso de contratos, que se ejecuta cada 15 minutos, genera el contrato.

**Qué hace el sistema**:

1. Comprueba que el residente tiene tipo y número de documento y dirección. Si no, espera a la siguiente ejecución.
2. Genera el **contrato de renta** con la plantilla del propietario y, si corresponde, el **contrato de servicios** con la del prestador.
3. En Barcelona, añade los **anexos documentales** del edificio y del piso.
4. Guarda los PDF en la reserva y genera el email *firma de contrato* (hoy desactivado de forma temporal: el residente recibe solo el email de DocuSign).
5. Si el edificio tiene **contrato digital**, envía los contratos a firmar por **DocuSign**, con el residente como firmante, en su idioma.

**Seguimiento**: DocuSign avisa de cada cambio (enviado, entregado, firmado, rechazado, caducado, anulado) y, además, cada noche a la 01:00 se revisan todos los contratos pendientes. Al firmarse, la reserva pasa a **contrato**. Mientras no se firme, el sistema genera un recordatorio de firma cada 3 días (solo en edificios con contrato digital; hoy desactivado de forma temporal).

**Edificios sin contrato digital**: el contrato se genera y se guarda, pero no se envía; su estado queda como *otro*. El personal gestiona la firma fuera del sistema y, una vez firmado, cambia el estado del contrato a **firmado** (*completed*) en la reserva para que avance a *contrato*.

### Regenerar un contrato

**Cuándo**: hay que corregir algo del contrato (datos del residente, importes, fechas) antes de que se firme, o el residente lo ha rechazado.

**Cómo**: corregir los datos y **vaciar el contrato de renta** de la reserva. En la siguiente ejecución (cada 15 minutos) se genera y se envía de nuevo.

**Qué hace el sistema si se anula la firma**: si el contrato estaba firmado y su estado deja de ser *firmado* (por ejemplo, porque se anula en DocuSign), la reserva vuelve a **firma de contrato**, se borran el contrato y su estado, y se genera de nuevo.

### Contrato de un grupo

1. Al confirmar el grupo, el proceso de contratos genera el contrato de renta (y el de servicios, si corresponde) con la plantilla B2B del propietario (habitación o piso) y los anexos de Barcelona. **No lo envía.**
2. El personal revisa el contrato en el grupo y marca **Contrato OK**.
3. En la siguiente ejecución se envía a DocuSign con el **pagador** como firmante.
4. El estado de la firma se actualiza cada noche.

**Anexos de grupo**: para incorporar una nueva tanda de residentes se crea un **anexo** en el grupo con el código de la tanda. El sistema lo genera con la relación de residentes de esa tanda y lo envía a firmar al pagador automáticamente.

### Cobrar la garantía

**Reservas B2C**:

- El **importe** se calcula al asignar el recurso: el del precio base, con un mínimo de 1,5 × la renta (ver *Inventario y precios*). Se puede cambiar a mano.
- El **cobro** se emite cuando la reserva pasa a *documentación OK*, por el terminal de pago del **propietario**. El residente lo paga desde el portal.
- Al pagarse, el sistema emite el **recibo del propietario** por la garantía; en Barcelona, con una línea aparte para la fianza INCASÒL.
- Si se cambia el importe antes de pagarlo, el cobro se sustituye; después, solo avisa.

**Grupos**: al confirmar el grupo, el sistema emite el cobro y el recibo por la garantía total (garantía por plaza × plazas), al pagador, por transferencia.

**Avisos al residente**: a 40 días de la entrada y cada 2 días a partir de 32 días, mientras no la pague. Si faltan menos de 30 días para la entrada y lleva más de 4 días sin pagarla, la reserva se descarta automáticamente (ver *Reservas B2C*).

### Gestionar la fianza INCASÒL (Barcelona)

**Qué calcula el sistema**: al calcular los precios de una reserva B2C o de un grupo en Barcelona con garantía, calcula la **fianza legal** una sola vez:

| Caso | Fianza legal |
|---|---|
| Habitación o plaza | Una mensualidad de renta. |
| Renta limitada | Una mensualidad de renta + consumos + mobiliario + gastos. |
| Piso completo en estancia recreativa (B2C) o grupo de pisos completos | Dos mensualidades, prorrateadas por la duración de la estancia sobre 180 días (como máximo, dos mensualidades). |
| Grupo | La fianza por plaza × número de plazas. |

La fianza no cambia la garantía: es la parte de la garantía que se deposita. Si después cambian la renta o el recurso, no se recalcula; hay que corregirla a mano.

**Qué hacer**:

1. **Depositar**: presentar en el INCASÒL las fianzas pendientes (dashboard *Administración › INCASÒL*, informe *INCASÒL* de altas en un periodo). Al hacerlo, registrar en la reserva el **número de registro** y cambiar el estado a **depositada**.
2. **Reclamar la devolución** al terminar la estancia: presentar la declaración responsable de devolución (informe *Declaraciones INCASÒL*, que descarga un ZIP con un PDF en catalán por reserva) y cambiar el estado a **reclamada**.
3. **Registrar la devolución**: cuando el INCASÒL la devuelve, cambiar el estado a **devuelta**.

Las fianzas las presenta Cotown. El seguimiento se lleva en el dashboard *Administración › INCASÒL*, que muestra las fianzas pendientes de depositar, reclamadas y por devolver: hay que mantener al día el estado de cada fianza para que el dashboard sea fiable.

## 5.4 Automático y manual

| Qué | A / M |
|---|---|
| Plantillas de contrato y firmantes | M |
| Generación del contrato B2C y envío a DocuSign | A |
| Revisión del contrato de grupo (*Contrato OK*) | M |
| Envío del contrato de grupo y de los anexos | A |
| Seguimiento de la firma (avisos y revisión nocturna) | A |
| Firma en edificios sin contrato digital | M |
| Regeneración de un contrato | M (vaciar el contrato); A (generarlo) |
| Importe de la garantía | A (se puede ajustar a mano) |
| Cobro y recibo de la garantía | A |
| Cálculo de la fianza INCASÒL | A |
| Depósito, reclamación y registro de la devolución en el INCASÒL | M |

## 5.5 Excepciones

| Situación | Qué pasa | Qué hacer |
|---|---|---|
| La reserva lleva tiempo en *firma de contrato* sin contrato | Falta el documento o la dirección del residente, o el proveedor no tiene plantilla para ese tipo y ciudad. | Completar los datos del residente o la plantilla del proveedor; avisar a Oimbra si no se ve la causa. |
| El residente rechaza o deja caducar el contrato en DocuSign | El estado del contrato lo refleja; la reserva sigue en *firma de contrato*. | Hablar con el residente, corregir si hace falta y regenerar el contrato. |
| El residente no recibe el email de DocuSign | — | Comprobar su email; regenerar el contrato si hay que cambiarlo. |
| Se cambia la renta o el recurso después de calcular la fianza INCASÒL | La fianza no se recalcula. | Corregirla a mano antes de depositarla. |
| Se ha enviado el contrato de un grupo con un error | — | Anular el sobre en DocuSign, vaciar el contrato, desmarcar *Contrato OK* y revisarlo de nuevo cuando se regenere. |

## 5.6 Fuentes

| Tema | Dónde está |
|---|---|
| Generación y envío de contratos y anexos | Proceso automático de contratos (cada 15 minutos) |
| Revisión nocturna de las firmas | Proceso automático de comprobación de contratos (01:00) |
| Avisos de DocuSign | Servicio de integración |
| Paso a *contrato* y regeneración | Reglas de la base de datos de las reservas |
| Plantilla activa única | Reglas de la base de datos de las plantillas |
| Garantía y fianza INCASÒL | Reglas de la base de datos de las reservas y de los grupos; proceso de facturación |
| Dashboard e informes INCASÒL | Backoffice complementario |

## 5.7 Pendiente de confirmar

| Tema | Quién o qué lo confirma |
|---|---|
| — | — |
