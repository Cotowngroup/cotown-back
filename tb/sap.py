# ###################################################
# SAP TB
# ---------------------------------------------------
# Build the Trial Balance export of a company and
# months from the general ledger of SAP (OData), with
# the same columns and format as the export done by
# hand, and save it or upload it as a TB upload of
# Airflows (Batch.Tb_upload), which tb.py
# processes. With --carga, the file replaces the one
# of an existing upload, which goes back to pendiente.
#
# python sap.py --empresa CTS00 --meses 2026-08
#   [--xlsx fichero.xlsx] [--subir [--carga ID]]
# ###################################################

# ###################################################
# Imports
# ###################################################

# System imports
import argparse
import re
import sys
from datetime import datetime
from pathlib import Path

# Third-party imports
import requests
from requests.auth import HTTPBasicAuth

# Cotown includes
from library.services.config import settings
from library.services.apiclient import APIClient

from library.business.errors import ReadError
from library.business.sap import SAP_FIELDS, Masters, Selection, build_export

# Logging
import logging
logger = logging.getLogger('COTOWN')

# Month argument: AAAA-MM
MONTH = re.compile(r'^\d{4}-(0[1-9]|1[0-2])$')

# Media type of an xlsx file
XLSX = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'

# Creation of a TB upload with its file; it is born 'pendiente'
QUERY_CREATE = 'mutation ($file: Models_DocumentTypeInputType!) { data: Batch_Tb_uploadCreate ( entity: { File: $file } ) { id } }'

# New file of an existing TB upload: back to 'pendiente', without the fields of its last processing
QUERY_REPLACE = 'mutation ($id: Int!, $file: Models_DocumentTypeInputType!) { data: Batch_Tb_uploadUpdate ( where: { id: { EQ: $id } }, entity: { File: $file, Status: pendiente, Log: null, Company: null, Months: null, Rows: null, Totals: null, Processed_at: null } ) { id } }'

# SAP masters the general ledger report lacks, from the same OData service: (report, key field, code field, text field)
MASTER_SERVICES = ('RPSERVICE_Q0001', 'CSERV_INT_ID', 'CPROD_CATG_UUID', 'TPROD_CATG_UUID')
MASTER_MATERIALS = ('RPMATERIAL_Q0001', 'CMATR_INT_ID', 'CPROD_CATG_UUID', 'TPROD_CATG_UUID')
MASTER_TASKS = ('RPPROPRJU05_Q0007', 'CTASK_UUID', 'CPR_RESP_CC_UUID', 'TPR_RESP_CC_UUID')


# ###################################################
# SAP
# ###################################################

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


# ###################################################
# Main
# ###################################################

# Print every error and return the exit code of a failed run
def fail(errors, what):

  print('{} errores; {}:'.format(len(errors), what), file=sys.stderr)
  for message in errors:
    print('- ' + message, file=sys.stderr)
  return 1


def main(argv=None):

  # Arguments
  parser = argparse.ArgumentParser(description='Trial Balance export from the general ledger of SAP.')
  parser.add_argument('--empresa', required=True, help='SAP company, e.g. CTS00')
  parser.add_argument('--meses', nargs='+', required=True, help='months, AAAA-MM')
  parser.add_argument('--xlsx', type=Path, help='save the export to this file')
  parser.add_argument('--subir', action='store_true', help='upload the export as a TB upload of Airflows')
  parser.add_argument('--carga', type=int, help='with --subir, replace the file of this TB upload and set it back to pendiente')
  args = parser.parse_args(argv)
  if not args.xlsx and not args.subir:
    parser.error('indica --xlsx, --subir o los dos')
  if args.carga is not None and not args.subir:
    parser.error('--carga va con --subir')
  errors = ['Mes {} no válido: usa AAAA-MM.'.format(month) for month in args.meses if not MONTH.match(month)]
  if args.empresa not in settings.SAPBOOKS:
    errors.append('Empresa {} sin libro contable en SAPBOOKS de .settings.toml.'.format(args.empresa))
  if errors:
    return fail(errors, 'no se ha generado nada')
  months = sorted(set(args.meses))

  # Records of every month and the masters, collecting every error; then the export
  records = []
  for month in months:
    try:
      records.extend(fetchMonth(args.empresa, month))
    except ReadError as e:
      errors.extend(e.errors)
  try:
    masters = fetchMasters()
  except ReadError as e:
    errors.extend(e.errors)
  if errors:
    return fail(errors, 'no se ha generado nada')
  book = settings.SAPBOOKS[args.empresa]
  book_name = settings.get('SAPBOOKNAMES', {}).get(book)
  selection = Selection(
    empresa=args.empresa,
    sistema_contable='{} ({})'.format(book, book_name) if book_name else book,
    usuario=settings.SAPUSER,
    generado=datetime.now().strftime('%d.%m.%Y %H:%M:%S'),
  )
  try:
    content = build_export(records, months, selection, masters)
  except ReadError as e:
    return fail(e.errors, 'no se ha generado nada')

  # Save
  name = 'TB - {} - {} (SAP).xlsx'.format(args.empresa, ', '.join(months))
  if args.xlsx:
    args.xlsx.write_bytes(content)
    print('Export guardado en {}.'.format(args.xlsx))

  # Upload: store the file, then create the TB upload with it or give it to an existing one
  if args.subir:
    what = 'no se ha creado la carga' if args.carga is None else 'no se ha cambiado la carga {}'.format(args.carga)
    try:
      apiClient = APIClient(settings.DBHOST)
      apiClient.auth(user=settings.GQLUSER, password=settings.GQLPASS)
      response = apiClient.putFile(args.carga or 0, 'Batch/Tb_upload', 'File', content, XLSX)
      if response.status_code != 200:
        return fail(['Airflows responde HTTP {} al subir el fichero: {}'.format(response.status_code, response.text[:300])], what)
      file = { 'name': name, 'oid': int(response.content), 'type': XLSX }
      if args.carga is None:
        result = apiClient.call(QUERY_CREATE, { 'file': file })
      else:
        result = apiClient.call(QUERY_REPLACE, { 'id': args.carga, 'file': file })
    except Exception as e:
      return fail(['No se puede guardar la carga en Airflows: {}.'.format(e)], what)
    if not result['data']:
      return fail(['La carga {} no existe en Airflows.'.format(args.carga)], what)
    upload_id = args.carga if args.carga is not None else result['data']['id']
    print('Carga TB {} {} en Airflows con "{}", en pendiente: la procesa tb.py.'.format(upload_id, 'creada' if args.carga is None else 'actualizada', name))
  return 0


# ###################################################
# Startup
# ###################################################

if __name__ == '__main__':

  logging.basicConfig(level=settings.LOGLEVEL, format='[%(asctime)s] [%(levelname)s] %(message)s')
  sys.exit(main())
