"""
Builds the credentials inventory (Word): every production credential of the system, where it is configured, who
manages it and how to rotate it. It contains no values, only the names of the parameters and files that hold them,
so it needs no copy of the production configuration.
Usage (from knowledge/): python scripts/gen_secretos.py <version> <date AAAA-MM-DD>
Output: salida/Cotown - Inventario de credenciales v<version>.docx (then run scripts/update_docx.ps1)
"""
import os, sys, tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gen_docx  # noqa: E402


def v(x):
  return f'`{x}`'


md = []
w = md.append


def cred(title, purpose, where, items, owner, rotate):
  w(f'### {title}')
  w('')
  w(purpose)
  w('')
  for label, value in items:
    w(f'- **{label}**: {value}')
  w(f'- **Dónde se configura**: {where}')
  w(f'- **Gestiona**: {owner}')
  w(f'- **Cómo se cambia**: {rotate}')
  w('')


w('# Inventario de credenciales')
w('')
w('**Documento confidencial.** Lista las credenciales de producción del sistema de Cotown, dónde se configuran, quién '
  'las gestiona y cómo se cambian. **No contiene sus valores**: cada credencial se identifica por el nombre del parámetro '
  'o del fichero que la guarda en los servidores, y los valores deben custodiarse en un gestor de contraseñas. Al añadir, '
  'mover o retirar una credencial hay que actualizar este inventario.')
w('')
w('Las credenciales de los entornos de desarrollo no se incluyen. Las rutas de ficheros se refieren a los servidores '
  'descritos en el *Manual técnico*, capítulo *Instalación*.')
w('')

w('## Acceso a los servidores')
w('')
cred('Servidor de servicios (`back.cotown.com`)', 'Acceso SSH de administración.',
     'Clave pública en `~/.ssh/authorized_keys` del usuario `cotown`.',
     [('Usuario', v('cotown')), ('Puerto', v('22')), ('Clave privada', 'Fichero `cotown.key.pem`, en los puestos de los administradores')],
     'Oimbra', 'Generar un nuevo par de claves, añadir la pública al servidor y retirar la anterior.')
cred('Servidor del data warehouse (`data.cotown.com`)', 'Acceso SSH de administración.',
     'Clave pública en `~/.ssh/authorized_keys` del usuario `cotown`.',
     [('Usuario', v('cotown')), ('Puerto', v('23141')), ('Clave privada', 'Fichero `cotown.key.pem`, en los puestos de los administradores')],
     'Oimbra', 'Igual que el anterior.')
cred('Túnel SSH hacia la base de datos de Airflows (`core.cotown.com`)',
     'Usuario limitado del servidor de Airflows que solo se usa para abrir el túnel hacia la base de datos `niledb` '
     'desde el servicio de integración, los procesos y el ETL.',
     '`~/app/.settings.toml` (`SSHUSER`) y `~/app/.secrets.toml` (`SSHPKEY`, nombre del fichero de clave) en `back.cotown.com`; '
     '`~/etl/.settings.toml` y `.secrets.toml` en `data.cotown.com`.',
     [('Usuario', v('SSHUSER')), ('Clave privada (servicio)', 'Fichero `~/app/id_partner.pem`'),
      ('Clave privada (ETL)', 'Fichero `~/etl/airflows.key.pem` (la misma clave)')],
     'Proveedor de Airflows (servidor) y Oimbra (claves)', 'Pedir al proveedor de Airflows que sustituya la clave pública autorizada.')

w('## Bases de datos')
w('')
cred('Base de datos de Airflows (`niledb`)',
     'Usuario con el que el servicio de integración, los procesos automáticos y el ETL hacen consultas SQL directas, a través del túnel SSH.',
     '`DATABASE`, `DBUSER` y `DBPASS` en `~/app/.settings.toml` / `.secrets.toml`; `DBHOST`, `DBNAME`, `DBUSER` y `DBPASS` en `~/etl/`.',
     [('Base de datos', v('DATABASE')), ('Usuario', v('DBUSER')), ('Contraseña (servicio)', v('DBPASS')),
      ('Usuario (ETL)', v('DBUSER')), ('Contraseña (ETL)', v('DBPASS'))],
     'Proveedor de Airflows', 'Cambiar la contraseña en PostgreSQL y actualizar los dos ficheros; reiniciar el contenedor `back`.')
cred('Base de datos de Airflows – usuario de consulta',
     'Usuario de solo lectura para consultas de metadatos y comprobaciones.', 'Rol de PostgreSQL en `niledb`.',
     [('Usuario', v('readonly')), ('Contraseña', 'No está en ningún fichero')],
     'Proveedor de Airflows / Oimbra', 'Cambiar la contraseña del rol en PostgreSQL.')
cred('Data warehouse (`dw`)',
     'Usuario del ETL y de la puerta de enlace de Power BI.',
     '`DWDBHOST`, `DWDBNAME`, `DWDBUSER` y `DWDBPASS` en `~/etl/` de `data.cotown.com`; conexión de la puerta de enlace en Power BI.',
     [('Servidor', v('data.cotown.com:5432 (SSL)')), ('Base de datos', v('DWDBNAME')), ('Usuario', v('DWDBUSER')),
      ('Contraseña', v('DWDBPASS'))],
     'Oimbra', 'Cambiar la contraseña en PostgreSQL, en `~/etl/.secrets.toml` y en la conexión de la puerta de enlace de Power BI.')

w('## Airflows')
w('')
cred('Usuario de servicio de Airflows',
     'Usuario con el que el servicio de integración, los procesos, el ETL y el generador de las webs llaman a la API GraphQL y a la API de ficheros.',
     '`GQLUSER` / `GQLPASS` en `~/app/` y `~/etl/`; en las webs, `webs/code/src/data/constants.js`.',
     [('Usuario', v('GQLUSER')), ('Contraseña (servicio)', v('GQLPASS')), ('Contraseña (ETL)', v('GQLPASS')),
      ('Usuario y contraseña (webs)', 'Llamada `login(username, password)` de `constants.js`')],
     'Oimbra', 'Cambiar la contraseña del usuario en Airflows y actualizar los tres sitios.')

w('## Pagos (Redsys)')
w('')
for pos in ('COTOWN', 'VANDOR', 'DELEGADO', 'DEFAULT'):
  cred(f'Terminal {pos.lower()}', 'Terminal de pago con tarjeta (ver *Integraciones*).',
       f'`REDSYS_MERCHANTCODE_{pos}`, `REDSYS_TERMINAL_{pos}` en `~/app/.settings.toml`; `REDSYS_KEY_{pos}` en `~/app/.secrets.toml`.',
       [('Código de comercio', v(f'REDSYS_MERCHANTCODE_{pos}')), ('Terminal', v(f'REDSYS_TERMINAL_{pos}')),
        ('Clave de firma (SHA-256)', v(f'REDSYS_KEY_{pos}'))],
       'Cotown (contrato con la entidad bancaria)', 'Generar una nueva clave en el portal de Redsys, actualizarla y reiniciar el contenedor `back`.')
w('Pasarela y URL de notificación: `REDSYS_URL` y `REDSYS_MERCHANTURL` en `~/app/.settings.toml`.')
w('')

w('## Firma electrónica (DocuSign)')
w('')
cred('Integración con DocuSign',
     'Aplicación de DocuSign con la que el sistema envía los contratos, autenticándose con JWT en nombre de un usuario de la cuenta.',
     '`AUTHORIZATION_SERVER`, `ACCOUNT_BASE_URI`, `SCOPES` en `~/app/.settings.toml`; `INTEGRATION_KEY`, `IMPERSONATED_USER_ID`, '
     '`API_ACCOUNT_ID` y `RSA_KEY` en `.secrets.toml`; clave privada en `~/app/docusign.private.key`.',
     [('Servidor de autenticación', v('AUTHORIZATION_SERVER')), ('URI de la cuenta', v('ACCOUNT_BASE_URI')),
      ('Clave de integración', v('INTEGRATION_KEY')), ('Usuario suplantado', v('IMPERSONATED_USER_ID')),
      ('Cuenta', v('API_ACCOUNT_ID')), ('Identificador de la clave RSA', v('RSA_KEY')),
      ('Clave privada', 'Fichero `~/app/docusign.private.key`')],
     'Cotown (cuenta de DocuSign) y Oimbra (integración)', 'Generar un nuevo par RSA en la aplicación de DocuSign, sustituir la clave privada y su identificador.')

w('## Correo (Microsoft 365)')
w('')
cred('Cuenta de envío de Cotown', 'Envío de los emails automáticos con remitente Cotown.',
     '`SMTPHOST`, `SMTPPORT`, `SMTPUSER`, `SMTPFROM` en `~/app/.settings.toml`; `SMTPPASS` en `.secrets.toml`.',
     [('Servidor', f"{v('SMTPHOST')}:{v('SMTPPORT')}"), ('Usuario', v('SMTPUSER')),
      ('Remitente', v('SMTPFROM')), ('Contraseña', v('SMTPPASS'))],
     'IT de Cotown', 'Cambiar la contraseña en Microsoft 365, actualizarla y reiniciar el contenedor `back`.')
cred('Cuenta de envío de Vandor', 'Envío de los emails con remitente Vandor (contratos LAU).',
     '`SMTPUSERVANDOR`, `SMTPFROMVANDOR` en `~/app/.settings.toml`; `SMTPPASSVANDOR` en `.secrets.toml`.',
     [('Usuario', v('SMTPUSERVANDOR')), ('Remitente', v('SMTPFROMVANDOR')), ('Contraseña', v('SMTPPASSVANDOR'))],
     'IT de Cotown', 'Igual que la anterior.')

w('## CRM (Pipedrive)')
w('')
cred('API de Pipedrive', 'Alta de personas, leads y oportunidades desde la web.',
     '`CRM_URL` en `~/app/.settings.toml`; `CRM_KEY` en `.secrets.toml`.',
     [('URL', v('CRM_URL')), ('Token de API', v('CRM_KEY'))],
     'Cotown (cuenta de Pipedrive)', 'Regenerar el token en Pipedrive y actualizarlo.')

w('## Contabilidad (SAP)')
w('')
cred('Claves de la API contable', 'Claves con las que SAP y algunos propietarios consultan la API de integración contable (cabecera `Api-Key`).',
     'Nombres de clave en `~/app/.secrets.toml` (el nombre es la clave; el valor, el rango de emisores autorizado).',
     [('SAP / Vandor (acceso completo)', 'Clave con el rango `0:9999`'), ('Lemos (propietario con id 5)', 'Clave con el rango `5:5`')],
     'Oimbra', 'Añadir una clave nueva con el mismo rango, comunicarla al consumidor y borrar la anterior.')
cred('Usuario de SAP Business ByDesign', 'Lectura del libro mayor por OData desde el ETL (hoy desactivada).',
     '`SAPUSER` y `SAPURL_GL` en `~/etl/.settings.toml`; `SAPPASS` en `.secrets.toml`.',
     [('URL', v('SAPURL_GL')), ('Usuario', v('SAPUSER')), ('Contraseña', v('SAPPASS'))],
     'Equipo de SAP de Cotown', 'Cambiar la contraseña en SAP y actualizarla.')

w('## Otras')
w('')
cred('Clave de sesión del asistente de reserva', 'Firma las cookies de sesión del asistente de reserva web.',
     '`COOKIE_KEY` en `~/app/.secrets.toml`.', [('Valor', v('COOKIE_KEY'))],
     'Oimbra', 'Generar un valor aleatorio nuevo (cierra las sesiones en curso).')
cred('ActiveCampaign (sin uso)', 'Antiguo CRM de marketing. La integración ya no se usa.',
     '`AC_KEY` en `~/app/.secrets.toml`.', [('Valor', v('AC_KEY'))],
     '—', 'Revocar en ActiveCampaign y retirar de la configuración.')

def cycle(title, generate, places, after, check):
  w(f'### {title}')
  w('')
  w(f'- **Nueva credencial**: {generate}')
  w('- **Dónde hay que colocarla**:')
  for p in places:
    w(f'  - {p}')
  w(f'- **Después**: {after}')
  w(f'- **Comprobación**: {check}')
  w('')


RESTART = '`docker restart back` en `back.cotown.com`; los procesos programados leen la configuración en cada ejecución'
w('## Ciclado de claves')
w('')
w('Procedimiento para sustituir cada credencial y lista de **todos los sitios** donde hay que volver a colocarla. '
  'Reglas generales:')
w('')
w('- **Primero añadir, después retirar.** Colocar la credencial nueva en todos los sitios, comprobar que funciona y solo '
  'entonces revocar la anterior. En las claves SSH, mantener abierta una sesión hasta comprobar que se puede entrar con la nueva.')
w('- **Ficheros de configuración.** `~/app/.secrets.toml` de `back.cotown.com` tiene una sección `[default]` y otra '
  '`[production]`; en producción manda `[production]`, así que hay que cambiar el valor en esa sección si existe en ella. '
  '`~/etl/.secrets.toml` de `data.cotown.com` solo usa `[default]`. Los ficheros de claves deben tener permisos `600`.')
w('- **Copias en el repositorio.** El repositorio `back` contiene copias antiguas de ficheros de secretos y de claves '
  '(se indican en cada caso). **No** deben actualizarse con los valores nuevos: hay que retirarlas del repositorio.')
w('- **Gestor de contraseñas.** Al terminar, guardar allí el valor nuevo. Este inventario solo cambia si cambia el nombre '
  'o el sitio de la credencial.')
w('')
cycle('Clave SSH de administración (`cotown.key.pem`)',
      '`ssh-keygen -t rsa -b 4096 -f cotown.key.pem` (o `-t ed25519`). La actual es RSA 3072, comentario `generated-by-azure`, '
      'huella `SHA256:AvrDjc2lAClZ/LZnRws3VEMwqzURm9hRvRSSklGMs2g`.',
      ['`back.cotown.com`: clave pública en `/home/cotown/.ssh/authorized_keys` y en `/root/.ssh/authorized_keys`.',
       '`data.cotown.com`: clave pública en `/home/cotown/.ssh/authorized_keys` y en `/root/.ssh/authorized_keys`.',
       'Para el usuario `cotown`, el portal de Azure permite hacerlo desde la máquina virtual, *Ayuda > Restablecer contraseña > '
       'Restablecer la clave pública SSH*; la de `root` se cambia a mano.',
       '`data.cotown.com`: copia de la clave privada en `~/etl/cotown.key.pem` (sustituir).',
       'Puestos de los administradores (Oimbra) que acceden a los servidores.',
       'Repositorio `back`: `etl/cotown.key.pem` (retirar).'],
      'Quitar la clave pública antigua de los cuatro `authorized_keys`.',
      'Entrar con la clave nueva en los dos servidores (`data` usa el puerto 23141) y comprobar con `ssh-keygen -lf <fichero>` '
      'que los `authorized_keys` solo contienen la huella nueva.')
cycle('Clave SSH del túnel hacia Airflows (`id_partner.pem` / `airflows.key.pem`)',
      'Es **la misma clave** con dos nombres (RSA 3072, comentario `paco@paco-thinkpad`, huella '
      '`SHA256:5s7vKD9SgC4NdjhLG5gacnQlIoqs3DT7cOf3KFe8IaU`). Generar una RSA en formato PEM, compatible con la librería del túnel: '
      '`ssh-keygen -t rsa -b 4096 -m PEM -N "" -f id_partner.pem`.',
      ['`core.cotown.com`: clave pública en `/home/partner/.ssh/authorized_keys`. Lo hace el **proveedor de Airflows**: '
       'enviarle solo la clave pública.',
       '`back.cotown.com`: `~/app/id_partner.pem` (el nombre está en `SSHPKEY` de `~/app/.secrets.toml`).',
       '`data.cotown.com`: `~/etl/airflows.key.pem` (el nombre está en `SSHPKEY` de `~/etl/.secrets.toml`).',
       'Repositorio `back`: `airflows.key.pem`, `etl/airflows.key.pem`, `app/id_partner.pem` y '
       '`app/templates/report/id_partner.pem` (retirar).'],
      f'{RESTART}; el ETL la usa en su siguiente ejecución. Pedir al proveedor que retire la clave pública antigua.',
      'Que el servicio responde (por ejemplo, un informe o la página de pago) y que no hay errores de túnel en `docker logs back`; '
      'que la siguiente carga del ETL termina bien (`~/etl/log`).')
cycle('Usuario de la base de datos de Airflows (`DBUSER` / `DBPASS`)',
      'La cambia el **proveedor de Airflows** en PostgreSQL (`ALTER ROLE … PASSWORD …`).',
      ['`back.cotown.com`: `DBPASS` en `~/app/.secrets.toml`.',
       '`data.cotown.com`: `DBPASS` en `~/etl/.secrets.toml`.',
       'Repositorio `back`: `app/.secrets.toml` y `etl/.secrets.toml` (retirar).'],
      RESTART + '.',
      'Igual que la clave del túnel: el servicio y el ETL consultan la base de datos sin errores.')
cycle('Usuario de consulta `readonly`', 'Cambiar la contraseña del rol en PostgreSQL (proveedor de Airflows).',
      ['Solo lo usan los administradores para consultas; no está en ningún fichero de los servidores.'],
      'Ninguno.', 'Conectar con la contraseña nueva.')
cycle('Usuario de servicio de Airflows (`GQLUSER` / `GQLPASS`)',
      'Cambiar la contraseña del usuario en Airflows (usuarios del sistema / Keycloak).',
      ['`back.cotown.com`: `GQLPASS` en `~/app/.secrets.toml`.',
       '`data.cotown.com`: `GQLPASS` en `~/etl/.secrets.toml`.',
       'Generador de las webs: `code/src/data/constants.js` del repositorio `webs` (el servidor lo toma del repositorio en la '
       'siguiente generación) y `upload/upload.py` si se usa.',
       'Repositorio `back`: `app/.secrets.toml` y `etl/.secrets.toml` (retirar).'],
      RESTART + '.',
      'Una reserva de prueba en la web o la descarga de un documento; la siguiente generación de las webs (cada 2 horas) y '
      'el siguiente ETL terminan bien.')
cycle('Data warehouse (`DWDBUSER` / `DWDBPASS`)',
      'En `data.cotown.com`: `docker exec -it postgres psql -U <usuario> -d dw -c "ALTER ROLE <usuario> PASSWORD \'…\'"`.',
      ['`data.cotown.com`: `DWDBPASS` en `~/etl/.secrets.toml`.',
       'Power BI: credenciales del origen de datos en la puerta de enlace.',
       'Repositorio `back`: `etl/.secrets.toml` (retirar).'],
      'Ninguno en el servidor; actualizar la puerta de enlace de Power BI a la vez para no cortar las actualizaciones.',
      'Siguiente ETL correcto y actualización programada de Power BI correcta.')
cycle('Claves de firma de Redsys (`REDSYS_KEY_*`)',
      'Generar una clave nueva para cada terminal en el portal de administración de Redsys (Cotown o la entidad bancaria).',
      ['`back.cotown.com`: `REDSYS_KEY_COTOWN`, `REDSYS_KEY_VANDOR`, `REDSYS_KEY_DELEGADO` y `REDSYS_KEY_DEFAULT` en '
       '`~/app/.secrets.toml`.'],
      RESTART + '. Coordinar el cambio en Redsys y en el servidor en el mismo momento: entre uno y otro fallan los pagos.',
      'Un pago real de importe mínimo (o en el entorno de pruebas de Redsys) y su notificación registrada en el ERP.')
cycle('DocuSign (`docusign.private.key` / `RSA_KEY`)',
      'En DocuSign, *Apps and Keys*, aplicación de la integración: *Add RSA Keypair*; guardar la clave privada y anotar su identificador.',
      ['`back.cotown.com`: `~/app/docusign.private.key` (clave privada).',
       '`back.cotown.com`: `RSA_KEY` en `~/app/.secrets.toml` (identificador del par).',
       'Repositorio `back`: `app/docusign.private.key` y los `.key` de `app/docusign/` (retirar).'],
      RESTART + '. Después, borrar el par antiguo en DocuSign.',
      'El envío de un contrato a firma funciona.')
cycle('Cuentas de correo (`SMTPPASS`, `SMTPPASSVANDOR`)', 'Cambiar la contraseña en Microsoft 365 (IT de Cotown).',
      ['`back.cotown.com`: `SMTPPASS` y `SMTPPASSVANDOR` en `~/app/.secrets.toml`.'],
      RESTART + '.', 'Siguiente email automático enviado (registro de emails del ERP sin errores).')
cycle('Pipedrive (`CRM_KEY`)', 'Regenerar el token de API en Pipedrive (*Ajustes personales > API*) del usuario de la integración.',
      ['`back.cotown.com`: `CRM_KEY` en `~/app/.secrets.toml`.'],
      RESTART + '.', 'Un formulario de contacto de la web crea el lead en Pipedrive.')
cycle('Claves de la API contable', 'Generar un UUID nuevo (`uuidgen`) por consumidor.',
      ['`back.cotown.com`: nueva línea `"<uuid>" = "<rango>"` en `~/app/.secrets.toml`, con el mismo rango que la clave que sustituye.',
       'Consumidor: equipo de SAP de Cotown (rango `0:9999`) y Lemos (rango `5:5`).'],
      RESTART + '. Cuando el consumidor confirme el cambio, borrar la línea de la clave antigua y volver a reiniciar.',
      'El consumidor consulta con la clave nueva; con la antigua, la API responde con error.')
cycle('Usuario de SAP Business ByDesign (`SAPPASS`)', 'Cambiar la contraseña en SAP (equipo de SAP de Cotown).',
      ['`data.cotown.com`: `SAPPASS` en `~/etl/.secrets.toml`.'],
      'Ninguno (la carga del libro mayor está desactivada).', 'Cuando se reactive, la carga del libro mayor termina bien.')
cycle('Clave de sesión de la web de reserva (`COOKIE_KEY`)', '`python3 -c "import secrets; print(secrets.token_hex(32))"`.',
      ['`back.cotown.com`: `COOKIE_KEY` en `~/app/.secrets.toml`.'],
      RESTART + '. Se cierran las sesiones abiertas en la web de reserva.', 'Iniciar sesión en la web de reserva.')
cycle('Autorización de SharePoint (`rclone`)',
      'En `back.cotown.com`, como `cotown`: `rclone config reconnect <remoto>:` (el nombre del remoto se ve con `rclone listremotes`).',
      ['`back.cotown.com`: `~/.config/rclone/rclone.conf` (lo reescribe `rclone`).'],
      'Revocar la sesión anterior en Microsoft 365 (cuenta usada para la autorización).',
      'La copia de las 02:30 llega a SharePoint (`rclone lsd <remoto>:`).')
cycle('Certificados TLS', 'Los renueva `certbot` automáticamente. Solo hay que sustituirlos si se cree que la clave privada se ha '
      'expuesto: `certbot revoke` y `certbot certonly` para el dominio afectado.',
      ['`back.cotown.com`: `/etc/letsencrypt/` (lo usa `nginx`).',
       '`data.cotown.com`: `/etc/letsencrypt/` y la copia para PostgreSQL en `~/certs` (`~/certs/renew.sh`).'],
      '`docker restart nginx` en `back`; en `data`, ejecutar `~/certs/renew.sh` y reiniciar el contenedor `postgres`.',
      'Abrir las webs y conectar al data warehouse con SSL.')

w('## Credenciales a completar')
w('')
w('No están en los ficheros de configuración del sistema. Deben añadirse aquí (o en el gestor de contraseñas) indicando quién las custodia:')
w('')
w('| Acceso | Para qué | Custodia |')
w('|---|---|---|')
for row in [('Portal de Azure', 'Máquinas virtuales `back` y `data`, grupos de seguridad, copias', ''),
            ('Proveedor de Airflows', 'Soporte y gestión del servidor `core.cotown.com`', ''),
            ('Usuarios administradores de Airflows', 'Configuración del ERP (modelo, permisos, funciones)', ''),
            ('Consola de administración de Keycloak', 'Realm `airflows`', ''),
            ('GitHub, organización Cotowngroup', 'Repositorios del código', ''),
            ('Registrador de dominios y DNS', 'Dominios cotown.com, vanguard-student-housing.com, cotowngroup.com', 'IT de Cotown'),
            ('Grafana', 'Usuario administrador (configuración por defecto)', ''),
            ('Portal de Redsys', 'Gestión de terminales y claves', ''),
            ('DocuSign (administración)', 'Cuenta, usuarios y aplicación de integración', ''),
            ('Microsoft 365 (administración)', 'Cuentas de correo y SharePoint', 'IT de Cotown'),
            ('SharePoint para `rclone`', 'Autorización OAuth guardada en `~/.config/rclone/rclone.conf` de `back.cotown.com`', ''),
            ('Pipedrive (administración)', 'Cuenta del CRM', ''),
            ('Power BI', 'Área de trabajo y puerta de enlace', ''),
            ('Let\'s Encrypt', 'Cuenta de certbot en los servidores de Azure', '')]:
  w(f'| {row[0]} | {row[1]} | {row[2]} |')
w('')

# Build the document in salida/ (its table of contents is filled in by scripts/update_docx.ps1)
with tempfile.TemporaryDirectory() as tmp:
  tmp_md = os.path.join(tmp, 'secretos.md')
  open(tmp_md, 'w', encoding='utf-8').write('\n'.join(md))
  gen_docx.build({'file': 'Cotown - Inventario de credenciales', 'subtitle': 'Inventario de credenciales (confidencial)', 'chapters': [tmp_md]})
