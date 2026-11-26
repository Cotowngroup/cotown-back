# ==============================================================================
# library/business/errors.py
# ------------------------------------------------------------------------------
# Error raised by the readers when an input file cannot be used at all. It
# carries every problem found, so they can all be reported in one run.
#
# Copyright Oimbra Technology 2026
# ==============================================================================


# Input file that cannot be read, with the full list of problems in Spanish
class ReadError(Exception):

    # Keep the list of problems and use them as the exception message
    def __init__(self, errors: list[str]) -> None:
        super().__init__('\n'.join(errors))
        self.errors = errors
