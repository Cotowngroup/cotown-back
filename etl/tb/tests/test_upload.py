# ==============================================================================
# tests/test_upload.py
# ------------------------------------------------------------------------------
# Tests of the processing of one TB upload (Batch.Tb_upload, decisions F2 and
# F3): from the bytes of the SAP export and the master workbook of its company
# to the status, Log, company, months, rows and totals the batch writes. The
# master workbook comes from a stand-in for Admin.Files; the expected figures
# are those of the phase I command line with the same files (932 rows).
#
# Copyright Oimbra Technology 2026
# ==============================================================================

# Standard libraries
from io import BytesIO
from pathlib import Path

# Third-party libraries
import openpyxl

# Application libraries
from tb.errors import ReadError
from tb.upload import MaestroWorkbook, UploadResult, process_upload

# Folder of the tb package, where the master workbook and the data live
TB_DIR = Path(__file__).resolve().parents[1]

# SAP export of September 2026 and the master workbook of CTS00
EXPORT = TB_DIR / 'data' / 'TB - CTS - SEP.xlsx'
MAESTRO = TB_DIR / 'maestro_tb_CTS00.xlsx'

# Date of the master workbook in Admin.Files
MODIFIED = '2026-11-24T16:30:00'


# Stand-in for Admin.Files: the given workbook for one company, nothing for any other
def admin_files(content: bytes, company: str = 'CTS00'):
    asked = []

    def fetch(empresa: str) -> MaestroWorkbook:
        asked.append(empresa)
        if empresa != company:
            raise ReadError([f'No hay hoja maestra para {empresa}.'])
        return MaestroWorkbook(content=content, modified=MODIFIED)

    fetch.asked = asked
    return fetch


# Workbook in memory with a single sheet and the given rows
def workbook(*rows: list) -> bytes:
    book = openpyxl.Workbook()
    for row in rows:
        book.active.append(row)
    stream = BytesIO()
    book.save(stream)
    return stream.getvalue()


# A good export with the master workbook of its company: ok, with the summary and the workbook date in the Log
def test_good_export_is_ok_with_summary():
    result = process_upload(BytesIO(EXPORT.read_bytes()), admin_files(MAESTRO.read_bytes()))

    assert result.status == 'ok'
    assert (result.company, result.months, result.rows) == ('CTS00', '2026-08, 2026-09', 932)
    assert result.totals == '2026-08: 0,00; 2026-09: 0,00'
    assert 'Hoja maestra: Maestro TB CTS00, modificada el 2026-11-24T16:30:00.' in result.log
    assert 'Claves: 576' in result.log


# A good upload gives back its own export with the TB rows in a sheet TB, after the export sheet
def test_good_export_gives_back_the_export_with_the_tb_sheet():
    result = process_upload(BytesIO(EXPORT.read_bytes()), admin_files(MAESTRO.read_bytes()))

    book = openpyxl.load_workbook(BytesIO(result.workbook), read_only=True)
    assert book.sheetnames == ['Exportac. 21.10.2026 12.15.22', 'TB']
    assert len(list(book['TB'].iter_rows(min_row=2, values_only=True))) == 932


# The errors of the master workbook go to the Log of the upload, all at once and with the workbook date
def test_master_workbook_errors_go_to_the_log():
    broken = workbook(['nada'])

    result = process_upload(BytesIO(EXPORT.read_bytes()), admin_files(broken))

    assert result.status == 'error'
    assert (result.company, result.months, result.rows, result.totals) == ('CTS00', '2026-08, 2026-09', None, None)
    assert 'Hoja maestra: Maestro TB CTS00, modificada el 2026-11-24T16:30:00.' in result.log
    assert 'Falta la pestaña Reglas en la hoja maestra.' in result.log
    assert 'Falta la pestaña Categorias en la hoja maestra.' in result.log
    assert result.workbook is None


# Without a master workbook for the company the upload is an error that names the company
def test_missing_master_workbook_is_an_error():
    fetch = admin_files(MAESTRO.read_bytes(), company='VDS00')

    result = process_upload(BytesIO(EXPORT.read_bytes()), fetch)

    assert result.status == 'error'
    assert result.company == 'CTS00'
    assert 'No hay hoja maestra para CTS00.' in result.log
    assert fetch.asked == ['CTS00']


# A file that is not a Trial Balance export is an error, and no master workbook is fetched
def test_file_that_is_not_an_export_is_an_error():
    fetch = admin_files(MAESTRO.read_bytes())

    result = process_upload(BytesIO(workbook(['Otra cosa'])), fetch)

    assert result == UploadResult(
        status='error',
        company=None,
        months=None,
        rows=None,
        totals=None,
        log='1 errores; no se ha cargado nada:\n'
        '- No se encuentra la fila de cabecera con "Cuenta de mayor": no parece un export de SAP.',
    )
    assert fetch.asked == []


# A file that cannot be opened as a workbook is an error too, not a crash of the batch
def test_file_that_is_not_a_workbook_is_an_error():
    result = process_upload(BytesIO(b'%PDF-1.7 not a workbook'), admin_files(MAESTRO.read_bytes()))

    assert result.status == 'error'
    assert 'No se puede abrir el export como libro Excel' in result.log


# An export with several companies is an error before fetching any master workbook
def test_export_with_several_companies_is_an_error():
    fetch = admin_files(MAESTRO.read_bytes())
    rows = [
        [None, 'Trial Balance'],
        [None, 'Empresa', '', 'Cuenta de mayor', '', 'Producto', '', 'Centro de beneficio', '009.2026'],
        *[[None, company, 'X', '705000', 'T', 'S_70504', 'T', 'CTS01', 1.0] for company in ('CTS00', 'VDS00')],
    ]

    result = process_upload(BytesIO(workbook(*rows)), fetch)

    assert result.status == 'error'
    assert 'El export tiene varias empresas (CTS00, VDS00)' in result.log
    assert fetch.asked == []
