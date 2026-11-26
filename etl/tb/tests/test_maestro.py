# ==============================================================================
# tests/test_maestro.py
# ------------------------------------------------------------------------------
# Tests of the reader of the master workbook: Cuentas gives the CCAA and the
# excluded accounts, Categorias the general rows (no asset) and the asset
# exceptions, and every problem of those sheets is reported at once.
#
# Copyright Oimbra Technology 2026
# ==============================================================================

# Standard libraries
from io import BytesIO

# Third-party libraries
import openpyxl
import pytest

# Application libraries
from tb.config import AnnualAccounts, Combination
from tb.errors import ReadError
from tb.maestro import read_maestro

# Building centre pattern of CTS00
CTS00_PATTERN = r'^CTS[A-Z]{3}(?P<edificio>[A-Z]{3})(?P<numero>\d{3,4})(_.*)?$'


# Master workbook in memory with the given Cuentas and Categorias rows and minimal other sheets
def maestro(cuentas: list[list], categorias: list[list]) -> BytesIO:
    sheets = {
        'Reglas': [['patron_edificio', 'digitos_numero'], [CTS00_PATTERN, '4']],
        'Cuentas': [['cuenta', 'ccaa1', 'ccaa2', 'excluida', 'descripcion', 'motivo'], *cuentas],
        'Equivalencias': [['centro_beneficio', 'asset', 'motivo'], ['CTS01', 'Manco', 'Sociedad']],
        'Reclasificaciones': [['cuenta', 'servicio_sap', 'centro_beneficio', 'servicio_tb', 'motivo']],
        'Categorias': [['cuenta', 'servicio', 'asset', 'categoria', 'descripcion', 'motivo'], *categorias],
    }
    book = openpyxl.Workbook()
    book.remove(book.active)
    for name, rows in sheets.items():
        sheet = book.create_sheet(name)
        for row in rows:
            sheet.append(row)
    stream = BytesIO()
    book.save(stream)
    stream.seek(0)
    return stream


# Cuentas: CCAA per account, excluded accounts apart; Categorias: general rows with an empty asset, plus exceptions
def test_accounts_and_categories_are_read():
    source = maestro(
        cuentas=[
            ['705000', 'PL', 'Revenue', None, 'PRESTACIONES', None],
            ['570000', None, None, 'Sí', 'CAJA', 'Neta 0'],
        ],
        categorias=[
            ['705000', 'S_70504', None, 'Checkout Cleaning', 'LIMPIEZA', None],
            ['705000', 'S_70504', 'BAI0033', 'Cleaning building', None, 'Excepción'],
        ],
    )

    config = read_maestro(source, 'CTS00')

    assert config.cuentas == {'705000': AnnualAccounts('PL', 'Revenue')}
    assert config.excluidas == ['570000']
    assert config.categorias == {
        Combination('705000', 'S_70504', ''): 'Checkout Cleaning',
        Combination('705000', 'S_70504', 'BAI0033'): 'Cleaning building',
    }


# Every problem of Cuentas and Categorias at once: missing CCAA, unknown excluida value, repeated rows
def test_account_and_category_errors_are_all_reported():
    source = maestro(
        cuentas=[
            ['705000', 'PL', None, None, None, None],
            ['629000', 'PL', 'External Services', 'quizá', None, None],
            ['629000', 'PL', 'External Services', None, None, None],
        ],
        categorias=[
            ['705000', 'S_70504', None, 'Checkout Cleaning', None, None],
            ['705000', 'S_70504', None, 'Cleaning', None, None],
            ['705000', 'S_70505', None, None, None, None],
        ],
    )

    with pytest.raises(ReadError) as raised:
        read_maestro(source, 'CTS00')

    assert raised.value.errors == [
        'Cuentas: la cuenta 629000 está repetida. Deja una sola fila.',
        'Cuentas: excluida de la cuenta 629000 debe ser "sí" o estar vacía, no "quizá".',
        'Cuentas: a la cuenta 705000 le falta ccaa1 o ccaa2. Complétala o márcala como excluida.',
        'Categorias: fila incompleta (cuenta 705000, servicio S_70505, categoria (vacío)).',
        'Categorias: 705000 S_70504 tiene repetida la fila general (sin asset). Deja una sola fila.',
    ]
