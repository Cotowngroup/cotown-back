# ==============================================================================
# tb/sap.py
# ------------------------------------------------------------------------------
# Generator of the Trial Balance export from the general ledger of SAP
# (ticket 08). It takes the OData records of the general ledger report and
# builds a workbook with the same layout as the export done by hand in SAP
# (title, header row with code + text columns, one NNN.AAAA column per
# period), so the upload is processed exactly like a manual one. The
# product code is CPRODUCT_UUID (TPRODUCT_UUID is its text, in Spanish with
# sap-language=ES) and the balance carry-forward (document type 00058) is left
# out. No input/output: the records come from the caller.
#
# Copyright Oimbra Technology 2026
# ==============================================================================

# Standard libraries
from io import BytesIO

# Third-party libraries
import openpyxl

# Application libraries
from tb.errors import ReadError
from tb.export import DIMENSIONS, TITLE_MARK, period_header

# Fields of the general ledger report that the generator needs, for the OData $select
SAP_FIELDS = [
    'CFISCYEAR',
    'CFISCPER',
    'CACCDOCTYPE',
    'CGLACCT',
    'TGLACCT',
    'CPRODUCT_UUID',
    'TPRODUCT_UUID',
    'CPROFITCTR_UUID',
    'KCBALANCE_CURRCOMP',
]

# Document type of the balance carry-forward at the start of the year: it does not go to the TB
CARRY_FORWARD = '00058'

# Product code and text of a line without product, as in the export done by hand
NO_PRODUCT = ('#', 'Sin asignar')

# Product codes with which SAP means there is no product
NO_PRODUCT_CODES = {'', '#', 'Not Assigned', 'No asignado'}

# Header row of the export, from column B: each dimension the reader uses, its text column with an empty header
HEADER = [name if not is_text else '' for _, name, is_text in DIMENSIONS]


# Build the export workbook of one company and the given months (AAAA-MM) from general ledger records
def build_export(records: list[dict], empresa: str, months: list[str]) -> bytes:
    # Sum by line: account, product and profit centre, with their texts; one amount per month
    lines: dict[tuple, dict[str, float]] = {}
    for item in records:
        if item['CACCDOCTYPE'] == CARRY_FORWARD:
            continue
        month = f'{item['CFISCYEAR']}-{int(item['CFISCPER']):02d}'
        has_product = item['CPRODUCT_UUID'] not in NO_PRODUCT_CODES
        product = (item['CPRODUCT_UUID'], item['TPRODUCT_UUID']) if has_product else NO_PRODUCT
        line = (item['CGLACCT'], item['TGLACCT'], *product, item['CPROFITCTR_UUID'])
        amounts = lines.setdefault(line, {})
        amounts[month] = amounts.get(month, 0.0) + float(item['KCBALANCE_CURRCOMP'])

    # Every month asked for has records: an empty month is a wrong period or company, not a month at 0
    found = {month for amounts in lines.values() for month in amounts}
    missing = [month for month in months if month not in found]
    if missing:
        raise ReadError(
            [f'SAP no tiene apuntes de {empresa} en {month}: revisa el periodo o la sociedad.' for month in missing],
        )

    # Workbook with the layout of the SAP export: title rows, header row, one row per line
    book = openpyxl.Workbook()
    sheet = book.active
    sheet.append([None, TITLE_MARK])
    sheet.append([])
    sheet.append([None, *HEADER, *(period_header(month) for month in months), 'Resultado'])
    for (account, account_text, product, product_text, centre), amounts in lines.items():
        row_amounts = [round(amounts.get(month, 0.0), 2) for month in months]
        sheet.append([None, empresa, account, account_text, product, product_text, centre, *row_amounts, None])
    stream = BytesIO()
    book.save(stream)
    return stream.getvalue()
