# ==============================================================================
# tb/schema.py
# ------------------------------------------------------------------------------
# Output schema of the TB rows (spec decision 20) and its validation, in a
# single place: every writer (CSV now, database in phase II) gets rows that
# passed it.
#
# Copyright Oimbra Technology 2026
# ==============================================================================

# Third-party libraries
import pandas as pd

# Columns of the TB output, in order
OUTPUT_COLUMNS = [
    'empresa',
    'cuenta',
    'servicio',
    'descripcion',
    'asset',
    'categoria',
    'ccaa1',
    'ccaa2',
    'budget',
    'clave',
    'mes',
    'importe',
]

# Columns that are always filled text; budget is the only nullable one
TEXT_COLUMNS = [column for column in OUTPUT_COLUMNS if column not in ('budget', 'importe')]

# Start of every schema violation message
SCHEMA_ERROR = 'Esquema de salida: '

# Natural key of a TB row
NATURAL_KEY = ['empresa', 'clave', 'mes']


# Check the TB rows against the output schema and return every violation
def validate_output(rows: pd.DataFrame) -> list[str]:
    # Exact columns, in order
    if list(rows.columns) != OUTPUT_COLUMNS:
        return [f'{SCHEMA_ERROR}columnas {list(rows.columns)}, se esperaban {OUTPUT_COLUMNS}.']
    errors = []

    # Filled text columns and an always-null budget
    for column in TEXT_COLUMNS:
        invalid = ~rows[column].map(lambda value: isinstance(value, str) and value != '')
        if invalid.any():
            errors.append(f'{SCHEMA_ERROR}{invalid.sum()} filas con {column} vacío o no textual.')
    if rows['budget'].notna().any():
        errors.append(f'{SCHEMA_ERROR}budget debe estar vacío.')

    # Formats: six-digit account, AAAA-MM month, non-zero amount with 2 decimals
    if (~rows['cuenta'].str.fullmatch(r'\d{6}', na=False)).any():
        errors.append(f'{SCHEMA_ERROR}hay cuentas que no tienen 6 dígitos.')
    if (~rows['mes'].str.fullmatch(r'\d{4}-(0[1-9]|1[0-2])', na=False)).any():
        errors.append(f'{SCHEMA_ERROR}hay meses que no tienen el formato AAAA-MM.')
    amounts = pd.to_numeric(rows['importe'], errors='coerce')
    if amounts.isna().any() or (amounts.round(2) != amounts).any() or (amounts == 0).any():
        errors.append(f'{SCHEMA_ERROR}hay importes vacíos, a cero o con más de 2 decimales.')

    # Unique natural key
    duplicated = rows[rows.duplicated(NATURAL_KEY, keep=False)]
    if not duplicated.empty:
        errors.append(f'{SCHEMA_ERROR}{len(duplicated)} filas repiten empresa + clave + mes.')
    return errors
