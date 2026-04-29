# tables.py

from dataclasses import dataclass


@dataclass(frozen=True)
class TableTags:
    boundaries: str = 'Table boundaries tag'
    mu_s: str = 'Table mu_s tag'
    av_int: str = 'Table av int tag'
