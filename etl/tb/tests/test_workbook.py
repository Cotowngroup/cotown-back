# ==============================================================================
# tests/test_workbook.py
# ------------------------------------------------------------------------------
# Tests of the TB sheet that a good upload adds to its own SAP export (ticket
# 09a): the rows of the TB in a sheet "TB" after the export, which stays as it
# was and first, so the file can be processed again; processing it again
# replaces that sheet.
#
# Copyright Oimbra Technology 2026
# ==============================================================================

# Standard libraries
from io import BytesIO

# Third-party libraries
import openpyxl
import pandas as pd

# Application libraries
from tb.schema import OUTPUT_COLUMNS
from tb.workbook import TB_SHEET, add_tb_sheet


# TB rows as the transformation returns them
def tb_rows(*amounts: float) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                'empresa': 'CTS00',
                'cuenta': '705000',
                'servicio': 'S_70504',
                'descripcion': 'LIMPIEZA CHECK OUT',
                'asset': 'BAI0033',
                'categoria': 'Checkout Cleaning Services (Final cleaning)',
                'ccaa1': 'PL',
                'ccaa2': 'Revenue',
                'budget': None,
                'clave': '705000 S_70504 BAI0033 Checkout Cleaning Services (Final cleaning)',
                'mes': f'2026-0{index + 1}',
                'importe': amount,
            }
            for index, amount in enumerate(amounts)
        ],
        columns=OUTPUT_COLUMNS,
    )


# An export workbook with a single sheet
def export_workbook() -> bytes:
    book = openpyxl.Workbook()
    book.active.title = 'Exportac. 26.11.2026 15.18.11'
    book.active['B1'] = 'Trial Balance'
    stream = BytesIO()
    book.save(stream)
    return stream.getvalue()


# The TB rows go to a sheet TB after the export, which stays first and unchanged; codes stay text
def test_tb_sheet_is_added_after_the_export():
    book = openpyxl.load_workbook(BytesIO(add_tb_sheet(export_workbook(), tb_rows(-314.04, 12.5))))

    assert book.sheetnames == ['Exportac. 26.11.2026 15.18.11', TB_SHEET]
    assert book.worksheets[0]['B1'].value == 'Trial Balance'
    rows = [list(row) for row in book[TB_SHEET].iter_rows(values_only=True)]
    assert rows[0] == OUTPUT_COLUMNS
    assert [(row[1], row[10], row[11]) for row in rows[1:]] == [
        ('705000', '2026-01', -314.04),
        ('705000', '2026-02', 12.5),
    ]
    assert book[TB_SHEET].auto_filter.ref == 'A1:L3'


# Processing the file again replaces its TB sheet
def test_tb_sheet_is_replaced_when_processed_again():
    once = add_tb_sheet(export_workbook(), tb_rows(-314.04, 12.5))

    book = openpyxl.load_workbook(BytesIO(add_tb_sheet(once, tb_rows(7.0))))

    assert book.sheetnames == ['Exportac. 26.11.2026 15.18.11', TB_SHEET]
    assert [row[11] for row in book[TB_SHEET].iter_rows(min_row=2, values_only=True)] == [7.0]
