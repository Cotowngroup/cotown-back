# ==============================================================================
# library/business/dw.py
# ------------------------------------------------------------------------------
# Rows of gold.tb in the DW (ticket 09b): the TB rows of a good upload, with
# the first day of their month (to join with gold.date) and the id of the
# upload that gave them, plus the SQL that replaces the months of an upload.
# No input/output: the batch runs the SQL with these rows.
#
# Copyright Oimbra Technology 2026
# ==============================================================================

# Standard libraries
from datetime import date

# Third-party libraries
import pandas as pd

# Application libraries
from library.business.schema import OUTPUT_COLUMNS

# Columns of gold.tb that an upload fills, in the order of the INSERT; ts takes its default
DW_COLUMNS = [*OUTPUT_COLUMNS[:-1], 'date', 'importe', 'tb_upload_id']

# Replace the months of an upload: delete its company and months, insert its rows (in one transaction)
SQL_DELETE = 'DELETE FROM gold.tb WHERE "empresa" = %s AND "mes" = ANY(%s)'
SQL_INSERT = 'INSERT INTO gold.tb ({}) VALUES %s'.format(', '.join(f'"{column}"' for column in DW_COLUMNS))


# Rows of gold.tb from the TB rows of an upload; an empty budget is NULL
def dw_records(rows: pd.DataFrame, upload_id: int) -> list[tuple]:
    records = []
    for row in rows[OUTPUT_COLUMNS].itertuples(index=False):
        year, month = row.mes.split('-')
        values = [None if pd.isna(value) else value for value in row[:-1]]
        records.append((*values, date(int(year), int(month), 1), float(row.importe), upload_id))
    return records
