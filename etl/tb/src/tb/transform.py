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
from tb.config import Category, Combination, Config
from tb.schema import BALANCE_TOLERANCE, NATURAL_KEY, OUTPUT_COLUMNS, format_amount

# Prefix that some profit centres carry in SAP and the TB ignores
AT_PREFIX = 'AT-'

# Columns of the export that tell its lines apart for the TB
LINE_DIMENSIONS = ['empresa', 'cuenta', 'producto', 'centro_beneficio', 'mes']


# Result of a transformation: the TB rows, empty when there are errors
@dataclass(frozen=True)
class TransformResult:
    rows: pd.DataFrame
    errors: list[str]
    export_totals: dict[str, float]


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

    # Sum the export lines that the TB does not tell apart (they may differ in cost centre or project task), keeping
    # the texts of the first one; then drop zero amounts: a line netting 0 in the month disappears, sums do not change
    lines = export.groupby(LINE_DIMENSIONS, sort=False, as_index=False).agg(
        texto_cuenta=('texto_cuenta', 'first'),
        texto_producto=('texto_producto', 'first'),
        importe=('importe', 'sum'),
    )
    lines = lines[lines['importe'].round(2) != 0].copy()

    # Excluded accounts (Cuentas) must net 0 every month: dropping them must not unbalance the TB
    is_excluded = lines['cuenta'].isin(config.excluidas)
    for (account, month), total in lines[is_excluded].groupby(['cuenta', 'mes'])['importe'].sum().items():
        if abs(total) > BALANCE_TOLERANCE:
            errors.append(
                f'Cuenta excluida que no neta 0: {account} en {month} suma {format_amount(total)}. '
                f'Revísala en SAP o, si debe pasar a la TB, quita la marca excluida en Cuentas.'
            )

    # Drop the excluded accounts; what is left is the export after the filter, the total the output must keep
    lines = lines[~is_excluded].copy()
    export_totals = lines.groupby('mes')['importe'].sum().to_dict()

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

    # Reclasificaciones: target services per account + SAP service + centre (None for the rows without centre)
    targets: dict[tuple[str, str, str | None], list[str]] = {}
    for row in config.reclasificaciones:
        targets.setdefault((row.cuenta, row.servicio_sap, row.centro_beneficio), []).append(row.servicio_tb)

    # Row level that applies to each line: its centre when a row names it, otherwise the general one
    line_keys = list(zip(lines['cuenta'], lines['servicio'], lines['centro_beneficio'], strict=True))
    row_keys = {key: key if key in targets else (*key[:2], None) for key in dict.fromkeys(line_keys)}

    # Two rows of the same level for a line are a conflict, reported once per row key
    for account, service, centre in dict.fromkeys(row_keys.values()):
        services = targets.get((account, service, centre), [])
        if len(services) > 1:
            where = f' del centro {centre}' if centre is not None else ''
            errors.append(
                f'Reclasificación en conflicto: {account} {service}{where} tiene {len(services)} filas en '
                f'Reclasificaciones ({', '.join(services)}). Deja una sola.'
            )

    # New service of each line, or its own service (key[1]) when no row applies
    lines['servicio'] = [targets.get(row_keys[key], [key[1]])[0] for key in line_keys]

    # Annual-accounts grouping of each account, from Cuentas; once per account without it
    for account in lines.loc[~lines['cuenta'].isin(config.cuentas), 'cuenta'].unique():
        text = lines.loc[lines['cuenta'] == account, 'texto_cuenta'].iloc[0]
        errors.append(f'Cuenta sin CCAA: {account} "{text}". Añádela a Cuentas con su ccaa1 y ccaa2.')

    # Category per account + service + asset (spec decision 18): the exception of the asset, else the general row
    lines['combinacion'] = list(map(Combination._make, lines[list(Combination._fields)].itertuples(index=False)))
    categories: dict[Combination, Category] = {}
    unmapped: set[Combination] = set()
    for combination in lines['combinacion'].unique():
        category = config.categorias.get(combination, config.categorias.get(combination._replace(asset='')))
        if category is None:
            unmapped.add(combination)
        elif combination.cuenta in config.cuentas:
            categories[combination] = Category(category, *config.cuentas[combination.cuenta])

    # Services without a category row, once per service with the accounts of its unresolved combinations
    unresolved = lines[[combination in unmapped for combination in lines['combinacion']]]
    for service in unresolved['servicio'].unique():
        service_lines = unresolved[unresolved['servicio'] == service]
        accounts = ', '.join(sorted(service_lines['cuenta'].unique()))
        errors.append(
            f'Servicio sin categoría: {service} "{service_lines['descripcion'].iloc[0]}" (cuentas {accounts}). '
            f'Añade cuenta + servicio a Categorias.'
        )

    # Category columns of every line
    for column in Category._fields:
        lines[column] = [getattr(categories.get(combination), column, None) for combination in lines['combinacion']]

    # Nothing is output when anything could not be resolved
    if errors:
        return TransformResult(
            rows=pd.DataFrame(columns=OUTPUT_COLUMNS),
            errors=errors,
            export_totals={},
        )

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
    return TransformResult(
        rows=rows[OUTPUT_COLUMNS],
        errors=errors,
        export_totals=export_totals,
    )
