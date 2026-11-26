# ==============================================================================
# library/business/maestro.py
# ------------------------------------------------------------------------------
# Reader of a company's master workbook (maestro_tb_<empresa>.xlsx): one sheet
# per configuration table, every cell read as text. Sheets whose name starts
# with _ are notes and are ignored. Takes a binary stream, so the workbook can
# come from disk or from Airflows (Admin.Files). The company is not in the
# workbook: the caller passes it. In Airflows, the workbook of a company is
# the single Admin.Files record named "Maestro TB <empresa>" (decision F3).
#
# Copyright Oimbra Technology 2026
# ==============================================================================

# Standard libraries
import re
from typing import BinaryIO, NamedTuple

# Third-party libraries
import pandas as pd

# Application libraries
from library.business.config import AnnualAccounts, Combination, Config, Reclassification
from library.business.errors import ReadError

# Columns the transformation needs from each sheet; other columns (descripcion, motivo) are informative
REQUIRED_COLUMNS = {
    'Reglas': ['patron_edificio', 'digitos_numero'],
    'Cuentas': ['cuenta', *AnnualAccounts._fields, 'excluida'],
    'Equivalencias': ['centro_beneficio', 'asset'],
    'Reclasificaciones': list(Reclassification._fields),
    'Categorias': [*Combination._fields, 'categoria'],
}

# Values of excluida in Cuentas: empty, the account goes to the TB; si or sí, it does not
EXCLUDED_VALUES = {'', 'sí', 'si'}


# Placeholder for an empty cell in the messages about incomplete rows
EMPTY = '(vacío)'

# Where the master workbooks live in Airflows, as the messages name it
FILES_ENTITY = 'Ficheros (Admin.Files) de Airflows'


# Admin.Files record holding the master workbook of a company, with the date of its last change
class MaestroFile(NamedTuple):
    id: int
    modified: str


# Name of the Admin.Files record of a company's master workbook
def maestro_name(empresa: str) -> str:
    return f'Maestro TB {empresa}'


# Choose the master workbook of a company among Admin.Files records (id, Name, Created_at, Updated_at)
def select_maestro(records: list[dict], empresa: str) -> MaestroFile:
    name = maestro_name(empresa)
    matching = [record for record in records if record['Name'] == name]

    # Exactly one record: none means no configuration, several are ambiguous
    if not matching:
        raise ReadError([f'No hay hoja maestra para {empresa}: falta el fichero "{name}" en {FILES_ENTITY}.'])
    if len(matching) > 1:
        ids = ', '.join(str(record['id']) for record in matching)
        raise ReadError([f'Hay {len(matching)} ficheros "{name}" en {FILES_ENTITY} (ids {ids}): deja solo uno.'])

    # Dated by its last update; a record never changed only has its creation date
    record = matching[0]
    return MaestroFile(id=record['id'], modified=record['Updated_at'] or record['Created_at'])


# Read the master workbook of a company into its configuration
def read_maestro(source: BinaryIO, empresa: str) -> Config:
    # Every sheet as text, except the _ notes
    sheets = pd.read_excel(source, sheet_name=None, dtype=str)
    sheets = {name: sheet for name, sheet in sheets.items() if not name.startswith('_')}
    errors = []

    # Every needed sheet with its needed columns
    for name, columns in REQUIRED_COLUMNS.items():
        if name not in sheets:
            errors.append(f'Falta la pestaña {name} en la hoja maestra.')
            continue
        missing = [column for column in columns if column not in sheets[name].columns]
        if missing:
            errors.append(f'Faltan columnas en la pestaña {name} de la hoja maestra: {', '.join(missing)}.')
    if errors:
        raise ReadError(errors)

    # Rows with something in the columns the process reads, codes without surrounding spaces; texts (categories,
    # CCAA) stay exactly as written, since they are part of the TB
    def table(name: str, codes: list[str]) -> pd.DataFrame:
        sheet = sheets[name].dropna(how='all', subset=REQUIRED_COLUMNS[name]).copy()
        for column in codes:
            sheet[column] = sheet[column].str.strip()
        return sheet

    rules = sheets['Reglas'].dropna(how='all')
    accounts = table('Cuentas', ['cuenta', 'excluida'])
    equivalences = table('Equivalencias', ['centro_beneficio'])
    reclassifications = table('Reclasificaciones', list(Reclassification._fields))
    categories = table('Categorias', list(Combination._fields))
    accounts['excluida'] = accounts['excluida'].fillna('').str.lower()
    categories['asset'] = categories['asset'].fillna('')

    # Reglas: a single row with the building pattern and the number length
    if len(rules) != 1:
        errors.append(f'La pestaña Reglas debe tener una sola fila y tiene {len(rules)}.')
    else:
        if not str(rules['digitos_numero'].iloc[0]).strip().isdigit():
            errors.append(f'digitos_numero de la pestaña Reglas no es un número: "{rules['digitos_numero'].iloc[0]}".')
        try:
            groups = re.compile(str(rules['patron_edificio'].iloc[0])).groupindex
            if not {'edificio', 'numero'} <= groups.keys():
                errors.append('patron_edificio de la pestaña Reglas debe tener los grupos edificio y numero.')
        except re.error as error:
            errors.append(f'patron_edificio de la pestaña Reglas no es una expresión regular válida: {error}.')

    # Cuentas: each account once; excluida is "sí" or empty; an account that goes to the TB needs both CCAA
    for row in accounts[accounts['cuenta'].isna()].fillna(EMPTY).itertuples():
        errors.append(f'Cuentas: fila sin cuenta (ccaa1 {row.ccaa1}, ccaa2 {row.ccaa2}).')
    accounts = accounts.dropna(subset=['cuenta'])
    for account in accounts.loc[accounts['cuenta'].duplicated(), 'cuenta'].unique():
        errors.append(f'Cuentas: la cuenta {account} está repetida. Deja una sola fila.')
    for row in accounts[~accounts['excluida'].isin(EXCLUDED_VALUES)].itertuples():
        errors.append(f'Cuentas: excluida de la cuenta {row.cuenta} debe ser "sí" o estar vacía, no "{row.excluida}".')
    is_excluded = accounts['excluida'] != ''
    for account in accounts.loc[~is_excluded & accounts[list(AnnualAccounts._fields)].isna().any(axis=1), 'cuenta']:
        errors.append(f'Cuentas: a la cuenta {account} le falta ccaa1 o ccaa2. Complétala o márcala como excluida.')

    # Equivalencias: one asset per profit centre
    incomplete = equivalences[equivalences[['centro_beneficio', 'asset']].isna().any(axis=1)]
    for row in incomplete.fillna(EMPTY).itertuples(index=False):
        errors.append(f'Equivalencias: fila incompleta (centro_beneficio {row.centro_beneficio}, asset {row.asset}).')
    for centre in equivalences.loc[equivalences['centro_beneficio'].duplicated(), 'centro_beneficio'].unique():
        errors.append(f'Equivalencias: el centro {centre} está repetido. Deja una sola fila.')

    # Reclasificaciones: account, SAP service and TB service; the centre is optional
    incomplete = reclassifications[['cuenta', 'servicio_sap', 'servicio_tb']].isna().any(axis=1)
    for row in reclassifications[incomplete].fillna(EMPTY).itertuples():
        errors.append(
            f'Reclasificaciones: fila incompleta (cuenta {row.cuenta}, servicio_sap {row.servicio_sap}, '
            f'servicio_tb {row.servicio_tb}).'
        )

    # Categorias: account, service and category, the asset only in exceptions; one row per account + service + asset
    incomplete = categories[['cuenta', 'servicio', 'categoria']].isna().any(axis=1)
    for row in categories[incomplete].fillna(EMPTY).itertuples():
        errors.append(
            f'Categorias: fila incompleta (cuenta {row.cuenta}, servicio {row.servicio}, categoria {row.categoria}).'
        )
    for row in categories[categories.duplicated(subset=list(Combination._fields))].itertuples():
        where = f'el asset {row.asset}' if row.asset else 'la fila general (sin asset)'
        errors.append(f'Categorias: {row.cuenta} {row.servicio} tiene repetida {where}. Deja una sola fila.')
    if errors:
        raise ReadError(errors)

    # Configuration of the company
    return Config(
        empresa=empresa,
        patron_edificio=rules['patron_edificio'].iloc[0],
        digitos_numero=int(rules['digitos_numero'].iloc[0]),
        excluidas=list(accounts.loc[is_excluded, 'cuenta']),
        cuentas={
            row.cuenta: AnnualAccounts(row.ccaa1, row.ccaa2)
            for row in accounts[~is_excluded].itertuples(index=False)
        },
        equivalencias=dict(zip(equivalences['centro_beneficio'], equivalences['asset'], strict=True)),
        # An empty centre (NaN, or only spaces before the strip) means a general row
        reclasificaciones=[
            Reclassification(row.cuenta, row.servicio_sap, row.centro_beneficio or None, row.servicio_tb)
            for row in reclassifications.fillna({'centro_beneficio': ''}).itertuples(index=False)
        ],
        # An empty asset is the general row of the account + service
        categorias={
            Combination(row.cuenta, row.servicio, row.asset): row.categoria
            for row in categories.itertuples(index=False)
        },
    )
