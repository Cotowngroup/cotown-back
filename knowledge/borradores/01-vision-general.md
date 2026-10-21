# 1. Visión general y glosario

> Capítulo común a los dos volúmenes (Manual funcional y Manual técnico).
> Borrador v0.1 · 2026-10-19 · Las marcas **[PREGUNTA Pn]** se resuelven en la ronda de preguntas y desaparecen de la versión final.

## 1.1 Propósito

Este capítulo da una imagen de conjunto del sistema de gestión de Cotown: a qué negocio sirve, de qué piezas se compone, quién lo usa y cómo fluye una reserva desde que alguien visita la web hasta que se le devuelve la garantía. También fija el vocabulario que se usa en el resto de capítulos.

No describe pantallas ni procedimientos paso a paso. Cada tema se desarrolla en su propio capítulo; aquí solo se presenta y se remite a él.

## 1.2 El negocio

Cotown es un operador de alojamiento flexible en España: residencias de estudiantes y coliving para jóvenes profesionales. Alquila **habitaciones, plazas en habitación compartida y pisos completos**, por estancias de meses.

Opera con dos marcas, que en el sistema se llaman **segmentos**:

| Marca | Público | Web |
|---|---|---|
| **Vanguard Student Housing** | Estudiantes | vanguard-student-housing.com |
| **Cotown** | Jóvenes profesionales | cotown.com |

Además existe **cotowngroup.com**, la web corporativa, que aloja el portal del residente.

Cotown gestiona inmuebles que en gran parte **no son suyos**: cada piso tiene un **propietario** (que es quien alquila y factura la renta) y, en su caso, un **prestador de servicios** (que factura los servicios). Cotown cobra el *membership fee* de cada reserva y una **comisión de gestión** (*management fee*) sobre lo que facturan los propietarios.

Hay tres modalidades de contratación:

- **B2C – reserva individual**: una persona reserva una plaza, una habitación o un piso.
- **B2B – reserva de grupo**: una empresa o institución reserva un bloque de plazas para varias personas y paga ella.
- **Reservas LAU y otros**: por un lado, contratos de arrendamiento clásicos (LAU) con los inquilinos que ya ocupaban pisos adquiridos por **Vandor Real Estate**, sociedad del grupo; a medida que esos contratos terminan, los pisos se reforman (pre-capex y capex) y pasan a la oferta de coliving. Por otro, el alquiler de activos que no son vivienda: locales comerciales (retail), plazas de parking y coworking.

El sistema tiene definidas cinco ubicaciones: **Barcelona, Madrid, Valencia, Bilbao y Lisboa**. Hoy hay actividad en las cuatro primeras (en octubre de 2026, 22 edificios activos en Barcelona, 4 en Valencia, 3 en Madrid y 1 en Bilbao); Lisboa está definida, pero sin edificios. Barcelona concentra las reglas específicas: depósito de la fianza en el INCASÒL, anexos de contrato y limitación de rentas de la Ley de vivienda. La limitación de rentas se aplica también en Bilbao.

## 1.3 Mapa del sistema

![Arquitectura del sistema](../diagramas/Arquitectura%20Cotown%20v2.png)

El sistema se compone de una plataforma central y de varias piezas construidas a su alrededor.

### Plataforma central: Airflows

**Airflows** es una plataforma de gestión de datos *low-code*. Contiene la base de datos con toda la información del negocio (edificios, recursos, clientes, reservas, facturas, cobros…) y es la **aplicación principal del personal de Cotown**: desde ella se consultan y editan los datos.

Buena parte de las reglas de negocio se ejecutan **dentro de la base de datos**, como *triggers*: cada vez que alguien crea o modifica una reserva, un cobro o un documento, la base de datos valida los datos, calcula precios, cambia el estado de la reserva y programa los emails que correspondan. Otros procesos de la base de datos se ejecutan de forma programada: la mayoría cada 15 minutos (avance de estados por fecha, recordatorios por email, facturación de limpiezas de grupos), los avisos de llegada de compañeros a diario a las 10:00 (hora UTC, como todos los procesos de la base de datos), el histórico y el estado de los recursos cada hora, y la actualización por IPC y la revisión de inquilinos de edad avanzada una vez al mes. Su calendario se define en Airflows y lo ejecuta el programador de tareas de la propia base de datos (pg_cron).

Airflows está alojada en **Hetzner** (`core.cotown.com`) y es el ERP de gestión de Cotown. Sus menús, en el orden en que aparecen, son:

| Menú | Contenido principal |
|---|---|
| **Propietarios** | Propietarios y prestadores de servicios, sus contactos, documentos y plantillas de contrato; marketplaces. |
| **Clientes** | Clientes, contactos, documentos y emails enviados. |
| **Ubicaciones** | Países, provincias, localidades, barrios y oficinas de Cotown. |
| **Edificios** | Edificios, sus servicios, transportes, documentos y valoraciones. |
| **Activos** | Pisos, habitaciones, plazas y demás recursos; tipologías, características, inventario, disponibilidad y valoraciones. |
| **Reservas** | Reservas B2C, reservas B2B, reservas LAU y otros, y sus catálogos (canales, motivos, cuestionarios, servicios de check-in/check-out…). Incluye el **Planning**. |
| **Dashboards** | Dashboards General, Operaciones, LAU, Administración y Documentos. |
| **Facturación** | Facturas, cobros, tarifas, precios base, promociones, productos, impuestos y medios de pago. |
| **Marketing** | Contenidos de las webs: imágenes, textos, blog, preguntas frecuentes, socios, testimonios, equipo, banners y redes sociales. |
| **Auxiliares** | Catálogos generales: marcas, escuelas, tipos de identificación, festivos, horarios, IPC… |
| **Procesos** | Cargas de datos desde Excel e **Informes**. |
| **Administración** | Usuarios y roles del personal, plantillas de email, parámetros, ficheros y notificaciones. |

El Planning, los Dashboards y los Informes son las pantallas del backoffice complementario, que se abren desde estos menús.

### Piezas alrededor de Airflows

El resto de piezas propias están alojadas en **Azure**. El **servidor de servicios** (`back.cotown.com`) ejecuta los procesos automáticos y sirve las webs, el proceso de reserva, el portal del residente, los pagos con Redsys y las funciones que Airflows usa en línea. El data warehouse está en un servidor aparte (`data.cotown.com`).

| Pieza | Para qué sirve | Quién la usa |
|---|---|---|
| **Webs públicas** (Cotown y Vanguard) | Escaparate comercial: ubicaciones, edificios, pisos y habitaciones, precios, disponibilidad, blog, formularios de contacto. Se regeneran automáticamente cada 2 horas con los datos de Airflows. | Público |
| **Proceso de reserva web** | Asistente de 4 pasos (búsqueda, resumen, registro, reserva) que crea la solicitud en Airflows. | Público |
| **Portal del residente** | Área privada: datos personales, documentos, reservas, check-in, alternativas, cuestionarios, facturas y pagos con tarjeta. | Residentes |
| **Backoffice complementario** | Pantallas que Airflows no ofrece: dashboards de operaciones, documentación, administración y LAU; planning de ocupación; informes Excel. Se abren desde dentro de Airflows. | Personal de Cotown |
| **Servicio de integración y procesos automáticos** | API que da servicio a las webs, al portal y al backoffice, y procesos que se ejecutan cada 15 minutos: facturación, generación de PDFs de facturas y contratos, envío a firma, carga de ficheros Excel y envío de emails. | Sistemas |
| **Data warehouse** | Copia analítica de los datos (ocupación, ingresos, forecast, contabilidad) que alimenta toda la analítica de datos de la compañía. | Dirección, operaciones, finanzas y booking |

## 1.4 Sistemas externos

Inventario de todos los sistemas de terceros con los que el sistema se relaciona. **Integración** indica cómo: *API* (intercambio automático de datos), *widget* (componente de terceros incrustado en una página), *enlace* (solo un enlace o un email), *fichero* (intercambio manual de ficheros) o *ninguna* (se usa fuera del sistema).

### Negocio

| Sistema | Para qué | Integración | Sentido |
|---|---|---|---|
| **Airflows** | Plataforma central: base de datos, aplicación del personal, inicio de sesión (Keycloak) y programación de procesos. | — | — |
| **SAP Business ByDesign** | Contabilidad. | API | SAP obtiene del sistema clientes, facturas, cobros y management fees. (El data warehouse tiene preparada la lectura del libro mayor de SAP, pero está desactivada.) |
| **Pipedrive** | CRM comercial. | API | El sistema envía como leads los formularios web, las conversaciones del chatbot y las solicitudes de reserva. |
| **Redsys** | Pago con tarjeta (membership fee, garantía, mensualidades, check-in). Cuatro terminales: Cotown, Vandor, delegado y por defecto. | API | El sistema envía el pago; Redsys notifica el resultado. |
| **DocuSign** | Firma electrónica de contratos y anexos. | API | El sistema envía los contratos; DocuSign notifica cuándo se firman. |
| **Microsoft 365 – correo** | Envío de los emails automáticos, desde dos remitentes: Cotown y Vandor. | API (SMTP) | Salida. |
| **Microsoft 365 – SharePoint** | Archivo de facturas y recibos en PDF por proveedor, año, mes y edificio. | API | Copia automática diaria. |
| **INCASÒL** | Depósito de las fianzas legales en Cataluña. | Fichero | El sistema calcula las fianzas y prepara el informe y los formularios; se presentan a mano. |
| **Trustpilot** | Reseñas de clientes. | Enlace | Email de invitación 30 días antes de la salida. |
| **Power BI** | Analítica de dirección, operaciones, finanzas y booking. | API | Lee del data warehouse. |
| **Marketplaces (Airbnb y otros)** | Intermediarios que traen reservas a cambio de una comisión. | API (iCal) | Consultan la disponibilidad en una URL de calendario por recurso. Sus reservas se registran a mano, indicando el marketplace. |

### Webs y marketing

Servicios de terceros incrustados o enlazados en las webs. Se gestionan fuera del sistema y aquí solo se enumeran.

| Sistema | Para qué | Integración |
|---|---|---|
| **Chatbot web** | Asistente conversacional en las dos webs. | Widget |
| **Google Tag Manager** | Etiquetas de analítica y marketing. | Widget |
| **Trustindex** | Reseñas en las webs. | Widget |
| **OpenStreetMap** | Mapas. | Widget |
| **Google Fonts** | Tipografías. | Widget |
| **WhatsApp** | Contacto directo. | Enlace |
| **Redes sociales** (Instagram, Facebook, TikTok, LinkedIn) | Perfiles de las marcas. | Enlace |

### Infraestructura

| Sistema | Para qué |
|---|---|
| **Hetzner** | Alojamiento de Airflows. |
| **Microsoft Azure** | Alojamiento del servicio de integración, los procesos automáticos, las webs y el data warehouse. |
| **Let's Encrypt** | Certificados de seguridad (HTTPS) de los dominios, renovados automáticamente cada semana. |
| **GitHub** | Repositorios del código fuente, en la organización `Cotowngroup`. |
| **Docker Hub** | Origen de las imágenes base de los contenedores (servidor web, monitorización, Python). |

### Fuera de uso

| Sistema | Situación |
|---|---|
| **ActiveCampaign** | Antiguo CRM de marketing de Vanguard, sustituido por Pipedrive. La integración ya no se usa. |

## 1.5 Actores

| Actor | Quién es | Cómo usa el sistema |
|---|---|---|
| **Personal de Cotown** | Equipos de reservas, operaciones, administración… | Airflows y el backoffice complementario. Tiene un rol base y roles adicionales según su función, que se gestionan en *Administración › Roles*: administración del sistema (*administrators*), reservas (*bookings*), marketing, operaciones (*operations*), facturación (*billing*), Vandor (*vandor*) y usuarios externos (*external*). |
| **Cliente / residente** | Persona que reserva y se aloja (B2C). Si es menor, tiene un tutor. | Web de reserva y portal del residente. Recibe los emails automáticos. |
| **Cliente empresa / pagador** | Empresa o institución que paga una reserva de grupo (B2B). | No usa el portal; recibe las facturas por email. No recibe emails automáticos de reserva. |
| **Residente de grupo** | Persona alojada dentro de una reserva de grupo. | Figura en la *rooming list*; no es cliente del sistema. |
| **Propietario** | Dueño de los pisos. Arrendador en el contrato; emite la factura o recibo de renta y el recibo de la garantía. | Acceso de consulta a Airflows con un rol restringido, incluidos los informes habilitados para proveedores. |
| **Prestador de servicios** | Empresa que factura los servicios del piso. | Como el propietario. |
| **Marketplace** | Intermediario que trae reservas a cambio de una comisión. Puede cobrar él el membership fee. | No usa el sistema; consulta la disponibilidad por iCal y se registra como dato de la reserva. |

## 1.6 El recorrido de una reserva

![Ciclo de vida de la reserva B2C](../diagramas/Ciclo%20reserva%20B2C%20v2.png)

Resumen del recorrido de una reserva individual (B2C). Cada fase se desarrolla en su capítulo. En la tabla, **A** = lo hace el sistema solo, **M** = lo hace una persona.

| Fase | Qué ocurre | A / M |
|---|---|---|
| **Captación** | El interesado visita la web, consulta disponibilidad o rellena un formulario. El formulario llega a Pipedrive como lead. | A |
| **Solicitud** | El interesado reserva desde la web (o el personal la registra a mano). Se crea la solicitud, sin recurso concreto todavía, y el cobro del membership fee. El cliente recibe un email. | A / M |
| **Asignación o alternativas** | El personal asigna un recurso concreto o propone alternativas (otro edificio u otra tipología), que el cliente acepta desde el portal. | M |
| **Pago del membership fee** | El cliente paga con tarjeta; la reserva queda **confirmada**. Si no paga en el plazo (2 días), **caduca**. | A |
| **Documentación** | El cliente sube su documentación al portal (plazo de 14 días); el personal la aprueba. | M |
| **Garantía** | Al aprobarse la documentación se emite el cobro de la garantía, a nombre del propietario. En Barcelona incluye la parte que se deposita en el INCASÒL. Si no se paga a tiempo, la reserva se descarta. | A |
| **Contrato** | El sistema genera el contrato y lo envía a firmar por DocuSign. Al firmarse, la reserva avanza sola. | A |
| **Check-in** | El residente indica fecha y hora de llegada. Llegada la fecha, la reserva pasa a check-in; el personal confirma la entrada y el residente queda **in house**. | A / M |
| **Estancia** | Cada mes se emiten automáticamente las facturas de renta (del propietario) y servicios (del prestador), y el cobro correspondiente. Cambios de fecha de salida (salida anticipada o extensión) y de habitación se gestionan a mano. | A / M |
| **Salida** | Antes de la salida se envían la invitación a Trustpilot y el aviso de check-out con cuestionario. Llegada la fecha, la reserva pasa a check-out; el personal revisa el estado del alojamiento. | A / M |
| **Devolución de la garantía** | El personal registra la devolución (o la retención) de la garantía y la reserva queda **finalizada**. | M |

A lo largo de todo el recorrido el sistema envía **emails automáticos** al cliente en cada cambio de estado y recordatorios periódicos (documentación, garantía, firma, check-in, pagos pendientes).

Las **reservas de grupo** siguen un recorrido más corto: se bloquean las plazas, el personal las confirma (y en ese momento se facturan el membership fee y la garantía por plaza), y la estancia, la salida y la devolución de la garantía funcionan de forma similar pero por grupo, con una *rooming list* para los residentes.

Los **contratos de larga duración** no tienen recorrido de reserva: se facturan mensualmente, se actualizan por IPC una vez al año y, al terminar, bloquean el piso para obras.

## 1.7 Glosario

Los términos en `monoespaciado` son el nombre que tiene el concepto en el sistema, para quien necesite localizarlo en Airflows.

### Inventario

| Término | Definición |
|---|---|
| **Ubicación** | Ciudad en la que Cotown tiene presencia. Contiene barrios. |
| **Barrio** | Zona dentro de una ubicación. Cada edificio pertenece a un barrio. |
| **Edificio** (`Building`) | Dirección postal que contiene uno o varios pisos. Se identifica con un código de 6 caracteres y tiene un tipo (por ejemplo, residencia) que determina el IVA y la plantilla de contrato. |
| **Recurso / activo** (`Resource`) | Cualquier unidad alquilable. En el menú del ERP se llaman *Activos*. Los de vivienda son pisos, habitaciones y plazas; además hay zonas comunes, locales, parkings, trasteros y salas. Pisos, habitaciones y plazas forman una jerarquía y comparten código (piso `BCN001.01.02`, habitación `….H01`, plaza `….H01.P1`); al ocupar uno se bloquean también sus padres e hijos. |
| **Piso** | Vivienda completa. Se define a nivel de piso el propietario, el prestador de servicios, la modalidad de venta, la marca y la forma de facturar; sus habitaciones y plazas lo heredan. |
| **Habitación** | Habitación de un piso, de uso individual o compartido. |
| **Plaza** | Cama dentro de una habitación compartida. |
| **Tipología** | Clasificación comercial. Hay tipología de piso y tipología de plaza; el cliente reserva una tipología en un edificio, no un recurso concreto. |
| **Modalidad de venta** (`Sale_type`) | Si el piso se alquila completo, por habitaciones/plazas, o de ambas formas. |
| **Segmento / marca** | Vanguard o Cotown. Se asigna al piso; determina en qué web aparece y desde qué marca se envían los emails. |
| **Amenity** | Característica del recurso (baño propio, terraza…) que puede incrementar la renta en un porcentaje. |
| **Disponibilidad / bloqueo** | Periodos en que un recurso no se puede reservar: por reserva, por contrato de larga duración, por obras (pre-capex, capex) u otros motivos. |
| **Régimen de renta** (`Limit_type`) | Si la renta del recurso es **libre** o está **limitada** por la Ley de vivienda (por un contrato LAU anterior o por el índice de referencia). En régimen limitado la renta máxima la fija el sistema. |
| **Inventario** | Mobiliario y enseres de cada recurso, por tipo y zona. |

### Personas y empresas

| Término | Definición |
|---|---|
| **Cliente** (`Customer`) | Persona o empresa que contrata. En B2C es el residente; en B2B es el pagador. El idioma del cliente (español o inglés) decide el de emails y contratos. |
| **Tutor** | Responsable de un cliente menor de edad. |
| **Lista negra** | Marca sobre un cliente que impide que sus reservas avancen, salvo autorización expresa. |
| **Proveedor** (`Provider`) | Propietario o prestador de servicios. Cada uno tiene su propia numeración de facturas, su plantilla de contrato y su terminal de pago. Cotown es también un proveedor (el que factura el membership fee y los servicios propios). |
| **Marketplace** (`Agent`) | Intermediario que trae reservas a cambio de comisión. |
| **Canal / referral** | Por dónde llegó la reserva y cómo nos conoció el cliente. |
| **Motivo de estancia** | Estudios, trabajo, estudios y trabajo, prácticas u ocio. Determina qué datos (escuela, empresa) y qué documentos se exigen. |
| **Lead** | Contacto comercial que llega desde un formulario web o una solicitud de reserva, y que se registra en Pipedrive. |

### Reservas

| Término | Definición |
|---|---|
| **Reserva** (`Booking`) | Reserva individual (B2C) de un cliente sobre un recurso, para un periodo. Distingue el **periodo contratado** (fechas desde/hasta) de las **fechas reales** de check-in y check-out. |
| **Solicitud** | Primera fase de la reserva: el cliente ha pedido un edificio y una tipología, pero todavía no tiene recurso asignado. |
| **Alternativa** (`Booking_option`) | Propuesta del personal cuando la solicitud no se puede atender tal cual: otro edificio, otra tipología u otras fechas. El cliente la acepta desde el portal. |
| **Estado de la reserva** | Fase en que se encuentra (solicitud, pendiente de pago, confirmada, contrato, in house, finalizada…). La lista completa y sus transiciones están en el capítulo *Ciclo de vida de la reserva*. |
| **Reserva de grupo** (`Booking_group`) | Reserva B2B de varias plazas para una empresa pagadora, con precio por plaza y mes. |
| **Rooming list** | Relación de residentes de una reserva de grupo, con la plaza y las fechas de cada uno. |
| **Reserva LAU y otros** (`Booking_other`) | Contratos que quedan fuera del modelo de reservas de coliving: arrendamientos de vivienda sujetos a la Ley de Arrendamientos Urbanos (LAU), locales comerciales, parkings y coworking. Se facturan mensualmente; los LAU se actualizan por IPC. |
| **Pre-capex / capex** | Periodos de bloqueo de un piso para obras, previos y posteriores a la reforma, que el sistema calcula al terminar un contrato de larga duración. |
| **ECO / EXT** | Salida anticipada (*early check-out*) o extensión de la estancia. Recalcula los precios de los meses pendientes. |
| **CHA** | Cambio de habitación: se crean dos reservas enlazadas, la de origen y la de destino. |
| **Check-in / check-out** | Entrada y salida reales del residente. Si el residente elige una opción de check-in o check-out (por franja horaria o día), se le cobra. |
| **Keyless** | Entrada sin entrega física de llaves. |
| **In house** | Estado de la reserva mientras el residente está alojado. |
| **Revisión** | Comprobación del estado del alojamiento tras la salida, previa a la devolución de la garantía. |
| **Cuestionario** | Encuesta de check-in o de check-out que el residente rellena en el portal; sus respuestas pueden abrir incidencias. |
| **Documentación** | Documentos que el cliente debe aportar (identidad, matrícula, contrato laboral…), según su tipo de identificación y su motivo de estancia. El personal los aprueba. |

### Precios, facturación y cobros

| Término | Definición |
|---|---|
| **Precio base** (`Pricing_detail`) | Precio de referencia por edificio, tipología de piso, tipología de plaza y año académico (septiembre a agosto). Distingue renta corta, media y larga según la duración, e incluye servicios, garantía, limpieza final, segundo residente y membership fee. |
| **Tarifa** (`Pricing_rate`) | Nivel de precio que se asigna a cada recurso y que se aplica sobre el precio base. |
| **Precio de la reserva** | Detalle mes a mes de lo que se factura en una reserva: renta, servicios y descuentos. Los meses incompletos se facturan completos, por quincena o de forma proporcional. |
| **Descuento** | Rebaja sobre la renta o los servicios de uno o varios meses, siempre con un motivo. |
| **Promoción** | Descuento temporal sobre la renta o el membership fee, para unos edificios o tipologías y unas fechas. La web aplica la promoción que mostró al cliente. |
| **Booking fee / membership fee** | Dos nombres para el mismo concepto: el importe que Cotown cobra al confirmar la reserva. Se devuelve si la reserva se descarta después de pagado. |
| **Garantía / fianza** | Dos nombres para el mismo concepto: el importe que el residente deposita como garantía. Se emite como **recibo a nombre del propietario**, se devuelve tras la salida y lo que se retiene se factura. |
| **Fianza legal (INCASÒL)** | Parte de la garantía que, en Barcelona, debe depositarse en el Institut Català del Sòl. Es el único caso en que "fianza" no equivale a "garantía". Su situación se sigue en el sistema: pendiente, depositada, reclamada o devuelta. |
| **Producto** | Concepto facturable (renta, servicios, garantía, check-in, limpieza, suministros…) con su IVA. |
| **Servicio adicional** | Concepto extra en una reserva: en la próxima factura, en una fecha concreta o recurrente. |
| **Limpieza final** | Limpieza de salida que se factura al residente (o al grupo, por piso). |
| **Factura / recibo / rectificativa** | Documentos de cobro. El propietario puede emitir recibo en lugar de factura. Una vez emitida no se modifica; se corrige con una rectificativa. |
| **Cobro** (`Payment`) | Importe que el cliente debe pagar: membership fee, garantía, mensualidad, check-in o check-out. Se paga con tarjeta (Redsys) o por otros medios que el personal registra a mano. |
| **TPV** | Terminal de pago de Redsys. Cada proveedor tiene asignado uno: Cotown usa el terminal *Cotown*, Vandor el terminal *Vandor* y el resto de propietarios y prestadores, el *delegado*. |
| **TPV delegado** | Terminal que se usa cuando un mismo cobro mensual reúne la renta de un propietario y los servicios de otro prestador con TPV distinto. También es el terminal por defecto, y sus cobros domiciliados forman la remesa SEPA por cuenta de terceros. |
| **Management fee** | Comisión de gestión de Cotown sobre lo que facturan los propietarios. Su porcentaje depende del recurso y de la frecuencia de limpieza contratada. |
| **IPC** | Índice de precios al consumo. Se usa para actualizar anualmente la renta de los contratos de larga duración y para calcular la renta máxima en régimen limitado. |
| **LAU** | Ley de Arrendamientos Urbanos. En el sistema da nombre a los contratos de larga duración, a uno de los regímenes de renta limitada y a una serie de facturas propia. |
| **Reserva limitada / recreativa** | Tipo de reserva obligatorio cuando el recurso tiene renta limitada: **limitada** aplica las rentas máximas; **recreativa** es una estancia vacacional. |

## 1.8 Fuentes

| Tema | Dónde está |
|---|---|
| Reglas de negocio (validaciones, estados, precios, emails) | `back/function/` (triggers de base de datos) |
| Servicio de integración y procesos automáticos | `back/app/` |
| Programación de los procesos automáticos | `back/config/pro/crontab` (procesos del servidor); los procesos de la base de datos, en Airflows (`Models.Function`), que los publica en el esquema `cron` |
| Modelo de datos (entidades, atributos, relaciones, estados, menús) | Metadatos de Airflows, esquema `Models` de la base de datos |
| Webs públicas | `webs/code/` |
| Portal del residente | `front/customer/` |
| Backoffice complementario | `front/cotown/` |
| Data warehouse | `back/etl/` |
| Plantillas de contrato | `back/app/contracts/` y la configuración de cada proveedor en Airflows |
| Diseño original (2023, referencia) | Documentación de diseño de Experis: requisitos, especificaciones y modelo de datos |

## 1.9 Pendiente de confirmar

| Tema | Quién o qué lo confirma |
|---|---|
| — | — |