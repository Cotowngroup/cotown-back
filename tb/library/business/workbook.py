# ==============================================================================
# library/business/workbook.py
# ------------------------------------------------------------------------------
# TB sheet of a good upload (ticket 09a): the TB rows go into a sheet "TB" of
# the same workbook as the SAP export, after it, so the file of the upload
# keeps the export it came from and the TB it gave. The export sheet stays
# first and unchanged, so the file can be processed again, which replaces the
# TB sheet. No input/output: bytes in, bytes out.
#
# Copyright Oimbra Technology 2026
# ==============================================================================

# Standard libraries
from io import BytesIO

# Third-party libraries
import openpyxl
import pandas as pd
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

# Application libraries
from library.business.schema import OUTPUT_COLUMNS

# Name of the sheet with the TB rows
TB_SHEET = 'TB'

# Format of the sheet: bold grey header with the filter, frozen; amounts with 2 decimals
HEADER_FONT = Font(bold=True)
HEADER_FILL = PatternFill('solid', fgColor='FFDFDFDF')
HEADER_BORDER = Border(bottom=Side(style='thin'))
HEADER_ALIGNMENT = Alignment(vertical='center')
AMOUNT_FORMAT = '#,##0.00'

# Column widths, in characters, by column; the rest keep the default
WIDTHS = {
    'empresa': 9,
    'cuenta': 9,
    'servicio': 12,
    'descripcion': 40,
    'asset': 10,
    'categoria': 40,
    'ccaa1': 12,
    'ccaa2': 30,
    'budget': 8,
    'clave': 70,
    'mes': 9,
    'importe': 14,
}


# Add the TB rows to the export workbook as its sheet TB, replacing the one of a previous processing
def add_tb_sheet(content: bytes, rows: pd.DataFrame) -> bytes:
    book = openpyxl.load_workbook(BytesIO(content))
    if TB_SHEET in book.sheetnames:
        del book[TB_SHEET]
    sheet = book.create_sheet(TB_SHEET)

    # Header, then one row per TB row; an empty budget stays an empty cell
    sheet.append(OUTPUT_COLUMNS)
    for values in rows[OUTPUT_COLUMNS].itertuples(index=False):
        sheet.append([None if pd.isna(value) else value for value in values])

    # Format: header, amounts, widths, filter and frozen header
    for cell in sheet[1]:
        cell.font, cell.fill, cell.border, cell.alignment = HEADER_FONT, HEADER_FILL, HEADER_BORDER, HEADER_ALIGNMENT
    amount_column = OUTPUT_COLUMNS.index('importe') + 1
    for (cell,) in sheet.iter_rows(min_row=2, min_col=amount_column, max_col=amount_column):
        cell.number_format = AMOUNT_FORMAT
    for index, column in enumerate(OUTPUT_COLUMNS, start=1):
        sheet.column_dimensions[get_column_letter(index)].width = WIDTHS[column]
    sheet.auto_filter.ref = sheet.dimensions
    sheet.freeze_panes = 'A2'
    stream = BytesIO()
    book.save(stream)
    return stream.getvalue()
