# ###################################################
# Batch TB
# ---------------------------------------------------
# Process the TB uploads of Airflows (Batch.Tb_upload):
# each SAP Trial Balance export in 'pendiente' is
# transformed with the master workbook of its company
# (Admin.Files, 'Maestro TB <empresa>') and the upload
# gets its status, log and summary. A good one also
# replaces its months in gold.tb of the DW, and gets
# its file back with the TB rows in a sheet TB.
# Run by cron on the ETL machine. Reprocess = set the
# upload to 'pendiente'.
# ###################################################

# ###################################################
# Imports
# ###################################################

# System imports
import io
import json
import os
import sys
from pathlib import Path

# Cotown includes
from library.services.dbclient import DBClient
from library.services.config import settings
from library.services.apiclient import APIClient

# TB package, from its source folder
sys.path.insert(0, str(Path(__file__).resolve().parent / 'tb' / 'src'))
from tb.dw import SQL_DELETE, SQL_INSERT, dw_records
from tb.errors import ReadError
from tb.maestro import maestro_name, select_maestro
from tb.upload import MaestroWorkbook, failed_upload, process_upload

# Third-party imports
from psycopg2.extras import execute_values

# Logging
import logging
from logging.handlers import RotatingFileHandler
logger = logging.getLogger('COTOWN')


# ###################################################
# SQL
# ###################################################

# Take the oldest pending upload, atomically: two runs never take the same one
SQL_TAKE = '''
UPDATE "Batch"."Tb_upload" SET "Status" = 'procesando'
WHERE id = (
  SELECT id FROM "Batch"."Tb_upload"
  WHERE "Status" = 'pendiente'
  ORDER BY id
  LIMIT 1
  FOR UPDATE SKIP LOCKED
)
RETURNING id
'''

# Media type of an xlsx file
XLSX = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'

# Name of the file of an upload, and the new file of an upload (its export with the TB sheet)
QUERY_FILE = 'query ($id: Int!) { data: Batch_Tb_uploadList ( where: { id: { EQ: $id } } ) { File { name } } }'
QUERY_SET_FILE = 'mutation ($id: Int!, $file: Models_DocumentTypeInputType!) { data: Batch_Tb_uploadUpdate ( where: { id: { EQ: $id } }, entity: { File: $file } ) { id } }'

# Save the result of an upload
SQL_SAVE = '''
UPDATE "Batch"."Tb_upload"
SET "Status" = %s, "Log" = %s, "Company" = %s, "Months" = %s, "Rows" = %s, "Totals" = %s, "Processed_at" = now()
WHERE id = %s
'''


# ###################################################
# Connections
# ###################################################

def apiConnect():

  apiClient = APIClient(settings.DBHOST)
  apiClient.auth(user=settings.GQLUSER, password=settings.GQLPASS)
  return apiClient


def dbConnect():

  dbClient = DBClient(
    host=settings.DBHOST,
    port=settings.get('DBPORT', 5432),
    dbname=settings.DBNAME,
    user=settings.DBUSER,
    password=settings.DBPASS,
    sshuser=settings.get('SSHUSER', None),
    sshpassword=settings.get('SSHPASS', None),
    sshprivatekey=settings.get('SSHPKEY', None),
    readonly=False
  )
  dbClient.connect()
  return dbClient


def dwConnect():

  dwClient = DBClient(
    host=settings.DWDBHOST,
    port=settings.get('DWDBPORT', 5432),
    dbname=settings.DWDBNAME,
    user=settings.DWDBUSER,
    password=settings.DWDBPASS,
    sshuser=settings.get('DWSSHUSER', None),
    sshpassword=settings.get('DWSSHPASS', None),
    sshprivatekey=settings.get('DWSSHPKEY', None),
    readonly=False
  )
  dwClient.connect()
  return dwClient


# ###################################################
# DW
# ###################################################

# Replace the months of a good upload in gold.tb, in one transaction; on failure the DW stays as it was
def storeTB(dwClient, id, result):

  con = dwClient.getconn()
  try:
    con.autocommit = False
    with con.cursor() as cur:
      cur.execute(SQL_DELETE, (result.company, result.months.split(', ')))
      execute_values(cur, SQL_INSERT, dw_records(result.tb, id))
    con.commit()
  except Exception as e:
    con.rollback()
    raise ReadError(['No se puede guardar el TB en el DW (gold.tb): {}.'.format(e)])
  finally:
    con.autocommit = True
    dwClient.putconn(con)


# ###################################################
# Files from Airflows
# ###################################################

# Download a file field, or fail with a message for the log
def download(apiClient, id, entity):

  response = apiClient.getFile(id, entity)
  if response.status_code != 200:
    raise ReadError(['No se puede descargar el fichero {} {} de Airflows (HTTP {}).'.format(entity, id, response.status_code)])
  return response.content


# Give an upload its export with the TB sheet, under the same file name; any failure is an error of the upload
def storeWorkbook(apiClient, id, content):

  try:
    name = apiClient.call(QUERY_FILE, { 'id': id })['data'][0]['File']['name']
    response = apiClient.putFile(id, 'Batch/Tb_upload', 'File', content, XLSX)
    if response.status_code != 200:
      raise ReadError(['No se puede guardar el TB en el fichero de la carga (HTTP {}).'.format(response.status_code)])
    apiClient.call(QUERY_SET_FILE, { 'id': id, 'file': { 'name': name, 'oid': int(response.content), 'type': XLSX } })
  except ReadError:
    raise
  except Exception as e:
    raise ReadError(['No se puede guardar el TB en el fichero de la carga: {}.'.format(e)])


# Master workbook of a company: the single Admin.Files record 'Maestro TB <empresa>'
def fetchMaestro(apiClient, empresa):

  # Admin.Files records with that name; an Airflows failure is an error of this upload, not of the batch
  name = json.dumps(maestro_name(empresa))
  try:
    result = apiClient.call('{ data: Admin_FilesList ( where: { Name: { EQ: ' + name + ' } } ) { id Name Created_at Updated_at } }')
  except Exception as e:
    raise ReadError(['No se puede consultar la hoja maestra {} en Airflows: {}.'.format(maestro_name(empresa), e)])

  # The single one, with its content and date
  maestro = select_maestro(result['data'], empresa)
  return MaestroWorkbook(content=download(apiClient, maestro.id, 'Admin/Files'), modified=maestro.modified)


# ###################################################
# Main
# ###################################################

def main():

  # Connect
  try:
    dbClient = dbConnect()
    dwClient = dwConnect()
    apiClient = apiConnect()
  except Exception as e:
    logger.error(e)
    return
  con = dbClient.getconn()

  # One pending upload at a time, until there are none
  num = 0
  while True:
    cur = dbClient.execute(con, SQL_TAKE)
    row = cur.fetchone()
    cur.close()
    if row is None:
      break
    id = row['id']
    logger.info('Processing TB upload {}...'.format(id))

    # Process; a good upload goes to the DW, then its file gets the TB sheet; the upload never stays in 'procesando'
    try:
      export = download(apiClient, id, 'Batch/Tb_upload')
      result = process_upload(io.BytesIO(export), lambda empresa: fetchMaestro(apiClient, empresa))
      if result.status == 'ok':
        storeTB(dwClient, id, result)
        storeWorkbook(apiClient, id, result.workbook)
    except ReadError as e:
      result = failed_upload(e.errors)
    except Exception as e:
      logger.exception(e)
      result = failed_upload(['Error inesperado del proceso: {}.'.format(e)])

    # Save the result; if it fails, the upload stays in 'procesando' and the next one is taken
    try:
      cur = dbClient.execute(con, SQL_SAVE, (result.status, result.log, result.company, result.months, result.rows, result.totals, id))
      cur.close()
      logger.info('TB upload {}: {}'.format(id, result.status))
    except Exception as e:
      logger.exception(e)
    num += 1

  # Disconnect
  dbClient.putconn(con)
  dbClient.disconnect()
  dwClient.disconnect()
  logger.info('{} TB uploads processed'.format(num))


# ###################################################
# Startup
# ###################################################

if __name__ == '__main__':

  # Logging
  os.makedirs('log', exist_ok=True)
  logger.setLevel(settings.LOGLEVEL)
  formatter = logging.Formatter('[%(asctime)s] [%(name)s] [%(module)s] [%(funcName)s/%(lineno)3d] [%(levelname)s] %(message)s')
  console_handler = logging.StreamHandler()
  console_handler.setLevel(settings.LOGLEVEL)
  console_handler.setFormatter(formatter)
  file_handler = RotatingFileHandler('log/batch_tb.log', maxBytes=1000000, backupCount=5)
  file_handler.setLevel(settings.LOGLEVEL)
  file_handler.setFormatter(formatter)
  logger.addHandler(console_handler)
  logger.addHandler(file_handler)
  logger.info('Started')

  main()
  logger.info('Finished')
