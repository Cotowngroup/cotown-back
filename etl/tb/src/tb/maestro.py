# ==============================================================================
# tb/maestro.py
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
from tb.config import Category, Combination, Config, Reclassification
from tb.errors import ReadError

# Columns the transformation needs from each sheet; other columns (motivo, descripcion) are informative
REQUIRED_COLUMNS = {
    'Reglas': ['patron_edificio', 'digitos_numero'],
    'Excluidas': ['cuenta'],
    'Equivalencias': ['centro_beneficio', 'asset'],
    'Reclasificaciones': list(Reclassification._fields),
    'Mapping': ['servicio', *Category._fields],
    'Categorias': [*Combination._fields, 'categoria'],
    'Referencia': [*Combination._fields, *Category._fields],
}


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

    # Codes without surrounding spaces; texts (categories) stay exactly as written, since they are part of TB!K
    rules = sheets['Reglas'].dropna(how='all')
    excluded = sheets['Excluidas']['cuenta'].dropna().str.strip()
    equivalences = sheets['Equivalencias'].dropna(subset=['centro_beneficio', 'asset'], how='all')
    reclassifications = sheets['Reclasificaciones'].dropna(subset=REQUIRED_COLUMNS['Reclasificaciones'], how='all')
    mapping = sheets['Mapping'].dropna(subset=['servicio'])
    equivalences['centro_beneficio'] = equivalences['centro_beneficio'].str.strip()
    for column in Reclassification._fields:
        reclassifications[column] = reclassifications[column].str.strip()
    mapping['servicio'] = mapping['servicio'].str.strip()
    categories_sheet = sheets['Categorias'].dropna(how='all', subset=REQUIRED_COLUMNS['Categorias'])
    reference_sheet = sheets['Referencia'].dropna(how='all', subset=REQUIRED_COLUMNS['Referencia'])
    for sheet in (categories_sheet, reference_sheet):
        for column in Combination._fields:
            sheet[column] = sheet[column].str.strip()

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

    # Excluidas: each account once
    for account in excluded[excluded.duplicated()].unique():
        errors.append(f'Excluidas: la cuenta {account} está repetida. Deja una sola fila.')

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

    # Mapping: one complete row per service
    for service in mapping.loc[mapping[list(Category._fields)].isna().any(axis=1), 'servicio']:
        errors.append(f'Mapping: al servicio {service} le falta categoria, ccaa1 o ccaa2.')
    for service in mapping.loc[mapping['servicio'].duplicated(), 'servicio'].unique():
        errors.append(f'Mapping: el servicio {service} está repetido. Deja una sola fila.')

    # Categorias: one complete row per combination
    incomplete = categories_sheet[REQUIRED_COLUMNS['Categorias']].isna().any(axis=1)
    for row in categories_sheet[incomplete].fillna(EMPTY).itertuples():
        errors.append(
            f'Categorias: fila incompleta ({row.cuenta} {row.servicio} {row.asset}, categoria {row.categoria}).'
        )
    for row in categories_sheet[categories_sheet.duplicated(subset=list(Combination._fields))].itertuples():
        errors.append(
            f'Categorias: la combinación {row.cuenta} {row.servicio} {row.asset} está repetida. Deja una sola fila.'
        )

    # Referencia: complete rows, one per combination and category
    incomplete = reference_sheet[REQUIRED_COLUMNS['Referencia']].isna().any(axis=1)
    for row in reference_sheet[incomplete].fillna(EMPTY).itertuples():
        errors.append(f'Referencia: fila incompleta ({row.cuenta} {row.servicio} {row.asset} {row.categoria}).')
    for row in reference_sheet[reference_sheet.duplicated(subset=[*Combination._fields, 'categoria'])].itertuples():
        errors.append(
            f'Referencia: la combinación {row.cuenta} {row.servicio} {row.asset} con categoría "{row.categoria}" '
            f'está repetida. Deja una sola fila.'
        )
    if errors:
        raise ReadError(errors)

    # Referencia grouped by combination, keeping the order of the sheet
    reference_categories: dict[Combination, list[Category]] = {}
    for row in reference_sheet.itertuples(index=False):
        combination = Combination(row.cuenta, row.servicio, row.asset)
        reference_categories.setdefault(combination, []).append(Category(row.categoria, row.ccaa1, row.ccaa2))

    # Configuration of the company
    return Config(
        empresa=empresa,
        patron_edificio=rules['patron_edificio'].iloc[0],
        digitos_numero=int(rules['digitos_numero'].iloc[0]),
        excluidas=list(excluded),
        equivalencias=dict(zip(equivalences['centro_beneficio'], equivalences['asset'], strict=True)),
        # An empty centre (NaN, or only spaces before the strip) means a general row
        reclasificaciones=[
            Reclassification(row.cuenta, row.servicio_sap, row.centro_beneficio or None, row.servicio_tb)
            for row in reclassifications.fillna({'centro_beneficio': ''}).itertuples(index=False)
        ],
        mapping={
            row.servicio: Category(row.categoria, row.ccaa1, row.ccaa2)
            for row in mapping.itertuples(index=False)
        },
        categorias={
            Combination(row.cuenta, row.servicio, row.asset): row.categoria
            for row in categories_sheet.itertuples(index=False)
        },
        referencia=reference_categories,
    )
