# ==============================================================================
# tests/test_schema.py
# ------------------------------------------------------------------------------
# Unit tests of the balance check (spec decision 22): TB rows and the export
# total per month after the filter in, the full list of errors out.
#
# Copyright Oimbra Technology 2026
# ==============================================================================

# Third-party libraries
import pandas as pd

# Application libraries
from tb.schema import validate_balance


# TB rows with only the columns the balance check reads: (mes, importe)
def build_rows(*amounts: tuple[str, float]) -> pd.DataFrame:
    return pd.DataFrame(amounts, columns=['mes', 'importe'])


# Months that net 0 and match the export are balanced, within ±0,005
def test_balanced_months():
    rows = build_rows(('2026-08', 100.0), ('2026-08', -100.004), ('2026-09', 25.5), ('2026-09', -25.5))

    assert validate_balance(rows, {'2026-08': -0.004, '2026-09': 0.0}) == []


# A month that does not sum 0 is an error with the month and the amount
def test_month_not_netting_is_error():
    rows = build_rows(('2026-08', 100.0), ('2026-08', -100.0), ('2026-09', 25.5), ('2026-09', -20.0))

    errors = validate_balance(rows, {'2026-08': 0.0, '2026-09': 5.5})

    assert len(errors) == 1
    assert '2026-09' in errors[0]
    assert '5,50' in errors[0]


# A month whose output total differs from the export total is an error with both amounts
def test_output_not_matching_export_is_error():
    rows = build_rows(('2026-08', 100.0), ('2026-08', -100.0), ('2026-09', 25.5), ('2026-09', -25.5))

    errors = validate_balance(rows, {'2026-08': 0.0, '2026-09': 0.01})

    assert len(errors) == 1
    for text in ('2026-09', '0,00', '0,01', 'export'):
        assert text in errors[0], text


# A month of the export missing from the output is compared against 0
def test_export_month_missing_from_output_is_error():
    rows = build_rows(('2026-08', 100.0), ('2026-08', -100.0))

    errors = validate_balance(rows, {'2026-08': 0.0, '2026-09': 0.04})

    assert len(errors) == 1
    assert '2026-09' in errors[0]
