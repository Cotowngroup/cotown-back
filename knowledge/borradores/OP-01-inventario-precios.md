# OP-1. Inventario y precios

> Manual funcional · Borrador v0.1 · 2026-10-20 · Las marcas **[PREGUNTA On]** se resuelven en la ronda de preguntas y desaparecen de la versión final.

## 1.1 Propósito

Este capítulo explica cómo se mantiene en Airflows **lo que Cotown ofrece y a qué precio**: edificios, pisos, habitaciones y plazas, sus tipologías, su disponibilidad, los precios base de cada año académico, las tarifas y las promociones.

Es la base de todo lo demás: de estos datos salen lo que se publica en las webs, la disponibilidad que ve el cliente, el precio de cada reserva, la garantía y el membership fee, y las rentas máximas en los pisos con renta limitada.

Se organiza por tareas: qué hay que hacer, cuándo, qué comprobar y qué hace el sistema a continuación.

## 1.2 Conceptos

Los términos generales (edificio, recurso, tipología, régimen de renta…) están en el glosario del capítulo *Visión general*. Aquí se añaden los que importan para mantener el inventario.

| Concepto | Qué es |
|---|---|
| **Jerarquía de recursos** | Piso → habitación → plaza. Comparten el inicio del código: piso `MAD001.01.02`, habitación `MAD001.01.02.H01`, plaza `MAD001.01.02.H01.P1`. Ocupar o bloquear uno afecta a los demás de su rama. |
| **Datos que se heredan del piso** | Edificio, propietario, prestador de servicios, forma de facturación, modalidad de venta, código SAP y porcentajes de management fee se informan en el piso; el sistema los copia a sus habitaciones y plazas. |
| **Modalidad de venta** | *Completo* (se alquila el piso entero), *plazas* (por habitaciones o plazas), *ambos* o *no aplica* (activos que no son vivienda). Decide qué se ofrece en la web. |
| **Web** | Vanguard, Cotown o vacía. Se informa en el piso; las habitaciones y plazas siguen a su piso. Decide en qué web se publica el recurso; vacía, no se publica en ninguna. |
| **Tipología** | Tipo de piso y tipo de plaza. El cliente reserva una tipología en un edificio; el precio base también va por tipología. |
| **Característica** (*amenity*) | Equipamiento del recurso (baño propio, terraza…). Cada tipo de característica puede tener un **incremento %** sobre la renta. |
| **Año académico** | De septiembre a agosto. En Airflows se identifica por el año en que **termina**: el año 2027 va de septiembre de 2026 a agosto de 2027. |
| **Precio base** | Precio de referencia por año académico, edificio, tipo de piso y tipo de plaza. |
| **Tarifa** | Nivel de precio con un **multiplicador** (por ejemplo, 1,10 = un 10 % sobre el precio base). Cada recurso tiene una. |
| **Promoción** | Descuento (o incremento) temporal sobre la renta o el membership fee, para unos edificios, tipologías y fechas. |
| **Estado / bloqueo** | Periodo en que un recurso no está disponible para coliving: obras, contrato de larga duración, fuera de servicio… El estado normal, *cosharing* (disponible), no se registra. |
| **Ocupación** | Resumen interno de qué recursos están ocupados en cada fecha, por reservas B2C, grupos y bloqueos. Lo mantiene el sistema; lo usan la web, el planning y la comprobación de solapes. |

## 1.3 Tareas

### Dar de alta un edificio

**Cuándo**: al incorporar una nueva dirección a la cartera.

**Qué informar**:

- Código (3 letras de la ciudad + 3 caracteres; por ejemplo `MAD001`), nombre, dirección, código postal y barrio. El barrio decide la ciudad.
- **Tipo de edificio** (co-sharing, apartamentos privados, residencia de estudiantes, grupos Study Abroad, B2B): decide el **IVA** de las reservas. En las residencias de estudiantes, además, el contrato usa la plantilla de residencia y la web presenta el edificio como residencia. Los edificios de grupos y B2B no se ofrecen en el asistente de reserva web.
- **Marca** y si está **activo**. Los edificios no activos no aparecen en las webs, en el planning ni en el selector de recursos.
- **Emitir contratos**: si las reservas del edificio generan contrato.
- Para Barcelona y Bilbao, **IBI** y **gastos de comunidad**: se usan para calcular los gastos repercutibles máximos (ver *Mantener los datos del régimen de renta*).
- Management fee del edificio, fechas de compra y de estabilización (para la analítica).
- Datos de acceso y operación: WiFi, puerta automática, notas de mantenimiento y emergencias.
- Contenido para la web: títulos, descripciones y textos SEO en los dos idiomas (piso compartido y apartamento privado), tour virtual, servicios, transportes e imágenes.
- Documentos del edificio. Los tipos de documento marcados *Adjuntar a contratos* se anexan a los contratos.

**Qué hace el sistema**: en la siguiente regeneración de las webs (cada 2 horas, de 8 a 21 h) el edificio aparece si está activo, su ciudad está publicada y tiene pisos asignados a esa web.

**Cambiar el código de un edificio**: el sistema recodifica automáticamente todos sus pisos, habitaciones y plazas.

### Dar de alta pisos, habitaciones y plazas

**Cuándo**: al incorporar un edificio o al dividir o reconfigurar un piso.

**Cómo**: de uno en uno en *Activos*, o de forma masiva con la carga Excel **Recursos** (*Procesos › Cargas*), que crea los que no existen y actualiza los que ya existen por su código. La plantilla de la carga se obtiene descargando el informe del mismo nombre.

**Qué informar en el piso**:

- Código con formato `XXXnnn.nn.nn` (código del edificio + portal/planta + puerta).
- Propietario y prestador de servicios.
- **Forma de facturación** de los meses incompletos: mes completo, quincena o proporcional a los días.
- Modalidad de venta, web en la que se publica (o vacía para no publicarlo), tipo y subtipo de piso, tarifa.
- Porcentajes de management fee: sin servicios, servicio premium (limpieza semanal), estándar (quincenal), mensual y marketplace.
- Código SAP.
- Datos técnicos y legales: superficie, cédula de habitabilidad, certificado energético, referencia catastral, contratos de suministros.
- Datos del régimen de renta (ver más abajo).

**Qué informar en habitaciones y plazas**: código (`….Hnn` para habitación, `….Hnn.Pn` para plaza, que debe empezar por el de su habitación), piso y habitación de los que dependen, tipo de plaza, tarifa, características y peso.

**Qué hace el sistema**:

- Valida el formato del código y rechaza el alta si no es correcto.
- Copia al resto de la rama los datos que se heredan del piso.
- Recalcula qué parte del piso representa cada habitación o plaza.
- Genera la URL del calendario iCal del recurso, que se comparte con los marketplaces.
- Al día siguiente, el proceso de rentas máximas calcula su régimen y sus rentas máximas.

**Comprobar**: que el recurso tiene tarifa y que existe precio base para su edificio y tipologías en el año académico en curso y en el siguiente. Sin precio base, la reserva no tendrá precio (ver *Excepciones*).

### Retirar un recurso o un edificio

- **Recurso** que deja de explotarse: no se borra. Se le añade un bloqueo con estado **Out** desde la fecha de retirada y con una fecha de fin muy lejana. Deja de estar disponible para reservas y, al superar el bloqueo los 5 años, deja de publicarse en la web. Su historial (reservas, facturas) se conserva.
- **Edificio** completo: se marca como **no activo**. Desaparece del planning y del selector de recursos de inmediato, y de las webs en la siguiente regeneración.
- **Dejar de publicar** un piso sin retirarlo: se deja vacía su web. Sigue disponible para reservas registradas a mano.

### Asignar tipologías, características y tarifa

- **Tipología**: decide el precio base que se aplica y cómo se agrupa el recurso en la web y en la reserva. Cambiarla en un recurso con reservas futuras no cambia los precios ya calculados hasta que esas reservas se modifiquen.
- **Características**: cada una suma su incremento % a la renta del recurso; si hay varias, los incrementos se acumulan (por ejemplo, +10 % y +5 % = +15,5 %).
- **Tarifa**: sube o baja el nivel de precio del recurso respecto del precio base. Es la forma de ajustar el precio de un recurso concreto sin tocar el de su tipología.

**Qué hace el sistema**: cada hora registra en el **histórico de precios** del recurso cualquier cambio de tarifa o de precio base. Ese histórico alimenta la analítica.

### Cargar los precios base del año académico

**Cuándo**: antes de abrir las reservas del siguiente año académico. Una reserva que empieza en septiembre o más tarde usa los precios del año siguiente, y una estancia que cruza septiembre usa los del año siguiente a partir de ese mes.

**Cómo**: carga Excel **Precios**, con una fila por año, edificio, tipo de piso y tipo de plaza (sin tipo de plaza para el precio del piso completo). Si la fila ya existe, se actualiza.

**Qué incluye cada fila**:

| Concepto | Uso |
|---|---|
| Renta corta, media y larga | Renta mensual según la duración de la estancia: **corta**, menos de 3 meses; **media**, de 3 a 6; **larga**, 7 o más. |
| Renta de grupo | Precio por plaza en reservas de grupo. |
| Servicios | Importe mensual de servicios. |
| Garantía | Importe de la garantía. |
| Límite de consumos | Consumo máximo incluido. |
| Segundo residente | Suplemento mensual por un segundo ocupante. |
| Limpieza final | Limpieza de salida que se factura al residente. |
| Membership fee | Importe del membership fee. |

**Qué hace el sistema con estos datos al calcular una reserva** (renta libre o recreativa):

- **Renta** = renta del precio base según la duración × multiplicador de la tarifa × incrementos por características, más el suplemento de segundo residente si la reserva lo tiene marcado.
- **Garantía** = la del precio base, con un mínimo de **1,5 × (renta + segundo residente)**.
- **Membership fee** = el del precio base, con la promoción si la hay.
- Genera el detalle mes a mes. Los meses incompletos se facturan completos, por quincena o de forma proporcional según la forma de facturación del recurso (se puede indicar otra distinta para el último mes en la reserva).

En **renta limitada** no se usa el precio base: la renta, los servicios, los consumos, el mobiliario y los gastos salen de las rentas máximas del recurso, y la garantía es 1,5 × (renta + consumos + mobiliario + gastos).

**Comprobar**: tras la carga, que la web muestra los precios nuevos (en la siguiente regeneración) y que ninguna tipología en venta se ha quedado sin precio.

### Crear una promoción

**Cuándo**: campañas comerciales, temporada baja o captación en edificios concretos.

**Qué informar**:

| Dato | Significado |
|---|---|
| **Activa desde / hasta** | Periodo en que la promoción se ofrece: la ve la web y se puede asignar a reservas nuevas. |
| **Aplicable desde / hasta** | Meses de estancia a los que se aplica el descuento. Una reserva que solo coincide en parte recibe el descuento en los meses que caen dentro. |
| **Renta %** o **Renta €** | Variación de la renta mensual: en negativo es un descuento (por ejemplo, −10). Se usa uno de los dos. |
| **Fees %** o **Fees €** | Variación del membership fee. Se usa uno de los dos. |
| **Tipo de limitación** | Si vale para recursos de renta libre, limitada o ambos. |
| **Edificios** | Lista de edificios. Sin ninguno, vale para todos. |
| **Tipos de piso o de plaza** | Lista de tipologías. Sin ninguna, vale para todas. Un apartamento privado solo recibe las promociones definidas para su tipo de piso sin tipo de plaza. |

**Qué hace el sistema**:

- La **web** busca la mejor promoción activa que encaja con el edificio, la tipología, las fechas y la marca, la muestra al cliente y la guarda en la solicitud.
- En una reserva **creada a mano sin promoción**, el sistema aplica la mejor promoción activa que valga para cualquier régimen de renta. Las promociones solo para renta libre o solo para renta limitada se asignan a mano, porque dependen del recurso.
- Si encajan varias, gana la de mayor descuento sobre la renta, después la de mayor descuento sobre el membership fee y, a igualdad, la más reciente.
- En la reserva, un descuento **en %** se aplica a la renta **y a los servicios** de cada mes afectado; un descuento **en importe**, solo a la renta. El descuento queda registrado en cada mes de la reserva como descuento por promoción.

**Comprobar**: que no hay dos promociones activas que se solapen sin querer en los mismos edificios y tipologías: solo se aplica una.

### Bloquear un recurso (no disponibilidad)

**Cuándo**: obras, reformas, averías, uso interno o cualquier periodo en que un recurso no deba reservarse.

**Cómo**: en la ficha del recurso, apartado *Estado*, se añade un periodo con fechas desde y hasta, el estado (motivo) y, si se quiere, un detalle.

**Estados**:

| Estado | Disponible | Uso |
|---|---|---|
| **Cosharing** | Sí | Estado por defecto: en explotación. No se registra. |
| **Alquiler/LAU** | No | Contrato de larga duración. Lo crea el contrato LAU. |
| **Pre capex** | No | Periodo previo a la reforma. Lo crea el contrato LAU al terminar. |
| **Capex** | No | Reforma. Lo crea el contrato LAU al terminar. |
| **Post Capex** | No | |
| **Bloqueo CTH** | No | Único estado marcado *No bloquea piso*. |
| **Out** | No | Recurso retirado de la explotación. |
| **Indefinido** | No | |
| **Vacío** | No | |
| **Reparaciones - out of stock** | No | Reparación que deja el recurso fuera de la oferta. |
| **Reparaciones** | Sí | Reparación puntual. |
| **Limpiezas** | Sí | Limpieza. |
| **Comercial** | Sí | |
| **Badi** | Sí | |

Todos los estados impiden reservar el recurso en sus fechas. La columna **Disponible** solo afecta a la analítica: los estados disponibles cuentan como camas en explotación al calcular la ocupación y el forecast; los no disponibles las restan. Los estados también indican si el recurso es **convertible** a coliving, dato que usa la analítica.

**Reglas**:

- No se registra el estado *cosharing*: es el estado por defecto.
- La fecha de fin debe ser posterior a la de inicio.
- Los bloqueos que crean los **contratos LAU** (contrato, pre-capex y capex) no se pueden modificar ni borrar a mano: se gestionan desde el contrato (ver *Contratos LAU y otros*).
- Bloquear un piso bloquea sus habitaciones y plazas; bloquear una habitación bloquea también su piso (para la venta del piso completo) y sus plazas. Los estados marcados **No bloquea piso** bloquean las habitaciones y plazas pero dejan libre el piso.

**Qué hace el sistema**:

- Lo refleja de inmediato en la ocupación: desaparece de la disponibilidad de la web, del planning y del selector de recursos.
- Cada hora actualiza el **estado actual** de cada piso según sus bloqueos vigentes.
- Los recursos con bloqueos de más de 5 años no se publican en la web.

### Consultar la ocupación y la disponibilidad

- **Planning** (desde *Reservas*): diagrama temporal de pisos, habitaciones y plazas, con filtros por ciudad, edificio y tipologías. Cada reserva es una barra con el color de su estado; los grupos y bloqueos tienen su propio estilo. Al indicar un rango de fechas marca en verde los recursos libres. También se usa como **selector** para asignar recurso a una solicitud (ver *Reservas B2C*).
- **Web**: en las páginas de ciudad y de edificio, al elegir fechas, la web consulta en vivo cuántos recursos quedan libres de la marca de la web y lo muestra ("agotado", "solo quedan n"). Las habitaciones y plazas cuentan si su piso se vende por plazas o de ambas formas; los pisos, si se venden completos o de ambas formas. En todos los edificios se pueden ofrecer pisos, habitaciones y plazas.

### Mantener los datos del régimen de renta

En Barcelona y Bilbao la Ley de vivienda limita la renta de muchos pisos. Cada día a las 05:00 el sistema calcula para cada piso su **régimen** (libre, LAU o índice) y sus **rentas máximas**, y las reparte entre habitaciones y plazas según su peso. El cálculo es automático, pero depende de datos que hay que mantener en el piso:

| Dato | Para qué |
|---|---|
| Fecha fin y renta del último contrato LAU | Si hubo un contrato LAU en los últimos 5 años, la renta máxima es esa renta actualizada por IPC. Se cargan con la carga Excel **Recursos** al terminar el contrato. |
| Valor índice | Índice de referencia del piso; se usa cuando no hay LAU reciente o es más bajo. |
| Fecha fin de reforma / de gran rehabilitación | Una reforma reciente permite un 10 % más; una gran rehabilitación de menos de 5 años deja el piso en renta libre. |
| Superficie | Los pisos de 150 m² o más sin LAU reciente quedan en renta libre. |
| Repercutir gastos | Si se repercuten IBI y comunidad del edificio. |
| Peso | Parte del piso que representa cada habitación o plaza. |

**Qué hace el sistema con el resultado**: en una reserva sobre un recurso con renta limitada exige indicar si es **limitada** (aplica las rentas máximas) o **recreativa** (estancia vacacional, con precio libre). El detalle del cálculo está en el *Manual técnico*.

### Otros datos del inventario

- **Inventario de mobiliario**: elementos de cada recurso por tipo y zona, con fecha de compra, garantía, precio y factura.
- **Valoraciones, forecast y stabilised**: datos de los recursos para la analítica. Se describen en *Informes y analítica*.

## 1.4 Automático y manual

| Qué | A / M |
|---|---|
| Alta y mantenimiento de edificios, recursos, tipologías, características y tarifas | M |
| Herencia de datos del piso a sus habitaciones y plazas; partes del piso; URL iCal | A |
| Carga de precios base por año académico | M |
| Histórico de precios (cada hora) | A |
| Alta de promociones | M |
| Elección de la promoción en la web y en reservas manuales sin promoción | A |
| Bloqueos manuales (obras, averías…) | M |
| Bloqueos de contratos LAU (contrato, pre-capex, capex) | A |
| Estado actual de cada piso (cada hora) | A |
| Régimen de renta y rentas máximas (diario) | A |
| Publicación en las webs (cada 2 horas, de 8 a 21 h) | A |

## 1.5 Excepciones

| Situación | Qué pasa | Qué hacer |
|---|---|---|
| Falta el precio base del año académico de la reserva | La reserva se crea sin renta y sin servicios. | Cargar el precio base y volver a guardar la reserva (cambiar y restaurar una fecha) para que se recalcule. |
| Falta el precio base del año siguiente en una estancia que cruza septiembre | Los meses desde septiembre se calculan con el precio del año en curso. | Cargar el precio del año siguiente antes de abrir reservas de ese año. |
| Se cambia la tarifa, la tipología o el precio base con reservas ya creadas | Las reservas existentes no cambian. Solo se recalculan si se cambian sus fechas o su recurso, y entonces se recalculan con los precios vigentes, sustituyendo los ajustes manuales de los meses no facturados. | Revisar los ajustes manuales tras cambiar fechas o recurso de una reserva. |
| Una reserva de grupo o un bloqueo ocupa un recurso | El recurso no aparece como libre en la web ni en el planning. | Comprobar en el planning antes de asignar a mano. |
| Un recurso no aparece en la web | Puede deberse a la web asignada al piso, la modalidad de venta, que el edificio no esté activo, que la ciudad no esté publicada, que no haya precio base del año, que tenga un bloqueo de más de 5 años o que aún no se haya regenerado la web. | Revisar esos datos; esperar a la siguiente regeneración. |

## 1.6 Fuentes

| Tema | Dónde está |
|---|---|
| Validación de códigos y herencia de datos del piso | Reglas de la base de datos de los recursos y edificios |
| Cálculo de precios, garantía y membership fee | Reglas de la base de datos de las reservas |
| Elección de promociones | Reglas de la base de datos de las reservas y servicio de integración (web) |
| Bloqueos y estado del piso | Reglas y procesos programados de la base de datos de disponibilidad |
| Disponibilidad en la web y en el planning | Servicio de integración |
| Rentas máximas | Proceso automático diario de rentas máximas |
| Cargas Excel | Proceso automático de cargas |

## 1.7 Pendiente de confirmar

| Tema | Quién o qué lo confirma |
|---|---|
| — | — |
