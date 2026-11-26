# ###################################################
# SAP TB
# ---------------------------------------------------
# Build the Trial Balance export of a company and
# months from the general ledger of SAP (OData), in
# the same layout as the export done by hand, and
# save it or upload it as a TB upload of Airflows
# (Batch.Tb_upload), which batch_tb.py processes.
#
# python sap_tb.py --empresa CTS00 --meses 2026-08
#   [--xlsx fichero.xlsx] [--subir]
# ###################################################

# ###################################################
# Imports
# ###################################################

# System imports
import argparse
import re
import sys
from pathlib import Path

# Third-party imports
import requests
from requests.auth import HTTPBasicAuth

# Cotown includes
from library.services.config import settings
from library.services.apiclient import APIClient

# TB package, from its source folder
sys.path.insert(0, str(Path(__file__).resolve().parent / 'tb' / 'src'))
from tb.errors import ReadError
from tb.sap import SAP_FIELDS, build_export

# Logging
import logging
logger = logging.getLogger('COTOWN')

# Month argument: AAAA-MM
MONTH = re.compile(r'^\d{4}-(0[1-9]|1[0-2])$')

# Media type of an xlsx file
XLSX = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'

# Creation of a TB upload with its file; it is born 'pendiente'
QUERY_CREATE = 'mutation ($file: Models_DocumentTypeInputType!) { data: Batch_Tb_uploadCreate ( entity: { File: $file } ) { id } }'


# ###################################################
# SAP
# ###################################################

# General ledger records of a company and month, texts in Spanish as in the export done by hand; raises ReadError
def fetchMonth(empresa, month):

  # The period goes without leading zero: SAP rejects 01 as a property name
  year, period = month.split('-')
  params = {
    '$select': ','.join(SAP_FIELDS),
    '$filter': "(PARA_SETOFBKS eq '{}' and PARA_COMPANY eq '{}' and CFISCPER eq {} and CFISCYEAR eq {})".format(settings.SAPBOOKS[empresa], empresa, int(period), year),
    '$format': 'json',
    '$top': 999999,
    '$inlinecount': 'allpages',
    'sap-language': 'ES'
  }
  try:
    response = requests.get(settings.SAPURL_GL, params=params, auth=HTTPBasicAuth(settings.SAPUSER, settings.SAPPASS), timeout=900)
  except requests.RequestException as e:
    raise ReadError(['No se puede conectar con SAP para {} de {}: {}.'.format(month, empresa, e)])
  if response.status_code != 200:
    raise ReadError(['SAP responde HTTP {} al pedir {} de {}: {}'.format(response.status_code, month, empresa, response.text[:300])])

  # Every record of the month, or an error
  try:
    data = response.json()['d']
    count = int(data['__count'])
  except (ValueError, KeyError) as e:
    raise ReadError(['Respuesta de SAP no válida para {} de {}: {}.'.format(month, empresa, e)])
  if count != len(data['results']):
    raise ReadError(['SAP ha devuelto {} de {} apuntes de {} en {}: respuesta incompleta.'.format(len(data['results']), count, empresa, month)])
  logger.info('{} {}: {} records'.format(empresa, month, count))
  return data['results']


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
  args = parser.parse_args(argv)
  if not args.xlsx and not args.subir:
    parser.error('indica --xlsx, --subir o los dos')
  errors = ['Mes {} no válido: usa AAAA-MM.'.format(month) for month in args.meses if not MONTH.match(month)]
  if args.empresa not in settings.SAPBOOKS:
    errors.append('Empresa {} sin libro contable en SAPBOOKS de .settings.toml.'.format(args.empresa))
  if errors:
    return fail(errors, 'no se ha generado nada')
  months = sorted(set(args.meses))

  # Records of every month, collecting the errors of all of them; then the export
  records = []
  for month in months:
    try:
      records.extend(fetchMonth(args.empresa, month))
    except ReadError as e:
      errors.extend(e.errors)
  if errors:
    return fail(errors, 'no se ha generado nada')
  try:
    content = build_export(records, args.empresa, months)
  except ReadError as e:
    return fail(e.errors, 'no se ha generado nada')

  # Save
  name = 'TB - {} - {} (SAP).xlsx'.format(args.empresa, ', '.join(months))
  if args.xlsx:
    args.xlsx.write_bytes(content)
    print('Export guardado en {}.'.format(args.xlsx))

  # Upload: store the file, then create the TB upload with it
  if args.subir:
    try:
      apiClient = APIClient(settings.DBHOST)
      apiClient.auth(user=settings.GQLUSER, password=settings.GQLPASS)
      response = apiClient.putFile(0, 'Batch/Tb_upload', 'File', content, XLSX)
      if response.status_code != 200:
        return fail(['Airflows responde HTTP {} al subir el fichero: {}'.format(response.status_code, response.text[:300])], 'no se ha creado la carga')
      result = apiClient.call(QUERY_CREATE, { 'file': { 'name': name, 'oid': int(response.content), 'type': XLSX } })
    except Exception as e:
      return fail(['No se puede crear la carga en Airflows: {}.'.format(e)], 'no se ha creado la carga')
    upload_id = result['data']['id']
    print('Carga TB {} creada en Airflows con "{}": la procesa batch_tb.py.'.format(upload_id, name))
  return 0


# ###################################################
# Startup
# ###################################################

if __name__ == '__main__':

  logging.basicConfig(level=settings.LOGLEVEL, format='[%(asctime)s] [%(levelname)s] %(message)s')
  sys.exit(main())
