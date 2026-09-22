# ##################################################
# Imports
# ##################################################

# System imports
from zipfile import ZipFile
from datetime import date
from base64 import b64encode
from jinja2 import Environment, FileSystemLoader, select_autoescape
from weasyprint import HTML
from PIL import Image, ImageOps, ImageChops
from io import BytesIO
import os
import re

# Logging
import logging
logger = logging.getLogger('COTOWN')


# ##################################################
# Clear folder
# ##################################################

def clear(folder):

  for filename in os.listdir(folder):
    file_path = os.path.join(folder, filename)
    if os.path.isfile(file_path):
      os.remove(file_path)


# ##################################################
# Zip all files in folder
# ##################################################

def zip(name, folder):

  with ZipFile(name, 'w') as zip_file:
    for foldername, _, filenames in os.walk(folder):
      for filename in filenames:
        logger.info(filename)
        file_path = os.path.join(foldername, filename)
        zip_file.write(file_path, foldername[len(folder):] + '/' + filename)
        os.remove(file_path)
    return name


# ##################################################
# Download bills from Airflows
# ##################################################

def download_bills(apiClient, variables=None):

  # Auth
  logger.info('Downloading bills...')
  clear('download')
 
  # Get records
  query = '''query Download ($fdesde:String, $fhasta:String, $pdesde:Int, $phasta:Int) {
    data: Billing_InvoiceList (
      where: {
        AND: [
          { Issued_date: { GE: $fdesde } }
          { Issued_date: { LT: $fhasta } }
          { Provider_id: { GE: $pdesde } }
          { Provider_id: { LE: $phasta } }
        ]
      }
    ) {
      id
      Code
      Bill_type
      Provider: ProviderViaProvider_id { Document }
      Document { name }
    }
  }'''
  result = apiClient.call(query, variables)

  # Download each file
  num = 0
  for item in result['data']:

    # Bill
    if item['Document']:
      name = item['Provider']['Document'] + '_' + item['Code']
      folder = 'recibos' if item['Bill_type'] == 'recibo' else 'facturas'
      file = apiClient.getFile(item['id'], 'Billing/Invoice', 'Document')
      with open('download/' + folder + '/' + name + '.pdf', 'wb') as pdf:
        logger.info(name)
        num += 1
        pdf.write(file.content)
        pdf.close()

  # Info
  logger.info('Downloaded {} bills'.format(num))

  # Zip
  if num > 0:
    zip('facturas.zip', 'download')
    return 'facturas.zip'


# ##################################################
# Download contracts from Airflows
# ##################################################

def download_contracts(apiClient, variables=None):

  # Auth
  logger.info('Downloading contracts...')
  clear('download')
 
  # Get records (B2C bookings)
  query = '''
  query Download ($fdesde:String, $fhasta:String, $pdesde:Int, $phasta:Int, $bdesde:Int, $bhasta:Int) {
    data: Booking_BookingList (
      where: {
        AND: [
          { Date_from: { GE: $fdesde } }
          { Date_from: { LT: $fhasta } }
          { Resource_id: { IS_NULL: false } }
        ]
      }
    ) {
      resource: ResourceViaResource_id {
        building: BuildingViaBuilding_id (
          joinType: INNER
          where: {
            AND: [
              { id: { GE: $bdesde } }
              { id: { LE: $bhasta } }
            ]
          }
        ) {
          Name
        }
        Code
        ProviderViaOwner_id (
          joinType: INNER
          where: {
            AND: [
              { id: { GE: $pdesde } }
              { id: { LE: $phasta } }
            ]
          }
        ) {
          id
        }
      }
      id
      Contract_rent { name }
      Contract_services { name }
    }
  }'''
  result = apiClient.call(query, variables)

  # Download each file
  num = 0
  for item in result['data']:

    # Rent contract
    if item['resource'] and item['Contract_rent']:
      name = 'Renta (' + str(item['id']) + ') ' + str(item['resource']['building']['Name']) + ' ' + str(item['resource']['Code'][7:])
      file = apiClient.getFile(item['id'], 'Booking/Booking', 'Contract_rent')
      with open('download/' + name + '.pdf', 'wb') as pdf:
        logger.info(name)
        num += 1
        pdf.write(file.content)
        pdf.close()

    # Services contract
    '''
    if item['resource'] and item['Contract_services']:
      name = 'Servicios (' + str(item['id']) + ') ' + str(item['resource']['building']['Name']) + ' ' + str(item['resource']['Code'][7:])
      file = apiClient.getFile(item['id'], 'Booking/Booking', 'Contract_services')
      with open('download/' + name + '.pdf', 'wb') as pdf:
        logger.info(name)
        num += 1
        pdf.write(file.content)
        pdf.close()
    '''

  # Get records (B2B group bookings)
  group_query = '''
  query Download ($fdesde:String, $fhasta:String) {
    data: Booking_Booking_groupList (
      where: {
        AND: [
          { Date_from: { GE: $fdesde } }
          { Date_from: { LT: $fhasta } }
        ]
      }
    ) {
      id
      Contract_rent { name }
      Contract_services { name }
      customer: CustomerViaPayer_id {
        Name
      }
    }
  }'''
  group_result = apiClient.call(group_query, variables)

  # Download each group file
  for item in group_result['data']:

    # Payer name (safe for file system)
    payer = str((item['customer'] or {}).get('Name') or '').replace('/', '-').replace('\\', '-').strip()

    # Rent contract
    if item['Contract_rent']:
      name = 'Renta B2B (' + str(item['id']) + ') ' + payer
      file = apiClient.getFile(item['id'], 'Booking/Booking_group', 'Contract_rent')
      with open('download/' + name + '.pdf', 'wb') as pdf:
        logger.info(name)
        num += 1
        pdf.write(file.content)
        pdf.close()

    # Services contract
    '''
    if item['Contract_services']:
      name = 'Servicios B2B (' + str(item['id']) + ') ' + payer
      file = apiClient.getFile(item['id'], 'Booking/Booking_group', 'Contract_services')
      with open('download/' + name + '.pdf', 'wb') as pdf:
        logger.info(name)
        num += 1
        pdf.write(file.content)
        pdf.close()
    '''

  # Info
  logger.info('Downloaded {} contracts'.format(num))

  # Zip
  if num > 0:
    zip('contratos.zip', 'download')
    return 'contratos.zip'


# ##################################################
# Download CSVs N2
# ##################################################

def download_nra(dbClient, variables=None):

  # Auth
  logger.info('Downloading CSVs N2...')
  clear('download')

  # SQL
  sql = '''
    SELECT
      b.id,
      r."Code",
      substring(r."Registry_num", 11, 14) AS "CRU", 
      r."Registry_num" AS "NRUA",
      CASE 
        WHEN b."id" IS NULL THEN NULL
        WHEN b."Agent_id" IS NULL THEN NULL
        WHEN b."Reason_id" IN (5)    THEN 1 -- Vacacional
        WHEN b."Reason_id" IN (2, 4) THEN 2 -- Laboral
        WHEN b."Reason_id" IN (1, 3) THEN 3 -- Estudios
        ELSE NULL
      END AS "Reason", 
      CASE 
        WHEN b."id" IS NULL THEN NULL
        WHEN b."Agent_id" IS NULL THEN NULL
        ELSE 1
      END AS "Pax",
      CASE 
        WHEN b."id" IS NULL THEN NULL
        WHEN b."Agent_id" IS NULL THEN NULL
        ELSE GREATEST(b."Date_from"::date, make_date(%s, 1, 1))
      END AS "Date_from",
      CASE 
        WHEN b."id" IS NULL THEN NULL
        WHEN b."Agent_id" IS NULL THEN NULL
        ELSE LEAST(b."Date_to"::date, make_date(%s, 12, 31)) 
      END AS "Date_to",
      a."Name"
    FROM "Resource"."Resource" r 
      LEFT JOIN "Booking"."Booking" b ON r."id" = b."Resource_id"
        AND (
          b."Status" IN ('confirmada','firmacontrato','contrato','checkinconfirmado','checkin','inhouse','checkout','devolvergarantia','finalizada','revision')
          AND b."Date_from"::date <= make_date(%s, 12, 31)
          AND b."Date_to"::date   >= make_date(%s, 1, 1)
        )
      LEFT JOIN "Booking"."Customer_reason" cr ON cr."id" = b."Reason_id"
      LEFT JOIN "Provider"."Agent" a ON a."id" = b."Agent_id"
    ORDER BY 3, 2, 1
  '''

  # Capture exceptions
  con = None
  try:

    # Get data
    year = variables['year'] or 2025
    con = dbClient.getconn()
    cur = dbClient.execute(con, sql, (year, year, year, year))
    data = cur.fetchall()
    cur.close()

    # Generate each CSV
    num = 0
    for item in data:

      # Valid NRUA
      nrua = item['NRUA']
      if nrua and len(nrua) == 53:

        # CSV Line
        line = ';'.join([
          nrua, 
          item['Date_from'].strftime('%Y-%m-%d') if item['Date_from'] else '', 
          item['Date_to'].strftime('%Y-%m-%d') if item['Date_to'] else '',
          str(item['Pax']) if item['Pax'] else '',
          str(item['Reason']) if item['Reason'] else '',
        ])

        # Write CSV file
        cru = item['CRU']
        if cru and len(cru) == 14:
          with open('download/n2/' + cru + '.csv', 'a') as csv:
            csv.write(line + '\n')
            num += 1

    # Zip
    if num > 0:
      zip('n2.zip', 'download')
      return 'n2.zip'

  # Error, return
  except Exception as e:
    logger.error(e)
    if con:
      con.rollback()
    return

  finally:
    dbClient.putconn(con)


# ##################################################
# Incasol deposit return declarations (one PDF per booking and owner)
# ##################################################

# Catalan month names for the declaration date
MONTHS_CA = ['de gener', 'de febrer', 'de març', "d'abril", 'de maig', 'de juny',
             'de juliol', "d'agost", 'de setembre', "d'octubre", 'de novembre', 'de desembre']

# B2C and B2B bookings with legal deposit leaving between dates, with owner and first signer
INCASOL_SQL = '''
  WITH bookings AS (
    SELECT
      b.id::text AS "Id",
      r."Owner_id",
      CONCAT_WS(', ', COALESCE(r."Street", f."Street"), COALESCE(f."Address", r."Address"), bu."Zip", l."Name") AS "Address",
      b."Contract_signed"::date AS "Contract_date",
      COALESCE(b."Check_out", b."Date_to")::date AS "Date_to",
      b."Incasol_deposit" AS "Deposit",
      c."Name" AS "Customer_name"
    FROM "Booking"."Booking" b
      INNER JOIN "Resource"."Resource" r ON r.id = b."Resource_id"
      LEFT JOIN "Resource"."Resource" f ON f.id = r."Flat_id"
      INNER JOIN "Building"."Building" bu ON bu.id = r."Building_id"
      LEFT JOIN "Geo"."District" d ON d.id = bu."District_id"
      LEFT JOIN "Geo"."Location" l ON l.id = d."Location_id"
      LEFT JOIN "Customer"."Customer" c ON c.id = b."Customer_id"
    WHERE COALESCE(b."Check_out", b."Date_to") >= %(fdesde)s AND COALESCE(b."Check_out", b."Date_to") < %(fhasta)s
      AND b."Contract_signed" IS NOT NULL
      AND b."Status"::text NOT IN ('cancelada', 'descartada', 'descartadapagada')
      AND COALESCE(b."Incasol_deposit", 0) > 0
    UNION ALL
    SELECT
      'B' || g.id,
      r."Owner_id",
      COALESCE(
        CASE WHEN COUNT(DISTINCT CONCAT_WS(', ', COALESCE(r."Street", f."Street"), COALESCE(f."Address", r."Address"), bu."Zip", l."Name")) = 1
          THEN MIN(CONCAT_WS(', ', COALESCE(r."Street", f."Street"), COALESCE(f."Address", r."Address"), bu."Zip", l."Name")) END,
        CONCAT_WS(', ', MIN(bu."Address"), MIN(bu."Zip"), MIN(l."Name"))
      ),
      g."Contract_signed"::date,
      g."Date_to"::date,
      g."Incasol_deposit",
      MIN(c."Name")
    FROM "Booking"."Booking_group" g
      INNER JOIN "Booking"."Booking_group_rooms" gr ON gr."Booking_id" = g.id
      INNER JOIN "Resource"."Resource" r ON r.id = gr."Resource_id"
      LEFT JOIN "Resource"."Resource" f ON f.id = r."Flat_id"
      INNER JOIN "Building"."Building" bu ON bu.id = r."Building_id"
      LEFT JOIN "Geo"."District" d ON d.id = bu."District_id"
      LEFT JOIN "Geo"."Location" l ON l.id = d."Location_id"
      LEFT JOIN "Customer"."Customer" c ON c.id = g."Payer_id"
    WHERE g."Date_to" >= %(fdesde)s AND g."Date_to" < %(fhasta)s
      AND g."Contract_signed" IS NOT NULL
      AND g."Status"::text NOT IN ('cancelada', 'descartada', 'descartadapagada')
      AND COALESCE(g."Incasol_deposit", 0) > 0
    GROUP BY g.id, r."Owner_id"
  )
  SELECT
    bk.*,
    p."Name" AS "Owner_name",
    p."Document" AS "Owner_document",
    CONCAT_WS(', ', p."Address", p."Zip", p."City") AS "Owner_address",
    p."IBAN" AS "Owner_iban",
    s.id AS "Signer",
    s."Name" AS "Signer_name",
    s."Document" AS "Signer_document",
    it."Name" AS "Signer_id_type"
  FROM bookings bk
    LEFT JOIN "Provider"."Provider" p ON p.id = bk."Owner_id"
    LEFT JOIN LATERAL (
      SELECT pc.id, pc."Name", pc."Document", pc."Id_type_id"
      FROM "Provider"."Provider_contact" pc
      WHERE pc."Provider_id" = p.id AND pc."Provider_contact_type_id" = 1
      ORDER BY pc.id
      LIMIT 1
    ) s ON TRUE
    LEFT JOIN "Auxiliar"."Id_type" it ON it.id = s."Id_type_id"
  ORDER BY bk."Owner_id", bk."Id"
'''


# Format a date as dd/mm/yyyy
def fmt_date(d):
  return d.strftime('%d/%m/%Y') if d else None


# Format an amount with Spanish separators
def fmt_amount(n):
  return '{:,.2f}'.format(n or 0).replace(',', 'X').replace('.', ',').replace('X', '.')


# Signature contrast, as fractions of the paper-ink distance measured below the paper: transparent until, opaque from
SIGNATURE_PAPER = 0.15
SIGNATURE_INK = 0.5


# Lightness (0-255) at the given fraction of the pixels in a histogram
def percentile(histogram, fraction):
  target = sum(histogram) * fraction
  total = 0
  for value, count in enumerate(histogram):
    total += count
    if total >= target:
      return value
  return 255


# Remove the paper background of a signature image, returned as a transparent PNG data URI
def transparent_signature(content):

  # Lightness and original opacity (transparent pixels are left out of the measures)
  image = Image.open(BytesIO(content)).convert('RGBA')
  opacity = image.getchannel('A')
  gray = ImageOps.grayscale(image.convert('RGB'))
  mask = opacity.point(lambda v: 255 if v > 0 else 0)

  # Paper and ink levels of this image: the background is most of it, the ink its darkest pixels
  histogram = gray.histogram(mask=mask)
  paper = percentile(histogram, 0.5)
  ink = percentile(histogram, 0.01)
  contrast = max(paper - ink, 1)

  # Paper transparent, ink fully opaque whatever its colour, short ramp in between for smooth edges
  clear = paper - contrast * SIGNATURE_PAPER
  solid = paper - contrast * SIGNATURE_INK
  ramp = max(clear - solid, 1)
  alpha = gray.point(lambda v: max(0, min(255, round(255 * (clear - v) / ramp))))

  # Keep the original transparency, as is when the background was already transparent (no paper to measure)
  if mask.histogram()[0] > image.width * image.height / 2:
    alpha = opacity
  else:
    alpha = ImageChops.multiply(alpha, opacity)

  # Dark ink colour with the computed transparency
  result = Image.new('RGBA', image.size, (20, 20, 60, 255))
  result.putalpha(alpha)
  out = BytesIO()
  result.save(out, format='PNG')
  return 'data:image/png;base64,' + b64encode(out.getvalue()).decode()


# Generate the Incasol declarations for bookings leaving between dates and zip them
def download_incasol(apiClient, dbClient, variables=None):

  # Init
  logger.info('Generando declaraciones Incasol...')
  clear('download')
  env = Environment(loader=FileSystemLoader('./templates/other'), autoescape=select_autoescape(['html', 'xml']))
  tpl = env.get_template('incasol.html')
  now = date.today()
  today = '{} {} de {}'.format(now.day, MONTHS_CA[now.month - 1], now.year)

  # Get data
  con = None
  try:
    con = dbClient.getconn()
    cur = dbClient.execute(con, INCASOL_SQL, {'fdesde': variables['fdesde'], 'fhasta': variables['fhasta']})
    data = cur.fetchall()
    cur.close()
  except Exception as e:
    logger.error(e)
    if con:
      con.rollback()
    return
  finally:
    dbClient.putconn(con)

  # One PDF per booking and owner
  num = 0
  signatures = {}
  for item in data:

    # Signature image, once per signer
    signer = item['Signer']
    if signer and signer not in signatures:
      signatures[signer] = None
      try:
        image = apiClient.getFile(signer, 'Provider/Provider_contact', 'Signature')
        if image.content:
          signatures[signer] = transparent_signature(image.content)
      except Exception as e:
        logger.warning('Firmante {} sin firma: {}'.format(signer, e))

    # Render (registry and control are blank until the fields exist)
    html = tpl.render(
      registry=None,
      control=None,
      account=item['Owner_iban'],
      signer_name=item['Signer_name'],
      signer_id=item['Signer_document'],
      signer_id_type=item['Signer_id_type'],
      signature=signatures.get(signer),
      owner_name=item['Owner_name'],
      owner_id=item['Owner_document'],
      owner_address=item['Owner_address'],
      address=item['Address'],
      contract_date=fmt_date(item['Contract_date']),
      date_to=fmt_date(item['Date_to']),
      deposit=fmt_amount(item['Deposit']),
      customer_name=item['Customer_name'],
      today=today,
    )

    # File name: Incasol number (placeholder until the field exists), address and booking, safe for the file system
    address = re.sub(r'[\\/:*?"<>|]', '-', str(item['Address'] or '')).strip()
    name = '{} {} {}'.format('XXXXXXXX', address, item['Id'])

    # Same booking with several owners, avoid overwriting
    if os.path.exists('download/' + name + '.pdf'):
      name += ' ' + str(item['Owner_id'])

    # Write PDF
    logger.info(name)
    HTML(string=html).write_pdf('download/' + name + '.pdf')
    num += 1

  # Info
  logger.info('Generadas {} declaraciones Incasol'.format(num))

  # Zip
  if num > 0:
    zip('incasol.zip', 'download')
    return 'incasol.zip'


# ##################################################
# Download
# ##################################################

def do_download(apiClient, dbClient, name, variables=None):

  # Variables
  if variables.get('fdesde') is None:
    variables['fdesde'] = '2023-01-01'
  if variables.get('fhasta') is None:
    variables['fhasta'] = '2099-12-31'
  if variables.get('pdesde') is None:
    variables['pdesde'] = 0
  if variables.get('phasta') is None:
    variables['phasta'] = 99999

  # Contracts
  if name == 'contratos':
    return download_contracts(apiClient, variables)
 
  # Bills
  elif name == 'facturas':
    return download_bills(apiClient, variables)
 
  # Incasol deposit return declarations
  elif name == 'incasol':
    return download_incasol(apiClient, dbClient, variables)

  # CSV N2
  elif name == 'nra':
    return download_nra(dbClient, variables)
 
  # Unknown
  else:
    return None
