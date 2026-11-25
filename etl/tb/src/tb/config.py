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


# Account + service + asset: the part of TB!K that decides the category
class Combination(NamedTuple):
    cuenta: str
    servicio: str
    asset: str

    # As it appears at the start of TB!K and in messages: cuenta servicio asset
    def __str__(self) -> str:
        return f'{self.cuenta} {self.servicio} {self.asset}'


# Row of Reclasificaciones: lines of cuenta + servicio_sap (and centre, when given) take servicio_tb
class Reclassification(NamedTuple):
    cuenta: str
    servicio_sap: str
    centro_beneficio: str | None
    servicio_tb: str


# Tables of the master workbook that the transformation uses
@dataclass(frozen=True)
class Config:
    empresa: str
    patron_edificio: str
    digitos_numero: int
    equivalencias: dict[str, str]
    reclasificaciones: list[Reclassification]
    mapping: dict[str, Category]
    categorias: dict[Combination, str]
    referencia: dict[Combination, list[Category]]
