# IT-7. Webs comerciales

> Manual técnico · Borrador v0.1 · 2026-10-20 · Las marcas **[PREGUNTA Tn]** se resuelven en la ronda de preguntas y desaparecen de la versión final.

## 7.1 Propósito

Este capítulo describe cómo están construidas y cómo se publican las webs comerciales de las dos marcas, **cotown.com** y **vanguard-student-housing.com**: de dónde salen sus contenidos y sus datos, qué páginas se generan, qué hacen en el navegador del visitante y qué contenidos se gestionan desde Airflows.

## 7.2 Planteamiento

Las webs son **sitios estáticos** generados con **Eleventy** (plantillas Nunjucks) a partir de los datos de Airflows. Cada 2 horas se regeneran y se publican los ficheros HTML resultantes, que sirve el servidor web. Así las páginas cargan rápido, no dependen de que Airflows esté disponible en el momento de la visita y solo hacen consultas en vivo para la disponibilidad, los formularios y la reserva.

Un mismo código produce las dos webs: cada página sabe para qué marca se genera (variable `site`: `cotown` o `vanguard`) y filtra los datos por su segmento (Vanguard = 1, Cotown = 2). Lo específico de cada marca (colores, logos, etiquetas de analítica, algunas secciones) está en carpetas propias.

| Aspecto | Descripción |
|---|---|
| Código | Repositorio `cotown-webs`, carpeta `code/`: `config/` (configuración de cada sitio y scripts de publicación), `src/pages/` (plantillas de página), `src/includes/` (secciones comunes y por marca), `src/assets/` (iconos, logos, scripts, vídeos), `src/data/` (carga de datos). |
| Idiomas | Inglés en la raíz (`/destinations.html`) y español en `/es/` (`/es/destinos.html`). Los textos con versión inglesa usan el campo `_en` de Airflows y, si está vacío, el español. |
| Generación | Contenedor `webgen` del servidor de servicios (Node 18 con Eleventy). |
| Publicación | Ficheros estáticos en `~/www/sites/cotown` y `~/www/sites/vanguard`, servidos por nginx. Unos 2.900 ficheros y 250 MB por marca, sobre todo imágenes. |

## 7.3 Datos

Al generar, cada web carga sus datos de dos fuentes:

**Airflows (GraphQL)**, con un usuario de servicio:

| Datos | Origen en Airflows | Uso |
|---|---|---|
| Ciudades, barrios, edificios y residencias | `Geo.Location` (publicadas), `Geo.District`, `Building.Building` (activos) con sus textos web, servicios e imágenes | Home, destinos, páginas de ciudad y de edificio |
| Tipologías | Tipos de plaza, tipos y subtipos de piso, con sus textos, características y fotos | Fichas de habitaciones y pisos |
| Textos | `Marketing.Text` | Casi todos los literales de las páginas, incluidos los textos legales |
| Imágenes | `Marketing.Media` y las imágenes de ciudades, barrios, edificios, tipologías y servicios | Toda la web |
| Blog | `Marketing.Post`, `Tag` (publicados) | Blog y etiquetas |
| Preguntas frecuentes | `Marketing.Faq_topic`, `Faq_question` | Página de FAQ y FAQ al pie de cada edificio |
| Otros contenidos | Banners, ventajas, socios, testimonios, redes sociales, equipo (autores del blog), oficinas, países, motivos de estancia | Home, membership, cabecera, pie, formularios |

**Servicio de integración (REST)**: precios de pisos y habitaciones por año académico, características, tipologías disponibles, promociones vigentes y recursos con bloqueos de más de 5 años (que no se publican; tampoco los edificios, barrios y ciudades que se quedan sin recursos).

Las imágenes se descargan de Airflows al generar y se convierten a WebP y JPEG en varios tamaños; el resultado se conserva en una caché de 2 horas. Los datos no se cachean: se consultan en cada generación.

## 7.4 Páginas

| Página | URL en inglés / español |
|---|---|
| Home | `/index.html` · `/es/index.html` |
| Destinos | `/destinations.html` · `/es/destinos.html` |
| Ciudad – habitaciones en piso compartido | `/shared-flats-<ciudad>.html` · `/es/pisos-compartidos-<ciudad>.html` |
| Ciudad – pisos completos | `/private-apartments-<ciudad>.html` · `/es/apartamentos-privados-<ciudad>.html` |
| Edificio – habitaciones / pisos | `/shared-flats-<edificio>.html` · `/private-apartments-<edificio>.html` (y sus equivalentes en español) |
| Residencia | `/<residencia>.html` · `/es/<residencia>.html` |
| Residencias (Vanguard) | `/residences.html` · `/es/residencias.html` |
| Blog, etiquetas y posts | `/blog.html`, `/blog/<etiqueta>.html`, `/<post>.html` (y en `/es/`) |
| Preguntas frecuentes | `/faqs.html` · `/es/preguntas-frecuentes.html` |
| Contacto / visita / reserva ahora / membership | `/contact.html`, `/schedule-visit.html`, `/book-now.html`, `/membership.html` (y en `/es/`) |
| Legales | Aviso legal, privacidad, seguridad de los datos |
| Técnicas | `sitemap.xml`, `robots.txt`, `llms.txt` (resumen para buscadores de IA) |

Las páginas de ciudad, edificio, residencia y post se generan automáticamente, una por cada registro publicado en Airflows.

**SEO**: cada página tiene título y descripción (de la configuración de idiomas o, en edificios, de sus textos web en Airflows), URL canónica, versiones alternativas por idioma (`hreflang`) y etiquetas para redes sociales; los posts incluyen datos estructurados. Las URL antiguas se redirigen con un mapa de más de 100 redirecciones 301 en el servidor web (`back/config/pro/301.conf`).

## 7.5 Comportamiento en el navegador

| Función | Cómo funciona |
|---|---|
| **Disponibilidad** | En las páginas de ciudad, edificio y residencia, al elegir fechas se consulta en vivo `GET /api/v1/availability/…` y se muestra si quedan plazas ("agotado", "solo quedan n") y la tarifa según la duración de la estancia. Las fechas se recuerdan durante la visita. |
| **Reservar** | El botón *Reservar* lleva al asistente de reserva del servicio de integración (`/booking/…`) con la ciudad, el edificio, la modalidad, la tipología y las fechas (ver *Servicio de integración*). |
| **Formularios** | Contacto, visita, reserva ahora y membership se envían a `POST /api/v1/form`, que crea el lead en Pipedrive. Se adjuntan los parámetros de campaña (UTM, `gclid`), guardados al entrar en la web. Protección básica contra robots: campo trampa y tiempo mínimo. |
| **Buscador** | En la home: ciudad y fechas, que llevan a la página de la ciudad o de la residencia. En las preguntas frecuentes, búsqueda dentro de la página. |
| **Terceros** | Chatbot, Google Tag Manager (un contenedor por marca), reseñas de Trustindex, mapas de OpenStreetMap (Leaflet) y WhatsApp (ver *Visión general*, sistemas externos). |
| **Otros** | Carruseles de imágenes, tour virtual del edificio (si existe), ficha legal del edificio en PDF y enlace al área de cliente (portal del residente). |

## 7.6 Generación y publicación

Cada web se regenera cada 2 horas desde el `crontab` del servidor de servicios: Vanguard en las horas pares (de 8:00 a 20:00) y Cotown en las impares (de 9:00 a 21:00). El script `webs/gen.sh`:

1. Actualiza el código desde GitHub (`git pull`).
2. Reinicia el contenedor `webgen`.
3. Ejecuta `config/publish.sh <marca>` dentro del contenedor, que:
   1. limpia la caché de imágenes de más de 2 horas;
   2. genera la web completa en `sites/<marca>-publish`;
   3. copia a `sites/<marca>` (la carpeta que sirve nginx) solo los ficheros que han cambiado.

Por tanto, **un cambio de contenido en Airflows tarda hasta 2 horas en verse en la web** y los cambios hechos por la noche se publican a partir de las 8:00. Para publicar antes, se puede lanzar `gen.sh publish <marca>` a mano en el servidor.

Existe también un modo **borrador** (`gen.sh draft <marca> <rama>`) que genera una copia de la web en `back.cotown.com/cotown` y `back.cotown.com/vanguard` para revisar cambios antes de publicarlos; hoy no está programado.

**cotowngroup.com** no se genera aquí: es una página estática que redirige al portal del residente.

## 7.7 Gestión de contenidos

| Se gestiona en Airflows | Está en el código |
|---|---|
| Textos de las páginas y textos legales (*Marketing › Textos*) | Estructura y diseño de todas las secciones |
| Imágenes (*Marketing › Imágenes* y las de ciudades, barrios, edificios, tipologías y servicios) | Títulos y descripciones SEO de las páginas fijas, y sus URL |
| Blog, etiquetas, autores | `llms.txt` |
| Preguntas frecuentes (generales, por ciudad o por edificio) | Identificadores de Google Tag Manager, chatbot y Trustindex |
| Banners, ventajas, socios, testimonios, redes sociales, oficinas | Mensajes de disponibilidad |
| Textos web de cada edificio (título, descripción, detalles, meta, tour virtual), de ciudades, barrios y tipologías | |
| Qué se publica: ciudades publicadas, edificios activos, servicios publicados, marca y modalidad de venta de cada recurso, orden | |
| Precios, promociones y bloqueos (a través de las tarifas, precios base, promociones y disponibilidad) | |

Los textos también admiten etiquetas de terceros (por ejemplo, códigos de verificación o de seguimiento), que se insertan en todas las páginas.

## 7.8 Fuentes

| Tema | Dónde está |
|---|---|
| Configuración de cada sitio | `webs/code/config/.base.js`, `.cotown.js`, `.vanguard.js` (y los de borrador) |
| Carga de datos | `webs/code/src/data/` |
| Plantillas | `webs/code/src/pages/`, `webs/code/src/includes/` |
| Textos SEO y URL por idioma | `webs/code/src/data/langs/` |
| Generación y publicación | `webs/gen.sh`, `webs/code/config/publish.sh`, `webs/code/Dockerfile` |
| Servidor web y redirecciones | `back/config/pro/nginx.conf`, `back/config/pro/301.conf` |

## 7.9 Pendiente de confirmar

No hay puntos pendientes.
