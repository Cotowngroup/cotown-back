# IT-1. Arquitectura y plataforma

> Manual técnico · Borrador v0.1 · 2026-10-20 · Las marcas **[PREGUNTA Tn]** se resuelven en la ronda de preguntas y desaparecen de la versión final.

## 1.1 Propósito

Este capítulo describe cómo está construido el sistema: qué componentes lo forman, dónde se ejecutan, cómo se comunican entre sí y cómo se reparte la lógica entre la plataforma Airflows y el código propio. Es la referencia para entender cualquier otro capítulo técnico y para diagnosticar dónde puede estar un problema.

No incluye procedimientos de despliegue ni de operación del servidor, que siguen a cargo de Oimbra.

## 1.2 Visión de conjunto

![Arquitectura del sistema](../diagramas/Arquitectura%20Cotown%20v2.png)

El sistema tiene tres bloques:

| Bloque | Dónde | Qué contiene |
|---|---|---|
| **Airflows** | Hetzner, `core.cotown.com` | El ERP de gestión: base de datos, modelo de datos, interfaz del personal, API GraphQL, inicio de sesión y reglas de negocio en la base de datos. También sirve el backoffice complementario. |
| **Servidor de servicios** | Azure, `back.cotown.com` | Todo el código propio que no vive en la base de datos: servidor web, webs comerciales, proceso de reserva, portal del residente, servicio de integración (API), procesos automáticos y monitorización. |
| **Data warehouse** | Azure, `data.cotown.com` | Base de datos analítica y su proceso de carga. Es la fuente de Power BI. |

La regla general es: **los datos y las reglas que dependen solo de los datos viven en Airflows**; lo que necesita hablar con el exterior (pagos, firma, correo, CRM, generación de PDF, webs) vive en el servidor de servicios.

## 1.3 Airflows

### Qué es

Airflows es una plataforma de datos *low-code* orientada por metadatos, producto de un tercero, sobre la que está construido el ERP de Cotown. El modelo de datos (entidades, atributos, relaciones, listas de valores, pantallas y menús) se define como datos dentro de la propia base de datos, en el esquema `Models`, y la plataforma genera a partir de él:

- Las **tablas** de PostgreSQL, en un esquema por área funcional (`Booking`, `Billing`, `Resource`…).
- La **interfaz de usuario** del ERP: menús, listados con filtros y exportación, formularios por pestañas y grupos.
- La **API GraphQL**, con consultas y mutaciones para cada entidad.
- La **búsqueda de texto**: una función `<Tabla>_B0_search` por entidad, generada automáticamente.
- La **seguridad**: usuarios, roles y permisos por fila.

Un proceso de la plataforma (`Models.synchronizer()`) aplica sobre la base de datos los cambios hechos en el modelo: crea o modifica tablas, claves y relaciones, recrea los triggers y programa los procesos periódicos.

### Componentes

| Componente | Descripción |
|---|---|
| **Base de datos** | PostgreSQL 15, base `niledb`. |
| **Modelo** | Esquema `Models`: 12 aplicaciones (menús), 153 entidades, 2.174 atributos, 269 relaciones y 37 listas de valores. Se detalla en el capítulo *Modelo de datos*. |
| **Interfaz de usuario** | Aplicación web del ERP en `https://core.cotown.com`. |
| **API GraphQL** | `https://core.cotown.com/graphql`. Autenticación con token, que se obtiene con la mutación `login` (usuario y contraseña) o renovando un token de Keycloak (`refreshToken`). |
| **API de ficheros** | Lectura y subida de los atributos de tipo documento (contratos, facturas, documentos de clientes…): `/document/<Esquema>/<Entidad>/<id>/<atributo>/contents`. |
| **Keycloak** | Servidor de identidad integrado en `https://core.cotown.com/auth`, *realm* `airflows`. Lo usa el portal del residente. No guarda usuarios propios: un conector (*User Storage SPI*, código en `misc/core/keycloak`) los valida directamente contra los usuarios de Airflows. |
| **Programador de tareas** | Extensión pg_cron de PostgreSQL. Ejecuta las funciones programadas según la frecuencia definida en el modelo. |
| **Enlaces externos** | Entradas de menú que abren aplicaciones externas pasando el token del usuario. Así se integra el backoffice complementario. |

### Lógica de negocio en la base de datos

Gran parte de las reglas de negocio son **funciones de la base de datos** que se registran en Airflows (`Models.Function`) y se enlazan a las tablas como triggers o se programan como tareas periódicas. Hay 236 funciones: 150 de búsqueda generadas por la plataforma y 86 propias de Cotown, de las cuales 82 en PL/pgSQL, 2 en Python (`plpython3u`) y 2 en JavaScript (motor Nashorn, ejecutadas por la interfaz).

El código fuente de las funciones propias está en el repositorio `back`, carpeta `function/`, un fichero por función. Para desplegar una función, su código se carga en la base de datos de Airflows (`Models.Function`) junto con su definición de trigger o su frecuencia, y la plataforma crea o actualiza el trigger o la tarea programada correspondiente.

**Convención de nombres:** `<Esquema>.<Tabla>_<Tipo><Orden>_<descripción>`

| Tipo | Momento | Uso habitual |
|---|---|---|
| `B` | Antes de guardar (BEFORE INSERT/UPDATE) | Validar los datos, completar o calcular campos de la propia fila, cambiar el estado. Puede rechazar el cambio con un mensaje de error. |
| `A` | Después de guardar (AFTER INSERT/UPDATE) | Efectos en otras tablas: crear registros relacionados, recalcular disponibilidad, encolar emails. |
| `D` | Después de borrar (AFTER DELETE) | Limpieza de registros relacionados. |
| `CRON` | Programada | Procesos por fecha: avance de estados, recordatorios, IPC. |

El número de orden determina la secuencia cuando una tabla tiene varios triggers del mismo tipo. Por ejemplo, al modificar una reserva B2C se ejecutan, entre otros, `Booking_B1_init`, `Booking_B2_validate`, `Booking_B3_calc_prices`, `Booking_B4_workflow` y `Booking_B5_buttons`, en ese orden, y después `Booking_A1…`, `Booking_A2_update_availability`, etc.

**Procesos programados:**

| Frecuencia | Procesos |
|---|---|
| Cada 15 minutos (escalonados) | Avance de estados de reservas B2C, grupos y rooming; recordatorios de check-in, check-out, contrato, garantía, documentación y pago; invitación a Trustpilot; facturación de limpiezas de grupos. |
| Cada hora | Histórico de precios y estado de los recursos. |
| Diario, 10:00 | Avisos de llegada de nuevos compañeros (B2C y grupos). |
| Mensual, día 1 | Revisión de inquilinos de edad avanzada (contratos LAU). |
| Mensual, día 28 | Actualización de rentas por IPC (contratos LAU). |

### Seguridad

- **Usuarios**: cada persona que accede tiene un usuario de Airflows con su propio rol de PostgreSQL. Los usuarios se crean automáticamente por trigger al dar de alta personal (`X…`), propietarios (`P…`) o clientes (`C…`).
- **Roles base**: personal de Cotown, proveedor y cliente. Sobre ellos, el personal recibe roles funcionales: *administrators*, *bookings*, *marketing*, *operations*, *billing*, *vandor* y *external*.
- **Seguridad por fila**: las tablas tienen políticas por rol. El personal ve todas las filas; un proveedor o un cliente solo ve las suyas.
- **Usuario de servicio**: el servidor de servicios y el data warehouse acceden con un usuario técnico propio.

El detalle está en el capítulo *Usuarios y roles*.

## 1.4 Servidor de servicios

Máquina en Azure con Docker. Cada pieza es un contenedor en una misma red interna:

| Contenedor | Función |
|---|---|
| **nginx** | Servidor web y proxy inverso. Termina HTTPS (certificados de Let's Encrypt) para todos los dominios, sirve las webs estáticas y reenvía `/api` y `/booking` al servicio de integración. |
| **back** | Servicio de integración: API REST en Python (Flask, servida con gunicorn) y proceso de envío inmediato de emails. Los procesos automáticos se ejecutan dentro de este mismo contenedor. |
| **webgen** | Generador de las webs comerciales (Eleventy). Se ejecuta bajo demanda. |
| **Monitorización** | Loki y Promtail (logs), Prometheus, node-exporter y cAdvisor (métricas), Grafana (consulta). |

### Dominios

| Dominio | Contenido |
|---|---|
| `cotown.com` | Web comercial de Cotown y proceso de reserva. |
| `vanguard-student-housing.com` | Web comercial de Vanguard y proceso de reserva. |
| `www.cotowngroup.com` | Web corporativa y portal del residente (`/customer`). |
| `back.cotown.com` | API (`/api/v1`), proceso de reserva (`/booking`), borradores de las webs y Grafana (`/grafana`). |

### Servicio de integración (API)

API REST bajo `/api/v1`, documentada con Swagger en `/api/apidocs/`. Da servicio a:

- **Webs comerciales**: disponibilidad, pisos, habitaciones, tipologías y promociones (al generarlas y en el navegador), textos legales en PDF y formulario de contacto.
- **Proceso de reserva web**: páginas de los 4 pasos, servidas por el propio servicio.
- **Portal del residente**: preparación del pago con Redsys, certificados, cuestionarios.
- **Backoffice complementario**: dashboards, planning, informes Excel y descargas masivas de PDF.
- **Airflows**: botones de cambio de estado de las reservas.
- **Terceros**: notificaciones de Redsys y DocuSign, API contable para SAP y calendarios iCal para marketplaces.

El detalle de cada grupo de rutas está en el capítulo *Servicio de integración y procesos automáticos*.

### Procesos automáticos

Se lanzan desde el `crontab` del servidor, cada uno dentro del contenedor `back`, con un bloqueo que impide dos ejecuciones simultáneas del mismo proceso:

| Proceso | Frecuencia | Qué hace |
|---|---|---|
| Facturación | Cada 15 min | Genera facturas, recibos y cobros mensuales y de servicios, de reservas B2C, grupos y contratos LAU. |
| PDF de facturas | Cada 15 min | Genera el PDF de las facturas emitidas, lo guarda en Airflows y lo envía por email cuando corresponde. |
| Contratos | Cada 15 min | Genera los contratos y anexos en PDF y los envía a firmar por DocuSign. |
| Cargas de Excel | Cada 15 min | Procesa los ficheros subidos en *Procesos › Cargas* (precios, recursos, rooming…). |
| Envío de emails | Cada 15 min | Envía los emails pendientes (respaldo del envío inmediato). |
| Comprobación de contratos | Diario, 01:00 | Consulta en DocuSign el estado de los contratos enviados (respaldo de las notificaciones de firma). |
| Archivo de facturas | Diario, 02:00 | Organiza los PDF de facturas y recibos por proveedor, año, mes y edificio. |
| Copia a SharePoint | Diario, 02:30 | Copia ese archivo a SharePoint (`rclone`), en *Departments/Financial/Documentación venta activos*. |
| Limpieza de bloqueos | Diario, 03:00 | Elimina bloqueos de procesos que hubieran quedado huérfanos. |
| Rentas máximas | Diario, 05:00 | Recalcula el régimen de renta y las rentas máximas de cada recurso según la Ley de vivienda. |
| Webs comerciales | Cada 2 h | Regenera y publica vanguard-student-housing.com (horas pares, 8:00–20:00) y cotown.com (horas impares, 9:00–21:00). |
| Certificados | Dos veces al día | Comprueba y, si toca, renueva los certificados HTTPS (temporizador de certbot). |

### Cómo se comunica con Airflows

- **GraphQL**, con un usuario de servicio, para la mayoría de lecturas y escrituras y para subir documentos.
- **SQL directo** sobre PostgreSQL, a través de un túnel SSH, para las operaciones masivas (facturación, informes, dashboards) que serían lentas por GraphQL.
- **Notificaciones de PostgreSQL**: al encolar un email, un trigger emite una notificación que el servicio escucha permanentemente, de modo que el email sale en segundos.

## 1.5 Data warehouse

Servidor en Azure (`data.cotown.com`) con una base de datos PostgreSQL 16 analítica (en Docker) y el proceso de carga (ETL, en Python). Power BI se conecta a esta base de datos.

El ETL lee de la base de datos de Airflows y calcula datos generales, ingresos, histórico, camas, ocupación y reservas. Se ejecuta desde el `crontab` del propio servidor a las 03:00 y cada 2 horas entre las 7:00 y las 17:00. La base de datos se reinicia cada día a las 04:00.

El ETL tiene también un paso que carga el libro mayor desde SAP Business ByDesign, pero está **desactivado**.

## 1.6 Flujos técnicos principales

| Flujo | Recorrido |
|---|---|
| **Reserva web** | Navegador → web comercial → `/booking` (servicio de integración) → registro o inicio de sesión en Airflows (GraphQL) → creación de la reserva → triggers de Airflows (precios, estado, cobro, email) → lead en Pipedrive. |
| **Pago con tarjeta** | Portal del residente → `/api/v1/pay/<cobro>` → formulario firmado → Redsys → notificación a `/api/v1/notify` → el servicio marca el cobro como pagado → los triggers avanzan el estado de la reserva. |
| **Email automático** | Trigger o proceso programado → fila en `Customer_email` → notificación → el servicio compone el email con la plantilla de Airflows y lo envía por Microsoft 365. |
| **Contrato** | Reserva en firma de contrato → proceso de contratos genera el PDF desde la plantilla del proveedor → DocuSign → notificación de firma a `/api/v1/contract` → la reserva pasa a contrato. |
| **Facturación** | Proceso de facturación → facturas y cobros en Airflows → proceso de PDF → PDF guardado en Airflows y enviado por email → SAP lo recoge por la API contable. |
| **Webs** | Cron cada 2 h → actualización del código desde GitHub → generador → lee datos de Airflows y del servicio de integración → publica los ficheros estáticos que sirve nginx. |

## 1.7 Entornos

| | Producción | Desarrollo |
|---|---|---|
| Airflows | `core.cotown.com` | `cotown-dev.flows.ninja` |
| Servidor de servicios | `back.cotown.com` | No hay servidor de desarrollo desplegado; el servicio se ejecuta en local contra el Airflows de desarrollo. |
| Pagos | Redsys real | Entorno de pruebas de Redsys |
| Email, DocuSign, CRM | Activos | Desactivados por configuración |

La configuración de cada entorno está en ficheros de configuración del servicio y se selecciona con la variable `COTOWN_ENV`.

## 1.8 Tecnologías

| Ámbito | Tecnología |
|---|---|
| Base de datos | PostgreSQL 15, pg_cron |
| Plataforma | Airflows, Keycloak |
| Servicio de integración y procesos | Python 3.12, Flask, gunicorn, WeasyPrint (PDF), openpyxl (Excel), pandas |
| Backoffice complementario y portal | Angular 15, Angular Material, Apollo (GraphQL) |
| Webs comerciales | Eleventy 2, Nunjucks |
| Infraestructura | Docker, nginx, Let's Encrypt |
| Monitorización | Grafana, Loki, Promtail, Prometheus |
| Código fuente | GitHub, organización `Cotowngroup`: repositorios `cotown-back`, `cotown-front` y `cotown-webs` |

## 1.9 Fuentes

| Tema | Dónde está |
|---|---|
| Configuración de contenedores, nginx, cron y monitorización | `back/config/pro/` |
| Servicio de integración | `back/app/main.py` y `back/app/library/` |
| Procesos automáticos | `back/app/batch_*.py` |
| Funciones de la base de datos | `back/function/` y, desplegadas, `Models.Function` |
| Triggers activos | Catálogo de PostgreSQL (`pg_trigger`) |
| Modelo de datos | Esquema `Models` |
| Data warehouse | `back/etl/` |

## 1.10 Pendiente de confirmar

No hay puntos pendientes.
