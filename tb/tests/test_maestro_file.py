# ==============================================================================
# tests/test_maestro_file.py
# ------------------------------------------------------------------------------
# Unit tests of the choice of the master workbook among the Admin.Files
# records of Airflows (spec decision F3): exactly one record named
# "Maestro TB <empresa>", dated by its last change.
#
# Copyright Oimbra Technology 2026
# ==============================================================================

# Third-party libraries
import pytest

# Application libraries
from library.business.errors import ReadError
from library.business.maestro import MaestroFile, maestro_name, select_maestro


# The record of the company is named "Maestro TB <empresa>"
def test_name_of_the_master_workbook_record():
    assert maestro_name('CTS00') == 'Maestro TB CTS00'


# The single record of the company is chosen, dated by its last update
def test_single_record_is_chosen_with_its_update_date():
    records = [
        {'id': 17, 'Name': 'Budget LAU + Retail 2026', 'Created_at': '2026-01-10T09:00:00', 'Updated_at': None},
        {
            'id': 18,
            'Name': 'Maestro TB CTS00',
            'Created_at': '2026-11-20T10:00:00',
            'Updated_at': '2026-11-24T16:30:00',
        },
    ]

    assert select_maestro(records, 'CTS00') == MaestroFile(id=18, modified='2026-11-24T16:30:00')


# A record never changed since it was uploaded is dated by its creation
def test_record_never_updated_is_dated_by_its_creation():
    records = [{'id': 18, 'Name': 'Maestro TB CTS00', 'Created_at': '2026-11-20T10:00:00', 'Updated_at': None}]

    assert select_maestro(records, 'CTS00') == MaestroFile(id=18, modified='2026-11-20T10:00:00')


# Without a record for the company there is no configuration: error naming the record to create
def test_missing_record_is_an_error():
    records = [{'id': 18, 'Name': 'Maestro TB CTS00', 'Created_at': '2026-11-20T10:00:00', 'Updated_at': None}]

    with pytest.raises(ReadError) as raised:
        select_maestro(records, 'VDS00')

    assert raised.value.errors == [
        'No hay hoja maestra para VDS00: falta el fichero "Maestro TB VDS00" en Ficheros (Admin.Files) de Airflows.',
    ]


# Two records with the same name are ambiguous: error, without choosing one
def test_duplicated_record_is_an_error():
    records = [
        {'id': 18, 'Name': 'Maestro TB CTS00', 'Created_at': '2026-11-20T10:00:00', 'Updated_at': None},
        {'id': 19, 'Name': 'Maestro TB CTS00', 'Created_at': '2026-11-21T10:00:00', 'Updated_at': None},
    ]

    with pytest.raises(ReadError) as raised:
        select_maestro(records, 'CTS00')

    assert raised.value.errors == [
        'Hay 2 ficheros "Maestro TB CTS00" en Ficheros (Admin.Files) de Airflows (ids 18, 19): deja solo uno.',
    ]
