# ==============================================================================
# tests/test_sap.py
# ------------------------------------------------------------------------------
# Unit tests of the generator of the Trial Balance export from the general
# ledger of SAP (ticket 08): the workbook it builds from OData records and
# masters must have the columns, order and format of the export done by hand,
# and be read by the export reader as the lines of those records.
#
# Copyright Oimbra Technology 2026
# ==============================================================================

# Standard libraries
import json
from io import BytesIO
from pathlib import Path

# Third-party libraries
import openpyxl
import pytest

# Application libraries
from library.business.errors import ReadError
from library.business.export import read_export
from library.business.maestro import read_maestro
from library.business.run import transform_and_validate
from library.business.sap import Masters, Selection, build_export

# Folder of the tb package, where the master workbook and the data live
TB_DIR = Path(__file__).resolve().parents[1]

# Selection block of the tests, as in the export done by hand
SELECTION = Selection('CTS00', 'ES02 (Sistema Contable Gestora ES)', 'Georgina González', '21.10.2026 12:15:22 WET')

# Masters of the tests: one service with its category, one project task with its responsible unit
MASTERS = Masters(
    product_categories={'S_70504': ('S_PS', 'Prestaciones de servicios')},
    responsible_units={'CTSBCNBAI0033': ('CTSBCNBAI0033', 'Bailén 33')},
)


# One OData record of the general ledger report, as SAP returns it (every value is text)
def record(
    account: str,
    product: str,
    centre: str,
    amount: str,
    period: str = '8',
    doc_type: str = '00009',
    product_text: str = '',
    task: str = '',
) -> dict:
    return {
        'CFISCYEAR': '2026',
        'CFISCPER': period,
        'CACCDOCTYPE': doc_type,
        'CCOMPANY_UUID': 'CTS00',
        'TCOMPANY_UUID': 'COTOWN SHARING LIFE S.L.',
        'CGLACCT': account,
        'TGLACCT': f'CUENTA {account}',
        'TGLACCT_TC': 'Ingresos o ganancias',
        'CPRODUCT_UUID': product,
        'TPRODUCT_UUID': product_text or ('No asignado' if not product else f'TEXTO {product}'),
        'CPROJ_TASK_UUID': task,
        'TPROJ_TASK_UUID': f'TAREA {task}' if task else 'No asignado',
        'CPROFITCTR_UUID': centre,
        'TPROFITCTR_UUID': f'CENTRO {centre}',
        'CCOST_CTR_UUID': '',
        'TCOST_CTR_UUID': 'No asignado',
        'KCBALANCE_CURRCOMP': amount,
    }


# Workbook built from the records
def build(records: list[dict], months: list[str]) -> bytes:
    return build_export(records, months, SELECTION, MASTERS)


# Canonical rows of the generated workbook, as the batch would read them
def read(records: list[dict], months: list[str]) -> list[dict]:
    return read_export(BytesIO(build(records, months))).to_dict('records')


# Cells of the data rows of the generated workbook, from column B
def data_rows(records: list[dict], months: list[str]) -> list[list]:
    sheet = openpyxl.load_workbook(BytesIO(build(records, months))).worksheets[0]
    return [list(row) for row in sheet.iter_rows(min_row=13, min_col=2, values_only=True)]


# Records of the same line are summed; the product code comes from CPRODUCT_UUID, its text from TPRODUCT_UUID
def test_records_of_a_line_are_summed_with_code_and_texts():
    records = [
        record('705000', 'S_70504', 'CTSBCNBAI0033_04.01', '-100.25', product_text='LIMPIEZA CHECK OUT'),
        record('705000', 'S_70504', 'CTSBCNBAI0033_04.01', '-32.01', product_text='LIMPIEZA CHECK OUT'),
    ]

    assert read(records, ['2026-08']) == [
        {
            'empresa': 'CTS00',
            'cuenta': '705000',
            'texto_cuenta': 'CUENTA 705000',
            'producto': 'S_70504',
            'texto_producto': 'LIMPIEZA CHECK OUT',
            'centro_beneficio': 'CTSBCNBAI0033_04.01',
            'mes': '2026-08',
            'importe': -132.26,
        },
    ]


# Every column of the export: dimensions with code and text, the master ones from the masters, unassigned as #
def test_row_has_every_column_of_the_export():
    rows = data_rows([record('705000', 'S_70504', 'CTSBCNBAI0033', '-10', task='CTSBCNBAI0033')], ['2026-08'])

    assert rows == [
        [
            'CTS00', 'COTOWN SHARING LIFE S.L.',
            '705000', 'CUENTA 705000',
            'Ingresos o ganancias',
            'S_70504', 'TEXTO S_70504',
            'S_PS', 'Prestaciones de servicios',
            'CTSBCNBAI0033', 'TAREA CTSBCNBAI0033',
            'CTSBCNBAI0033', 'Bailén 33',
            'CTSBCNBAI0033', 'CENTRO CTSBCNBAI0033',
            '#', 'Sin asignar',
            -10, -10,
        ],
    ]


# A line without product (empty code, or SAP's own markers for it) is '#' with 'Sin asignar', also its category
@pytest.mark.parametrize('code', ['', '#', 'Not Assigned', 'No asignado'])
def test_line_without_product_is_hash(code):
    row = data_rows([record('280000', code, 'CTS01', '-7220')], ['2026-08'])[0]

    assert row[5:9] == ['#', 'Sin asignar', '#', 'Sin asignar']


# The balance carry-forward of the year (document type 00058) does not go to the TB
def test_balance_carry_forward_is_left_out():
    records = [
        record('129000', '', 'CTS01', '1500', period='1', doc_type='00058'),
        record('555800', '', 'CTS01', '-1500', period='1', doc_type='00058'),
        record('705000', 'S_70504', 'CTS01', '-10', period='1'),
        record('430000', '', 'CTS01', '10', period='1'),
    ]

    rows = read(records, ['2026-01'])

    assert [(row['cuenta'], row['importe']) for row in rows] == [('430000', 10.0), ('705000', -10.0)]


# Rows go in the order of the export: by codes, an unassigned code after the assigned ones
def test_rows_are_sorted_by_code_with_unassigned_last():
    records = [
        record('705000', '', 'CTS01', '-1'),
        record('705000', 'S_70504', 'CTS01', '-2'),
        record('430000', 'S_70504', 'CTS01', '3'),
    ]

    rows = data_rows(records, ['2026-08'])

    assert [(row[2], row[5]) for row in rows] == [('430000', 'S_70504'), ('705000', 'S_70504'), ('705000', '#')]


# Several months: one period column each; a month without postings is empty, and the result sums the months
def test_several_months_are_period_columns_with_result():
    records = [
        record('705000', 'S_70504', 'CTS01', '-10', period='8'),
        record('705000', 'S_70504', 'CTS01', '-20', period='9'),
        record('430000', '', 'CTS01', '10', period='8'),
    ]

    rows = data_rows(records, ['2026-08', '2026-09'])

    assert [(row[2], row[17:]) for row in rows] == [('430000', [10, None, 10]), ('705000', [-10, -20, -30])]
    assert [(row['cuenta'], row['mes'], row['importe']) for row in read(records, ['2026-08', '2026-09'])] == [
        ('430000', '2026-08', 10.0),
        ('430000', '2026-09', 0.0),
        ('705000', '2026-08', -10.0),
        ('705000', '2026-09', -20.0),
    ]


# A month asked for without any record is an error, not an empty month
def test_month_without_records_is_an_error():
    with pytest.raises(ReadError) as raised:
        build([record('705000', 'S_70504', 'CTS01', '-10', period='8')], ['2026-08', '2026-09'])

    assert raised.value.errors == ['SAP no tiene apuntes de CTS00 en 2026-09: revisa el periodo o la sociedad.']


# General ledger of August and September 2026 from SAP, with the masters, as saved from SAP
def august_and_september() -> bytes:
    records = [
        item
        for month in ('08', '09')
        for item in json.loads((TB_DIR / 'data' / f'sap_gl_CTS00_2026-{month}.json').read_text(encoding='utf-8'))
    ]
    masters = json.loads((TB_DIR / 'data' / 'sap_maestros_2026-09.json').read_text(encoding='utf-8'))
    return build_export(
        records,
        ['2026-08', '2026-09'],
        SELECTION,
        Masters(
            product_categories={key: tuple(value) for key, value in masters['categorias_producto'].items()},
            responsible_units={key: tuple(value) for key, value in masters['unidades_responsables'].items()},
        ),
    )


# Golden test: from SAP, August and September give, to the cent, the TB of the export done by hand (932 rows)
def test_august_and_september_from_sap_match_the_manual_export():
    with (TB_DIR / 'maestro_tb_CTS00.xlsx').open('rb') as source:
        config = read_maestro(source, 'CTS00')
    with (TB_DIR / 'data' / 'TB - CTS - SEP.xlsx').open('rb') as source:
        manual = read_export(source)

    from_sap, sap_errors = transform_and_validate(read_export(BytesIO(august_and_september())), config)
    by_hand, manual_errors = transform_and_validate(manual, config)

    assert sap_errors == manual_errors == []
    assert len(by_hand.rows) == 932
    columns = ['clave', 'mes', 'importe']
    expected = by_hand.rows[columns].sort_values(columns).reset_index(drop=True)
    assert from_sap.rows[columns].sort_values(columns).reset_index(drop=True).equals(expected)


# Format of a cell, as compared with the export done by hand
def cell_format(cell) -> tuple:
    border = cell.border
    return (
        cell.font.name,
        cell.font.sz,
        bool(cell.font.b),
        cell.fill.fill_type,
        cell.fill.fgColor.rgb if cell.fill.fill_type else None,
        cell.number_format,
        cell.alignment.horizontal,
        cell.alignment.vertical,
        bool(cell.alignment.wrap_text),
        *(getattr(side, 'style', None) for side in (border.left, border.right, border.top, border.bottom)),
    )


# Golden test of the layout: title, selection block, columns, order and format of the export done by hand, with a
# single bold header row with the filter instead of its three header rows; the values of the data rows may differ
# only where SAP changed after that export
def test_august_and_september_from_sap_have_the_layout_of_the_manual_export():
    generated = openpyxl.load_workbook(BytesIO(august_and_september())).worksheets[0]
    manual = openpyxl.load_workbook(TB_DIR / 'data' / 'TB - CTS - SEP.xlsx').worksheets[0]

    # Sheet name, title and selection block, with their format
    assert generated.title == manual.title
    assert list(map(str, generated.merged_cells.ranges)) == ['B1:U1']
    for row in range(1, 12):
        for column in range(2, 22):
            mine, theirs = generated.cell(row, column), manual.cell(row, column)
            assert (mine.value or None) == (theirs.value or None), mine.coordinate
            if theirs.value not in (None, ''):
                assert cell_format(mine) == cell_format(theirs), mine.coordinate

    # Header row: the dimension and period names of the export, the text column of the cost centre without the name
    # of the period axis; bold and grey, with the filter of the table
    header = [cell.value or '' for cell in generated[12][1:21]]
    assert header == [*(cell.value or '' for cell in manual[14][1:17]), '', '008.2026', '009.2026', 'Resultado']
    assert all(cell.font.b and cell.fill.fgColor.rgb == 'FFDFDFDF' for cell in generated[12][1:21])
    assert generated.auto_filter.ref == f'B12:U{generated.max_row}'

    # Data rows: the same lines in the same order and format; only the drifted ones and the two fixed asset
    # categories (individual products, not in the OData masters) differ
    def lines(sheet, first: int) -> dict:
        return {tuple(cell.value for cell in row[1:18]): row for row in sheet.iter_rows(min_row=first)}

    mine, theirs = lines(generated, 13), lines(manual, 15)
    common = [key for key in theirs if key in mine]
    assert len(common) == len(theirs) - 3
    assert [key for key in mine if key in theirs] == common
    for key in common:
        for cell, expected in zip(mine[key][1:21], theirs[key][1:21], strict=True):
            if expected.value != '' and cell.value == expected.value:
                assert cell_format(cell) == cell_format(expected), cell.coordinate

    # Column widths: narrow margins, every column of the table wide, the rest of the sheet hidden
    def columns(sheet) -> list[tuple]:
        return [(dimension.min, dimension.max, None if dimension.hidden else dimension.width, dimension.hidden)
                for dimension in sheet.column_dimensions.values()]

    assert columns(generated) == columns(manual)
