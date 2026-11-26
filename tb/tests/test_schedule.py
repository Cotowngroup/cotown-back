# ==============================================================================
# tests/test_schedule.py
# ------------------------------------------------------------------------------
# Tests of the planning of the daily download from SAP (spec, phase IV): which
# months are downloaded on a given day (A3) and which TB upload each month
# goes to (A4, A5).
#
# Copyright Oimbra Technology 2026
# ==============================================================================

# Standard libraries
from datetime import date

# Application libraries
from library.business.schedule import (
    CREATE,
    REPLACE,
    SKIP,
    DownloadMonth,
    UploadRow,
    choose_upload,
    export_name,
    months_to_download,
)


# A row of Batch.Tb_upload as Airflows returns it
def upload(id_: int, months: str | None, status: str = 'ok', company: str | None = 'CTS00') -> UploadRow:
    return {'id': id_, 'Company': company, 'Months': months, 'Status': status}


# The previous month must have postings; the current one may still have none
def test_previous_and_current_month():
    assert months_to_download(date(2026, 11, 26)) == [
        DownloadMonth('2026-10', may_be_empty=False),
        DownloadMonth('2026-11', may_be_empty=True),
    ]


# On day 1 the new month is the current one
def test_first_day_of_month():
    assert months_to_download(date(2026, 12, 1)) == [
        DownloadMonth('2026-11', may_be_empty=False),
        DownloadMonth('2026-12', may_be_empty=True),
    ]


# In January the previous month is December of the year before
def test_january():
    assert months_to_download(date(2027, 1, 15)) == [
        DownloadMonth('2026-12', may_be_empty=False),
        DownloadMonth('2027-01', may_be_empty=True),
    ]


# No upload of that company and month: a new one is created
def test_no_upload_creates_one():
    uploads = [upload(12, '2026-09'), upload(14, '2026-11', company='CTS01')]
    choice = choose_upload(uploads, 'CTS00', '2026-11')
    assert choice.action == CREATE
    assert choice.id is None


# The upload of that company and month, whatever its status but procesando, gets the new file
def test_one_upload_is_replaced():
    uploads = [upload(12, '2026-09'), upload(13, '2026-10', status='error')]
    assert choose_upload(uploads, 'CTS00', '2026-10') == (REPLACE, 13, None)


# Several uploads of that company and month: the newest one, with a warning naming the others
def test_several_uploads_newest_with_warning():
    uploads = [upload(13, '2026-10'), upload(21, '2026-10'), upload(17, '2026-10')]
    choice = choose_upload(uploads, 'CTS00', '2026-10')
    assert (choice.action, choice.id) == (REPLACE, 21)
    assert choice.warning == 'CTS00 2026-10: varias cargas (13, 17, 21); se usa la 21.'


# The upload of the month is being processed: this download leaves it alone
def test_upload_in_procesando_is_skipped():
    uploads = [upload(13, '2026-10', status='procesando')]
    choice = choose_upload(uploads, 'CTS00', '2026-10')
    assert (choice.action, choice.id) == (SKIP, 13)
    assert choice.warning == 'CTS00 2026-10: la carga 13 está en procesando; se descarga en la próxima ejecución.'


# An upload of several months is not the upload of one of them: the month gets its own
def test_upload_of_several_months_does_not_match():
    uploads = [upload(3, '2026-09, 2026-10'), upload(13, '2026-10', company=None, status='error')]
    assert choose_upload(uploads, 'CTS00', '2026-10').action == CREATE


# The newest upload of the month is being processed: skipped, even with older ones
def test_newest_in_procesando_is_skipped_with_older_ones():
    uploads = [upload(13, '2026-10'), upload(21, '2026-10', status='procesando')]
    assert choose_upload(uploads, 'CTS00', '2026-10').action == SKIP


# Name of the file of a month downloaded from SAP
def test_export_name():
    assert export_name('CTS00', '2026-11') == 'TB - CTS00 - 2026-11 (SAP).xlsx'
