# IT-9. Integraciones

> Manual técnico · Borrador v0.1 · 2026-10-20 · Las marcas **[PREGUNTA Tn]** se resuelven en la ronda de preguntas y desaparecen de la versión final.

## 9.1 Propósito

Este capítulo reúne, sistema a sistema, cómo se integra Cotown con cada servicio externo: qué se intercambia, en qué sentido, qué lo dispara, dónde se configura, qué pasa si falla y dónde mirar. Complementa el inventario de *Visión general* (sección *Sistemas externos*) y los capítulos *Servicio de integración* y *Procesos automáticos*, donde están los flujos con detalle.

Las credenciales de todas las integraciones están en la configuración del servicio de integración (ficheros de configuración por entorno del contenedor `back`) y en la del data warehouse; no se reproducen en este documento.

## 9.2 Resumen

| Sistema | Sentido | Disparador | Componente |
|---|---|---|---|
| Redsys | Salida y entrada | El residente paga; Redsys notifica | Servicio de integración |
| DocuSign | Salida y entrada | Proceso de contratos; DocuSign notifica; comprobación diaria | Procesos automáticos y servicio de integración |
| Microsoft 365 – correo | Salida | Emails automáticos, facturas, avisos internos | Servicio de integración y procesos |
| Microsoft 365 – SharePoint | Salida | Diario, 02:00–02:30 | Proceso de archivo + `rclone` |
| Pipedrive | Salida | Formularios web y reservas web | Servicio de integración |
| SAP Business ByDesign | Entrada (SAP consulta) | Diario, programado por el equipo de SAP de Cotown | Servicio de integración |
| SAP Business ByDesign (libro mayor) | Salida (lectura) | ETL (desactivado temporalmente) | Data warehouse |
| Marketplaces (iCal) | Entrada (consultan) | Cada marketplace, según su propia programación | Servicio de integración |
| Keycloak | — | Inicio de sesión del portal | Airflows (conector propio con sus usuarios) |
| Power BI | Entrada (consulta) | Actualización de los informes | Data warehouse (puerta de enlace) |
| INCASÒL | Ninguna (ficheros) | El personal descarga y presenta | Backoffice complementario |
| Trustpilot | Enlace | Email automático 30 días antes de la salida | Proceso programado de Airflows |

## 9.3 Redsys (pago con tarjeta)

| Aspecto | Detalle |
|---|---|
| Qué intercambia | El servicio prepara una orden de pago firmada (importe, pedido, terminal, URL de vuelta) y Redsys devuelve el resultado: autorizado o denegado, con código de autorización. |
| Terminales | Cuatro: *cotown* (membership fee, check-in, check-out), *vandor* (contratos LAU), *delegado* (cobros que reúnen renta y servicios de emisores distintos) y uno por defecto. Cada uno con su número de comercio, terminal y clave, en la configuración (`REDSYS_*`). El terminal de cada cobro lo fija Airflows. |
| Entornos | Producción contra `sis.redsys.es`; desarrollo contra el entorno de pruebas `sis-t.redsys.es`. |
| Seguridad | Firma HMAC-SHA256 en ambos sentidos; la notificación se rechaza si la firma no es válida. |
| Si falla | Si Redsys no puede notificar, reintenta; el cobro queda pendiente hasta recibir la notificación. Si el pago se deniega, el cobro sigue pendiente y el residente puede volver a intentarlo desde el portal. Una notificación repetida no tiene efecto. |
| Dónde mirar | Log del servicio de integración (mensajes de pago con identificador y pedido); en Airflows, el cobro (*Facturación › Pagos*: pedido, autorización, fecha de pago); en el portal de comercio de Redsys, la operación por número de pedido. |

## 9.4 DocuSign (firma de contratos)

| Aspecto | Detalle |
|---|---|
| Qué intercambia | El proceso de contratos envía un sobre con el PDF (contrato de renta y, si hay, de servicios o anexo) y un firmante: el residente, el pagador del grupo o el firmante del anexo. DocuSign notifica los cambios de estado. |
| Cuenta | Cuenta europea de DocuSign; el servicio se autentica con JWT en nombre de un usuario de la cuenta. Clave e identificadores en la configuración. Solo se envía si el edificio tiene *contrato digital* y si el envío está activado en la configuración (`DOCUSIGNSEND`). |
| Entrada | Notificaciones de DocuSign Connect en `POST /api/v1/contract` (actualiza el estado del contrato B2C). Además, cada noche a la 01:00 se consulta el estado de todos los sobres pendientes, incluidos grupos y anexos. |
| Estados | Enviado, entregado, firmado (*completed*), rechazado, caducado, anulado. Al firmarse, la reserva pasa a *contrato*. |
| Si falla | Si el envío falla, el contrato queda generado pero sin enviar y hay que revisarlo a mano. Si se pierde una notificación, la comprobación nocturna actualiza el estado. |
| Dónde mirar | `batch_printcontract.log`; en Airflows, los campos de contrato de la reserva (identificador del sobre, estado, fecha); en la consola de DocuSign, el sobre por su identificador. |

## 9.5 Microsoft 365

**Correo.** Envío de todos los emails automáticos por SMTP (`smtp.office365.com`, puerto 587 con STARTTLS), con dos cuentas remitentes: Cotown (`no-reply@cotown.com`) y Vandor (`no-reply@vandor.es`). El envío se puede desactivar por configuración (`SMTPSEND`), como en desarrollo. Si un envío falla, el email queda pendiente y se reintenta cada 15 minutos (ver *Procesos automáticos*). Dónde mirar: `batch_sendemail.log`, la salida del contenedor `back` y, en Airflows, los emails del cliente (*fecha de envío*).

**SharePoint.** Cada noche se copia el archivo de facturas y recibos a la biblioteca de documentos *DOC ACTUALIZADA*, carpeta *Departments/Financial/Documentación venta activos*, con `rclone` (conexión de tipo OneDrive/SharePoint configurada en el servidor de servicios). Si falla, la siguiente noche vuelve a copiar lo pendiente (el archivo incluye los dos últimos días). Dónde mirar: `batch_sharepoint.log` y `sharepoint.log`.

## 9.6 Pipedrive (CRM)

| Aspecto | Detalle |
|---|---|
| Qué envía | Por cada formulario de la web (contacto, visita, disponibilidad, reserva ahora), conversación del chatbot o solicitud de reserva web: crea o actualiza la **persona** (por email), crea un **lead** con sus datos comerciales y una **oportunidad** (*deal*) en el embudo de reservas, en la etapa *Lead entrante* o *Reserva pendiente* (si viene de una solicitud de reserva). Adjunta el fichero del formulario si lo hay. |
| Datos | Persona: nombre, email, teléfono, género, idioma, fecha de nacimiento, nacionalidad, comentarios. Lead: tipo (B2C/B2B), canal y subcanal, marca, web, formulario, motivo, edificio, ciudad, tipología, presupuesto máximo, fechas y parámetros de campaña (UTM, `gclid`). |
| Correspondencias | Los valores de lista de Pipedrive (edificios, ciudades, tipologías, formularios, canales, marcas) están definidos en el código del servicio (`library/services/pipedrive.py`). Un edificio, ciudad o tipología nuevos deben añadirse ahí para llegar al CRM: al abrirlos, Cotown crea la opción en Pipedrive y pide a Oimbra que actualice la integración. |
| Además | Cada lead genera un email de aviso al equipo comercial (`book@cotown.com`). Envío y aviso se pueden desactivar por configuración (`CRMSEND`, `CRMEMAIL`). |
| Si falla | El formulario o la reserva se registran igualmente en el sistema; el error queda en el log del servicio de integración. |

## 9.7 SAP Business ByDesign (contabilidad)

**De Cotown a SAP.** SAP consulta la API de integración contable (ver *Servicio de integración*): clientes, facturas, cobros y management fees, con una clave de acceso. Las correspondencias contables se mantienen en Airflows: código SAP del proveedor (emisor), del producto, del recurso (proyecto) y del medio de pago; las cuentas de cobro de cada terminal, en los parámetros (`TPV_<TERMINAL>`). Solo se envían los emisores, productos y medios de pago marcados para SAP. SAP consulta la API cada día; esa consulta la programa y mantiene el equipo de SAP de Cotown.

**De SAP al data warehouse.** Lectura del libro mayor por OData para la analítica contable; desactivada temporalmente (ver *Data warehouse*).

## 9.8 Marketplaces (calendarios iCal)

Cada recurso publica un calendario en `https://back.cotown.com/api/v1/ical/<token>`, cuya URL figura en la ficha del recurso en Airflows (*Ical*). El marketplace (Airbnb y otros) la consulta periódicamente para bloquear las fechas ocupadas. Incluye las reservas futuras del recurso y, a partir del viernes a las 10:00, los días libres del fin de semana en curso. Las reservas que traen los marketplaces se registran a mano en Airflows, indicando el marketplace; su comisión se refleja en el management fee y en sus facturas (*Propietarios › Marketplaces*).

## 9.9 Keycloak (inicio de sesión del portal)

Keycloak forma parte de Airflows (`core.cotown.com/auth`, *realm* `airflows`). No tiene usuarios propios: un conector propio (*User Storage SPI*) valida email y contraseña contra los usuarios de Airflows. El portal del residente usa el cliente `airflows-private`. El código del conector y el tema visual de las pantallas de inicio de sesión están en `misc/core/keycloak`.

## 9.10 Power BI

El servicio de Power BI en la nube lee el data warehouse de `data.cotown.com` a través de una puerta de enlace de datos (ver *Data warehouse*).

## 9.11 INCASÒL

No hay conexión automática. El sistema calcula en cada reserva de Barcelona la fianza legal que debe depositarse y sigue su situación (pendiente, depositada, reclamada, devuelta). El personal presenta los depósitos y devoluciones con la información del sistema:

- *Dashboards › Administración › INCASÒL*: fianzas pendientes, reclamadas o por devolver.
- *Informes › INCASÒL*: altas y bajas de fianzas en un periodo.
- *Informes › Declaraciones INCASÒL*: ZIP con la declaración responsable de devolución de fianza de cada reserva, en PDF y en catalán.

## 9.12 Trustpilot

Sin integración técnica: el sistema envía al residente el email *trustpilot*, con el enlace de invitación a dejar una reseña, 30 días antes de la salida. Las reseñas se muestran en las webs con el widget de Trustindex.

## 9.13 Fuentes

| Integración | Código |
|---|---|
| Redsys | `back/app/library/services/redsys.py`, `back/app/library/api/payment.py` |
| DocuSign | `back/app/library/business/contract.py`, `back/app/library/api/contract.py`, `back/app/batch_checkcontract.py` |
| Correo | `back/app/library/business/send_email.py` |
| SharePoint | `back/app/batch_sharepoint.py`; `rclone` en el `crontab` del servidor |
| Pipedrive | `back/app/library/services/pipedrive.py` |
| SAP | `back/app/library/api/integration.py`, `back/app/library/business/integration.py`; `back/etl/library/business/gl.py` |
| iCal | `back/app/library/api/misc.py`; URL generada en `back/function/Resource.Resource_B1_flat_data.sql` |
| Keycloak | `misc/core/keycloak/` |

## 9.14 Pendiente de confirmar

No hay puntos pendientes.
