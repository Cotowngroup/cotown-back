# Anexo. Permisos por rol

> Generado automáticamente a partir de la configuración de permisos de Airflows (esquema `Models`).

Abreviaturas: **L** leer, **A** alta, **M** modificar, **B** borrar, **E** exportar, **Me** visible en el menú. Un usuario de personal tiene siempre el rol base `cotown` más sus roles funcionales; sus permisos son la suma de todos ellos.

## Resumen por área

| Rol | Descripción | Propietarios | Clientes | Ubicaciones | Edificios | Activos | Reservas | Facturación | Marketing | Auxiliares | Procesos | Administración |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `cotown` | Rol base de todo el personal de Cotown | L | L | L | L | L | L | L | L | L | L | L |
| `administrators` | Administración del sistema | A M B | A M B | A M B | A M B | A M B | A M B | A M B | A M B | A M B | A M B | A M B |
| `bookings` | Reservas | – | A M B | – | – | M | A M B | L A M B | – | A M B | – | M |
| `marketing` | Marketing | – | – | A M B | A M B | A M B | – | A M B | A M B | A M B | – | A M B |
| `operations` | Operaciones | – | A | – | – | A M B | A M B | – | – | – | A | – |
| `billing` | Facturación | A M | M | – | – | – | – | A M B | – | A M B | – | A M B |
| `vandor` | Vandor (contratos LAU y otros) | A M | A M B | – | – | – | A M B | A M B | – | A M B | – | A M B |
| `provider` | Propietarios (rol base) | L A M | L | L | L | L | L | L | – | L | – | – |
| `customer` | Clientes (rol base) | L | L A M B | L | L | L | L A M B | L | – | L | – | – |
| `external` | Gestores externos (sin uso) | L | L | L | L | L | L | L | – | L | L | L |

## Pantallas del backoffice complementario

| Rol | Pantallas |
|---|---|
| `cotown` | Batch › Reports |
| `administrators` | Booking › Planning, Dashboards › Administration, Dashboards › Documents, Dashboards › General, Dashboards › LAU, Dashboards › Operations |
| `bookings` | Booking › Planning, Dashboards › Administration, Dashboards › Documents, Dashboards › General, Dashboards › LAU, Dashboards › Operations |
| `operations` | Booking › Planning, Dashboards › Documents, Dashboards › General, Dashboards › Operations |
| `billing` | Dashboards › Administration, Dashboards › LAU |
| `vandor` | Dashboards › LAU |
| `provider` | Batch › Reports |

## Rol `cotown` — Rol base de todo el personal de Cotown

| Entidad | Nombre en el ERP | Permisos |
|---|---|---|
| `Admin.Email` | Plantilla de email | L E |
| `Admin.Email_cc` | Copiar a | L E |
| `Admin.Files` | Fichero | L E |
| `Admin.Log` | Log | L E |
| `Admin.Notification` | Notificación | L E |
| `Admin.Param` | Parámetro | L E |
| `Admin.Role` | Rol | L E |
| `Admin.User` | Usuario | L E |
| `Admin.User_role` | Rol | L E |
| `Auxiliar.Gender` | Género | L E |
| `Auxiliar.Holiday` | Festivo | L E |
| `Auxiliar.Id_type` | Tipo de Id | L E |
| `Auxiliar.Ipc` | IPC | L E |
| `Auxiliar.Language` | Idioma | L E |
| `Auxiliar.Monthname` | Mes | L E |
| `Auxiliar.School` | Escuela | L E |
| `Auxiliar.School_category` | Tipo de escuela | L E |
| `Auxiliar.Segment` | Marca | L E |
| `Auxiliar.Sequence` | Secuencia | L E |
| `Auxiliar.Timetable` | Horario | L E |
| `Batch.Upload` | Carga | L E |
| `Billing.Invoice` | Factura | L E |
| `Billing.Invoice_line` | Línea de factura | L E |
| `Billing.Payment` | Pago | L E |
| `Billing.Payment_method` | Medio de pago | L E |
| `Billing.Pricing_detail` | Precio base | L E |
| `Billing.Pricing_rate` | Tarifa | L E |
| `Billing.Product` | Producto | L E |
| `Billing.Product_type` | Tipo de producto | L E |
| `Billing.Promotion` | Promoción | L E |
| `Billing.Promotion_building` | Edificio | L E |
| `Billing.Promotion_place` | Tipo de piso o de plaza | L E |
| `Billing.Tax` | Impuesto | L E |
| `Billing.Tax_type` | Tipo de impuesto | L E |
| `Booking.Booking` | Reserva B2C | L E |
| `Booking.Booking_answer` | Pregunta-Respuesta | L E |
| `Booking.Booking_channel` | Canal de reserva | L E |
| `Booking.Booking_detail` | Reserva | L E |
| `Booking.Booking_discount_type` | Tipo de descuento | L E |
| `Booking.Booking_doc` | Documento de reserva | L E |
| `Booking.Booking_doc_type` | Tipo de documento | L E |
| `Booking.Booking_group` | Reserva B2B | L E |
| `Booking.Booking_group_annex` | Anexo | L E |
| `Booking.Booking_group_doc` | Documento | L E |
| `Booking.Booking_group_price` | Precio por plaza | L E |
| `Booking.Booking_group_rooming` | Rooming list | L E |
| `Booking.Booking_group_rooms` | Habitación | L E |
| `Booking.Booking_group_service` | Concepto extra | L E |
| `Booking.Booking_internal_doc` | Documento | L E |
| `Booking.Booking_log` | Log | L E |
| `Booking.Booking_option` | Alternativa | L E |
| `Booking.Booking_other` | Reserva LAU y otros | L E |
| `Booking.Booking_other_doc` | Documento | L E |
| `Booking.Booking_other_resource` | Recurso adicional | L E |
| `Booking.Booking_other_service` | Concepto extra | L E |
| `Booking.Booking_photo` | Foto/Vídeo | L E |
| `Booking.Booking_price` | Precio | L E |
| `Booking.Booking_question` | Pregunta | L E |
| `Booking.Booking_question_group` | Tipo de pregunta | L E |
| `Booking.Booking_questionnaire` | Cuestionario | L E |
| `Booking.Booking_referral` | Tipo de referencia | L E |
| `Booking.Booking_rooming` | Rooming list | L E |
| `Booking.Booking_search` | Búsqueda | L E |
| `Booking.Booking_service` | Concepto extra | L E |
| `Booking.Booking_subtype` | Tipo de reserva LAU | L E |
| `Booking.Booking_who` | Tipo de solicitante | L E |
| `Booking.Checkin_price` | Precio | L E |
| `Booking.Checkin_type` | Servicio check-in/check-out | L E |
| `Booking.Customer_reason` | Motivo de estancia | L E |
| `Building.Building` | Edificio | L E |
| `Building.Building_doc` | Documento | L E |
| `Building.Building_doc_type` | Tipo de documento | L E |
| `Building.Building_service` | Servicio | L E |
| `Building.Building_service_type` | Tipo de servicio | L E |
| `Building.Building_text` | Textos web | L E |
| `Building.Building_transport` | Transporte | L E |
| `Building.Building_transport_type` | Tipo de transporte | L E |
| `Building.Building_type` | Tipo de venta | L E |
| `Building.Building_value` | Valoración | L E |
| `Customer.Customer` | Cliente | L E |
| `Customer.Customer_contact` | Contacto | L E |
| `Customer.Customer_contact_type` | Tipo de contacto  | L E |
| `Customer.Customer_doc` | Documento de cliente | L E |
| `Customer.Customer_doc_option` | Opción | L E |
| `Customer.Customer_doc_type` | Tipo de documento | L E |
| `Customer.Customer_email` | Email | L E |
| `Customer.Customer_fav` | Favorito | L E |
| `Customer.Customer_resident_status` | Estado de residente | L E |
| `Customer.Customer_status` | Estado de cliente | L E |
| `Geo.Country` | País | L E |
| `Geo.District` | Barrio | L E |
| `Geo.District_text` | Textos web | L E |
| `Geo.Location` | Localidad | L E |
| `Geo.Location_text` | Texto | L E |
| `Geo.Office` | Oficina | L E |
| `Geo.Province` | Provincia | L E |
| `Marketing.Advantages` | Ventaja | L E |
| `Marketing.Author` | Autor | L E |
| `Marketing.Banner` | Banner | L E |
| `Marketing.Contact` | Contacto | L E |
| `Marketing.Faq_question` | Pregunta frecuente | L E |
| `Marketing.Faq_topic` | Pregunta frecuente | L E |
| `Marketing.Media` | Imagen-Vïdeo | L E |
| `Marketing.Media_amenity` | Imagen | L E |
| `Marketing.Media_building` | Imagen | L E |
| `Marketing.Media_country` | Imagen | L E |
| `Marketing.Media_district` | Imagen | L E |
| `Marketing.Media_location` | Imagen | L E |
| `Marketing.Media_post` | Imagen | L E |
| `Marketing.Media_province` | Imagen | L E |
| `Marketing.Media_resource_type` | Imagen | L E |
| `Marketing.Media_service_type` | Imagen | L E |
| `Marketing.Partner` | Socio | L E |
| `Marketing.Post` | Post | L E |
| `Marketing.Post_tag` | Etiqueta | L E |
| `Marketing.Social_network` | Red social | L E |
| `Marketing.Tag` | Etiqueta | L E |
| `Marketing.Team` | Equipo | L E |
| `Marketing.Testimonials` | Testimonio | L E |
| `Marketing.Text` | Texto | L E |
| `Provider.Agent` | Marketplace | L E |
| `Provider.Agent_bills` | Factura | L E |
| `Provider.Agent_type` | Tipo de marketplace | L E |
| `Provider.Provider` | Propietario | L E |
| `Provider.Provider_bill` | Numero de factura | L E |
| `Provider.Provider_contact` | Contacto | L E |
| `Provider.Provider_contact_type` | Tipo de contacto  | L E |
| `Provider.Provider_contract` | Plantilla de contrato | L E |
| `Provider.Provider_doc` | Documento | L E |
| `Provider.Provider_doc_type` | Tipo de documento | L E |
| `Provider.Provider_template` | Plantilla de contrato | L E |
| `Provider.Provider_type` | Tipo de proveedor | L E |
| `Resource.Resource` | Recurso | L E |
| `Resource.Resource_amenity` | Característica | L E |
| `Resource.Resource_amenity_type` | Tipo de característica | L E |
| `Resource.Resource_availability` | Estado | L E |
| `Resource.Resource_doc` | Documento | L E |
| `Resource.Resource_doc_type` | Tipo de documento | L E |
| `Resource.Resource_flat_amenity` | Característica | L E |
| `Resource.Resource_flat_subtype` | Subtipo de piso | L E |
| `Resource.Resource_flat_type` | Tipo de piso | L E |
| `Resource.Resource_forecast` | Forecast | L E |
| `Resource.Resource_inventory` | Inventario | L E |
| `Resource.Resource_inventory_type` | Tipo de inventario | L E |
| `Resource.Resource_inventory_zone` | Zona de inventario | L E |
| `Resource.Resource_place_text` | Texto | L E |
| `Resource.Resource_place_type` | Tipo de plaza | L E |
| `Resource.Resource_price` | Precio | L E |
| `Resource.Resource_stabilised` | Stabilised | L E |
| `Resource.Resource_status` | Estado | L E |
| `Resource.Resource_subtype_text` | Textos web | L E |
| `Resource.Resource_usage` | Tipo de uso | L E |
| `Resource.Resource_value` | Valoración | L E |

Seguridad por fila: ve todas las filas.

## Rol `administrators` — Administración del sistema

| Entidad | Nombre en el ERP | Permisos |
|---|---|---|
| `Admin.Email` | Plantilla de email | A M B Me |
| `Admin.Email_cc` | Copiar a | A M B |
| `Admin.Files` | Fichero | M Me |
| `Admin.Role` | Rol | A M B Me |
| `Admin.User` | Usuario | A M B Me |
| `Admin.User_role` | Rol | A M B |
| `Auxiliar.Gender` | Género | A M B Me |
| `Auxiliar.Holiday` | Festivo | A M B Me |
| `Auxiliar.Id_type` | Tipo de Id | A M B Me |
| `Auxiliar.Ipc` | IPC | A M B Me |
| `Auxiliar.Language` | Idioma | A M B Me |
| `Auxiliar.School` | Escuela | A M B Me |
| `Auxiliar.School_category` | Tipo de escuela | A M B Me |
| `Auxiliar.Segment` | Marca | A M B Me |
| `Auxiliar.Sequence` | Secuencia | A M B |
| `Auxiliar.Timetable` | Horario | A M B Me |
| `Batch.Upload` | Carga | A M B Me |
| `Billing.Invoice` | Factura | A M B Me |
| `Billing.Invoice_line` | Línea de factura | A M B |
| `Billing.Payment` | Pago | M B Me |
| `Billing.Payment_method` | Medio de pago | A M B Me |
| `Billing.Pricing_detail` | Precio base | A M B Me |
| `Billing.Pricing_rate` | Tarifa | A M B Me |
| `Billing.Product` | Producto | A M B Me |
| `Billing.Product_type` | Tipo de producto | A M B Me |
| `Billing.Promotion` | Promoción | A M B Me |
| `Billing.Promotion_building` | Edificio | A M B |
| `Billing.Promotion_place` | Tipo de piso o de plaza | A M B |
| `Billing.Tax` | Impuesto | A M B Me |
| `Billing.Tax_type` | Tipo de impuesto | A M B Me |
| `Booking.Booking` | Reserva B2C | Me |
| `Booking.Booking_answer` | Pregunta-Respuesta | A M B |
| `Booking.Booking_channel` | Canal de reserva | A M B Me |
| `Booking.Booking_detail` | Reserva | A M B |
| `Booking.Booking_discount_type` | Tipo de descuento | A M B Me |
| `Booking.Booking_doc` | Documento de reserva | A M B |
| `Booking.Booking_doc_type` | Tipo de documento | A M B |
| `Booking.Booking_group` | Reserva B2B | A M B Me |
| `Booking.Booking_group_annex` | Anexo | A M B |
| `Booking.Booking_group_doc` | Documento | A M B |
| `Booking.Booking_group_price` | Precio por plaza | A M B |
| `Booking.Booking_group_rooming` | Rooming list | A M B |
| `Booking.Booking_group_rooms` | Habitación | A M B |
| `Booking.Booking_group_service` | Concepto extra | A M B |
| `Booking.Booking_internal_doc` | Documento | A M B Me |
| `Booking.Booking_log` | Log | A M B |
| `Booking.Booking_option` | Alternativa | A M B |
| `Booking.Booking_other` | Reserva LAU y otros | A M B Me |
| `Booking.Booking_other_doc` | Documento | A M B |
| `Booking.Booking_other_resource` | Recurso adicional | A M B |
| `Booking.Booking_other_service` | Concepto extra | A M B |
| `Booking.Booking_price` | Precio | A M B |
| `Booking.Booking_question` | Pregunta | M |
| `Booking.Booking_question_group` | Tipo de pregunta | M Me |
| `Booking.Booking_questionnaire` | Cuestionario | A M B Me |
| `Booking.Booking_referral` | Tipo de referencia | A M B Me |
| `Booking.Booking_rooming` | Rooming list | A M B |
| `Booking.Booking_service` | Concepto extra | A M B |
| `Booking.Booking_subtype` | Tipo de reserva LAU | A M B Me |
| `Booking.Booking_who` | Tipo de solicitante | A M B Me |
| `Booking.Checkin_price` | Precio | A M B |
| `Booking.Checkin_type` | Servicio check-in/check-out | A M B Me |
| `Booking.Customer_reason` | Motivo de estancia | A M B Me |
| `Building.Building` | Edificio | A M B Me |
| `Building.Building_doc` | Documento | A M B |
| `Building.Building_doc_type` | Tipo de documento | A M B Me |
| `Building.Building_service` | Servicio | A M B |
| `Building.Building_service_type` | Tipo de servicio | A M B Me |
| `Building.Building_text` | Textos web | A M B |
| `Building.Building_transport` | Transporte | A M B |
| `Building.Building_transport_type` | Tipo de transporte | A M B Me |
| `Building.Building_type` | Tipo de venta | A M B Me |
| `Building.Building_value` | Valoración | A M B |
| `Customer.Customer` | Cliente | A M B Me |
| `Customer.Customer_contact` | Contacto | A M B |
| `Customer.Customer_contact_type` | Tipo de contacto  | A M B Me |
| `Customer.Customer_doc` | Documento de cliente | A M B |
| `Customer.Customer_doc_option` | Opción | A M B |
| `Customer.Customer_doc_type` | Tipo de documento | A M B Me |
| `Customer.Customer_email` | Email | A M B |
| `Customer.Customer_fav` | Favorito | A M B |
| `Geo.Country` | País | A M B Me |
| `Geo.District` | Barrio | A M B Me |
| `Geo.District_text` | Textos web | A M B |
| `Geo.Location` | Localidad | A M B Me |
| `Geo.Location_text` | Texto | A M B |
| `Geo.Office` | Oficina | A M B Me |
| `Geo.Province` | Provincia | A M B Me |
| `Marketing.Advantages` | Ventaja | A M B Me |
| `Marketing.Banner` | Banner | A M B Me |
| `Marketing.Faq_question` | Pregunta frecuente | A M B |
| `Marketing.Faq_topic` | Pregunta frecuente | A M B Me |
| `Marketing.Media` | Imagen-Vïdeo | A M B Me |
| `Marketing.Media_amenity` | Imagen | A M B |
| `Marketing.Media_building` | Imagen | A M B |
| `Marketing.Media_country` | Imagen | A M B |
| `Marketing.Media_district` | Imagen | A M B |
| `Marketing.Media_location` | Imagen | A M B |
| `Marketing.Media_post` | Imagen | A M B |
| `Marketing.Media_province` | Imagen | A M B |
| `Marketing.Media_resource_type` | Imagen | A M B |
| `Marketing.Media_service_type` | Imagen | A M B |
| `Marketing.Partner` | Socio | A M B Me |
| `Marketing.Post` | Post | A M B Me |
| `Marketing.Post_tag` | Etiqueta | A M B |
| `Marketing.Social_network` | Red social | A M B Me |
| `Marketing.Tag` | Etiqueta | A M B Me |
| `Marketing.Team` | Equipo | A M B Me |
| `Marketing.Testimonials` | Testimonio | A M B Me |
| `Marketing.Text` | Texto | A M B Me |
| `Provider.Agent` | Marketplace | A M B |
| `Provider.Agent_bills` | Factura | A M B |
| `Provider.Agent_type` | Tipo de marketplace | A M B |
| `Provider.Provider` | Propietario | A M B Me |
| `Provider.Provider_bill` | Numero de factura | A M B |
| `Provider.Provider_contact` | Contacto | A M B |
| `Provider.Provider_contact_type` | Tipo de contacto  | A M B Me |
| `Provider.Provider_contract` | Plantilla de contrato | A M B Me |
| `Provider.Provider_doc` | Documento | A M B |
| `Provider.Provider_doc_type` | Tipo de documento | A M B Me |
| `Provider.Provider_template` | Plantilla de contrato | A M B |
| `Provider.Provider_type` | Tipo de proveedor | A M B Me |
| `Resource.Resource` | Recurso | A M B Me |
| `Resource.Resource_amenity` | Característica | A M B |
| `Resource.Resource_amenity_type` | Tipo de característica | A M B Me |
| `Resource.Resource_availability` | Estado | A M B |
| `Resource.Resource_doc` | Documento | A M B |
| `Resource.Resource_doc_type` | Tipo de documento | A M B Me |
| `Resource.Resource_flat_amenity` | Característica | A M B |
| `Resource.Resource_flat_subtype` | Subtipo de piso | A M B Me |
| `Resource.Resource_flat_type` | Tipo de piso | A M B Me |
| `Resource.Resource_forecast` | Forecast | A M B |
| `Resource.Resource_inventory` | Inventario | A M B |
| `Resource.Resource_inventory_type` | Tipo de inventario | A M B Me |
| `Resource.Resource_inventory_zone` | Zona de inventario | A M B Me |
| `Resource.Resource_place_text` | Texto | A M B |
| `Resource.Resource_place_type` | Tipo de plaza | A M B Me |
| `Resource.Resource_price` | Precio | A M B |
| `Resource.Resource_stabilised` | Stabilised | A M B |
| `Resource.Resource_status` | Estado | A M B Me |
| `Resource.Resource_subtype_text` | Textos web | A M B |
| `Resource.Resource_usage` | Tipo de uso | A M B |
| `Resource.Resource_value` | Valoración | A M B |

Campos que este rol puede informar o modificar (en el resto de campos de esas entidades, solo lectura):

| Entidad | Campos |
|---|---|
| `Booking.Booking` | # (A M), Aviso compañeros (A M), Cambio gestionado (A M), Canal (A M), Check in (A M), Check in OK (A M), Check out (A M), Check out OK (A M), Comentarios (A M), Comisión (A M), Consumos (límite) (A M), Contrato de renta (A M), Contrato de servicios (A M), Created_at (A M), Created_by (A M), Cómo nos conoció (A M), Descartar (A M), Desperfectos (A M), Desperfectos gestionados (A M), Documentación antes de (A M), Edificio (A M), Empresa (A M), Enviar alternativas (A M), Escuela (A M), Escuela (otro) (A M), Estado (M), Estado INCASOL (A M), Estado del contrato (A M), Estado factura (A M), Facturación primer mes (A M), Facturación último mes (A M), Fecha de confirmación (A M), Fecha de estado (A M), Fecha de solicitud (A M), Fecha desde (A M), Fecha devuelta (A M), Fecha hasta (A M), Fecha original de check-ou (A M), Fecha requerida (A M), Fianza INCASOL (A M), Frecuencia de limpieza (A M), Garantía depositada (A M), Garantía devolución requerida (A M), Garantía devuelta (A M), Garantía teórica (A M), Gastos repercutibles (A M), Habitación ok (A M), Habitación revisada ok (A M), Hora de check-in (A M), Hora de llegada (A M), Hora de recogida (A M), IVA (A M), Id Contrato (A M), Ignorar lista negra (A M), Incidencias entrada (A M), Incidencias gestionadas (A M), Limpieza final (A M), Llave móvil actualizada (A M), Llave móvil off (A M), Llaves devueltas (A M), Llaves keyless ok (A M), Llaves ok (A M), Marketplace (A M), Membership fee a pagar (A M), Membership fee devuelto (A M), Membership fee pagado (A M), Membership fee teórico (A M), Membership marketplace (A M), Mobiliario (A M), Motivo de estancia (A M), Motivo suplemento/descuento (A M), No cambiar asignación (A M), Nota en factura (A M), Nueva fecha de salida (A M), Nº registro (A M), Opción (A M), Opción (A M), Penalización ECO (A M), Promoción (A M), Quién hizo la reserva (A M), Reactivar (A M), Recurso (A M), Renta (A M), Reserva destino (A M), Reserva master B2B (A M), Reserva origen (A M), Reserva relacionada (A M), Residente (A M), Residente (A M), Retenida temporalmente (A M), Search (A M), Segundo residente (A M), Servicios (A M), Tipo de limitación (A M), Tipo de recurso (A M), Tipo de relación (A M), Tipo de reserva (A M), Tipología de piso (A M), Tipología de plaza (A M), Updated_at (A M), Updated_by (A M), Valida hasta (A M), Vuelo/Tren (A M), Vuelo/Tren (A M) |

## Rol `bookings` — Reservas

| Entidad | Nombre en el ERP | Permisos |
|---|---|---|
| `Admin.Email` | Plantilla de email | M Me |
| `Auxiliar.School` | Escuela | A M B Me |
| `Billing.Invoice` | Factura | Me |
| `Billing.Invoice_line` | Línea de factura | A M B |
| `Billing.Payment` | Pago | M Me |
| `Billing.Product` | Producto | L A M B Me |
| `Booking.Booking` | Reserva B2C | Me |
| `Booking.Booking_channel` | Canal de reserva | Me |
| `Booking.Booking_detail` | Reserva | A M B |
| `Booking.Booking_discount_type` | Tipo de descuento | A M B |
| `Booking.Booking_group` | Reserva B2B | A M B Me |
| `Booking.Booking_group_annex` | Anexo | A M B |
| `Booking.Booking_group_price` | Precio por plaza | A M B |
| `Booking.Booking_group_rooming` | Rooming list | M |
| `Booking.Booking_group_rooms` | Habitación | A M B |
| `Booking.Booking_group_service` | Concepto extra | A M B |
| `Booking.Booking_internal_doc` | Documento | Me |
| `Booking.Booking_log` | Log | A M B |
| `Booking.Booking_option` | Alternativa | A M B |
| `Booking.Booking_other` | Reserva LAU y otros | A M B Me |
| `Booking.Booking_other_doc` | Documento | A M B |
| `Booking.Booking_other_resource` | Recurso adicional | A M B |
| `Booking.Booking_other_service` | Concepto extra | A M B |
| `Booking.Booking_price` | Precio | A M B |
| `Booking.Booking_questionnaire` | Cuestionario | Me |
| `Booking.Booking_referral` | Tipo de referencia | Me |
| `Booking.Booking_rooming` | Rooming list | A M B |
| `Booking.Booking_service` | Concepto extra | A M B |
| `Booking.Booking_subtype` | Tipo de reserva LAU | A M B Me |
| `Booking.Booking_who` | Tipo de solicitante | Me |
| `Booking.Checkin_type` | Servicio check-in/check-out | Me |
| `Booking.Customer_reason` | Motivo de estancia | Me |
| `Building.Building` | Edificio | Me |
| `Customer.Customer` | Cliente | A M B Me |
| `Customer.Customer_contact` | Contacto | A M B |
| `Customer.Customer_doc` | Documento de cliente | A M B |
| `Customer.Customer_email` | Email | A M B |
| `Customer.Customer_fav` | Favorito | A M B |
| `Geo.District` | Barrio | Me |
| `Resource.Resource` | Recurso | M Me |

Campos que este rol puede informar o modificar (en el resto de campos de esas entidades, solo lectura):

| Entidad | Campos |
|---|---|
| `Booking.Booking` | # (A M), Aviso compañeros (A M), Cambio gestionado (A M), Canal (A M), Check in (A M), Check in OK (A M), Check in solicitado (A M), Check out (A M), Check out OK (A M), Comentarios (A M), Comisión (A M), Consumos (límite) (A M), Contrato de renta (A M), Contrato de servicios (A M), Created_at (A M), Created_by (A M), Cómo nos conoció (A M), Descartar (A M), Desperfectos (A M), Desperfectos gestionados (A M), Documentación antes de (A M), Edificio (A M), Empresa (A M), Enviar alternativas (A M), Escuela (A M), Escuela (otro) (A M), Estado (A M), Estado INCASOL (A M), Estado del contrato (A M), Estado factura (A M), Facturación primer mes (A M), Facturación último mes (A M), Fecha de confirmación (A M), Fecha de estado (A M), Fecha de solicitud (A M), Fecha desde (A M), Fecha devuelta (A M), Fecha hasta (A M), Fecha original de check-ou (A M), Fecha requerida (A M), Fianza INCASOL (A M), Frecuencia de limpieza (A M), Garantía depositada (A M), Garantía devolución requerida (A M), Garantía devuelta (A M), Garantía teórica (A M), Gastos repercutibles (A M), Habitación ok (A M), Habitación revisada ok (A M), Hora de check-in (A M), Hora de llegada (A M), Hora de recogida (A M), IVA (A M), Id Contrato (A M), Ignorar lista negra (A M), Incidencias entrada (A M), Incidencias gestionadas (A M), Limpieza final (A M), Llave móvil actualizada (A M), Llave móvil off (A M), Llaves devueltas (A M), Llaves keyless ok (A M), Llaves ok (A M), Marketplace (A M), Membership fee a pagar (A M), Membership fee devuelto (A M), Membership fee pagado (A M), Membership fee teórico (A M), Membership marketplace (A M), Mobiliario (A M), Motivo de estancia (A M), Motivo suplemento/descuento (A M), No cambiar asignación (A M), Nota en factura (A M), Nueva fecha de salida (A M), Nº registro (A M), Opción (A M), Opción (A M), Penalización ECO (A M), Promoción (A M), Quién hizo la reserva (A M), Reactivar (A M), Recurso (A M), Renta (A M), Reserva destino (A M), Reserva master B2B (A M), Reserva origen (A M), Reserva relacionada (A M), Residente (A M), Residente (A M), Retenida temporalmente (A M), Search (A M), Segundo residente (A M), Servicios (A M), Tipo de limitación (A M), Tipo de recurso (A M), Tipo de relación (A M), Tipo de reserva (A M), Tipología de piso (A M), Tipología de plaza (A M), Updated_at (A M), Updated_by (A M), Valida hasta (A M), Vuelo/Tren (A M), Vuelo/Tren (A M) |
| `Resource.Resource` | Notas (limpieza, tipo de suelo…) (A M) |

## Rol `marketing` — Marketing

| Entidad | Nombre en el ERP | Permisos |
|---|---|---|
| `Admin.Email` | Plantilla de email | A M B Me |
| `Auxiliar.School` | Escuela | A M B Me |
| `Billing.Promotion` | Promoción | A M B Me |
| `Billing.Promotion_building` | Edificio | A M B |
| `Billing.Promotion_place` | Tipo de piso o de plaza | A M B |
| `Booking.Booking` | Reserva B2C | Me |
| `Booking.Booking_group` | Reserva B2B | Me |
| `Building.Building` | Edificio | M Me |
| `Building.Building_service` | Servicio | M |
| `Building.Building_service_type` | Tipo de servicio | M Me |
| `Building.Building_text` | Textos web | A M B |
| `Building.Building_transport` | Transporte | M |
| `Building.Building_transport_type` | Tipo de transporte | M Me |
| `Building.Building_type` | Tipo de venta | M Me |
| `Building.Building_value` | Valoración | A M B |
| `Customer.Customer` | Cliente | Me |
| `Geo.District` | Barrio | A M B Me |
| `Geo.District_text` | Textos web | A M B |
| `Geo.Location` | Localidad | A M B Me |
| `Geo.Office` | Oficina | A M B |
| `Marketing.Advantages` | Ventaja | A M B Me |
| `Marketing.Banner` | Banner | A M B Me |
| `Marketing.Faq_question` | Pregunta frecuente | A M B |
| `Marketing.Faq_topic` | Pregunta frecuente | A M B Me |
| `Marketing.Media` | Imagen-Vïdeo | A M B Me |
| `Marketing.Media_amenity` | Imagen | A M B |
| `Marketing.Media_building` | Imagen | A M B |
| `Marketing.Media_country` | Imagen | A M B |
| `Marketing.Media_district` | Imagen | A M B |
| `Marketing.Media_location` | Imagen | A M B |
| `Marketing.Media_post` | Imagen | A M B |
| `Marketing.Media_province` | Imagen | A M B |
| `Marketing.Media_resource_type` | Imagen | A M B |
| `Marketing.Media_service_type` | Imagen | A M B |
| `Marketing.Partner` | Socio | A M B Me |
| `Marketing.Post` | Post | A M B Me |
| `Marketing.Post_tag` | Etiqueta | A M B |
| `Marketing.Social_network` | Red social | A M B Me |
| `Marketing.Tag` | Etiqueta | A M B Me |
| `Marketing.Team` | Equipo | A M B Me |
| `Marketing.Testimonials` | Testimonio | A M B Me |
| `Marketing.Text` | Texto | A M B Me |
| `Resource.Resource` | Recurso | A M B Me |
| `Resource.Resource_amenity` | Característica | A M B |
| `Resource.Resource_availability` | Estado | A M B |
| `Resource.Resource_doc` | Documento | A M B |
| `Resource.Resource_flat_amenity` | Característica | A M B |
| `Resource.Resource_flat_subtype` | Subtipo de piso | A M B Me |
| `Resource.Resource_flat_type` | Tipo de piso | A M B Me |
| `Resource.Resource_inventory` | Inventario | A M B |
| `Resource.Resource_place_text` | Texto | A M B |
| `Resource.Resource_place_type` | Tipo de plaza | A M B Me |
| `Resource.Resource_price` | Precio | A M B |
| `Resource.Resource_subtype_text` | Textos web | A M B |

## Rol `operations` — Operaciones

| Entidad | Nombre en el ERP | Permisos |
|---|---|---|
| `Batch.Upload` | Carga | A Me |
| `Booking.Booking` | Reserva B2C | M Me |
| `Booking.Booking_group` | Reserva B2B | M Me |
| `Booking.Booking_group_rooming` | Rooming list | A M B |
| `Booking.Booking_price` | Precio | A M B |
| `Booking.Booking_question_group` | Tipo de pregunta | Me |
| `Booking.Booking_service` | Concepto extra | A M B |
| `Building.Building` | Edificio | Me |
| `Customer.Customer` | Cliente | Me |
| `Customer.Customer_email` | Email | A |
| `Resource.Resource` | Recurso | Me |
| `Resource.Resource_inventory_type` | Tipo de inventario | A M B Me |
| `Resource.Resource_inventory_zone` | Zona de inventario | A M B Me |

Campos que este rol puede informar o modificar (en el resto de campos de esas entidades, solo lectura):

| Entidad | Campos |
|---|---|
| `Booking.Booking` | # (A M), Aviso compañeros (A M), Cambio gestionado (A M), Canal (A M), Check in (A M), Check in OK (A M), Check in solicitado (A M), Check out (A M), Check out OK (A M), Comentarios (A M), Comisión (A M), Consumos (límite) (A M), Contrato de renta (A M), Contrato de servicios (A M), Created_at (A M), Created_by (A M), Cómo nos conoció (A M), Descartar (A M), Desperfectos (A M), Desperfectos gestionados (A M), Documentación antes de (A M), Edificio (A M), Empresa (A M), Enviar alternativas (A M), Escuela (A M), Escuela (otro) (A M), Estado (A M), Estado INCASOL (A M), Estado del contrato (A M), Estado factura (A M), Facturación primer mes (A M), Facturación último mes (A M), Fecha de confirmación (A M), Fecha de estado (A M), Fecha de solicitud (A M), Fecha desde (A M), Fecha devuelta (A M), Fecha hasta (A M), Fecha original de check-ou (A M), Fecha requerida (A M), Fianza INCASOL (A M), Frecuencia de limpieza (A M), Garantía depositada (A M), Garantía devolución requerida (A M), Garantía devuelta (A M), Garantía teórica (A M), Gastos repercutibles (A M), Habitación ok (A M), Habitación revisada ok (A M), Hora de check-in (A M), Hora de llegada (A M), Hora de recogida (A M), IVA (A M), Id Contrato (A M), Ignorar lista negra (A M), Incidencias entrada (A M), Incidencias gestionadas (A M), Limpieza final (A M), Llave móvil actualizada (A M), Llave móvil off (A M), Llaves devueltas (A M), Llaves keyless ok (A M), Llaves ok (A M), Marketplace (A M), Membership fee a pagar (A M), Membership fee devuelto (A M), Membership fee pagado (A M), Membership fee teórico (A M), Membership marketplace (A M), Mobiliario (A M), Motivo de estancia (A M), Motivo suplemento/descuento (A M), No cambiar asignación (A M), Nota en factura (A M), Nueva fecha de salida (A M), Nº registro (A M), Opción (A M), Opción (A M), Penalización ECO (A M), Promoción (A M), Quién hizo la reserva (A M), Reactivar (A M), Recurso (A M), Renta (A M), Reserva destino (A M), Reserva master B2B (A M), Reserva origen (A M), Reserva relacionada (A M), Residente (A M), Residente (A M), Retenida temporalmente (A M), Search (A M), Segundo residente (A M), Servicios (A M), Tipo de limitación (A M), Tipo de recurso (A M), Tipo de relación (A M), Tipo de reserva (A M), Tipología de piso (A M), Tipología de plaza (A M), Updated_at (A M), Updated_by (A M), Valida hasta (A M), Vuelo/Tren (A M), Vuelo/Tren (A M) |

## Rol `billing` — Facturación

| Entidad | Nombre en el ERP | Permisos |
|---|---|---|
| `Admin.Email` | Plantilla de email | A M B Me |
| `Auxiliar.Sequence` | Secuencia | A M B |
| `Billing.Invoice` | Factura | A M B Me |
| `Billing.Invoice_line` | Línea de factura | A M B |
| `Billing.Payment` | Pago | M B Me |
| `Billing.Product` | Producto | A M B Me |
| `Billing.Product_type` | Tipo de producto | A M B Me |
| `Booking.Booking` | Reserva B2C | Me |
| `Booking.Booking_group` | Reserva B2B | Me |
| `Booking.Booking_other` | Reserva LAU y otros | Me |
| `Booking.Booking_subtype` | Tipo de reserva LAU | Me |
| `Building.Building` | Edificio | Me |
| `Customer.Customer` | Cliente | M Me |
| `Provider.Provider` | Propietario | M Me |
| `Provider.Provider_bill` | Numero de factura | A M |
| `Provider.Provider_contract` | Plantilla de contrato | A M |
| `Provider.Provider_template` | Plantilla de contrato | A M |

## Rol `vandor` — Vandor (contratos LAU y otros)

| Entidad | Nombre en el ERP | Permisos |
|---|---|---|
| `Admin.Email` | Plantilla de email | A M B Me |
| `Auxiliar.Ipc` | IPC | A M B Me |
| `Auxiliar.Sequence` | Secuencia | A M B |
| `Billing.Invoice` | Factura | A M B Me |
| `Billing.Invoice_line` | Línea de factura | A M B |
| `Billing.Payment` | Pago | A M B Me |
| `Billing.Product` | Producto | A M B Me |
| `Billing.Product_type` | Tipo de producto | A M B Me |
| `Booking.Booking` | Reserva B2C | Me |
| `Booking.Booking_group` | Reserva B2B | Me |
| `Booking.Booking_other` | Reserva LAU y otros | A M B Me |
| `Booking.Booking_other_doc` | Documento | A M B |
| `Booking.Booking_other_resource` | Recurso adicional | A M B |
| `Booking.Booking_other_service` | Concepto extra | A M B |
| `Booking.Booking_subtype` | Tipo de reserva LAU | A M B Me |
| `Building.Building` | Edificio | Me |
| `Customer.Customer` | Cliente | A M Me |
| `Customer.Customer_contact` | Contacto | A M B |
| `Provider.Provider` | Propietario | M Me |
| `Provider.Provider_bill` | Numero de factura | A M |
| `Provider.Provider_contract` | Plantilla de contrato | A M |
| `Provider.Provider_template` | Plantilla de contrato | A M |

## Rol `provider` — Propietarios (rol base)

| Entidad | Nombre en el ERP | Permisos |
|---|---|---|
| `Auxiliar.Gender` | Género | L |
| `Auxiliar.Id_type` | Tipo de Id | L |
| `Auxiliar.Language` | Idioma | L |
| `Auxiliar.Monthname` | Mes | L |
| `Auxiliar.School` | Escuela | L |
| `Auxiliar.Segment` | Marca | L |
| `Billing.Invoice` | Factura | L Me |
| `Billing.Invoice_line` | Línea de factura | L |
| `Billing.Payment` | Pago | L Me |
| `Billing.Payment_method` | Medio de pago | L |
| `Billing.Pricing_detail` | Precio base | L |
| `Billing.Pricing_rate` | Tarifa | L |
| `Billing.Product` | Producto | L |
| `Billing.Product_type` | Tipo de producto | L |
| `Billing.Promotion` | Promoción | L |
| `Billing.Tax` | Impuesto | L |
| `Billing.Tax_type` | Tipo de impuesto | L |
| `Booking.Booking` | Reserva B2C | L |
| `Booking.Booking_channel` | Canal de reserva | L |
| `Booking.Booking_detail` | Reserva | L |
| `Booking.Booking_discount_type` | Tipo de descuento | L |
| `Booking.Booking_group` | Reserva B2B | L |
| `Booking.Booking_group_price` | Precio por plaza | L |
| `Booking.Booking_group_rooming` | Rooming list | L |
| `Booking.Booking_other` | Reserva LAU y otros | L |
| `Booking.Booking_price` | Precio | L |
| `Booking.Booking_questionnaire` | Cuestionario | L |
| `Booking.Booking_referral` | Tipo de referencia | L |
| `Booking.Booking_subtype` | Tipo de reserva LAU | L |
| `Booking.Booking_who` | Tipo de solicitante | L |
| `Booking.Checkin_type` | Servicio check-in/check-out | L |
| `Booking.Customer_reason` | Motivo de estancia | L |
| `Building.Building` | Edificio | L |
| `Building.Building_doc` | Documento | L |
| `Building.Building_doc_type` | Tipo de documento | L |
| `Building.Building_service_type` | Tipo de servicio | L |
| `Building.Building_transport_type` | Tipo de transporte | L |
| `Building.Building_type` | Tipo de venta | L |
| `Customer.Customer` | Cliente | L Me |
| `Customer.Customer_doc` | Documento de cliente | L |
| `Customer.Customer_doc_option` | Opción | L |
| `Customer.Customer_doc_type` | Tipo de documento | L |
| `Geo.Country` | País | L |
| `Geo.District` | Barrio | L |
| `Geo.Location` | Localidad | L |
| `Geo.Province` | Provincia | L |
| `Provider.Agent` | Marketplace | L |
| `Provider.Agent_type` | Tipo de marketplace | L |
| `Provider.Provider` | Propietario | L Me |
| `Provider.Provider_bill` | Numero de factura | L |
| `Provider.Provider_contact` | Contacto | L A M |
| `Provider.Provider_contact_type` | Tipo de contacto  | L |
| `Provider.Provider_contract` | Plantilla de contrato | L |
| `Provider.Provider_doc` | Documento | L |
| `Provider.Provider_doc_type` | Tipo de documento | L |
| `Provider.Provider_template` | Plantilla de contrato | L |
| `Provider.Provider_type` | Tipo de proveedor | L |
| `Resource.Resource` | Recurso | L |
| `Resource.Resource_amenity` | Característica | L |
| `Resource.Resource_amenity_type` | Tipo de característica | L |
| `Resource.Resource_availability` | Estado | L |
| `Resource.Resource_doc_type` | Tipo de documento | L |
| `Resource.Resource_flat_subtype` | Subtipo de piso | L |
| `Resource.Resource_flat_type` | Tipo de piso | L |
| `Resource.Resource_inventory` | Inventario | L |
| `Resource.Resource_inventory_type` | Tipo de inventario | L |
| `Resource.Resource_inventory_zone` | Zona de inventario | L |
| `Resource.Resource_place_type` | Tipo de plaza | L |
| `Resource.Resource_status` | Estado | L |
| `Resource.Resource_usage` | Tipo de uso | L |

Seguridad por fila: solo ve las filas propias en `Billing.Invoice_line`, `Billing.Invoice`, `Billing.Pricing_detail`, `Booking.Booking_group_price`, `Booking.Booking_group_rooming`, `Booking.Booking_group`, `Booking.Booking_price`, `Booking.Booking`, `Building.Building`, `Customer.Customer`, `Provider.Provider_contact`, `Provider.Provider_template`, `Provider.Provider`, `Resource.Resource_amenity`, `Resource.Resource_availability`, `Resource.Resource_doc`, `Resource.Resource_inventory`, `Resource.Resource`.

## Rol `customer` — Clientes (rol base)

| Entidad | Nombre en el ERP | Permisos |
|---|---|---|
| `Auxiliar.Gender` | Género | L |
| `Auxiliar.Holiday` | Festivo | L |
| `Auxiliar.Id_type` | Tipo de Id | L |
| `Auxiliar.Language` | Idioma | L |
| `Auxiliar.School` | Escuela | L |
| `Auxiliar.Segment` | Marca | L |
| `Auxiliar.Timetable` | Horario | L |
| `Billing.Invoice` | Factura | L Me |
| `Billing.Payment` | Pago | L Me |
| `Billing.Payment_method` | Medio de pago | L |
| `Billing.Product` | Producto | L |
| `Billing.Product_type` | Tipo de producto | L |
| `Billing.Promotion` | Promoción | L |
| `Billing.Tax` | Impuesto | L |
| `Billing.Tax_type` | Tipo de impuesto | L |
| `Booking.Booking` | Reserva B2C | L Me |
| `Booking.Booking_channel` | Canal de reserva | L |
| `Booking.Booking_discount_type` | Tipo de descuento | L |
| `Booking.Booking_group` | Reserva B2B | L |
| `Booking.Booking_group_price` | Precio por plaza | L |
| `Booking.Booking_group_rooming` | Rooming list | L M |
| `Booking.Booking_internal_doc` | Documento | L |
| `Booking.Booking_option` | Alternativa | L A M B E |
| `Booking.Booking_photo` | Foto/Vídeo | L A |
| `Booking.Booking_price` | Precio | L |
| `Booking.Booking_question` | Pregunta | L |
| `Booking.Booking_question_group` | Tipo de pregunta | L |
| `Booking.Booking_questionnaire` | Cuestionario | L |
| `Booking.Booking_referral` | Tipo de referencia | L |
| `Booking.Booking_who` | Tipo de solicitante | L |
| `Booking.Checkin_price` | Precio | L |
| `Booking.Checkin_type` | Servicio check-in/check-out | L |
| `Booking.Customer_reason` | Motivo de estancia | L |
| `Building.Building` | Edificio | L |
| `Building.Building_type` | Tipo de venta | L |
| `Customer.Customer` | Cliente | L Me |
| `Customer.Customer_contact` | Contacto | L A M B |
| `Customer.Customer_contact_type` | Tipo de contacto  | L |
| `Customer.Customer_doc` | Documento de cliente | L M Me |
| `Customer.Customer_doc_option` | Opción | L |
| `Customer.Customer_doc_type` | Tipo de documento | L |
| `Customer.Customer_fav` | Favorito | L |
| `Geo.Country` | País | L |
| `Geo.District` | Barrio | L |
| `Geo.Location` | Localidad | L |
| `Provider.Provider_contract` | Plantilla de contrato | L |
| `Resource.Resource` | Recurso | L |
| `Resource.Resource_flat_type` | Tipo de piso | L |
| `Resource.Resource_place_type` | Tipo de plaza | L |

Campos que este rol puede informar o modificar (en el resto de campos de esas entidades, solo lectura):

| Entidad | Campos |
|---|---|
| `Booking.Booking` | Check in (M), Check out (M), Empresa (M), Escuela (M), Escuela (otro) (M), Fecha de estado (M), Hora de check-in (M), Hora de llegada (M), Hora de recogida (M), Id Contrato (M), Motivo de estancia (M), Opción (M), Opción (M), Search (M), Updated_at (M), Updated_by (M), Vuelo/Tren (M), Vuelo/Tren (M) |
| `Booking.Booking_option` | Search (M), Updated_at (M), Updated_by (M), ¿Aceptada? (M) |
| `Customer.Customer` | Ciudad (M), Ciudad (M), Ciudad del titular (M), Código postal (M), Código postal (M), Dirección (M), Dirección (M), Dirección del titular (M), Documento de identidad (M), Documento de identidad (M), Documento de identidad (M), Email (M), Escuela (M), Fecha de nacimiento (M), Foto (M), GDPR (M), Género (M), IBAN para domiciliación (M), IBAN/Cuenta para devolución de depósito (M), Idioma (M), Idioma preferido (M), Medio de pago (M), Misma cuenta para devolución (M), Nacionalidad (M), Nombre (M), Nombre (M), Nombre del banco (M), País (M), País (M), País de origen (M), País del titular (M), Persona/Empresa (M), Provincia (M), Provincia (M), Search (M), Swift/BIC (M), Teléfonos (M), Teléfonos (M), Tipo de documento (M), Tipo de documento (M), Tipo de documento (M), Titular (M), Updated_at (M), Updated_by (M) |

Seguridad por fila: solo ve las filas propias en `Billing.Invoice_line`, `Billing.Invoice`, `Billing.Payment`, `Booking.Booking_group_price`, `Booking.Booking_group_rooming`, `Booking.Booking_group`, `Booking.Booking_option`, `Booking.Booking_price`, `Booking.Booking`, `Customer.Customer_contact`, `Customer.Customer_doc`, `Customer.Customer_email`, `Customer.Customer`, `Resource.Resource`.

## Rol `external` — Gestores externos (sin uso)

| Entidad | Nombre en el ERP | Permisos |
|---|---|---|
| `Admin.Email` | Plantilla de email | L |
| `Admin.Email_cc` | Copiar a | L |
| `Admin.Files` | Fichero | L |
| `Admin.Log` | Log | L |
| `Admin.Notification` | Notificación | L |
| `Admin.Role` | Rol | L |
| `Admin.User` | Usuario | L |
| `Admin.User_role` | Rol | L |
| `Auxiliar.Gender` | Género | L |
| `Auxiliar.Holiday` | Festivo | L |
| `Auxiliar.Id_type` | Tipo de Id | L |
| `Auxiliar.Ipc` | IPC | L |
| `Auxiliar.Language` | Idioma | L |
| `Auxiliar.Monthname` | Mes | L |
| `Auxiliar.School` | Escuela | L |
| `Auxiliar.Segment` | Marca | L |
| `Auxiliar.Sequence` | Secuencia | L |
| `Auxiliar.Timetable` | Horario | L |
| `Batch.Upload` | Carga | L |
| `Billing.Invoice` | Factura | L |
| `Billing.Invoice_line` | Línea de factura | L |
| `Billing.Payment` | Pago | L |
| `Billing.Payment_method` | Medio de pago | L |
| `Billing.Pricing_rate` | Tarifa | L |
| `Billing.Product` | Producto | L |
| `Billing.Product_type` | Tipo de producto | L |
| `Billing.Promotion` | Promoción | L |
| `Billing.Promotion_building` | Edificio | L |
| `Billing.Tax` | Impuesto | L |
| `Billing.Tax_type` | Tipo de impuesto | L |
| `Booking.Booking` | Reserva B2C | L Me |
| `Booking.Booking_answer` | Pregunta-Respuesta | L |
| `Booking.Booking_channel` | Canal de reserva | L |
| `Booking.Booking_detail` | Reserva | L |
| `Booking.Booking_discount_type` | Tipo de descuento | L |
| `Booking.Booking_group` | Reserva B2B | L Me |
| `Booking.Booking_group_price` | Precio por plaza | L |
| `Booking.Booking_group_service` | Concepto extra | L |
| `Booking.Booking_internal_doc` | Documento | L |
| `Booking.Booking_log` | Log | L |
| `Booking.Booking_option` | Alternativa | L |
| `Booking.Booking_other_doc` | Documento | L |
| `Booking.Booking_other_resource` | Recurso adicional | L |
| `Booking.Booking_other_service` | Concepto extra | L |
| `Booking.Booking_price` | Precio | L |
| `Booking.Booking_question` | Pregunta | L |
| `Booking.Booking_question_group` | Tipo de pregunta | L |
| `Booking.Booking_questionnaire` | Cuestionario | L |
| `Booking.Booking_referral` | Tipo de referencia | L |
| `Booking.Booking_rooming` | Rooming list | L |
| `Booking.Booking_search` | Búsqueda | L |
| `Booking.Booking_service` | Concepto extra | L |
| `Booking.Booking_subtype` | Tipo de reserva LAU | L |
| `Booking.Booking_who` | Tipo de solicitante | L |
| `Booking.Checkin_price` | Precio | L |
| `Booking.Checkin_type` | Servicio check-in/check-out | L |
| `Booking.Customer_reason` | Motivo de estancia | L |
| `Building.Building` | Edificio | L |
| `Building.Building_doc` | Documento | L |
| `Building.Building_doc_type` | Tipo de documento | L |
| `Building.Building_service` | Servicio | L |
| `Building.Building_service_type` | Tipo de servicio | L |
| `Building.Building_transport` | Transporte | L |
| `Building.Building_transport_type` | Tipo de transporte | L |
| `Building.Building_type` | Tipo de venta | L |
| `Customer.Customer` | Cliente | L |
| `Customer.Customer_contact` | Contacto | L |
| `Customer.Customer_contact_type` | Tipo de contacto  | L |
| `Customer.Customer_doc` | Documento de cliente | L |
| `Customer.Customer_doc_type` | Tipo de documento | L |
| `Customer.Customer_email` | Email | L |
| `Customer.Customer_fav` | Favorito | L |
| `Customer.Customer_resident_status` | Estado de residente | L |
| `Customer.Customer_status` | Estado de cliente | L |
| `Geo.Country` | País | L |
| `Geo.District` | Barrio | L |
| `Geo.Location` | Localidad | L |
| `Geo.Location_text` | Texto | L |
| `Geo.Office` | Oficina | L |
| `Geo.Province` | Provincia | L |
| `Provider.Agent` | Marketplace | L |
| `Provider.Agent_bills` | Factura | L |
| `Provider.Agent_type` | Tipo de marketplace | L |
| `Provider.Provider` | Propietario | L |
| `Provider.Provider_bill` | Numero de factura | L |
| `Provider.Provider_contact` | Contacto | L |
| `Provider.Provider_contact_type` | Tipo de contacto  | L |
| `Provider.Provider_contract` | Plantilla de contrato | L |
| `Provider.Provider_doc` | Documento | L |
| `Provider.Provider_doc_type` | Tipo de documento | L |
| `Provider.Provider_template` | Plantilla de contrato | L |
| `Provider.Provider_type` | Tipo de proveedor | L |
| `Resource.Resource` | Recurso | L |
| `Resource.Resource_amenity` | Característica | L |
| `Resource.Resource_amenity_type` | Tipo de característica | L |
| `Resource.Resource_availability` | Estado | L |
| `Resource.Resource_doc` | Documento | L |
| `Resource.Resource_doc_type` | Tipo de documento | L |
| `Resource.Resource_flat_amenity` | Característica | L |
| `Resource.Resource_flat_subtype` | Subtipo de piso | L |
| `Resource.Resource_flat_type` | Tipo de piso | L |
| `Resource.Resource_inventory` | Inventario | L |
| `Resource.Resource_inventory_type` | Tipo de inventario | L |
| `Resource.Resource_inventory_zone` | Zona de inventario | L |
| `Resource.Resource_place_text` | Texto | L |
| `Resource.Resource_place_type` | Tipo de plaza | L |
| `Resource.Resource_price` | Precio | L |
| `Resource.Resource_status` | Estado | L |
| `Resource.Resource_usage` | Tipo de uso | L |
| `Resource.Resource_value` | Valoración | L |

Seguridad por fila: ve todas las filas.
