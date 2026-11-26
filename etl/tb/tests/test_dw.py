# ==============================================================================
# tests/test_dw.py
# ------------------------------------------------------------------------------
# Tests of the rows of gold.tb in the DW (ticket 09b): the TB rows of a good
# upload, with the first day of their month and the upload that gave them,
# in the column order of the INSERT.
#
# Copyright Oimbra Technology 2026
# ==============================================================================

# Standard libraries
from datetime import date

# Third-party libraries
import pandas as pd

# Application libraries
from tb.dw import DW_COLUMNS, dw_records
from tb.schema import OUTPUT_COLUMNS


# TB rows as the transformation returns them
def tb_rows() -> pd.DataFrame:
    return pd.DataFrame(
        [
            ['CTS00', '705000', 'S_70504', 'LIMPIEZA', 'BAI0033', 'Cleaning', 'PL', 'Revenue', None,
             '705000 S_70504 BAI0033 Cleaning', '2026-09', -314.04],
            ['CTS00', '430000', '430000', 'CLIENTES', 'Manco', 'Clients', 'BS', 'Receivables', None,
             '430000 430000 Manco Clients', '2026-12', 12.5],
        ],
        columns=OUTPUT_COLUMNS,
    )


# Each TB row becomes a row of gold.tb: its columns, the first day of its month and the upload id
def test_tb_rows_become_dw_records_with_date_and_upload():
    records = dw_records(tb_rows(), 12)

    assert DW_COLUMNS == [
        'empresa', 'cuenta', 'servicio', 'descripcion', 'asset', 'categoria', 'ccaa1', 'ccaa2', 'budget', 'clave',
        'mes', 'date', 'importe', 'tb_upload_id',
    ]
    assert records == [
        ('CTS00', '705000', 'S_70504', 'LIMPIEZA', 'BAI0033', 'Cleaning', 'PL', 'Revenue', None,
         '705000 S_70504 BAI0033 Cleaning', '2026-09', date(2026, 9, 1), -314.04, 12),
        ('CTS00', '430000', '430000', 'CLIENTES', 'Manco', 'Clients', 'BS', 'Receivables', None,
         '430000 430000 Manco Clients', '2026-12', date(2026, 12, 1), 12.5, 12),
    ]
