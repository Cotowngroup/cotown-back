# ###################################################
# Batch TB
# ---------------------------------------------------
# Two steps, each with its own cron line on the ETL
# machine (spec, phase IV):
#
# procesar (default, every 15 minutes): process the TB
# uploads of Airflows (Batch.Tb_upload). Uploads stuck
# in 'procesando' for over an hour go back to
# 'pendiente'; each upload in 'pendiente' is
# transformed with the master workbook of its company
# (Admin.Files, 'Maestro TB <empresa>') and gets its
# status, log and summary; then uploads in 'error'
# whose master workbook changed after they were
# processed are processed again. A good one also
# replaces its months in gold.tb of the DW, and gets
# its file back with the TB rows in a sheet TB.
#
# sap (daily): build the Trial Balance export of the
# previous and the current month of each company of
# SAPBOOKS from the general ledger of SAP (OData), with
# the same columns and format as the export done by
# hand, and give it to the upload of that company and
# month, which goes back to 'pendiente'.
#
# python tb.py [procesar]
# python tb.py sap [--empresa CTS00] [--meses 2026-08 ...] [--xlsx CARPETA]
# ###################################################

# ###################################################
# Imports
# ###################################################

# System imports
import argparse
import io
import json
import os
import re
from datetime import date, datetime
from pathlib import Path

# Cotown includes
from library.services.dbclient import DBClient
from library.services.config import settings
from library.services.apiclient import APIClient

from library.business.dw import SQL_DELETE, SQL_INSERT, dw_records
from library.business.errors import ReadError
from library.business.maestro import maestro_name, select_maestro
from library.business.sap import SAP_FIELDS, Masters, Selection, build_export
from library.business.schedule import CREATE, SKIP, DownloadMonth, choose_upload, export_name, months_to_download
from library.business.upload import MaestroWorkbook, failed_upload, process_upload

# Third-party imports
import requests
from requests.auth import HTTPBasicAuth
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

# Uploads stuck in 'procesando' for over an hour go back to 'pendiente'; the audit trigger sets Updated_at when it is taken
SQL_RECOVER = '''
UPDATE "Batch"."Tb_upload" SET "Status" = 'pendiente'
WHERE "Status" = 'procesando' AND "Updated_at" < now() - interval '1 hour'
RETURNING id
'''

# Take the oldest upload in 'error' with company whose master workbook (maestro_name()) changed after it was processed
SQL_TAKE_RETRY = '''
UPDATE "Batch"."Tb_upload" SET "Status" = 'procesando'
WHERE id = (
  SELECT u.id FROM "Batch"."Tb_upload" u
  WHERE u."Status" = 'error'
    AND u."Company" IS NOT NULL
    AND EXISTS (
      SELECT 1 FROM "Admin"."Files" f
      WHERE f."Name" = 'Maestro TB ' || u."Company" AND f."Updated_at" > u."Processed_at"
    )
  ORDER BY u.id
  LIMIT 1
  FOR UPDATE OF u SKIP LOCKED
)
RETURNING id
'''

# Media type of an xlsx file
XLSX = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'

# Name of the file of an upload, and the new file of an upload (its export with the TB sheet)
QUERY_FILE = 'query ($id: Int!) { data: Batch_Tb_uploadList ( where: { id: { EQ: $id } } ) { File { name } } }'
QUERY_SET_FILE = 'mutation ($id: Int!, $file: Models_DocumentTypeInputType!) { data: Batch_Tb_uploadUpdate ( where: { id: { EQ: $id } }, entity: { File: $file } ) { id } }'

# Uploads, to choose the one of a company and month
QUERY_UPLOADS = '{ data: Batch_Tb_uploadList { id Company Months Status } }'

# Creation of a TB upload with its file, company and month; it is born 'pendiente'
QUERY_CREATE = 'mutation ($file: Models_DocumentTypeInputType!, $company: String!, $months: String!) { data: Batch_Tb_uploadCreate ( entity: { File: $file, Company: $company, Months: $months } ) { id } }'

# New file of an upload not in 'procesando': back to 'pendiente', with its company and month and without the rest of its last processing
QUERY_REPLACE = 'mutation ($id: Int!, $file: Models_DocumentTypeInputType!, $company: String!, $months: String!) { data: Batch_Tb_uploadUpdate ( where: { id: { EQ: $id }, Status: { NE: procesando } }, entity: { File: $file, Status: pendiente, Company: $company, Months: $months, Log: null, Rows: null, Totals: null, Processed_at: null } ) { id } }'

# Save the result of an upload; when the result does not know its company and months, the upload keeps the ones it had
SQL_SAVE = '''
UPDATE "Batch"."Tb_upload"
SET "Status" = %s, "Log" = %s, "Company" = COALESCE(%s, "Company"), "Months" = COALESCE(%s, "Months"), "Rows" = %s, "Totals" = %s, "Processed_at" = now()
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
# SAP
# ###################################################

# Month argument: AAAA-MM
MONTH = re.compile(r'^\d{4}-(0[1-9]|1[0-2])$')

# SAP masters the general ledger report lacks, from the same OData service: (report, key field, code field, text field)
MASTER_SERVICES = ('RPSERVICE_Q0001', 'CSERV_INT_ID', 'CPROD_CATG_UUID', 'TPROD_CATG_UUID')
MASTER_MATERIALS = ('RPMATERIAL_Q0001', 'CMATR_INT_ID', 'CPROD_CATG_UUID', 'TPROD_CATG_UUID')
MASTER_TASKS = ('RPPROPRJU05_Q0007', 'CTASK_UUID', 'CPR_RESP_CC_UUID', 'TPR_RESP_CC_UUID')


# Every record of an OData report of SAP, texts in Spanish as in the export done by hand; raises ReadError
def fetchReport(url, params, what):

  params = { **params, '$format': 'json', '$top': 999999, '$inlinecount': 'allpages', 'sap-language': 'ES' }
  try:
    response = requests.get(url, params=params, auth=HTTPBasicAuth(settings.SAPUSER, settings.SAPPASS), timeout=900)
  except requests.RequestException as e:
    raise ReadError(['No se puede conectar con SAP para {}: {}.'.format(what, e)])
  if response.status_code != 200:
    raise ReadError(['SAP responde HTTP {} al pedir {}: {}'.format(response.status_code, what, response.text[:300])])
  try:
    data = response.json()['d']
    count = int(data['__count'])
  except (ValueError, KeyError) as e:
    raise ReadError(['Respuesta de SAP no válida para {}: {}.'.format(what, e)])
  if count != len(data['results']):
    raise ReadError(['SAP ha devuelto {} de {} registros de {}: respuesta incompleta.'.format(len(data['results']), count, what)])
  return data['results']


# Code and text of each key of an SAP master report: { key: (code, text) }
def fetchMaster(report, key, code, text):

  url = '{}/{}QueryResults'.format(settings.SAPURL_GL.rsplit('/', 1)[0], report)
  records = fetchReport(url, { '$select': ','.join([key, code, text]) }, 'el maestro {}'.format(report))
  return { record[key]: (record[code], record[text]) for record in records }


# Masters of the export: product categories of services and materials, responsible units of project tasks
def fetchMasters():

  categories = { **fetchMaster(*MASTER_MATERIALS), **fetchMaster(*MASTER_SERVICES) }
  return Masters(product_categories=categories, responsible_units=fetchMaster(*MASTER_TASKS))


# General ledger records of a company and month; raises ReadError
def fetchMonth(empresa, month):

  # The period goes without leading zero: SAP rejects 01 as a property name
  year, period = month.split('-')
  params = {
    '$select': ','.join(SAP_FIELDS),
    '$filter': "(PARA_SETOFBKS eq '{}' and PARA_COMPANY eq '{}' and CFISCPER eq {} and CFISCYEAR eq {})".format(settings.SAPBOOKS[empresa], empresa, int(period), year),
  }
  records = fetchReport(settings.SAPURL_GL, params, '{} de {}'.format(month, empresa))
  logger.info('{} {}: {} records'.format(empresa, month, len(records)))
  return records


# Export of a company and month from SAP, as the export done by hand; None if the month may be empty and is; raises ReadError
def exportMonth(empresa, download, masters):

  records = fetchMonth(empresa, download.month)
  if not records and download.may_be_empty:
    return None
  book = settings.SAPBOOKS[empresa]
  book_name = settings.get('SAPBOOKNAMES', {}).get(book)
  selection = Selection(
    empresa=empresa,
    sistema_contable='{} ({})'.format(book, book_name) if book_name else book,
    usuario=settings.SAPUSER,
    generado=datetime.now().strftime('%d.%m.%Y %H:%M:%S'),
  )
  return build_export(records, [download.month], selection, masters)


# Give the export of a company and month to its upload (A4, A5): a new one, or the existing one back to 'pendiente'
def uploadMonth(apiClient, empresa, month, content):

  # The upload of that company and month
  choice = choose_upload(apiClient.call(QUERY_UPLOADS)['data'], empresa, month)
  if choice.warning:
    logger.warning(choice.warning)
  if choice.action == SKIP:
    return

  # Store the file, then create the upload with it or give it to the existing one
  response = apiClient.putFile(choice.id or 0, 'Batch/Tb_upload', 'File', content, XLSX)
  if response.status_code != 200:
    raise ReadError(['Airflows responde HTTP {} al subir el fichero: {}'.format(response.status_code, response.text[:300])])
  variables = {
    'file': { 'name': export_name(empresa, month), 'oid': int(response.content), 'type': XLSX },
    'company': empresa,
    'months': month,
  }
  if choice.action == CREATE:
    result = apiClient.call(QUERY_CREATE, variables)
  else:
    result = apiClient.call(QUERY_REPLACE, { 'id': choice.id, **variables })
  if not result['data']:
    raise ReadError(['Airflows no ha guardado la carga de {} {}: la carga {} está en procesando o ya no existe; se descarga en la próxima ejecución.'.format(empresa, month, choice.id)])
  logger.info('{} {}: TB upload {} {}, in pendiente'.format(empresa, month, choice.id or result['data']['id'], 'replaced' if choice.id else 'created'))


# ###################################################
# Steps
# ###################################################

# Process one taken upload; a good upload goes to the DW, then its file gets the TB sheet; it never stays in 'procesando'
def processUpload(dbClient, con, dwClient, apiClient, id):

  logger.info('Processing TB upload {}...'.format(id))
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

  # Save the result; if it fails, the upload stays in 'procesando' until it is recovered
  try:
    cur = dbClient.execute(con, SQL_SAVE, (result.status, result.log, result.company, result.months, result.rows, result.totals, id))
    cur.close()
    logger.info('TB upload {}: {}'.format(id, result.status))
  except Exception as e:
    logger.exception(e)


# Take uploads with a query, one at a time, until there are none; returns how many
def processAll(dbClient, con, dwClient, apiClient, sql):

  num = 0
  while True:
    cur = dbClient.execute(con, sql)
    row = cur.fetchone()
    cur.close()
    if row is None:
      return num
    processUpload(dbClient, con, dwClient, apiClient, row['id'])
    num += 1


# Step procesar (A2): recover stuck uploads, process the pending ones, then the errors whose master workbook changed
def stepProcess():

  # Connect
  try:
    dbClient = dbConnect()
    dwClient = dwConnect()
    apiClient = apiConnect()
  except Exception as e:
    logger.error(e)
    return
  con = dbClient.getconn()

  # Stuck in 'procesando'
  cur = dbClient.execute(con, SQL_RECOVER)
  recovered = [row['id'] for row in cur.fetchall()]
  cur.close()
  if recovered:
    logger.warning('TB uploads back to pendiente after an hour in procesando: {}'.format(', '.join(map(str, recovered))))

  # Pending, then errors to retry
  pending = processAll(dbClient, con, dwClient, apiClient, SQL_TAKE)
  retried = processAll(dbClient, con, dwClient, apiClient, SQL_TAKE_RETRY)

  # Disconnect
  dbClient.putconn(con)
  dbClient.disconnect()
  dwClient.disconnect()
  logger.info('{} TB uploads processed, {} retried after a change of their master workbook'.format(pending, retried))


# Step sap (A3-A6): each company and month from SAP to its upload; or, with a folder, to files there and not to Airflows
def stepSap(empresas, downloads, folder):

  # SAP masters once for every export, and Airflows
  try:
    masters = fetchMasters()
    apiClient = None if folder else apiConnect()
  except ReadError as e:
    logger.error(' '.join(e.errors))
    return
  except Exception as e:
    logger.error(e)
    return

  # Each company and month on its own: a failure leaves its upload as it was and does not stop the rest
  for empresa in empresas:
    for download in downloads:
      try:
        content = exportMonth(empresa, download, masters)
        if content is None:
          logger.info('{} {}: no postings in SAP yet, skipped'.format(empresa, download.month))
        elif folder:
          path = folder / export_name(empresa, download.month)
          path.write_bytes(content)
          logger.info('{} {}: saved in {}'.format(empresa, download.month, path))
        else:
          uploadMonth(apiClient, empresa, download.month, content)
      except ReadError as e:
        logger.error('{} {}: {}'.format(empresa, download.month, ' '.join(e.errors)))
      except Exception as e:
        logger.exception(e)


# ###################################################
# Main
# ###################################################

def main(argv=None):

  # Arguments
  parser = argparse.ArgumentParser(description='TB batch: process the TB uploads of Airflows, or download months from SAP.')
  parser.add_argument('paso', nargs='?', choices=['procesar', 'sap'], default='procesar', help='step; procesar by default')
  parser.add_argument('--empresa', help='sap: one SAP company, e.g. CTS00; every company of SAPBOOKS by default')
  parser.add_argument('--meses', nargs='+', help='sap: months, AAAA-MM; the previous and the current month by default')
  parser.add_argument('--xlsx', type=Path, help='sap: save the exports in this folder instead of uploading them')
  args = parser.parse_args(argv)
  if args.paso == 'procesar' and (args.empresa or args.meses or args.xlsx):
    parser.error('--empresa, --meses y --xlsx van con el paso sap')

  if args.paso == 'procesar':
    stepProcess()
    return

  # Companies and months of the step sap; months asked for by hand must have postings
  empresas = [args.empresa] if args.empresa else list(settings.SAPBOOKS)
  if args.empresa and args.empresa not in settings.SAPBOOKS:
    parser.error('empresa {} sin libro contable en SAPBOOKS de .settings.toml'.format(args.empresa))
  if args.meses:
    wrong = [month for month in args.meses if not MONTH.match(month)]
    if wrong:
      parser.error('meses no válidos (usa AAAA-MM): {}'.format(', '.join(wrong)))
    downloads = [DownloadMonth(month, may_be_empty=False) for month in sorted(set(args.meses))]
  else:
    downloads = months_to_download(date.today())
  if args.xlsx:
    args.xlsx.mkdir(parents=True, exist_ok=True)
  stepSap(empresas, downloads, args.xlsx)


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
  file_handler = RotatingFileHandler('log/tb.log', maxBytes=1000000, backupCount=5)
  file_handler.setLevel(settings.LOGLEVEL)
  file_handler.setFormatter(formatter)
  logger.addHandler(console_handler)
  logger.addHandler(file_handler)
  logger.info('Started')

  main()
  logger.info('Finished')
