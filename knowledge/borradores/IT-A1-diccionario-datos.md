# Anexo. Diccionario de datos

> Generado automáticamente a partir de los metadatos de Airflows (esquema `Models`). No editar a mano: se regenera a partir de los metadatos cuando cambia el modelo.

153 entidades y 2174 atributos, agrupados por esquema. Para cada atributo: nombre técnico, etiqueta en el ERP, tipo, si es obligatorio (●) y, en su caso, la entidad a la que referencia o los valores posibles. Se omiten los campos que tienen todas las entidades (`id`, `Created_at`, `Created_by`, `Updated_at`, `Updated_by` y `Search`), descritos en el capítulo *Modelo de datos*, apartado *Convenciones*.

## Esquema `Provider` — Propietarios

![ER Provider](../diagramas/er/ER%20Provider.png)

| Entidad | Nombre en el ERP | Descripción |
|---|---|---|
| `Provider` | Propietario | Personas físicas o jurídicas que ostentan la propiedad de los recursos gestionados, proporcionan servicios, y pueden emitir facturas. |
| `Provider_bill` | Numero de factura | Numeración de facturas por emisor y año |
| `Provider_contact` | Contacto | Personas físicas de contacto de un proveedor, si es persona jurídica. Un proveedor puede tener varias personas de contacto. |
| `Provider_doc` | Documento | Documentos asociados a un proveedor. Un proveedor puede tener varios documentos. |
| `Provider_template` | Plantilla de contrato | Plantillas de contrato para cada propietario o empresa de servicios. Un proveedor puede tener varias plantillas de contrato. |
| `Provider_type` | Tipo de proveedor | Clasificación de los proveedores: propietarios y empresas de servicios. Tabla de códigos |
| `Provider_contact_type` | Tipo de contacto | Tipos de contacto para proveedores |
| `Provider_doc_type` | Tipo de documento | Categorización de los tipos de documentos que se pueden requerir de un proveedor: contratos, justificantes, etc. Tabla de códigos, asociado a un documento de proveedor. |
| `Provider_contract` | Plantilla de contrato | Plantillas de contrato |
| `Agent` | Marketplace | Marketplaces |
| `Agent_type` | Tipo de marketplace | Tipos de marketplaces |
| `Agent_bills` | Factura | Facturas de los marketplaces |

### `Provider.Provider` — Propietario

Personas físicas o jurídicas que ostentan la propiedad de los recursos gestionados, proporcionan servicios, y pueden emitir facturas.

| Atributo | Etiqueta | Tipo | Oblig. | Referencia / valores |
|---|---|---|---|---|
| `Provider_type_id` | Tipo de proveedor | Entero | ● | → `Provider.Provider_type` |
| `Type` | Persona/Empresa | Lista de valores | ● | persona, empresa |
| `Id_type_id` | Tipo de documento | Entero | ● | → `Auxiliar.Id_type` |
| `Document` | Documento de identidad | Texto | ● |  |
| `Name` | Nombre | Texto | ● |  |
| `Comments` | Comentarios | Texto |  |  |
| `Email` | Email | Texto | ● |  |
| `User_name` | Usuario | Texto |  |  |
| `Phones` | Teléfonos | Texto |  |  |
| `Address` | Dirección | Texto | ● |  |
| `Zip` | Código postal | Texto | ● |  |
| `City` | Ciudad | Texto | ● |  |
| `Province` | Provincia | Texto | ● |  |
| `Country_id` | País | Entero | ● | → `Geo.Country` |
| `Bill_pattern` | Formato nº factura | Texto |  |  |
| `Credit_pattern` | Formato nº factura rectificativa | Texto |  |  |
| `Receipt_pattern` | Formato nº recibo | Texto |  |  |
| `LAU_bill_pattern` | Formato nº factura LAU | Texto |  |  |
| `LAU_credit_pattern` | Formato nº factura LAU rectificativa | Texto |  |  |
| `SAP_code` | Código SAP | Texto |  |  |
| `Pos` | TPV | Lista de valores |  | delegado, cotown, vandor |
| `Bill_line` | Texto pie factura | Texto |  |  |
| `Receipt` | Emite recibo, no factura | Sí/No | ● |  |
| `IBAN` | IBAN | Texto |  |  |
| `Rent_product_id` | Producto renta | Entero |  | → `Billing.Product` |
| `Service_product_id` | Producto servicios | Entero |  | → `Billing.Product` |
| `Create_user` | Crear usuario | Texto |  |  |

### `Provider.Provider_bill` — Numero de factura

Numeración de facturas por emisor y año

| Atributo | Etiqueta | Tipo | Oblig. | Referencia / valores |
|---|---|---|---|---|
| `Provider_id` | Proveedor | Entero |  | → `Provider.Provider` |
| `Year` | Año | Entero |  |  |
| `Bill_number` | Nº de factura | Entero |  |  |
| `Credit_number` | Nº de factura rectificativa | Entero |  |  |
| `LAU_bill_number` | Nº de factura LAU | Entero |  |  |
| `LAU_credit_number` | Nº de factura rectificativa LAU | Entero |  |  |
| `Receipt_number` | Nº de recibo | Entero |  |  |

### `Provider.Provider_contact` — Contacto

Personas físicas de contacto de un proveedor, si es persona jurídica. Un proveedor puede tener varias personas de contacto.

| Atributo | Etiqueta | Tipo | Oblig. | Referencia / valores |
|---|---|---|---|---|
| `Provider_id` | Proveedor | Entero | ● | → `Provider.Provider` |
| `Provider_contact_type_id` | Tipo de contacto | Entero |  | → `Provider.Provider_contact_type` |
| `Id_type_id` | Tipo de documento | Entero |  | → `Auxiliar.Id_type` |
| `Document` | Documento de identidad | Texto |  |  |
| `Name` | Nombre y apellidos | Texto | ● |  |
| `Email` | Email | Texto |  |  |
| `Phones` | Teléfonos | Texto |  |  |
| `Signature` | Firma | Documento |  |  |

### `Provider.Provider_doc` — Documento

Documentos asociados a un proveedor. Un proveedor puede tener varios documentos.

| Atributo | Etiqueta | Tipo | Oblig. | Referencia / valores |
|---|---|---|---|---|
| `Provider_id` | Proveedor | Entero | ● | → `Provider.Provider` |
| `Provider_doc_type_id` | Tipo de documento | Entero | ● | → `Provider.Provider_doc_type` |
| `Name` | Nombre | Texto | ● |  |
| `Expiry_date` | Fecha de expiración | Fecha |  |  |
| `Document` | Documento | Documento |  |  |

### `Provider.Provider_template` — Plantilla de contrato

Plantillas de contrato para cada propietario o empresa de servicios. Un proveedor puede tener varias plantillas de contrato.

| Atributo | Etiqueta | Tipo | Oblig. | Referencia / valores |
|---|---|---|---|---|
| `Provider_id` | Proveedor | Entero | ● | → `Provider.Provider` |
| `Type` | Tipo | Lista de valores | ● | residencia, otro, b2b_habitacion, b2b_piso, b2c_habitacion, b2c_piso |
| `Book_type` | Tipo de reserva | Texto |  |  |
| `Location_id` | Ciudad | Entero |  | → `Geo.Location` |
| `Name` | Nombre | Texto | ● |  |
| `Contract_id` | Contrato | Entero |  | → `Provider.Provider_contract` |
| `Active` | Activo | Sí/No | ● |  |

### `Provider.Provider_type` — Tipo de proveedor

Clasificación de los proveedores: propietarios y empresas de servicios. Tabla de códigos

| Atributo | Etiqueta | Tipo | Oblig. | Referencia / valores |
|---|---|---|---|---|
| `Name` | Nombre (español) | Texto | ● |  |
| `Name_en` | Nombre (inglés) | Texto | ● |  |

### `Provider.Provider_contact_type` — Tipo de contacto

Tipos de contacto para proveedores

| Atributo | Etiqueta | Tipo | Oblig. | Referencia / valores |
|---|---|---|---|---|
| `Name` | Nombre | Texto | ● |  |

### `Provider.Provider_doc_type` — Tipo de documento

Categorización de los tipos de documentos que se pueden requerir de un proveedor: contratos, justificantes, etc. Tabla de códigos, asociado a un documento de proveedor.

| Atributo | Etiqueta | Tipo | Oblig. | Referencia / valores |
|---|---|---|---|---|
| `Name` | Nombre (español) | Texto | ● |  |
| `Name_en` | Nombre (inglés) | Texto | ● |  |
| `Provider_type_id` | Tipo de proveedor | Entero |  | → `Provider.Provider_type` |
| `Mandatory` | Obligatorio | Sí/No | ● |  |

### `Provider.Provider_contract` — Plantilla de contrato

Plantillas de contrato

| Atributo | Etiqueta | Tipo | Oblig. | Referencia / valores |
|---|---|---|---|---|
| `Name` | Nombre | Texto | ● |  |
| `Template` | Contenido | Texto | ● |  |
| `Annex` | Anexo inglés | Texto |  |  |

### `Provider.Agent` — Marketplace

Marketplaces

| Atributo | Etiqueta | Tipo | Oblig. | Referencia / valores |
|---|---|---|---|---|
| `Name` | Nombre | Texto | ● |  |
| `Active` | Activo | Sí/No | ● |  |
| `Contact` | Contacto | Texto |  |  |
| `Web` | Web | Texto |  |  |
| `Email` | Email | Texto |  |  |
| `Phones` | Teléfonos | Texto |  |  |
| `Agent_type_id` | Tipo de marketplace | Entero |  | → `Provider.Agent_type` |
| `Payment_method` | Metodo de pago | Lista de valores |  | firstrent, debit, transfer |
| `Commision_percent` | Comisión (%) | Decimal |  |  |
| `Commision_value` | Comisión (valor fijo) | Decimal |  |  |
| `Comments` | Observaciones | Texto |  |  |

### `Provider.Agent_type` — Tipo de marketplace

Tipos de marketplaces

| Atributo | Etiqueta | Tipo | Oblig. | Referencia / valores |
|---|---|---|---|---|
| `Name` | Nombre (español) | Texto | ● |  |
| `Name_en` | Nombre (inglés) | Texto | ● |  |

### `Provider.Agent_bills` — Factura

Facturas de los marketplaces

| Atributo | Etiqueta | Tipo | Oblig. | Referencia / valores |
|---|---|---|---|---|
| `Agent_id` | Marketplace | Entero | ● | → `Provider.Agent` |
| `Concept` | Concepto | Texto | ● |  |
| `Amount` | Importe | Decimal | ● |  |
| `Date_from` | Fecha desde | Fecha | ● |  |
| `Date_to` | Fecha hasta | Fecha | ● |  |

## Esquema `Customer` — Clientes

![ER Customer](../diagramas/er/ER%20Customer.png)

| Entidad | Nombre en el ERP | Descripción |
|---|---|---|
| `Customer` | Cliente | Personas físicas o jurídicas que contratan, pagan o utilizan, los servicios de Cotown |
| `Customer_contact` | Contacto | Personas físicas de contacto de un cliente, si es persona jurídica. Un cliente puede tener varios contactos, |
| `Customer_doc` | Documento de cliente | Documentos asociados a cada cliente. Un cliente puede tener varios documentos. |
| `Customer_email` | Email | Emails enviados a los clientes |
| `Customer_fav` | Favorito | Favoritos de un cliente |
| `Customer_contact_type` | Tipo de contacto | Tipos de contactos para clientes |
| `Customer_doc_option` | Opción | Categorización de los subtipos de documentos que se pueden requerir de un cliente |
| `Customer_doc_type` | Tipo de documento | Categorización de los tipos de documentos que se pueden requerir de un cliente: DNI (ambas caras), nómina, matrícula académica, etc. Tabla de códigos, asociado a un documento de cliente. |
| `Customer_resident_status` | Estado de residente | BORRAR |
| `Customer_status` | Estado de cliente | BORRAR |

### `Customer.Customer` — Cliente

Personas físicas o jurídicas que contratan, pagan o utilizan, los servicios de Cotown

| Atributo | Etiqueta | Tipo | Oblig. | Referencia / valores |
|---|---|---|---|---|
| `Photo` | Foto | Documento |  |  |
| `Type` | Persona/Empresa | Lista de valores | ● | persona, empresa |
| `Id_type_id` | Tipo de documento | Entero |  | → `Auxiliar.Id_type` |
| `Document` | Documento de identidad | Texto |  |  |
| `Name` | Nombre y apellidos o Razón social | Texto | ● |  |
| `Lang` | Idioma preferido | Lista de valores | ● | es, en |
| `User_name` | Usuario | Texto |  |  |
| `Create_user` | Crear usuario | Sí/No |  |  |
| `Signer_name` | Firmante | Texto | ● |  |
| `Signer_id_type_id` | Tipo de documento | Entero |  | → `Auxiliar.Id_type` |
| `Signer_document` | Documento de identidad | Texto |  |  |
| `Email` | Email | Texto | ● |  |
| `Phones` | Teléfonos | Texto |  |  |
| `Address` | Dirección | Texto |  |  |
| `Zip` | Código postal | Texto |  |  |
| `City` | Ciudad | Texto |  |  |
| `Province` | Provincia | Texto |  |  |
| `Country_id` | País | Entero |  | → `Geo.Country` |
| `Gender_id` | Género | Entero |  | → `Auxiliar.Gender` |
| `Language_id` | Idioma | Entero |  | → `Auxiliar.Language` |
| `Nationality_id` | Nacionalidad | Entero |  | → `Geo.Country` |
| `Country_origin_id` | País de origen | Entero |  | → `Geo.Country` |
| `Payment_method_id` | Medio de pago | Entero |  | → `Billing.Payment_method` |
| `Birth_date` | Fecha de nacimiento | Fecha |  |  |
| `IBAN` | IBAN para domiciliación | Texto |  |  |
| `Same_account` | Misma cuenta para devolución | Sí/No | ● |  |
| `GDPR` | GDPR | Sí/No |  |  |
| `Comments` | Comentarios | Texto |  |  |
| `Tutor_id_type_id` | Tipo de documento | Entero |  | → `Auxiliar.Id_type` |
| `Tutor_document` | Documento de identidad | Texto |  |  |
| `Tutor_name` | Nombre | Texto |  |  |
| `Tutor_email` | Email | Texto |  |  |
| `Bank_account` | IBAN/Cuenta para devolución de depósito | Texto |  |  |
| `Tutor_phones` | Teléfonos | Texto |  |  |
| `Swift` | Swift/BIC | Texto |  |  |
| `Bank_holder` | Titular | Texto |  |  |
| `Bank_name` | Nombre del banco | Texto |  |  |
| `Bank_address` | Dirección del titular | Texto |  |  |
| `Bank_city` | Ciudad del titular | Texto |  |  |
| `Bank_country_id` | País del titular | Entero |  | → `Geo.Country` |
| `Billing_type` | Persona/Empresa | Lista de valores |  | persona, empresa |
| `Billing_id_type_id` | Tipo de documento | Entero |  | → `Auxiliar.Id_type` |
| `Billing_document` | Documento de identidad | Texto |  |  |
| `Billing_name` | Nombre | Texto |  |  |
| `Billing_address` | Dirección | Texto |  |  |
| `Billing_zip` | Código postal | Texto |  |  |
| `Billing_city` | Ciudad | Texto |  |  |
| `Billing_province` | Provincia | Texto |  |  |
| `Billing_country_id` | País | Entero |  | → `Geo.Country` |
| `Bill_email_to` | Enviar factura a | Texto |  |  |
| `Bill_email_cc` | Enviar factura cc | Texto |  |  |
| `Black_list` | Lista negra | Sí/No | ● |  |
| `Black_reason` | Motivo | Texto |  |  |
| `Bill_rooming_list` | Rooming list en facturas | Sí/No |  |  |
| `School_id` | Escuela | Entero |  | → `Auxiliar.School` |

### `Customer.Customer_contact` — Contacto

Personas físicas de contacto de un cliente, si es persona jurídica. Un cliente puede tener varios contactos,

| Atributo | Etiqueta | Tipo | Oblig. | Referencia / valores |
|---|---|---|---|---|
| `Customer_id` | Cliente | Entero | ● | → `Customer.Customer` |
| `Customer_contact_type_id` | Tipo de contacto | Entero | ● | → `Customer.Customer_contact_type` |
| `Name` | Nombre y apellidos | Texto | ● |  |
| `Email` | Email | Texto |  |  |
| `Phones` | Teléfonos | Texto |  |  |

### `Customer.Customer_doc` — Documento de cliente

Documentos asociados a cada cliente. Un cliente puede tener varios documentos.

| Atributo | Etiqueta | Tipo | Oblig. | Referencia / valores |
|---|---|---|---|---|
| `Customer_id` | Cliente | Entero | ● | → `Customer.Customer` |
| `Booking_id` | Reserva B2C | Entero |  | → `Booking.Booking` |
| `Customer_doc_type_id` | Tipo de documento | Entero | ● | → `Customer.Customer_doc_type` |
| `Customer_doc_option_id` | Opción | Entero |  | → `Customer.Customer_doc_option` |
| `Document` | Documento (anverso) | Documento |  |  |
| `Document_back` | Documento (reverso) | Documento |  |  |
| `Expiry_date` | Fecha de expiracion | Fecha |  |  |
| `Approved` | Aprobado | Sí/No |  |  |

### `Customer.Customer_email` — Email

Emails enviados a los clientes

| Atributo | Etiqueta | Tipo | Oblig. | Referencia / valores |
|---|---|---|---|---|
| `Customer_id` | Cliente | Entero | ● | → `Customer.Customer` |
| `From_type` | De | Lista de valores |  | cotown, vandor |
| `Sent_at` | Enviado | Fecha y hora |  |  |
| `Template` | Plantilla | Texto |  |  |
| `Entity_id` | Clave | Entero |  |  |
| `Cc` | CC | Texto |  |  |
| `Cco` | CCO | Texto |  |  |
| `Subject` | Asunto | Texto |  |  |
| `Body` | Mensaje | Texto |  |  |

### `Customer.Customer_fav` — Favorito

Favoritos de un cliente

| Atributo | Etiqueta | Tipo | Oblig. | Referencia / valores |
|---|---|---|---|---|
| `Customer_id` | Cliente | Entero | ● | → `Customer.Customer` |
| `Building_id` | Edificio | Entero |  | → `Building.Building` |
| `Flat_type_id` | Tipo de piso | Entero |  | → `Resource.Resource_flat_type` |
| `Place_type_id` | Tipo de plaza | Entero |  | → `Resource.Resource_place_type` |

### `Customer.Customer_contact_type` — Tipo de contacto

Tipos de contactos para clientes

| Atributo | Etiqueta | Tipo | Oblig. | Referencia / valores |
|---|---|---|---|---|
| `Internal_area` | Área interna | Sí/No | ● |  |
| `Name` | Nombre (español) | Texto | ● |  |
| `Name_en` | Nombre (inglés) | Texto | ● |  |

### `Customer.Customer_doc_option` — Opción

Categorización de los subtipos de documentos que se pueden requerir de un cliente

| Atributo | Etiqueta | Tipo | Oblig. | Referencia / valores |
|---|---|---|---|---|
| `Customer_doc_type_id` | Tipo | Entero | ● | → `Customer.Customer_doc_type` |
| `Name` | Nombre (español) | Texto | ● |  |
| `Name_en` | Nombre (inglés) | Texto | ● |  |

### `Customer.Customer_doc_type` — Tipo de documento

Categorización de los tipos de documentos que se pueden requerir de un cliente: DNI (ambas caras), nómina, matrícula académica, etc. Tabla de códigos, asociado a un documento de cliente.

| Atributo | Etiqueta | Tipo | Oblig. | Referencia / valores |
|---|---|---|---|---|
| `Name` | Nombre (español) | Texto | ● |  |
| `Name_en` | Nombre (inglés) | Texto | ● |  |
| `Description` | Descripción (español) | Texto |  |  |
| `Description_en` | Descripción (inglés) | Texto |  |  |
| `Type` | Tipo | Lista de valores |  | identificacion, motivo, otros |
| `Id_type_id` | Tipo de documento | Entero |  | → `Auxiliar.Id_type` |
| `Reason_id` | Motivo de estancia | Entero |  | → `Booking.Customer_reason` |
| `Images` | Nº imágenes | Entero |  |  |
| `Mandatory` | Obligatorio? | Sí/No | ● |  |
| `Expires` | Expira? | Sí/No | ● |  |
| `Multiple` | Mutiple? | Sí/No |  |  |

### `Customer.Customer_resident_status` — Estado de residente

BORRAR

| Atributo | Etiqueta | Tipo | Oblig. | Referencia / valores |
|---|---|---|---|---|
| `Name` | Nombre (español) | Texto | ● |  |
| `Name_en` | Nombre (inglés) | Texto | ● |  |

### `Customer.Customer_status` — Estado de cliente

BORRAR

| Atributo | Etiqueta | Tipo | Oblig. | Referencia / valores |
|---|---|---|---|---|
| `Name` | Nombre (español) | Texto | ● |  |
| `Name_en` | Nombre (inglés) | Texto | ● |  |

## Esquema `Geo` — Ubicaciones

![ER Geo](../diagramas/er/ER%20Geo.png)

| Entidad | Nombre en el ERP | Descripción |
|---|---|---|
| `Country` | País | Inventario de países del mundo, para indicar la dirección de origen o nacionalidad de los residentes. |
| `District_text` | Textos web | Textos de barrios |
| `Province` | Provincia | Inventario de provincias o regiones de los países. Un país puede tener varias provincias. Sólo para los recursos. |
| `Location` | Localidad | Diferentes ubicaciones donde pueden encontrarse activos. |
| `Location_text` | Texto | Textos de localidades |
| `District` | Barrio | Barrios, distritos o zonas en que pueden dividirse las localizaciones o ciudades. |
| `Office` | Oficina | Oficinas de Cotown |

### `Geo.Country` — País

Inventario de países del mundo, para indicar la dirección de origen o nacionalidad de los residentes.

| Atributo | Etiqueta | Tipo | Oblig. | Referencia / valores |
|---|---|---|---|---|
| `Code` | Código | Texto | ● |  |
| `Alpha3` | Alpha-3 | Texto |  |  |
| `Num` | Numérico | Entero |  |  |
| `Tld` | TLD | Texto |  |  |
| `Name` | Nombre (español) | Texto | ● |  |
| `Name_en` | Nombre (inglés) | Texto | ● |  |
| `Continent` | Continente | Texto |  |  |
| `Prefix` | Prefijo telefónico | Texto |  |  |
| `Sepa` | SEPA | Sí/No | ● |  |

### `Geo.District_text` — Textos web

Textos de barrios

| Atributo | Etiqueta | Tipo | Oblig. | Referencia / valores |
|---|---|---|---|---|
| `District_id` | Distrito | Entero | ● | → `Geo.District` |
| `Segment_id` | Web | Entero | ● | → `Auxiliar.Segment` |
| `Description` | Descripción (español) | Texto |  |  |
| `Description_en` | Descripción (inglés) | Texto |  |  |

### `Geo.Province` — Provincia

Inventario de provincias o regiones de los países. Un país puede tener varias provincias. Sólo para los recursos.

| Atributo | Etiqueta | Tipo | Oblig. | Referencia / valores |
|---|---|---|---|---|
| `Country_id` | País | Entero | ● | → `Geo.Country` |
| `Name` | Nombre | Texto | ● |  |

### `Geo.Location` — Localidad

Diferentes ubicaciones donde pueden encontrarse activos.

| Atributo | Etiqueta | Tipo | Oblig. | Referencia / valores |
|---|---|---|---|---|
| `Province_id` | Provincia | Entero | ● | → `Geo.Province` |
| `Code` | Código | Texto |  |  |
| `Published` | Publicar en web | Sí/No | ● |  |
| `Name` | Nombre (español) | Texto | ● |  |
| `Name_en` | Nombre (inglés) | Texto | ● |  |
| `Description` | Entradilla (español) | Texto |  |  |
| `Description_en` | Entradilla (inglés) | Texto |  |  |
| `Details` | Detalles (español) | Texto |  |  |
| `Details_en` | Detalles (inglés) | Texto |  |  |

### `Geo.Location_text` — Texto

Textos de localidades

| Atributo | Etiqueta | Tipo | Oblig. | Referencia / valores |
|---|---|---|---|---|
| `Location_id` | Localidad | Entero | ● | → `Geo.Location` |
| `Segment_id` | Web | Entero | ● | → `Auxiliar.Segment` |
| `Title` | Título habitaciones (español) | Texto |  |  |
| `Title_en` | Título habitaciones (inglés) | Texto |  |  |
| `Title_flat` | Título pisos (español) | Texto |  |  |
| `Title_flat_en` | Título pisos (inglés) | Texto |  |  |
| `Description` | Descripción (español) | Texto |  |  |
| `Description_en` | Descripción (inglés) | Texto |  |  |

### `Geo.District` — Barrio

Barrios, distritos o zonas en que pueden dividirse las localizaciones o ciudades.

| Atributo | Etiqueta | Tipo | Oblig. | Referencia / valores |
|---|---|---|---|---|
| `Location_id` | Localidad | Entero | ● | → `Geo.Location` |
| `Name` | Nombre | Texto | ● |  |
| `Description` | Detalles (español) | Texto |  |  |
| `Description_en` | Detalles (inglés) | Texto |  |  |

### `Geo.Office` — Oficina

Oficinas de Cotown

| Atributo | Etiqueta | Tipo | Oblig. | Referencia / valores |
|---|---|---|---|---|
| `Segment_id` | Web | Entero | ● | → `Auxiliar.Segment` |
| `Location` | Localidad | Texto | ● |  |
| `Address` | Dirección | Texto | ● |  |
| `Email` | Email | Texto |  |  |
| `Phone` | Teléfonos | Texto |  |  |
| `Lat_lon` | Posición geográfica | Coordenadas |  |  |
| `Image` | Imagen | Documento |  |  |

## Esquema `Building` — Edificios

![ER Building](../diagramas/er/ER%20Building.png)

| Entidad | Nombre en el ERP | Descripción |
|---|---|---|
| `Building` | Edificio | Dirección en la que se encuentran recursos de tipo piso, habitación o plaza. |
| `Building_doc` | Documento | Categorización de los tipos de documentos de edificios |
| `Building_service` | Servicio | Disponibilidad de tipos de servicio para cada edificio. Un edificio puede tener varios servicios. |
| `Building_text` | Textos web | Textos de edificios |
| `Building_transport` | Transporte | Disponibilidad de tipos de transporte para cada edificio. Un edificio puede tener varios transportes. |
| `Building_value` | Valoración | Valoración histórica de edificios |
| `Building_type` | Tipo de venta | Tipos de edificios. Tabla de códigos, asociado a edificio. |
| `Building_service_type` | Tipo de servicio | Tipos de servicios ofrecidos en cada edificio. Tabla de códigos, asociada a servicios por edificio. |
| `Building_transport_type` | Tipo de transporte | Tipos de transporte para acceder a los edificios. Tabla de códigos, asociado a transporte por edificio. |
| `Building_doc_type` | Tipo de documento | Documentos asociados a cada edificio. Un edificio puede tener varios documentos. |

### `Building.Building` — Edificio

Dirección en la que se encuentran recursos de tipo piso, habitación o plaza.

| Atributo | Etiqueta | Tipo | Oblig. | Referencia / valores |
|---|---|---|---|---|
| `Code` | Código | Texto | ● |  |
| `Description` | Descripción piso compartido (español) | Texto |  |  |
| `Description_private` | Descripción apartamento privado (español) | Texto |  |  |
| `Order` | Orden | Entero |  |  |
| `Description_en` | Descripción piso compartido (inglés) | Texto |  |  |
| `Description_private_en` | Descripción apartamento privado (inglés) | Texto |  |  |
| `Name` | Nombre | Texto | ● |  |
| `Active` | Activo | Sí/No | ● |  |
| `Details` | Detalles piso compartido (español) | Texto |  |  |
| `Details_private` | Detalles apartamento privado (español) | Texto |  |  |
| `Details_en` | Detalles piso compartido (inglés) | Texto |  |  |
| `Details_private_en` | Detalles apartamento privado (inglés) | Texto |  |  |
| `Start_date` | Fecha inicio/compra | Fecha |  |  |
| `Estabilised_date` | Fecha ramp-up a estabilised | Fecha |  |  |
| `Title` | Título (español) | Texto |  |  |
| `Title_private` | Título (español) | Texto |  |  |
| `Address` | Dirección | Texto | ● |  |
| `Cadastral_ref` | Referencia catastral | Texto |  |  |
| `Title_en` | Título (inglés) | Texto |  |  |
| `Title_private_en` | Título (inglés) | Texto |  |  |
| `Contract` | Emitir contratos | Sí/No | ● |  |
| `Meta_description` | Meta description (español) | Texto |  |  |
| `Meta_description_private` | Meta description (español) | Texto |  |  |
| `Zip` | Código postal | Texto | ● |  |
| `Expense_IBI` | IBI | Decimal |  |  |
| `Meta_description_en` | Meta description (inglés) | Texto |  |  |
| `Meta_description_private_en` | Meta description (inglés) | Texto |  |  |
| `Expense_HOA` | Gastos de comunidad | Decimal |  |  |
| `Header` | H1 (español) | Texto |  |  |
| `Header_private` | H1 (español) | Texto |  |  |
| `Lat_lon` | Posición geográfica | Coordenadas |  |  |
| `Header_en` | H1 (inglés) | Texto |  |  |
| `Header_private_en` | H1 (inglés) | Texto |  |  |
| `Tour` | Tour virtual piso compartido | Texto |  |  |
| `Tour_private` | Tour virtual apartamento privado | Texto |  |  |
| `Wifi_ssid` | WiFi SSID | Texto |  |  |
| `Wifi_key` | WiFi Clave | Texto |  |  |
| `Gate_mac` | Puerta - MAC | Texto |  |  |
| `Gate_phone` | Puerta - Teléfono | Texto |  |  |
| `Gate_url` | Puerta - URL | Texto |  |  |
| `Notes` | Notas (contactos de mantenimiento, emergencias 24h/llaves, asset manager…) | Texto |  |  |
| `Building_type_id` | Tipo de venta | Entero | ● | → `Building.Building_type` |
| `District_id` | Barrio | Entero | ● | → `Geo.District` |
| `Management_fee` | Management fee | Decimal |  |  |
| `Segment_id` | Marca | Entero | ● | → `Auxiliar.Segment` |

### `Building.Building_doc` — Documento

Categorización de los tipos de documentos de edificios

| Atributo | Etiqueta | Tipo | Oblig. | Referencia / valores |
|---|---|---|---|---|
| `Building_id` | Edificio | Entero | ● | → `Building.Building` |
| `Building_doc_type_id` | Tipo de documento | Entero | ● | → `Building.Building_doc_type` |
| `Description` | Descripción | Texto |  |  |
| `Document` | Documento | Documento |  |  |

### `Building.Building_service` — Servicio

Disponibilidad de tipos de servicio para cada edificio. Un edificio puede tener varios servicios.

| Atributo | Etiqueta | Tipo | Oblig. | Referencia / valores |
|---|---|---|---|---|
| `Building_id` | Edificio | Entero | ● | → `Building.Building` |
| `Service_id` | Servicio | Entero | ● | → `Building.Building_service_type` |
| `Description` | Detalles (español) | Texto |  |  |
| `Description_en` | Detalles (inglés) | Texto |  |  |

### `Building.Building_text` — Textos web

Textos de edificios

| Atributo | Etiqueta | Tipo | Oblig. | Referencia / valores |
|---|---|---|---|---|
| `Building_id` | Edificio | Entero | ● | → `Building.Building` |
| `Segment_id` | Web | Entero | ● | → `Auxiliar.Segment` |
| `Web_type` | Tipo de venta | Lista de valores | ● | compartido, privado |
| `Description` | Descripción (español) | Texto |  |  |
| `Description_en` | Descripción (inglés) | Texto |  |  |
| `Tour` | Tour virtual | Texto |  |  |
| `Title` | Título (español) | Texto |  |  |
| `Title_en` | Título (inglés) | Texto |  |  |
| `Meta_description` | Meta (español) | Texto |  |  |
| `Meta_description_en` | Meta (inglés) | Texto |  |  |
| `Header` | H1 (español) | Texto |  |  |
| `Header_en` | H1 (inglés | Texto |  |  |
| `Details` | Detalles (español) | Texto |  |  |
| `Details_en` | Detalles (inglés) | Texto |  |  |

### `Building.Building_transport` — Transporte

Disponibilidad de tipos de transporte para cada edificio. Un edificio puede tener varios transportes.

| Atributo | Etiqueta | Tipo | Oblig. | Referencia / valores |
|---|---|---|---|---|
| `Building_id` | Edificio | Entero | ● | → `Building.Building` |
| `Transport_id` | Medio de transporte | Entero | ● | → `Building.Building_transport_type` |
| `Description` | Detalles (español) | Texto |  |  |
| `Description_en` | Detalles (inglés) | Texto |  |  |

### `Building.Building_value` — Valoración

Valoración histórica de edificios

| Atributo | Etiqueta | Tipo | Oblig. | Referencia / valores |
|---|---|---|---|---|
| `Building_id` | Edificio | Entero | ● | → `Building.Building` |
| `Valuation_type` | Tipo | Lista de valores |  | eco, rics, vicente |
| `Valuation_date` | Fecha tasación | Fecha | ● |  |
| `Pre_capex_long_term` | Pre-capex indefinidos | Decimal |  |  |
| `Pre_capex_vacant` | Pre-capex vacío | Decimal |  |  |
| `Post_capex` | Post-capex | Decimal |  |  |
| `ECO_valuation` | ECO Tasación | Decimal |  |  |
| `ECO_rent_update` | ECO Act. de rentas | Decimal |  |  |
| `ECO_refinance` | ECO Residencial | Decimal |  |  |
| `RICS_valuation` | RICS | Decimal |  |  |

### `Building.Building_type` — Tipo de venta

Tipos de edificios. Tabla de códigos, asociado a edificio.

| Atributo | Etiqueta | Tipo | Oblig. | Referencia / valores |
|---|---|---|---|---|
| `Name` | Nombre (español) | Texto | ● |  |
| `Name_en` | Nombre (inglés) | Texto | ● |  |
| `Tax_id` | Tipo de impuesto | Entero |  | → `Billing.Tax` |
| `Icon` | Icono | Documento |  |  |
| `Image` | Imagen | Documento |  |  |

### `Building.Building_service_type` — Tipo de servicio

Tipos de servicios ofrecidos en cada edificio. Tabla de códigos, asociada a servicios por edificio.

| Atributo | Etiqueta | Tipo | Oblig. | Referencia / valores |
|---|---|---|---|---|
| `Name` | Nombre (español) | Texto | ● |  |
| `Name_en` | Nombre (inglés) | Texto | ● |  |
| `Description` | Descripción (español) | Texto |  |  |
| `Description_en` | Descripción (inglés) | Texto |  |  |
| `Published` | Publicar en web | Sí/No | ● |  |
| `Contract` | Incorporar en contrato | Sí/No | ● |  |

### `Building.Building_transport_type` — Tipo de transporte

Tipos de transporte para acceder a los edificios. Tabla de códigos, asociado a transporte por edificio.

| Atributo | Etiqueta | Tipo | Oblig. | Referencia / valores |
|---|---|---|---|---|
| `Name` | Nombre (español) | Texto | ● |  |
| `Name_en` | Nombre (inglés) | Texto | ● |  |
| `Icon` | Icono | Documento |  |  |
| `Image` | Imagen | Documento |  |  |

### `Building.Building_doc_type` — Tipo de documento

Documentos asociados a cada edificio. Un edificio puede tener varios documentos.

| Atributo | Etiqueta | Tipo | Oblig. | Referencia / valores |
|---|---|---|---|---|
| `Name` | Nombre | Texto | ● |  |
| `Contract` | Adjuntar a contratos | Sí/No |  |  |

## Esquema `Resource` — Activos

![ER Resource](../diagramas/er/ER%20Resource.png)

| Entidad | Nombre en el ERP | Descripción |
|---|---|---|
| `Resource` | Recurso | Recursos de los que dispone Cotown para su alquiler. Pueden ser pisos, habitaciones o camas/plazas. |
| `Resource_amenity` | Característica | Equipamientos de los que dispone cada recurso: piso, habitación o plaza. |
| `Resource_availability` | Estado | Periodos de indisponibilidad del recurso |
| `Resource_doc` | Documento | Categorización de los tipos de documentos de recursos |
| `Resource_forecast` | Forecast | Forecast |
| `Resource_inventory` | Inventario | Elementos que forman parte del inventario de un recurso. |
| `Resource_price` | Precio | Precios históricos de los recursos |
| `Resource_stabilised` | Stabilised | Stabilised |
| `Resource_subtype_text` | Textos web | Textos de subtipos de piso |
| `Resource_status` | Estado | Posibles estados de los recursos: disponible, en obras, etc. |
| `Resource_flat_type` | Tipo de piso | Clasificación de los recursos en base a sus características principales, que permiten identificar agrupar recursos con características similares o equivalentes. |
| `Resource_flat_amenity` | Característica | Equipamientos de los que dispone cada subtipo de piso |
| `Resource_flat_subtype` | Subtipo de piso | Subclasificación de los pisos en base a sus características |
| `Resource_usage` | Tipo de uso | Tipos de uso |
| `Resource_value` | Valoración | Valoración histórica de recursos |
| `Resource_place_type` | Tipo de plaza | Clasificación de los recursos en base a sus características principales, que permiten identificar agrupar recursos con características similares o equivalentes. |
| `Resource_place_text` | Texto | Textos de clasificación de los recursos |
| `Resource_amenity_type` | Tipo de característica | Servicios o equipamiento de los que puede disponer un determinado recurso, edificio, piso, habitación o plaza, como aire acondicionado, calefacción, etc. Tabla de códigos, asociado a características |
| `Resource_doc_type` | Tipo de documento | Documentos asociados a cada recurso. Un recurso puede tener varios documentos. |
| `Resource_inventory_type` | Tipo de inventario | Tipos de elementos del inventario de los recursos. |
| `Resource_inventory_zone` | Zona de inventario | Zonas de un piso, para poder asignar el inventario. |

### `Resource.Resource` — Recurso

Recursos de los que dispone Cotown para su alquiler. Pueden ser pisos, habitaciones o camas/plazas.

| Atributo | Etiqueta | Tipo | Oblig. | Referencia / valores |
|---|---|---|---|---|
| `Resource_type` | Tipo de recurso | Lista de valores |  | piso, habitacion, plaza, comun, local, parking, trastero, sala |
| `Code` | Código | Texto | ● |  |
| `Status_id` | Status | Entero |  | → `Resource.Resource_status` |
| `Address` | Dirección | Texto | ● |  |
| `Street` | Calle, nº | Texto |  |  |
| `Management_fee` | 0% Management fee | Decimal |  |  |
| `Management_fee_no_cleaning` | Sin servicios | Decimal |  |  |
| `Management_fee_weekly` | Servicio premium | Decimal |  |  |
| `Management_fee_biweekly` | Servicio estándar | Decimal |  |  |
| `Management_fee_monthly` | Servicio mensual | Decimal |  |  |
| `Building_id` | Edificio | Entero | ● | → `Building.Building` |
| `Registry_code` | Referencia catastral | Texto |  |  |
| `Flat_id` | Piso | Entero | ● | → `Resource.Resource` |
| `Occupancy_certificate` | Nº cédula habitabilidad | Texto |  |  |
| `Room_id` | Habitación | Entero |  | → `Resource.Resource` |
| `Usage_id` | Uso catastral | Entero |  | → `Resource.Resource_usage` |
| `Flat_type_id` | Tipo de piso | Entero | ● | → `Resource.Resource_flat_type` |
| `Limit_type` | Tipo de afectación | Lista de valores |  | libre, lau, indice |
| `Big_renovation_date` | Fecha fin gran rehabilitación | Fecha |  |  |
| `Flat_subtype_id` | Subtipo de piso | Entero |  | → `Resource.Resource_flat_subtype` |
| `Place_type_id` | Tipo de plaza | Entero |  | → `Resource.Resource_place_type` |
| `Renovation_date` | Fecha fin reforma | Fecha |  |  |
| `Baths` | Nº de baños compartidos | Entero |  |  |
| `Energy_certificate` | Certificado energético | Texto |  |  |
| `Owner_id` | Propietario | Entero | ● | → `Provider.Provider` |
| `Energy_certificate_rate` | Valor certificado | Texto |  |  |
| `Places` | Nº máximo/potencial de plazas | Entero |  |  |
| `SAP_code` | Código SAP | Texto |  |  |
| `Service_id` | Empresa de servicios | Entero | ● | → `Provider.Provider` |
| `Orientation` | Orientación | Texto |  |  |
| `Weigth` | Coeficiente | Decimal |  |  |
| `Billing_type` | Tipo de facturación | Lista de valores | ● | mes, quincena, proporcional, na |
| `Interior` | Interior/Exterior | Lista de valores |  | interior, exterior |
| `Last_LAU_date` | Fecha fin último LAU | Fecha |  |  |
| `Last_LAU_free_date` | Fecha liberación LAU | Fecha |  |  |
| `Part` | Partes | Texto |  |  |
| `Sale_type` | Tipo de venta | Lista de valores | ● | completo, plazas, ambos, na |
| `Area` | Superficie total (m²) | Decimal |  |  |
| `Last_LAU_rent` | Importe última renta LAU | Decimal |  |  |
| `Area_woc` | Superficie sin comunes (m²) | Decimal |  |  |
| `Max_LAU_rent` | Máxima renta LAU | Decimal |  |  |
| `Segment_id` | Web | Entero |  | → `Auxiliar.Segment` |
| `Wifi_ssid` | WiFi SSID | Texto |  |  |
| `Index_rent` | Valor índice | Decimal |  |  |
| `Rate_id` | Tarifa | Entero |  | → `Billing.Pricing_rate` |
| `Wifi_key` | WiFi Clave | Texto |  |  |
| `LAU_applicable` | LAU aplicable? | Sí/No |  |  |
| `Max_rent` | Máxima renta | Decimal |  |  |
| `Max_services` | Servicios | Decimal |  |  |
| `Notes` | Notas (limpieza, tipo de suelo…) | Texto |  |  |
| `Gate_mac` | Puerta - MAC | Texto |  |  |
| `Max_utility` | Consumos | Decimal |  |  |
| `Registry_num` | Nº de registro | Texto |  |  |
| `Gate_url` | Puerta - URL | Texto |  |  |
| `Max_furniture` | Mobiliario | Decimal |  |  |
| `Registry_date` | Fecha de registro | Fecha |  |  |
| `Contract_gas` | Contrato de gas | Texto |  |  |
| `Gate_phone` | Puerta - Teléfono | Texto |  |  |
| `Max_expenses` | Gastos repercutibles | Decimal |  |  |
| `Contract_electricity` | Contrato de luz | Texto |  |  |
| `HOA` | Repercutir gastos | Sí/No |  |  |
| `Ical` | URL iCal | Texto |  |  |
| `Contract_water` | Contrato de agua | Texto |  |  |
| `Capex` | CAPEX previsto | Decimal |  |  |
| `Last_cleaning` | Última limpieza | Fecha |  |  |
| `Pre_capex_long_term` | Valor pre-capex renta antigua | Decimal |  |  |
| `Last_planned_cleaning` | Última limpieza prevista | Fecha |  |  |
| `Pre_capex_vacant` | Valor pre-capex vacío | Decimal |  |  |
| `Post_capex` | Valor cosharing convertido | Decimal |  |  |
| `Post_capex_residential` | Valor residencial | Decimal |  |  |
| `Description` | Detalles (español) | Texto |  |  |
| `Description_en` | Detalles (inglés) | Texto |  |  |

### `Resource.Resource_amenity` — Característica

Equipamientos de los que dispone cada recurso: piso, habitación o plaza.

| Atributo | Etiqueta | Tipo | Oblig. | Referencia / valores |
|---|---|---|---|---|
| `Resource_id` | Recurso | Entero | ● | → `Resource.Resource` |
| `Amenity_type_id` | Tipo de característica | Entero | ● | → `Resource.Resource_amenity_type` |
| `Description` | Detalles (español) | Texto |  |  |

### `Resource.Resource_availability` — Estado

Periodos de indisponibilidad del recurso

| Atributo | Etiqueta | Tipo | Oblig. | Referencia / valores |
|---|---|---|---|---|
| `Date_from` | Desde | Fecha | ● |  |
| `Date_to` | Hasta | Fecha | ● |  |
| `Description` | Detalles | Texto |  |  |
| `Convertible` | Convertible | Texto |  |  |
| `Booking_id` | Reserva LAU | Entero |  | → `Booking.Booking_other` |
| `Resource_id` | Recurso | Entero | ● | → `Resource.Resource` |
| `Status_id` | Estado | Entero | ● | → `Resource.Resource_status` |

### `Resource.Resource_doc` — Documento

Categorización de los tipos de documentos de recursos

| Atributo | Etiqueta | Tipo | Oblig. | Referencia / valores |
|---|---|---|---|---|
| `Resource_id` | Recurso | Entero | ● | → `Resource.Resource` |
| `Resource_doc_type_id` | Tipo de documento | Entero | ● | → `Resource.Resource_doc_type` |
| `Description` | Descripción | Texto |  |  |
| `Document` | Document | Documento |  |  |

### `Resource.Resource_forecast` — Forecast

Forecast

| Atributo | Etiqueta | Tipo | Oblig. | Referencia / valores |
|---|---|---|---|---|
| `Resource_id` | Recurso | Entero | ● | → `Resource.Resource` |
| `Date_price` | Mes | Fecha | ● |  |
| `Beds` | Camas | Decimal | ● |  |
| `Occupancy` | % Ocupación | Decimal | ● |  |
| `Rent_short` | Tarifa Short | Decimal | ● |  |
| `Rent_medium` | Tarifa Medium | Decimal | ● |  |
| `Rent_group` | Tarifa Group | Decimal | ● |  |
| `Rent_long` | Tarifa Long | Decimal | ● |  |
| `Pct_short` | % Short | Decimal | ● |  |
| `Pct_medium` | % Medium | Decimal | ● |  |
| `Pct_long` | % Long | Decimal | ● |  |
| `Discount` | % Descuento | Decimal | ● |  |
| `Services` | Servicios | Decimal | ● |  |
| `Final_cleaning` | Limpieza final | Decimal | ● |  |
| `Booking_fee` | Membership fee | Decimal | ● |  |
| `Reinvoices` | Refacturación | Decimal | ● |  |
| `Management_fee` | Management fee | Decimal | ● |  |

### `Resource.Resource_inventory` — Inventario

Elementos que forman parte del inventario de un recurso.

| Atributo | Etiqueta | Tipo | Oblig. | Referencia / valores |
|---|---|---|---|---|
| `Resource_id` | Recurso | Entero | ● | → `Resource.Resource` |
| `Inventory_type_id` | Tipo de elemento | Entero | ● | → `Resource.Resource_inventory_type` |
| `Inventory_zone_id` | Zona | Entero | ● | → `Resource.Resource_inventory_zone` |
| `Asset` | Activo | Sí/No | ● |  |
| `Description` | Descripción | Texto | ● |  |
| `Price` | Precio | Decimal |  |  |
| `Base` | Base imponible | Decimal |  |  |
| `Qty` | Cantidad | Entero |  |  |
| `Bill` | Factura | Texto |  |  |
| `Purchase_date` | Fecha de compra | Fecha |  |  |
| `Warranty_date` | Fecha de garantía | Fecha |  |  |
| `Brand` | Marca | Texto |  |  |
| `Model` | Modelo | Texto |  |  |
| `Comments` | Comentarios | Texto |  |  |

### `Resource.Resource_price` — Precio

Precios históricos de los recursos

| Atributo | Etiqueta | Tipo | Oblig. | Referencia / valores |
|---|---|---|---|---|
| `Resource_id` | Recurso | Entero | ● | → `Resource.Resource` |
| `Date_price` | Fecha | Fecha | ● |  |
| `Rate_id` | Tarifa | Entero | ● | → `Billing.Pricing_rate` |
| `Rent_short` | Corta estancia | Decimal |  |  |
| `Rent_medium` | Media estancia | Decimal |  |  |
| `Rent_long` | Larga estancia | Decimal |  |  |
| `Rent_group` | Grupo | Decimal |  |  |
| `Services` | Servicios | Decimal |  |  |
| `Deposit` | Garantía | Decimal |  |  |
| `Limit` | Consumos (límite) | Decimal |  |  |
| `Final_cleaning` | Limpieza final | Decimal |  |  |
| `Booking_fee` | Mambership fee | Decimal |  |  |

### `Resource.Resource_stabilised` — Stabilised

Stabilised

| Atributo | Etiqueta | Tipo | Oblig. | Referencia / valores |
|---|---|---|---|---|
| `Resource_id` | Recurso | Entero | ● | → `Resource.Resource` |
| `Date_price` | Mes | Entero | ● | → `Auxiliar.Monthname` |
| `Occupancy` | % Ocupación | Decimal | ● |  |
| `Pct_short` | % Short | Decimal | ● |  |
| `Pct_medium` | % Medium | Decimal | ● |  |
| `Pct_long` | % Long | Decimal | ● |  |
| `Leakage` | % Leakage | Decimal | ● |  |

### `Resource.Resource_subtype_text` — Textos web

Textos de subtipos de piso

| Atributo | Etiqueta | Tipo | Oblig. | Referencia / valores |
|---|---|---|---|---|
| `Flat_subtype_id` | Subtipo de piso | Entero | ● | → `Resource.Resource_flat_subtype` |
| `Segment_id` | Web | Entero | ● | → `Auxiliar.Segment` |
| `Name` | Nombre (español) | Texto | ● |  |
| `Name_en` | Nombre (inglés) | Texto | ● |  |
| `Tour` | Tour virtual | Texto |  |  |
| `Description` | Descripción (español) | Texto |  |  |
| `Description_en` | Descripción (inglés) | Texto |  |  |

### `Resource.Resource_status` — Estado

Posibles estados de los recursos: disponible, en obras, etc.

| Atributo | Etiqueta | Tipo | Oblig. | Referencia / valores |
|---|---|---|---|---|
| `Name` | Nombre | Texto | ● |  |
| `Available` | Disponible | Sí/No | ● |  |
| `Convertible` | Convertible | Sí/No | ● |  |
| `Not_flat` | No bloquea piso | Sí/No |  |  |

### `Resource.Resource_flat_type` — Tipo de piso

Clasificación de los recursos en base a sus características principales, que permiten identificar agrupar recursos con características similares o equivalentes.

| Atributo | Etiqueta | Tipo | Oblig. | Referencia / valores |
|---|---|---|---|---|
| `Code` | Código | Texto | ● |  |
| `Name` | Nombre (español) | Texto | ● |  |
| `Name_en` | Nombre (inglés) | Texto | ● |  |
| `Icon` | Icono | Documento |  |  |

### `Resource.Resource_flat_amenity` — Característica

Equipamientos de los que dispone cada subtipo de piso

| Atributo | Etiqueta | Tipo | Oblig. | Referencia / valores |
|---|---|---|---|---|
| `Flat_subtype_id` | Subtipo de piso | Entero | ● | → `Resource.Resource_flat_subtype` |
| `Amenity_type_id` | Tipo de característica | Entero | ● | → `Resource.Resource_amenity_type` |
| `Description` | Descripción | Texto |  |  |

### `Resource.Resource_flat_subtype` — Subtipo de piso

Subclasificación de los pisos en base a sus características

| Atributo | Etiqueta | Tipo | Oblig. | Referencia / valores |
|---|---|---|---|---|
| `Code` | Código | Texto | ● |  |
| `Name` | Nombre (español) | Texto | ● |  |
| `Name_en` | Nombre (inglés) | Texto | ● |  |
| `Description` | Descripción (español) | Texto |  |  |
| `Description_en` | Descripción (inglés) | Texto |  |  |
| `Tour` | Tour virtual | Texto |  |  |

### `Resource.Resource_usage` — Tipo de uso

Tipos de uso

| Atributo | Etiqueta | Tipo | Oblig. | Referencia / valores |
|---|---|---|---|---|
| `Name` | Nombre (español) | Texto |  |  |
| `Name_en` | Nombre (inglés) | Texto |  |  |

### `Resource.Resource_value` — Valoración

Valoración histórica de recursos

| Atributo | Etiqueta | Tipo | Oblig. | Referencia / valores |
|---|---|---|---|---|
| `Resource_id` | Recurso | Entero | ● | → `Resource.Resource` |
| `Valuation_date` | Fecha | Fecha | ● |  |
| `Pre_capex_long_term` | Valor pre-capex renta antigua | Decimal | ● |  |
| `Pre_capex_vacant` | Valor pre-capex vacío | Decimal | ● |  |
| `Post_capex` | Valor cosharing convertido | Decimal | ● |  |
| `Post_capex_residential` | Valor residencial | Decimal | ● |  |

### `Resource.Resource_place_type` — Tipo de plaza

Clasificación de los recursos en base a sus características principales, que permiten identificar agrupar recursos con características similares o equivalentes.

| Atributo | Etiqueta | Tipo | Oblig. | Referencia / valores |
|---|---|---|---|---|
| `Code` | Código | Texto | ● |  |
| `Name` | Nombre (español) | Texto | ● |  |
| `Name_en` | Nombre (inglés) | Texto | ● |  |
| `Icon` | Icono | Documento |  |  |

### `Resource.Resource_place_text` — Texto

Textos de clasificación de los recursos

| Atributo | Etiqueta | Tipo | Oblig. | Referencia / valores |
|---|---|---|---|---|
| `Place_type_id` | Tipo de plaza | Entero | ● | → `Resource.Resource_place_type` |
| `Segment_id` | Web | Entero | ● | → `Auxiliar.Segment` |
| `Building_id` | Edificio | Entero |  | → `Building.Building` |
| `Location_id` | Ciudad | Entero |  | → `Geo.Location` |
| `Description` | Descripción (español) | Texto |  |  |
| `Description_en` | Descripción (inglés) | Texto |  |  |

### `Resource.Resource_amenity_type` — Tipo de característica

Servicios o equipamiento de los que puede disponer un determinado recurso, edificio, piso, habitación o plaza, como aire acondicionado, calefacción, etc. Tabla de códigos, asociado a características

| Atributo | Etiqueta | Tipo | Oblig. | Referencia / valores |
|---|---|---|---|---|
| `Code` | Código | Texto | ● |  |
| `Increment` | Incremento % | Decimal | ● |  |
| `Name` | Nombre (español) | Texto | ● |  |
| `Name_en` | Nombre (inglés) | Texto | ● |  |
| `Description` | Detalles (español) | Texto |  |  |
| `Description_en` | Detalles (inglés) | Texto |  |  |
| `Icon` | Icono | Documento |  |  |
| `Image` | Imagen | Documento |  |  |

### `Resource.Resource_doc_type` — Tipo de documento

Documentos asociados a cada recurso. Un recurso puede tener varios documentos.

| Atributo | Etiqueta | Tipo | Oblig. | Referencia / valores |
|---|---|---|---|---|
| `Name` | Nombre | Texto | ● |  |
| `Contract` | Adjuntar a contratos | Sí/No |  |  |

### `Resource.Resource_inventory_type` — Tipo de inventario

Tipos de elementos del inventario de los recursos.

| Atributo | Etiqueta | Tipo | Oblig. | Referencia / valores |
|---|---|---|---|---|
| `Name` | Nombre (español) | Texto | ● |  |
| `Name_en` | Nombre (inglés) | Texto | ● |  |
| `Icon` | Icono | Documento |  |  |
| `Image` | Imagen | Documento |  |  |

### `Resource.Resource_inventory_zone` — Zona de inventario

Zonas de un piso, para poder asignar el inventario.

| Atributo | Etiqueta | Tipo | Oblig. | Referencia / valores |
|---|---|---|---|---|
| `Name` | Nombre (español) | Texto | ● |  |
| `Name_en` | Nombre (inglés) | Texto | ● |  |
| `Icon` | Icono | Documento |  |  |
| `Image` | Imagen | Documento |  |  |

## Esquema `Booking` — Reservas

![ER Booking B2C](../diagramas/er/ER%20Booking%20B2C.png)

![ER Booking B2B](../diagramas/er/ER%20Booking%20B2B.png)

![ER Booking LAU](../diagramas/er/ER%20Booking%20LAU.png)

| Entidad | Nombre en el ERP | Descripción |
|---|---|---|
| `Booking` | Reserva B2C | Reservas y peticiones de reserva de los activos de Cotown. |
| `Booking_doc` | Documento de reserva | Documentos asociados a cada reserva |
| `Booking_group_doc` | Documento | Documentos asociados a cada reserva B2B |
| `Booking_log` | Log | Log de acciones en la reserva |
| `Booking_option` | Alternativa | Alternativas propuestas por Cotown a las solicitudes de reserva de un cliente. |
| `Booking_price` | Precio | Precios mensuales para todo el periodo de cada reserva |
| `Booking_service` | Concepto extra | Servicios adicionales proporcionados, que se incorporarán a las facturas. |
| `Checkin_price` | Precio | Precios y horarios de las opciones de checkin |
| `Booking_group` | Reserva B2B | Reservas de grupo de los activos de Cotown. |
| `Booking_group_annex` | Anexo | Anexos al contrato |
| `Booking_group_price` | Precio por plaza | Precios mensuales para todo el periodo de cada reserva de grupo |
| `Booking_group_rooming` | Rooming list | Rooming list B2B |
| `Booking_group_rooms` | Habitación | Habitaciones de una reserva de grupo (expansión de Room_ids) |
| `Booking_group_service` | Concepto extra | Servicios adicionales proporcionados, que se incorporarán a las facturas. |
| `Booking_other` | Reserva LAU y otros | Reservas de otros activos |
| `Booking_other_doc` | Documento | Documentos de reservas de otros activos |
| `Booking_other_resource` | Recurso adicional | Otros recursos reservados |
| `Booking_other_service` | Concepto extra | Servicios adicionales proporcionados, que se incorporarán a las facturas. |
| `Booking_channel` | Canal de reserva | Canales |
| `Booking_referral` | Tipo de referencia | Cómo nos han conocido |
| `Booking_who` | Tipo de solicitante | Quien hizo la reserva |
| `Customer_reason` | Motivo de estancia | Motivos para residir en un recurso de Cotown. Tabla de códigos asociado a un cliente. |
| `Booking_rooming` | Rooming list | Rooming list B2C |
| `Booking_subtype` | Tipo de reserva LAU | Tipos de inquilinos para otras reservas |
| `Checkin_type` | Servicio check-in/check-out | Tipos de check in que un cliente puede solicitar, por ejemplo, en oficina, recogida en aeropuerto, etc. |
| `Booking_questionnaire` | Cuestionario | Cuestionarios |
| `Booking_search` | Búsqueda | FUTURO |
| `Booking_discount_type` | Tipo de descuento | Tipos de descuento |
| `Booking_answer` | Pregunta-Respuesta | Respuestas |
| `Booking_photo` | Foto/Vídeo | Fotos |
| `Booking_doc_type` | Tipo de documento | Categorización de los tipos de documentos de reservas |
| `Booking_internal_doc` | Documento | Documentos y normas internas para las reservas |
| `Booking_detail` | Reserva | Tabla interna para la gestión de disponibilidad |
| `Booking_question` | Pregunta | Preguntas |
| `Booking_question_group` | Tipo de pregunta | Preguntas |

### `Booking.Booking` — Reserva B2C

Reservas y peticiones de reserva de los activos de Cotown.

| Atributo | Etiqueta | Tipo | Oblig. | Referencia / valores |
|---|---|---|---|---|
| `Status` | Estado | Lista de valores | ● | solicitud, solicitudpagada, alternativas, alternativaspagada, descartada, descartadapagada, pendientepago, caducada, confirmada, cancelada, firmacontrato, contrato, checkinconfirmado, checkin, inhouse, checkout, devolvergarantia, finalizada, revision, documentacionok, documentacionko |
| `Button_activate` | Reactivar | Texto |  |  |
| `Button_discard` | Descartar | Texto |  |  |
| `Button_checkin` | Check in OK | Texto |  |  |
| `Button_checkout` | Check out OK | Texto |  |  |
| `Date_from` | Fecha desde | Fecha | ● |  |
| `Date_to` | Fecha hasta | Fecha | ● |  |
| `Request_date` | Fecha de solicitud | Fecha |  |  |
| `Confirmation_date` | Fecha de confirmación | Fecha |  |  |
| `Expiry_date` | Valida hasta | Fecha |  |  |
| `Documentation_limit` | Documentación antes de | Fecha |  |  |
| `Book_type` | Tipo de reserva | Lista de valores |  | limitado, recreativo |
| `New_check_out` | Nueva fecha de salida | Fecha |  |  |
| `Limit_type` | Tipo de limitación | Lista de valores |  | libre, lau, indice |
| `Old_check_out` | Fecha original de check-ou | Fecha |  |  |
| `Eco_ext_fee` | Penalización ECO | Texto |  |  |
| `Master_id` | Reserva master B2B | Entero |  | → `Booking.Booking_group` |
| `Eco_ext_change_ok` | Cambio gestionado | Sí/No | ● |  |
| `Eco_ext_keyless_ok` | Llave móvil actualizada | Sí/No | ● |  |
| `Customer_id` | Residente | Entero | ● | → `Customer.Customer` |
| `Ignore_black_list` | Ignorar lista negra | Sí/No |  |  |
| `Info` | Residente | Texto |  |  |
| `Contract_rent` | Contrato de renta | Documento |  |  |
| `Building_id` | Edificio | Entero | ● | → `Building.Building` |
| `Contract_services` | Contrato de servicios | Documento |  |  |
| `Contract_id` | Id Contrato | Texto |  |  |
| `Resource_type` | Tipo de recurso | Lista de valores | ● | piso, habitacion |
| `Contract_status` | Estado del contrato | Lista de valores |  | sent, delivered, declined, completed, expired, other, pending, voided |
| `Flat_type_id` | Tipología de piso | Entero | ● | → `Resource.Resource_flat_type` |
| `Contract_signed` | Fecha de estado | Fecha y hora |  |  |
| `Place_type_id` | Tipología de plaza | Entero |  | → `Resource.Resource_place_type` |
| `Reason_id` | Motivo de estancia | Entero |  | → `Booking.Customer_reason` |
| `School_id` | Escuela | Entero |  | → `Auxiliar.School` |
| `Company` | Empresa | Texto |  |  |
| `Other_school` | Escuela (otro) | Texto |  |  |
| `Promotion_id` | Promoción | Entero |  | → `Billing.Promotion` |
| `Button_options` | Enviar alternativas | Texto |  |  |
| `Booking_channel_id` | Canal | Entero | ● | → `Booking.Booking_channel` |
| `Booking_referral_id` | Cómo nos conoció | Entero |  | → `Booking.Booking_referral` |
| `Booking_who_id` | Quién hizo la reserva | Entero |  | → `Booking.Booking_who` |
| `Agent_id` | Marketplace | Entero |  | → `Provider.Agent` |
| `Commision` | Comisión | Decimal |  |  |
| `Commision_bill_status` | Estado factura | Texto |  |  |
| `Comments` | Comentarios | Texto |  |  |
| `Resource_id` | Recurso | Entero |  | → `Resource.Resource` |
| `Billing_type` | Facturación primer mes | Lista de valores |  | mes, quincena, proporcional, na |
| `Billing_type_last` | Facturación último mes | Lista de valores |  | mes, quincena, proporcional, na |
| `Tax_id` | IVA | Entero |  | → `Billing.Tax` |
| `Link_id` | Reserva relacionada | Entero |  | → `Booking.Booking` |
| `Cleaning_freq` | Frecuencia de limpieza | Lista de valores |  | no, semanal, quincenal, mensual, sin |
| `Lock` | No cambiar asignación | Sí/No | ● |  |
| `Second_resident` | Segundo residente | Sí/No | ● |  |
| `Invoice_comment` | Nota en factura | Texto |  |  |
| `Rent` | Renta | Decimal |  |  |
| `Services` | Servicios | Decimal |  |  |
| `Limit` | Consumos (límite) | Decimal |  |  |
| `Expenses` | Gastos repercutibles | Decimal |  |  |
| `Furniture` | Mobiliario | Decimal |  |  |
| `Final_cleaning` | Limpieza final | Decimal |  |  |
| `Booking_fee_calc` | Membership fee teórico | Decimal |  |  |
| `Check_in` | Check in | Fecha |  |  |
| `Booking_fee` | Membership fee a pagar | Decimal |  |  |
| `Check_in_time` | Hora de check-in | Hora |  |  |
| `Arrival` | Hora de llegada | Hora |  |  |
| `Booking_fee_actual` | Membership fee pagado | Decimal |  |  |
| `Booking_fee_returned` | Membership fee devuelto | Decimal |  |  |
| `Flight` | Vuelo/Tren | Texto |  |  |
| `Booking_discount_type_id` | Motivo suplemento/descuento | Entero |  | → `Booking.Booking_discount_type` |
| `Check_in_option_id` | Opción | Entero |  | → `Booking.Checkin_type` |
| `Check_in_room_ok` | Habitación ok | Sí/No | ● |  |
| `Check_in_keys_ok` | Llaves ok | Sí/No | ● |  |
| `Check_in_keyless_ok` | Llaves keyless ok | Sí/No | ● |  |
| `Check_in_notice_ok` | Aviso compañeros | Sí/No | ● |  |
| `Check_in_req` | Check in solicitado | Sí/No |  |  |
| `Deposit` | Garantía teórica | Decimal |  |  |
| `Issues` | Incidencias entrada | Texto |  |  |
| `Check_out` | Check out | Fecha |  |  |
| `Deposit_actual` | Garantía depositada | Decimal |  |  |
| `Issues_ok` | Incidencias gestionadas | Sí/No | ● |  |
| `Check_out_time` | Hora de recogida | Hora |  |  |
| `Deposit_required` | Garantía devolución requerida | Decimal |  |  |
| `Date_deposit_required` | Fecha requerida | Fecha |  |  |
| `Flight_out` | Vuelo/Tren | Texto |  |  |
| `Check_out_option_id` | Opción | Entero |  | → `Booking.Checkin_type` |
| `Deposit_returned` | Garantía devuelta | Decimal |  |  |
| `Check_out_keys_ok` | Llaves devueltas | Sí/No | ● |  |
| `Date_deposit_returned` | Fecha devuelta | Fecha |  |  |
| `Check_out_keyless_ok` | Llave móvil off | Sí/No | ● |  |
| `Incasol_deposit` | Fianza INCASOL | Decimal |  |  |
| `Check_out_revision_ok` | Habitación revisada ok | Sí/No | ● |  |
| `Incasol_reg` | Nº registro | Texto |  |  |
| `Damages` | Desperfectos | Texto |  |  |
| `Incasol_type` | Estado INCASOL | Lista de valores |  | pendiente, depositada, reclamada, devuelta |
| `Damages_ok` | Desperfectos gestionados | Sí/No | ● |  |
| `Deposit_locked` | Retenida temporalmente | Sí/No |  |  |
| `Fee_marketplace` | Membership marketplace | Sí/No |  |  |
| `Origin_id` | Reserva origen | Entero |  | → `Booking.Booking` |
| `Destination_id` | Reserva destino | Entero |  | → `Booking.Booking` |
| `Cha_ext` | Tipo de relación | Lista de valores |  | cha, ext |
| `Customer` | Cliente | Texto |  |  |

### `Booking.Booking_doc` — Documento de reserva

Documentos asociados a cada reserva

| Atributo | Etiqueta | Tipo | Oblig. | Referencia / valores |
|---|---|---|---|---|
| `Booking_id` | Reserva | Entero | ● | → `Booking.Booking` |
| `Booking_doc_type_id` | Tipo de documento | Entero | ● | → `Booking.Booking_doc_type` |
| `Document` |  | Documento |  |  |

### `Booking.Booking_group_doc` — Documento

Documentos asociados a cada reserva B2B

| Atributo | Etiqueta | Tipo | Oblig. | Referencia / valores |
|---|---|---|---|---|
| `Booking_id` | Reserva | Entero | ● | → `Booking.Booking_group` |
| `Booking_doc_type_id` | Tipo de documento | Entero | ● | → `Booking.Booking_doc_type` |
| `Document` | Documento | Documento |  |  |

### `Booking.Booking_log` — Log

Log de acciones en la reserva

| Atributo | Etiqueta | Tipo | Oblig. | Referencia / valores |
|---|---|---|---|---|
| `Booking_id` | Reserva | Entero | ● | → `Booking.Booking` |
| `Log` | Acción | Texto | ● |  |

### `Booking.Booking_option` — Alternativa

Alternativas propuestas por Cotown a las solicitudes de reserva de un cliente.

| Atributo | Etiqueta | Tipo | Oblig. | Referencia / valores |
|---|---|---|---|---|
| `Booking_id` | Reserva | Entero | ● | → `Booking.Booking` |
| `Building_id` | Edificio | Entero | ● | → `Building.Building` |
| `Resource_type` | Tipo de recurso | Lista de valores | ● | piso, habitacion |
| `Flat_type_id` | Tipología de piso | Entero | ● | → `Resource.Resource_flat_type` |
| `Place_type_id` | Tiipología de plaza | Entero |  | → `Resource.Resource_place_type` |
| `Accepted` | ¿Aceptada? | Sí/No | ● |  |
| `Details` | Detalles | Texto |  |  |

### `Booking.Booking_price` — Precio

Precios mensuales para todo el periodo de cada reserva

| Atributo | Etiqueta | Tipo | Oblig. | Referencia / valores |
|---|---|---|---|---|
| `Booking_id` | Reserva | Entero | ● | → `Booking.Booking` |
| `Rent_date` | Mes | Fecha | ● |  |
| `Rent_total` | Renta+Descuentos | Decimal |  |  |
| `Rent` | Renta | Decimal | ● |  |
| `Rent_discount` | € Supl(+) / Desc(-) renta | Decimal |  |  |
| `Rent_discount_pct` | % Supl(+) / Desc(-) renta | Decimal |  |  |
| `Rent_rack` | Renta (rack rate) | Decimal |  |  |
| `Invoice_rent_id` | Factura renta | Entero |  | → `Billing.Invoice` |
| `Services_total` | Servicios+Descuentos | Decimal |  |  |
| `Services` | Servicios | Decimal | ● |  |
| `Services_discount` | € Supl(+) / Desc(-) servicios | Decimal |  |  |
| `Services_discount_pct` | % Supl(+) / Desc(-) servicios | Decimal |  |  |
| `Services_rack` | Servicios (rack rate) | Decimal |  |  |
| `Invoice_services_id` | Factura servicios | Entero |  | → `Billing.Invoice` |
| `Discount_type_id` | Motivo suplemento/descuento | Entero |  | → `Booking.Booking_discount_type` |
| `Expenses` | Gastos repercutibles | Decimal |  |  |
| `Furniture` | Mobiliario | Decimal |  |  |
| `Utility` | Consumos | Decimal |  |  |
| `Apply_to_all` | Aplicar a todas las líneas | Sí/No | ● |  |
| `Invoice_external` | Facturado externamente | Sí/No | ● |  |
| `Comments` | Comentarios | Texto |  |  |

### `Booking.Booking_service` — Concepto extra

Servicios adicionales proporcionados, que se incorporarán a las facturas.

| Atributo | Etiqueta | Tipo | Oblig. | Referencia / valores |
|---|---|---|---|---|
| `Booking_id` | Reserva | Entero | ● | → `Booking.Booking` |
| `Extra_type` | Modo de facturación | Lista de valores | ● | asap, puntual, recurrente |
| `Billing_date_from` | Fecha servicio | Fecha |  |  |
| `Billing_date_to` | Facturar hasta (*recurrente) | Fecha |  |  |
| `Concept` | Concepto | Texto |  |  |
| `Product_id` | Producto/Servicio | Entero | ● | → `Billing.Product` |
| `Amount` | Importe | Decimal | ● |  |
| `Tax_id` | Impuesto | Entero |  | → `Billing.Tax` |
| `Payment_method_id` | Medio de pago | Entero |  | → `Billing.Payment_method` |
| `Provider_id` | Proveedor | Entero |  | → `Provider.Provider` |
| `Invoice_services_id` | Factura | Entero |  | → `Billing.Invoice` |
| `Comments` | Comentarios | Texto |  |  |

### `Booking.Checkin_price` — Precio

Precios y horarios de las opciones de checkin

| Atributo | Etiqueta | Tipo | Oblig. | Referencia / valores |
|---|---|---|---|---|
| `Checkin_type_id` | Opcón de check-in | Entero |  | → `Booking.Checkin_type` |
| `Location_id` | Localidad | Entero |  | → `Geo.Location` |
| `Timetable_id` | Horario | Entero |  | → `Auxiliar.Timetable` |
| `Date_from` | Fecha desde | Fecha |  |  |
| `Date_to` | Fecha hasta | Fecha |  |  |
| `Price` | Precio | Decimal |  |  |

### `Booking.Booking_group` — Reserva B2B

Reservas de grupo de los activos de Cotown.

| Atributo | Etiqueta | Tipo | Oblig. | Referencia / valores |
|---|---|---|---|---|
| `Status` | Status | Lista de valores | ● | grupobloqueado, grupoconfirmado, inhouse, cancelada, revision, devolvergarantia, finalizada |
| `Building_id` | Edificio | Entero | ● | → `Building.Building` |
| `Payer_id` | Cliente | Entero | ● | → `Customer.Customer` |
| `Agent_id` | Marketplace | Entero |  | → `Provider.Agent` |
| `Date_from` | Fecha desde | Fecha | ● |  |
| `Commision` | Comisión | Decimal |  |  |
| `Date_to` | Fecha hasta | Fecha | ● |  |
| `Request_date` | Fecha de solicitud | Fecha |  |  |
| `Type_B2C` | Gestión B2C | Sí/No | ● |  |
| `Confirmation_date` | Fecha de confirmación | Fecha |  |  |
| `Master` | Master | Sí/No | ● |  |
| `Bill_email_to` | Enviar factura a | Texto |  |  |
| `Book_type` | Tipo de reserva | Lista de valores |  | limitado, recreativo |
| `Bill_email_cc` | Enviar factura cc | Texto |  |  |
| `Billing_type` | Tipo de facturación primer mes | Lista de valores |  | mes, quincena, proporcional, na |
| `Billing_type_last` | Tipo de facturación último mes | Lista de valores |  | mes, quincena, proporcional, na |
| `Invoice_comment` | Nota en factura | Texto |  |  |
| `Rooms` | Nº plazas | Entero |  |  |
| `Limit_type` | Tipo de limitación | Lista de valores |  | libre, lau, indice |
| `Room_ids` | Plazas | Texto (lista) |  |  |
| `Full_flat` | Piso completo | Sí/No |  |  |
| `Comments` | Comentarios | Texto |  |  |
| `Contract_rent` | Contrato de renta | Documento |  |  |
| `Contract_services` | Contrato de servicios | Documento |  |  |
| `Contract_ok` | Contrato Ok | Sí/No | ● |  |
| `Rent` | Renta (x plaza) | Decimal | ● |  |
| `Contract_id` | Id Contrato | Texto |  |  |
| `Services` | Servicios (x plaza) | Decimal | ● |  |
| `Contract_status` | Estado del contrato | Lista de valores |  | sent, delivered, declined, completed, expired, other, pending, voided |
| `Limit` | Consumos (límite) | Decimal |  |  |
| `Contract_signed` | Fecha de estado | Fecha y hora |  |  |
| `Expenses` | Gastos repercutibles | Decimal |  |  |
| `Furniture` | Mobiliario | Decimal |  |  |
| `Booking_fee` | Membership fee | Decimal |  |  |
| `Deposit` | Garantía (x plaza) | Decimal |  |  |
| `Deposit_actual` | Garantía total a depositar | Decimal |  |  |
| `Deposit_required` | Garantía total a devolver | Decimal |  |  |
| `Date_deposit_required` | Fecha a devolver | Fecha |  |  |
| `Deposit_returned` | Garantía total devuelta | Decimal |  |  |
| `Date_deposit_returned` | Fecha devuelta | Fecha |  |  |
| `Incasol_deposit` | Fianza INCASOL | Decimal |  |  |
| `Incasol_reg` | Nº registro | Texto |  |  |
| `Incasol_type` | Estado INCASOL | Lista de valores |  | pendiente, depositada, reclamada, devuelta |
| `Final_cleaning` | Limpieza final (x plaza) | Decimal |  |  |
| `Cleaning_freq` | Frecuencia de limpieza | Lista de valores |  | no, semanal, quincenal, mensual, sin |
| `Tax` | No aplica IVA (indicar inquilinos en la rooming list) | Sí/No | ● |  |
| `Customer` | Cliente | Texto |  |  |

### `Booking.Booking_group_annex` — Anexo

Anexos al contrato

| Atributo | Etiqueta | Tipo | Oblig. | Referencia / valores |
|---|---|---|---|---|
| `Booking_id` | Reserva | Entero | ● | → `Booking.Booking_group` |
| `Code` | Grupo | Texto | ● |  |
| `Contract_annex` | Anexo | Documento |  |  |
| `Contract_id` | Id Contrato | Texto |  |  |
| `Contract_status` | Estado del contrato | Lista de valores |  | sent, delivered, declined, completed, expired, other, pending, voided |
| `Contract_signed` | Fecha de estado | Fecha y hora |  |  |

### `Booking.Booking_group_price` — Precio por plaza

Precios mensuales para todo el periodo de cada reserva de grupo

| Atributo | Etiqueta | Tipo | Oblig. | Referencia / valores |
|---|---|---|---|---|
| `Booking_id` | Reserva | Entero | ● | → `Booking.Booking_group` |
| `Rent_date` | Mes | Fecha | ● |  |
| `Invoice_rent_id` | Factura renta | Entero |  | → `Billing.Invoice` |
| `Rent` | Renta | Decimal | ● |  |
| `Expenses` | Gastos repercutibles | Decimal |  |  |
| `Furniture` | Mobiliario | Decimal |  |  |
| `Utility` | Consumos | Decimal |  |  |
| `Invoice_services_id` | Factura servicios | Entero |  | → `Billing.Invoice` |
| `Services` | Servicios | Decimal | ● |  |
| `Comments` | Comentarios | Texto |  |  |

### `Booking.Booking_group_rooming` — Rooming list

Rooming list B2B

| Atributo | Etiqueta | Tipo | Oblig. | Referencia / valores |
|---|---|---|---|---|
| `Booking_id` | Reserva | Entero | ● | → `Booking.Booking_group` |
| `Resource_id` | Recurso | Entero |  | → `Resource.Resource` |
| `Room_id` | Plaza | Entero | ● | → `Booking.Booking_group_rooms` |
| `Group_code` | Grupo | Texto | ● |  |
| `Status` | Estado | Lista de valores |  | checkin, inhouse, checkout, revisada |
| `Check_in` | Check in | Fecha | ● |  |
| `Arrival` | Hora de llegada | Hora |  |  |
| `Check_in_time` | Hora de check-in | Hora |  |  |
| `Flight` | Vuelo/Tren | Texto |  |  |
| `Check_in_option_id` | Opción | Entero |  | → `Booking.Checkin_type` |
| `Check_in_ok` | Check-in ok | Sí/No | ● |  |
| `Check_in_room_ok` | Habitación ok | Sí/No |  |  |
| `Check_in_keys_ok` | Llaves ok | Sí/No |  |  |
| `Check_in_keyless_ok` | Llaves keyless ok | Sí/No |  |  |
| `Check_in_notice_ok` | Aviso compañeros ok | Sí/No |  |  |
| `Check_in_req` | Check in solicitado | Sí/No |  |  |
| `Check_out` | Check out | Fecha | ● |  |
| `Check_out_time` | Hora de recogida | Hora |  |  |
| `Flight_out` | Vuelo/Tren | Texto |  |  |
| `Check_out_option_id` | Opción | Entero |  | → `Booking.Checkin_type` |
| `Check_out_revision_ok` | Habitación revisada ok | Sí/No | ● |  |
| `Check_out_keys_ok` | Llaves devueltas | Sí/No |  |  |
| `Check_out_keyless_ok` | Llave móvil off | Sí/No |  |  |
| `Cleaning_billed` | Limpieza final facturada | Sí/No |  |  |
| `Id_type_id` | Tipo de documento | Entero |  | → `Auxiliar.Id_type` |
| `Document` | Documento de identidad | Texto |  |  |
| `Name` | Nombre y apellidos | Texto |  |  |
| `Address` | Dirección | Texto |  |  |
| `Zip` | Código postal | Texto |  |  |
| `City` | Ciudad | Texto |  |  |
| `Province` | Provincia | Texto |  |  |
| `Country_id` | Pais | Entero |  | → `Geo.Country` |
| `Email` | Email | Texto |  |  |
| `Phones` | Teléfonos | Texto |  |  |
| `Gender_id` | Género | Entero |  | → `Auxiliar.Gender` |
| `Language_id` | Idioma | Entero |  | → `Auxiliar.Language` |
| `Nationality_id` | Nacionalidad | Entero |  | → `Geo.Country` |
| `Country_origin_id` | País de origen | Entero |  | → `Geo.Country` |
| `Issues` | Incidencias | Texto |  |  |
| `Issues_ok` | Incidencias gestionadas | Sí/No |  |  |
| `Damages` | Desperfectos | Texto |  |  |
| `Damages_ok` | Desperfectos gestionados | Sí/No |  |  |

### `Booking.Booking_group_rooms` — Habitación

Habitaciones de una reserva de grupo (expansión de Room_ids)

| Atributo | Etiqueta | Tipo | Oblig. | Referencia / valores |
|---|---|---|---|---|
| `Booking_id` | Reserva | Entero | ● | → `Booking.Booking_group` |
| `Resource_id` | Recurso | Entero | ● | → `Resource.Resource` |
| `Code` | Código | Texto | ● |  |

### `Booking.Booking_group_service` — Concepto extra

Servicios adicionales proporcionados, que se incorporarán a las facturas.

| Atributo | Etiqueta | Tipo | Oblig. | Referencia / valores |
|---|---|---|---|---|
| `Booking_id` | Reserva | Entero | ● | → `Booking.Booking_group` |
| `Billing_date_from` | Fecha servicio | Fecha | ● |  |
| `Billing_date_to` | Facturar hasta (*recurrente) | Fecha |  |  |
| `Invoice_services_id` | Factura | Entero |  | → `Billing.Invoice` |
| `Product_id` | Producto/Servicio | Entero | ● | → `Billing.Product` |
| `Quantity` | Cantidad | Entero |  |  |
| `Amount` | Importe por plaza | Decimal | ● |  |
| `Tax_id` | Impuesto | Entero |  | → `Billing.Tax` |
| `Provider_id` | Proveedor | Entero |  | → `Provider.Provider` |
| `Concept` | Concepto | Texto |  |  |
| `Comments` | Comentarios | Texto |  |  |

### `Booking.Booking_other` — Reserva LAU y otros

Reservas de otros activos

| Atributo | Etiqueta | Tipo | Oblig. | Referencia / valores |
|---|---|---|---|---|
| `Booking_type` | Tipo de contrato | Lista de valores | ● | lau, retail, parking, coworking |
| `Customer_id` | Cliente | Entero | ● | → `Customer.Customer` |
| `Resource_id` | Recurso | Entero |  | → `Resource.Resource` |
| `Substatus_id` | Status | Entero |  | → `Booking.Booking_subtype` |
| `Product_id` | Producto a facturar | Entero | ● | → `Billing.Product` |
| `Date_from` | Fecha inicio | Fecha | ● |  |
| `Date_to` | Fecha fin | Fecha |  |  |
| `Date_estimated` | Fecha estimada fin | Fecha |  |  |
| `Date_bill_from` | Facturar desde | Fecha |  |  |
| `Burofax_date` | Burofax fin contrato | Fecha |  |  |
| `Date_precapex` | Fecha fin pre-capex | Fecha |  |  |
| `Date_capex` | Fecha fin capex | Fecha |  |  |
| `Calc_locks` | Calcular bloqueos | Sí/No | ● |  |
| `Business_type` | Tipo de negocio | Texto |  |  |
| `Pending_subrogation` | Subrogación pendiente | Lista de valores |  | no, si, dosanios, indefinido |
| `Unlawful` | Ocupación inconsentida | Sí/No | ● |  |
| `Bill_unlawful` | Facturar inconsentida | Sí/No | ● |  |
| `Invoice_comment` | Nota en factura | Texto |  |  |
| `Rent` | Renta | Decimal |  |  |
| `Payment_method_id` | Medio de pago | Entero | ● | → `Billing.Payment_method` |
| `Debts` | Deudas anteriores | Decimal |  |  |
| `Warrants` | Garantías extra | Decimal |  |  |
| `Extras` | Otros | Decimal |  |  |
| `Extras_concept` | Otros, concepto | Texto |  |  |
| `Send_bill` | Enviar factura | Sí/No | ● |  |
| `IPC_apply` | Aplicar IPC | Sí/No | ● |  |
| `IPC_updated` | Último incremento | Fecha |  |  |
| `Send_IPC` | Enviar incremento IPC | Sí/No | ● |  |
| `IPC_notified` | Última notificación | Fecha |  |  |
| `Negotiation` | Estado negociación | Lista de valores |  | notstarted, inprogress, failed, nooption, accepted |
| `Prev_rent` | Renta anterior | Decimal |  |  |
| `Applied_IPC` | IPC aplicado | Decimal |  |  |
| `Max_IPC` | IPC máximo | Decimal |  |  |
| `Contribution_percent` | % Contribución | Decimal |  |  |
| `IPC_month` | Mes incremento IPC | Entero | ● | → `Auxiliar.Monthname` |
| `Contribution_recommended` | MAC | Decimal |  |  |
| `Contribution_asking` | Solicitud inquilino | Decimal |  |  |
| `Contribution_proposal` | Propuesta Vandor | Decimal |  |  |
| `Contribution_proposed_date` | Fecha de propuesta | Fecha |  |  |
| `Comments` | Comentarios | Texto |  |  |
| `Deposit` | Fianza depositada | Decimal |  |  |
| `Deposit_required` | Fianza a devolver | Decimal |  |  |
| `Deposit_required_date` | Devolución prevista | Fecha |  |  |
| `Deposit_returned` | Fianza devuelta | Decimal |  |  |
| `Deposit_return_date` | Devolución efectiva | Fecha |  |  |
| `Compensation` | Indemnizaciones | Decimal |  |  |
| `Compensation_required_date` | Indemnización prevista | Fecha |  |  |
| `Compensation_date` | Indemnización efectiva | Fecha |  |  |
| `ITP_required_date` | Pago ITP previsto | Fecha |  |  |
| `ITP_date` | Pago ITP efectivo | Fecha |  |  |
| `Include_gas` | Gas incluido | Sí/No | ● |  |
| `Include_electricity` | Luz incluida | Sí/No | ● |  |
| `Include_water` | Agua incluida | Sí/No | ● |  |
| `Contribution_chance` | Posibilidad de negociación | Sí/No |  |  |
| `Contribution_comments` | Status | Texto |  |  |
| `End_1_month` | Aviso fin contrato - 1 mes | Sí/No |  |  |
| `IPC_1_month` | Aviso subida IPC - 1 mes | Sí/No |  |  |

### `Booking.Booking_other_doc` — Documento

Documentos de reservas de otros activos

| Atributo | Etiqueta | Tipo | Oblig. | Referencia / valores |
|---|---|---|---|---|
| `Booking_id` | Reserva | Entero |  | → `Booking.Booking_other` |
| `Name` | Nombre | Texto | ● |  |
| `Description` | Descripción | Texto | ● |  |
| `Document` | Documento | Documento | ● |  |

### `Booking.Booking_other_resource` — Recurso adicional

Otros recursos reservados

| Atributo | Etiqueta | Tipo | Oblig. | Referencia / valores |
|---|---|---|---|---|
| `Booking_id` | Reserva | Entero |  | → `Booking.Booking_other` |
| `Resource_id` | Recurso | Entero |  | → `Resource.Resource` |

### `Booking.Booking_other_service` — Concepto extra

Servicios adicionales proporcionados, que se incorporarán a las facturas.

| Atributo | Etiqueta | Tipo | Oblig. | Referencia / valores |
|---|---|---|---|---|
| `Booking_id` | Reserva | Entero | ● | → `Booking.Booking_other` |
| `Invoice_id` | Factura | Entero |  | → `Billing.Invoice` |
| `Billing_date` | Fecha | Fecha | ● |  |
| `Concept` | Concepto | Texto |  |  |
| `Amount` | Importe | Decimal | ● |  |
| `Comments` | Comentarios | Texto |  |  |

### `Booking.Booking_channel` — Canal de reserva

Canales

| Atributo | Etiqueta | Tipo | Oblig. | Referencia / valores |
|---|---|---|---|---|
| `Name` | Nombre (español) | Texto | ● |  |
| `Name_en` | Nombre (inglés) | Texto | ● |  |

### `Booking.Booking_referral` — Tipo de referencia

Cómo nos han conocido

| Atributo | Etiqueta | Tipo | Oblig. | Referencia / valores |
|---|---|---|---|---|
| `Name` | Nombre (español) | Texto | ● |  |
| `Name_en` | Nombre (inglés) | Texto | ● |  |

### `Booking.Booking_who` — Tipo de solicitante

Quien hizo la reserva

| Atributo | Etiqueta | Tipo | Oblig. | Referencia / valores |
|---|---|---|---|---|
| `Name` | Nombre (inglés) | Texto | ● |  |
| `Name_en` | Nombre (inglés) | Texto | ● |  |

### `Booking.Customer_reason` — Motivo de estancia

Motivos para residir en un recurso de Cotown. Tabla de códigos asociado a un cliente.

| Atributo | Etiqueta | Tipo | Oblig. | Referencia / valores |
|---|---|---|---|---|
| `Name` | Nombre (español) | Texto | ● |  |
| `Name_en` | Nombre (inglés) | Texto | ● |  |

### `Booking.Booking_rooming` — Rooming list

Rooming list B2C

| Atributo | Etiqueta | Tipo | Oblig. | Referencia / valores |
|---|---|---|---|---|
| `Booking_id` | Reserva | Entero | ● | → `Booking.Booking` |
| `Id_type_id` | Tipo de documento | Entero |  | → `Auxiliar.Id_type` |
| `Document` | Documento de identidad | Texto |  |  |
| `Name` | Nombre y apellidos | Texto |  |  |
| `Address` | Dirección | Texto |  |  |
| `Zip` | Código postal | Texto |  |  |
| `City` | Ciudad | Texto |  |  |
| `Province` | Provincia | Texto |  |  |
| `Country_id` | Pais | Entero |  | → `Geo.Country` |
| `Email` | Email | Texto |  |  |
| `Phones` | Teléfonos | Texto |  |  |
| `Gender_id` | Género | Entero |  | → `Auxiliar.Gender` |
| `Language_id` | Idioma | Entero |  | → `Auxiliar.Language` |
| `Nationality_id` | Nacionalidad | Entero |  | → `Geo.Country` |
| `Country_origin_id` | País de origen | Entero |  | → `Geo.Country` |

### `Booking.Booking_subtype` — Tipo de reserva LAU

Tipos de inquilinos para otras reservas

| Atributo | Etiqueta | Tipo | Oblig. | Referencia / valores |
|---|---|---|---|---|
| `Name` | Nombre (español) | Texto | ● |  |
| `Name_en` | Nombre (inglés) | Texto | ● |  |

### `Booking.Checkin_type` — Servicio check-in/check-out

Tipos de check in que un cliente puede solicitar, por ejemplo, en oficina, recogida en aeropuerto, etc.

| Atributo | Etiqueta | Tipo | Oblig. | Referencia / valores |
|---|---|---|---|---|
| `Type` | Tipo | Lista de valores |  | checkin, checkout |
| `Name` | Nombre (español) | Texto | ● |  |
| `Name_en` | Nombre (inglés) | Texto | ● |  |
| `Description` | Descripción (español) | Texto |  |  |
| `Description_en` | Descripción (inglés) | Texto |  |  |
| `Comments` | Comentarios | Texto |  |  |

### `Booking.Booking_questionnaire` — Cuestionario

Cuestionarios

| Atributo | Etiqueta | Tipo | Oblig. | Referencia / valores |
|---|---|---|---|---|
| `Booking_id` | Reserva B2C | Entero | ● | → `Booking.Booking` |
| `Questionnaire_type` | Tipo de cuestionario | Lista de valores | ● | checkin, checkout |
| `Completed` | Fecha completado | Fecha y hora |  |  |

### `Booking.Booking_search` — Búsqueda

FUTURO

| Atributo | Etiqueta | Tipo | Oblig. | Referencia / valores |
|---|---|---|---|---|

### `Booking.Booking_discount_type` — Tipo de descuento

Tipos de descuento

| Atributo | Etiqueta | Tipo | Oblig. | Referencia / valores |
|---|---|---|---|---|
| `Name` | Nombre (español) | Texto | ● |  |
| `Name_en` | Nombre (inglés) | Texto | ● |  |

### `Booking.Booking_answer` — Pregunta-Respuesta

Respuestas

| Atributo | Etiqueta | Tipo | Oblig. | Referencia / valores |
|---|---|---|---|---|
| `Questionnaire_id` | Cuestionario | Entero | ● | → `Booking.Booking_questionnaire` |
| `Question_id` | Pregunta | Entero | ● | → `Booking.Booking_question` |
| `Answer` | Respuesta | Texto |  |  |

### `Booking.Booking_photo` — Foto/Vídeo

Fotos

| Atributo | Etiqueta | Tipo | Oblig. | Referencia / valores |
|---|---|---|---|---|
| `Questionnaire_id` | Cuestionario | Entero |  | → `Booking.Booking_questionnaire` |
| `Image` | Foto/Vídeo | Documento |  |  |
| `Comments` | Comentarios | Texto |  |  |

### `Booking.Booking_doc_type` — Tipo de documento

Categorización de los tipos de documentos de reservas

| Atributo | Etiqueta | Tipo | Oblig. | Referencia / valores |
|---|---|---|---|---|
| `Name` | Nombre (español) | Texto | ● |  |
| `Name_en` | Nombre (inglés) | Texto | ● |  |

### `Booking.Booking_internal_doc` — Documento

Documentos y normas internas para las reservas

| Atributo | Etiqueta | Tipo | Oblig. | Referencia / valores |
|---|---|---|---|---|
| `Name` | Nombre (español) | Texto | ● |  |
| `Name_en` | Nombre (inglés) | Texto | ● |  |
| `Description` | Descripción (español) | Texto |  |  |
| `Description_en` | Descripción (inglés) | Texto |  |  |
| `Document` | Documento (español) | Documento |  |  |
| `Document_en` | Documento (inglés) | Documento |  |  |

### `Booking.Booking_detail` — Reserva

Tabla interna para la gestión de disponibilidad

| Atributo | Etiqueta | Tipo | Oblig. | Referencia / valores |
|---|---|---|---|---|
| `Availability_id` |  | Entero |  | → `Resource.Resource_availability` |
| `Billing_type` |  | Texto |  |  |
| `Billing_type_last` |  | Texto |  |  |
| `Booked_resource_id` |  | Entero |  | → `Resource.Resource` |
| `Booking_group_id` |  | Entero |  | → `Booking.Booking_group` |
| `Booking_id` |  | Entero |  | → `Booking.Booking` |
| `Booking_rooming_id` |  | Entero |  | → `Booking.Booking_group_rooming` |
| `Building_id` |  | Entero |  | → `Building.Building` |
| `Date_from` |  | Fecha |  |  |
| `Date_to` |  | Fecha |  |  |
| `Flat_type_id` |  | Entero |  | → `Resource.Resource_flat_type` |
| `Lock` |  | Sí/No |  |  |
| `Place_type_id` |  | Entero |  | → `Resource.Resource_place_type` |
| `Resource_id` |  | Entero |  | → `Resource.Resource` |
| `Status` |  | Texto |  |  |

### `Booking.Booking_question` — Pregunta

Preguntas

| Atributo | Etiqueta | Tipo | Oblig. | Referencia / valores |
|---|---|---|---|---|
| `Group_id` | Grupo | Entero | ● | → `Booking.Booking_question_group` |
| `Order` | Orden | Entero | ● |  |
| `Question_type` | Tipo de pregunta | Lista de valores | ● | puntos, check, texto |
| `Question` | Pregunta (español) | Texto | ● |  |
| `Question_en` | Pregunta (inglés) | Texto | ● |  |

### `Booking.Booking_question_group` — Tipo de pregunta

Preguntas

| Atributo | Etiqueta | Tipo | Oblig. | Referencia / valores |
|---|---|---|---|---|
| `Questionnaire_type` | Tipo de cuestionario | Lista de valores | ● | checkin, checkout |
| `Order` | Orden | Entero | ● |  |
| `Name` | Nombre | Texto | ● |  |
| `Description` | Título (español) | Texto |  |  |
| `Description_en` | Título (inglés) | Texto |  |  |

## Esquema `Billing` — Facturación

![ER Billing](../diagramas/er/ER%20Billing.png)

| Entidad | Nombre en el ERP | Descripción |
|---|---|---|
| `Invoice` | Factura | Facturas emitidas. |
| `Invoice_line` | Línea de factura | Líneas de las facturas emitidas. |
| `Payment` | Pago | Pagos realizados, asociados a las facturas emitidas |
| `Pricing_rate` | Tarifa | Niveles de precio de los activos. |
| `Pricing_detail` | Precio base | Precios base de los activos por cada tipología |
| `Payment_method` | Medio de pago | Inventario de los diferentes medios de pago utilizados. |
| `Promotion` | Promoción | Promociones |
| `Promotion_building` | Edificio | Edificios de una promoción |
| `Promotion_place` | Tipo de piso o de plaza | Tipos de plaza de una promoción |
| `Product` | Producto | Inventario de los posibles servicios ofrecidos y facturados. |
| `Product_type` | Tipo de producto | Clasificación de los posibles servicios ofrecidos y facturados. |
| `Tax` | Impuesto | Impuestos que pueden gravar los servicios ofrecidos por Cotown. |
| `Tax_type` | Tipo de impuesto | Tipos de impuestos que pueden gravar los servicios ofrecidos por Cotown. |

### `Billing.Invoice` — Factura

Facturas emitidas.

| Atributo | Etiqueta | Tipo | Oblig. | Referencia / valores |
|---|---|---|---|---|
| `Bill_type` | Tipo | Lista de valores |  | factura, rectificativa, recibo |
| `Code` | Nº factura/recibo | Texto |  |  |
| `Duplicate_id` | Copìar de | Entero |  |  |
| `Payment_id` | Pago | Entero |  | → `Billing.Payment` |
| `Booking_id` | Reserva | Entero |  | → `Booking.Booking` |
| `Booking_group_id` | Reserva de grupo | Entero |  | → `Booking.Booking_group` |
| `Booking_other_id` | Reserva LAU/Otros | Entero |  | → `Booking.Booking_other` |
| `Payment_method_id` | Medio de pago | Entero |  | → `Billing.Payment_method` |
| `Total` | Importe | Decimal |  |  |
| `Issued_date` | Fecha de emisión | Fecha |  |  |
| `Issued` | Emitida | Sí/No | ● |  |
| `Rectified` | Rectificar | Sí/No | ● |  |
| `Customer_id` | Cliente | Entero |  | → `Customer.Customer` |
| `Provider_id` | Emisor | Entero |  | → `Provider.Provider` |
| `Concept` | Concepto | Texto |  |  |
| `Document` | Factura/Recibo PDF | Documento |  |  |
| `Comments` | Comentarios (interno) | Texto |  |  |
| `SAP_code` | Código SAP | Texto |  |  |

### `Billing.Invoice_line` — Línea de factura

Líneas de las facturas emitidas.

| Atributo | Etiqueta | Tipo | Oblig. | Referencia / valores |
|---|---|---|---|---|
| `Invoice_id` | Nº factura | Entero | ● | → `Billing.Invoice` |
| `Product_id` | Producto/Servicio | Entero | ● | → `Billing.Product` |
| `Amount` | Importe | Decimal |  |  |
| `Tax_id` | Impuesto | Entero |  | → `Billing.Tax` |
| `Concept` | Concepto | Texto |  |  |
| `Resource_id` | Recurso | Entero |  | → `Resource.Resource` |
| `Management_fee` | Management fee | Decimal |  |  |
| `Comments` | Comentarios | Texto |  |  |

### `Billing.Payment` — Pago

Pagos realizados, asociados a las facturas emitidas

| Atributo | Etiqueta | Tipo | Oblig. | Referencia / valores |
|---|---|---|---|---|
| `Payment_type` | Tipo de pago | Lista de valores | ● | booking, deposito, servicios, checkin, checkout |
| `Amount` | Importe | Decimal | ● |  |
| `Payment_order` | Nº de orden TPV | Texto |  |  |
| `Issued_date` | Fecha emisiòn | Fecha | ● |  |
| `Payment_date` | Fecha de pago | Fecha y hora |  |  |
| `Amount_payed` | Importe pagado | Decimal |  |  |
| `Payment_method_id` | Medio de pago | Entero | ● | → `Billing.Payment_method` |
| `Pos` | TPV | Lista de valores |  | delegado, cotown, vandor |
| `Booking_id` | Reserva B2C | Entero |  | → `Booking.Booking` |
| `Payment_auth` | Código de autorización | Texto |  |  |
| `Customer_id` | Cliente | Entero | ● | → `Customer.Customer` |
| `Booking_group_id` | Reserva B2B | Entero |  | → `Booking.Booking_group` |
| `Concept` | Concepto | Texto | ● |  |
| `Booking_other_id` | Reserva LAU/Otros | Entero |  | → `Booking.Booking_other` |
| `Comments` | Comentarios | Texto |  |  |
| `Warning_1` | Aviso 1 | Fecha |  |  |
| `Warning_2` | Aviso 2 | Fecha |  |  |
| `Warning_3` | Aviso 3 | Fecha |  |  |
| `Pay` | Pagar | Texto |  |  |

### `Billing.Pricing_rate` — Tarifa

Niveles de precio de los activos.

| Atributo | Etiqueta | Tipo | Oblig. | Referencia / valores |
|---|---|---|---|---|
| `Code` | Código | Texto | ● |  |
| `Name` | Nombre | Texto | ● |  |
| `Multiplier` | Multiplicador | Decimal | ● |  |

### `Billing.Pricing_detail` — Precio base

Precios base de los activos por cada tipología

| Atributo | Etiqueta | Tipo | Oblig. | Referencia / valores |
|---|---|---|---|---|
| `Year` | Año | Entero | ● |  |
| `Building_id` | Edificio | Entero | ● | → `Building.Building` |
| `Resource_type` | Tipo de recurso | Lista de valores | ● | piso, habitacion |
| `Flat_type_id` | Tipo de piso | Entero | ● | → `Resource.Resource_flat_type` |
| `Place_type_id` | Tipo de plaza | Entero |  | → `Resource.Resource_place_type` |
| `Rent_short` | Corta estancia | Decimal | ● |  |
| `Rent_medium` | Media estancia | Decimal | ● |  |
| `Rent_long` | Larga estancia | Decimal | ● |  |
| `Rent_group` | Grupo | Decimal |  |  |
| `Services` | Servicios | Decimal | ● |  |
| `Deposit` | Garantía | Decimal | ● |  |
| `Limit` | Consumos (límite) | Decimal | ● |  |
| `Second_resident` | Segundo residente | Decimal |  |  |
| `Cleaning_price` | Precio limpieza | Decimal |  |  |
| `Final_cleaning` | Precio limpieza final | Decimal |  |  |
| `Booking_fee` | Membership fee | Decimal |  |  |

### `Billing.Payment_method` — Medio de pago

Inventario de los diferentes medios de pago utilizados.

| Atributo | Etiqueta | Tipo | Oblig. | Referencia / valores |
|---|---|---|---|---|
| `Name` | Nombre (español) | Texto | ● |  |
| `Name_en` | Nombre (inglés) | Texto | ● |  |
| `SAP_code` | Código SAP | Texto |  |  |
| `Customer` | Area interna | Sí/No | ● |  |
| `Gateway` | Redsys activo | Sí/No | ● |  |
| `SAP` | Conciliar con SAP | Sí/No |  |  |

### `Billing.Promotion` — Promoción

Promociones

| Atributo | Etiqueta | Tipo | Oblig. | Referencia / valores |
|---|---|---|---|---|
| `Name` | Nombre (español) | Texto | ● |  |
| `Date_from` | Aplicable desde | Fecha | ● |  |
| `Active_from` | Activa desde | Fecha |  |  |
| `Value_rent_pct` | Renta % Incr (+) / Desc(-) | Decimal |  |  |
| `Value_rent` | Renta € Incr(+) / Desc(-) | Decimal |  |  |
| `Name_en` | Nombre (inglés) | Texto | ● |  |
| `Date_to` | Aplicable hasta | Fecha | ● |  |
| `Active_to` | Activa hasta | Fecha |  |  |
| `Value_fee_pct` | Fees % Incr (+) / Desc(-) | Decimal |  |  |
| `Value_fee` | Fees € Incr(+) / Desc(-) | Decimal |  |  |
| `Confirm_before` | Confirmar antes de | Fecha |  |  |
| `Limit_type` | Tipo de limitación | Lista de valores |  | libre, limitado, ambos |
| `Building_id` | Edificio | Entero |  | → `Building.Building` |
| `Flat_type_id` | Tipo de piso | Entero |  | → `Resource.Resource_flat_type` |
| `Place_type_id` | Tipo de plaza | Entero |  | → `Resource.Resource_place_type` |

### `Billing.Promotion_building` — Edificio

Edificios de una promoción

| Atributo | Etiqueta | Tipo | Oblig. | Referencia / valores |
|---|---|---|---|---|
| `Promotion_id` | Promoción | Entero | ● | → `Billing.Promotion` |
| `Building_id` | Edificio | Entero | ● | → `Building.Building` |

### `Billing.Promotion_place` — Tipo de piso o de plaza

Tipos de plaza de una promoción

| Atributo | Etiqueta | Tipo | Oblig. | Referencia / valores |
|---|---|---|---|---|
| `Promotion_id` | Promoción | Entero | ● | → `Billing.Promotion` |
| `Flat_type_id` | Tipo de piso | Entero |  | → `Resource.Resource_flat_type` |
| `Place_type_id` | Tipo de plaza | Entero |  | → `Resource.Resource_place_type` |

### `Billing.Product` — Producto

Inventario de los posibles servicios ofrecidos y facturados.

| Atributo | Etiqueta | Tipo | Oblig. | Referencia / valores |
|---|---|---|---|---|
| `Product_type_id` | Tipo de producto/servcio | Entero | ● | → `Billing.Product_type` |
| `Tax_id` | Impuesto | Entero | ● | → `Billing.Tax` |
| `SAP_code` | Código SAP | Texto |  |  |
| `Name` | Nombre (español) | Texto | ● |  |
| `Name_en` | Nombre (inglés) | Texto | ● |  |

### `Billing.Product_type` — Tipo de producto

Clasificación de los posibles servicios ofrecidos y facturados.

| Atributo | Etiqueta | Tipo | Oblig. | Referencia / valores |
|---|---|---|---|---|
| `Name` | Nombre (español) | Texto | ● |  |
| `Name_en` | Nombre (inglés) | Texto | ● |  |

### `Billing.Tax` — Impuesto

Impuestos que pueden gravar los servicios ofrecidos por Cotown.

| Atributo | Etiqueta | Tipo | Oblig. | Referencia / valores |
|---|---|---|---|---|
| `Tax_type_id` | Tipo de impuesto | Entero | ● | → `Billing.Tax_type` |
| `SAP_code` | Código SAP | Texto |  |  |
| `Value` | Valor | Decimal | ● |  |
| `Name` | Nombre (español) | Texto | ● |  |
| `Name_en` | Nombre (inglés) | Texto | ● |  |

### `Billing.Tax_type` — Tipo de impuesto

Tipos de impuestos que pueden gravar los servicios ofrecidos por Cotown.

| Atributo | Etiqueta | Tipo | Oblig. | Referencia / valores |
|---|---|---|---|---|
| `Name` | Nombre (español) | Texto | ● |  |
| `Name_en` | Nombre (inglés) | Texto | ● |  |

## Esquema `Auxiliar` — Auxiliares

![ER Auxiliar](../diagramas/er/ER%20Auxiliar.png)

| Entidad | Nombre en el ERP | Descripción |
|---|---|---|
| `Segment` | Marca | Marcas o segmentos de negocio. Cada marca podrá comercializar un conjunto de productos en un sitio web. Los recursos se asociarán a marcas. |
| `School` | Escuela | Inventario de escuelas y empresas. |
| `School_category` | Tipo de escuela | Tipos de escuela |
| `Gender` | Género | Posibles géneros para asignar los residentes. |
| `Language` | Idioma | Inventario de idiomas que hablan los residentes. |
| `Id_type` | Tipo de Id | Tipos de documentos de identificación: DNI, NIE, pasaporte… Tabla de códigos, asociado a un cliente o un proveedor. |
| `Holiday` | Festivo | Festivos |
| `Timetable` | Horario | Horarios |
| `Ipc` | IPC | IPC mensual |
| `Monthname` | Mes | Nombres de los meses |
| `Sequence` | Secuencia | Secuencias |

### `Auxiliar.Segment` — Marca

Marcas o segmentos de negocio. Cada marca podrá comercializar un conjunto de productos en un sitio web. Los recursos se asociarán a marcas.

| Atributo | Etiqueta | Tipo | Oblig. | Referencia / valores |
|---|---|---|---|---|
| `Name` | Nombre | Texto | ● |  |
| `Description` | Descripción | Texto |  |  |
| `Url` | URL | Texto | ● |  |

### `Auxiliar.School` — Escuela

Inventario de escuelas y empresas.

| Atributo | Etiqueta | Tipo | Oblig. | Referencia / valores |
|---|---|---|---|---|
| `Name` | Nombre | Texto | ● |  |
| `Category` | Tipo | Entero |  | → `Auxiliar.School_category` |
| `Location_id` | Localidad | Entero |  | → `Geo.Location` |
| `Image` | Imagen | Documento |  |  |
| `Type` | Tipo | Lista de valores |  | public, private, language, other, professional |

### `Auxiliar.School_category` — Tipo de escuela

Tipos de escuela

| Atributo | Etiqueta | Tipo | Oblig. | Referencia / valores |
|---|---|---|---|---|
| `Name` | Nombre (español) | Texto | ● |  |
| `Name_en` | Nombre (inglés) | Texto | ● |  |

### `Auxiliar.Gender` — Género

Posibles géneros para asignar los residentes.

| Atributo | Etiqueta | Tipo | Oblig. | Referencia / valores |
|---|---|---|---|---|
| `Code` | Código | Texto | ● |  |
| `Name` | Nombre (español) | Texto | ● |  |
| `Name_en` | Nombre (inglés) | Texto | ● |  |

### `Auxiliar.Language` — Idioma

Inventario de idiomas que hablan los residentes.

| Atributo | Etiqueta | Tipo | Oblig. | Referencia / valores |
|---|---|---|---|---|
| `Code` | Código | Texto | ● |  |
| `Name` | Nombre (español) | Texto | ● |  |
| `Name_en` | Nombre (inglés) | Texto | ● |  |

### `Auxiliar.Id_type` — Tipo de Id

Tipos de documentos de identificación: DNI, NIE, pasaporte… Tabla de códigos, asociado a un cliente o un proveedor.

| Atributo | Etiqueta | Tipo | Oblig. | Referencia / valores |
|---|---|---|---|---|
| `Name` | Nombre (español) | Texto | ● |  |
| `Name_en` | Nombre (inglés) | Texto | ● |  |

### `Auxiliar.Holiday` — Festivo

Festivos

| Atributo | Etiqueta | Tipo | Oblig. | Referencia / valores |
|---|---|---|---|---|
| `Text` | Nombre | Texto | ● |  |
| `Day` | Fecha | Fecha | ● |  |
| `Location_id` | Localidad | Entero |  | → `Geo.Location` |

### `Auxiliar.Timetable` — Horario

Horarios

| Atributo | Etiqueta | Tipo | Oblig. | Referencia / valores |
|---|---|---|---|---|
| `Name` | Nombre | Texto | ● |  |
| `Week_from` | Lun-Jue - Desde | Hora |  |  |
| `Week_to` | Lun-Jue - Hasta | Hora |  |  |
| `Fri_from` | Vie - Desde | Hora |  |  |
| `Fri_to` | Vie - Hasta | Hora |  |  |
| `Sat_from` | Sáb - Desde | Hora |  |  |
| `Sat_to` | Sáb - Hasta | Hora |  |  |
| `Sun_from` | Dom-Fes - Desde | Hora |  |  |
| `Sun_to` | Dom-Fes - Hasta | Hora |  |  |

### `Auxiliar.Ipc` — IPC

IPC mensual

| Atributo | Etiqueta | Tipo | Oblig. | Referencia / valores |
|---|---|---|---|---|
| `Date_IPC` | Fecha | Fecha | ● |  |
| `Value_IPC` | Valor % | Decimal | ● |  |

### `Auxiliar.Monthname` — Mes

Nombres de los meses

| Atributo | Etiqueta | Tipo | Oblig. | Referencia / valores |
|---|---|---|---|---|
| `Name` | Nombre (español) | Texto | ● |  |
| `Name_en` | Nombre (inglés) | Texto | ● |  |
| `Description` | Descripción (español) | Texto |  |  |
| `Description_en` | Descripción (inglés) | Texto |  |  |

### `Auxiliar.Sequence` — Secuencia

Secuencias

| Atributo | Etiqueta | Tipo | Oblig. | Referencia / valores |
|---|---|---|---|---|
| `Payment_order` |  | Identificador | ● |  |

## Esquema `Batch` — Procesos

![ER Batch](../diagramas/er/ER%20Batch.png)

| Entidad | Nombre en el ERP | Descripción |
|---|---|---|
| `Upload` | Carga | Cargas de datos |

### `Batch.Upload` — Carga

Cargas de datos

| Atributo | Etiqueta | Tipo | Oblig. | Referencia / valores |
|---|---|---|---|---|
| `File` | Fichero | Documento | ● |  |
| `Result` | Resultado | Texto |  |  |
| `Log` | Log | Texto |  |  |

## Esquema `Marketing` — Marketing

![ER Marketing](../diagramas/er/ER%20Marketing.png)

| Entidad | Nombre en el ERP | Descripción |
|---|---|---|
| `Media` | Imagen-Vïdeo | Contenido multimedia: imágenes, documentos, videos… |
| `Faq_question` | Pregunta frecuente | Preguntas frecuentes para la web. |
| `Faq_topic` | Pregunta frecuente | Temas o grupos para las preguntas frecuentes. |
| `Post` | Post | Contenido del blog |
| `Post_tag` | Etiqueta | Etiquetas del post |
| `Tag` | Etiqueta | Etiquetas para clasificar contenidos, post, etc. |
| `Partner` | Socio | Entidades educativas o empresas que son socios de Cotown. |
| `Advantages` | Ventaja | Ventajas |
| `Testimonials` | Testimonio | Testimonios |
| `Team` | Equipo | Equipo |
| `Author` | Autor | Autores blog |
| `Contact` | Contacto | FUTURO |
| `Social_network` | Red social | Redes sociales |
| `Banner` | Banner | Redes sociales |
| `Media_amenity` | Imagen | Iconos para cada tipo de caracteritica |
| `Media_building` | Imagen | Fotos para la web para cada edificio. Un edificio puede tener varias fotos. |
| `Media_country` | Imagen | No usar |
| `Media_district` | Imagen | Fotos para la web para cada barrio o distrito. Un distrito puede tener varias fotos. |
| `Media_location` | Imagen | Fotos para la web para cada ubicación. Una ubicación puede tener varias fotos. |
| `Media_post` | Imagen | Fotos para los post |
| `Media_province` | Imagen | No usar |
| `Media_resource_type` | Imagen | Fotos para la web para cada recurso. Un recurso puede tener varias fotos. |
| `Media_service_type` | Imagen | Iconos para cada tipo de servicio |
| `Text` | Texto | Textos |

### `Marketing.Media` — Imagen-Vïdeo

Contenido multimedia: imágenes, documentos, videos…

| Atributo | Etiqueta | Tipo | Oblig. | Referencia / valores |
|---|---|---|---|---|
| `Segment_id` | Web | Entero | ● | → `Auxiliar.Segment` |
| `Code` | Código | Texto | ● |  |
| `Image` | Medio | Documento |  |  |
| `Name` | Nombre | Texto |  |  |
| `Alt` | Alt (español) | Texto |  |  |
| `Alt_en` | Alt (inglés) | Texto |  |  |
| `Name_en` | . | Texto |  |  |

### `Marketing.Faq_question` — Pregunta frecuente

Preguntas frecuentes para la web.

| Atributo | Etiqueta | Tipo | Oblig. | Referencia / valores |
|---|---|---|---|---|
| `Topic_id` | Tema | Entero |  | → `Marketing.Faq_topic` |
| `Order` | Posición | Entero | ● |  |
| `Question` | Pregunta (español) | Texto | ● |  |
| `Response` | Respuesta (español) | Texto | ● |  |
| `Question_en` | Pregunta (inglés) | Texto | ● |  |
| `Response_en` | Respuesta (inglés) | Texto | ● |  |

### `Marketing.Faq_topic` — Pregunta frecuente

Temas o grupos para las preguntas frecuentes.

| Atributo | Etiqueta | Tipo | Oblig. | Referencia / valores |
|---|---|---|---|---|
| `Segment_id` | Web | Entero | ● | → `Auxiliar.Segment` |
| `Location_id` | Ciudad | Entero |  | → `Geo.Location` |
| `Building_id` | Edificio | Entero |  | → `Building.Building` |
| `Web_type` | Tipología | Lista de valores |  | compartido, privado |
| `Order` | Posición | Entero | ● |  |
| `Name` | Título (español) | Texto | ● |  |
| `Name_en` | Título (inglés) | Texto | ● |  |

### `Marketing.Post` — Post

Contenido del blog

| Atributo | Etiqueta | Tipo | Oblig. | Referencia / valores |
|---|---|---|---|---|
| `Segment_id` | Web | Entero | ● | → `Auxiliar.Segment` |
| `Publish_date` | Fecha de publicación | Fecha | ● |  |
| `Published` | Publicado | Sí/No | ● |  |
| `Featured` | Destacado | Sí/No | ● |  |
| `Author_id` | Autor | Entero |  | → `Marketing.Team` |
| `Slug` | URL (español) | Texto | ● |  |
| `Slug_en` | URL (inglés) | Texto | ● |  |
| `Title` | Título (español) | Texto | ● |  |
| `Title_en` | Título (inglés) | Texto | ● |  |
| `Subtitle` | Resumen (español) | Texto |  |  |
| `Subtitle_en` | Resumen (inglés) | Texto |  |  |
| `Rich_content` | Contenido (español) | Texto |  |  |
| `Rich_content_en` | Contenido (inglés) | Texto |  |  |
| `Image` | Imagen | Documento |  |  |
| `Content` | Contenido (español) | Texto |  |  |
| `Content_en` | Contenido (inglés) | Texto |  |  |

### `Marketing.Post_tag` — Etiqueta

Etiquetas del post

| Atributo | Etiqueta | Tipo | Oblig. | Referencia / valores |
|---|---|---|---|---|
| `Post_id` | Post | Entero |  | → `Marketing.Post` |
| `Tag_id` | Etiqueta | Entero | ● | → `Marketing.Tag` |

### `Marketing.Tag` — Etiqueta

Etiquetas para clasificar contenidos, post, etc.

| Atributo | Etiqueta | Tipo | Oblig. | Referencia / valores |
|---|---|---|---|---|
| `Name` | Nombre (español) | Texto | ● |  |
| `Name_en` | Nombre (inglés) | Texto | ● |  |

### `Marketing.Partner` — Socio

Entidades educativas o empresas que son socios de Cotown.

| Atributo | Etiqueta | Tipo | Oblig. | Referencia / valores |
|---|---|---|---|---|
| `Segment_id` | Web | Entero | ● | → `Auxiliar.Segment` |
| `Name` | Nombre | Texto | ● |  |
| `Image` | Logo | Documento |  |  |

### `Marketing.Advantages` — Ventaja

Ventajas

| Atributo | Etiqueta | Tipo | Oblig. | Referencia / valores |
|---|---|---|---|---|
| `Segment_id` | Web | Entero | ● | → `Auxiliar.Segment` |
| `Order` | Posición | Entero | ● |  |
| `Name` | Nombre | Texto |  |  |
| `Image` | Imagen | Documento |  |  |
| `Second_image` | Segunda imagen | Documento |  |  |

### `Marketing.Testimonials` — Testimonio

Testimonios

| Atributo | Etiqueta | Tipo | Oblig. | Referencia / valores |
|---|---|---|---|---|
| `Segment_id` | Web | Entero | ● | → `Auxiliar.Segment` |
| `Name` | Nombre | Texto | ● |  |
| `Text` | Contenido (español) | Texto |  |  |
| `Text_en` | Contenido (inglés) | Texto |  |  |
| `Image` | Foto | Documento |  |  |
| `Stars` | Estrellas | Entero |  |  |
| `Date` | Fecha | Fecha |  |  |

### `Marketing.Team` — Equipo

Equipo

| Atributo | Etiqueta | Tipo | Oblig. | Referencia / valores |
|---|---|---|---|---|
| `Segment_id` | Web | Entero | ● | → `Auxiliar.Segment` |
| `Order` | Posición | Entero | ● |  |
| `Name` | Nombre y Apellidos | Texto |  |  |
| `Link` | Linkedin | Texto |  |  |
| `Position` | Cargo (español) | Texto |  |  |
| `Position_en` | Cargo (inglés) | Texto |  |  |
| `Description` | Bio (español) | Texto |  |  |
| `Description_en` | Bio (inglés) | Texto |  |  |
| `Image` | Foto | Documento |  |  |
| `Second_image` | Segunda imagen | Documento |  |  |

### `Marketing.Author` — Autor

Autores blog

| Atributo | Etiqueta | Tipo | Oblig. | Referencia / valores |
|---|---|---|---|---|
| `Segment_id` | Web | Entero | ● | → `Auxiliar.Segment` |
| `Order` | Orden | Entero | ● |  |
| `Name` | Nombre | Texto | ● |  |
| `Description` | Descripción (español) | Texto |  |  |
| `Description_en` | Descripción (inglés) | Texto |  |  |
| `Link` | Enlace | Texto |  |  |
| `Image` | Foto | Documento |  |  |

### `Marketing.Contact` — Contacto

FUTURO

| Atributo | Etiqueta | Tipo | Oblig. | Referencia / valores |
|---|---|---|---|---|
| `Contact_type` | Tipo de contacto | Lista de valores |  | contacto, cv |
| `Name` | Nombre | Texto |  |  |
| `Email` | Email | Texto |  |  |
| `Phone` | Teléfono | Texto |  |  |
| `Message` | Mensaje | Texto |  |  |
| `Attachment` | Adjunto | Documento |  |  |

### `Marketing.Social_network` — Red social

Redes sociales

| Atributo | Etiqueta | Tipo | Oblig. | Referencia / valores |
|---|---|---|---|---|
| `Segment_id` | Web | Entero | ● | → `Auxiliar.Segment` |
| `Name` | Nombre | Texto | ● |  |
| `Order` | Posición | Entero | ● |  |
| `Link` | Enlace | Texto | ● |  |

### `Marketing.Banner` — Banner

Redes sociales

| Atributo | Etiqueta | Tipo | Oblig. | Referencia / valores |
|---|---|---|---|---|
| `Segment_id` | Web | Entero | ● | → `Auxiliar.Segment` |
| `Page` | Página | Lista de valores | ● | home, equipo, ventajas |
| `Published` | Publicado | Sí/No | ● |  |
| `Text` | Texto (español) | Texto |  |  |
| `Text_en` | Texto (inglés) | Texto |  |  |
| `Link` | Enlace (español) | Texto |  |  |
| `Link_en` | Enlace (inglés) | Texto |  |  |

### `Marketing.Media_amenity` — Imagen

Iconos para cada tipo de caracteritica

| Atributo | Etiqueta | Tipo | Oblig. | Referencia / valores |
|---|---|---|---|---|
| `Amenity_type_id` | Tipo de característica | Entero | ● | → `Resource.Resource_amenity_type` |
| `Segment_id` | Web | Entero | ● | → `Auxiliar.Segment` |
| `Icon` | Icono | Documento |  |  |

### `Marketing.Media_building` — Imagen

Fotos para la web para cada edificio. Un edificio puede tener varias fotos.

| Atributo | Etiqueta | Tipo | Oblig. | Referencia / valores |
|---|---|---|---|---|
| `Building_id` | Edificio | Entero | ● | → `Building.Building` |
| `Image_type` | Tipo de imagen | Lista de valores | ● | piso, habitacion |
| `Order` | Posición | Entero | ● |  |
| `Name` | Nombre | Texto | ● |  |
| `Alt` | Alt (español) | Texto |  |  |
| `Alt_en` | Alt (inglés) | Texto |  |  |
| `Image` | Imagen | Documento |  |  |

### `Marketing.Media_country` — Imagen

No usar

| Atributo | Etiqueta | Tipo | Oblig. | Referencia / valores |
|---|---|---|---|---|
| `Country_id` |  | Entero |  | → `Geo.Country` |
| `Image_type` | Tipo de imagen | Lista de valores | ● | principal, landing, galeria, icono |
| `Order` | Posición | Entero |  |  |
| `Name` | Nombre | Texto | ● |  |
| `Image` | Imagen | Documento |  |  |

### `Marketing.Media_district` — Imagen

Fotos para la web para cada barrio o distrito. Un distrito puede tener varias fotos.

| Atributo | Etiqueta | Tipo | Oblig. | Referencia / valores |
|---|---|---|---|---|
| `District_id` | Barrio | Entero | ● | → `Geo.District` |
| `Image_type` | Tipo de imagen | Lista de valores | ● | principal, landing, galeria, icono |
| `Order` | Posición | Entero | ● |  |
| `Name` | Nombre | Texto | ● |  |
| `Alt` | Alt (español) | Texto |  |  |
| `Alt_en` | Alt (inglés) | Texto |  |  |
| `Image` | Imagen | Documento |  |  |

### `Marketing.Media_location` — Imagen

Fotos para la web para cada ubicación. Una ubicación puede tener varias fotos.

| Atributo | Etiqueta | Tipo | Oblig. | Referencia / valores |
|---|---|---|---|---|
| `Location_id` | Localidad | Entero |  | → `Geo.Location` |
| `Segment_id` | Web | Entero | ● | → `Auxiliar.Segment` |
| `Image_type` | Tipo de imagen | Lista de valores | ● | principal, landing, galeria, icono |
| `Order` | Posición | Entero | ● |  |
| `Name` | Nombre | Texto | ● |  |
| `Alt` | Alt (español) | Texto |  |  |
| `Alt_en` | Alt (inglés) | Texto |  |  |
| `Image` | Imagen | Documento |  |  |

### `Marketing.Media_post` — Imagen

Fotos para los post

| Atributo | Etiqueta | Tipo | Oblig. | Referencia / valores |
|---|---|---|---|---|
| `Post_id` | Post | Entero | ● | → `Marketing.Post` |
| `Name` | Nombre | Texto | ● |  |
| `Alt` | Alt (español) | Texto |  |  |
| `Alt_en` | Alt (inglés) | Texto |  |  |
| `Image` | Imagen | Documento |  |  |

### `Marketing.Media_province` — Imagen

No usar

| Atributo | Etiqueta | Tipo | Oblig. | Referencia / valores |
|---|---|---|---|---|
| `Province_id` |  | Entero |  | → `Geo.Province` |
| `Image_type` | Tipo de imagen | Lista de valores | ● | principal, landing, galeria, icono |
| `Order` | Posición | Entero |  |  |
| `Name` | Nombre | Texto | ● |  |
| `Alt` | Alt (español) | Texto |  |  |
| `Alt_en` | Alt (inglés) | Texto |  |  |
| `Image` | Imagen | Documento |  |  |

### `Marketing.Media_resource_type` — Imagen

Fotos para la web para cada recurso. Un recurso puede tener varias fotos.

| Atributo | Etiqueta | Tipo | Oblig. | Referencia / valores |
|---|---|---|---|---|
| `Building_id` | Edificio | Entero | ● | → `Building.Building` |
| `Flat_subtype_id` | Subtipo de piso | Entero |  | → `Resource.Resource_flat_subtype` |
| `Place_type_id` | Tipo de plaza | Entero |  | → `Resource.Resource_place_type` |
| `Order` | Posición | Entero | ● |  |
| `Alt` | Alt (español) | Texto |  |  |
| `Name` | Nombre | Texto | ● |  |
| `Alt_en` | Alt (inglés) | Texto |  |  |
| `Image` | Imagen | Documento |  |  |

### `Marketing.Media_service_type` — Imagen

Iconos para cada tipo de servicio

| Atributo | Etiqueta | Tipo | Oblig. | Referencia / valores |
|---|---|---|---|---|
| `Segment_id` | Web | Entero | ● | → `Auxiliar.Segment` |
| `Service_type_id` | Tipo de servicio | Entero | ● | → `Building.Building_service_type` |
| `Icon` | Icono | Documento |  |  |

### `Marketing.Text` — Texto

Textos

| Atributo | Etiqueta | Tipo | Oblig. | Referencia / valores |
|---|---|---|---|---|
| `Segment_id` | Web | Entero | ● | → `Auxiliar.Segment` |
| `Code` | Código | Texto | ● |  |
| `Value` | Valor (español) | Texto | ● |  |
| `Value_en` | Valor (inglés) | Texto | ● |  |
| `Summary` | Valor | Texto |  |  |

## Esquema `Admin` — Administración

![ER Admin](../diagramas/er/ER%20Admin.png)

| Entidad | Nombre en el ERP | Descripción |
|---|---|---|
| `Files` | Fichero | Ficheros |
| `Email` | Plantilla de email | Plantillas de email |
| `Email_cc` | Copiar a | CC y CCO para emails |
| `User` | Usuario | Usuarios de backoffice |
| `User_role` | Rol | Roles de cada usuario |
| `Role` | Rol | Roles de backoffice |
| `Log` | Log | Logs de cambios |
| `Notification` | Notificación | Notificaciones del sistema |
| `Param` | Parámetro | Parámetros |

### `Admin.Files` — Fichero

Ficheros

| Atributo | Etiqueta | Tipo | Oblig. | Referencia / valores |
|---|---|---|---|---|
| `Name` | Nombre | Texto | ● |  |
| `File` | Fichero | Documento | ● |  |

### `Admin.Email` — Plantilla de email

Plantillas de email

| Atributo | Etiqueta | Tipo | Oblig. | Referencia / valores |
|---|---|---|---|---|
| `Name` | Nombre | Texto | ● |  |
| `From_type` | Remitente | Lista de valores | ● | cotown, vandor |
| `Enabled` | Activo | Sí/No | ● |  |
| `Subject` | Asunto (español) | Texto | ● |  |
| `Subject_en` | Asunto (inglés) | Texto | ● |  |
| `Body` | Mensaje (español) | Texto |  |  |
| `Body_en` | Mensaje (inglés) | Texto |  |  |
| `Rich_body` | Mensaje (español) | Texto |  |  |
| `Rich_body_en` | Mensaje (inglés) | Texto |  |  |
| `Query` | Query | Texto |  |  |

### `Admin.Email_cc` — Copiar a

CC y CCO para emails

| Atributo | Etiqueta | Tipo | Oblig. | Referencia / valores |
|---|---|---|---|---|
| `Template_id` | Plantilla | Entero | ● | → `Admin.Email` |
| `Segment_id` | Marca | Entero | ● | → `Auxiliar.Segment` |
| `Cc` | CC | Texto |  |  |
| `Cco` | CCO | Texto |  |  |

### `Admin.User` — Usuario

Usuarios de backoffice

| Atributo | Etiqueta | Tipo | Oblig. | Referencia / valores |
|---|---|---|---|---|
| `Name` | Nombre y apellidos | Texto | ● |  |
| `Email` | Email | Texto | ● |  |
| `User_name` | Usuario | Texto |  |  |

### `Admin.User_role` — Rol

Roles de cada usuario

| Atributo | Etiqueta | Tipo | Oblig. | Referencia / valores |
|---|---|---|---|---|
| `User_id` | Usuario | Entero | ● | → `Admin.User` |
| `Role_id` | Rol | Entero | ● | → `Admin.Role` |

### `Admin.Role` — Rol

Roles de backoffice

| Atributo | Etiqueta | Tipo | Oblig. | Referencia / valores |
|---|---|---|---|---|
| `Name` | Nombre | Texto | ● |  |
| `Email` | Email | Texto |  |  |

### `Admin.Log` — Log

Logs de cambios

| Atributo | Etiqueta | Tipo | Oblig. | Referencia / valores |
|---|---|---|---|---|
| `Table` | Tabla | Texto |  |  |
| `Action` | Acción | Texto |  |  |
| `When` | Fecha/Hora | Fecha y hora |  |  |
| `User` | Usuario | Texto |  |  |
| `Record` | Datos | Texto |  |  |
| `Changes` | Cambios | Texto |  |  |

### `Admin.Notification` — Notificación

Notificaciones del sistema

| Atributo | Etiqueta | Tipo | Oblig. | Referencia / valores |
|---|---|---|---|---|
| `Role_id` | Rol | Entero | ● | → `Admin.Role` |
| `Sent_at` | Enviado | Fecha y hora |  |  |
| `Text` | Texto | Texto | ● |  |

### `Admin.Param` — Parámetro

Parámetros

| Atributo | Etiqueta | Tipo | Oblig. | Referencia / valores |
|---|---|---|---|---|
| `Name` | Parámetro | Texto |  |  |
| `Value` | Valor | Texto |  |  |
