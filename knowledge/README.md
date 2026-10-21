# Base de conocimiento Cotown – carpeta de trabajo

Contenido de la carpeta, cómo regenerar los documentos y acuerdos tomados con Alejandro André (Oimbra). Leer los acuerdos antes de continuar el trabajo.

| Ruta | Contenido |
|---|---|
| `TODO.md` | Errores, riesgos y mejoras detectados, un capítulo por prioridad; en prioridad alta, los fallos críticos de seguridad y pérdida de datos con sus pasos de corrección (uso interno de Oimbra). |
| `borradores/` | Capítulos en Markdown: la fuente del contenido. `01-*` es común a los dos volúmenes, `IT-*` es el manual técnico y `OP-*` el funcional; `IT-A*` y `OP-A*` son anexos. |
| `diagramas/` | Diagramas en draw.io (editables) y PNG (para el Word). `er/` contiene los diagramas entidad-relación. |
| `fuentes/docs/` | Documentos y diagramas de diseño originales de Experis (2023) y ficheros de Power BI (`.pbix`). Solo referencia; no se modifican. |
| `fuentes/plantilla/` | Plantilla de formato (`Nomenclatura BD v1.0.docx`) y logos. |
| `fuentes/bd/` | Instantánea de los metadatos de Airflows (esquema `Models`). |
| `scripts/` | Generadores: instantánea de metadatos, diccionario de datos, diagramas y documentos Word. |
| `salida/` | Documentos Word generados. No editar a mano: se regeneran desde los borradores. |

## Regenerar

Desde `knowledge/` (requiere el entorno Python con `psycopg2`, `python-docx` y `networkx`, y draw.io de escritorio para exportar PNG):

| Qué | Comando |
|---|---|
| Instantánea de metadatos | `python scripts/dump_models.py fuentes/bd/airflows-models-<fecha>.json` (con el túnel SSH a la BD abierto en el puerto 15432) |
| Diccionario de datos | `python scripts/gen_diccionario.py fuentes/bd/airflows-models-<fecha>.json borradores/IT-A1-diccionario-datos.md` |
| Anexo de permisos por rol | `python scripts/gen_permisos.py fuentes/bd/airflows-permisos-<fecha>.json fuentes/bd/airflows-models-<fecha>.json borradores/IT-A2-permisos.md` |
| Diagramas entidad-relación | `python scripts/gen_er.py fuentes/bd/airflows-models-<fecha>.json diagramas/er` |
| Diagramas de arquitectura y ciclo de reserva | `python scripts/gen_arquitectura.py "diagramas/Arquitectura Cotown v2.drawio"` y `python scripts/gen_ciclo_reserva.py "diagramas/Ciclo reserva B2C v2.drawio"` |
| PNG de un diagrama | `"C:/Program Files/draw.io/draw.io.exe" -x -f png -s 2 -b 10 -o <salida.png> <entrada.drawio>` |
| Inventario de credenciales | `python scripts/gen_secretos.py <versión> <fecha AAAA-MM-DD>` y después `pwsh scripts/update_docx.ps1` |
| Documentos Word | `python scripts/gen_docx.py <versión> <fecha AAAA-MM-DD>` y después `pwsh scripts/update_docx.ps1` (abre cada documento en Word y actualiza el índice; con `-Pdf` exporta además un PDF) |

## Acuerdos

Decisiones tomadas con Alejandro André (Oimbra) desde el 2026-10-19.

### Objetivo y lectores

- Base de conocimiento funcional y técnica de Cotown para el cliente. No es un traspaso: Oimbra sigue manteniendo el sistema.
- Dos volúmenes `.docx` en español:
  - *Cotown – Base de conocimiento – Manual funcional v1.0* → Operaciones.
  - *Cotown – Base de conocimiento – Manual técnico v1.0* → IT.
- Mismo mapa general al inicio de ambos. Autor en la tabla de versiones: "Oimbra".
- Formato: el de `fuentes/plantilla/Nomenclatura BD v1.0.docx` (portada, tabla de versiones, estilos), con la marca de Cotown Group: logo de Cotown Group en portada y cabecera, logo de Oimbra pequeño ("Elaborado por" en portada y a la derecha de la cabecera), colores turquesa `#08BDBD`, rosa `#FF4870` y negro. Los Word se generan desde los borradores con `scripts/gen_docx.py`; no se editan a mano.

### Alcance

- Repositorios `back`, `front` y `webs`. `webs/code` (Eleventy, en producción) a fondo; `webs/src` (reescritura FastAPI) no se menciona en los documentos del cliente por ahora (decisión del 2026-10-20).
- Fuera: `misc`, `newebs`. Excepción: el conector de Keycloak con Airflows (User Storage SPI, `misc/core/keycloak`), que está en producción, se menciona en la documentación.
- Código legacy o muerto: no se documenta; se avisa a Alejandro para quitarlo.
- Todos los errores, riesgos y mejoras que se detecten se anotan en `TODO.md` (uso interno), con su prioridad; los críticos de seguridad o pérdida de datos van en prioridad alta, con sus pasos de corrección. Las vulnerabilidades no se mencionan en los documentos del cliente. Las funcionalidades futuras no implementadas no se documentan; se anotan en `TODO.md`.
- Cuando el código no hace lo que dice la regla de negocio que confirma Alejandro, el manual documenta la regla de negocio y la diferencia se anota en `TODO.md`.
- Secretos: no se mencionan en los manuales. Van en un documento aparte, *Inventario de credenciales*, generado con `scripts/gen_secretos.py`: lista cada credencial (parámetro o fichero donde está, quién la gestiona, cómo se cambia) **sin sus valores** y sin cifrar (decisión del 2026-10-21). Los valores se custodian en un gestor de contraseñas. Se regenera al añadir, mover o retirar credenciales.
- Ejemplos: siempre con datos ficticios.

### Contenido

- Mapa general + un capítulo de profundización por tema.
- Operaciones: procesos y reglas (qué es automático, qué manual, cuándo y por qué). Sin guías clic a clic.
- IT: extenso en comprensión (arquitectura, modelo de datos, triggers, batch y calendario, API, integraciones, infraestructura, monitorización). Sin runbooks de despliegue.
- Estructura de capítulo, siempre que sea posible: Propósito · Conceptos · Flujo · Reglas · Automático/manual (en IT: Componentes técnicos) · Excepciones · Fuentes · Pendiente de confirmar.
- Sistemas externos: inventario completo de los que aparecen en el código. Los servicios de terceros que solo están incrustados o enlazados (chatbot, GTM, widgets, redes) se enumeran sin documentar. Los que se usan sin ninguna relación con el sistema no se incluyen.
- Diagramas: copias corregidas de los drawio de `fuentes/docs/` en `diagramas/`, exportadas a imagen para el Word. Los originales no se tocan.

### Manual técnico

Arquitectura y plataforma Airflows · Modelo de datos · Servicio de integración · Procesos automáticos · Triggers · Frontends · Webs · Data warehouse · Integraciones · Infraestructura y monitorización · Usuarios y roles · Instalación · Deuda técnica; anexos de diccionario de datos y de permisos.

### Manual funcional (decidido el 2026-10-20)

- Índice: OP-1 Inventario y precios · OP-2 Captación · OP-3 Reservas B2C · OP-4 Reservas de grupo B2B · OP-5 Contratos, garantías e INCASÒL · OP-6 Facturación y cobros · OP-7 Operación diaria · OP-8 Comunicación con el residente (emails y portal) · OP-9 Contratos LAU y otros · OP-10 Propietarios · OP-11 Informes y analítica · anexo OP-A1.
- Cada capítulo se organiza **por tarea**: qué hay que hacer, cuándo, qué comprobar y qué hace el sistema a continuación. No por pantalla ni por tabla, y sin guías clic a clic.
- **Sin equipos**: las tareas no se asignan a equipos concretos; se habla del "personal" y, si hace falta, del permiso necesario.
- Los procesos automáticos y los triggers se explican dentro de cada tarea ("Qué hace el sistema") y en la tabla "Automático y manual" de cada capítulo. Al final del manual, anexo **OP-A1. Calendario de procesos automáticos**: cada proceso, cuándo se ejecuta, qué hace y en qué capítulo se explica.
- Lenguaje de negocio: los nombres internos (`Booking`, `Pricing_rate`…) solo entre paréntesis cuando ayudan a localizar el dato en Airflows. Sin código ni SQL.

### Fuentes

- La verdad está en el código. Los documentos de Experis (`fuentes/docs/`, 2023) son solo referencia.
- BD `niledb` en `core.cotown.com` (SSH `partner` + `back/airflows.key.pem`, usuario `readonly`). Desde el 2026-10-21, `readonly` tiene `BYPASSRLS` y puede leer los datos de negocio, además de los metadatos de Airflows (`Models`, instantánea en `fuentes/bd/`) y el esquema `cron`.
- Conocimiento de Alejandro, en rondas de preguntas por capítulo.
- Lo no resuelto se marca "Pendiente de confirmar" indicando quién o qué lo podría confirmar.

### Método y orden

- Capítulo a capítulo: borrador desde el código → ronda de preguntas → incorporar respuestas.
- Borradores Markdown en `borradores/`; Word generado al final en `salida/`.
- Orden: 1) Visión general y glosario; 2) Volumen IT; 3) Volumen Operaciones.
- Control de versiones del documento: se decide más adelante.
