# OP-8. Comunicación con el residente

> Manual funcional · Borrador v0.1 · 2026-10-21 · Las marcas **[PREGUNTA On]** se resuelven en la ronda de preguntas y desaparecen de la versión final.

## 8.1 Propósito

Este capítulo explica cómo se comunica el sistema con el residente: los **emails automáticos** (cuándo sale cada uno, quién lo envía, en qué idioma y con qué copias), cómo se mantienen sus plantillas y qué puede ver y hacer el residente en el **portal**.

## 8.2 Conceptos

| Concepto | Qué es |
|---|---|
| **Plantilla de email** | Asunto y cuerpo en español y en inglés, con variables que se rellenan con los datos de la reserva, el cliente o el cobro. Se mantienen en *Administración › Plantillas de email*. |
| **Plantilla activa** | Solo se envían los emails cuya plantilla **existe y está activa**. La tabla de plantillas es el interruptor: activar o desactivar una plantilla activa o desactiva ese email sin tocar nada más. |
| **Remitente** | Cotown o Vandor, según la plantilla. |
| **Copias** | Direcciones en copia (CC) o copia oculta (CCO) que se añaden a un email según la **marca** del piso (Cotown o Vanguard). |
| **Emails del cliente** | Registro de cada email generado para un cliente (*Clientes › Emails*): plantilla, entidad a la que se refiere, asunto y cuerpo enviados, y fecha de envío. |

## 8.3 Cómo funcionan los emails

1. Una regla o un proceso programado **genera** el email: lo registra en los emails del cliente con la plantilla y la reserva (o el cobro) a la que se refiere.
2. En ese momento el sistema lo **filtra**: lo descarta si la plantilla no existe o está desactivada, y si el cliente es una **empresa** (salvo el aviso de IPC). Si sigue adelante, añade las copias configuradas para la marca del piso.
3. Se **envía** en segundos. Si falla, se reintenta cada 15 minutos.
4. Al enviarse, quedan guardados el asunto y el cuerpo definitivos y la fecha de envío. Un email con fecha de envío no se vuelve a enviar.

**Idioma**: el del cliente (español o inglés). **Marca**: la del piso de la reserva; decide las copias.

**Envío manual**: para reenviar un email o enviar uno concreto, se añade a mano en los emails del cliente indicando la plantilla y la reserva.

## 8.4 Emails automáticos

| Email | Cuándo se genera | Remitente | Hoy |
|---|---|---|---|
| **solicitud** | Al crear una solicitud o reactivar una reserva descartada. | Cotown | Se envía |
| **alternativas** | Al enviar alternativas. | Cotown | Se envía |
| **pendientepago** | Al asignar recurso a una solicitud sin pagar. | Cotown | Se envía |
| **confirmada** | Al confirmarse la reserva. | — | Sin plantilla: no se envía |
| **caducada** | Al caducar el plazo de pago. | Cotown | Se envía |
| **descartada** / **descartadapagada** | Al descartar una reserva. | — | Sin plantilla: no se envía |
| **documentacion** | Si faltan documentos obligatorios a 20 días o menos de la entrada (como mucho, uno a la semana). | Cotown | Desactivado |
| **deposito** | A 40 días de la entrada, si la garantía no está pagada. | Cotown | Se envía |
| **depositorecall** | Cada 2 días a partir de 32 días de la entrada, si la garantía no está pagada. | Cotown | Se envía |
| **firmacontrato** | Al generarse el contrato. | Cotown | Desactivado de forma temporal |
| **firmacontratorecall** | Cada 3 días mientras el contrato no esté firmado. | Cotown | Desactivado de forma temporal |
| **completacheckin** | A 30 días o menos de la entrada, para que complete los datos de llegada. | Cotown | Se envía |
| **completacheckinrecall** | Cada 5 días mientras no complete los datos de llegada. | Cotown | Se envía |
| **checkinconfirmado** | Al informar la fecha de llegada. | Cotown | Se envía |
| **compis** | A 2 días o menos de la llegada de un nuevo residente, a sus compañeros de piso alojados (diario, 10:00 UTC). | Cotown | Se envía |
| **compisgroup** | Ídem, por la llegada de residentes de grupos con gestión B2C. | Cotown | Se envía |
| **keyless** | Al marcar *Llaves keyless OK*. | Cotown | Se envía |
| **inhouse** | Al confirmar la entrada: bienvenida. | Cotown | Se envía |
| **pago** | Al crearse un cobro mensual con tarjeta. | Cotown | Se envía |
| **pagorecall** | A los 6 días de un cobro mensual con tarjeta sin pagar. | Cotown | Se envía |
| **pagorecallagain** | A los 11 días de un cobro mensual con tarjeta sin pagar. | — | Sin plantilla: no se envía |
| **trustpilot** | A 30 días o menos de la salida, una vez: invitación a dejar una reseña. | Cotown | Se envía (con copia) |
| **checkoutproximo** | A 10 días o menos de la salida: datos de salida y cuestionario. | Cotown | Se envía (con copia) |
| **devolvergarantia** | Al pasar a *devolver garantía*. | — | Sin plantilla: no se envía |
| **ipc** | Dos meses antes de la actualización de la renta de un contrato LAU (ver *Contratos LAU y otros*). | Vandor | Se envía, con copia a Vandor |

Las reservas de destino de un cambio de habitación no generan *solicitud*, *pendientepago*, *confirmada* ni *keyless*, para no duplicarlos.

**Plantillas disponibles sin uso actual**: *bienvenida*, *cancelada*, *canceladapenalizacion*, *devolucion* (desactivadas) y *preconfirmada* (activa, pero ninguna regla la genera). Se conservan para usarlas en el futuro.

**Otros emails** que no pasan por las plantillas:

- Aviso al equipo comercial de cada lead (ver *Captación*).
- Facturas de grupos y de contratos LAU (ver *Facturación y cobros*).
- Emails de DocuSign para firmar los contratos.
- Email para crear o recuperar la contraseña del portal, que envía el sistema de inicio de sesión (Keycloak).

## 8.5 Tareas

### Activar o desactivar un email

En *Administración › Plantillas de email*, marcar o desmarcar **Activo**. Afecta a los emails que se generen a partir de ese momento; los ya enviados no cambian.

Para que se envíe un email que hoy no tiene plantilla (*confirmada*, *descartada*, *descartadapagada*, *devolvergarantia*, *pagorecallagain*), basta con crear la plantilla con ese nombre exacto y activarla.

### Cambiar el texto de un email

En la plantilla: asunto y cuerpo en español y en inglés (editor de texto enriquecido) y remitente. Las variables (`{{Customer.Name}}`, fechas, importes…) salen de la consulta de datos de la plantilla; si se necesita una variable nueva, hay que pedir a Oimbra que amplíe la consulta.

**Comprobar**: revisar los dos idiomas. Una variable mal escrita aparece vacía en el email.

### Configurar copias por marca

En la plantilla, apartado *Copiar a*: una fila por marca con las direcciones en CC y en CCO. Hoy tienen copias *trustpilot* y *checkoutproximo*.

### Consultar los emails enviados a un cliente

En *Clientes › Emails* de la ficha del cliente: cada email con su plantilla, fecha de envío, asunto y cuerpo tal como se enviaron. Un email sin fecha de envío está pendiente o ha fallado.

## 8.6 El portal del residente

El residente entra en el portal (área de cliente, desde `cotowngroup.com` o el enlace de las webs) con su email y contraseña.

| Sección | Qué puede ver y hacer |
|---|---|
| **Mis datos** | Datos personales, dirección, tutor (si es menor) y datos bancarios. Cada campo se rellena una sola vez: una vez guardado queda bloqueado (salvo teléfono e idioma) y los cambios posteriores los hace el personal, porque esos datos van al contrato y a la facturación. Edad mínima: 16 años. Foto de perfil. |
| **Contactos** | Contactos adicionales (tipo, nombre, email o teléfono). |
| **Documentos** | Los documentos que debe aportar, con anverso y reverso y fecha de caducidad si aplica. Puede subirlos y sustituirlos hasta que el personal los aprueba. |
| **Reservas** | Sus reservas B2C, con estado, fechas, motivo, recurso asignado y precios mes a mes. Según el estado: **anular** la solicitud (solicitud, alternativas, pendiente de pago), **aceptar una alternativa**, descargar el **certificado de residencia** (desde firma de contrato hasta la salida), informar **fecha, hora, transporte y opción de check-in** (desde *contrato*) y, desde 10 días antes de la salida, los de **check-out**. |
| **Cuestionarios** | Cuestionarios de check-in y check-out pendientes: puntuaciones, sí/no, texto, incidencias y fotos o vídeos. |
| **Facturas** | Sus facturas y recibos en PDF. |
| **Pagos** | Sus cobros. Los pendientes con tarjeta se pagan desde aquí, si tiene completos los datos fiscales y no queda pendiente el membership fee de la misma reserva. |
| **PDFs** | Documentos informativos de Cotown (normas, guías), en su idioma. |

El contrato no se firma en el portal sino en DocuSign; el portal muestra si está firmado.

**Qué hacer cuando el residente pide un cambio de un dato bloqueado**: corregirlo en su ficha de cliente en Airflows. Si el contrato ya está generado y el dato aparece en él, regenerar el contrato (ver *Contratos, garantías e INCASÒL*).

**Usuario y contraseña**: el usuario del portal se crea al registrarse el cliente en la web o al darlo de alta en Airflows.

**Contraseña olvidada o primer acceso**: en la pantalla de inicio de sesión, el enlace *¿Has olvidado tu contraseña?* envía al residente un email (desde el sistema de inicio de sesión) para crear una contraseña nueva, que se guarda en su usuario de Airflows. Es también la forma de dar acceso a un cliente dado de alta a mano en Airflows: se le indica que entre en el portal y use ese enlace con su email.

## 8.7 Automático y manual

| Qué | A / M |
|---|---|
| Generación, filtrado y envío de los emails | A |
| Plantillas: textos, activación, copias | M |
| Envío manual o reenvío de un email | M |
| Cambios de datos bloqueados del residente | M |

## 8.8 Excepciones

| Situación | Qué pasa | Qué hacer |
|---|---|---|
| El residente dice que no ha recibido un email | Puede que la plantilla esté desactivada o no exista, que el email haya fallado o que esté en su carpeta de spam. | Mirar sus emails en la ficha: si no aparece, el email se descartó por la plantilla; si aparece sin fecha de envío, está pendiente o ha fallado; si tiene fecha, se envió. |
| Un cliente empresa no recibe los emails de reserva | Los clientes de tipo empresa no reciben emails automáticos (salvo el de IPC). | Comunicarse con ellos directamente. |
| Un email sale con un dato vacío | La variable no existe o el dato falta en la reserva o el cliente. | Completar el dato o corregir la plantilla. |

## 8.9 Fuentes

| Tema | Dónde está |
|---|---|
| Generación de emails por estado | Reglas de la base de datos de las reservas y de los cobros |
| Emails periódicos | Procesos programados de la base de datos |
| Filtro y copias | Reglas de la base de datos de los emails del cliente |
| Envío | Proceso de escucha y proceso automático de envío (cada 15 minutos) |
| Plantillas | Airflows, *Administración › Plantillas de email* |
| Portal | Portal del residente |

## 8.10 Pendiente de confirmar

| Tema | Quién o qué lo confirma |
|---|---|
| — | — |
