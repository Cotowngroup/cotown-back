# IT-11. Usuarios, roles y permisos

> Manual técnico · Borrador v0.1 · 2026-10-20 · Las marcas **[PREGUNTA Tn]** se resuelven en la ronda de preguntas y desaparecen de la versión final.

## 11.1 Propósito

Este capítulo explica quién accede al sistema, con qué tipo de usuario y qué puede ver o hacer cada uno: el personal de Cotown, los propietarios, los residentes y los usuarios técnicos que usan los procesos para comunicarse entre sí.

## 11.2 Modelo de seguridad

La seguridad del sistema se apoya en Airflows y en PostgreSQL:

1. **Cada persona tiene un usuario de Airflows** y, ligado a él, un **rol de PostgreSQL con su mismo nombre**. Todo lo que hace en el ERP, en el backoffice complementario o en el portal se ejecuta con ese rol.
2. **Roles base**: cada usuario recibe uno según su tipo (personal, propietario o cliente), que fija a qué tablas puede acceder.
3. **Roles funcionales**: el personal recibe además roles que fijan qué menús y acciones tiene en el ERP.
4. **Seguridad por fila**: en las tablas con datos de propietarios y clientes, PostgreSQL filtra las filas según el rol: el personal ve todas; un propietario o un cliente solo ve las suyas.

## 11.3 Tipos de usuario

| Tipo | Nombre de usuario | Rol base | Cómo se crea | Dónde entra |
|---|---|---|---|---|
| **Personal de Cotown** | `X` + número (6 dígitos) | `cotown` | Al dar de alta a la persona en *Administración › Usuarios* | ERP (Airflows) y backoffice complementario |
| **Propietario** | `P` + número | `provider` | Al dar de alta el propietario | ERP (Airflows), con acceso de consulta a lo suyo e informes propios |
| **Cliente (residente)** | `C` + número | `customer` | Al marcar *Crear usuario* en su ficha, o al registrarse en la web de reserva. Recibe el email de bienvenida. | Portal del residente (y asistente de reserva) |
| **Gestor externo** | — | `external` | Rol previsto para gestores externos; hoy sin uso | — |

Al borrar una persona, un propietario o un cliente, se borran también su usuario y su rol. Si cambia el email de un cliente o de un propietario, se actualiza el de su usuario.

Los usuarios inician sesión con su email (o nombre de usuario) y su contraseña de Airflows. El portal del residente lo hace a través de Keycloak, que valida contra los mismos usuarios (ver *Integraciones*).

## 11.4 Perfiles y roles

Todo el personal tiene el rol base `cotown`, que permite **consultar todo el ERP** y acceder a la pantalla de informes. Los roles funcionales, que se asignan en *Administración › Usuarios › Roles*, añaden la capacidad de **dar de alta, modificar y borrar** en las áreas de cada equipo y el acceso a sus pantallas del backoffice complementario. Una persona puede tener varios roles; sus permisos son la suma de todos ellos.

| Perfil | Rol | Usuarios | Puede modificar | Pantallas del backoffice |
|---|---|---|---|---|
| Administración del sistema | `administrators` | 24 | Todo el ERP | Planning y todos los dashboards |
| Reservas | `bookings` | 15 | Clientes, reservas, facturación, catálogos auxiliares; algunos campos de activos | Planning y todos los dashboards |
| Operaciones | `operations` | 13 | Reservas y activos; altas de clientes y cargas de Excel | Planning, dashboards general, de operaciones y de documentos |
| Facturación | `billing` | 5 | Facturación, propietarios, catálogos y administración; algunos campos de clientes | Dashboards de administración y LAU |
| Vandor | `vandor` | 12 | Contratos LAU y otros, clientes, facturación, propietarios | Dashboard LAU |
| Marketing | `marketing` | 4 | Contenidos web, ubicaciones, edificios, activos, precios y promociones | — |
| Propietario | `provider` | 13 | Solo sus contactos; consulta lo suyo | Informes (los suyos) |
| Cliente | `customer` | 4.716 | Sus datos, contactos, documentos y alternativas, desde el portal | — (usa el portal) |
| Gestor externo | `external` | 3 | Nada (solo consulta); previsto para gestores externos, sin uso | — |

Además, en reservas, operaciones y administración hay restricciones por campo: dentro de una tabla, cada rol solo puede informar o modificar los campos que le corresponden.

El detalle completo, tabla a tabla y campo a campo, está en el *Anexo. Permisos por rol*, generado a partir de la configuración de Airflows.

## 11.5 Seguridad por fila

Las tablas con datos de propietarios y clientes tienen políticas por rol. Por ejemplo, en *Propietarios*:

| Rol | Ve |
|---|---|
| Personal (`cotown`), administración y externos | Todas las filas. |
| Propietario | Solo su propia ficha. |

Del mismo modo, un cliente solo ve en el portal su ficha, sus contactos, sus documentos, sus reservas, sus facturas y sus cobros; y un propietario, en el ERP y en los informes, solo lo que le corresponde. Por eso los informes del backoffice complementario muestran a un propietario solo sus datos sin que la aplicación tenga que filtrarlos.

## 11.6 Usuarios técnicos

| Usuario | Lo usa | Para qué |
|---|---|---|
| Usuario de servicio de Airflows | Servicio de integración, procesos automáticos, ETL y generador de webs | Llamadas GraphQL y descarga y subida de documentos. |
| Usuario de base de datos del servicio | Servicio de integración, procesos automáticos y ETL | Consultas SQL directas a la base de datos de Airflows (dashboards, informes, facturación, carga del data warehouse), a través de un túnel SSH. |
| Usuario SSH `partner` | Servidor de servicios y data warehouse | Túnel SSH hacia la base de datos de Airflows. |
| Usuario `readonly` | Consultas puntuales de Oimbra | Lectura de metadatos de Airflows. |
| Usuario del data warehouse | ETL y Power BI | Escritura y lectura del esquema `gold`. |
| Claves de la API contable | SAP y propietarios | Consulta de clientes, facturas, cobros y management fees, limitada por emisor. |
| Credenciales de servicios externos | Servicio de integración | Redsys (por terminal), DocuSign, Microsoft 365, Pipedrive, SAP. |

Todas las credenciales están en la configuración de cada componente; no se reproducen en este documento.

## 11.7 Acceso a los servidores

| Servidor | Acceso |
|---|---|
| `core.cotown.com` (Airflows) | Proveedor de Airflows; Oimbra, con un usuario limitado para el túnel a la base de datos. |
| `back.cotown.com` | Oimbra, por SSH con clave. |
| `data.cotown.com` | Oimbra, por SSH con clave, en un puerto no estándar. |
| Grafana | Usuarios de Grafana, en `back.cotown.com/grafana`. |

## 11.8 Fuentes

| Tema | Dónde está |
|---|---|
| Alta y baja de usuarios | `back/function/Admin.User_*`, `Customer.Customer_A1_create_user`, `Provider.Provider_A1_create_user` y sus `D1` |
| Roles funcionales | `back/function/Admin.User_role_*`; catálogo en *Administración › Roles* |
| Permisos por rol y seguridad por fila | Configuración de Airflows (esquema `Models`: `Role`, `EntityPermission`, `EntityAttributePermission`, `ExternalEntityPermission`, `RowLevelPermission`) |

## 11.9 Pendiente de confirmar

No hay puntos pendientes.
