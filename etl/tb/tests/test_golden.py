# ==============================================================================
# tests/test_golden.py
# ------------------------------------------------------------------------------
# Golden test (spec, acceptance criteria): the SAP export of September 2026
# with the master workbook of CTS00 must reproduce, to the cent, what was
# loaded by hand in the TB sheet of the September TB workbook (columns CY for
# 2026-08 and CZ for 2026-09). Both sides are summed by key (TB!K) and month,
# because the TB has a duplicated key, and the TB rows at 0 are ignored.
#
# Copyright Oimbra Technology 2026
# ==============================================================================

# Standard libraries
from pathlib import Path

# Third-party libraries
import pandas as pd
import pytest
from openpyxl import load_workbook
from openpyxl.utils import column_index_from_string

# Application libraries
from tb.config import Combination, Config
from tb.export import read_export
from tb.maestro import read_maestro
from tb.schema import validate_balance, validate_output
from tb.transform import TransformResult, transform

# Folder of the tb package, where the master workbook and the data live
TB_DIR = Path(__file__).resolve().parents[1]

# First data row of the TB sheet (rows 1-5 are totals, periods and headers)
TB_FIRST_ROW = 6

# Column of the key (TB!K) in the TB sheet
TB_KEY_COLUMN = 'K'

# Column of each month in the TB sheet
TB_MONTH_COLUMNS = {'2026-08': 'CY', '2026-09': 'CZ'}

# Both sides are compared by key and month
COMPARED_BY = ['clave', 'mes']

# Amounts are compared to the cent
CENTS = 2


# Configuration of CTS00 from its master workbook
@pytest.fixture(scope='module')
def config() -> Config:
    with (TB_DIR / 'maestro_tb_CTS00.xlsx').open('rb') as source:
        return read_maestro(source, 'CTS00')


# Transformation of the September export with that configuration
@pytest.fixture(scope='module')
def result(config: Config) -> TransformResult:
    with (TB_DIR / 'data' / 'TB - CTS - SEP.xlsx').open('rb') as source:
        export = read_export(source)
    return transform(export, config)


# The process runs without errors and its output passes the schema and the balance
def test_september_has_no_errors(result: TransformResult):
    assert result.errors == []
    assert validate_output(result.rows) == []
    assert validate_balance(result.rows, result.export_totals) == []


# The output matches the TB sheet by key and month, to the cent
def test_september_matches_tb(result: TransformResult):

    # Output amounts by key and month
    output = result.rows.groupby(COMPARED_BY)['importe'].sum().round(CENTS)

    # TB amounts by key and month, summed (one key is duplicated) and without zeros
    key_index = column_index_from_string(TB_KEY_COLUMN) - 1
    month_indexes = {month: column_index_from_string(column) - 1 for month, column in TB_MONTH_COLUMNS.items()}
    amounts: list[tuple[str, str, float]] = []
    with (TB_DIR / 'data' / '09.2026 TB - COTOWN.xlsx').open('rb') as source:
        workbook = load_workbook(source, read_only=True, data_only=True)
        for row in workbook['TB'].iter_rows(min_row=TB_FIRST_ROW, values_only=True):
            if row[key_index] is not None:
                amounts.extend((row[key_index], month, row[index] or 0.0) for month, index in month_indexes.items())
        workbook.close()
    expected = pd.DataFrame(amounts, columns=[*COMPARED_BY, 'importe']).groupby(COMPARED_BY)['importe'].sum()
    expected = expected.round(CENTS)
    expected = expected[expected != 0]

    # Same keys and months on both sides, and the same amount in each
    comparison = pd.concat({'output': output, 'tb': expected}, axis=1).fillna(0.0)
    differences = comparison[comparison['output'] != comparison['tb']]
    assert differences.empty, f'Diferencias con la TB:\n{differences.to_string()}'


# 624000 S_62400 TDG0043, reassigned by hand in the manual process, takes its category only from Referencia
def test_september_tdg0043_from_reference(config: Config, result: TransformResult):
    rows = result.rows[result.rows['clave'].str.startswith('624000 S_62400 TDG0043 ')]

    assert Combination('624000', 'S_62400', 'TDG0043') not in config.categorias
    assert list(rows['clave'].unique()) == ['624000 S_62400 TDG0043 Other expenses Trips and Delivery building']
