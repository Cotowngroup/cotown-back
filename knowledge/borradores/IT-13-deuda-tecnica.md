# IT-13. Deuda técnica y recomendaciones

> Manual técnico · Borrador v0.1 · 2026-10-20 · Las marcas **[PREGUNTA Tn]** se resuelven en la ronda de preguntas y desaparecen de la versión final.

## 13.1 Propósito

Este capítulo recoge los aspectos técnicos del sistema que, sin impedir hoy su funcionamiento, aumentan el coste de mantenerlo o el riesgo de una incidencia, junto con una recomendación para cada uno. Sirve para entender el porqué de futuras mejoras y para priorizarlas.

## 13.2 Versiones sin soporte

| Componente | Situación | Recomendación |
|---|---|---|
| Backoffice complementario y portal del residente | Angular 15, sin soporte desde noviembre de 2023. | Actualizar a una versión con soporte, aprovechando para revisar dependencias. |
| Generador de las webs | Node 18, sin soporte desde abril de 2025. | Actualizar la imagen a una versión LTS vigente. |
| Imágenes de contenedores del servidor de servicios | Varias sin versión fija (*latest*) y alguna muy antigua. | Fijar versiones y actualizarlas de forma planificada. |

## 13.3 Pruebas automáticas

No hay pruebas automáticas en ningún componente (servicio de integración, procesos, frontends, webs, ETL ni reglas de la base de datos). Cada cambio se valida a mano, lo que hace más lento y arriesgado evolucionar las partes críticas (facturación, flujo de reservas, cálculo de precios, contratos).

**Recomendación**: empezar por pruebas de los cálculos con más impacto económico (precios mensuales, facturación, management fee, rentas máximas) y del flujo de estados de la reserva, ejecutadas contra el entorno de desarrollo.

## 13.4 Despliegue y control de versiones

| Situación | Recomendación |
|---|---|
| Los despliegues son manuales y no hay scripts versionados para ellos (servicio de integración, frontends, data warehouse). | Automatizarlos con scripts versionados o un sistema de integración continua. |
| El código del data warehouse en el servidor es una copia manual, no un clon del repositorio, y no coincide con la última versión del repositorio. | Desplegarlo desde el repositorio y verificar que coinciden. |
| Parte de la configuración de producción solo existe en los servidores (programación de procesos, copia a SharePoint, configuración del data warehouse) y difiere de la que hay en el repositorio. | Versionar la configuración de cada servidor y desplegarla desde el repositorio. |
| Las funciones de la base de datos se cargan a mano en Airflows; el repositorio es la copia de referencia, pero no hay comprobación automática de que coincidan. | Comparar periódicamente las funciones desplegadas con el repositorio. |
| El conector de Keycloak con Airflows, que está en producción, está en un repositorio de pruebas y restos. | Moverlo a un repositorio propio con su proceso de construcción. |

## 13.5 Supervisión, logs y copias

| Situación | Recomendación |
|---|---|
| No hay alertas: la supervisión es manual. | Alertas básicas: servicio caído, proceso automático con errores o sin ejecutarse, generación de webs fallida, ETL fallido, disco casi lleno. |
| Los logs tienen poco histórico (procesos: 5 ficheros de 1 MB; data warehouse: unas 10 horas). | Ampliar la retención o consultarlos siempre en Loki, con retención definida. |
| El servidor del data warehouse no tiene monitorización. | Incorporarlo a Prometheus y Loki. |
| La base de datos de Airflows no tiene copia fuera de su servidor. | Copia externa automatizada y prueba periódica de restauración (previsto). |

## 13.6 Valores fijos en el código

Algunos datos de negocio están escritos en el código en lugar de configurarse, así que cambiarlos exige un desarrollo:

- Correspondencias con Pipedrive (edificios, ciudades, tipologías, formularios, canales).
- Ubicaciones con reglas específicas (Barcelona para INCASÒL y anexos; Barcelona y Bilbao para la limitación de rentas).
- Identificadores concretos de proveedores, tipos de edificio, medios de pago y productos usados en la facturación y en el data warehouse; el IVA de las residencias.
- Textos y títulos de las webs (SEO, `llms.txt`).

**Recomendación**: trasladarlos progresivamente a tablas o parámetros de Airflows.

## 13.7 Data warehouse

| Situación | Recomendación |
|---|---|
| Cada carga vacía y recarga las tablas por separado: durante unos minutos, Power BI puede ver tablas vacías o a medio cargar; y si falla una consulta, la tabla queda incompleta sin aviso. | Cargar en tablas temporales y sustituirlas al final de forma atómica; avisar si una carga falla. |
| Los cálculos son fila a fila y algunos se repiten en cada ejecución. | Optimizarlos para reducir el tiempo de carga. |
| Conviven dos fuentes de forecast. | Decidir cuál se mantiene. |

## 13.8 Código y documentación

- Hay código duplicado (consultas, lógica de promociones, pantallas del backoffice) y código sin uso pendiente de retirar.
- La documentación técnica de la API (Swagger) solo cubre la integración contable.
- La plataforma Airflows es un producto de un tercero: su evolución, sus versiones y la gestión de su servidor dependen del proveedor.

**Recomendación**: reducir duplicación al tocar cada área, retirar el código sin uso, completar la documentación de la API y mantener al día esta base de conocimiento.

## 13.9 Fuentes

Este capítulo resume la revisión del código y de los servidores realizada para elaborar la base de conocimiento (octubre de 2026).

## 13.10 Pendiente de confirmar

No hay puntos pendientes.
