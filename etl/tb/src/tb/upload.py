# ==============================================================================
# tb/upload.py
# ------------------------------------------------------------------------------
# Processing of one TB upload of Airflows (Batch.Tb_upload, spec decisions F2
# and F3), with no input/output of its own: it takes the bytes of the SAP
# export and a function that fetches the master workbook of a company (from
# Admin.Files in the batch), and returns what the batch writes in the upload:
# status, Log, company, months, rows and totals, and, when it is good, its own
# export with the TB rows in a sheet TB (ticket 09a). Every problem, including
# those of the master workbook, is collected into the Log; nothing raises.
#
# Copyright Oimbra Technology 2026
# ==============================================================================

# Standard libraries
import zipfile
from collections.abc import Callable
from dataclasses import dataclass
from io import BytesIO
from typing import BinaryIO, NamedTuple

# Third-party libraries
from openpyxl.utils.exceptions import InvalidFileException

# Application libraries
from tb.errors import ReadError
from tb.export import read_export
from tb.maestro import maestro_name, read_maestro
from tb.run import error_lines, month_totals, summary_lines, transform_and_validate
from tb.workbook import add_tb_sheet

# Status of an upload once processed, as in the enum Tb_upload_status
STATUS_OK = 'ok'
STATUS_ERROR = 'error'

# Second half of the first line of the Log of a failed upload
NOTHING_LOADED = 'no se ha cargado nada'

# What openpyxl raises on a file that is not an xlsx workbook; reading the master workbook, pandas adds ValueError
NOT_A_WORKBOOK = (zipfile.BadZipFile, InvalidFileException)


# Master workbook of a company as stored in Admin.Files: its content and the date of its last change
class MaestroWorkbook(NamedTuple):
    content: bytes
    modified: str


# What the batch writes in the upload; months, rows and totals stay empty when they are not known, and the workbook
# (the export with its TB sheet) is only there when the upload is good
@dataclass(frozen=True)
class UploadResult:
    status: str
    company: str | None
    months: str | None
    rows: int | None
    totals: str | None
    log: str
    workbook: bytes | None = None


# Process one upload: read the export, fetch the master workbook of its company, transform and validate
def process_upload(export_source: BinaryIO, fetch_maestro: Callable[[str], MaestroWorkbook]) -> UploadResult:
    errors: list[str] = []
    company = months = maestro_line = None

    # The export, which also gives the company and the months; its bytes are kept to add the TB sheet
    content = export_source.read()
    export = None
    try:
        export = read_export(BytesIO(content))
    except ReadError as error:
        errors.extend(error.errors)
    except NOT_A_WORKBOOK as error:
        errors.append(f'No se puede abrir el export como libro Excel (xlsx): {error}.')
    if export is not None:
        companies = sorted(export['empresa'].unique())
        months = ', '.join(sorted(export['mes'].unique())) or None
        if len(companies) > 1:
            errors.append(
                f'El export tiene varias empresas ({', '.join(companies)}). Exporta de SAP una sola sociedad.',
            )
        elif not companies:
            errors.append('El export no tiene ninguna línea con empresa.')
        else:
            company = companies[0]

    # The master workbook of that company, read in every upload
    config = None
    if company is not None:
        try:
            maestro = fetch_maestro(company)
            maestro_line = f'Hoja maestra: {maestro_name(company)}, modificada el {maestro.modified}.'
            config = read_maestro(BytesIO(maestro.content), company)
        except ReadError as error:
            errors.extend(error.errors)
        except (*NOT_A_WORKBOOK, ValueError) as error:
            errors.append(f'No se puede abrir la hoja maestra {maestro_name(company)} como libro Excel: {error}.')

    # Transform, then validate the output schema and the balance
    if config is not None:
        result, run_errors = transform_and_validate(export, config)
        errors.extend(run_errors)

    # Any error: nothing is loaded, and the whole list goes to the Log
    if errors:
        log = error_lines(errors, NOTHING_LOADED)
        if maestro_line:
            log.append(maestro_line)
        return UploadResult(STATUS_ERROR, company, months, None, None, '\n'.join(log))

    # Summary: master workbook used, rows, keys and total per month
    log = [
        maestro_line,
        f'Empresa: {company}',
        f'Meses: {months}',
        *summary_lines(result),
    ]
    return UploadResult(
        status=STATUS_OK,
        company=company,
        months=months,
        rows=len(result.rows),
        totals='; '.join(month_totals(result.rows)),
        log='\n'.join(log),
        workbook=add_tb_sheet(content, result.rows),
    )


# Result of an upload that failed outside the transformation (download, Airflows): only the errors are known
def failed_upload(errors: list[str]) -> UploadResult:
    return UploadResult(STATUS_ERROR, None, None, None, None, '\n'.join(error_lines(errors, NOTHING_LOADED)))
