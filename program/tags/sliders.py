# sliders.py

from dataclasses import dataclass


@dataclass(frozen=True)
class SliderTags:
    x1: str = 'x1 tag'
    x2: str = 'x2 tag'
    y1: str = 'y1 tag'
    y2: str = 'y2 tag'
