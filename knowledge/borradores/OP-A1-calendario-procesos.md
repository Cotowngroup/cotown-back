# Anexo. Calendario de procesos automáticos

> Manual funcional · Borrador v0.1 · 2026-10-21 · Las marcas **[PREGUNTA On]** se resuelven en la ronda de preguntas y desaparecen de la versión final.

Este anexo reúne en una sola tabla los procesos que el sistema ejecuta por sí solo, cuándo se ejecutan, qué hacen y en qué capítulo se explican. Sirve para responder a preguntas como "¿por qué ha cambiado esta reserva a las 3:17?" o "¿cuándo saldrá esta factura?".

No incluye lo que el sistema hace **en el momento** en que alguien guarda un dato (calcular precios al asignar un recurso, emitir un cobro al aprobar la documentación, numerar una factura al emitirla…): eso se explica en cada tarea, en el apartado "Qué hace el sistema".

Hay dos tipos de procesos programados: los de la **base de datos de Airflows** y los del **servidor de servicios** (o del servidor del data warehouse).

**Horas**: los procesos de la base de datos de Airflows se programan en **hora UTC**, que en España es una hora menos en invierno y dos en verano (las 10:00 UTC son las 11:00 en invierno y las 12:00 en verano). Los procesos del servidor de servicios y del data warehouse usan la hora de España. En las tablas, *(UTC)* indica un proceso de la base de datos.

## Permanente

| Proceso | Qué hace | Capítulo |
|---|---|---|
| Envío de emails | Envía cada email en segundos, en cuanto se genera. | *Comunicación con el residente* |
| Avisos de Redsys y DocuSign | Registran los pagos con tarjeta y los cambios de estado de los contratos en cuanto llegan. | *Facturación y cobros*, *Contratos, garantías e INCASÒL* |

## Cada 15 minutos

| Minutos | Proceso | Qué hace | Capítulo |
|---|---|---|---|
| :00, :15, :30, :45 | **Facturación** | Emite facturas, recibos y cobros de todo lo vencido: membership fee, garantía, check-in/out, mensualidades B2C y de grupos, servicios adicionales, contratos LAU y otros, y cobros de facturas manuales. | *Facturación y cobros* |
| :02, :17, :32, :47 | **Estados de las reservas B2C** | Caduca las pendientes de pago vencidas, pasa a *documentación KO* las que superan el plazo, descarta las caducadas hace más de 5 días y las que no pagan la garantía a menos de 30 días de la entrada, pasa a *check-in* y *check-out* por fecha y borra los cuestionarios de check-in sin completar a los 7 días. | *Reservas B2C* |
| :03, :18, :33, :48 | **PDF de facturas** | Genera el PDF de las facturas y recibos emitidos y envía por email los de grupos y contratos LAU. | *Facturación y cobros* |
| :03, :18, :33, :48 | Emails de **check-in** | Pide completar los datos de llegada a 30 días de la entrada y lo recuerda cada 5 días. | *Comunicación con el residente* |
| :04, :19, :34, :49 | Emails de **check-out** | Aviso de salida y cuestionario a 10 días. | *Comunicación con el residente* |
| :05, :20, :35, :50 | Emails de **firma de contrato** | Recordatorio de firma cada 3 días (hoy desactivado). | *Contratos, garantías e INCASÒL* |
| :06, :21, :36, :51 | **Contratos** | Genera los contratos de las reservas en firma de contrato y de los grupos confirmados; envía a DocuSign los B2C y los de grupo con *Contrato OK*, y los anexos. | *Contratos, garantías e INCASÒL* |
| :06, :21, :36, :51 | Emails de **garantía** | Aviso a 40 días de la entrada y recordatorio cada 2 días desde 32 días. | *Contratos, garantías e INCASÒL* |
| :07, :22, :37, :52 | Emails de **documentación** | Aviso si faltan documentos a 20 días de la entrada (hoy desactivado). | *Reservas B2C* |
| :08, :23, :38, :53 | Emails de **pago** | Recordatorio a los 6 días de un cobro con tarjeta sin pagar (y a los 11, si existe su plantilla). | *Facturación y cobros* |
| :09, :24, :39, :54 | **Cargas Excel** | Procesa las cargas subidas en *Procesos › Cargas*. | *Inventario y precios*, *Reservas de grupo B2B*, *Informes y analítica* |
| :10, :25, :40, :55 | Email de **Trustpilot** | Invitación a dejar una reseña a 30 días de la salida. | *Operación diaria* |
| :11, :26, :41, :56 | **Estados de los grupos** | Pasa los grupos a *en curso* y a *revisión* por fecha. | *Reservas de grupo B2B* |
| :12, :27, :42, :57 | **Envío de emails pendientes** | Reintenta los emails que no se pudieron enviar. | *Comunicación con el residente* |
| :12, :27, :42, :57 | **Limpieza de salida de grupos** | Factura al pagador la limpieza de los pisos de los que han salido residentes. | *Reservas de grupo B2B* |
| :13, :28, :43, :58 | **Estados de la rooming list** | Pasa cada residente de grupo a *check-in*, *in house*, *check-out* o *revisada* según su fecha (sin gestión B2C, directamente). | *Reservas de grupo B2B* |

## Cada hora (en punto)

| Proceso | Qué hace | Capítulo |
|---|---|---|
| **Estado de los pisos** | Actualiza el estado actual de cada piso según sus bloqueos vigentes. | *Inventario y precios* |
| **Histórico de precios** | Registra los cambios de tarifa o de precio base de cada recurso. | *Inventario y precios* |

## Cada 2 horas

| Horas | Proceso | Qué hace | Capítulo |
|---|---|---|---|
| 03:00 y de 07:00 a 17:00 en horas impares | **Carga del data warehouse** | Recalcula la copia analítica que usa Power BI. | *Informes y analítica* |
| 08:00 a 20:00 en horas pares | **Web de Vanguard** | Regenera y publica la web. | *Captación* |
| 09:00 a 21:00 en horas impares | **Web de Cotown** | Regenera y publica la web. | *Captación* |

## Diario

| Hora | Proceso | Qué hace | Capítulo |
|---|---|---|---|
| 01:00 | **Comprobación de contratos** | Consulta en DocuSign el estado de todos los contratos y anexos pendientes de firma. | *Contratos, garantías e INCASÒL* |
| 02:00 y 02:30 | **Archivo de facturas** | Organiza los PDF de los dos últimos días y los copia a SharePoint. | *Facturación y cobros* |
| 04:00 | Reinicio del data warehouse | Mantenimiento técnico. | — |
| 05:00 | **Rentas máximas** | Recalcula el régimen de renta y las rentas máximas de cada piso y las reparte entre habitaciones y plazas. | *Inventario y precios* |
| 10:00 (UTC) | **Aviso a compañeros** | Avisa a los residentes de un piso de la llegada de un nuevo compañero (B2C y grupos con gestión B2C). | *Operación diaria* |

## Mensual

| Día | Proceso | Qué hace | Capítulo |
|---|---|---|---|
| 1, 00:00 (UTC) | **Edad avanzada** | Pasa a *edad avanzada* a los inquilinos LAU de más de 90 años y mantiene su fin a dos años vista. | *Contratos LAU y otros* |
| 28, 00:00 (UTC) | **IPC** | Fija el IPC y avisa al inquilino dos meses antes del mes de incremento; actualiza la renta un mes antes. | *Contratos LAU y otros* |

## Pendiente de confirmar

| Tema | Quién o qué lo confirma |
|---|---|
| — | — |
