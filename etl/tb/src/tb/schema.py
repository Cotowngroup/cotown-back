# ==============================================================================
# tb/schema.py
# ------------------------------------------------------------------------------
# Output schema of the TB rows (spec decision 20) and the balance check
# (decision 22), in a single place: every writer (CSV now, database in phase
# II) gets rows that passed both. Also the amount format of the messages.
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

# Largest difference accepted when amounts must net to 0 or match, in euros
BALANCE_TOLERANCE = 0.005


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


# Amount as the messages show it: 2 decimals and decimal comma
def format_amount(amount: float) -> str:

    # Adding 0 turns -0.0 into 0.0, so a balanced month does not show -0,00
    return f'{amount + 0:.2f}'.replace('.', ',')


# Check that every month of the TB rows nets 0 and matches the export total after the filter (spec decision 22)
def validate_balance(rows: pd.DataFrame, export_totals: dict[str, float]) -> list[str]:
    errors = []

    # Every month of either side, so a month missing from the output is also checked
    totals = rows.groupby('mes')['importe'].sum()
    for month in sorted(set(totals.index) | set(export_totals)):
        total = totals.get(month, 0.0)
        export_total = export_totals.get(month, 0.0)

        # Every month nets 0
        if abs(total) > BALANCE_TOLERANCE:
            errors.append(f'Cuadre: {month} suma {format_amount(total)} y debe sumar 0. Revisa el export.')

        # And keeps the amount of the export after the filter
        elif abs(total - export_total) > BALANCE_TOLERANCE:
            errors.append(
                f'Cuadre: {month} suma {format_amount(total)} en la salida y {format_amount(export_total)} '
                f'en el export.'
            )
    return errors
