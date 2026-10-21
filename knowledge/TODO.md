# TODO – Errores, riesgos y mejoras

Lista única de errores, riesgos y mejoras encontrados durante la extracción de conocimiento. Uso interno de Oimbra: no forma parte de la base de conocimiento ni se menciona en ella.

Un capítulo por prioridad y, dentro de cada uno, por área:

- **🔴 Alta**: fallos críticos de seguridad o de pérdida de datos (puntos C1–C10, con sus pasos de corrección) y otros fallos graves.
- **🟠 Media**: fallos funcionales u operativos.
- **🟢 Baja**: limpieza o mejora.
- **Evidencia**: [E] comprobado en código, BD o servidor; [I] inferido, verificar antes de actuar. Los posibles fallos de lógica se verifican contra la versión desplegada en Airflows antes de corregirlos.
- Al resolver un punto, márcalo con `[x]` y la fecha.

## 1. 🔴 Prioridad alta

### Fallos críticos de seguridad y pérdida de datos

#### C1. Inyección SQL en la API, accesible sin credenciales

- [ ] **Qué pasa**: `back/app/library/business/queries.py` construye las consultas de los dashboards con f-strings a partir de la URL y de la query string. Ejemplo: `GET /api/v1/dashboard/<status>` mete `status` tal cual en `WHERE b."Status" = '{status}'` (`queries.py:213-217`). También `date_from`, `date_to`, `building`, `building[]` y `location` (`queries.py:73-79, 155-228, 304-350, 380-393, 424, 454-467, 490, 502-513, 606-619, 665`) y `/api/v1/report/<status>`. [E]
- **Impacto**: la API no exige token (punto 2) y el servicio se conecta a la BD como `postgres` por el túnel SSH: **cualquiera en Internet puede leer o modificar toda la base de datos**.
- **Corrección**:
  1. Pasar todos los valores como parámetros (`%s` / `%(nombre)s`) y validar `status` contra una lista blanca de estados.
  2. Conectar el servicio a la BD con un usuario de privilegios mínimos, no `postgres`.
  3. Revisar el resto de consultas con f-strings de `queries.py` y `integration.py`.

#### C2. La API no valida la autenticación

- [ ] **Qué pasa**: en `back/app/library/api/token.py`, si una petición no trae token, se ejecuta con el usuario de servicio (`return 403` comentado como "Debug / Remove in production"); si trae un token, no se valida (ni firma ni caducidad). [E]
- **Impacto**: todas las rutas "internas" son públicas en la práctica. En particular, sin credenciales se puede:
  - descargar el certificado de residencia de cualquier reserva (`/cert/<booking>`);
  - obtener la firma manuscrita de cualquier contacto de propietario (`/signature/<id>`);
  - exportar informes con datos personales y bancarios (`/export/sepa` con IBAN, facturas, contratos, `/download/...`);
  - cambiar el estado de cualquier reserva (`GET /booking/<id>/status/<status>`, con un GET y sin validar la transición);
  - consultar cobros (`/pay/<id>`) y escribir cuestionarios (`/questionnaire/<id>`). [E]
- **Corrección**:
  1. Validar el token contra Airflows (o su firma y caducidad) y devolver 401/403 sin token.
  2. Ojo: estas llamadas funcionan hoy **sin token** (con el usuario de servicio) y dejarían de funcionar; corregirlas a la vez o convertir la ruta en pública con su propia protección (revisado ruta a ruta el 2026-10-21):
     - `/signature/<id>`: la piden las plantillas PDF desde WeasyPrint (`contracts/*.md`, `templates/other/annex.html:118`, `cert.html:38`).
     - `/export/<name>`: `front/cotown/src/app/pages/reports/reports.component.ts:110` no añade el token en los informes sin filtro (propietarios, edificios, recursos, inventario, precios, weekly, devoluciones, depositreturns, reservaslau, ltc, cuestionarios, sepa, stabilised).
     - `/pay/<id>`: `front/customer/src/app/services/axios-api.service.ts:30-34` pasa el token como configuración de axios, no como parámetro.
     - `/questionnaire/<id>`, `/iban/<code>`, `/swift/<code>`: `axios-api.service.ts:74, 79, 92`, sin token.
     - `/form`: formularios de las webs (`webs/code/src/includes/shared/js/pipedrive.js:55`), sin token; debería ser pública (`pub_`) con su protección antirrobots.
     - `/ical/<token>`: la consultan los marketplaces; debería ser pública (`pub_`), protegida por el token de la ruta.
     - Botones de Airflows (`/booking/<id>/status/...`): las URL que generan `Booking_B4_workflow.sql:22,28` y `Booking_B5_buttons.sql:39-63` no llevan token; comprobar si Airflows lo añade.
     - Además, el backoffice envía `access_token=` vacío cuando no hay token (`localStorage.getItem('access_token') || ''`), que no cae en el usuario de servicio.
  3. Comprobar en cada ruta que el usuario tiene derecho sobre el recurso (reserva, cobro, cuestionario).
  4. Cambiar el cambio de estado de reservas a POST.

#### C3. Posible inicio de sesión como otro cliente en la web de reserva

- [ ] **Qué pasa**: el `APIClient` es uno por proceso de gunicorn y se comparte entre peticiones. `library/services/apiclient.py:43-50` no borra el token anterior si el login falla, y `library/api/booking.py:231` comprueba `token is None`, que nunca ocurre. Con una contraseña incorrecta se reutiliza el token de la petición anterior atendida por ese proceso; si era de otro cliente, `Customer_CustomerList` devuelve un registro y se inicia sesión como él. Además, la mutación de login concatena usuario y contraseña (inyección GraphQL). [I: verificar en pruebas]
- **Corrección**: usar un cliente GraphQL por petición (o reiniciar el token antes de cada login), comprobar el resultado del login y pasar usuario y contraseña como variables GraphQL.

#### C4. La carga de "Valoraciones" borra todas las valoraciones

- [ ] **Qué pasa**: en `back/app/library/business/load_values.py:35-40` la subconsulta `SELECT "Resource_id" FROM "Resource"."Resource" WHERE "Code" IN …` usa una columna que no existe en `Resource.Resource`; PostgreSQL la resuelve contra la tabla exterior y el `DELETE` borra **todas** las filas de `Resource_value`, no solo las de los recursos de la hoja. Después inserta solo las de la hoja. [E: columnas verificadas en `Models`]
- **Impacto**: según los logs, esta carga se usó el 22/05, 26/06, 31/07, 12/08, 30/09 y 09/10/2026. Las valoraciones son periódicas (p. ej., cada 6 meses) y la tabla guarda una por recurso y fecha. La plantilla de carga se obtiene del informe "recursos", cuya hoja de valoraciones exporta **todo el histórico** (`templates/report/recursos.valoraciones.sql`, sin filtro de fechas): si la carga se prepara así (descargar, añadir las nuevas, subir), cada carga reinserta el histórico y **no se pierde nada**. Pero basta con que alguien suba una hoja solo con las valoraciones nuevas para borrar todas las demás. [E, logs del servidor y plantilla 2026-10-20]
- **Comprobación recomendada**: que alguien con permisos ejecute `SELECT "Valuation_date", count(*) FROM "Resource"."Resource_value" GROUP BY 1 ORDER BY 1;` y confirme que siguen existiendo las fechas de valoración antiguas.
- **Corrección**:
  1. Cambiar la subconsulta por `SELECT id FROM "Resource"."Resource" WHERE "Code" IN %s`.
  2. Corregir el `except:` que usa `error` sin definir (`load_values.py:43-46`).

#### C5. Contraseña inicial común para todos los usuarios y reseteo al cambiar el email

- [ ] **Qué pasa**: todos los usuarios nuevos de Airflows (personal `X…`, propietarios `P…` y clientes `C…`) se crean con **la misma contraseña fija** (`back/function/Admin.User_A1_create_user.sql:20`, `Customer.Customer_A1_create_user.sql:29`, `Provider.Provider_A1_create_user.sql:24`; el registro web hace login con ella en `back/app/library/api/booking.py:302`). Además, **al cambiar el email de un propietario su contraseña vuelve a la de por defecto** (`Provider.Provider_B2_validate.sql:21`). Los roles de PostgreSQL de cada usuario se crean también con una contraseña literal común (`Admin.User_A1:29`, `Customer_A1:42`, `Provider_A1:37`). [E]
- **Impacto**: cualquiera que conozca esa contraseña puede entrar en el ERP, en el portal o en la web de reserva con cualquier cuenta que no la haya cambiado. Los nombres de usuario son secuenciales y predecibles. [I: depende de cuántos usuarios no la hayan cambiado]
- **Corrección**:
  1. Generar una contraseña aleatoria por usuario (o ninguna) y enviar un enlace de activación o de restablecimiento.
  2. Quitar el reseteo de contraseña al cambiar el email del propietario.
  3. Forzar el cambio de contraseña a los usuarios que aún tengan la de por defecto.
  4. Revisar si los roles de PostgreSQL por usuario necesitan contraseña (si no se conectan directamente, crearlos sin `LOGIN`).

#### C6. La carga de "Estados" borra todos los bloqueos

- [ ] **Qué pasa**: el mismo error en `back/app/library/business/load_status.py:35-40` (`"Resource_id"` y `"Booking_id"` no existen en `Resource.Resource`). El `DELETE` borra **todas** las filas de `Resource_availability` sin reserva de todo el sistema (bloqueos de contratos LAU, capex, pre-capex, CTH…) y luego inserta solo las de la hoja. [E]
- **Impacto**: según los logs, no se ha usado desde mayo de 2026; si se usa, se pierden los bloqueos de disponibilidad de todos los recursos que no estén en la hoja.
- **Corrección**: subconsulta `SELECT id FROM "Resource"."Resource" WHERE "Code" IN %s` y filtrar `"Booking_id" IS NULL` en la tabla exterior; corregir también el `except:` (`load_status.py:44-47`). Hasta corregirlo, avisar de que no se use esta carga.

#### C7. XSS almacenado en el backoffice desde el formulario público de reserva

- [ ] **Qué pasa**: el backoffice complementario (`front/cotown`) construye HTML con datos del cliente sin escapar (nombre, email, teléfonos, comentarios) y lo pinta con `[innerHtml]` y el pipe `safe`, que llama a `bypassSecurityTrustHtml` y desactiva la protección de Angular. Ejemplo verificado: el tooltip de las barras del planning (`src/app/pages/planning/planning.component.ts:741-754`, pintado en `src/app/time-chart/time-chart-control/time-chart-control.component.html:62,79`). También en `operations.component.ts:288,305` y en las vistas de administración, LAU y documentos. [E]
- **Impacto**: cualquiera puede registrarse en la web de reserva con un nombre o comentario que contenga un script. Cuando alguien del personal abre el planning o un dashboard, el script se ejecuta en su sesión y puede leer su token de Airflows (`localStorage.access_token`) y actuar en el ERP en su nombre.
- **Corrección**:
  1. Escapar los datos al construir el HTML (o construir los tooltips con plantillas de Angular sin `innerHtml`) y retirar el pipe `safe` donde haya datos de usuario.
  2. Revisar los datos ya guardados (nombres y comentarios con `<` o `>`).
  3. Añadir una política CSP en el servidor que sirve el backoffice.

#### C8. Sin copia de seguridad externa de la base de datos de Airflows

- [ ] **Qué pasa**: la base de datos de Airflows (`niledb`, en `core.cotown.com`) tiene copia base de PostgreSQL y recuperación a un instante (PITR), pero **en el mismo servidor**; no hay copia fuera de él. Tampoco hay copia de la configuración de los servidores de Azure (configuración del servicio, `crontab`, certificados, `~/etl` con las fotos del Business Plan y los CSV del libro mayor). [E, confirmado por Alejandro 2026-10-20]
- **Impacto**: si se pierde el servidor de Airflows (fallo de disco, borrado, cifrado por ransomware, problema con el proveedor), se pierden a la vez la base de datos y sus copias: **todo el ERP** (reservas, clientes, facturas, contratos y documentos).
- **Corrección**:
  1. Copiar las copias base y los WAL a un almacenamiento externo (otro proveedor o cuenta, p. ej. Azure Blob o S3), con cifrado y retención definida.
  2. Programar y supervisar la copia (alerta si falla).
  3. Probar una restauración completa periódicamente.
  4. Versionar o copiar la configuración de `back.cotown.com` y `data.cotown.com`.

#### C9. El data warehouse es accesible desde Internet

- [ ] **Qué pasa**: el PostgreSQL del data warehouse (`data.cotown.com`, contenedor `postgres`) publica el puerto 5432 en todas las interfaces y **responde desde Internet** (comprobado el 2026-10-20). Solo lo protege la contraseña del usuario de la base de datos, que está en el repositorio (`back/etl/.secrets.toml`). El data warehouse contiene datos personales de clientes (`gold.booking`: email, teléfonos, fecha de nacimiento) y toda la información financiera. El cortafuegos del sistema (`ufw`) está inactivo. [E]
- **Impacto**: cualquiera con acceso al repositorio (o que obtenga la contraseña) puede leer el data warehouse desde cualquier lugar.
- **Corrección**:
  1. Limitar el puerto 5432 en el grupo de seguridad de Azure a la IP de la puerta de enlace de Power BI (y, si hace falta, a las de Oimbra).
  2. Rotar la contraseña y sacarla del repositorio.
  3. Crear un usuario de solo lectura para Power BI, distinto del que usa el ETL.
  4. Quitar los datos personales innecesarios de `gold.booking` (ver `TODO.md`).

#### C10. Incidente: acceso remoto no autorizado a back.cotown.com (`helmsman` y clave `fleet_ed25519`)

- [x] 2026-10-20 **Cerrado por Alejandro**: acceso cerrado y comprobado; las IP de inicio de sesión pendientes son conocidas. La rotación de credenciales queda como recomendación en el punto *Rotar las credenciales expuestas*.
- **Qué pasó** [E, servidor 2026-10-20]:
  - El **23/07/2026 16:22** se instaló en `back.cotown.com` el agente `helmsman` (servicio systemd `helmsman`, `/usr/local/lib/helmsman`). Es una herramienta de "gestión de flotas por Telegram": un *hub* con un bot de Telegram registra servidores, entra en ellos por SSH, instala el agente y, desde entonces, el agente consulta al hub por HTTPS y **ejecuta como `root`** los comandos que recibe. La IP `51.103.21.92` que figuraba en el servicio es la del propio `back.cotown.com` (etiqueta del agente), **no** la del hub. La dirección del hub estaba en `config.env` (`HUB_URL`), que no se leyó y se borró al eliminar el agente: **se desconoce dónde está el hub y quién lo controla**.
  - El **09/08/2026** se añadió a `/root/.ssh/authorized_keys` una segunda clave, `fleet_ed25519` (ED25519 `SHA256:SrKDP5yVzzju53Bnwe6g6mLdzub+jDZwukvQ38pCuxM`), y el **05/09/2026 14:52 UTC** se usó para entrar como `root` desde `77.236.19.135`. **Esta clave sigue autorizada**: eliminar el agente no cerró este acceso.
  - **2026-10-20 19:50**: Alejandro quitó la clave `fleet_ed25519`. Comprobado después: `authorized_keys` de `root` y `cotown` solo tienen `cotown.key.pem`; sin rastro de `helmsman`; sin usuarios nuevos; ninguna cuenta tiene contraseña utilizable; `dpkg --verify` sin alteraciones en `openssh`, `pam`, `sudo`, `systemd`, `bash`, `coreutils`, `procps`, `python3.14` ni `docker`; sin `ld.so.preload`; `crontab` de `root` y `cron.d` sin cambios; `/usr/local` vacío. El intruso también había creado `/etc/ssh/sshd_config.d/00-fleet.conf` y modificado `/etc/ssh/sshd_config` (ambos el 09/08/2026 12:36) para activar `PermitRootLogin yes` y `PasswordAuthentication yes`. **2026-10-20 19:56**: corregido (`00-fleet.conf` borrado; `PermitRootLogin no` y `PasswordAuthentication no`; `ssh` recargado) y comprobado desde fuera (`Permission denied (publickey)`). Se vació también `sshd_config.d`, incluidos `50-cloud-init.conf` y `50-cloudimg-settings.conf` (sin efecto con la configuración actual).
  - El servidor admite **inicio de sesión con contraseña** y **como `root`** (`PasswordAuthentication yes`, `PermitRootLogin yes`), y el usuario `cotown` tiene `sudo` sin contraseña. Desde el 27/08/2026 hay ~1,3 millones de intentos fallidos de contraseña desde Internet.
  - Los registros del sistema solo llegan al 27/08/2026: no hay registro de quién instaló el agente en julio. En `/root` hay una carpeta `.ansible` del 11/08/2026 (se ejecutó Ansible como `root`), `.profile` modificado el 24/08/2026 y `.bash_history` y `.viminfo` recientes.
  - Inicios de sesión SSH aceptados desde el 27/08/2026, aparte de las IP domésticas habituales (`2.138.x.x`, `85.48…`, `81.47…`, `80.29…`, `46.6…`, `176.83…`, `95.127…`), **pendientes de identificar**:

    | IP | Clave | Usuario | Primera | Última |
    |---|---|---|---|---|
    | `77.236.19.135` | `fleet_ed25519` | `root` | 05/09/2026 | 05/09/2026 |
    | `116.203.34.22` (Hetzner) | `cotown.key.pem` | `cotown` | 21/09/2026 | 20/10/2026 (diaria) |
    | `78.47.185.39` (Hetzner) | `cotown.key.pem` | `cotown` | 06/09/2026 | 06/09/2026 |
    | `37.209.162.162` | `cotown.key.pem` | `cotown` | 08/09/2026 | 15/10/2026 |
    | `45.129.228.34` | `cotown.key.pem` | `cotown` | 27/08/2026 | 27/08/2026 |
    | `43.252.22.194` | `cotown.key.pem` | `cotown` | 27/08/2026 | 27/08/2026 |
  - En `data.cotown.com` no está la clave `fleet_ed25519` y no se admite contraseña ni `root` con contraseña. En `core.cotown.com` el usuario `partner` no tiene la clave; no se ha podido revisar `root` (sin permisos).
- **Impacto**: desde el 23/07/2026, un tercero desconocido ha tenido control total de `back.cotown.com` y lo **sigue teniendo** por la clave de `root`. Con ello tiene todo lo que hay allí: los secretos de producción (`~/app/.secrets.toml`: contraseña de la BD de Airflows, usuario de servicio GraphQL, claves de Redsys, DocuSign, correo, Pipedrive, claves de la API de contabilidad), la clave SSH `id_partner.pem` (acceso a `core.cotown.com` y, por el túnel, a la BD de Airflows como `postgres`, es decir, a **todos los datos del ERP**), la clave de DocuSign y el token de SharePoint de `rclone`. **Hay que suponer que todos están comprometidos.**
- **Respuesta**:
  1. [x] 2026-10-20 **Inmediato: cerrar el acceso** (hecho, salvo limitar el puerto 22 en Azure). Quitar la línea `fleet_ed25519` de `/root/.ssh/authorized_keys`; poner `PasswordAuthentication no` y `PermitRootLogin no` (o `prohibit-password`) en `sshd` y recargarlo; revisar `/etc/sudoers.d`. Limitar en el grupo de seguridad de Azure el puerto 22 a las IP de Oimbra.
  2. **Conservar evidencias** antes de seguir: copia de `journalctl`, `/var/log`, el historial de shell de `root` y `cotown`, `crontab` de todos los usuarios, unidades de systemd, `/root` y `authorized_keys`, con sus fechas.
  3. **Rotar todas las credenciales** que estaban en `back.cotown.com` y las claves SSH, siguiendo el apartado "Ciclado de claves" del *Inventario de credenciales*. Prioridad: clave `id_partner.pem` de `core` y contraseña de la BD de Airflows; después usuario de servicio GraphQL, claves de Redsys, de la API de contabilidad y de DocuSign.
  4. **Revisar lo ejecutado desde el 23/07/2026**: inicios de sesión (`journalctl`, `last`), comandos `sudo`, usuarios nuevos, cron y systemd añadidos, ficheros modificados en `/etc`, `/usr/local`, `/opt`, `/root` y `/home`, contenedores e imágenes Docker nuevos. Identificar las IP de origen de los inicios de sesión que no sean de Oimbra.
  5. **Buscar persistencia** en `core.cotown.com` (pedir al proveedor de Airflows que revise `root` y `partner`, los inicios de sesión y `pg_stat_activity` y los logs de PostgreSQL), en los repositorios (commits, ramas o claves de despliegue no reconocidos, acciones, webhooks) y en los portales externos (Redsys, DocuSign, Pipedrive, M365, SharePoint).
  6. **Reinstalar** `back.cotown.com` desde cero, salvo que la revisión permita descartar otras puertas traseras.
  7. **Comunicar** el incidente a Cotown y valorar con ellos la notificación a la AEPD (había acceso a datos personales de clientes): 72 horas desde que se tiene constancia (20/10/2026).

### Seguridad

- [ ] 🔴 **Secretos y claves privadas en git** (repo `back`): `app/.secrets.toml`, `etl/.secrets.toml`, `airflows.key.pem`, `etl/*.key.pem`, `app/id_partner.pem` (también copiada en `app/templates/report/`), `app/docusign.private.key`, `app/docusign/*.key`. Sacarlos del repositorio, limpiar el historial y rotar las claves. [E]
- [ ] 🔴 **Contraseñas en el código**: `webs/upload/upload.py`, `webs/code/src/data/constants.js` (login del usuario de servicio), `back/etl/sap.py` y `front/cotown/src/app/app.component.ts:163-170` (código comentado con el usuario administrador de modelos). Mover a configuración, borrar y rotar (siguen en el historial de git). [E]

### Operación e infraestructura

- [x] 2026-10-20 **Agente `helmsman` eliminado** de `back.cotown.com`: agente de administración remota controlado por Telegram, instalado el 23/07/2026, que ejecutaba como `root` los comandos recibidos de un hub desconocido (51.103.21.92 es la IP del propio servidor). Eliminado y verificado (servicio, ficheros, proceso y conexiones). Se trata como **incidente de seguridad**: ver C10. [E]

### Triggers de base de datos

- [ ] 🔴 **Doble reserva B2C/B2B posible**: la comprobación de solapes de `Booking.Booking_B2_validate.sql:107-114` usa `b."Booking_id" <> NEW.id`, que excluye las filas de `Booking_detail` sin `Booking_id` (las de grupos y bloqueos), así que **una reserva B2C no detecta solape con un grupo** (ni con un bloqueo). Los grupos tampoco comprueban solapes con B2C (`Booking_group_A2_create_rooms.sql`). [I: verificar con un caso]

### Procesos automáticos (back/app)

- [ ] 🔴 **`import prints` en un `except`** (`library/business/contract.py:1266`): el módulo no existe, así que cualquier error al generar un contrato B2B lanza `ModuleNotFoundError` y aborta todo `batch_printcontract` (no se procesan el resto de grupos, los envíos ni los anexos). [E]

## 2. 🟠 Prioridad media

### Seguridad

- [ ] 🟠 **Api-Key de la integración contable resuelta como nombre de configuración** (`api/integration.py:115,259,400,483`): cualquier nombre de clave de configuración con valor sirve como Api-Key en `customers` e `invoices`; su valor se inserta en SQL. Además la clave recibida se escribe en el log (`:117`). Usar una sección dedicada y validar el rango numérico. [E]
- [ ] 🟠 **Contraseña del registro web guardada en la cookie de sesión** (firmada, no cifrada) junto con el JWT de Airflows (`api/booking.py:456`). [I]
- [ ] 🟠 **Token iCal predecible**: es base64 de `md5(Code)` y el código de recurso es público (`function/Resource.Resource_B1_flat_data.sql:15`). [E]
- [ ] 🟠 **Redirección abierta** en `/api/v1/href/<path>`: limitar a destinos permitidos. [E]
- [ ] 🟠 **Webhook de DocuSign** (`POST /api/v1/contract`) público sin verificar la firma HMAC: `api/contract.py:27-56` confía en el JSON recibido; cualquiera puede marcar como firmado el contrato de una reserva. [E]
- [ ] 🟢 **Rutas de la API sin uso** (revisado 2026-10-21): `/dashboard/documents` sin estado, `/booking/<id>/status/<s>/<old>`, `/notify` sin terminal (Redsys siempre usa `/notify/<pos>`), `/roomsd/...`, `/http/<code>`, `/hi` (no hay sonda que la use) y `/assets/...` (nginx no la enruta al contenedor). Además, la vista `req_occupancy` (`library/api/airflows.py:118`) no está registrada. `/href/<path>` no tiene llamador en los repositorios: confirmar si se usa desde Airflows. Retirar las que no se usen. [E]
- [ ] 🟠 **Clave de la API contable** con alcance `0:9999` (todas las sociedades): acotar al código de empresa que corresponda. [E]

### Operación e infraestructura

- [ ] 🟠 **Repositorio desalineado con producción**: el crontab real de `back.cotown.com` no coincide con `back/config/pro/crontab` (el real añade `checkcontract` 01:00, `sharepoint` 02:00, `rclone` a SharePoint 02:30, `law` 05:00 y limpia bloqueos a las 03:00). Actualizar el repositorio. [E, servidor 2026-10-20]
- [ ] 🟠 **`dobatch.sh` desalineado**: el del servidor tiene `trap` para borrar el bloqueo; el del repositorio (`back/app/dobatch.sh`) no. Subir la versión del servidor. [E]
- [ ] 🟠 **El ETL de producción ejecuta una versión antigua**: en `data.cotown.com`, `~/etl` no es una copia de git (se copió a mano, con saltos de línea de Windows) y tres consultas son anteriores al repositorio (servidor 07/07/2026, repo `bfb7b24` 09/07/2026): `sql/booking.sql`, `sql/mf_b2b_otb.sql` y `sql/mf_b2c_otb.sql`. La versión del servidor calcula el management fee previsto (OTB) siempre con `Management_fee` del recurso, sin tener en cuenta la frecuencia de limpieza ni la comisión de marketplace; la del repositorio lo hace igual que la facturación (`Invoice_line_B1_change`). **Los management fees previstos en Power BI no cuadran con los facturados.** Desplegar el ETL desde git (clon en el servidor) y verificar los datos. [E, servidor 2026-10-20]
- [ ] 🟠 **Crontab y scripts del data warehouse fuera del repositorio**: el crontab de `data.cotown.com` (ETL a las 03:00 y cada 2 h de 7 a 17, reinicio de Postgres a las 04:00) no está versionado. [E]
- [ ] 🟠 **Reinicio diario del Postgres del DW** (`docker restart postgres` a las 04:00): parece tapar un problema de fondo (memoria o conexiones). Investigar. [I]
- [ ] 🟠 **Tras un reinicio del servidor de servicios, las webs, el portal y la API quedan caídos**: solo el contenedor `back` tiene política de reinicio (`unless-stopped`); `nginx`, `webgen`, `grafana`, `prometheus`, `loki`, `promtail`, `cadvisor` y `nodexp` tienen `no`. Poner `unless-stopped` (en `back/config/pro/makefile` y en los contenedores actuales). [E, servidor 2026-10-20]
- [ ] 🟠 **`~/app` del servidor de servicios no es un clon de git** (copia manual): no se sabe con certeza qué versión está desplegada. Contiene además restos (`batch_sendcrm.py`, borrado en el repositorio; `contratos.zip`, `facturas.zip`, `incasol.zip`, `md.py`, `oid.py`). Desplegar desde git y limpiar. [E]
- [ ] 🟠 **Certificado del data warehouse**: se copia de Let's Encrypt a `~/certs` con `~/certs/renew.sh`, que no está en el `crontab`; confirmar que certbot lo ejecuta tras renovar (hook de despliegue). El actual caduca el 09/01/2027; si no se copia, Power BI dejará de conectar. [I]
- [ ] 🟠 **Rotar las credenciales expuestas en `back.cotown.com`** tras el incidente C10 (cerrado el 2026-10-20): entre el 23/07 y el 20/10/2026 un tercero tuvo acceso `root`. Prioridad: clave `id_partner.pem` (`core`) y contraseña de la BD de Airflows; después usuario de servicio GraphQL, Redsys, claves de la API de contabilidad, DocuSign, correo, Pipedrive y token de `rclone`. Pasos en el apartado "Ciclado de claves" del *Inventario de credenciales*. Pendiente también limitar el puerto 22 de `back` en Azure a las IP de Oimbra y pedir al proveedor de Airflows que revise `root` en `core`. [E]
- [ ] 🟠 **Imágenes Docker sin versión fija** en `back` (`nginx:latest`, `grafana/grafana:latest`, `prom/prometheus:latest`, `grafana/loki:latest`, `grafana/promtail:latest`, `cadvisor:latest`) y `node-exporter:v1.2.0` muy antigua: un reinicio con `pull` puede cambiar de versión sin control. Fijar versiones. [E, servidor 2026-10-20]
- [ ] 🟠 **Sin historial de cambios**: el trigger `Admin.audit` (en 153 tablas) solo rellena `Created_*`/`Updated_*`; el registro de cambios en `Admin.Log` (registro anterior y diferencias) está comentado (`back/function/Admin.audit.sql:17-46`), así que no se puede saber quién cambió qué, salvo en reservas (`Booking_log`). Decidir si se reactiva (valorar volumen). [E]
- [ ] 🟠 **Rol `external` sin uso pero asignado a 3 usuarios**: da lectura de todo el ERP (clientes, facturas, reservas) y modificación en reservas. Revisar esos 3 usuarios y retirar el rol. [E, configuración de Airflows 2026-10-20]
- [ ] 🟠 **Sin alertas** (hoy la supervisión es manual, a cargo de Alejandro; decidido automatizarla 2026-10-20): Prometheus no tiene reglas ni Alertmanager, y no se monitoriza la disponibilidad de la API, nginx, Airflows ni el ETL. [E]
- [ ] 🟠 **Algo agota las 10 conexiones del rol `readonly` de forma recurrente** (19 y 20/10/2026): averiguar quién lo usa (`SELECT usename, application_name, client_addr, state, backend_start FROM pg_stat_activity WHERE usename = 'readonly'`) y darle su propio rol; probablemente conexiones que no se cierran (¿Metabase, Power BI, alguna herramienta de consulta?). [E]

### Triggers de base de datos

- [ ] 🟠 **Validaciones que no se aplican al asignar recurso**: `Booking_B2_validate.sql:102-104` mira el estado anterior (antes de que B4 lo cambie); al asignar recurso a una solicitud, la reserva pasa a pendiente de pago o confirmada **sin** comprobar solape, datos fiscales ni lista negra hasta el siguiente cambio. [I]
- [ ] 🟠 **Reservas sin recurso reprocesadas en cada cambio**: `Booking_B4_workflow.sql:222` compara `OLD.Resource_id = NEW.Resource_id`, que da NULL sin recurso; cada UPDATE de una reserva en alternativas o descartada vuelve a enviar el email, escribir log y borrar cobros. [I]
- [ ] 🟠 **Prorrateo proporcional del último mes con los días del mes anterior** (`Booking_B3_calc_prices.sql:323`, `Booking_group_A1_create_prices.sql:64`): p. ej. salida el 10 de marzo → divide entre 28. [I]
- [ ] 🟠 **Contratos LAU borrados dejan sus bloqueos**: `Booking_other_A1_locks.sql:15-16` usa `NEW` en DELETE (es NULL). [I: salvo FK en cascada]
- [x] 2026-10-20 **Check-in/check-out de grupos**: el trigger crea un único cobro al pagador (con el primer residente que hace check-in o check-out). Es correcto: el servicio es una cantidad única para todas las plazas (Alejandro, 2026-10-20; corrige la regla anotada antes). [E]
- [ ] 🟠 **Management fee de marketplace sin desplegar**: el `Billing.Invoice_line_B1_change` desplegado en Airflows no usa `Management_fee_marketplace` (ni en B2C ni en grupos); el del repositorio sí, en los dos casos. Desde 2025 hay 64 líneas de facturas de grupos con marketplace y 57 no llevan el management fee de marketplace. Regla (Alejandro, 2026-10-20): las reservas B2C y los grupos con marketplace usan el management fee de marketplace. Desplegar la función del repositorio y decidir si se recalculan las líneas ya emitidas. [E, BD 2026-10-20]
- [ ] 🟠 **Confirmar un grupo al crearlo falla** ("No places assigned": las plazas se crean en el trigger AFTER) y no se puede desconfirmar y volver a confirmar ni corregir la garantía (`Booking_group_B2_workflow.sql:31-39, 101`). [I]
- [ ] 🟠 **IPC**: si `Auxiliar.Ipc` está vacía, `LEAST(NULL, …)` aplica `Max_IPC` o **999 %**; `Applied_IPC` no se reinicia, así que si falla el aviso se aplica el IPC del año anterior (`Booking_other_CRON_IPC.sql:28-32, 68`). [I]
- [ ] 🟠 **Los procesos programados masivos son todo o nada** (`Booking_CRON_workflow.sql:12,22,33,44`): un error en una reserva (p. ej. un solape) impide el cambio de estado de todas las demás y solo deja un aviso. [I]
- [ ] 🟠 **Se pueden añadir líneas a facturas emitidas**: `Billing.Invoice_line_B1_change.sql:30-38` solo protege UPDATE y DELETE; un INSERT cambia el total de una factura ya numerada. La protección de `Invoice_B2_validate.sql:42-51` tampoco detecta cambios desde o hacia NULL ni protege `Code`, `Total` o el medio de pago. [E]
- [ ] 🟠 **Duplicar una factura LAU pierde la reserva LAU** (`Invoice_B1_copy.sql:24-42` no copia `Booking_other_id`). [E]
- [ ] 🟠 **Números truncados con `LPAD`**: usuarios `X/C/P` + 6 dígitos (colisión a partir del id 1.000.000), número de pedido manual (5 dígitos) y número de factura (5 dígitos por año y emisor). [E]
- [ ] 🟠 **`RESET ROLE` sin restaurar el rol** en varias salidas tempranas (`Booking_B2_validate.sql:102-104`, `Booking_B6_checkin.sql:121`, `B6_checkout.sql:118`, `Booking_group_rooming_B3/B4:124`, `Booking_other_A1_locks.sql:21`, `Booking_group_A2_create_rooms.sql:27`, `Customer_D1_delete_user.sql:9`, `Provider_D1_delete_user.sql:9`, `Resource_B1_flat_data.sql:20`): el resto de la transacción continúa con el rol de sesión. [E]
- [ ] 🟠 **Email con copias equivocadas**: `Customer_email_B1_validate.sql:28-35` trata siempre `Entity_id` como una reserva, pero en `pago` es un cobro y en `bienvenida` un cliente: CC/CCO de otra marca o vacíos. [E]
- [ ] 🟠 **`Admin.goout.js` envía el token del usuario a cualquier URL** (redirección abierta con fuga de token); hoy solo se usa desde los enlaces externos del menú. [E]
- [ ] 🟠 **Recordatorio de firma en edificios sin contrato digital**: `Booking_CRON_contract_emails` envía *firmacontratorecall* cada 3 días a toda reserva en *firma de contrato*, también en edificios sin *Emitir contratos* (`Building.Contract` = false), donde no hay nada que firmar en DocuSign. Debe enviarse solo si el edificio emite contratos digitales (Alejandro, 2026-10-21). [E]
- [ ] 🟠 **Tipo de edificio "No publicar"** (id 6): según Alejandro ya no se usa (la publicación va por la web del piso), pero **7 edificios lo tienen** (AVM110, AVN062, BVM201, COR207, ENC160, SEP083 activos y PTX004 inactivo), 6 de ellos con pisos asignados a una web, y el código sigue filtrando por tipo: el asistente de reserva solo ofrece tipos 1–3 (`booking.py:190` `< 4`, `:272` `< 3`) y la portada solo lista tipos 1–2 (`home/locations.html.njk`, `main-header.html.njk`). Esos edificios tienen página de edificio y disponibilidad, pero no salen en la portada ni en el asistente de reserva; lo mismo los de grupos (COR052, ENT069, ROB67A, ROB67B) y B2B (RAL006). Decidir el tipo correcto de esos edificios o quitar los filtros por tipo. [E, BD 2026-10-20]

### Frontends (front/cotown y front/customer)

- [ ] 🟠 **Token de Airflows en la URL y en `localStorage`** (backoffice) y como parámetro `access_token` en todas las llamadas (los dos frontends): queda en historial, logs y Referer. Enviarlo en cabecera. El portal no renueva el token de Airflows: al caducar, las consultas fallan en silencio hasta recargar. [E]
- [ ] 🟠 **El portal llama a `/pay`, `/questionnaire`, `/iban` y `/swift` sin token** (`front/customer/src/app/services/axios-api.service.ts:29-33, 72-93`); también los informes sin filtro del backoffice (`front/cotown/src/app/pages/reports/reports.component.ts:110`). Hay que corregirlo a la vez que la autenticación de la API (C2). [E]
- [ ] 🟠 **Backoffice – operaciones**: guardar en "Incidencias" quita la fila aunque no se marque "Gestionadas" (`operations.component.ts:581`); en B2B la casilla de check-out no se guarda (`:525-528`, `booking.query.ts:164-193`); los festivos intermedios no se descuentan del margen entre reservas (`:346, :363`). [E]
- [ ] 🟠 **Backoffice – administración**: marcar "Retenida temporalmente" en Garantías lanza un error y no se puede guardar (`admon.component.ts:379-386`). [E]
- [ ] 🟠 **Backoffice – informes**: "Ingresos" para propietarios no está implementado (`reports.component.ts:45`); no se comprueba la respuesta y un error se descarga como fichero sin nombre (`:243-258`); "Descuentos", "Marketplaces" y "Forecast" se pueden lanzar sin fechas (`:116-145`). [E]
- [ ] 🟠 **Backoffice – planning**: con "Todos" los edificios no se muestra la disponibilidad (`planning.component.ts:871`); los recursos sin tarifa no aparecen (`:508`). [E]
- [ ] 🟠 **Excel de dashboards que fallan**: no hay plantilla para `revision` (operaciones) ni para `upload`/`approve` (documentos): error 500 (`back/app/library/api/airflows.py:214-248`). [E]
- [ ] 🟠 **Portal – datos no guardados**: `UPDATE_CUSTOMER` no incluye `Tutor_document` ni `Name` (`customer.query.ts:229-292`); los datos bancarios se exigen siempre aunque la cuenta coincida con el IBAN (`myData.component.ts:368-374`). [E]
- [ ] 🟠 **Portal – pagos**: si `/pay` devuelve error (p. ej. datos fiscales incompletos), el spinner se queda girando (`invoicePay.component.ts:40`); las pantallas de pago correcto o fallido no refrescan los pagos y están solo en español. [E]

### Webs comerciales (webs/code)

- [ ] 🟠 **Las páginas retiradas nunca se borran**: `config/publish.sh` copia con `rsync` sin `--delete` y no limpia `sites/<site>-publish`; edificios, ciudades o posts retirados siguen publicados e indexables para siempre. Además, sin `set -e` ni comprobación del build, si Eleventy falla se publica igualmente lo que haya. Publicar de forma atómica (directorio nuevo + enlace simbólico, o `rsync --delete` tras comprobar el build). [E]
- [ ] 🟠 **La página de reserva se genera como `/.html` y `/es/.html`**: `pages/booking/booking.html.njk` usa `name: booking`, que no existe en `data/langs/*.json`; la cabecera enlaza a `/es/reserva.html`, que no existe (`header.html.njk:136,173`); y esas páginas acaban en el sitemap. [E]
- [ ] 🟠 **Marketing puede inyectar JavaScript en las webs públicas**: los textos `tag-others` y `meta` de `Marketing_Text` se insertan tal cual en todas las páginas (`head.html.njk:14,90`) y el markdown admite HTML. Es una vía prevista (etiquetas de terceros), pero conviene limitarla a perfiles de confianza. [E]
- [ ] 🟠 **Fallos de enlaces y datos**: enlaces relativos del pie que dan 404 desde las páginas de etiquetas del blog (`footer.html.njk:32-70`); teléfono vacío en el pie móvil (`o.Phones` frente a `Phone`, `:15`); enlaces sociales vacíos en el menú móvil (`header.html.njk:283-286`); el `noscript` de GTM usa el contenedor de Vanguard también en Cotown (`header.html.njk:4`); el botón de cerrar de la reserva siempre vuelve a la home en inglés (`booking.html.njk:31`). [E]
- [ ] 🟠 **Formularios**: muestran "enviado" aunque el servidor responda con error y no avisan si falla la conexión (`includes/shared/js/pipedrive.js:33-39`). [E]
- [ ] 🟠 **Disponibilidad de habitaciones en las páginas de ciudad de Barcelona**: la consulta de todos los edificios (`/availability/0/…`, que usan las páginas de ciudad de habitaciones y pisos, `location/*/main.html.njk:149,161`) solo cuenta habitaciones y plazas de Barcelona en residencias (`back/app/library/business/booking.py:730`: `d."Location_id" <> 1 OR b."Building_type_id" = 3`). Los edificios de co-sharing de Barcelona aparecen "agotados" en la página de ciudad aunque tengan plazas libres; en la página del edificio sí se ven. La regla de negocio es ofrecer pisos, habitaciones y plazas en todos los edificios (confirmado por Alejandro 2026-10-20): quitar la condición. [E]

### Data warehouse y ETL (back/etl)

- [ ] 🟠 **Duración de estancia mal clasificada en el DW**: `EXTRACT(MONTH FROM AGE(...))` ignora los años (13 meses → SHORT) en `sql/booking.sql:37`, `income_b2c_real.sql:13`, `income_b2c_otb.sql:14,62,114,158`, `mf_real.sql:15`, `mf_b2c_otb.sql:12` y `library/business/occupancy.py:92`. Afecta a los informes por duración (no a la facturación, que lo calcula bien). [E]
- [ ] 🟠 **Power BI puede leer tablas vacías o incompletas**: cada paso vacía la tabla y la recarga en transacciones separadas; si una consulta falla, la tabla queda sin ese bloque (p. ej. `income` sin B2C) y solo queda un error en el log; el proceso siempre termina con código 0 y no hay alertas ni bloqueo contra ejecuciones solapadas. Cargar en tablas temporales e intercambiar, devolver código de error y alertar. [E]
- [ ] 🟠 **El paso `general` vacía también los hechos**: `_clear_general.sql` hace `TRUNCATE … CASCADE` de `resource`, `owner` y `location`, lo que borra `resource_history`, `beds` y `occupancy`. En producción se recalculan en la misma ejecución, pero ejecutar `general` solo los deja vacíos. [E]
- [ ] 🟠 **Fallos de cálculo**: en `gold.beds` las valoraciones valen siempre 0 (`beds.py:216` las sobrescribe); solo se evalúa el primer bloqueo de cada recurso y el día 1 del mes (`beds.py:49-75`); la valoración "última" de `resource_history` no está ordenada por fecha (`history.py:35-37`); posible doble conteo de recursos con varias bajas (`history.py:142`); filas MPR perdidas en residencias (`income.py:269`); OTB de grupos con la renta del grupo imputada a cada habitación (`income_b2b_otb.sql:40-42`); ids que pueden colisionar al concatenar sin separador (`CONCAT('IBOR', bp.id, r.rid)`); management fee OTB desde 2024 mientras los ingresos OTB son desde hoy (`mf_*_otb.sql`); facturas LAU sin filtrar por emitidas (`income_lau_real.sql:39`). [I: verificar con datos]
- [ ] 🟠 **Datos personales en el DW**: `gold.booking` copia email, teléfonos y fecha de nacimiento de los clientes (`sql/booking.sql:13-16`) sin necesidad analítica evidente (RGPD). Seudonimizar o quitar. [E]

### Servicio de integración (API)

- [ ] 🟠 **Pipedrive con listas fijas en el código** (`library/services/pipedrive.py:33-149`): edificios (31 códigos), ciudades (4: falta Lisboa), tipologías, formularios, canales y marcas están mapeados a identificadores de opciones de Pipedrive. Un edificio, ciudad o tipología nuevos llegan al CRM sin ese dato hasta que se actualiza el código. Llevar el mapeo a una tabla de Airflows o resolverlo por nombre contra la API de Pipedrive. [E]
- [ ] 🟠 **`/pay/<id>` permite volver a pagar un cobro ya pagado** (no filtra `Payment_date IS NULL`, `queries.py:1175-1180`) y genera un número de pedido nuevo en cada llamada. [I]
- [ ] 🟠 **`/notify` no comprueba que `Ds_Order` coincida con el pedido** del cobro y, si el importe no cuadra, solo lo registra en el log (`api/payment.py:75-91`). [E]
- [ ] 🟠 **Número de pedido de Redsys de más de 12 caracteres** cuando el id del cobro o la secuencia superen 99.999 (`queries.py:1198`). [E]
- [ ] 🟠 **Descargas masivas mezcladas**: `/download/<name>` usa una carpeta `download/` compartida entre los 5 procesos; dos descargas simultáneas pueden mezclar o borrar ficheros (`business/download.py:25-47`). [E]
- [ ] 🟠 **Paso 1 del asistente de reserva** envía a `/booking/<lang>/2`, ruta inexistente (404) (`booking/es/step-1.html:27` y `en`). En la práctica se entra por el paso 2. [E]
- [ ] 🟠 **Reserva web sin sesión**: si no hay cliente en la sesión, `customer['id']` lanza un error 500 (`api/booking.py:509`). [E]
- [ ] 🟠 **Duplicados de reservas de piso completo no detectados**: la comprobación usa `"Place_type_id" = %s`, que nunca coincide con NULL (`business/booking.py:649`). Verificar además si en pisos completos se guarda bien `Flat_type_id` (`api/booking.py:512`). [I]
- [ ] 🟠 **Integración contable**: por defecto `payments` consulta un único día (2023-01-01); en `invoices` el comentario de cabecera recibe el de la línea (alias duplicado, `business/integration.py:300,306`); en `managementfees` la parte B2C no aplica el filtro de códigos (`:391-392`); el Swagger no coincide con los nombres reales (`invoice_id` frente a `code`, `direc_debit_*`, `comments` frente a `note`, `gross` repetido). [E]

### Procesos automáticos (back/app)

- [ ] 🟠 **Condición invertida en el envío de contratos B2B** (`contract.py:1288`): cuando el contrato de servicios existe, no se adjunta y se registra "no encontrado". [E]
- [ ] 🟠 **Contratos B2B sin plantilla se regeneran cada 15 min** (`contract.py:1257`: `json_rent != '{}'` siempre es cierto). [I]
- [ ] 🟠 **Riesgo de reenvío a DocuSign en B2C**: si falta la plantilla de renta pero se genera la de servicios, `Contract_rent` sigue vacío y la reserva se vuelve a procesar y enviar en cada ejecución. [I]
- [ ] 🟠 **Plantilla de email inexistente**: `send_email.py:86` devuelve 2 valores y `:241` desempaqueta 3 → `ValueError` y el email se reintenta para siempre. [E]
- [ ] 🟠 **Facturación de grupos** (`batch_billing.py:713-763`): las líneas de suministros, gastos y mobiliario están fuera del bucle por piso (solo se aplican al último); la línea de extras de renta está dentro de `if furniture > 0`; el cobro suma los extras sin multiplicar por plazas (`:601`, `:655`) y las líneas sí, así que cobro y factura no cuadran. [I]
- [ ] 🟠 **Resultado de carga engañoso** (`batch_processload.py:94-175`): `ok` se sobrescribe en cada hoja; si una hoja falla y la siguiente se ignora (p. ej. "Tarifas"), la carga queda como "Ok". [I]
- [ ] 🟠 **`pay_bills` no enlaza los cobros de facturas LAU manuales** con el contrato (`Booking_other_id`) (`batch_billing.py:1182-1197`). [I]
- [ ] 🟠 **La carga de "Inventario" borra toda la tabla** `Resource_inventory` aunque la hoja sea parcial (`load_inventory.py:17`); hoy no está conectada, pero si se reactiva es peligrosa. [E]
- [ ] 🟠 **Numeración de facturas sin bloqueo**: el trigger lee el contador de `Provider_bill` sin `FOR UPDATE`; emisiones simultáneas (proceso + Airflows) podrían duplicar un número. [I]
- [ ] 🟠 **Emails**: sin límite de reintentos; posible doble envío si `listen.py` y `batch_sendemail` procesan el mismo email a la vez; con `SMTPSEND` desactivado los emails se marcan como enviados; varias direcciones en `Cc`/`Cco` separadas por comas podrían enviarse como un solo destinatario (`send_email.py:133-152`). [I]
- [ ] 🟠 **printbill envía el email antes de guardar el PDF** (`print_bill.py:193-251`): si falla el guardado, se reenvía en la siguiente ejecución. [I]
- [ ] 🟠 **Contrato B2C en `pending` sin sobre**: si DocuSign falla tras generar el PDF, la reserva queda `pending` sin `Contract_id` y `checkcontract` no la revisa. [I]
- [ ] 🟠 **Email atascado que se reintenta para siempre**: desde al menos el 28/07/2026, cada ejecución de `batch_sendemail` (cada 15 min) falla con `list index out of range` en el mismo email (unos 1.300 errores por log rotado). Causa: `back/app/library/business/send_email.py:97-98` hace `result['data'][0]` sin comprobar que la consulta de la plantilla devuelva datos (la entidad referenciada ya no existe o no es visible). El email nunca se marca como enviado ni como erróneo. Corregir: comprobar la lista vacía y marcar el email como fallido (p. ej., con un campo de error), y localizar el registro de `Customer.Customer_email` afectado. [E, servidor 2026-10-20]
- [ ] 🟠 **Garantías retenidas sin factura**: la práctica es facturar lo retenido como servicios adicionales cobrados con el medio de pago *De la garantía* (informe *Devoluciones*). De las 792 reservas B2C finalizadas o en *devolver garantía* desde 2025 con `Deposit_returned` < `Deposit_actual`, 307 cuadran con esas facturas y 239 son origen de un cambio de habitación (garantía traspasada), pero **151 retienen sin ninguna factura** y el resto no cuadra. Según Alejandro (2026-10-20) la diferencia debe facturarse: revisar esos casos y valorar un control (aviso o bloqueo al pasar a *finalizada* si lo retenido no está facturado). Ídem en grupos. [E, BD 2026-10-21]
- [ ] 🟠 `Booking.Booking_B4_workflow.sql`: el email `descartadapagada` se envía **dos veces** (se ejecutan dos bloques IF). [E]
- [ ] 🟠 `Booking_group_service_B1_validate.sql`: condición `WHERE bg.id = 1` fija. [E]
- [ ] 🟠 `Booking_group_A1_create_prices.sql`: calcula `effective_billing_type` pero usa `NEW."Billing_type"`, así que ignora el tipo de facturación del último mes. [E]
- [ ] 🟠 Email `compis` en grupos: se envía al pagador del grupo y no a los residentes. [I]

### Código y datos a retirar – back

- [ ] 🟠 `function/Scripts.sql`: script destructivo de la migración (TRUNCATE de reservas, clientes y pagos). Retirar del repositorio. [E]

### Código y datos a retirar – Fuera de los repositorios

- [ ] 🟠 **El conector de Keycloak con Airflows (User Storage SPI) y el tema de inicio de sesión viven en `misc/core/keycloak`**, un repositorio de restos con un único commit. Es una pieza en producción (el portal del residente depende de ella): moverla a un repositorio propio o a `back`, con su proceso de construcción documentado. [E, confirmado por Alejandro 2026-10-20]

## 3. 🟢 Prioridad baja

### Seguridad

- [ ] 🟢 **Inyección HTML** en el email interno de aviso de leads: los campos del formulario se concatenan sin escapar (`business/send_email.py:217-220`). [E]
- [ ] 🟢 Sin límite de peticiones ni CAPTCHA en `/form` y `/booking` (solo honeypot y tiempo mínimo). [E]
- [ ] 🟢 **Puertos de monitorización** (3100, 9100, 8080, 9090, 3000) publicados en el host con `-p`; desde fuera no responden (los filtra Azure, comprobado 2026-10-20). Publicarlos solo en la red interna de Docker. [E]
- [ ] 🟢 **Traspasar los repositorios `front` y `webs`** de la cuenta personal `alejandro-andre` a la organización `Cotowngroup` (decidido el 2026-10-19). Después, actualizar el remoto en las copias locales y en el servidor (`~/www/webs`, que usa `gen.sh`) y revisar la clave de despliegue. [E]

### Operación e infraestructura

- [ ] 🟢 **Logs del ETL**: cada ejecución llena un fichero de 1 MB y se conservan 5, así que solo hay unas 10 horas de histórico. [E]
- [ ] 🟢 **Carga del libro mayor de SAP en el DW desactivada** (paso `gl` comentado en el crontab): temporal, el proyecto está en pausa (confirmado 2026-10-20). Al retomarlo, revisar los puntos del GL de la sección del data warehouse. [E]
- [ ] 🟢 **`webs/gen.sh` termina con `docker logs -f webgen`**, que no acaba hasta el siguiente `docker restart webgen` (como mucho 2 horas): siempre hay un proceso de cron colgado. Quitar el `-f` o redirigir a un log. [E, servidor 2026-10-20: un único proceso vivo]
- [ ] 🟢 **`~/config` del servidor de servicios desactualizado**: su `crontab` es de diciembre de 2024 y no coincide con el activo; hay copias `nginx.old` y `301.conf.old`. [E]
- [ ] 🟢 **Cortafuegos del sistema (`ufw`) inactivo** en `back` y `data`: hoy el filtrado depende solo del grupo de seguridad de Azure (los puertos de monitorización de `back` no responden desde fuera; el 5432 de `data`, sí: ver C9). [E]
- [ ] 🟢 **Disco de `core.cotown.com` al 70 %** (38 GB): vigilar crecimiento de la BD, documentos y logs de Airflows. [E]
- [ ] 🟢 **Imágenes sin uso en `data.cotown.com`** (`postgres:15-alpine`, `loki`, `node-exporter`, `cadvisor`): el servidor del DW no tiene monitorización activa. [E]
- [ ] 🟢 **Metabase en el servidor de Airflows** (`metabase/metabase:latest` en `core.cotown.com`): confirmar si se usa y para qué; si no, retirarlo. [E]
- [ ] 🟢 **Error de sintaxis en `back/config/pro/nginx.conf`**: falta `;` tras `server_name www.cotowngroup.com`. Comprobar la versión desplegada. [E]
- [ ] 🟢 **Nivel de log DEBUG en producción** (`LOGLEVEL=10`). [E]
- [ ] 🟢 **Clave `back/airflows.key.pem` con saltos de línea CRLF**: OpenSSH la rechaza tal cual. [E]
- [ ] 🟢 **Rol `readonly` de Postgres**: tiene un límite de 10 conexiones que se llegó a agotar, y no tiene política de seguridad por fila en las tablas de negocio (por ejemplo `Provider.Provider`), así que no ve filas. [E]

### Triggers de base de datos

- [ ] 🟢 **Inventario**: el fichero del repositorio `Resource_inventory_B1_validate.sql:11` tiene un carácter `·` que es error de sintaxis; el desplegado debe de ser otro. Sincronizar el repositorio con Airflows. [E]
- [ ] 🟢 **Medios de pago a depurar** (`Billing.Payment_method`, 21 valores): dos *Portal* duplicados (ids 5 y 48), *Paygold - Desactivado* (7), y significado por confirmar de *Portal - Pendiente*, *Garantía diferencia*, *Validación en curso* y *Domiciliación - Puiggali i Dosta*. Unificar duplicados, retirar los desactivados y documentar el uso de cada uno. [E, BD 2026-10-21]
- [ ] 🟢 **Recibos domiciliados devueltos sin registro**: un recibo devuelto simplemente no se marca como pagado; no queda constancia de la devolución ni del motivo, y el cobro vuelve a salir en el siguiente informe SEPA. Valorar registrar las devoluciones (fecha y motivo) y la marca de cobro incluido en remesa para no duplicarlo. [E]
- [ ] 🟢 **Factura emitida sin número si el proveedor no tiene patrón**: `Billing.Invoice_B2_validate.sql:150-180` hace `REPLACE` sobre un patrón NULL y deja `Code` vacío sin error (y consume el contador). Exigir el patrón al emitir. [E]
- [ ] 🟢 **Proveedor sin terminal de pago**: *NOVA CORSEGA IMMOBLES S.L.* no tiene TPV asignado (`Provider.Pos` vacío); el resto usa *delegado*, salvo Cotown y Vandor. Revisar si tiene recursos y asignarle el terminal. [E, BD 2026-10-21]
- [ ] 🟢 **Productos de renta y servicios del proveedor sin uso** (`Provider.Rent_product_id`, `Service_product_id`): ningún proceso los usa (la facturación usa productos fijos) y están vacíos en los 13 proveedores. Retirarlos o usarlos. [E, BD 2026-10-21]
- [ ] 🟢 **Plantillas de contrato**: el campo *Tipo de reserva* de la plantilla asignada (`Provider_template.Book_type`) no lo usa la selección de plantilla (`contract.py:981`), que solo mira tipo y ciudad; y la regla de plantilla activa única (`Provider_template_B1_active_contract.sql`) compara `Location_id = NEW."Location_id"`, que no desactiva otras plantillas genéricas (ciudad vacía). [E]
- [ ] 🟢 **Promociones**: el campo *Confirmar antes de* (`Billing.Promotion.Confirm_before`) no lo usa ninguna regla ni la web, y los campos de edificio y tipologías de la propia promoción (`Building_id`, `Flat_type_id`, `Place_type_id`) tampoco (se usan las listas `Promotion_building` y `Promotion_place`). Decidir si se implementa o se retira. [E]
- [ ] 🟢 **Suplemento de segundo residente sumado siempre** (latente: hoy todos los precios base desde 2026 tienen `Second_resident` = 0 y solo 2 reservas desde 09/2025 lo marcan; comprobado 2026-10-20): `Booking_B3_calc_prices.sql` suma a la renta (y a la base de la garantía mínima) el `Second_resident` del precio base sin mirar la casilla `Booking.Second_resident`. Si el precio base no tiene ese campo informado, la suma da NULL: la renta se queda con el valor anterior de la reserva o 0 y la garantía mínima no se calcula. Regla de negocio (Alejandro, 2026-10-20): sumarlo solo si la reserva tiene marcado segundo residente; tratar el NULL como 0. [I: verificar con un caso]
- [ ] 🟢 **Campo "Precio limpieza" del precio base sin uso** (`Pricing_detail.Cleaning_price`): solo aparece en la carga y el informe de Precios. Retirarlo. [E]
- [ ] 🟢 Cálculo de precios: la garantía solo sube, nunca baja, al cambiar de recurso; en EXT no se regenera el mes en curso, que estaba prorrateado (`Booking_B3_calc_prices.sql:235, 109-113`). (Que la tarifa sustituya la renta manual y que el % de promoción se aplique a renta y servicios es intencionado.) [I]
- [ ] 🟢 La fianza INCASÒL se calcula una sola vez y no se recalcula al cambiar recurso o renta (`Booking_B3_incasol.sql:12`, `Booking_group_B2_incasol.sql:11`). [E]
- [ ] 🟢 Emails programados con condiciones que excluyen casos por NULL (`Check_in_notice_ok`, `Contract_status`, `Check_in_keyless_ok`) y avisos a compañeros que no incluyen reservas en `contrato` sin fecha de check-in (`Booking_CRON_notice_emails.sql:15`, `Booking_CRON_contract_emails.sql:16`, `Booking_B5_buttons.sql:30`). [I]
- [ ] 🟢 El emparejamiento por prefijo de código para bloquear padres e hijos puede casar códigos no relacionados (`X.1` con `X.10`) (`Booking_A2_update_availability.sql:11-12`). [I]
- [ ] 🟢 `Resource_CRON_status.sql:14`: con varias disponibilidades solapadas hoy, el estado elegido es aleatorio. `Resource_CRON_history`: con `Multiplier` NULL todos los precios quedan NULL. [I]
- [ ] 🟢 Validaciones con mensajes en inglés y español que no dicen lo mismo, o que contradicen la condición (`validate_NIF_NIE.sql:14,17`, `Resource_inventory_B1_validate.sql:8`, `Resource_availability_B1_validate.sql:29-30`); el NIE no valida la letra de control. [E]

### Frontends (front/cotown y front/customer)

- [ ] 🟢 **Portal – detalles**: los emails `@cotown.com` ven siempre el botón Pagar (`myPayments.component.ts:66`); datos personales en la consola del navegador (`customer.service.ts:36`, `myDocuments.component.ts:68`, `myPayments.component.ts:103`); claves de traducción inexistentes (`unknown_error`, `check_out_no_options`); formatos de hora `HH:MM:SS` erróneos; el teléfono del enlace no coincide con el mostrado (`layout.component.html:9,14`); las fotos de los cuestionarios se suben como foto del cliente 0 (`axios-api.service.ts:36`); los PDF internos los ven todos los clientes sin filtrar por edificio. [E]
- [ ] 🟢 **Portal – rutas**: los imports `paymentOK`/`paymentKO` no coinciden en mayúsculas con los ficheros: compila en Windows pero fallaría en Linux o CI (`customer-routing.module.ts:20-21`). [E]
- [ ] 🟢 **Backoffice – detalles**: guarda `"undefined"` como token si no llega (`app.component.ts:161`); columnas vacías por erratas (`general.component.ts:145`, `lau.component.ts:71,190`); columnas desalineadas en LAU (`lau.component.html:425-427`); `postMessage` a cualquier origen (`planning.component.ts:226,237`). [E]
- [ ] 🟢 **Angular 15 sin soporte** desde noviembre de 2023, en los dos frontends; sin tests; sin script de despliegue versionado; `environment.ts` del backoffice marca `production: true` con hosts de desarrollo. [E]

### Webs comerciales (webs/code)

- [ ] 🟢 **SEO**: `og:title`/`twitter:title` sin sustituir `{city}`, `og:url` siempre a la home, `og:site_name` "Cotown" también en Vanguard, `og:image` = "TBD" (`head.html.njk:36-44`, `globals.js:12,22`); JSON-LD de los posts con doble barra y sin escapar comillas (`post.html.njk:11`); sin JSON-LD de organización, alojamiento o FAQ; `llms.txt` escrito a mano, desactualizado y con un enlace roto (`/es/conocenos.html`). [E]
- [ ] 🟢 **Rendimiento y robustez del build**: unos 60–70 logins GraphQL por build (`data/graphql.js:10,15` llama dos veces a `token()`); sin caché de datos; sin control de errores en `graphql.js`, `sql.js` y `unlocked.js`; `docker restart` en `gen.sh` interrumpe un build en curso; los borradores no se generan (cron comentado) y se sirven sin autenticación. [E]
- [ ] 🟢 **Colisiones posibles**: posts, residencias y páginas fijas comparten carpeta (un slug repetido rompe el build); las imágenes se nombran por `slugify(nombre)` y dos con el mismo nombre se pisan (`config/.base.js:276-278`). [I]
- [ ] 🟢 El forzado de `SAR326` como residencia está en el código (`data/buildings*.js:96-100`) pero no en `residences.js`: la home podría enlazar a una página que no se genera. Mejor marcarlo en Airflows. [I]
- [ ] 🟢 **Publicación solo por cron** (cada 2 h, de 8 a 21 h): un cambio en Airflows tarda hasta 2 h en verse, y por la noche no se publica nada. Valorar un botón o webhook de publicación desde Airflows. [E]
- [ ] 🟢 Leaflet desde unpkg sin SRI (`contact.html.njk:32`, `location/*/main.html.njk:11`); `node:18` sin soporte en el `Dockerfile`; dependencias y código sin uso (`lunr`, `uncss`, `team.js`, `book.js`, `calendar.html.njk`, `icons/`). [E]

### Data warehouse y ETL (back/etl)

- [ ] 🟢 **El ETL abre la BD de Airflows con permiso de escritura** (`etl.py:68`) solo para marcar el parámetro `COPY_STABILISED`. [E]
- [ ] 🟢 **Dos fuentes de forecast conviven**: el Excel "Forecast" de Airflows (marcado "TO BE REMOVED?", `etl.py:168-169`) y `Resource_forecast`. Decidir cuál queda. [E]
- [ ] 🟢 **Rendimiento**: `beds_real_calc` se calcula 3 veces por ejecución y los cálculos son fila a fila con pandas; no se mide la duración. [E]
- [ ] 🟢 **El histórico del libro mayor de SAP vive solo en CSV del servidor** (`csv/CTS00-*.csv`); `gold.gl` se recarga desde ellos. Sin paginación en la consulta OData (`$top=999999`). [E]
- [ ] 🟢 Sin vistas ni usuario de solo lectura para Power BI (lee las tablas de `gold` con el usuario del ETL); `gold.date` solo cubre 2024-2030 y su `yearweek` no es ISO (`_init.sql:59,71`). [E]

### Power BI

- [ ] 🟢 **Tabla de fechas automática activada** en el modelo central: 34 tablas `LocalDateTable_*` ocultas que aumentan el tamaño del modelo (63 MB). Desactivar *Fecha y hora automáticas* y usar solo la dimensión `date`. [E]
- [ ] 🟢 **Informe Profiling con 91 páginas**, varias duplicadas ("Duplicate of …") y otras con nombres provisionales ("Page 3", "%", "#"). Depurar. [E]
- [ ] 🟢 **Medidas RevPOB y RevPAB**: la rama "Real" de la fórmula incluye OTB y Tentative, aunque no está en el selector (sin efecto hoy); limpiar para evitar confusiones. [E]
- [ ] 🟢 **Gráfico de terceros "Zebra BI Tables"** en el informe SGR: comprobar licencia. [E]

### Servicio de integración (API)

- [ ] 🟢 `/iban` devuelve un objeto de excepción (error 500) (`misc.py:126`); `/swift` compara el builtin `str` en lugar de `code` (`misc.py:133`). [E]
- [ ] 🟢 `/report/<status>` y `/export/<name>` dan error 500 con nombres sin plantilla (`export.py:160`, fichero que no se cierra). [E]
- [ ] 🟢 El webhook de DocuSign da error 500 si falta `event` en el JSON (`api/contract.py`). [E]
- [ ] 🟢 Las respuestas JSON de dashboards y datos web se sirven como texto (`json.dumps` en lugar de `jsonify`). [E]
- [ ] 🟢 Código duplicado: conversión de la query string (`api/airflows.py`, 4 veces), lógica de promociones (4 funciones), validación de Api-Key y fecha (4 endpoints). [E]
- [ ] 🟢 Swagger solo documenta las 4 rutas de integración. [E]

### Procesos automáticos (back/app)

- [ ] 🟢 **Webhook de DocuSign solo actualiza reservas B2C**: grupos y anexos dependen de la comprobación diaria. [E]
- [ ] 🟢 **Anexos de Barcelona en B2B**: solo se anexan los documentos del primer recurso (`contract.py:968`). [I]
- [ ] 🟢 `batch_sharepoint.py:99`: `item['Lines'][0]` cae si una factura no tiene líneas. [I]
- [ ] 🟢 `batch_law.py`: sin control de errores (un fallo aborta todo); `KeyError` si un recurso no tiene código de edificio (`:175`); asignación muerta (`:195`); ubicación 4 (Bilbao) fija en el código (`:178`). [E]
- [ ] 🟢 `checkcontract` consulta cada día, para siempre, los sobres rechazados y caducados y pide un token por sobre. [E]
- [ ] 🟢 Logs cruzados: `batch_checkcontract` escribe en `batch_printcontract.log`; `listen.py` solo en la salida de Docker. [E]
- [ ] 🟢 Erratas en logs y mensajes: "LAU inloices" (`batch_billing.py:1376`), "desconcida" (`batch_processload.py`). [E]
- [ ] 🟢 El token de Airflows viaja en la URL al subir documentos (`print_bill.py:186`, `contract.py:1085`). [E]
- [ ] 🟢 Estado `documentacionko`: Operaciones lo gestiona a mano (confirmado); falta darle color en el backoffice y quizá un dashboard que liste estas reservas. [E]
- [ ] 🟢 Carácter "·" tras `"Request_date"` en `Booking_B2_validate.sql` y tras `"Purchase_date"` en `Resource_inventory_B1_validate.sql`. [E]
- [ ] 🟢 Medio de pago 2: se llama "transferencia" en `batch_billing.py` y "SEPA/remesa" en los informes. Unificar. [E]

### Código y datos a retirar – back

- [ ] 🟢 `app/library/services/olddbclient.py`: cliente de BD antiguo; no se importa. [E]
- [ ] 🟢 `app/library/services/keycloak.py`, `cipher.py`: no se importan. [E]
- [ ] 🟢 `app/library/services/ac.py`: ActiveCampaign, sustituido por Pipedrive; no se importa. [E]
- [ ] 🟢 Informe Excel **ActiveCampaign** (`app/templates/report/ac.*` y su entrada en `front/cotown/src/app/pages/reports/reports.component.ts:36`): obsoleto (confirmado por Alejandro 2026-10-21). Retirarlo. [E]
- [ ] 🟢 `function/Customer.Customer_D2_delete_keycloak_user.py`, `Provider.Provider_A2_create_keycloak_user.py`, `Provider.Provider_D2_delete_keycloak_user.py`: llaman a rutas que no existen y no están desplegados en Airflows. [E, BD 2026-10-20]
- [ ] 🟢 `function/Resource.Resource_B2_history.sql`: no está desplegado en Airflows. [E, BD 2026-10-20]
- [ ] 🟢 `function/Billing.Invoice_line_CRON_management_fee.sql`: no tiene programación, nunca se ejecuta (pone a NULL los management fees del mes; el trigger `Invoice_line_B1_change` los recalcularía en el mismo UPDATE). [E, BD 2026-10-20]
- [ ] 🟢 Funciones `create_airflows_user`, `delete_airflows_user`, `get_provider`, `get_customer` en `app/library/business/queries.py`: sin uso. [I]
- [ ] 🟢 Import `q_change_contract` en `app/library/api/misc.py`: sin uso. [E]
- [ ] 🟢 `app/library/business/load_inventory.py`: no se importa. [E]
- [ ] 🟢 `app/batch_weights.py`: **funcionalidad futura no implementada** (cálculo automático de pesos de habitaciones y plazas a partir de los precios). Hoy solo simula: registra los UPDATE sin ejecutarlos, tiene un código de depuración fijo (`BLM335`) y escribe en `batch_law.log`. No se documenta en la base de conocimiento. [E, confirmado por Alejandro 2026-10-20]
- [ ] 🟢 `app/docusign/`: prototipo de DocuSign; la lógica real está en `business/contract.py`. [I]
- [ ] 🟢 `app/test.py`, `test.ps1`, `md.py`, `oid.py`, `contracts/test/*.pdf`: herramientas puntuales y artefactos de prueba. [I]
- [ ] 🟢 `app/templates/report/*.graphql.old`, `oldforecast.*`: plantillas de informe sustituidas. [E]
- [ ] 🟢 `config/pro/301.conf.old 1`, `301.conf.old 2`, `301.conf.old.3`: versiones antiguas de las redirecciones. [E]
- [ ] 🟢 `config/dev/*`: desfasado (Python 3.9, sin monitorización) y no hay servidor de desarrollo desplegado. [E]
- [ ] 🟢 `misc/syncronizer old.sql`, `syncronizer new.sql`: copias de la función de plataforma `Models.synchronizer()`. [E]
- [ ] 🟢 `etl/sap.py`: script exploratorio; la lógica real está en `library/business/gl.py`. [I]
- [ ] 🟢 `etl/csv/*`: datos y copias de seguridad dentro del repositorio. [E]

### Código y datos a retirar – webs

- [ ] 🟢 `upload/upload.py`: utilidad puntual solo para Windows (además, con contraseña en el código). [I]
- [ ] 🟢 `code/src/icons.zip`: artefacto. [I]
- [ ] 🟢 Comentarios `// remove` en `code/config/.cotown*.js`: passthrough de CSS pendiente de quitar. [E]
- [ ] 🟢 Errata de host `back.cotown.oimbra.tecg` (comentada) en `code/src/data/constants.js`. [E]

### Código y datos a retirar – front

- [ ] 🟢 `customer/test.html`: fichero de prueba. [I]

### Código y datos a retirar – Modelo de datos (Airflows)

- [ ] 🟢 Entidades sin uso: `Booking.Booking_search` y `Marketing.Contact` (marcadas "FUTURO"), `Customer.Customer_status` y `Customer.Customer_resident_status` (marcadas "BORRAR"), `Marketing.Media_country` y `Marketing.Media_province` (marcadas "No usar"). Se documentan como "sin uso"; decidir si se eliminan. [E]

### Código y datos a retirar – Fuera de los repositorios

- [ ] 🟢 `misc/`: pruebas de concepto, espejo de WordPress (`facultades`, 21 MB) y otros restos. [E]
