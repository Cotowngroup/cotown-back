# IT-10. Infraestructura, operación y monitorización

> Manual técnico · Borrador v0.1 · 2026-10-20 · Las marcas **[PREGUNTA Tn]** se resuelven en la ronda de preguntas y desaparecen de la versión final.

## 10.1 Propósito

Este capítulo describe la infraestructura sobre la que funciona el sistema: los servidores y lo que se ejecuta en cada uno, los dominios y certificados, la configuración por entornos, cómo se registran y consultan los logs y las métricas, las copias de seguridad y cómo llegan los cambios a producción. Es descriptivo: los procedimientos de operación los realiza Oimbra.

## 10.2 Servidores

| Servidor | Proveedor | Sistema | Recursos | Qué ejecuta |
|---|---|---|---|---|
| `core.cotown.com` | Hetzner | Ubuntu 24.04 | 4 vCPU, 15 GB RAM, 38 GB de disco | Airflows (plataforma 2.1, con su PostgreSQL 15 y Keycloak 21.1) y el backoffice complementario. El servidor y la plataforma (actualizaciones, disponibilidad) los gestiona el proveedor de Airflows; Oimbra carga las funciones y la configuración de Cotown. |
| `back.cotown.com` | Azure | Ubuntu 26.04 | 2 vCPU, 7,7 GB RAM, 29 GB de disco | Servidor de servicios: nginx, servicio de integración y procesos automáticos (`back`), generador de webs (`webgen`) y monitorización. |
| `data.cotown.com` | Azure | Ubuntu 26.04 | 2 vCPU, 7,7 GB RAM, 29 GB de disco | Data warehouse (PostgreSQL 16) y su proceso de carga. Acceso SSH por un puerto no estándar. |

Todo el software propio se ejecuta en contenedores Docker. Los tres servidores tienen cortafuegos activo.

### Contenedores del servidor de servicios

| Contenedor | Imagen | Función |
|---|---|---|
| `nginx` | nginx | Servidor web y proxy inverso, HTTPS. |
| `back` | Propia (`cotown`, Python 3.12) | Servicio de integración (gunicorn, 5 procesos), escucha de emails y procesos automáticos. |
| `webgen` | Propia (`11ty`, Node 18) | Generación de las webs comerciales. |
| `loki`, `promtail` | Grafana Loki y Promtail | Recogida y almacenamiento de logs. |
| `prometheus`, `nodexp`, `cadvisor` | Prometheus, node-exporter, cAdvisor | Métricas del servidor y de los contenedores. |
| `grafana` | Grafana | Consulta de logs y métricas. |

Todos comparten una red interna de Docker (`cotownnet`). El código y la configuración del servicio se montan desde el servidor (`~/app`), así que un cambio de código no exige reconstruir la imagen.

## 10.3 Dominios y certificados

| Dominio | Servidor | Contenido |
|---|---|---|
| `core.cotown.com` | core | Airflows (ERP, API GraphQL, ficheros, Keycloak) y backoffice complementario (`/cotown`). |
| `cotown.com` (y `www`) | back | Web comercial de Cotown y asistente de reserva. |
| `vanguard-student-housing.com` (y `www`) | back | Web comercial de Vanguard y asistente de reserva. |
| `www.cotowngroup.com` (y raíz) | back | Portal del residente (`/customer`). |
| `back.cotown.com` | back | API (`/api/v1`), asistente de reserva (`/booking`), Grafana (`/grafana`) y borradores de las webs. |
| `data.cotown.com` | data | Acceso SSH al data warehouse (sin web). |

En el servidor de servicios, los certificados HTTPS son de Let's Encrypt y los renueva automáticamente certbot (temporizador del sistema, dos veces al día). nginx redirige HTTP a HTTPS y las variantes con y sin `www` a la principal, y aplica las redirecciones 301 de URL antiguas de las webs.

Los dominios y el DNS los gestiona el departamento de IT de Cotown.

## 10.4 Configuración y entornos

- **Servicio de integración y procesos**: ficheros de configuración por entorno (Dynaconf), separados en parámetros y secretos; la variable `COTOWN_ENV` elige el entorno (`production` en el servidor). Incluyen las direcciones de Airflows, de la base de datos y de los servicios externos, los indicadores que activan o desactivan envíos (email, DocuSign, CRM) y las fechas de corte de facturación y contratos.
- **Data warehouse**: ficheros equivalentes en `~/etl`.
- **Webs**: configuración por sitio en `webs/code/config`.
- **Frontends**: ficheros `environment*.ts`, que se fijan al construir la aplicación.
- **Entorno de desarrollo**: Airflows de desarrollo en `cotown-dev.flows.ninja`; el resto se ejecuta en local.

## 10.5 Logs y monitorización

### Dónde están los logs

| Componente | Dónde |
|---|---|
| Servicio de integración y escucha de emails | Salida del contenedor `back`, recogida por Loki. |
| Procesos automáticos | Ficheros `~/app/log/batch_<proceso>.log` del servidor de servicios (rotan a 1 MB, se conservan 5), recogidos por Promtail hacia Loki. |
| Generador de webs | Salida del contenedor `webgen`, recogida por Loki. |
| Copia a SharePoint | `~/app/log/sharepoint.log`. |
| Data warehouse | `~/etl/log/etl.log` en `data.cotown.com` (rota a 1 MB; unas 10 horas de histórico). |
| Airflows | En su propio servidor, a cargo del proveedor. |

Todos los logs propios usan el mismo formato: fecha y hora, componente, función y línea, nivel y mensaje. Cada proceso automático registra al final cuántos elementos ha tratado.

### Grafana

Grafana está publicado en `https://back.cotown.com/grafana`. Permite:

- Consultar los logs del servicio, de los procesos y del generador de webs (fuente Loki), filtrando por contenedor o proceso y por texto.
- Ver las métricas del servidor de servicios (CPU, memoria, disco, red) y de cada contenedor (fuente Prometheus).

No hay alertas configuradas: la supervisión la hace Oimbra consultando Grafana y los logs, de forma periódica o cuando Cotown avisa de una incidencia. Está previsto automatizarla.

## 10.6 Copias de seguridad

| Componente | Copia |
|---|---|
| Base de datos de Airflows | Copia base de PostgreSQL con recuperación a un instante concreto (*point-in-time recovery*, PITR), en el propio servidor. No hay copia externa; está previsto automatizarla. |
| Data warehouse | Sin copia: se reconstruye entero desde Airflows con el ETL. Las únicas excepciones son las fotos del Business Plan y el histórico del libro mayor de SAP, que se guardan como ficheros en el servidor. |
| Código | En GitHub. |
| Configuración de los servidores de Azure | En los propios servidores (ficheros de configuración, `crontab`, certificados). |

## 10.7 Cómo llegan los cambios a producción

| Componente | Cómo se despliega |
|---|---|
| Reglas de negocio (triggers) | Se cargan en Airflows, que crea o actualiza los triggers (ver *Arquitectura*). |
| Modelo de datos, pantallas, menús, plantillas de email | Se configuran en Airflows. |
| Servicio de integración y procesos | El código se actualiza en `~/app` del servidor de servicios y se reinicia el contenedor `back`. |
| Webs comerciales | Automático: cada generación descarga la última versión del repositorio. |
| Backoffice complementario | Se construye y se copia al servidor de Airflows. |
| Portal del residente | Se construye y se copia a `~/www/sites/cotowngroup/customer` (se conserva la versión anterior). |
| Data warehouse | El código se actualiza en `~/etl` de `data.cotown.com`. |

El código fuente está en GitHub, en la organización `Cotowngroup`. Los despliegues los realiza Oimbra.

## 10.8 Fuentes

| Tema | Dónde está |
|---|---|
| Contenedores, red y volúmenes | `back/config/pro/makefile` |
| nginx y redirecciones | `back/config/pro/nginx.conf`, `back/config/pro/301.conf` |
| Monitorización | `back/config/pro/prometheus.yml`, `promtail-config.yaml`, `grafana.ini` |
| Programación de procesos | `crontab` del usuario `cotown` en `back.cotown.com` y `data.cotown.com` |

## 10.9 Pendiente de confirmar

No hay puntos pendientes.
