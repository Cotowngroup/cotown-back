# ==============================================================================
# library/business/csv_writer.py
# ------------------------------------------------------------------------------
# CSV writer of the TB rows, for review in Excel (spec decision 21): UTF-8
# with BOM, ; separator, decimal comma and a header with the column names.
#
# Copyright Oimbra Technology 2026
# ==============================================================================

# Standard libraries
from pathlib import Path

# Third-party libraries
import pandas as pd


# Write the TB rows as a CSV that Excel opens with a double click
def write_csv(rows: pd.DataFrame, path: Path) -> None:
    rows.to_csv(path, sep=';', decimal=',', float_format='%.2f', index=False, encoding='utf-8-sig')
