# IT-3. Servicio de integración (API)

> Manual técnico · Borrador v0.1 · 2026-10-20 · Las marcas **[PREGUNTA Tn]** se resuelven en la ronda de preguntas y desaparecen de la versión final.

## 3.1 Propósito

Este capítulo describe el servicio de integración: la API REST propia que da servicio a las webs, al proceso de reserva, al portal del residente, al backoffice complementario, a Airflows y a los sistemas externos. Explica cómo está construido, qué rutas ofrece, quién las usa y qué hace cada una, con detalle en los flujos críticos: la reserva web, el pago con tarjeta y la integración contable.

## 3.2 Construcción

| Aspecto | Descripción |
|---|---|
| Tecnología | Python 3.12 con Flask, servido por gunicorn con 5 procesos (tiempo máximo por petición: 240 s), en el contenedor `back` del servidor de servicios. |
| Código | Repositorio `back`, carpeta `app/`: `main.py` (registro de rutas), `library/api/` (controladores), `library/business/` (lógica y consultas), `library/services/` (clientes de Airflows, base de datos, Redsys, Pipedrive, correo). |
| Prefijo | `/api/v1`, salvo el asistente de reserva (`/booking`) y sus recursos estáticos (`/assets`). |
| Documentación | Swagger en `https://back.cotown.com/api/apidocs/` (especificación en `/api/cotown_api_spec.json`). Hoy solo están documentadas las rutas de integración contable. |
| Acceso a datos | Dos vías hacia Airflows: **GraphQL** con un usuario de servicio, para lecturas puntuales y para subir o descargar documentos, y **SQL directo** a la base de datos por un túnel SSH, para consultas masivas (dashboards, informes, datos de las webs). Cada proceso mantiene un cliente GraphQL y un pequeño grupo de conexiones a la base de datos. |
| Configuración | Ficheros de configuración por entorno (Dynaconf), seleccionados con la variable `COTOWN_ENV`. |
| Errores | Los errores de negocio que lanzan los triggers de Airflows llegan con el formato `!!!mensaje en inglés!!!mensaje en español!!!` y se muestran al usuario en su idioma. |
| Registro | Cada petición se registra en la salida del contenedor, que recoge Loki (ver *Infraestructura y monitorización*). |

### Autenticación

| Tipo de ruta | Mecanismo |
|---|---|
| **Públicas** | Webs, asistente de reserva, disponibilidad, textos legales, notificaciones de Redsys y DocuSign, comprobación de servicio. No requieren credenciales. |
| **Internas** | Backoffice, portal del residente y botones de Airflows. Reciben el token de Airflows del usuario en el parámetro `access_token` de la URL. |
| **Integración contable** | Cabecera `Api-Key` con una clave por consumidor, que además limita qué emisores puede ver. |
| **Notificaciones de pago** | Firma criptográfica de Redsys, verificada en cada notificación. |

## 3.3 Rutas por función

### Datos para las webs comerciales

Las usa el generador de las webs al construirlas (cada 2 horas) y, en el caso de la disponibilidad, el navegador del visitante.

| Ruta | Qué devuelve |
|---|---|
| `GET /flats/<marca>/<año>` | Precios de pisos completos por edificio y subtipo, con promociones, para el año académico indicado y el siguiente. |
| `GET /rooms/<marca>/<año>` | Precios de habitaciones por edificio, tipo de plaza y tipo de piso. |
| `GET /amenities/<marca>` | Características por edificio y tipología. |
| `GET /typologies/<marca>` | Ciudades, modalidades (plaza, piso, residencia) y tipos de habitación disponibles. |
| `GET /promo/<marca>` | Promociones vigentes por edificio y tipología. |
| `GET /locked` | Recursos con bloqueos de más de 5 años, que no se publican. |
| `GET /availability/<tipo>/<filtro>` | Disponibilidad entre dos fechas: de todos los edificios, de las habitaciones de un edificio o de sus pisos. La consulta el navegador. |
| `GET /legal/<modalidad>/<marca>/<edificio>.pdf` | Ficha legal del edificio en PDF (pisos y plazas, régimen de renta, certificados, disponibilidad). |
| `POST /form` | Formularios de contacto y visita. Crea persona, lead y oportunidad en Pipedrive y envía un aviso por email al equipo comercial. Incluye protección básica contra robots (campo trampa y tiempo mínimo de cumplimentación). |

La marca es 1 para Vanguard y 2 para Cotown.

### Asistente de reserva web

`/booking/<paso>`, servido por el propio servicio con plantillas en español e inglés (`app/booking/es`, `app/booking/en`). La web comercial enlaza directamente con el paso 2, pasando ciudad, modalidad, tipo de habitación y fechas. El estado se conserva en la sesión del navegador.

| Paso | Qué ocurre |
|---|---|
| **2. Resultados** | Busca los recursos libres en las fechas (sin solapes en la tabla de ocupación), filtrados por ciudad, marca y modalidad. Calcula el precio mensual según la duración (corta: menos de 3 meses; media: de 3 a 6; larga: 7 o más) y la tarifa del recurso, y agrupa los resultados por edificio y tipología, ordenados por precio. |
| **3. Resumen y datos** | Muestra el desglose: renta del primer y último mes (prorrateada según la forma de facturación), servicios, garantía, membership fee, limpieza final, desglose mensual y mejor promoción aplicable. El visitante inicia sesión o se registra, e indica el motivo de estancia (con escuela o empresa según el motivo). En Barcelona, para Cotown, solo se admite la estancia vacacional con declaración de estancia recreativa. Si el visitante es menor de edad se piden los datos del tutor. |
| **4. Confirmación** | Crea la reserva en Airflows en estado *solicitud*, por el canal web, con la promoción aplicada, tras comprobar que no existe ya una igual. Envía el lead a Pipedrive (con los parámetros de campaña) y muestra el número de solicitud. |

El registro crea el cliente directamente en la base de datos; Airflows crea su usuario de acceso por trigger. Al crearse la reserva, los triggers de Airflows calculan precios y crean el cobro del membership fee. El pago no se hace en el asistente: el cliente paga después desde el portal del residente.

El paso 1 (selección de tipología) existe pero no se usa: la búsqueda se hace en la web comercial.

### Pagos con tarjeta (Redsys)

| Ruta | Quién la usa | Qué hace |
|---|---|---|
| `GET /pay/<cobro>` | Portal del residente | Prepara el pago: genera el número de pedido, elige el terminal y devuelve los parámetros firmados para el formulario de Redsys. Exige que el cliente tenga completos sus datos fiscales. |
| `POST /notify/<terminal>` | Redsys | Recibe el resultado del pago y, si es correcto, marca el cobro como pagado. |

**Flujo:**

1. El residente pulsa *Pagar* en el portal, que llama a `/pay/<cobro>`.
2. El servicio genera un número de pedido de 12 dígitos (año, identificador del cobro y un número de secuencia) y lo guarda en el cobro.
3. El **terminal** sale del propio cobro: *cotown* para el membership fee, el del propietario para rentas y garantías, *vandor* para los contratos LAU y *delegado* cuando un mismo cobro reúne renta y servicios de emisores con terminales distintos (ver glosario).
4. El servicio firma los parámetros con la clave del terminal (HMAC-SHA256, estándar de Redsys) y el portal envía el formulario a Redsys, donde el residente paga.
5. Redsys notifica el resultado a `/notify/<terminal>`. El servicio verifica la firma; si el pago está autorizado, guarda el código de autorización y la fecha de pago. Si el cobro ya estaba pagado, no hace nada (la notificación se puede recibir más de una vez sin efecto).
6. Al registrarse el pago, los triggers de Airflows hacen el resto: avanzan el estado de la reserva y, en el siguiente ciclo de facturación, se emite la factura o el recibo.
7. Redsys devuelve al residente a la página de pago correcto o fallido del portal.

### Contratos y documentos

| Ruta | Qué hace |
|---|---|
| `POST /contract` | Notificación de DocuSign: actualiza el estado del contrato de la reserva B2C (enviado, entregado, firmado, rechazado, caducado, anulado). Los contratos de grupo y los anexos se actualizan con la comprobación diaria (ver *Procesos automáticos*). |
| `GET /signature/<contacto>` | Imagen de la firma del representante del propietario, que se incrusta en contratos, anexos y certificados. |
| `GET /cert/<reserva>` | Certificado de residencia en PDF. |

### Backoffice complementario

Rutas que alimentan las pantallas de *Planning*, *Dashboards* e *Informes*.

| Ruta | Qué devuelve |
|---|---|
| `GET /dashboard` y `/dashboard/<situación>` | Operaciones: contadores y listas de reservas por situación (próximas entradas y salidas, check-in, check-out, revisión, incidencias, salidas anticipadas y extensiones…), con filtros por fechas, edificio, ubicación y B2C/B2B. |
| `GET /dashboard/prevnext` | Reserva anterior y siguiente del mismo recurso. |
| `GET /dashboard/payments`, `/deposits`, `/incasol` | Administración: cobros pendientes, garantías por devolver y fianzas INCASÒL pendientes, reclamadas o por devolver. |
| `GET /dashboard/documents/<situación>` | Documentación de clientes pendiente de subir o de aprobar. |
| `GET /dashboardlau/<tipo>` | Contratos LAU: devoluciones de fianza, ITP y finalizaciones. |
| `POST /availability` | Recursos libres entre fechas, para el planning. |
| `GET /labels/<lista>/<idioma>` | Etiquetas traducidas de las listas de valores de Airflows. |
| `GET /report/<situación>` | Excel de un dashboard. |
| `GET /export/<informe>` | Informes Excel (ver *Procesos automáticos, emails y documentos*). |
| `GET /download/<tipo>` | Descargas masivas en ZIP: facturas y recibos, contratos, ficheros del registro NRUA y formularios de devolución de fianza del INCASÒL. |

### Airflows y portal del residente

| Ruta | Qué hace |
|---|---|
| `GET /booking/<reserva>/status/<estado>` | Cambia el estado de una reserva. Es la acción de los botones de la ficha de reserva en Airflows (*Enviar alternativas*, *Descartar*, *Reactivar*, *Check-in OK*, *Check-out OK*); sus URL las generan los triggers. Los triggers de Airflows hacen el resto (cobros, emails). |
| `POST /questionnaire/<cuestionario>` | Guarda las respuestas de un cuestionario de check-in o check-out del portal y copia las incidencias declaradas a la reserva. |
| `GET /iban/<código>`, `/swift/<código>` | Validan IBAN y BIC en los formularios del portal. |

### Integración contable (SAP y propietarios)

SAP consulta estas rutas para incorporar a la contabilidad lo que genera el sistema. Algunos propietarios tienen también su propia clave, limitada a sus facturas y clientes, para descargarlos desde sus sistemas. Todas devuelven JSON; las fechas de entrada van en formato `AAAA-MM-DD` y las de salida en `DD/MM/AAAA`.

| Ruta | Parámetro | Qué devuelve |
|---|---|---|
| `GET /integration/customers` | `date`: desde | Clientes creados o modificados desde la fecha que tienen reservas activas B2C, B2B (pagadores) o contratos LAU, locales o parking: identificación, dirección, datos de facturación y bancarios (con banco y BIC deducidos del IBAN). |
| `GET /integration/invoices` | `date`: desde | Facturas, recibos y rectificativas emitidas desde la fecha por emisores con código SAP, con sus líneas: producto (código SAP), proyecto (código SAP del emisor y del recurso), importe e impuesto. Tipo de documento según emisor y producto (garantía, rectificativa, factura). |
| `GET /integration/payments` | `date`: día | Cobros de ese día con las facturas que liquidan y la cuenta de cobro (la del terminal, para tarjeta, o la del medio de pago). |
| `GET /integration/managementfees` | `month`: `AAAA-MM` | Management fees del mes por propietario y edificio: importe bruto, neto y comisión. |

Cada clave de acceso (`Api-Key`) tiene asociado el rango de emisores que puede consultar. La clave de SAP tiene acceso completo; las de los propietarios solo ven sus facturas y sus clientes. Los cobros y los management fees solo están disponibles con acceso completo.

### Marketplaces

| Ruta | Qué devuelve |
|---|---|
| `GET /ical/<token>` | Calendario iCal de las reservas futuras de un recurso. A partir del viernes a las 10:00 marca también como ocupados los días libres del fin de semana en curso, para evitar reservas de última hora. La URL de cada recurso la genera Airflows y se guarda en el propio recurso. |

## 3.4 Inventario de rutas

Todas las rutas en uso, con quién las llama y cómo se autentican. Salvo que se indique otra cosa, llevan el prefijo `/api/v1`. **Autenticación**: *ninguna* (ruta pública), *token* (token de Airflows en el parámetro `access_token` de la URL; ninguna ruta usa la cabecera `Authorization`), *Api-Key* (cabecera con la clave del consumidor) o *firma* (firma de Redsys).

| Método y ruta | Autenticación | Quién la llama | Para qué |
|---|---|---|---|
| GET `/flats/<marca>/<año>` | Token | Generador de las webs (`webs/code/src/data/flats.js`), al construirlas | Precios de pisos completos |
| GET `/rooms/<marca>/<año>` | Token | Generador de las webs (`data/rooms.js`) | Precios de habitaciones |
| GET `/amenities/<marca>` | Token | Generador de las webs (`data/amenities.js`) | Características por edificio y tipología |
| GET `/typologies/<marca>` | Token | Generador de las webs (`data/typologies.js`) | Ciudades, modalidades y tipos de habitación |
| GET `/promo/<marca>` | Token | Generador de las webs (`data/promos.js`) | Promociones vigentes |
| GET `/locked` | Token | Generador de las webs (`data/unlocked.js`) | Recursos con bloqueos de más de 5 años |
| GET `/availability/<tipo>/<filtro>` | Ninguna | Navegador del visitante, en las páginas de ciudad, edificio y residencia (`includes/shared/sections/common/availability.html.njk`) | Disponibilidad en vivo |
| GET `/legal/<modalidad>/<marca>/<edificio>.pdf` | Ninguna | Enlaces de las páginas de edificio de las webs | Ficha legal del edificio |
| POST `/form` | Token | Formularios de las webs (`includes/shared/js/pipedrive.js`) | Lead a Pipedrive y aviso al equipo comercial |
| GET, POST `/booking/<paso>` (sin prefijo) | Ninguna | Botón *Reservar* de las webs y navegación del propio asistente | Asistente de reserva |
| GET `/pay/<cobro>` | Token | Portal del residente (*Pagos*) | Formulario firmado de pago en Redsys |
| POST `/notify/<terminal>` | Firma | Redsys (URL de notificación configurada en cada pago) | Registrar el resultado del pago |
| GET `/iban/<código>`, `/swift/<código>` | Token | Portal del residente (*Mis datos*) | Validar IBAN y BIC |
| GET `/cert/<reserva>` | Token | Portal del residente (*Reservas*) | Certificado de residencia en PDF |
| POST `/questionnaire/<cuestionario>` | Token | Portal del residente (*Cuestionarios*) | Guardar respuestas e incidencias |
| GET `/booking/<reserva>/status/<estado>` | Token | Botones de la ficha de reserva en Airflows (URL generadas por los triggers) y portal del residente (anular solicitud) | Cambiar el estado de una reserva |
| GET `/signature/<contacto>` | Token | Generador de PDF (WeasyPrint), desde las plantillas de contratos, anexos y certificados | Firma del apoderado del propietario |
| POST `/contract` | Ninguna | DocuSign Connect | Estado del contrato B2C |
| GET `/ical/<token>` | Token de la propia ruta | Marketplaces (URL guardada en cada recurso) | Calendario de ocupación del recurso |
| GET `/integration/customers`, `/invoices`, `/payments`, `/managementfees` | Api-Key | SAP Business ByDesign y propietarios con clave | Integración contable |
| GET `/dashboard`, `/dashboard/<situación>` | Token | Backoffice: dashboard general y de operaciones | Contadores y listas de reservas |
| GET `/dashboard/prevnext` | Token | Backoffice: dashboard de operaciones | Reserva anterior y siguiente del recurso |
| GET `/dashboard/payments`, `/deposits`, `/incasol` | Token | Backoffice: dashboard de administración | Cobros pendientes, garantías, fianzas INCASÒL |
| GET `/dashboard/documents/<situación>` | Token | Backoffice: dashboard de documentos | Documentación pendiente |
| GET `/dashboardlau/<tipo>` | Token | Backoffice: dashboard LAU | Seguimiento de contratos LAU |
| GET `/labels/<lista>/<idioma>` | Token | Backoffice: dashboards y planning | Etiquetas traducidas de las listas de valores |
| POST `/availability` | Token | Backoffice: planning | Recursos libres entre fechas |
| GET `/report/<situación>` | Token | Backoffice: dashboards de operaciones, documentos y administración | Excel de un dashboard |
| GET `/export/<informe>` | Token | Backoffice: informes y dashboard general | Informes Excel |
| GET `/download/<tipo>` | Token | Backoffice: informes | Descargas masivas en ZIP |

## 3.5 Fuentes

| Tema | Dónde está |
|---|---|
| Registro de rutas | `back/app/main.py` |
| Controladores | `back/app/library/api/` |
| Consultas y lógica | `back/app/library/business/` (`queries.py`, `booking.py`, `integration.py`, `download.py`, `export.py`) |
| Redsys | `back/app/library/services/redsys.py`, `back/app/library/api/payment.py` |
| Asistente de reserva | `back/app/booking/` (plantillas) y `back/app/library/api/booking.py` |
| Especificación de la API | `https://back.cotown.com/api/apidocs/` |

## 3.6 Pendiente de confirmar

No hay puntos pendientes.
