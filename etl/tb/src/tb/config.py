# ==============================================================================
# tb/config.py
# ------------------------------------------------------------------------------
# Configuration of one company, as read from its master workbook
# (maestro_tb_<empresa>.xlsx). The transformation only sees this object, never
# the workbook, so the configuration can come from disk or from Airflows.
#
# Copyright Oimbra Technology 2026
# ==============================================================================

# Standard libraries
from dataclasses import dataclass
from typing import NamedTuple


# Category and annual-accounts grouping that a TB row carries
class Category(NamedTuple):
    categoria: str
    ccaa1: str
    ccaa2: str


# Tables of the master workbook that the transformation uses
@dataclass(frozen=True)
class Config:
    empresa: str
    patron_edificio: str
    digitos_numero: int
    equivalencias: dict[str, str]
    mapping: dict[str, Category]
