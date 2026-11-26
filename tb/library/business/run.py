# ==============================================================================
# library/business/run.py
# ------------------------------------------------------------------------------
# Steps shared by the command line and the Airflows uploads: transform and
# validate the canonical export with a configuration, and the texts reported
# afterwards (the summary of a good run and the list of errors of a bad one).
#
# Copyright Oimbra Technology 2026
# ==============================================================================

# Third-party libraries
import pandas as pd

# Application libraries
from library.business.config import Config
from library.business.schema import format_amount, validate_balance, validate_output
from library.business.transform import TransformResult, transform


# Transform, then validate the output schema and the balance; returns the result and every error
def transform_and_validate(export: pd.DataFrame, config: Config) -> tuple[TransformResult, list[str]]:
    result = transform(export, config)
    errors = (
        result.errors
        or validate_output(result.rows)
        or validate_balance(result.rows, result.export_totals)
    )
    return result, errors


# Total of each month of the TB rows, as 'AAAA-MM: 0,00'
def month_totals(rows: pd.DataFrame) -> list[str]:
    totals = rows.groupby('mes')['importe'].sum().round(2)
    return [f'{month}: {format_amount(total)}' for month, total in totals.items()]


# Summary of a good run: rows, keys and total per month
def summary_lines(result: TransformResult) -> list[str]:
    rows = result.rows
    return [
        f'Filas: {len(rows)}',
        f'Claves: {rows['clave'].nunique()}',
        'Total por mes:',
        *(f'  {total}' for total in month_totals(rows)),
    ]


# Report of a bad run: how many errors, that nothing was done, and the full list
def error_lines(errors: list[str], nothing_done: str) -> list[str]:
    return [f'{len(errors)} errores; {nothing_done}:', *(f'- {message}' for message in errors)]
