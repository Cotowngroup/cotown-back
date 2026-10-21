# IT-2. Modelo de datos

> Manual técnico · Borrador v0.1 · 2026-10-20 · Las marcas **[PREGUNTA Tn]** se resuelven en la ronda de preguntas y desaparecen de la versión final.

## 2.1 Propósito

Este capítulo explica cómo están organizados los datos del sistema: en qué áreas se dividen, cuáles son las entidades principales y cómo se relacionan, y qué convenciones siguen. El detalle completo de cada entidad y atributo está en el *Anexo. Diccionario de datos*, que se genera automáticamente a partir de los metadatos de Airflows.

## 2.2 Cómo se define el modelo

El modelo no se define con scripts SQL, sino como **metadatos de Airflows** (esquema `Models`). Cada entidad, atributo, relación y lista de valores es un registro en esas tablas, y la plataforma crea y mantiene a partir de ellos las tablas físicas, la interfaz y la API GraphQL (ver *Arquitectura y plataforma*).

Consecuencias prácticas:

- La fuente de verdad del modelo es la base de datos de Airflows, no el repositorio.
- Los cambios de modelo (nuevos campos, nuevas tablas) se hacen en Airflows, y la interfaz y la API los reflejan sin desarrollo adicional.
- Cada atributo tiene etiqueta en español e inglés, que es el nombre que ve el usuario en el ERP. Esas etiquetas son las que se usan en el diccionario de datos.

En cifras: 12 áreas, 153 entidades, 2.174 atributos, 269 relaciones y 37 listas de valores.

## 2.3 Convenciones

| Elemento | Convención | Ejemplo |
|---|---|---|
| Esquema | Uno por área funcional, nombre en inglés con mayúscula inicial. | `Booking`, `Billing` |
| Tabla | Nombre de la entidad en inglés, mayúscula inicial, palabras separadas por guion bajo. Las tablas dependientes llevan como prefijo la entidad principal. | `Booking_price`, `Booking_group_rooming` |
| Clave primaria | `id`, numérica autoincremental, en todas las tablas. | |
| Clave foránea | `<Entidad>_id`. Cuando hay varias referencias a la misma tabla, el nombre indica el papel. | `Customer_id`, `Owner_id` y `Service_id` (ambos a `Provider`) |
| Auditoría | Todas las tablas tienen `Created_at`, `Created_by`, `Updated_at` y `Updated_by`, que rellena la plataforma. | |
| Búsqueda | Campo `Search` con el texto indexado para la búsqueda del ERP, mantenido por la función `<Tabla>_B0_search`. | |
| Textos bilingües | Pareja de campos en español e inglés, con sufijo `_en` para el inglés. | `Name` / `Name_en` |
| Campos calculados | Marcados como no editables en el ERP; los rellenan los triggers. | `Max_rent`, `Limit_type` |
| Documentos | Atributos de tipo documento (PDF, imágenes) almacenados por la plataforma y accesibles por su API de ficheros. | `Contract_rent`, `Document` |
| Listas de valores | Tipos enumerados de PostgreSQL definidos en el esquema `Auxiliar`. | `Auxiliar.Booking_status` |
| Catálogos | Tablas de códigos editables desde el ERP, con `Name` y `Name_en`. | `Booking_channel`, `Customer_reason` |

Los nombres técnicos están en inglés y llevan comillas en SQL porque tienen mayúsculas: `"Booking"."Booking"."Status"`.

## 2.4 Áreas funcionales

| Esquema | Menú del ERP | Entidades | Contenido |
|---|---|---|---|
| `Provider` | Propietarios | 12 | Propietarios y prestadores de servicios, contactos, documentos, plantillas de contrato, numeración de facturas, marketplaces y sus facturas. |
| `Customer` | Clientes | 10 | Clientes, contactos, documentos y tipos de documento, favoritos y emails enviados. |
| `Geo` | Ubicaciones | 7 | Países, provincias, localidades, barrios, oficinas y sus textos para la web. |
| `Building` | Edificios | 10 | Edificios, tipos, servicios, transportes, documentos, valoraciones y textos para la web. |
| `Resource` | Activos | 21 | Recursos (pisos, habitaciones, plazas y otros), tipologías, características, inventario, disponibilidad, estados, precios históricos, forecast y valoraciones. |
| `Booking` | Reservas | 35 | Reservas B2C, de grupo y LAU, con sus precios, servicios, documentos, alternativas, rooming, cuestionarios, logs y catálogos; tabla interna de disponibilidad. |
| `Billing` | Facturación | 13 | Facturas y líneas, cobros, medios de pago, productos, impuestos, tarifas, precios base y promociones. |
| `Marketing` | Marketing | 24 | Contenidos de las webs: imágenes, textos, blog, preguntas frecuentes, socios, testimonios, equipo, banners, redes sociales. |
| `Auxiliar` | Auxiliares | 11 | Catálogos generales (marcas, escuelas, géneros, idiomas, tipos de identificación, festivos, horarios, IPC) y las listas de valores. |
| `Batch` | Procesos | 1 | Ficheros Excel subidos para carga masiva. |
| `Admin` | Administración | 9 | Usuarios y roles del personal, plantillas de email y sus copias, parámetros, ficheros, notificaciones y log de cambios. |

El menú *Dashboards* no tiene tablas propias: agrupa los enlaces al backoffice complementario.

## 2.5 Entidades principales y relaciones

![Modelo de datos – visión general](../diagramas/er/ER%20general.png)

Cada área tiene además su propio diagrama, con todas sus entidades y sus relaciones con las entidades principales de otras áreas: `knowledge/diagramas/er/ER <esquema>.png` (las reservas, divididas en B2C, B2B y LAU y otros). Se incluyen en el *Anexo. Diccionario de datos*, al inicio de cada esquema.

### Inventario

```
Location (localidad) ─< District (barrio) ─< Building (edificio) ─< Resource (recurso)
                                                                     │
                                       Resource (piso) ─< Resource (habitación) ─< Resource (plaza)
```

- **`Building`** pertenece a un barrio (`District_id`), a una marca (`Segment_id`) y a un tipo (`Building_type_id`).
- **`Resource`** pertenece a un edificio y se enlaza consigo mismo para formar la jerarquía: una habitación apunta a su piso (`Flat_id`) y una plaza a su piso y a su habitación (`Room_id`). Tiene propietario (`Owner_id`) y prestador de servicios (`Service_id`), ambos en `Provider`, tipología de piso y de plaza, tarifa (`Rate_id`), estado (`Status_id`) y uso (`Usage_id`). Es una de las entidades más grandes, con 78 atributos.
- **`Resource_availability`** guarda los periodos en que un recurso no está disponible (obras, contratos de larga duración, bloqueos).
- **`Booking_detail`** es una tabla interna que reúne la ocupación de cada recurso por reservas B2C, grupos y bloqueos. La mantienen los triggers y la usan la validación de solapes, el planning y la disponibilidad de las webs.

### Personas y empresas

- **`Customer`** es tanto el residente (B2C) como el pagador de un grupo (B2B). Tiene datos de identificación, contacto, facturación, banco, tutor y firmante, y el usuario de acceso al portal.
- **`Provider`** son los propietarios y prestadores de servicios. Define los productos que factura por renta y por servicios (`Rent_product_id`, `Service_product_id`), su terminal de pago y si emite factura o recibo.
- **`Agent`** son los marketplaces.

### Reservas

| Entidad | Relaciones principales |
|---|---|
| **`Booking`** (reserva B2C, 106 atributos) | Cliente, edificio, tipología solicitada, recurso asignado, canal, referencia, motivo, escuela, marketplace, promoción, opciones de check-in/check-out. Se enlaza consigo misma para los cambios de habitación (`Origin_id`, `Destination_id`) y las reservas vinculadas (`Link_id`), y con un grupo (`Master_id`). |
| **`Booking_group`** (reserva B2B, 53 atributos) | Pagador (`Payer_id`, en `Customer`), edificio, marketplace. Sus plazas están en `Booking_group_rooms` y sus residentes en `Booking_group_rooming`. |
| **`Booking_other`** (reserva LAU y otros, 63 atributos) | Cliente, recurso, subtipo de inquilino, producto, medio de pago y mes de actualización del IPC. |

Cada tipo de reserva tiene sus tablas dependientes: precios mensuales (`Booking_price`, `Booking_group_price`), servicios adicionales (`Booking_service`, `Booking_group_service`, `Booking_other_service`) y documentos. La reserva B2C tiene además alternativas (`Booking_option`), cuestionarios y respuestas, fotos y un log de cambios (`Booking_log`).

### Precios

- **`Pricing_detail`** (precio base): por edificio, tipología de piso, tipología de plaza y año.
- **`Pricing_rate`** (tarifa): nivel de precio que se asigna a cada recurso.
- **`Promotion`**, con sus edificios (`Promotion_building`) y tipologías (`Promotion_place`).
- **`Resource_price`**: histórico de precios por recurso.

### Facturación

```
Invoice (factura) ─< Invoice_line (línea) >─ Product (producto) >─ Tax (impuesto)
   │
   └─ Payment (cobro)
```

- **`Invoice`** la emite un proveedor (`Provider_id`) a un cliente (`Customer_id`) y se asocia a una reserva B2C, de grupo o LAU. Puede tener un cobro asociado (`Payment_id`).
- **`Invoice_line`** detalla los conceptos: producto, impuesto, recurso e importe, y el management fee de la línea.
- **`Payment`** es lo que el cliente debe pagar, asociado al cliente y a una reserva. Registra el medio de pago, el terminal y la fecha de cobro.

## 2.6 Listas de valores

Las 37 listas de valores fijan los estados y tipos que usan las reglas de negocio. Las más relevantes:

| Lista | Valores | Uso |
|---|---|---|
| `Booking_status` | 21 estados, de `solicitud` a `finalizada` | Estado de la reserva B2C. |
| `Group_status` | `grupobloqueado`, `grupoconfirmado`, `inhouse`, `revision`, `devolvergarantia`, `finalizada`, `cancelada` | Estado de la reserva de grupo. |
| `Rooming_status` | `checkin`, `inhouse`, `checkout`, `revisada` | Estado de cada residente de un grupo. |
| `Resource_type` | `piso`, `habitacion`, `plaza`, `comun`, `local`, `parking`, `trastero`, `sala` | Tipo de recurso. |
| `Other_booking_type` | `lau`, `retail`, `parking`, `coworking` | Tipo de reserva LAU y otros. |
| `Lock_type` | `FTC`, `LTC`, `LTNC`, `CAPEX`, `PRECAPEX` | Tipo de bloqueo de disponibilidad. |
| `Limit_type` | `libre`, `lau`, `indice` | Régimen de renta del recurso. |
| `Billing_type` | `mes`, `quincena`, `proporcional`, `na` | Facturación de meses incompletos. |
| `Bill_type` | `factura`, `recibo`, `rectificativa` | Tipo de documento de cobro. |
| `Payment_type` | `booking`, `deposito`, `servicios`, `checkin`, `checkout` | Concepto del cobro. |
| `Pos_type` | `cotown`, `vandor`, `delegado` | Terminal de pago. |
| `Contract_status` | `sent`, `delivered`, `completed`, `declined`, `expired`, `voided`, `pending`, `other` | Estado del contrato en DocuSign. |
| `Incasol_type` | `pendiente`, `depositada`, `reclamada`, `devuelta` | Situación de la fianza legal. |

La lista completa, con todos sus valores, está en el diccionario de datos.

## 2.7 Entidades sin uso

Algunas entidades existen en el modelo pero no se usan:

| Entidad | Situación |
|---|---|
| `Booking.Booking_search` | Marcada como futura (búsquedas guardadas). |
| `Marketing.Contact` | Marcada como futura. |
| `Customer.Customer_status`, `Customer.Customer_resident_status` | Marcadas para borrar. |
| `Marketing.Media_country`, `Marketing.Media_province` | Marcadas como no usar. |

## 2.8 Fuentes

| Tema | Dónde está |
|---|---|
| Modelo completo | Esquema `Models` de la base de datos de Airflows |
| Diccionario de datos | *Anexo. Diccionario de datos*, generado automáticamente a partir de los metadatos de Airflows |
| Diseño original (2023, referencia) | Documentación de diseño de Experis: *Modelo de datos v1.2* |

## 2.9 Pendiente de confirmar

No hay puntos pendientes.
