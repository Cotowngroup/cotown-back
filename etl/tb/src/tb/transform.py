# ==============================================================================
# tb/transform.py
# ------------------------------------------------------------------------------
# Pure transformation of the canonical export into TB rows (spec decisions
# 12-19). Input: one row per export line and month (empresa, cuenta,
# texto_cuenta, producto, texto_producto, centro_beneficio, mes, importe) and
# the company configuration. Output: one row per empresa + clave + mes. No
# input/output: every problem is collected as a message instead of raised.
#
# Copyright Oimbra Technology 2026
# ==============================================================================

# Standard libraries
import re
from dataclasses import dataclass

# Third-party libraries
import pandas as pd

# Application libraries
from tb.config import Category, Config
from tb.schema import NATURAL_KEY, OUTPUT_COLUMNS

# Prefix that some profit centres carry in SAP and the TB ignores
AT_PREFIX = 'AT-'


# Result of a transformation: the TB rows, empty when there are errors
@dataclass(frozen=True)
class TransformResult:
    rows: pd.DataFrame
    errors: list[str]


# Transform the canonical export with the company configuration
def transform(export: pd.DataFrame, config: Config) -> TransformResult:
    errors: list[str] = []

    # One company per export, the one of the master workbook; every line counts, also those at 0
    companies = sorted(export['empresa'].unique())
    if len(companies) > 1:
        errors.append(f'El export tiene varias empresas ({', '.join(companies)}). Exporta de SAP una sola sociedad.')
    elif companies and companies[0] != config.empresa:
        errors.append(
            f'La empresa del export ({companies[0]}) no es la de la hoja maestra ({config.empresa}). '
            f'Usa maestro_tb_{companies[0]}.xlsx.'
        )

    # Drop zero amounts: a line with every period at 0 disappears, and the sums do not change
    lines = export[export['importe'] != 0].copy()

    # Service: the S_ product code, otherwise the account
    is_service = lines['producto'].str.startswith('S_')
    lines['servicio'] = lines['producto'].where(is_service, lines['cuenta'])
    lines['descripcion'] = lines['texto_producto'].where(is_service, lines['texto_cuenta'])

    # Profit centre without the AT- prefix
    lines['centro_beneficio'] = lines['centro_beneficio'].str.removeprefix(AT_PREFIX)

    # Asset from the profit centre: exact equivalence, then the base (without _floor.door), then the building pattern
    pattern = re.compile(config.patron_edificio)
    assets = {}
    for centre in lines['centro_beneficio'].unique():
        base = centre.split('_', 1)[0]
        match = pattern.match(centre)
        if centre in config.equivalencias:
            assets[centre] = config.equivalencias[centre]
        elif base in config.equivalencias:
            assets[centre] = config.equivalencias[base]
        elif match:
            assets[centre] = match['edificio'] + match['numero'].zfill(config.digitos_numero)
        else:
            accounts = ', '.join(sorted(lines.loc[lines['centro_beneficio'] == centre, 'cuenta'].unique()))
            errors.append(
                f'Centro de beneficio sin asset: {centre} (cuentas {accounts}). '
                f'Añádelo a Equivalencias o revisa el centro en SAP.'
            )
    lines['asset'] = lines['centro_beneficio'].map(assets)

    # Category and annual-accounts grouping from Mapping, by service
    for service in lines['servicio'].unique():
        if service not in config.mapping:
            service_lines = lines[lines['servicio'] == service]
            accounts = ', '.join(sorted(service_lines['cuenta'].unique()))
            errors.append(
                f'Servicio sin categoría: {service} "{service_lines['descripcion'].iloc[0]}" (cuentas {accounts}). '
                f'Añádelo a Mapping.'
            )
    categories = lines['servicio'].map(config.mapping)
    for column in Category._fields:
        lines[column] = categories.map(lambda category, field=column: getattr(category, field, None))

    # Nothing is output when anything could not be resolved
    if errors:
        return TransformResult(rows=pd.DataFrame(columns=OUTPUT_COLUMNS), errors=errors)

    # Key identical to TB!K
    lines['clave'] = lines['cuenta'] + ' ' + lines['servicio'] + ' ' + lines['asset'] + ' ' + lines['categoria']

    # One description per key, the one of its first line in export order, whatever the month
    lines['descripcion'] = lines.groupby(['empresa', 'clave'], sort=False)['descripcion'].transform('first')

    # Sum by empresa + clave + mes, rounding after aggregating
    attributes = ['cuenta', 'servicio', 'descripcion', 'asset', 'categoria', 'ccaa1', 'ccaa2']
    rows = lines.groupby(NATURAL_KEY, sort=False).agg(
        **{column: (column, 'first') for column in attributes},
        importe=('importe', 'sum'),
    ).reset_index()
    rows['importe'] = rows['importe'].round(2)
    rows = rows[rows['importe'] != 0].reset_index(drop=True)
    rows['budget'] = None
    return TransformResult(rows=rows[OUTPUT_COLUMNS], errors=errors)
