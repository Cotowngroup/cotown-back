# ==============================================================================
# local.py
# ------------------------------------------------------------------------------
# Command line, to try an export without uploading it: python local.py
# <export.xlsx> --maestro maestro_tb_<empresa>.xlsx [--csv salida.csv]. Reads
# the SAP export and the company's master workbook, transforms, validates and
# either writes the CSV or prints a summary (rows, keys, total per month). On
# any error nothing is written, every error goes to stderr and the exit code
# is 1.
#
# Copyright Oimbra Technology 2026
# ==============================================================================

# Standard libraries
import argparse
import re
import sys
from pathlib import Path

# Application libraries
from library.business.csv_writer import write_csv
from library.business.errors import ReadError
from library.business.export import read_export
from library.business.maestro import read_maestro
from library.business.run import error_lines, summary_lines, transform_and_validate

# File name of a master workbook; the company comes from it
MAESTRO_NAME = re.compile(r'^maestro_tb_(?P<empresa>[^.]+)\.xlsx$', re.IGNORECASE)


# Run the command line and return the exit code
def main(argv: list[str] | None = None) -> int:
    # Arguments
    parser = argparse.ArgumentParser(
        prog='python local.py',
        description='Transform an SAP Trial Balance export into TB rows.',
    )
    parser.add_argument('export', type=Path, help='SAP Trial Balance export (xlsx), as it comes out of SAP')
    parser.add_argument(
        '--maestro',
        type=Path,
        required=True,
        help='master workbook of the company: maestro_tb_<empresa>.xlsx',
    )
    parser.add_argument('--csv', type=Path, help='write the TB rows to this CSV; without it, print a summary')
    args = parser.parse_args(argv)
    errors = []

    # Company from the master workbook file name
    name_match = MAESTRO_NAME.match(args.maestro.name)
    if not name_match:
        errors.append(f'La hoja maestra debe llamarse maestro_tb_<empresa>.xlsx y se llama {args.maestro.name}.')

    # Read both inputs, collecting the problems of each
    export = config = None
    try:
        with args.export.open('rb') as source:
            export = read_export(source)
    except ReadError as error:
        errors.extend(error.errors)
    except OSError as error:
        errors.append(f'No se puede leer el export {args.export}: {error}.')
    if name_match:
        try:
            with args.maestro.open('rb') as source:
                config = read_maestro(source, name_match['empresa'])
        except ReadError as error:
            errors.extend(error.errors)
        except OSError as error:
            errors.append(f'No se puede leer la hoja maestra {args.maestro}: {error}.')

    # Transform, then validate the output schema and the balance
    if export is not None and config is not None:
        result, run_errors = transform_and_validate(export, config)
        errors.extend(run_errors)

    # Any error: report them all and write nothing
    if errors:
        print('\n'.join(error_lines(errors, 'no se ha escrito nada')), file=sys.stderr)
        return 1

    # Write the CSV, or print the summary
    if args.csv:
        write_csv(result.rows, args.csv)
        print(f'{len(result.rows)} filas escritas en {args.csv}.')
    else:
        print('\n'.join(summary_lines(result)))
    return 0


if __name__ == '__main__':
    sys.exit(main())
