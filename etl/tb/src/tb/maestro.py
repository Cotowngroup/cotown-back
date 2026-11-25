# ==============================================================================
# tb/maestro.py
# ------------------------------------------------------------------------------
# Reader of a company's master workbook (maestro_tb_<empresa>.xlsx): one sheet
# per configuration table, every cell read as text. Sheets whose name starts
# with _ are notes and are ignored. Takes a binary stream, so the workbook can
# come from disk or from Airflows (Admin.Files). The company is not in the
# workbook: the caller passes it.
#
# Copyright Oimbra Technology 2026
# ==============================================================================

# Standard libraries
import re
from typing import BinaryIO

# Third-party libraries
import pandas as pd

# Application libraries
from tb.config import Category, Config
from tb.errors import ReadError

# Columns the transformation needs from each sheet; other columns (motivo, descripcion) are informative
REQUIRED_COLUMNS = {
    'Reglas': ['patron_edificio', 'digitos_numero'],
    'Equivalencias': ['centro_beneficio', 'asset'],
    'Mapping': ['servicio', *Category._fields],
}


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
    equivalences = sheets['Equivalencias'].dropna(subset=['centro_beneficio', 'asset'], how='all')
    mapping = sheets['Mapping'].dropna(subset=['servicio'])
    equivalences['centro_beneficio'] = equivalences['centro_beneficio'].str.strip()
    mapping['servicio'] = mapping['servicio'].str.strip()

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

    # Equivalencias: one asset per profit centre
    incomplete = equivalences[equivalences[['centro_beneficio', 'asset']].isna().any(axis=1)]
    for row in incomplete.fillna('(vacío)').itertuples(index=False):
        errors.append(f'Equivalencias: fila incompleta (centro_beneficio {row.centro_beneficio}, asset {row.asset}).')
    for centre in equivalences.loc[equivalences['centro_beneficio'].duplicated(), 'centro_beneficio'].unique():
        errors.append(f'Equivalencias: el centro {centre} está repetido. Deja una sola fila.')

    # Mapping: one complete row per service
    for service in mapping.loc[mapping[list(Category._fields)].isna().any(axis=1), 'servicio']:
        errors.append(f'Mapping: al servicio {service} le falta categoria, ccaa1 o ccaa2.')
    for service in mapping.loc[mapping['servicio'].duplicated(), 'servicio'].unique():
        errors.append(f'Mapping: el servicio {service} está repetido. Deja una sola fila.')
    if errors:
        raise ReadError(errors)

    # Configuration of the company
    return Config(
        empresa=empresa,
        patron_edificio=rules['patron_edificio'].iloc[0],
        digitos_numero=int(rules['digitos_numero'].iloc[0]),
        equivalencias=dict(zip(equivalences['centro_beneficio'], equivalences['asset'], strict=True)),
        mapping={
            row.servicio: Category(row.categoria, row.ccaa1, row.ccaa2)
            for row in mapping.itertuples(index=False)
        },
    )
