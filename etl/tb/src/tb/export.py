# ==============================================================================
# tb/export.py
# ------------------------------------------------------------------------------
# Reader of the SAP Trial Balance export (xlsx, as it comes out of SAP). It
# returns the canonical input of the transformation: one row per line and
# month (spec decision 7). The file is read by column name: the header row is
# the one with "Cuenta de mayor", a dimension's text is the unnamed column
# after its code, and the periods are the NNN.AAAA columns. Takes a binary
# stream, so the file can come from disk or from Airflows.
#
# Copyright Oimbra Technology 2026
# ==============================================================================

# Standard libraries
import re
from typing import BinaryIO

# Third-party libraries
import openpyxl
import pandas as pd

# Application libraries
from tb.errors import ReadError

# Header cell that identifies the column header row of the export
HEADER_MARK = 'Cuenta de mayor'

# Period column header: NNN.AAAA, e.g. 008.2026
PERIOD_PATTERN = re.compile(r'^(?P<period>\d{3})\.(?P<year>\d{4})$')

# Canonical columns taken from the export: (output column, export header, whether it is the text column)
DIMENSIONS = [
    ('empresa', 'Empresa', False),
    ('cuenta', 'Cuenta de mayor', False),
    ('texto_cuenta', 'Cuenta de mayor', True),
    ('producto', 'Producto', False),
    ('texto_producto', 'Producto', True),
    ('centro_beneficio', 'Centro de beneficio', False),
]


# Turn a code or text cell into a string: integers without .0, None as empty
def _as_text(value: object) -> str:
    if value is None:
        return ''
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value).strip()


# Read the SAP export into canonical rows
def read_export(source: BinaryIO) -> pd.DataFrame:
    # Every cell of the first sheet, where SAP writes the export
    book = openpyxl.load_workbook(source, read_only=True, data_only=True)
    cells = list(book.worksheets[0].iter_rows(values_only=True))
    book.close()

    # Header row: the one with "Cuenta de mayor"
    header_index = next((i for i, row in enumerate(cells) if HEADER_MARK in [_as_text(v) for v in row]), None)
    if header_index is None:
        raise ReadError([f'No se encuentra la fila de cabecera con "{HEADER_MARK}": no parece un export de SAP.'])
    header = [_as_text(value) for value in cells[header_index]]
    errors = []

    # Dimension columns by name; the text is the next column when its header is empty
    positions = {}
    for column, name, is_text in DIMENSIONS:
        if name not in header:
            if not is_text:
                errors.append(f'Falta la columna "{name}" en la cabecera del export.')
            continue
        position = header.index(name) + 1 if is_text else header.index(name)
        if is_text and (position >= len(header) or header[position]):
            errors.append(f'Falta la columna de texto que sigue a "{name}" en el export.')
            continue
        positions[column] = position

    # Period columns: NNN.AAAA becomes AAAA-MM
    periods = {}
    for position, name in enumerate(header):
        match = PERIOD_PATTERN.match(name)
        if match and 1 <= int(match['period']) <= 12:
            periods[position] = f'{match['year']}-{match['period'][1:]}'
        elif match:
            errors.append(f'El periodo {name} no es un mes (001 a 012): exporta solo periodos mensuales.')
    if not periods:
        errors.append('No hay columnas de periodo (NNN.AAAA) en el export.')
    if errors:
        raise ReadError(errors)

    # One canonical row per line with a company and period; empty amounts are 0
    rows = []
    for row_number, row in enumerate(cells[header_index + 1:], start=header_index + 2):
        values = {column: _as_text(row[position]) for column, position in positions.items()}
        if not values['empresa']:
            continue
        for position, month in periods.items():
            amount = row[position]
            if amount is None or amount == '':
                amount = 0.0
            elif not isinstance(amount, int | float):
                errors.append(f'Importe no numérico en la fila {row_number}, periodo {header[position]}: "{amount}".')
                continue
            rows.append({**values, 'mes': month, 'importe': float(amount)})
    if errors:
        raise ReadError(errors)
    return pd.DataFrame(rows, columns=[column for column, _, _ in DIMENSIONS] + ['mes', 'importe'])
