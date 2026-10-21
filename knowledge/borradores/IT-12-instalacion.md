# IT-12. Instalación

> Manual técnico · Borrador v0.1 · 2026-10-20 · Las marcas **[PREGUNTA Tn]** se resuelven en la ronda de preguntas y desaparecen de la versión final.

## 12.1 Propósito

Este capítulo describe cómo está instalado el sistema en cada servidor, tal como estaba el 20 de octubre de 2026: usuarios, carpetas, ficheros de configuración, scripts, tareas programadas, contenedores, redes, volúmenes, puertos, certificados y logs. Sirve como mapa para localizar cualquier pieza en producción. Las credenciales no se incluyen; están en el documento de secretos, que se entrega aparte.

## 12.2 Servidor de servicios (`back.cotown.com`)

Máquina virtual de Azure con Ubuntu 26.04, Docker 28 y acceso SSH por el puerto estándar con clave. Todo se instala bajo el usuario **`cotown`** (`/home/cotown`).

### Carpetas

| Ruta | Contenido |
|---|---|
| `~/app/` | Código del servicio de integración y de los procesos automáticos (copia del repositorio `cotown-back`, carpeta `app/`). Se monta en el contenedor `back`. |
| `~/app/.settings.toml`, `~/app/.secrets.toml` | Configuración del servicio (parámetros y secretos), por entorno. |
| `~/app/library/`, `templates/`, `booking/`, `assets/` | Lógica, plantillas de PDF e informes, asistente de reserva y sus recursos. |
| `~/app/start.sh` | Arranque del contenedor `back`. |
| `~/app/dobatch.sh` | Lanzador de los procesos automáticos desde el `crontab`. |
| `~/app/log/` | Logs de los procesos automáticos (`batch_*.log`) y de la copia a SharePoint. |
| `~/app/download/` | Carpeta temporal de las descargas masivas (ZIP). |
| `~/app/sharepoint/` | Archivo de facturas y recibos que se copia a SharePoint. |
| `~/config/` | Configuración de la infraestructura: `makefile` (definición de contenedores), `nginx.conf`, `301.conf` (redirecciones), `Dockerfile` y `requirements.txt` del contenedor `back`, `grafana.ini`, `prometheus.yml`, `promtail-config.yaml`. |
| `~/www/webs/` | Clon del repositorio `cotown-webs` (rama `main`), que actualiza la generación de las webs. Incluye `gen.sh`. |
| `~/www/sites/` | Webs publicadas que sirve nginx: `cotown/`, `vanguard/`, `cotowngroup/` (redirección y portal del residente en `customer/`, con la versión anterior en `customer-old/`) y las carpetas de trabajo `cotown-publish/` y `vanguard-publish/`. |
| `~/www/certs/` | Carpeta auxiliar de certificados. |
| `/etc/letsencrypt/` | Certificados HTTPS de Let's Encrypt de todos los dominios. |

### Scripts

| Script | Qué hace |
|---|---|
| `~/app/start.sh` | Arranca la escucha de emails (`listen.py`) en segundo plano y el servicio de integración (gunicorn, 5 procesos, puerto 5000, tiempo máximo 240 s). |
| `~/app/dobatch.sh <proceso>` | Comprueba que el proceso no esté ya en marcha (fichero `/tmp/batch_<proceso>.lock`), ejecuta `docker exec back python3 batch_<proceso>.py` y borra el bloqueo al terminar. |
| `~/www/webs/gen.sh <publish\|draft> <marca> [rama]` | Actualiza el clon de las webs (`git pull`), reinicia el contenedor `webgen` y ejecuta dentro la generación (`config/publish.sh` o `config/draft.sh`). |
| `config/publish.sh <marca>` (en `webgen`) | Limpia la caché de imágenes de más de 2 horas, genera la web en `sites/<marca>-publish` y copia a `sites/<marca>` solo los ficheros que han cambiado. |

### Tareas programadas (`crontab` del usuario `cotown`)

| Programación | Tarea |
|---|---|
| `00,15,30,45 * * * *` | `dobatch.sh billing` – facturación |
| `03,18,33,48 * * * *` | `dobatch.sh printbill` – PDF de facturas |
| `06,21,36,51 * * * *` | `dobatch.sh printcontract` – contratos |
| `09,24,39,54 * * * *` | `dobatch.sh processload` – cargas de Excel |
| `12,27,42,57 * * * *` | `dobatch.sh sendemail` – emails pendientes |
| `0 1 * * *` | `dobatch.sh checkcontract` – estado de contratos en DocuSign |
| `0 2 * * *` | `dobatch.sh sharepoint` – archivo de facturas |
| `30 2 * * *` | `rclone copy ~/app/sharepoint` → SharePoint |
| `0 3 * * *` | Borrado de bloqueos huérfanos (`/tmp/batch*.lock`) |
| `0 5 * * *` | `dobatch.sh law` – rentas máximas |
| `0 8-20/2 * * *` | `gen.sh publish vanguard` |
| `0 9-21/2 * * *` | `gen.sh publish cotown` |

Además, el sistema renueva los certificados con el temporizador de certbot (`snap.certbot.renew.timer`).

### Contenedores

Todos en la red de Docker `cotownnet`, salvo `cadvisor` (red `bridge`). Los logs de `back` y `webgen` van directamente a Loki (controlador de logs `lokidriver`); el resto, al controlador por defecto de Docker (máximo 3 ficheros de 50 MB).

| Contenedor | Imagen | Puertos publicados | Volúmenes | Reinicio automático |
|---|---|---|---|---|
| `nginx` | `nginx` | 80, 443 | `~/config/nginx.conf` y `301.conf` (solo lectura), `~/www/sites` (solo lectura), `/etc/letsencrypt` | No |
| `back` | `cotown` (propia: Python 3.12 + WeasyPrint) | — (5000 interno) | `~/app` → `/app` | Sí |
| `webgen` | `11ty` (propia: Node 18 + Eleventy) | — | `~/www/webs/code/src`, `~/www/webs/code/config`, `~/www/sites` | No |
| `loki` | `grafana/loki` | 3100 | Volumen `loki-data` | No |
| `promtail` | `grafana/promtail` | — | `~/config`, `~/app/log` | No |
| `prometheus` | `prom/prometheus` | 9090 | `~/config/prometheus.yml`, volumen `prometheus-data` | No |
| `nodexp` | `node-exporter` | 9100 | Sistema de ficheros del host (solo lectura) | No |
| `cadvisor` | `cadvisor` | 8080 | Sistema del host (solo lectura) | No |
| `grafana` | `grafana/grafana` | 3000 | `~/config/grafana.ini`, volumen `grafana-data` | No |

Los puertos de monitorización (3000, 3100, 8080, 9090, 9100) no son accesibles desde Internet: los filtra el grupo de seguridad de Azure. Grafana se publica a través de nginx en `https://back.cotown.com/grafana`.

Los contenedores se crean con las instrucciones de `~/config/makefile` (una regla por contenedor).

### Servidor web (nginx)

| Sitio | Configuración |
|---|---|
| `cotown.com` | Sirve `~/www/sites/cotown`; `/booking` y `/assets` al contenedor `back`. `www` y HTTP redirigen a `https://cotown.com`. Aplica las redirecciones 301. |
| `vanguard-student-housing.com` | Igual, con `~/www/sites/vanguard`. |
| `www.cotowngroup.com` | Sirve `~/www/sites/cotowngroup` (portal en `/customer`). La raíz sin `www` redirige. |
| `back.cotown.com` | `/api` y `/booking` al contenedor `back`; `/grafana` al contenedor `grafana`; `/cotown` y `/vanguard`, borradores de las webs; `/`, copia de la web de Cotown. |

Todos los sitios aplican HSTS y una política de seguridad de contenidos (CSP).

### Otros servicios del sistema

- **Agente de Azure** (`walinuxagent`) y Docker.

## 12.3 Servidor del data warehouse (`data.cotown.com`)

Máquina virtual de Azure con Ubuntu 26.04 y Docker 28. Acceso SSH con clave por el puerto **23141**. Todo bajo el usuario **`cotown`**.

### Carpetas

| Ruta | Contenido |
|---|---|
| `~/etl/` | Proceso de carga (copia de `cotown-back`, carpeta `etl/`): `etl.py`, `library/`, `sql/`, `copy.sh`, `tunnel`. |
| `~/etl/.settings.toml`, `~/etl/.secrets.toml` | Configuración del ETL. |
| `~/etl/venv/` | Entorno Python del ETL. |
| `~/etl/csv/` | Ficheros intermedios de la carga, fotos del Business Plan (subcarpetas con fecha) e histórico del libro mayor de SAP. |
| `~/etl/log/` | Log del ETL (`etl.log`, rota a 1 MB, 5 copias). |
| `~/data/postgres/` | Datos de la base de datos del data warehouse (volumen del contenedor). |
| `~/certs/` | Certificado TLS de `data.cotown.com` para PostgreSQL, copiado de Let's Encrypt con `~/certs/renew.sh` (copia y reinicia el contenedor). Caduca el 09/01/2027. |
| `~/config/makefile` | Definición del contenedor. |

### Tareas programadas (`crontab` del usuario `cotown`)

| Programación | Tarea |
|---|---|
| `0 3,7-17/2 * * *` | `etl.py --steps general income history beds occupancy booking` |
| `0 4 * * *` | `docker restart postgres` |
| *(comentada)* | `etl.py --steps gl` (libro mayor de SAP) |

### Contenedor

| Contenedor | Imagen | Puerto | Volúmenes | Reinicio automático |
|---|---|---|---|---|
| `postgres` | `postgres:16-alpine` | 5432 (con SSL) | `~/data/postgres`, `~/certs` | Sí |

La base de datos es `dw` y el esquema, `gold`. La puerta de enlace de Power BI se conecta directamente al puerto 5432.

## 12.4 Servidor de Airflows (`core.cotown.com`)

Máquina de Hetzner con Ubuntu 24.04, 4 vCPU y 15 GB de RAM, gestionada por el proveedor de Airflows. Contenedores principales:

| Componente | Imagen |
|---|---|
| Plataforma Airflows (ERP, API GraphQL, ficheros, backoffice complementario) | `airflows/platform` (versión 2.1) |
| Base de datos `niledb` | `niledb/postgres:15` |
| Keycloak | `keycloak:21.1.1` |
| Otros componentes de la plataforma | Metabase, AutoML, monitorización |

Oimbra accede con un usuario SSH limitado (`partner`), que solo se usa para el túnel hacia la base de datos.

## 12.5 Repositorios frente a producción

| Componente | En producción | Relación con el repositorio |
|---|---|---|
| Servicio de integración y procesos | `back.cotown.com:~/app` | Copia manual (no es un clon de git). |
| Configuración de infraestructura | `back.cotown.com:~/config` | Copia; el `crontab` activo es distinto del guardado. |
| Webs comerciales | `back.cotown.com:~/www/webs` | Clon de git (`main`), actualizado en cada generación. |
| Portal del residente | `back.cotown.com:~/www/sites/cotowngroup/customer` | Versión construida y copiada a mano. |
| Backoffice complementario | `core.cotown.com/cotown` | Versión construida y copiada a mano. |
| ETL | `data.cotown.com:~/etl` | Copia manual. |
| Funciones de la base de datos | Airflows | Cargadas a mano desde `back/function`. |

## 12.6 Pendiente de confirmar

Se rellena tras la ronda de preguntas.
