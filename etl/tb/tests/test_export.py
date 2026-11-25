# ==============================================================================
# tests/test_export.py
# ------------------------------------------------------------------------------
# Unit tests of the SAP export reader. Each test builds the workbook in memory
# with the layout of the real export (title rows, header row, code + text
# columns, one column per period, Resultado) and reads it back.
#
# Copyright Oimbra Technology 2026
# ==============================================================================

# Standard libraries
from io import BytesIO

# Third-party libraries
import openpyxl
import pytest

# Application libraries
from tb.errors import ReadError
from tb.export import read_export

# Header row of the real export, column B onwards; '' is the text column of the dimension before it
SAP_HEADER = (
    'Empresa',
    '',
    'Cuenta de mayor',
    '',
    'Tipo de cuenta de mayor',
    'Producto',
    '',
    'Categoría de producto',
    '',
    'Centro de beneficio',
    '',
    'Centro de coste',
    'Período/año contable',
)

# Two data lines of the real export, without the period amounts
SAP_LINES = [
    [
        'CTS00',
        'COTOWN SHARING LIFE S.L.',
        '705000',
        'PRESTACIONES DE SERVICIOS',
        'Ingresos o ganancias',
        'S_70504',
        'LIMPIEZA CHECK OUT',
        'S_PS',
        'Prestaciones de servicios',
        'CTSBCNBAI0033_04.01',
        '4º 1ª',
        '#',
        'Sin asignar',
    ],
    [
        'CTS00',
        'COTOWN SHARING LIFE S.L.',
        '280000',
        'AMORT. ACUM. INMOVILIZADO INTANGIBLE',
        'Activos fijos',
        '#',
        'Sin asignar',
        '#',
        'Sin asignar',
        'CTS01',
        'COTOWN SHARING LIFE SL RF',
        '#',
        'Sin asignar',
    ],
]


# Export workbook in memory: SAP title rows, the header row and one row per line with its period amounts
def build_sap_export(periods: list[str], amounts: list[list], header: tuple[str, ...] = SAP_HEADER) -> BytesIO:
    book = openpyxl.Workbook()
    sheet = book.active
    sheet.append([None, 'Trial Balance'])
    sheet.append([])
    sheet.append([None, 'Empresa', 'CTS00 (COTOWN SHARING LIFE S.L.)'])
    sheet.append([None, '', '', '', 'Importe en moneda de empresa'])
    sheet.append([None, *header, *periods, 'Resultado'])
    for values, line_amounts in zip(SAP_LINES, amounts, strict=True):
        sheet.append([None, *values, *line_amounts, None])
    stream = BytesIO()
    book.save(stream)
    stream.seek(0)
    return stream


# Each line and period becomes a canonical row; codes and texts are read by column name, empty amounts are 0
def test_reads_lines_and_periods_into_canonical_rows():
    stream = build_sap_export(['008.2026', '009.2026'], [[-132.26, ''], [-7220, -6981]])

    export = read_export(stream)

    assert export.to_dict('records') == [
        {
            'empresa': 'CTS00',
            'cuenta': '705000',
            'texto_cuenta': 'PRESTACIONES DE SERVICIOS',
            'producto': 'S_70504',
            'texto_producto': 'LIMPIEZA CHECK OUT',
            'centro_beneficio': 'CTSBCNBAI0033_04.01',
            'mes': '2026-08',
            'importe': -132.26,
        },
        {
            'empresa': 'CTS00',
            'cuenta': '705000',
            'texto_cuenta': 'PRESTACIONES DE SERVICIOS',
            'producto': 'S_70504',
            'texto_producto': 'LIMPIEZA CHECK OUT',
            'centro_beneficio': 'CTSBCNBAI0033_04.01',
            'mes': '2026-09',
            'importe': 0.0,
        },
        {
            'empresa': 'CTS00',
            'cuenta': '280000',
            'texto_cuenta': 'AMORT. ACUM. INMOVILIZADO INTANGIBLE',
            'producto': '#',
            'texto_producto': 'Sin asignar',
            'centro_beneficio': 'CTS01',
            'mes': '2026-08',
            'importe': -7220.0,
        },
        {
            'empresa': 'CTS00',
            'cuenta': '280000',
            'texto_cuenta': 'AMORT. ACUM. INMOVILIZADO INTANGIBLE',
            'producto': '#',
            'texto_producto': 'Sin asignar',
            'centro_beneficio': 'CTS01',
            'mes': '2026-09',
            'importe': -6981.0,
        },
    ]


# An export with a single period is read the same way
def test_reads_single_period():
    stream = build_sap_export(['009.2026'], [[-314.04], [None]])

    export = read_export(stream)

    assert export[['cuenta', 'mes', 'importe']].to_dict('records') == [
        {'cuenta': '705000', 'mes': '2026-09', 'importe': -314.04},
        {'cuenta': '280000', 'mes': '2026-09', 'importe': 0.0},
    ]


# A file that is not an SAP export reports every missing piece at once
def test_missing_columns_and_periods_are_reported():
    header = tuple(name if name != 'Producto' else 'Material' for name in SAP_HEADER)
    stream = build_sap_export([], [[], []], header=header)

    with pytest.raises(ReadError) as raised:
        read_export(stream)

    assert len(raised.value.errors) == 2
    assert 'Producto' in raised.value.errors[0]
    assert 'NNN.AAAA' in raised.value.errors[1]


# Without the 'Cuenta de mayor' header row the file is not an SAP export
def test_missing_header_row_is_reported():
    book = openpyxl.Workbook()
    book.active.append(['Otra cosa'])
    stream = BytesIO()
    book.save(stream)
    stream.seek(0)

    with pytest.raises(ReadError) as raised:
        read_export(stream)

    assert raised.value.errors == [
        'No se encuentra la fila de cabecera con "Cuenta de mayor": no parece un export de SAP.',
    ]
