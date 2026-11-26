# ==============================================================================
# tb/sap.py
# ------------------------------------------------------------------------------
# Generator of the Trial Balance export from the general ledger of SAP
# (ticket 08). It takes the OData records of the general ledger report and
# the masters that report lacks (product category, responsible unit of the
# project task), and builds a workbook with the same columns, order and
# format as the Trial Balance export done by hand in SAP: title, selection
# block, three header rows, one row per company + account + product + project
# task + profit centre + cost centre, one NNN.AAAA column per period and the
# result. The product code is CPRODUCT_UUID (TPRODUCT_UUID is its text, in
# Spanish with sap-language=ES) and the balance carry-forward (document type
# 00058) is left out. No input/output: the records come from the caller.
#
# Copyright Oimbra Technology 2026
# ==============================================================================

# Standard libraries
import textwrap
from io import BytesIO
from typing import NamedTuple

# Third-party libraries
import openpyxl
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.utils.indexed_list import IndexedList
from openpyxl.worksheet.dimensions import ColumnDimension

# Application libraries
from tb.errors import ReadError
from tb.export import TITLE_MARK, period_header

# Fields of the general ledger report that the generator needs, for the OData $select
SAP_FIELDS = [
    'CFISCYEAR',
    'CFISCPER',
    'CACCDOCTYPE',
    'CCOMPANY_UUID',
    'TCOMPANY_UUID',
    'CGLACCT',
    'TGLACCT',
    'TGLACCT_TC',
    'CPRODUCT_UUID',
    'TPRODUCT_UUID',
    'CPROJ_TASK_UUID',
    'TPROJ_TASK_UUID',
    'CPROFITCTR_UUID',
    'TPROFITCTR_UUID',
    'CCOST_CTR_UUID',
    'TCOST_CTR_UUID',
    'KCBALANCE_CURRCOMP',
]

# Document type of the balance carry-forward at the start of the year: it does not go to the TB
CARRY_FORWARD = '00058'

# Code and text of an unassigned dimension, as in the export done by hand
UNASSIGNED = ('#', 'Sin asignar')

# Codes with which SAP means a dimension is not assigned
UNASSIGNED_CODES = {'', '#', 'Not Assigned', 'No asignado'}

# Header of the dimension columns from B, as in the export: a dimension takes its code and its text (empty header),
# the account type only its text; the last header goes over the text of the cost centre
HEADERS = [
    'Empresa', '',
    'Cuenta de mayor', '',
    'Tipo de cuenta de mayor',
    'Producto', '',
    'Categoría de producto', '',
    'Tarea de proyecto', '',
    'Unidad responsable de proyecto', '',
    'Centro de beneficio', '',
    'Centro de coste', '',
]

# Positions of the codes in the dimension cells, in the order in which the export sorts its rows
CODE_POSITIONS = [0, 2, 5, 7, 9, 11, 13, 15]

# Header texts above the period columns and over the text column of the last dimension
AMOUNT_TITLE = 'Importe en moneda de empresa'
YEAR_TITLE = 'Año (Fecha de contabilización)'
PERIOD_TITLE = 'Período/año contable'
RESULT_TITLE = 'Resultado'

# Format of the export: fonts, fills, borders and number formats of the SAP export
FIRST_COLUMN = 2
DEFAULT_FONT = Font(name='Calibri', sz=10, family=2, scheme='minor')
TITLE_FONT = Font(name='Arial', size=20, bold=True)
TEXT_FONT = Font(name='Arial', size=12)
BOLD_FONT = Font(name='Arial', size=12, bold=True)
WHITE = PatternFill('solid', fgColor='FFFFFFFF')
GREY = PatternFill('solid', fgColor='FFDFDFDF')
THIN = Side(style='thin')
HAIR = Side(style='hair')
TITLE_BORDER = Border(top=THIN, bottom=THIN)
GRID_BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)
AMOUNT_BORDER = Border(left=HAIR, right=HAIR, top=HAIR, bottom=HAIR)
RESULT_BORDER = Border(left=HAIR, right=THIN, top=HAIR, bottom=HAIR)
RESULT_HEADER_BORDER = Border(left=HAIR, right=THIN, top=HAIR, bottom=THIN)
WRAP = Alignment(vertical='center', wrap_text=True)
AMOUNT_ALIGNMENT = Alignment(horizontal='right', vertical='center', wrap_text=True)
LEFT = Alignment(horizontal='left')
MONEY = '#,##0.00\\ "EUR"'
NO_AMOUNT = '#,##0'

# Column widths of the export: margins around the table, every column of the table, last column of a sheet
MARGIN_WIDTH = 2.6640625
COLUMN_WIDTH = 27.6640625
MAX_COLUMN = 16384

# Row height of the export: 15 points per line of the widest wrapped text, at least two lines
LINE_HEIGHT = 15
WRAP_CHARACTERS = 20
MIN_LINES = 2


# Masters that the general ledger report lacks: product -> product category, project task -> responsible unit
class Masters(NamedTuple):
    product_categories: dict[str, tuple[str, str]]
    responsible_units: dict[str, tuple[str, str]]


# Selection block of the export: books, user and generation time, as SAP writes them
class Selection(NamedTuple):
    empresa: str
    sistema_contable: str
    usuario: str
    generado: str


# Code and text of a dimension of a record, unassigned when SAP has no code
def _dimension(item: dict, code_field: str, text_field: str) -> tuple[str, str]:
    code = item[code_field]
    return UNASSIGNED if code in UNASSIGNED_CODES else (code, item[text_field])


# Cells of the dimension columns of a record, from column B
def _dimension_cells(item: dict, masters: Masters) -> list[str]:
    product = _dimension(item, 'CPRODUCT_UUID', 'TPRODUCT_UUID')
    task = _dimension(item, 'CPROJ_TASK_UUID', 'TPROJ_TASK_UUID')
    category = masters.product_categories.get(product[0], UNASSIGNED if product == UNASSIGNED else ('', ''))
    unit = masters.responsible_units.get(task[0], UNASSIGNED)
    return [
        *_dimension(item, 'CCOMPANY_UUID', 'TCOMPANY_UUID'),
        *_dimension(item, 'CGLACCT', 'TGLACCT'),
        item['TGLACCT_TC'],
        *product,
        *category,
        *task,
        *unit,
        *_dimension(item, 'CPROFITCTR_UUID', 'TPROFITCTR_UUID'),
        *_dimension(item, 'CCOST_CTR_UUID', 'TCOST_CTR_UUID'),
    ]


# Order of the export: by codes, an unassigned code after the assigned ones
def _sort_key(cells: list[str]) -> tuple:
    return tuple((cells[position] == UNASSIGNED[0], cells[position]) for position in CODE_POSITIONS)


# Style one cell
def _style(cell, font=None, fill=None, border=None, alignment=None, number_format=None) -> None:
    for name, value in (('font', font), ('fill', fill), ('border', border), ('alignment', alignment)):
        if value is not None:
            setattr(cell, name, value)
    if number_format is not None:
        cell.number_format = number_format


# Height of a data row: the widest wrapped text of its dimension cells
def _row_height(cells: list[str]) -> float:
    lines = max(len(textwrap.wrap(text, WRAP_CHARACTERS)) or 1 for text in cells[1:])
    return LINE_HEIGHT * max(MIN_LINES, lines)


# Build the export workbook of one company and the given months (AAAA-MM) from general ledger records
def build_export(records: list[dict], months: list[str], selection: Selection, masters: Masters) -> bytes:
    # Sum by line, one amount per month; a month without postings stays empty, a month netting 0 is 0
    lines: dict[tuple, dict[str, float]] = {}
    for item in records:
        if item['CACCDOCTYPE'] == CARRY_FORWARD:
            continue
        month = f'{item['CFISCYEAR']}-{int(item['CFISCPER']):02d}'
        amounts = lines.setdefault(tuple(_dimension_cells(item, masters)), {})
        amounts[month] = amounts.get(month, 0.0) + float(item['KCBALANCE_CURRCOMP'])

    # Every month asked for has records: an empty month is a wrong period or company, not a month at 0
    found = {month for amounts in lines.values() for month in amounts}
    missing = [month for month in months if month not in found]
    if missing:
        raise ReadError(
            [
                f'SAP no tiene apuntes de {selection.empresa} en {month}: revisa el periodo o la sociedad.'
                for month in missing
            ],
        )

    # Columns: the dimensions from B, then one per period, the result, a spacer and a hidden column
    first_period = FIRST_COLUMN + len(HEADERS)
    result_column = first_period + len(months)
    last_column = result_column
    book = openpyxl.Workbook()
    book._fonts = IndexedList([DEFAULT_FONT])
    sheet = book.active
    sheet.title = f'Exportac. {selection.generado[:19].replace(':', '.')}'
    book.properties.creator = selection.usuario

    # Title, merged over the whole table
    title = sheet.cell(1, FIRST_COLUMN, TITLE_MARK)
    _style(title, TITLE_FONT, WHITE, TITLE_BORDER, Alignment(vertical='center', wrap_text=True))
    for column in range(FIRST_COLUMN + 1, last_column + 1):
        sheet.cell(1, column).border = TITLE_BORDER
    sheet.merge_cells(start_row=1, start_column=FIRST_COLUMN, end_row=1, end_column=last_column)
    sheet.row_dimensions[1].height = 79.95

    # Selection block
    company_text = next((cells[1] for cells in lines), '')
    periods = '; '.join(f'{period_header(month)} ({period_header(month)})' for month in months)
    block = {
        3: ('Enviados a: ', selection.generado),
        4: ('Datos basados usuario: ', selection.usuario),
        5: ('Código contexto de acceso: ', '* (Sin restricciones)'),
        7: ('Selección:', None),
        8: ('Sistema contable', selection.sistema_contable),
        9: ('Empresa', f'{selection.empresa} ({company_text})'),
        10: ('Período/año contable (Asiento contable)', periods),
    }
    for row, values in block.items():
        for offset, value in enumerate(values):
            if value is not None:
                cell = sheet.cell(row, FIRST_COLUMN + offset, value)
                _style(cell, TEXT_FONT, WHITE, alignment=LEFT if row in (3, 7) else None)
        sheet.row_dimensions[row].height = LINE_HEIGHT

    # Header rows: amount title, year of each period, dimension and period names
    for row in (12, 13, 14):
        for column in range(FIRST_COLUMN, result_column):
            _style(sheet.cell(row, column, ''), TEXT_FONT, GREY, GRID_BORDER, WRAP)
    sheet.cell(12, first_period, AMOUNT_TITLE)
    sheet.merge_cells(start_row=12, start_column=first_period, end_row=12, end_column=result_column)
    sheet.cell(13, first_period - 1, YEAR_TITLE)
    years: dict[str, list[int]] = {}
    for index, month in enumerate(months):
        years.setdefault(month[:4], []).append(first_period + index)
    for year, columns in years.items():
        end = result_column if columns[-1] == result_column - 1 else columns[-1]
        sheet.cell(13, columns[0], year)
        if end > columns[0]:
            sheet.merge_cells(start_row=13, start_column=columns[0], end_row=13, end_column=end)
    for offset, name in enumerate([*HEADERS[:-1], PERIOD_TITLE, *(period_header(month) for month in months)]):
        sheet.cell(14, FIRST_COLUMN + offset, name)
    for row in (12, 13):
        sheet.cell(row, result_column).border = Border(right=THIN, top=THIN, bottom=THIN)
    result = sheet.cell(14, result_column, RESULT_TITLE)
    _style(result, BOLD_FONT, WHITE, RESULT_HEADER_BORDER, Alignment(horizontal='left', vertical='center',
                                                                       wrap_text=True), '@')
    for row in (13, 14):
        sheet.row_dimensions[row].height = LINE_HEIGHT * MIN_LINES

    # One row per line in the order of the export; an empty month is an empty text cell, as SAP writes it
    for row, cells in enumerate(sorted(lines, key=_sort_key), start=15):
        amounts = lines[cells]
        for offset, value in enumerate(cells):
            _style(sheet.cell(row, FIRST_COLUMN + offset, value), TEXT_FONT, GREY, GRID_BORDER, WRAP)
        for offset, month in enumerate(months):
            amount = round(amounts[month], 2) if month in amounts else ''
            cell = sheet.cell(row, first_period + offset, amount)
            _style(cell, TEXT_FONT, None, AMOUNT_BORDER, AMOUNT_ALIGNMENT, MONEY if month in amounts else NO_AMOUNT)
        total = sheet.cell(row, result_column, round(sum(amounts.values()), 2))
        _style(total, BOLD_FONT, WHITE, RESULT_BORDER, AMOUNT_ALIGNMENT, MONEY)
        sheet.row_dimensions[row].height = _row_height(list(cells))

    # Columns: narrow margins, every column of the table wide, the rest of the sheet hidden; filter over the table
    for first, last, width, hidden in (
        (1, 1, MARGIN_WIDTH, False),
        (FIRST_COLUMN, last_column, COLUMN_WIDTH, False),
        (last_column + 1, last_column + 1, MARGIN_WIDTH, False),
        (last_column + 2, MAX_COLUMN, 0, True),
    ):
        sheet.column_dimensions[get_column_letter(first)] = ColumnDimension(
            sheet, index=get_column_letter(first), min=first, max=last, width=width, hidden=hidden,
        )
    sheet.auto_filter.ref = f'{get_column_letter(FIRST_COLUMN)}12:{get_column_letter(last_column)}{sheet.max_row}'
    sheet.sheet_format.baseColWidth = 10
    sheet.sheet_format.defaultColWidth = 0
    stream = BytesIO()
    book.save(stream)
    return stream.getvalue()
