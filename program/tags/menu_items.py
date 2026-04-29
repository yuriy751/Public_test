# menu_items.py

from dataclasses import dataclass


@dataclass(frozen=True)
class MenuItemTags:
    new_project: str = 'New Project bar tag'
    open_project: str = 'Open project bar tag'
    save: str = 'Menu save bar tag'
    save_as: str = 'Menu saveas bar tag'
    quit: str = 'Menu quit bar tag'
    fullscreen: str = 'Menu fullscreen bar tag'
    help: str = 'Menu help bar tag'
    about: str = 'Menu about bar tag'
