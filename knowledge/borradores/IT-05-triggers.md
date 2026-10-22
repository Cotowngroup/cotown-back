# IT-5. Reglas de negocio en la base de datos

> Manual técnico · Borrador v0.1 · 2026-10-20 · Las marcas **[PREGUNTA Tn]** se resuelven en la ronda de preguntas y desaparecen de la versión final.

## 5.1 Propósito

Buena parte de la lógica del negocio no está en el servicio de integración sino en la propia base de datos de Airflows, como *triggers* (funciones que se ejecutan al crear, modificar o borrar un registro) y como procesos programados. Este capítulo describe, área por área, qué hace cada uno: qué valida, qué calcula, qué estados cambia y qué provoca en otras tablas. Es la referencia para entender por qué el sistema reacciona como lo hace ante un cambio y para interpretar los mensajes de error que ve el usuario.

## 5.2 Funcionamiento general

### Tipos de función

| Tipo | Cuándo se ejecuta | Para qué se usa |
|---|---|---|
| **B** (*before*) | Antes de guardar el registro (alta o modificación) | Validar, completar campos, calcular importes, cambiar el estado. Puede rechazar el cambio. |
| **A** (*after*) | Después de guardar | Efectos en otras tablas: cobros, disponibilidad, documentos, usuarios, emails. |
| **D** (*delete*) | Después de borrar | Limpieza: usuarios, roles. |
| **CRON** | Según calendario | Avances de estado por fecha, recordatorios, IPC, históricos. |

El nombre de cada función sigue el patrón `<Esquema>.<Tabla>_<Tipo><Orden>_<descripción>` (por ejemplo `Booking.Booking_B4_workflow`). Cuando una tabla tiene varios triggers del mismo tipo, PostgreSQL los ejecuta en orden alfabético de nombre, de modo que el número fija la secuencia: en una reserva B2C se ejecutan B1, B2, B3, B4, B5, B6 y B7 y, una vez guardada, A1, A2 y A3.

Un trigger puede modificar otras tablas, y esas modificaciones disparan a su vez sus propios triggers. Por ejemplo, registrar el pago de un cobro (`Payment`) actualiza el estado de la reserva, lo que dispara el flujo de la reserva y crea el cobro de la garantía y el email correspondiente.

Para poder escribir en tablas de sistema (usuarios, roles) y en tablas a las que el usuario no tiene acceso directo, varios triggers elevan temporalmente sus privilegios durante su ejecución.

### Mensajes de error

Cuando un trigger rechaza un cambio, lanza un error con el texto en inglés y en español separados por `!!!`: `!!!Wrong dates!!!Fechas incorrectas!!!`. El ERP y las aplicaciones muestran la parte del idioma del usuario. La sección 5.12 recoge los mensajes más habituales.

### Auditoría

Todas las tablas (153) tienen un trigger común, `Admin.audit`, que rellena automáticamente quién creó el registro y cuándo (`Created_by`, `Created_at`) y quién lo modificó por última vez y cuándo (`Updated_by`, `Updated_at`). No se guarda el historial de cambios campo a campo, salvo en las reservas B2C, que tienen su propio registro de acciones (`Booking_log`).

### Despliegue

El código de cada función está en el repositorio `back`, carpeta `function/`, un fichero por función. Se despliega cargándolo en Airflows, que crea el trigger o la tarea programada (ver *Arquitectura y plataforma*). Hay 86 funciones propias desplegadas: 61 triggers de negocio, 5 validadores genéricos usados en 25 tablas, la auditoría y 17 procesos programados, más 150 funciones de búsqueda que genera la plataforma.

## 5.3 Validadores genéricos

| Validador | Tablas | Qué comprueba |
|---|---|---|
| `validate_image` | 18 tablas con imagen (marketing, escuelas, oficinas, tipos de inventario y de característica…) | Que la imagen no supere 1920 píxeles de ancho ni de alto. |
| `validate_contact` | Contactos de clientes y de proveedores | Que haya email, teléfono o ambos. |
| `validate_NIF_NIE` | Clientes y proveedores | DNI: formato (8 dígitos y letra) y letra de control. NIE: formato (X, Y o Z, 7 dígitos y letra). Otros documentos no se validan. |
| `validate_iban` | Clientes y proveedores | Que el IBAN sea válido (incluida la cuenta nacional). |
| `validate_ccc` | Clientes | Que la cuenta bancaria sea un IBAN válido o, si no lo es, que venga acompañada de un código SWIFT válido. |

## 5.4 Reservas B2C

### Al crear o modificar una reserva

| Orden | Función | Qué hace |
|---|---|---|
| B1 | `init` (solo al crear) | Estado inicial *solicitud*; IVA según el tipo de edificio; promoción (la indicada por la web o, si no hay, la mejor vigente aplicable al edificio y a la tipología); membership fee según el precio base y la promoción. |
| B2 | `validate` | Validaciones de fechas (inicio y fin, check-in, check-out, nueva fecha de salida, caducidad, límite de documentación) y de reserva bloqueada. A partir de *pendiente de pago*: solapes con otras reservas del recurso, datos fiscales del cliente, lista negra (salvo autorización), motivo de estancia con escuela o empresa, y tipo de reserva obligatorio si el recurso tiene renta limitada. |
| B3 | `calc_prices` | Cuando cambian el recurso o las fechas, recalcula los precios mensuales no facturados (ver más abajo). Gestiona también la salida anticipada o extensión (ECO/EXT). |
| B3 | `incasol` | En Barcelona, calcula una única vez la fianza legal a depositar en el INCASÒL. |
| B4 | `workflow` | Flujo de estados de la reserva (ver más abajo), cobros de membership fee y garantía, y emails de cada cambio de estado. |
| B5 | `buttons` | Mantiene enlazadas las dos reservas de un cambio de habitación; envía el email de entrada sin llaves; calcula las URL de los botones de la ficha (*Reactivar*, *Descartar*, *Check-in OK*, *Check-out OK*). |
| B6 | `checkin` / `checkout` | Si el residente elige una opción de check-in o check-out, exige fecha y hora y crea el cobro según la ubicación y la franja: laborable, viernes, sábado, domingo o festivo. |
| B7 | `final_cleaning` | Para reservas desde junio de 2024 con limpieza final, crea el servicio adicional de limpieza de salida. |
| A1 | `init` (solo al crear) | Crea el cobro del membership fee, escribe en el registro de la reserva y envía el email de *solicitud*. |
| A2 | `update_availability` | Actualiza la tabla de ocupación: bloquea el recurso reservado y sus padres e hijos (piso, habitación, plaza) mientras la reserva esté en un estado que ocupa. |
| A3 | `docs` | Crea en la ficha del cliente los documentos que debe aportar según su tipo de identificación y su motivo de estancia. |

### Cálculo de precios

- **Duración**: corta (menos de 3 meses), media (de 3 a 6) o larga (7 o más). Fija qué renta del precio base se aplica.
- **Renta libre o recreativa**: renta del precio base del año académico × multiplicador de la tarifa del recurso × incrementos por características; más servicios, garantía, limpieza final, segundo residente y límite de suministros. A partir de septiembre se usan los precios del año académico siguiente.
- **Renta limitada**: rentas máximas del recurso (renta, servicios, suministros, mobiliario y gastos) calculadas por el proceso de rentas máximas. En régimen LAU no hay gastos; en régimen de índice, no hay mobiliario.
- **Garantía**: la del precio base, con un mínimo de 1,5 × (renta + segundo residente); en renta limitada, 1,5 × la suma de los conceptos.
- **Precio mensual** (`Booking_price`): una fila por mes con renta, servicios y descuentos. Las promociones se aplican a los meses dentro de su periodo: un descuento en porcentaje se aplica sobre el precio total (renta y servicios); un descuento en importe, solo sobre la renta.
- **Precios ajustados a mano**: al cambiar las fechas o el recurso, los meses no facturados se recalculan con la tarifa y sustituyen cualquier importe puesto a mano. Tras un cambio así hay que revisar los ajustes manuales. Los meses incompletos se facturan completos, por quincena o de forma proporcional a los días, según la forma de facturación del recurso (y la específica del último mes).
- **ECO/EXT**: al informar una nueva fecha de salida, se borran los meses no facturados afectados, se recalculan y la fecha de fin pasa a ser la nueva; la anterior se guarda y Operaciones debe confirmar el cambio.

### Flujo de estados

![Ciclo de vida de la reserva B2C](../diagramas/Ciclo%20reserva%20B2C%20v2.png)

Lo gestiona `B4_workflow` en cada modificación, más el proceso programado `Booking_CRON_workflow` para los cambios por fecha:

| Desde | Hacia | Cuándo |
|---|---|---|
| Solicitud / alternativas | Pendiente de pago | Se asigna un recurso. El plazo de pago es de al menos 2 días. |
| Solicitud / alternativas (pagadas) | Confirmada | Se asigna un recurso con el membership fee ya pagado. |
| Solicitud (pagada o no) | Alternativas (pagada o no) | El personal envía alternativas con el botón. |
| Alternativas | Solicitud | El cliente acepta una alternativa en el portal (se copian edificio y tipologías). |
| Pendiente de pago | Confirmada | Se paga el membership fee, o la reserva viene de un marketplace que lo ha cobrado. |
| Pendiente de pago | Caducada | Vence el plazo de pago (al modificarla o por el proceso programado). |
| Caducada | Pendiente de pago | El personal amplía el plazo. |
| Caducada | Descartada | Lleva más de 5 días caducada (proceso programado). |
| Confirmada | Documentación OK | La reserva no exige documentos o tiene al menos un documento aprobado (basta con uno). |
| Confirmada | Documentación KO | Vence el plazo de documentación (14 días; proceso programado). El sistema no trata este estado: Operaciones lo gestiona a mano (reclama la documentación o descarta la reserva). |
| Documentación OK | Firma de contrato | La garantía está pagada o es cero. En reservas de marketplace se pasa directamente desde *confirmada*. |
| Confirmada / documentación OK | Descartada pagada | Entrada en menos de 30 días y garantía emitida hace más de 4 días sin pagar (proceso programado). |
| Firma de contrato | Contrato | DocuSign notifica la firma. |
| Contrato | Firma de contrato | La firma se anula; el contrato se regenera. |
| Contrato | Check-in confirmado | Se informa la fecha de llegada. |
| Contrato / check-in confirmado | Check-in | Llega la fecha de entrada (proceso programado). |
| Check-in | In house | El personal pulsa *Check-in OK*. |
| In house | Check-out | Llega la fecha de salida (proceso programado). |
| Check-out | Revisión | El personal pulsa *Check-out OK*. |
| Revisión | Devolver garantía | El personal marca la revisión como correcta. |
| Devolver garantía | Finalizada | Se registra la devolución de la garantía sin retención. |
| Descartada pagada | Descartada | Se registra la devolución del membership fee. |
| Descartada (pagada o no) | Solicitud (pagada o no) | El personal pulsa *Reactivar*: se vuelve a emitir el membership fee. |
| Cualquiera | Cancelada | A mano. |

**Efectos de cada estado:**

| Estado | Efectos automáticos |
|---|---|
| Pendiente de pago | Email *pendientepago*. |
| Confirmada | Fecha de confirmación, plazo de documentación (14 días), se borran las alternativas, email *confirmada*. |
| Documentación OK | Se emite el cobro de la garantía (al terminal del propietario). |
| Caducada / descartada | Email del estado; al descartar se quita el recurso y se borran los cobros no pagados. |
| Firma de contrato | Al generarse el contrato, email *firmacontrato*. |
| Check-in confirmado | Email *checkinconfirmado*. |
| In house | Cuestionario de check-in y email *inhouse*. |
| Devolver garantía | Email *devolvergarantia*. |
| Cancelada | Se borran los cobros no pagados. |

Cada cambio de estado queda registrado en el log de la reserva. Las reservas destino de un cambio de habitación no envían los emails comerciales.

### Cambios de importes

- Si se cambia el membership fee o la garantía y el cobro aún no está pagado, se sustituye por uno nuevo. Si ya está pagado, solo se muestra un aviso.
- Si se cambia un descuento de un mes con *Aplicar a todos*, se copia al resto de meses. Todo descuento exige un motivo.

## 5.5 Alternativas, precios y servicios de la reserva

| Tabla | Qué hacen sus triggers |
|---|---|
| **Alternativas** (`Booking_option`) | Exigen el tipo de plaza. Cuando el cliente acepta una alternativa, la reserva toma su edificio y tipologías y vuelve a *solicitud*. |
| **Precio mensual** (`Booking_price`) | Calculan el descuento en importe y en porcentaje, el total del mes y la copia a todos los meses. |
| **Servicios adicionales** (`Booking_service`) | Según el tipo: inmediato (sin fechas), puntual (fecha de facturación) o recurrente (inicio y fin). Por defecto los factura Cotown, salvo los de tipo renta, que factura el propietario; el IVA y el concepto salen del producto. |

## 5.6 Reservas de grupo (B2B)

| Función | Qué hace |
|---|---|
| `B1_validate` | Fechas coherentes con los precios y la rooming list; número de plazas; no permite cancelar un grupo con facturas. Mientras el grupo está bloqueado, comprueba que todos los pisos tengan el mismo régimen y la misma renta máxima, aplica rentas limitadas si corresponde y calcula la garantía por plaza (1,5 × la base). |
| `B2_incasol` | Fianza legal INCASÒL por plaza en Barcelona. |
| `B2_workflow` | Al informar la fecha de confirmación pasa a *confirmado* y emite el cobro y la factura del membership fee (plazas × importe) y, al informar la garantía, el cobro y el recibo de garantía del propietario. Avanza a *en curso* al llegar la fecha de inicio, a *revisión* al llegar la de fin, a *devolver garantía* y a *finalizado* según se informan las garantías exigida y devuelta. |
| `A1_create_prices` | Mientras el grupo está bloqueado, genera los precios mensuales por plaza. |
| `A2_create_rooms` | Convierte la lista de plazas en registros de plaza y de rooming list, y bloquea la ocupación de esas plazas y sus pisos. |

**Rooming list** (`Booking_group_rooming`): valida fechas y solapes de la misma plaza dentro del grupo; gestiona el estado de cada residente (check-in, in house, check-out, revisada), que en grupos gestionados como B2C exige la confirmación del personal; y cobra al pagador del grupo (el intermediario) los servicios de check-in y check-out elegidos.

## 5.7 Reservas LAU y otros

| Función | Qué hace |
|---|---|
| `B1_validate` | Fechas coherentes; fecha estimada de fin por defecto; en contratos LAU con cálculo automático, fechas de pre-capex (fin de mes + 2 meses tras la fecha estimada) y capex (4 meses más); fecha de ITP (un mes tras la compensación) y aportación recomendada. |
| `A1_locks` | Crea los bloqueos de disponibilidad del recurso: el del contrato (sin fecha estimada: hasta 2099; con fecha estimada: hasta ella; con fecha de fin: hasta ella) y, si procede, los de pre-capex y capex. Estos bloqueos solo se pueden modificar desde el propio contrato. |

## 5.8 Facturación

| Tabla | Función | Qué hace |
|---|---|---|
| **Factura** | `B1_copy` / `A1_copy` | Al crear una factura indicando otra en *Duplicar*, copia su cabecera y sus líneas. |
| | `B2_validate` | Datos obligatorios (tipo, medio de pago, emisor, concepto, reserva) y cliente deducido de la reserva. Al emitirla: importe positivo (negativo en rectificativas), **numeración** según el patrón del emisor y contador anual, y fecha de emisión. Una factura emitida no se puede modificar ni borrar (los recibos sí se pueden borrar). Al marcarla como rectificada, crea y emite la **rectificativa** con las líneas en negativo. |
| **Línea de factura** | `B1_change` | IVA y concepto por defecto del producto; piso de la reserva si no se indica recurso; **management fee** de la línea si el emisor no es Cotown, según la frecuencia de limpieza de la reserva (la frecuencia `marketplace` usa el porcentaje de marketplace del recurso; el marketplace de la reserva no interviene). Impide cambiar líneas de facturas emitidas. |
| | `A1_sum_amount` | Recalcula el total de la factura. |
| **Cobro** | `B1_process_payment` | Al registrar la fecha de pago: si es manual, genera la referencia de pago; si es un membership fee, avanza la reserva (*solicitud pagada*, *alternativas pagada* o *confirmada*); si es una garantía, la registra y avanza la reserva a *firma de contrato*. Si la reserva no se puede actualizar, el pago se guarda igualmente y el problema queda anotado en el log de la reserva. |
| | `A1_insert` | Al crear un cobro mensual con tarjeta, envía el email *pago* con el enlace al portal. |

Los patrones de numeración se configuran en la ficha de cada proveedor (facturas, recibos, rectificativas y sus variantes LAU); `[Y]` es el año y `[N]` el número correlativo con 5 dígitos.

## 5.9 Clientes, proveedores y usuarios

| Tabla | Qué hacen sus triggers |
|---|---|
| **Cliente** | Email único; normalización de IBAN, cuenta y SWIFT; los menores de edad exigen tutor; IBAN de país SEPA; datos del titular si la cuenta es distinta del IBAN; al modificarlo, crea los documentos que le corresponden por su tipo de identificación y sincroniza el email con su usuario. Si se marca *Crear usuario*, crea su usuario de acceso (`C` + número) con rol de cliente y envía el email de *bienvenida*. Al borrarlo, borra su usuario. |
| **Documento de cliente** | La fecha de caducidad no puede estar vencida. Al aprobar un documento vinculado a una reserva confirmada, se reevalúa el paso a *documentación OK*. |
| **Email de cliente** | Descarta los emails a empresas (salvo el de IPC) y los de plantillas desactivadas; añade las copias configuradas para la marca; avisa al servicio de envío (ver *Procesos automáticos*). |
| **Proveedor** | Al crearlo, crea su usuario (`P` + número) con rol de proveedor; sincroniza el email; al borrarlo, borra su usuario. |
| **Plantilla de contrato** | Al activar una plantilla, desactiva las demás del mismo proveedor, tipo y ubicación. |
| **Usuario y rol de personal** | Al dar de alta a una persona, crea su usuario (`X` + número) con el rol base de personal; al asignar o quitar roles, los aplica en Airflows y en la base de datos. |

## 5.10 Inventario

| Tabla | Qué hacen sus triggers |
|---|---|
| **Edificio** | Al cambiar el código del edificio, recodifica todos sus recursos. |
| **Recurso** | Valida el formato del código según el tipo (`XXXnnn.nn.nn` piso, `….Hnn` habitación, `….Hnn.Pn` plaza, que debe empezar por el de su habitación); genera la URL de su calendario iCal; propaga del piso a sus habitaciones y plazas el edificio, el propietario, el prestador de servicios, la forma de facturación, la modalidad de venta, el código SAP y los management fees. Al dar de alta o baja un recurso, recalcula la fracción del piso que representa cada uno. |
| **Disponibilidad** (`Resource_availability`) | El estado por defecto (*cosharing*) no se registra; la fecha de fin debe ser posterior a la de inicio; los bloqueos que vienen de contratos LAU no se pueden tocar a mano. Cada bloqueo se refleja en la tabla de ocupación para el recurso y sus padres e hijos. |
| **Forecast / stabilised** | Ocupación máxima 100 %; los porcentajes por duración no pueden sumar más de 100. |
| **Inventario** | Fecha de compra no futura; garantía posterior a la compra. |
| **Valoración** | Copia la última valoración a la ficha del recurso. |

## 5.11 Procesos programados en la base de datos

| Proceso | Frecuencia | Qué hace |
|---|---|---|
| `Booking_CRON_workflow` | Cada 15 min | Caducidad de pendientes de pago, vencimiento del plazo de documentación, descarte de caducadas, descarte por garantía impagada, paso a *check-in* y *check-out* por fecha; borra los cuestionarios de check-in no completados en 7 días. |
| `Booking_CRON_checkin_emails` | Cada 15 min | *completacheckin* cuando faltan 30 días o menos para la entrada; recordatorio cada 5 días. |
| `Booking_CRON_checkout_emails` | Cada 15 min | *checkoutproximo* y cuestionario de check-out cuando faltan 10 días o menos para la salida. |
| `Booking_CRON_contract_emails` | Cada 15 min | *firmacontratorecall* cada 3 días mientras el contrato no esté firmado. |
| `Booking_CRON_deposit_emails` | Cada 15 min | *deposito* a 40 días de la entrada y *depositorecall* cada 2 días a partir de 32 días, mientras la garantía no esté pagada. |
| `Booking_CRON_document_emails` | Cada 15 min | *documentacion* (como mucho uno a la semana por cliente) si faltan documentos obligatorios a 20 días o menos de la entrada. |
| `Booking_CRON_payment_emails` | Cada 15 min | *pagorecall* a los 6 días y *pagorecallagain* a los 11 días de un cobro mensual con tarjeta sin pagar. |
| `Booking_CRON_trustpilot_emails` | Cada 15 min | *trustpilot*, una vez, cuando faltan 30 días o menos para la salida. |
| `Booking_CRON_notice_emails` | Diario, 10:00 UTC | *compis* a los residentes del piso cuando faltan 2 días o menos para la llegada de un nuevo compañero. |
| `Booking_group_CRON_workflow` | Cada 15 min | Grupos a *en curso* y a *revisión* por fecha. |
| `Booking_group_CRON_bill_cleaning` | Cada 15 min | Factura la limpieza de salida de los pisos de los grupos a medida que salen los residentes. |
| `Booking_group_rooming_CRON_workflow` | Cada 15 min | Estado de cada residente de grupo por fecha. |
| `Booking_group_rooming_CRON_notice_emails` | Diario, 10:00 UTC | *compisgroup*: aviso de llegada de residentes de grupos gestionados como B2C. |
| `Booking_other_CRON_IPC` | Mensual, día 28 | Dos meses antes del mes de actualización, fija el IPC a aplicar (con su tope) y avisa al inquilino (email *ipc*, con copia a Vandor); un mes antes, actualiza la renta y guarda la anterior. |
| `Booking_other_CRON_advanced_age` | Mensual, día 1 | Inquilinos LAU de más de 90 años: subtipo *edad avanzada*, fin estimado a dos años vista y sin pre-capex ni capex. |
| `Resource_CRON_history` | Cada hora | Registra en el histórico de precios los cambios de tarifa o de precio base de cada recurso. |
| `Resource_CRON_status` | Cada hora | Actualiza el estado actual de cada piso según su disponibilidad. |

## 5.12 Mensajes de error más habituales

| Mensaje (español) | Dónde | Causa |
|---|---|---|
| Fechas incorrectas | Reservas, grupos, LAU | La fecha de fin es anterior a la de inicio. |
| Solapamiento … con la reserva … | Reserva B2C | El recurso ya está ocupado en esas fechas por otra reserva. |
| Cliente sin datos fiscales | Reserva B2C | Faltan tipo de documento, documento o dirección del cliente. |
| Cliente en lista negra: "…" | Reserva B2C | El cliente está en lista negra y no se ha marcado *Ignorar lista negra*. |
| Motivo no seleccionado / Escuela no seleccionada / Compañía no indicada | Reserva B2C | Faltan el motivo de estancia o los datos que exige. |
| Recurso con renta limitada | Reserva B2C | El recurso tiene renta limitada y no se ha indicado el tipo de reserva (limitada o recreativa). |
| Reserva bloqueada | Reserva B2C | Se intenta cambiar el recurso de una reserva marcada como bloqueada. |
| El tipo de plaza es obligatoria | Reserva, alternativa | Falta la tipología de plaza en una reserva que no es de piso completo. |
| Fecha de check in/check out no puede ser… | Reserva, rooming | Las fechas reales quedan fuera del periodo contratado. |
| Debes indicar la fecha/hora de check-in / Servicio no disponible | Reserva, rooming | Se ha elegido una opción de check-in o check-out sin fecha u hora, o no hay precio para esa franja. |
| Motivo del descuento obligatorio | Precio mensual | Descuento sin motivo. |
| Pisos con diferentes tipos de limitación / rentas máximas | Grupo | Las plazas del grupo están en pisos con régimen o renta máxima distintos. |
| No se puede cancelar una reserva con facturas | Grupo | El grupo tiene facturas con importe. |
| No se puede cambiar/borrar una factura emitida | Factura | La factura ya está numerada. Para corregirla, se rectifica. |
| Factura con importe menor o igual a 0 | Factura | Se intenta emitir una factura sin líneas o con total no positivo. |
| Falta indicar la reserva B2C, B2B u otra / Falta indicar el cliente | Factura | Factura manual sin reserva o sin cliente. |
| El recurso (piso) es obligatorio | Línea de factura | Línea sin recurso en una factura sin reserva B2C. |
| Ya existe ese email / El email ya existe | Cliente, proveedor, usuario | El email ya está en uso. |
| Menores requieren tutor | Cliente | Cliente menor de 18 años sin datos de tutor. |
| IBAN de un país no-SEPA / No es un IBAN válido | Cliente, proveedor | IBAN incorrecto o de un país fuera de la zona SEPA. |
| El DNI/NIE introducido no es válido | Cliente, proveedor | Formato o letra de control incorrectos. |
| Código de piso/habitación/plaza incorrecto | Recurso | El código no sigue el formato del tipo de recurso. |
| NO se pueden modificar bloqueos de reservas LAU | Disponibilidad | El bloqueo pertenece a un contrato LAU; se cambia desde el contrato. |
| Cosharing es el estado por defecto | Disponibilidad | No se registra el estado por defecto. |
| La imagen no puede ser más ancha/alta de 1920px | Tablas con imagen | Imagen demasiado grande. |

## 5.13 Fuentes

| Tema | Dónde está |
|---|---|
| Código de las funciones | `back/function/` (un fichero por función) |
| Triggers desplegados | Catálogo de PostgreSQL (`pg_trigger`) en `niledb` |
| Procesos programados | Airflows (`Models.Function`) y pg_cron |

## 5.14 Pendiente de confirmar

No hay puntos pendientes.
