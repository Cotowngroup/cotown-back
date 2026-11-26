# ###################################################
# Batch TB
# ---------------------------------------------------
# Process the TB uploads of Airflows (Batch.Tb_upload):
# each SAP Trial Balance export in 'pendiente' is
# transformed with the master workbook of its company
# (Admin.Files, 'Maestro TB <empresa>') and the upload
# gets its status, log and summary. Run by cron on the
# ETL machine. Reprocess = set the upload to 'pendiente'.
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
from tb.errors import ReadError
from tb.maestro import maestro_name, select_maestro
from tb.upload import MaestroWorkbook, failed_upload, process_upload

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


# ###################################################
# Files from Airflows
# ###################################################

# Download a file field, or fail with a message for the log
def download(apiClient, id, entity):

  response = apiClient.getFile(id, entity)
  if response.status_code != 200:
    raise ReadError(['No se puede descargar el fichero {} {} de Airflows (HTTP {}).'.format(entity, id, response.status_code)])
  return response.content


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

    # Process; whatever happens, the upload does not stay in 'procesando'
    try:
      export = download(apiClient, id, 'Batch/Tb_upload')
      result = process_upload(io.BytesIO(export), lambda empresa: fetchMaestro(apiClient, empresa))
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
