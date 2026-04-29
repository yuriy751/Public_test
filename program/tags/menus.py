# menus.py

from dataclasses import dataclass


@dataclass(frozen=True)
class MenuTags:
    file: str = 'Menu file tag'
    settings: str = 'Menu settings tag'
    help: str = 'Menu help tag'