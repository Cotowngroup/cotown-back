# ==============================================================================
# tests/test_sap.py
# ------------------------------------------------------------------------------
# Unit tests of the generator of the Trial Balance export from the general
# ledger of SAP (ticket 08): the workbook it builds from OData records must be
# read by the export reader as the lines of those records, summed by company,
# account, product and profit centre, one amount column per period.
#
# Copyright Oimbra Technology 2026
# ==============================================================================

# Standard libraries
import json
from io import BytesIO
from pathlib import Path

# Third-party libraries
import pytest

# Application libraries
from tb.errors import ReadError
from tb.export import read_export
from tb.maestro import read_maestro
from tb.run import transform_and_validate
from tb.sap import build_export

# Folder of the tb package, where the master workbook and the data live
TB_DIR = Path(__file__).resolve().parents[1]


# One OData record of the general ledger report, as SAP returns it (every value is text)
def record(
    account: str,
    product: str,
    centre: str,
    amount: str,
    period: str = '8',
    doc_type: str = '00009',
    product_text: str = '',
) -> dict:
    return {
        'CFISCYEAR': '2026',
        'CFISCPER': period,
        'CACCDOCTYPE': doc_type,
        'CGLACCT': account,
        'TGLACCT': f'CUENTA {account}',
        'CPRODUCT_UUID': product,
        'TPRODUCT_UUID': product_text or ('No asignado' if not product else f'TEXTO {product}'),
        'CPROFITCTR_UUID': centre,
        'KCBALANCE_CURRCOMP': amount,
    }


# Canonical rows of the generated workbook, as the batch would read them
def read(records: list[dict], months: list[str]) -> list[dict]:
    return read_export(BytesIO(build_export(records, 'CTS00', months))).to_dict('records')


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


# A line without product (empty code, or SAP's own markers for it) is '#' with 'Sin asignar', as in the export
@pytest.mark.parametrize('code', ['', '#', 'Not Assigned', 'No asignado'])
def test_line_without_product_is_hash(code):
    rows = read([record('280000', code, 'CTS01', '-7220')], ['2026-08'])

    assert (rows[0]['producto'], rows[0]['texto_producto']) == ('#', 'Sin asignar')


# The balance carry-forward of the year (document type 00058) does not go to the TB
def test_balance_carry_forward_is_left_out():
    records = [
        record('129000', '', 'CTS01', '1500', period='1', doc_type='00058'),
        record('555800', '', 'CTS01', '-1500', period='1', doc_type='00058'),
        record('705000', 'S_70504', 'CTS01', '-10', period='1'),
        record('430000', '', 'CTS01', '10', period='1'),
    ]

    rows = read(records, ['2026-01'])

    assert [(row['cuenta'], row['importe']) for row in rows] == [('705000', -10.0), ('430000', 10.0)]


# Several months: one period column each, and a line missing in a month is 0 there
def test_several_months_are_period_columns():
    records = [
        record('705000', 'S_70504', 'CTS01', '-10', period='8'),
        record('705000', 'S_70504', 'CTS01', '-20', period='9'),
        record('430000', '', 'CTS01', '10', period='8'),
    ]

    rows = read(records, ['2026-08', '2026-09'])

    assert [(row['cuenta'], row['mes'], row['importe']) for row in rows] == [
        ('705000', '2026-08', -10.0),
        ('705000', '2026-09', -20.0),
        ('430000', '2026-08', 10.0),
        ('430000', '2026-09', 0.0),
    ]


# A month asked for without any record is an error, not an empty month
def test_month_without_records_is_an_error():
    with pytest.raises(ReadError) as raised:
        build_export([record('705000', 'S_70504', 'CTS01', '-10', period='8')], 'CTS00', ['2026-08', '2026-09'])

    assert raised.value.errors == ['SAP no tiene apuntes de CTS00 en 2026-09: revisa el periodo o la sociedad.']


# Golden test: the general ledger of August and September 2026 from SAP gives, to the cent, the TB of the export
# done by hand (932 rows, the figure of the phase I command line)
def test_august_and_september_from_sap_match_the_manual_export():
    months = ['2026-08', '2026-09']
    with (TB_DIR / 'maestro_tb_CTS00.xlsx').open('rb') as source:
        config = read_maestro(source, 'CTS00')
    records = [
        record
        for month in months
        for record in json.loads((TB_DIR / 'data' / f'sap_gl_CTS00_{month}.json').read_text(encoding='utf-8'))
    ]
    with (TB_DIR / 'data' / 'TB - CTS - SEP.xlsx').open('rb') as source:
        manual = read_export(source)

    generated = read_export(BytesIO(build_export(records, 'CTS00', months)))
    from_sap, sap_errors = transform_and_validate(generated, config)
    by_hand, manual_errors = transform_and_validate(manual, config)

    assert sap_errors == manual_errors == []
    assert len(by_hand.rows) == 932
    columns = ['clave', 'mes', 'importe']
    expected = by_hand.rows[columns].sort_values(columns).reset_index(drop=True)
    assert from_sap.rows[columns].sort_values(columns).reset_index(drop=True).equals(expected)
