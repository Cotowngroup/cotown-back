# IT-6. Aplicaciones web: backoffice complementario y portal del residente

> Manual técnico · Borrador v0.1 · 2026-10-20 · Las marcas **[PREGUNTA Tn]** se resuelven en la ronda de preguntas y desaparecen de la versión final.

## 6.1 Propósito

Este capítulo describe las dos aplicaciones web propias que completan Airflows: el **backoffice complementario**, que usa el personal de Cotown, y el **portal del residente**. Explica cómo están construidas, cómo se autentican, qué datos usan, dónde se despliegan y qué hace cada pantalla. El uso de cada pantalla en el día a día se describe en el manual funcional.

## 6.2 Rasgos comunes

| Aspecto | Descripción |
|---|---|
| Tecnología | Angular 15 con Angular Material y PureCSS. Navegación con almohadilla (`/#/ruta`). |
| Código | Repositorio `cotown-front`: `cotown/` (backoffice) y `customer/` (portal). |
| Datos | **GraphQL de Airflows** (Apollo) para leer y modificar registros, **API de ficheros de Airflows** para documentos y PDF, y el **servicio de integración** (`/api/v1`) para dashboards, disponibilidad, informes, pagos y certificados. |
| Idiomas | Español e inglés (ngx-translate). Las etiquetas de estados y tipos se leen de Airflows. Los errores de los triggers se muestran en el idioma del usuario. |
| Entornos | Fichero `environment.production.ts` (Airflows `core.cotown.com`, servicio `back.cotown.com`) y ficheros de desarrollo (Airflows `cotown-dev.flows.ninja`). |
| Construcción | `npm run build` genera la aplicación en `dist/<app>` con la configuración de producción. |
| Despliegue | Manual: se copia el contenido de `dist/<app>` al servidor correspondiente. No hay script de despliegue en el repositorio. |

## 6.3 Backoffice complementario

### Qué es y dónde se sirve

Siete pantallas que Airflows no ofrece. Se sirven desde el propio servidor de Airflows, en `https://core.cotown.com/cotown/`, de modo que comparten origen con el ERP. Se abren desde los menús de Airflows, que añaden a la URL el token del usuario:

| Menú de Airflows | Pantalla | Ruta |
|---|---|---|
| Reservas › Planning | Planning de ocupación | `/cotown/#/planning` |
| Dashboards › General | Embudo de reservas | `/cotown/#/dashboard` |
| Dashboards › Operaciones | Entradas, salidas, revisiones e incidencias | `/cotown/#/operations` |
| Dashboards › LAU | Contratos LAU y otros | `/cotown/#/lau` |
| Dashboards › Administración | Cobros, garantías y fianzas INCASÒL | `/cotown/#/admon` |
| Dashboards › Documentos | Documentación de clientes | `/cotown/#/documents` |
| Procesos › Informes | Informes Excel y descargas | `/cotown/#/reports` |

Además, el planning se usa como **selector** desde los formularios de Airflows: al elegir el recurso de una reserva B2C (selección única) o las plazas de una reserva de grupo (selección múltiple), Airflows abre el planning en una ventana emergente.

### Autenticación

No tiene inicio de sesión propio. Airflows pasa el token del usuario en la URL (`access_token`); la aplicación lo guarda en el navegador y lo usa en todas las llamadas. Lo que cada usuario puede ver depende de sus permisos en Airflows, en particular en la pantalla de informes (ver más abajo).

Desde cualquier pantalla, al pulsar una fila se abre el registro correspondiente en Airflows.

### Pantallas

**Planning.** Diagrama temporal de ocupación de pisos, habitaciones y plazas, con filtros por ciudad, edificio, tipología de piso y de plaza, y navegación por semanas y meses (70 días visibles; hasta 6 meses atrás).

- Cada reserva es una barra con el color de su estado y, al pasar el ratón, sus datos (residente, fechas, contacto). Los grupos y los bloqueos (obras, fuera de servicio, contratos LAU) tienen su propio estilo.
- Marcas de check-in, check-out, última limpieza y limpieza prevista.
- Cada recurso indica su régimen de renta (LAU, próximo fin de LAU, índice), si le falta el número de registro y sus precios por año académico.
- Al indicar un rango de fechas, marca en verde los recursos disponibles (consulta al servicio de integración).
- No permite crear ni mover reservas. En modo selector, permite elegir recursos disponibles; si la tipología elegida no coincide con la solicitada, pide confirmación. La selección se devuelve a Airflows, que la guarda.

Colores de las barras:

| Estado | Color |
|---|---|
| Grupo bloqueado / confirmado | Rosa claro / rosa |
| Pendiente de pago / confirmada | Naranja claro / naranja |
| Caducada | Negro |
| Firma de contrato / contrato | Amarillo claro / amarillo |
| Check-in confirmado / check-in / in house | Verdes, de claro a oscuro |
| Check-out / revisión / devolver garantía | Azules, de claro a oscuro |
| Finalizada | Gris |

**Dashboard general.** Contadores de reservas B2C por fase (solicitudes, alternativas, descartadas pagadas, recurso asignado, próximas entradas y salidas, devolver garantía). Al pulsar un contador se muestra la lista y se puede descargar en Excel. Solo consulta.

**Operaciones.** Pantalla de trabajo diaria, para reservas B2C y residentes de grupos, con pestañas: próximas entradas, entradas, incidencias, próximas salidas, salidas, revisiones y salidas anticipadas o extensiones. Filtros por ciudad, edificios, B2C/B2B y fechas.

- Muestra para cada reserva la salida anterior y la entrada siguiente en el mismo recurso, con el margen en días laborables (descontando fines de semana y festivos); un margen de menos de 2 días se resalta.
- El personal marca las tareas de cada fila (check-in solicitado, limpieza, llaves, keyless, check-in hecho, check-out hecho, revisión, incidencias y desperfectos gestionados, cambio ECO/EXT confirmado) y guarda. Algunas marcas cambian el estado: *Check-in* pasa la reserva a *in house*; *Check-out*, a *revisión*; *Revisión OK*, a *devolver garantía* (o a *revisada* en grupos).
- Cada pestaña se puede descargar en Excel.

**LAU y otros.** Seguimiento de los contratos LAU y otros: devoluciones de fianza, pagos de ITP y fin de contrato. El personal registra la fecha de devolución, la de pago del ITP o la del burofax.

**Administración.** Tres pestañas:

- *Cobros pendientes*: el personal registra las fechas de los avisos de impago.
- *Garantías*: importe y fecha a devolver, importe y fecha devueltos y retención temporal.
- *INCASÒL*: situación de la fianza legal (pendiente, depositada, reclamada, devuelta).

**Documentos.** Documentación obligatoria de las reservas pendiente de subir o de aprobar, agrupada por reserva; se resaltan las entradas en menos de 14 días. Permite ver cada documento y aprobarlo. No permite subir documentos (lo hace el residente en el portal).

**Informes.** Informes Excel y descargas masivas, con sus filtros (fechas, emisor, edificio, año). La lista depende del usuario:

- **Personal de Cotown** (ve todos los proveedores): todos los informes y descargas.
- **Propietarios** (solo se ven a sí mismos): entran en Airflows con su usuario y descargan desde esta pantalla sus ingresos, management fees, contratos y facturas.

| Informe | Filtros |
|---|---|
| Propietarios, Edificios, Recursos (con precios y tarifas), Inventario, Precios, Plantilla Stabilised | — |
| Reservas PowerBI (semanal), Devoluciones, Previsión de devoluciones, Reservas LAU/otros, Análisis LT LAU, Cuestionarios, SEPA | — |
| Disponibilidad, Reservas, Docs reservas, Marketplaces, Pagos recibidos, Descuentos, Contratos, INCASÒL, Plantilla Forecast | Fechas |
| Pagos emitidos, Ingresos, Management fee | Fechas y emisor |
| Rooming list | Reserva de grupo |
| Datos formato N2 (NRUA) | Año |
| Descargas: contratos (fechas, emisor, edificio), facturas y recibos (mes, emisor), CSV N2 (año), declaraciones INCASÒL (fechas) | — |

## 6.4 Portal del residente

### Qué es y dónde se sirve

Área privada de los residentes B2C. Se sirve desde el servidor de servicios, en `https://www.cotowngroup.com/customer/` (carpeta `~/www/sites/cotowngroup/customer` del servidor; la versión anterior se conserva en `customer-old`). La versión desplegada hoy es del 29/08/2026.

### Autenticación

1. El portal redirige al inicio de sesión de **Keycloak** (realm `airflows`, en `core.cotown.com/auth`).
2. Con el token de Keycloak obtiene un token de Airflows (mutación `refreshToken`) y lo usa en todas las llamadas.
3. Carga la ficha del cliente: la seguridad por fila de Airflows solo devuelve la del propio residente. Si no devuelve exactamente un cliente (por ejemplo, un usuario de personal o un propietario), cierra la sesión.
4. *Cerrar sesión* cierra la sesión en Keycloak.

El usuario del residente se crea en Airflows cuando se marca *Crear usuario* en su ficha o cuando se registra en la web de reserva, y recibe el email de bienvenida. Keycloak no tiene una copia de los usuarios: un conector propio (*User Storage SPI*) los consulta directamente en Airflows, de modo que el residente inicia sesión con su email y su contraseña de Airflows.

Los residentes de grupos B2B no tienen acceso: no son clientes del sistema. Las empresas que pagan reservas de grupo tampoco usan el portal: reciben sus facturas por email.

### Secciones

| Sección | Qué puede ver y hacer el residente |
|---|---|
| **Mis datos** | Datos personales, dirección, tutor (si es menor) y datos bancarios. Cada campo se puede rellenar una sola vez: una vez guardado, queda bloqueado (salvo teléfono e idioma) y los cambios posteriores los hace el personal, como control de los datos que van al contrato y a la facturación. Edad mínima: 16 años. Foto de perfil. |
| **Contactos** | Contactos adicionales (tipo, nombre, email o teléfono): alta y baja. |
| **Documentos** | Los documentos que debe aportar, con anverso y reverso según el tipo, subtipo y fecha de caducidad si aplica. Puede subirlos y sustituirlos hasta que el personal los aprueba. |
| **Reservas** | Lista de sus reservas B2C. En el detalle: estado, fechas, motivo, recurso asignado y desglose de precios mensuales. Según el estado: **anular** la solicitud (solicitud, alternativas, pendiente de pago), **aceptar una alternativa**, descargar el **certificado de residencia** (desde firma de contrato hasta check-out) y, a partir de *contrato*, informar **fecha, hora, transporte y opción de check-in** (con su precio según el día y la franja) y, desde 10 días antes de la salida, los de **check-out**. Informar la fecha de llegada pasa la reserva a *check-in confirmado*. |
| **Cuestionarios** | Cuestionarios de check-in y check-out pendientes: puntuaciones, sí/no, texto, incidencias y fotos o vídeos. |
| **Facturas** | Sus facturas y recibos en PDF. |
| **Pagos** | Sus cobros. Los pendientes con medio de pago por tarjeta se pagan con Redsys (ver *Servicio de integración*), siempre que estén completos sus datos fiscales y que no quede pendiente el membership fee de la misma reserva. |
| **PDFs** | Documentos informativos de Cotown (normas, guías), en el idioma del residente. |

La firma de contratos no se hace en el portal sino por DocuSign; el portal solo muestra si el contrato está firmado.

## 6.5 Fuentes

| Tema | Dónde está |
|---|---|
| Backoffice | `front/cotown/src/app/` (pantallas en `pages/`, consultas GraphQL en `schemas/query-definitions/`, llamadas REST en `services/api.service.ts`) |
| Portal | `front/customer/src/app/` (secciones en `customer/`, autenticación en `auth/`, consultas en `schemas/query-definitions/`) |
| Enlaces de los menús de Airflows | Metadatos de Airflows (`Models.ExternalEntity`) |
| Servidor del portal | `back/config/pro/nginx.conf` (sitio `www.cotowngroup.com`) |
| Conector de Keycloak con Airflows (User Storage SPI) y tema de las pantallas de inicio de sesión | `misc/core/keycloak/` |

## 6.6 Pendiente de confirmar

No hay puntos pendientes.
