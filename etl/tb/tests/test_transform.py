# ==============================================================================
# tests/test_transform.py
# ------------------------------------------------------------------------------
# Unit tests of the pure transformation: canonical export rows and an in-memory
# configuration in, TB rows and the full list of errors out. No files involved.
#
# Copyright Oimbra Technology 2026
# ==============================================================================

# Standard libraries
from dataclasses import replace

# Third-party libraries
import pandas as pd
import pytest

# Application libraries
from tb.config import AnnualAccounts, Combination, Config, Reclassification
from tb.transform import TransformResult, transform

# Building centre pattern of CTS00, as in the Reglas sheet of the master workbook
CTS00_PATTERN = r'^CTS[A-Z]{3}(?P<edificio>[A-Z]{3})(?P<numero>\d{3,4})(_.*)?$'


# Build a canonical export line per month from a few overridable fields
def build_line(**fields) -> list[dict]:
    base = {
        'empresa': 'CTS00',
        'cuenta': '705000',
        'texto_cuenta': 'PRESTACIONES DE SERVICIOS',
        'producto': 'S_70504',
        'texto_producto': 'LIMPIEZA CHECK OUT',
        'centro_beneficio': 'CTSBCNBAI0033_04.01',
    }
    amounts = fields.pop('amounts', {'2026-09': -314.04})
    base.update(fields)
    return [{**base, 'mes': month, 'importe': amount} for month, amount in amounts.items()]


# Canonical export DataFrame from several lines
def build_export(*lines: list[dict]) -> pd.DataFrame:
    return pd.DataFrame([row for rows in lines for row in rows])


# CTS00 configuration: a few Cuentas, Equivalencias and general Categorias; no excluded accounts or Reclasificaciones
def build_config(**overrides) -> Config:
    config = Config(
        empresa='CTS00',
        patron_edificio=CTS00_PATTERN,
        digitos_numero=4,
        excluidas=[],
        cuentas={
            '705000': AnnualAccounts('PL', 'Revenue'),
            '629000': AnnualAccounts('PL', 'External Services'),
        },
        equivalencias={'CTS01': 'Manco', 'CTSBCNCON0012': 'CCD0012', 'CTSMADDCT075': 'DCT075'},
        reclasificaciones=[],
        categorias={
            Combination('705000', 'S_70504', ''): 'Checkout Cleaning Services (Final cleaning)',
            Combination('629000', '629000', ''): 'Other expenses',
            Combination('705000', 'S_70505', ''): 'Cleaning Services',
        },
    )
    return replace(config, **overrides)


# Output rows as plain dicts, to compare against literal expectations
def to_records(result: TransformResult) -> list[dict]:
    return result.rows.to_dict('records')


# A service line becomes one TB row with the key of TB!K
def test_service_line_becomes_tb_row():
    result = transform(build_export(build_line()), build_config())

    assert result.errors == []
    assert to_records(result) == [
        {
            'empresa': 'CTS00',
            'cuenta': '705000',
            'servicio': 'S_70504',
            'descripcion': 'LIMPIEZA CHECK OUT',
            'asset': 'BAI0033',
            'categoria': 'Checkout Cleaning Services (Final cleaning)',
            'ccaa1': 'PL',
            'ccaa2': 'Revenue',
            'budget': None,
            'clave': '705000 S_70504 BAI0033 Checkout Cleaning Services (Final cleaning)',
            'mes': '2026-09',
            'importe': -314.04,
        },
    ]


# Without an S_ product (# or a fixed-asset code), the service and the description come from the account
def test_non_service_product_uses_account():
    lines = build_export(
        build_line(cuenta='629000', texto_cuenta='OTROS SERVICIOS', producto='#', texto_producto='Sin asignar'),
        build_line(cuenta='629000', texto_cuenta='OTROS SERVICIOS', producto='100003019', texto_producto='PORTATIL'),
    )

    result = transform(lines, build_config())

    assert result.errors == []
    assert [(row['servicio'], row['descripcion'], row['clave']) for row in to_records(result)] == [
        ('629000', 'OTROS SERVICIOS', '629000 629000 BAI0033 Other expenses'),
    ]


# A key with several descriptions takes the one of its first line in export order
def test_description_of_first_line():
    lines = build_export(
        build_line(texto_producto='LIMPIEZA CHECK OUT', amounts={'2026-09': -10.0}),
        build_line(texto_producto='LIMPIEZA SALIDA', amounts={'2026-08': -5.0, '2026-09': -2.5}),
    )

    result = transform(lines, build_config())

    assert [(row['mes'], row['descripcion'], row['importe']) for row in to_records(result)] == [
        ('2026-09', 'LIMPIEZA CHECK OUT', -12.5),
        ('2026-08', 'LIMPIEZA CHECK OUT', -5.0),
    ]


# The asset comes from the profit centre: exact equivalence, base equivalence, building pattern; AT- is dropped first
@pytest.mark.parametrize(
    ('centre', 'asset'),
    [
        ('CTS01', 'Manco'),
        ('CTSBCNCON0012_BJ.01', 'CCD0012'),
        ('CTSBCNCON0012', 'CCD0012'),
        ('CTSMADDCT075_01.IZ', 'DCT075'),
        ('CTSBCNBAI0033', 'BAI0033'),
        ('CTSMADGTF038_PB.IZ', 'GTF0038'),
        ('AT-CTSBCNSAR0326', 'SAR0326'),
        ('AT-CTS01', 'Manco'),
    ],
)
def test_asset_from_profit_centre(centre, asset):
    result = transform(build_export(build_line(centro_beneficio=centre)), build_config())

    assert result.errors == []
    assert [row['asset'] for row in to_records(result)] == [asset]


# A profit centre that matches no equivalence nor the pattern is an error that names it, and nothing is output
def test_profit_centre_without_asset_is_error():
    lines = build_export(build_line(centro_beneficio='CTS0000XYZ'), build_line(centro_beneficio='CTSBCNBAI0033'))

    result = transform(lines, build_config())

    assert result.rows.empty
    assert len(result.errors) == 1
    assert 'CTS0000XYZ' in result.errors[0]
    assert 'Equivalencias' in result.errors[0]


# A service without a row in Categorias is an error that names it and points to Categorias
def test_service_without_category_is_error():
    result = transform(build_export(build_line(producto='S_99999', texto_producto='NUEVO SERVICIO')), build_config())

    assert result.rows.empty
    assert len(result.errors) == 1
    assert 'S_99999' in result.errors[0]
    assert 'Categorias' in result.errors[0]


# Every problem is reported in the same run, once per centre or service
def test_all_errors_in_one_run():
    lines = build_export(
        build_line(centro_beneficio='CTS0000XYZ'),
        build_line(centro_beneficio='CTS0000XYZ', cuenta='629000', producto='#'),
        build_line(producto='S_99999'),
        build_line(producto='S_88888', centro_beneficio='CTSZZZ'),
    )

    result = transform(lines, build_config())

    assert result.rows.empty
    assert len(result.errors) == 4
    for code in ('CTS0000XYZ', 'CTSZZZ', 'S_99999', 'S_88888'):
        assert any(code in error for error in result.errors), code


# An export with several companies is an error that names them
def test_several_companies_is_error():
    result = transform(build_export(build_line(), build_line(empresa='CTS01')), build_config())

    assert result.rows.empty
    assert len(result.errors) == 1
    assert 'CTS00' in result.errors[0]
    assert 'CTS01' in result.errors[0]


# The export company must be the one of the master workbook
def test_company_without_master_is_error():
    result = transform(build_export(build_line(empresa='CTS01')), build_config())

    assert result.rows.empty
    assert result.errors == [
        'La empresa del export (CTS01) no es la de la hoja maestra (CTS00). Usa maestro_tb_CTS01.xlsx.',
    ]


# A line with every period at 0 is dropped before anything is resolved, so it raises no error
def test_zero_line_is_ignored():
    lines = build_export(
        build_line(),
        build_line(centro_beneficio='CTS0000XYZ', amounts={'2026-08': 0.0, '2026-09': 0.0}),
    )

    result = transform(lines, build_config())

    assert result.errors == []
    assert [row['asset'] for row in to_records(result)] == ['BAI0033']


# Export lines that differ only in dimensions the TB does not use (cost centre, project task) are summed first: if
# they net 0 in the month, they need no asset or category
def test_lines_netting_zero_across_unused_dimensions_are_ignored():
    lines = build_export(
        build_line(),
        build_line(producto='S_99999', centro_beneficio='CTS0000XYZ', amounts={'2026-09': 21.78}),
        build_line(producto='S_99999', centro_beneficio='CTS0000XYZ', amounts={'2026-09': -21.78}),
    )

    result = transform(lines, build_config())

    assert result.errors == []
    assert [row['asset'] for row in to_records(result)] == ['BAI0033']


# Amounts are rounded to 2 decimals after summing, and key-months that net to 0 are not output
def test_rounding_and_zero_sums():
    lines = build_export(
        build_line(amounts={'2026-08': 0.1, '2026-09': 100.0}),
        build_line(amounts={'2026-08': 0.2, '2026-09': -100.0}),
        build_line(amounts={'2026-08': -0.3}),
        build_line(centro_beneficio='CTSBCNBAI0034', amounts={'2026-08': 10.006, '2026-09': 1.111}),
    )

    result = transform(lines, build_config())

    assert [(row['asset'], row['mes'], row['importe']) for row in to_records(result)] == [
        ('BAI0034', '2026-08', 10.01),
        ('BAI0034', '2026-09', 1.11),
    ]


# The company check sees every line, also those with every period at 0
def test_several_companies_with_zero_line_is_error():
    lines = build_export(build_line(), build_line(empresa='CTS01', amounts={'2026-09': 0.0}))

    result = transform(lines, build_config())

    assert result.rows.empty
    assert len(result.errors) == 1
    assert 'CTS01' in result.errors[0]


# Combination of the default line (705000 S_70504 in BAI0033)
BAI0033_CLEANING = Combination('705000', 'S_70504', 'BAI0033')


# The general row of account + service gives the category to any asset, with the CCAA of the account
def test_general_category_with_ccaa_of_the_account():
    lines = build_export(build_line(), build_line(centro_beneficio='CTSMADGTF038'))

    result = transform(lines, build_config())

    assert result.errors == []
    assert [(row['asset'], row['categoria'], row['ccaa1'], row['ccaa2']) for row in to_records(result)] == [
        ('BAI0033', 'Checkout Cleaning Services (Final cleaning)', 'PL', 'Revenue'),
        ('GTF0038', 'Checkout Cleaning Services (Final cleaning)', 'PL', 'Revenue'),
    ]


# A row with the asset is an exception that wins over the general row, only for that asset
def test_asset_exception_wins_over_general_category():
    config = build_config(categorias={**build_config().categorias, BAI0033_CLEANING: 'Cleaning building'})
    lines = build_export(build_line(), build_line(centro_beneficio='CTSMADGTF038'))

    result = transform(lines, config)

    assert result.errors == []
    assert [(row['asset'], row['clave']) for row in to_records(result)] == [
        ('BAI0033', '705000 S_70504 BAI0033 Cleaning building'),
        ('GTF0038', '705000 S_70504 GTF0038 Checkout Cleaning Services (Final cleaning)'),
    ]


# A service known under another account has no category in this one: the category goes by account + service
def test_service_of_another_account_is_error():
    result = transform(build_export(build_line(cuenta='629000', producto='S_70504')), build_config())

    assert result.rows.empty
    assert len(result.errors) == 1
    for text in ('S_70504', '629000', 'Categorias'):
        assert text in result.errors[0], text


# An account missing from Cuentas is an error that names it with its text and points to Cuentas
def test_account_without_ccaa_is_error():
    config = build_config(categorias={**build_config().categorias, Combination('706000', 'S_70504', ''): 'Fees'})

    result = transform(build_export(build_line(cuenta='706000', texto_cuenta='OTROS INGRESOS')), config)

    assert result.rows.empty
    assert len(result.errors) == 1
    for text in ('706000', 'OTROS INGRESOS', 'Cuentas'):
        assert text in result.errors[0], text


# A general reclassification changes the service of every line of its account and SAP service
def test_general_reclassification():
    config = build_config(reclasificaciones=[Reclassification('705000', 'S_70504', None, 'S_70505')])
    lines = build_export(build_line(), build_line(centro_beneficio='CTSBCNBAI0034'))

    result = transform(lines, config)

    assert result.errors == []
    assert [(row['servicio'], row['asset'], row['categoria']) for row in to_records(result)] == [
        ('S_70505', 'BAI0033', 'Cleaning Services'),
        ('S_70505', 'BAI0034', 'Cleaning Services'),
    ]


# A reclassification by profit centre (clean, without AT-) only changes the lines of that centre
def test_reclassification_by_centre():
    config = build_config(reclasificaciones=[Reclassification('705000', 'S_70504', 'CTSBCNBAI0034', 'S_70505')])
    lines = build_export(build_line(), build_line(centro_beneficio='AT-CTSBCNBAI0034'))

    result = transform(lines, config)

    assert result.errors == []
    assert [(row['servicio'], row['asset']) for row in to_records(result)] == [
        ('S_70504', 'BAI0033'),
        ('S_70505', 'BAI0034'),
    ]


# A row with centre wins over a general row of the same account and service
def test_reclassification_by_centre_wins_over_general():
    config = build_config(
        reclasificaciones=[
            Reclassification('705000', 'S_70504', None, '629000'),
            Reclassification('705000', 'S_70504', 'CTSBCNBAI0034', 'S_70505'),
        ],
        categorias={**build_config().categorias, Combination('705000', '629000', ''): 'Other expenses'},
    )
    lines = build_export(build_line(), build_line(centro_beneficio='CTSBCNBAI0034'))

    result = transform(lines, config)

    assert result.errors == []
    assert [(row['servicio'], row['asset']) for row in to_records(result)] == [
        ('629000', 'BAI0033'),
        ('S_70505', 'BAI0034'),
    ]


# Two rows of the same level for the same line: error that names the line and the target services, no choice
def test_reclassification_conflict_is_error():
    config = build_config(
        reclasificaciones=[
            Reclassification('705000', 'S_70504', 'CTSBCNBAI0033_04.01', 'S_70505'),
            Reclassification('705000', 'S_70504', 'CTSBCNBAI0033_04.01', '629000'),
        ],
    )

    result = transform(build_export(build_line()), config)

    assert result.rows.empty
    assert len(result.errors) == 1
    for text in ('705000', 'S_70504', 'CTSBCNBAI0033_04.01', 'S_70505', '629000', 'Reclasificaciones'):
        assert text in result.errors[0], text


# A line whose account and service are in no row keeps its service, even if a row matches its service elsewhere
def test_line_without_reclassification():
    config = build_config(reclasificaciones=[Reclassification('629000', 'S_70504', None, 'S_70505')])

    result = transform(build_export(build_line()), config)

    assert result.errors == []
    assert [row['servicio'] for row in to_records(result)] == ['S_70504']


# An excluded account that nets 0 every month disappears, and its service needs no category
def test_excluded_account_is_dropped():
    config = build_config(excluidas=['570000'])
    lines = build_export(
        build_line(),
        build_line(cuenta='570000', producto='#', amounts={'2026-08': 50.0, '2026-09': 314.04}),
        build_line(cuenta='570000', producto='#', amounts={'2026-08': -50.0, '2026-09': -314.04}),
    )

    result = transform(lines, config)

    assert result.errors == []
    assert [row['cuenta'] for row in to_records(result)] == ['705000']


# An excluded account that does not net 0 in a month is an error with the account, the month and the amount
def test_excluded_account_not_netting_is_error():
    config = build_config(excluidas=['570000'])
    lines = build_export(
        build_line(),
        build_line(cuenta='570000', producto='#', amounts={'2026-08': 50.0, '2026-09': 314.04}),
        build_line(cuenta='570000', producto='#', amounts={'2026-08': -50.0, '2026-09': -14.04}),
    )

    result = transform(lines, config)

    assert result.rows.empty
    assert len(result.errors) == 1
    for text in ('570000', '2026-09', '300,00', 'Cuentas'):
        assert text in result.errors[0], text
