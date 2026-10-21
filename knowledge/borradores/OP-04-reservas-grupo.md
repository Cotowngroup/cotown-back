# OP-4. Reservas de grupo B2B

> Manual funcional · Borrador v0.1 · 2026-10-20 · Las marcas **[PREGUNTA On]** se resuelven en la ronda de preguntas y desaparecen de la versión final.

## 4.1 Propósito

Este capítulo explica cómo se gestiona una reserva de grupo: una empresa, universidad o intermediario (el **pagador**) reserva un bloque de plazas o pisos para varias personas y paga por todas. Cubre el bloqueo, la confirmación, los precios, el contrato, la rooming list, la estancia, la salida y la devolución de la garantía.

## 4.2 Conceptos

| Concepto | Qué es |
|---|---|
| **Pagador** | Cliente empresa que contrata y paga el grupo. Firma el contrato y recibe las facturas. No usa el portal ni recibe los emails automáticos de reserva. |
| **Plazas** | Recursos concretos reservados para el grupo (habitaciones, plazas o pisos), indicados por su código. |
| **Piso completo** | El grupo reserva pisos enteros, no plazas sueltas. Cambia el cálculo de la fianza INCASÒL. |
| **Rooming list** | Relación de residentes del grupo: quién ocupa cada plaza y en qué fechas, con sus datos personales. Los residentes no son clientes del sistema. |
| **Gestión B2C** | Grupo cuyos residentes se atienden como residentes individuales: el personal confirma uno a uno su entrada, salida y revisión, y sus compañeros de piso reciben el aviso de llegada. Sin esta marca, el sistema da por hechas la entrada y la salida en las fechas previstas. |
| **Grupo master** | Contenedor que bloquea las plazas de un colectivo; dentro se generan después las reservas B2C de cada residente, porque cada uno paga su plaza. |
| **Tanda** (*grupo* en la rooming list) | Código que agrupa a los residentes que entran a la vez. La primera tanda (código 1) entra con el contrato; las siguientes se incorporan con un anexo. |
| **Precio por plaza** | Renta, servicios, garantía, membership fee y limpieza final del grupo se fijan **por plaza y mes**; el sistema multiplica por el número de plazas. |

## 4.3 Estados

| Estado | Significado | Cómo avanza |
|---|---|---|
| **Grupo bloqueado** | Plazas bloqueadas, todavía no confirmado. Precios, plazas y condiciones se pueden cambiar. | Al informar la fecha de confirmación → *grupo confirmado*. |
| **Grupo confirmado** | Confirmado y facturado el membership fee. | Llega la fecha de inicio → *en curso*. Si se borra la fecha de confirmación, vuelve a *bloqueado*. |
| **En curso** (*in house*) | El grupo está alojado. | Llega la fecha de fin → *revisión*. |
| **Revisión** | Pendiente de revisar los pisos. | Al informar la garantía a devolver y su fecha → *devolver garantía*. |
| **Devolver garantía** | Pendiente de devolver la garantía. | Al informar la garantía devuelta y su fecha → *finalizada*. |
| **Finalizada** | Cerrada. | — |
| **Cancelada** | Anulada a mano. Solo se puede cancelar un grupo sin facturas. | — |

Los cambios por fecha los hace un proceso automático cada 15 minutos.

Cada residente de la rooming list tiene su propio estado: **check-in**, **in house**, **check-out** y **revisada**.

## 4.4 Tareas

### Bloquear un grupo

**Cuándo**: cuando un cliente empresa pide plazas y se quieren reservar mientras se negocia.

**Qué informar**:

- **Pagador** (cliente empresa) y, si lo hay, **marketplace**. En los grupos de marketplace, el management fee de las facturas usa el porcentaje *marketplace* del recurso.
- **Edificio**, fechas y **número de plazas**.
- **Plazas**: códigos de los recursos reservados. Si es un piso completo, marcar *Piso completo*.
- **Precio por plaza**: renta y servicios mensuales, garantía, membership fee y limpieza final.
- **Forma de facturación** del primer y último mes (si no se indica, la de los recursos del edificio).
- **Frecuencia de limpieza** (decide el management fee).
- **IVA**: si el tipo de edificio no fija el IVA, el grupo se factura al 21 %; si se marca *No aplica IVA*, se factura exento, y entonces hay que indicar los inquilinos en la rooming list.
- **Gestión B2C**, si los residentes se atienden uno a uno.
- Direcciones a las que enviar las facturas (*Enviar factura a* y *cc*) y nota en factura.

**Renta limitada**: si los pisos tienen renta limitada, todos los del grupo deben tener el mismo régimen y la misma renta máxima, y hay que indicar el tipo de reserva (*limitada* o *recreativa*). Si no se indica renta, el sistema toma la media de las rentas máximas de las plazas.

**Qué hace el sistema**:

- Bloquea las plazas, y sus pisos y habitaciones, en la ocupación: dejan de estar disponibles en la web y en el planning.
- Crea una línea de la rooming list por plaza, con las fechas del grupo.
- Genera los **precios mensuales por plaza**, prorrateando los meses incompletos según la forma de facturación.
- Calcula la **garantía por plaza**: 1,5 × la renta (en renta limitada, 1,5 × la suma de renta, consumos, mobiliario y gastos), si no se ha indicado otra.
- En Barcelona, calcula la **fianza INCASÒL** del grupo (ver *Contratos, garantías e INCASÒL*).

Mientras el grupo está bloqueado, cambiar la renta regenera los precios mensuales; añadir o quitar plazas actualiza la rooming list y los bloqueos.

### Confirmar el grupo

**Cuándo**: el pagador acepta las condiciones.

**Cómo**: informar la **fecha de confirmación**.

**Qué hace el sistema**:

- Pasa el grupo a **confirmado**.
- Emite el **cobro y la factura de Cotown** del membership fee: número de plazas × membership fee por plaza.
- Fija la **garantía total** (garantía por plaza × plazas) y emite el **cobro y el recibo del propietario** por ese importe.
- Los precios mensuales quedan fijados: a partir de aquí ya no se regeneran.

**Comprobar antes**: que las plazas están asignadas, el precio es el acordado y el número de plazas coincide con los códigos indicados.

### Contrato del grupo

Para los grupos confirmados o en curso sin contrato, el proceso de contratos genera el contrato (y los anexos de Barcelona) pero **no lo envía**. El personal lo revisa en el grupo y marca **Contrato OK**; en la siguiente ejecución (cada 15 minutos) se envía a firmar por DocuSign al pagador. El estado de la firma se actualiza cada noche. Detalle en *Contratos, garantías e INCASÒL*.

**Anexos**: para incorporar una nueva tanda de residentes (o cambios) después de firmado el contrato se crea un **anexo** del grupo con el código de la tanda. El anexo se genera con los residentes de esa tanda y se envía a firmar automáticamente.

### Completar la rooming list

**Cuándo**: en cuanto el pagador envía los datos de los residentes, antes de la llegada.

**Cómo**: en la rooming list del grupo, o de forma masiva con la carga Excel **Rooming** (*Procesos › Cargas*), que identifica cada línea por grupo, código de residente y plaza. La plantilla se obtiene descargando el informe de rooming list del grupo.

**Qué informar por residente**: tanda (código 1 para los que entran con el contrato), nombre, documento de identidad, dirección, email, teléfono, nacionalidad, idioma, fechas de entrada y salida (dentro de las del grupo) y, si se conocen, hora de llegada y vuelo.

**Reglas**:

- Las fechas de entrada y salida deben estar dentro del periodo del grupo.
- Una misma plaza no puede tener dos residentes con fechas solapadas dentro del grupo.
- El grupo no puede acortarse si deja fuera precios o residentes ya registrados.

### Entrada y salida de los residentes

- **Grupo sin gestión B2C**: al llegar la fecha de entrada de cada residente, el sistema lo pasa directamente a *in house*; al llegar la de salida, a *revisada*.
- **Grupo con gestión B2C**: al llegar la fecha de entrada, el residente pasa a *check-in* y el personal confirma su llegada (*Check-in OK*) → *in house*. Al llegar la de salida, pasa a *check-out* y el personal confirma la revisión → *revisada*. Los compañeros de piso reciben el aviso de llegada de un nuevo residente.
- **Opciones de check-in o check-out de pago** (franja horaria o día): se cobran al **pagador** del grupo una sola vez, como una cantidad única para todas las plazas, según la ubicación y el día (laborable, viernes, sábado, domingo o festivo). El cobro se crea con el primer residente que tiene la opción informada.

El detalle de las tareas de entrada y salida está en *Operación diaria*.

### Durante la estancia

- **Facturación mensual automática** al pagador: una factura o recibo del propietario con una línea por piso y el número de plazas, y una factura del prestador de servicios; cobro por transferencia. Las facturas se envían por email a las direcciones del grupo (o del cliente), con copia al equipo de Cotown, y pueden incluir la rooming list. Ver *Facturación y cobros*.
- **Servicios adicionales del grupo**: conceptos extra facturados al pagador, igual que en las reservas B2C.
- **Limpieza de salida**: a medida que salen los residentes, el sistema factura al pagador la limpieza final de cada piso (limpieza por plaza × plazas que salen ese día).

### Cerrar el grupo y devolver la garantía

1. Al llegar la fecha de fin, el grupo pasa a **revisión**.
2. Revisar los pisos y registrar incidencias y desperfectos en la rooming list.
3. Informar la **garantía a devolver** y la fecha prevista → *devolver garantía*.
4. Al devolverla, informar la **garantía devuelta** y la fecha → *finalizada*.

La diferencia entre la garantía depositada y la devuelta es la parte retenida, que debe facturarse al pagador.

### Cancelar un grupo

Cambiar el estado a **cancelada**. Solo es posible si el grupo **no tiene facturas** (por ejemplo, un grupo bloqueado que no llega a confirmarse). Al cancelarlo se liberan sus plazas. Un grupo ya facturado hay que cerrarlo con rectificativas antes de cancelarlo.

### Grupos master

**Cuándo**: un colectivo (por ejemplo, un programa de una universidad) necesita un bloque de plazas, pero **cada residente paga su plaza**.

**Cómo**:

1. Crear el grupo marcado como **master**, con el pagador (la entidad que organiza el colectivo), las plazas y las fechas.
2. Para cada residente, crear su **reserva B2C** en una plaza del grupo, enlazada al grupo master.

**Qué hace el sistema**:

- El grupo master bloquea las plazas, pero **no genera precios** ni factura mensualidades.
- Las reservas B2C enlazadas **no ocupan plaza** por su cuenta (la ocupa el grupo) y **se facturan de forma individual** a cada residente, como cualquier reserva B2C.
- Las reservas B2C enlazadas **no generan contrato individual**: el contrato es el del grupo, con su pagador.

## 4.5 Automático y manual

| Qué | A / M |
|---|---|
| Alta del grupo, plazas y precios por plaza | M |
| Bloqueo de plazas, rooming list inicial, precios mensuales, garantía e INCASÒL | A |
| Confirmación | M |
| Membership fee y garantía: cobro, factura y recibo | A |
| Contrato: generación | A; revisión (*Contrato OK*), M; envío y seguimiento de la firma, A |
| Rooming list | M (a mano o por carga Excel) |
| Estados del grupo por fecha | A |
| Estados de los residentes | A (sin gestión B2C); M (con gestión B2C) |
| Facturación mensual y de limpiezas de salida | A |
| Revisión y devolución de la garantía | M |

## 4.6 Excepciones

| Situación | Qué pasa | Qué hacer |
|---|---|---|
| Error "No hay plazas asignadas" al confirmar | El grupo no tiene plazas creadas todavía. | Guardar primero el grupo con sus plazas y confirmarlo después, en un segundo paso. |
| Error "Pisos con diferentes tipos de limitación" o "con diferentes rentas máximas" | Las plazas pertenecen a pisos con regímenes de renta distintos. | Separar el grupo en varios, uno por régimen. |
| Error "No se puede cancelar una reserva con facturas" | El grupo ya tiene facturas. | Rectificar las facturas antes de cancelar. |
| Error "Hay rentas o check-ins anteriores a la fecha de inicio" (o posteriores al fin) | Se han cambiado las fechas del grupo dejando fuera precios o residentes. | Ajustar antes los precios y la rooming list. |
| Error "El pago del membership fee ya fue emitido" | Se ha vuelto a confirmar un grupo ya confirmado. | No volver a confirmar; corregir a mano el cobro si hace falta. |
| Se cambian precios después de confirmar | Los precios mensuales ya no se regeneran. | Ajustar a mano los meses afectados. |

## 4.7 Fuentes

| Tema | Dónde está |
|---|---|
| Validaciones, estados, precios, cobros e INCASÒL del grupo | Reglas de la base de datos de las reservas de grupo |
| Rooming list y estados de los residentes | Reglas y proceso programado de la base de datos de la rooming list |
| Limpieza de salida | Proceso programado de la base de datos |
| Contratos y anexos | Proceso automático de contratos |
| Facturación mensual | Proceso automático de facturación |
| Carga de la rooming list | Proceso automático de cargas |

## 4.8 Pendiente de confirmar

| Tema | Quién o qué lo confirma |
|---|---|
| — | — |
