# global_constants.py

from dataclasses import dataclass


@dataclass(frozen=False)
class Constants:
    Fraction: float = 0.23
    const_1: float = 18
    const_2: float = 150
    const_3: float = 100
    thumb_size: int = 150
    field_width_1: int = 110
    field_height_1: int = 40
    original_width: int = 2245
    original_height: int = 1024
    boundaries_searching_window_width_fraction: float = 0.9
    boundaries_searching_window_height_fraction: float = 0.8
    colourmap = {
        0: (0, 0, 255),
        1: (0, 255, 0),
        2: (255, 0, 0),
        3: (0, 255, 255),
        4: (255, 0, 255)
    }
    additional_scale: float = 0.8