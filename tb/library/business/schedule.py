# ==============================================================================
# library/business/schedule.py
# ------------------------------------------------------------------------------
# Planning of the daily download from SAP (spec, phase IV), with no input/output
# of its own: which months are downloaded on a given day (A3) and which TB
# upload of Airflows each month goes to (A4, A5).
#
# Copyright Oimbra Technology 2026
# ==============================================================================

# Standard libraries
from datetime import date
from typing import NamedTuple, TypedDict


# A month to download, AAAA-MM; the current month may have no postings yet (day 1), the previous one may not
class DownloadMonth(NamedTuple):
    month: str
    may_be_empty: bool


# What the download does with the TB upload of a company and month
CREATE = 'crear'
REPLACE = 'sustituir'
SKIP = 'saltar'

# Status of an upload the batch is processing, as in the enum Tb_upload_status
STATUS_PROCESSING = 'procesando'


# The action on the upload of a month and, when it is an existing one, its id; warning is for the log
class UploadChoice(NamedTuple):
    action: str
    id: int | None = None
    warning: str | None = None


# A row of Batch.Tb_upload as Airflows returns it; Company and Months are empty until it is downloaded or processed
class UploadRow(TypedDict):
    id: int
    Company: str | None
    Months: str | None
    Status: str


# Name of the file of a company and month downloaded from SAP
def export_name(company: str, month: str) -> str:
    return f'TB - {company} - {month} (SAP).xlsx'


# Choose the upload of a company and month among the rows of Batch.Tb_upload
def choose_upload(uploads: list[UploadRow], company: str, month: str) -> UploadChoice:
    matching = [row for row in uploads if row['Company'] == company and row['Months'] == month]
    if not matching:
        return UploadChoice(CREATE)
    ids = sorted(row['id'] for row in matching)
    newest = ids[-1]
    if any(row['id'] == newest and row['Status'] == STATUS_PROCESSING for row in matching):
        return UploadChoice(
            SKIP,
            newest,
            f'{company} {month}: la carga {newest} está en procesando; se descarga en la próxima ejecución.',
        )
    warning = None
    if len(ids) > 1:
        warning = f'{company} {month}: varias cargas ({", ".join(map(str, ids))}); se usa la {newest}.'
    return UploadChoice(REPLACE, newest, warning)


# Months of the daily download: the previous month and the current one, in that order
def months_to_download(today: date) -> list[DownloadMonth]:
    previous = date(today.year - 1, 12, 1) if today.month == 1 else date(today.year, today.month - 1, 1)
    return [
        DownloadMonth(previous.strftime('%Y-%m'), may_be_empty=False),
        DownloadMonth(today.strftime('%Y-%m'), may_be_empty=True),
    ]
