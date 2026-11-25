# ==============================================================================
# tb/__main__.py
# ------------------------------------------------------------------------------
# Command line: python -m tb <export.xlsx> --maestro maestro_tb_<empresa>.xlsx
# [--csv salida.csv]. Reads the SAP export and the company's master workbook,
# transforms, validates and either writes the CSV or prints a summary (rows,
# keys, total per month). On any error nothing is written, every error goes
# to stderr and the exit code is 1.
#
# Copyright Oimbra Technology 2026
# ==============================================================================

# Standard libraries
import argparse
import re
import sys
from pathlib import Path

# Application libraries
from tb.csv_writer import write_csv
from tb.errors import ReadError
from tb.export import read_export
from tb.maestro import read_maestro
from tb.schema import validate_output
from tb.transform import transform

# File name of a master workbook; the company comes from it
MAESTRO_NAME = re.compile(r'^maestro_tb_(?P<empresa>[^.]+)\.xlsx$', re.IGNORECASE)


# Run the command line and return the exit code
def main(argv: list[str] | None = None) -> int:
    # Arguments
    parser = argparse.ArgumentParser(
        prog='python -m tb',
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

    # Transform and validate the output schema
    if export is not None and config is not None:
        result = transform(export, config)
        errors.extend(result.errors or validate_output(result.rows))

    # Any error: report them all and write nothing
    if errors:
        print(f'{len(errors)} errores; no se ha escrito nada:', file=sys.stderr)
        for message in errors:
            print(f'- {message}', file=sys.stderr)
        return 1

    # Write the CSV, or print the summary
    rows = result.rows
    if args.csv:
        write_csv(rows, args.csv)
        print(f'{len(rows)} filas escritas en {args.csv}.')
        return 0
    print(f'Filas: {len(rows)}')
    print(f'Claves: {rows['clave'].nunique()}')
    print('Total por mes:')
    for month, total in rows.groupby('mes')['importe'].sum().round(2).items():
        print(f'  {month}: {total + 0:.2f}'.replace('.', ','))
    return 0


if __name__ == '__main__':
    sys.exit(main())
