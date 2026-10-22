# OP-2. Captación

> Manual funcional · Borrador v0.1 · 2026-10-20 · Las marcas **[PREGUNTA On]** se resuelven en la ronda de preguntas y desaparecen de la versión final.

## 2.1 Propósito

Este capítulo explica cómo llegan los interesados y las reservas al sistema: por las webs (formularios y asistente de reserva), por el chatbot, por los canales directos (teléfono, email, WhatsApp, oficina) y por los marketplaces. Termina cuando existe una **solicitud** de reserva en Airflows; lo que sigue está en *Reservas B2C*.

También explica qué se gestiona desde Airflows para que las webs muestren la información correcta y qué hay que avisar cuando cambia la oferta.

## 2.2 Conceptos

| Concepto | Qué es |
|---|---|
| **Lead** | Interesado que ha dejado sus datos (formulario, chatbot o solicitud de reserva). Se registra en **Pipedrive**, el CRM comercial; no en Airflows. |
| **Oportunidad** (*deal*) | Seguimiento comercial de un lead en el embudo de reservas de Pipedrive. Empieza en la etapa *Lead entrante* o, si viene de una solicitud de reserva web, en *Reserva pendiente*. |
| **Solicitud** | Primer estado de una reserva en Airflows: el cliente ha pedido un edificio, una tipología y unas fechas, todavía sin recurso concreto. |
| **Canal** | Por dónde llegó la reserva: web, marketplace, teléfono, email, WhatsApp, chatbot, oficina, referido, redes sociales, B2B… y los canales internos de cambio, extensión, *retention* y descartada pagada (ver *Registrar una reserva a mano*). |
| **Cómo nos conoció** | Origen comercial declarado por el cliente: redes sociales, un amigo, un intermediario o un portal concreto (Idealista, Spotahome, Uniplaces, Erasmus Play…). |
| **Solicitante** | Quién hace la reserva: el propio cliente, una empresa, un familiar o un agente. |
| **Marketplace** | Intermediario (Airbnb, Spotahome, Uniplaces, Housing Anywhere…) que trae reservas a cambio de una comisión, una cuota mensual o una cuota anual. Se mantienen en *Propietarios › Marketplaces*. |
| **Motivo de estancia** | Estudios, trabajo (laboral o prácticas), estudios y trabajo, o vacaciones/recreativo. Decide qué datos y documentos se piden. |

## 2.3 Tareas

### Atender un lead de un formulario web

**Qué llega**: las webs tienen formularios de **contacto**, **visita**, **disponibilidad** y **reserva ahora**. Al enviarse, el sistema:

1. Crea o actualiza la **persona** en Pipedrive (por email), con nombre, teléfono, idioma, fecha de nacimiento, nacionalidad y comentarios.
2. Crea un **lead** con tipo (B2C), canal *Directo* y subcanal *Web*, marca, web, formulario, motivo, edificio, ciudad, tipología, presupuesto, fechas y los datos de la campaña publicitaria de la que vino el visitante.
3. Crea una **oportunidad** en el embudo de reservas, en *Lead entrante*.
4. Envía un **email de aviso** al equipo comercial (`book@cotown.com`), con el fichero adjunto si el formulario lo tenía.

Si el interesado ya tenía un lead u oportunidad abiertos, se actualizan en lugar de duplicarse.

**Qué hacer**: el seguimiento comercial (llamar, enviar información, concertar la visita) se hace en Pipedrive. Si el interesado decide reservar, se le dirige al asistente de reserva de la web o se registra la reserva a mano (ver más abajo).

**Protección contra envíos automáticos**: el sistema descarta en silencio los formularios rellenados por robots (los que se envían en menos de 3 segundos o rellenan un campo oculto).

### Atender un lead del chatbot

Las webs tienen un chatbot de un proveedor externo. El propio proveedor envía sus conversaciones a Pipedrive como leads con el formulario *Chatbot*, sin pasar por los sistemas de Cotown. Se atienden igual que los leads de los formularios.

### Recibir una solicitud de reserva desde la web

**Cómo reserva el cliente**: desde la página de una ciudad, un edificio o una residencia, elige fechas, ve la disponibilidad y pulsa *Reservar*. El asistente de reserva:

1. **Resultados**: muestra los edificios y tipologías con recursos libres en esas fechas, ordenados por precio. El precio mensual depende de la duración de la estancia (ver *Inventario y precios*).
2. **Resumen y datos**: muestra el desglose (renta del primer y último mes, servicios, garantía, membership fee, limpieza final, detalle mensual y promoción aplicada). El cliente inicia sesión o se registra e indica el motivo de estancia, con la escuela o la empresa según el motivo. Si es menor de edad, se piden los datos del tutor.
3. **Confirmación**: crea la solicitud y muestra su número.

**Regla de Barcelona (Cotown)**: por la Ley de vivienda, en la web de Cotown, en Barcelona solo se admite el motivo *vacaciones – recreativo*, con la declaración de estancia recreativa. La declaración queda anotada en los comentarios de la solicitud. En la web de Vanguard no hay esta restricción.

**Qué hace el sistema al crear la solicitud**:

- La registra con canal *Web*, la tipología pedida, el motivo, los comentarios (edificio, tipología y extras elegidos) y la **promoción que se mostró** al cliente.
- Si el cliente ya tiene una solicitud idéntica (mismas fechas, edificio y tipología), no crea otra.
- Calcula el membership fee y crea su **cobro**, que el cliente paga después desde el portal del residente.
- Envía al cliente el email de *solicitud*.
- Envía el lead a Pipedrive con la oportunidad en la etapa *Reserva pendiente*.

**Qué hacer**: atender la solicitud: asignar recurso o proponer alternativas (ver *Reservas B2C*).

### Registrar una reserva a mano

**Cuándo**: la reserva llega por teléfono, email, WhatsApp, oficina, un referido o un marketplace.

**Qué informar** además de los datos de la reserva (cliente, edificio, tipología, fechas, motivo):

- **Canal** por el que llegó.
- **Cómo nos conoció**, si el cliente lo dice.
- **Solicitante**: cliente, empresa, familiar o agente.
- **Marketplace**, si viene de uno (ver la tarea siguiente).
- **Promoción**: si no se indica, el sistema aplica la mejor promoción activa que valga para cualquier régimen de renta. Las promociones solo para renta libre o solo para renta limitada se asignan a mano.

**Canales internos**: no son canales comerciales; se usan para reservas que nacen de otra:

| Canal | Uso |
|---|---|
| Cambio | Reserva de destino de un cambio de habitación. |
| Extensión | Extensión registrada como reserva nueva. |
| Retention | Renovación de un residente actual para un nuevo periodo. |
| Descartada Pagada | Nueva reserva de un cliente con una reserva descartada cuyo membership fee ya estaba pagado. |

**Qué hace el sistema**: lo mismo que con una solicitud web (membership fee, cobro, email de *solicitud*), salvo el envío a Pipedrive, que solo hacen las solicitudes web. Si se quiere seguimiento comercial de una reserva manual, se registra a mano en Pipedrive.

**Comprobar**: que el cliente no existe ya antes de darlo de alta, para no duplicarlo.

### Gestionar las reservas de marketplaces

**Publicar la disponibilidad**: cada recurso tiene una URL de calendario (iCal) que se da de alta en el marketplace. El marketplace la consulta periódicamente y bloquea las fechas ocupadas. Desde el viernes a las 10:00, el calendario marca también como ocupados los días libres del fin de semana en curso, para evitar reservas de última hora.

**Registrar la reserva**: las reservas de marketplace se registran a mano en Airflows, con canal *Marketplace* e indicando el **marketplace**.

**Membership fee cobrado por el marketplace**: si el marketplace cobra él el membership fee, se marca en la reserva. Entonces:

- Al asignar recurso, la reserva pasa directamente a **confirmada**, sin esperar al pago del membership fee.
- No se exige documentación: con la garantía pagada (o sin garantía), pasa a **firma de contrato**.

**Management fee**: al registrar la reserva, poner la frecuencia de limpieza *marketplace* para que la facturación use el porcentaje *marketplace* del recurso. El sistema no la pone solo: indicar el marketplace no cambia el porcentaje.

**Datos del marketplace** (*Propietarios › Marketplaces*): tipo (comisionista, referral, cuota mensual o anual), forma de cobro de la comisión (de la primera renta, por domiciliación o por transferencia), porcentaje o importe, contacto y facturas recibidas. Ningún proceso los usa: son la referencia para revisar a mano las facturas que emiten los marketplaces.

### Avisar de un edificio, ciudad o tipología nuevos

Pipedrive tiene sus propias listas de edificios, ciudades y tipologías. La integración traduce los datos de Cotown a esas listas, y la traducción está en el código del servicio.

**Qué hacer**: al abrir un edificio, una ciudad o una tipología nuevos, crear la opción en Pipedrive y pedir a Oimbra que actualice la integración. Hasta entonces, los leads de ese edificio, ciudad o tipología llegan a Pipedrive sin ese dato.

### Mantener los contenidos de las webs

Casi todo lo que muestran las webs se gestiona en Airflows:

| Contenido | Dónde |
|---|---|
| Textos de las páginas y textos legales | *Marketing › Textos* |
| Imágenes | *Marketing › Imágenes* y las fichas de ciudades, barrios, edificios, tipologías y servicios |
| Blog, etiquetas y autores | *Marketing* |
| Preguntas frecuentes (generales, por ciudad o por edificio) | *Marketing* |
| Banners, ventajas, socios, testimonios, redes sociales, oficinas | *Marketing* |
| Textos web de ciudades, barrios, edificios y tipologías | En cada ficha |
| Qué se publica | Ciudades publicadas, edificios activos, web asignada a cada piso, modalidad de venta (ver *Inventario y precios*) |
| Precios, promociones y disponibilidad | Precios base, tarifas, promociones y bloqueos (ver *Inventario y precios*) |

**Cuándo se ve**: las webs se regeneran cada 2 horas (Vanguard en las horas pares de 8:00 a 20:00 y Cotown en las impares de 9:00 a 21:00). Un cambio tarda hasta 2 horas en publicarse; los cambios hechos por la noche se publican a partir de las 8:00. Para publicar antes hay que pedírselo a Oimbra.

**Comprobar**: tras publicar contenido nuevo, revisar la página en las dos lenguas. Si falta el texto en inglés, la web muestra el español.

Los textos admiten etiquetas de terceros (por ejemplo, códigos de seguimiento o de verificación), que se insertan en todas las páginas: conviene que solo las añadan personas que sepan lo que hacen.

## 2.4 Automático y manual

| Qué | A / M |
|---|---|
| Lead, persona y oportunidad en Pipedrive desde formularios y solicitudes web; email de aviso | A |
| Seguimiento comercial de los leads | M (en Pipedrive) |
| Solicitud de reserva desde la web, con promoción, cobro del membership fee y email | A |
| Registro de reservas por canales directos y marketplaces | M |
| Publicación del calendario iCal para los marketplaces | A |
| Avance a confirmada de las reservas con membership fee cobrado por el marketplace | A |
| Aviso de edificios, ciudades o tipologías nuevos para Pipedrive | M |
| Contenidos de las webs | M |
| Regeneración y publicación de las webs | A (cada 2 horas) |

## 2.5 Excepciones

| Situación | Qué pasa | Qué hacer |
|---|---|---|
| Falla el envío a Pipedrive | El lead de un formulario no llega al CRM ni se envía el email de aviso; sus datos solo quedan en el registro del servicio. Una solicitud de reserva se crea igualmente en Airflows. | Si se echa en falta un lead, avisar a Oimbra, que puede recuperarlo del registro. |
| El cliente repite la solicitud en la web | No se crea una segunda solicitud idéntica. | Ninguna. |
| El cliente quiere unas fechas o tipología que la web no ofrece | La web solo ofrece lo que está libre. | Registrar la solicitud a mano y proponer alternativas. |
| Un marketplace reserva un recurso ya ocupado | El calendario iCal puede tardar en actualizarse en el marketplace. | Al registrar la reserva, el sistema detecta el solape; buscar otro recurso o cancelar con el marketplace. |

## 2.6 Fuentes

| Tema | Dónde está |
|---|---|
| Formularios y envío a Pipedrive | Servicio de integración |
| Asistente de reserva web | Servicio de integración |
| Membership fee, promoción y email de solicitud | Reglas de la base de datos de las reservas |
| Calendario iCal | Servicio de integración |
| Reservas de marketplace | Reglas de la base de datos de las reservas y de la facturación |
| Contenidos y publicación de las webs | Webs comerciales |

## 2.7 Pendiente de confirmar

| Tema | Quién o qué lo confirma |
|---|---|
| — | — |
