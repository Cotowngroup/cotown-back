# OP-10. Propietarios

> Manual funcional · Borrador v0.1 · 2026-10-21 · Las marcas **[PREGUNTA On]** se resuelven en la ronda de preguntas y desaparecen de la versión final.

## 10.1 Propósito

Este capítulo explica cómo se da de alta y se mantiene un **proveedor** (propietario o empresa de servicios) para que el sistema pueda emitir sus contratos, facturas y cobros, y qué puede consultar el propio proveedor en el sistema.

## 10.2 Conceptos

| Concepto | Qué es |
|---|---|
| **Proveedor** | Propietario, empresa de servicios u otro emisor. Cotown también es un proveedor: el que emite el membership fee, los servicios de check-in/out y otros servicios propios. |
| **Propietario** | Dueño de los pisos. Es el arrendador en los contratos de renta y emite las facturas o recibos de renta y los recibos de garantía. |
| **Empresa de servicios** | Prestador de los servicios del piso (limpieza, suministros, atención). Firma el contrato de servicios y emite sus facturas. |
| **Apoderado** | Contacto del proveedor que firma los contratos en su nombre; su firma escaneada se incrusta en ellos. |
| **Patrones de numeración** | Formato de los números de factura, recibo y rectificativa del proveedor (y sus variantes LAU), con el año y un correlativo de 5 dígitos. |
| **Usuario de proveedor** | Acceso del proveedor a Airflows para consultar sus datos y descargar sus informes. |

## 10.3 Tareas

### Dar de alta un proveedor

**Qué informar**:

- **Tipo de proveedor** (propietario, empresa de servicios u otro), **persona o empresa**, documento de identidad, nombre, email, teléfonos y dirección.
- **Facturación**:
  - **Emite recibo, no factura**, si el propietario no emite factura por la renta.
  - **Patrones de numeración** de facturas, rectificativas y recibos, y de facturas y rectificativas LAU. Sin patrón, el documento se emite **sin número**.
  - **Texto al pie** de factura (aparece también en los contratos).
  - **Terminal de pago (TPV)**: *Cotown*, *Vandor* o *delegado*. Es el terminal por el que se cobran con tarjeta sus rentas y garantías.
  - **IBAN** y **código SAP** (para la contabilidad).
- **Contactos**: al menos un **apoderado** con su documento y su **firma** escaneada. Otros contactos: administración, mantenimiento, limpieza, administración de fincas, emergencias.
- **Documentos**: contrato de gestión, *Property Management Agreement*, acuerdo de management fee, refacturaciones, certificado de titularidad bancaria, certificado de gran tenedor, contrato.
- **Plantillas de contrato** asignadas por tipo de reserva y ciudad (ver *Contratos, garantías e INCASÒL*).

**Qué hace el sistema**: crea su **usuario** de acceso (`P` + número) con el rol de proveedor, que solo le deja ver lo suyo. Si cambia su email, actualiza el de su usuario.

**Después**: asignarlo como **propietario** o **empresa de servicios** en los pisos que le correspondan (ver *Inventario y precios*). Las habitaciones y plazas lo heredan del piso.

**Comprobar** antes de que tenga reservas:

- Patrones de numeración completos.
- Apoderado con firma.
- Plantillas activas para todos los tipos de reserva que va a tener.
- Terminal de pago y, si se usa Redsys con un terminal propio, que esté configurado.
- Código SAP, si sus facturas deben llegar a la contabilidad.

### Mantener los management fees del propietario

Los porcentajes de management fee no están en el proveedor sino en cada **piso**: sin servicios, servicio premium (semanal), estándar (quincenal), mensual, marketplace y 0 %. El sistema los aplica a cada línea de sus facturas (ver *Facturación y cobros*). El acuerdo firmado con el propietario se guarda en sus documentos.

### Dar acceso a un propietario

El propietario entra en Airflows con su usuario. Ve solo sus datos: su ficha y contactos, sus pisos, las reservas, facturas y cobros que le corresponden. Desde *Procesos › Informes* puede descargar:

| Informe | Contenido |
|---|---|
| **Ingresos** | Sus ingresos en un periodo. |
| **Management fee** | El management fee de sus facturas en un periodo. |
| **Contratos** | ZIP con los contratos de sus reservas. |
| **Facturas y recibos** | ZIP con sus facturas y recibos de un mes. |

**Contraseña**: el propietario la crea o la recupera con el enlace *¿Has olvidado tu contraseña?* del inicio de sesión, que le envía un email. Es la forma de darle acceso tras el alta. Los propietarios usan este acceso para consultar y descargar su información.

### Integración contable de un propietario

Un propietario que lo pida puede recibir una **clave de la API contable**, limitada a sus facturas y clientes, para descargarlos desde su propio sistema. La clave la configura Oimbra.

### Cambiar datos de un proveedor

- Los cambios de dirección, documento o patrones afectan a los documentos que se emitan a partir de ese momento; los ya emitidos no cambian.
- Un cambio de apoderado o de firma afecta a los contratos que se generen después. Para aplicarlo a un contrato pendiente de firma, regenerarlo.
- Si cambia el email, se actualiza el de su usuario.

## 10.4 Automático y manual

| Qué | A / M |
|---|---|
| Alta y mantenimiento del proveedor, contactos, documentos y plantillas | M |
| Creación y sincronización de su usuario | A |
| Asignación a pisos y management fees por piso | M |
| Numeración de sus documentos | A |
| Informes y descargas del propietario | Propietario |
| Clave de la API contable | M (Oimbra) |

## 10.5 Excepciones

| Situación | Qué pasa | Qué hacer |
|---|---|---|
| No se generan los contratos de un propietario | Falta su plantilla para ese tipo y ciudad, o el apoderado. | Completar plantillas y apoderado. |
| Una factura o recibo de un proveedor sale sin número | Falta el patrón de numeración de ese tipo de documento. | Completar el patrón y rectificar el documento. |
| Las facturas del proveedor no llegan a SAP | Falta su código SAP o no está marcado para SAP. | Completarlo. |

## 10.6 Fuentes

| Tema | Dónde está |
|---|---|
| Usuario del proveedor y seguridad | Reglas de la base de datos de los proveedores; roles de Airflows |
| Numeración | Reglas de la base de datos de las facturas |
| Plantillas y firmas | Proceso automático de contratos |
| Informes del propietario | Backoffice complementario |
| API contable | Servicio de integración |

## 10.7 Pendiente de confirmar

| Tema | Quién o qué lo confirma |
|---|---|
| — | — |
