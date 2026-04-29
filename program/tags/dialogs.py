# dialogs.py

from dataclasses import dataclass


@dataclass(frozen=True)
class DialogTags:
    choose_images: str = 'Choose images tag'
    open_project: str = 'Open project tag'
    save_project: str = 'Save project tag'
    save_files_to_project: str = 'Save files to project tag'
    save_images_to_project: str = 'Save images to project tag'

