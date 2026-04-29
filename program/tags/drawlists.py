# drawlists.py

from dataclasses import dataclass


@dataclass(frozen=True)
class DrawlistTags:
    boundary: str = 'Boundary drawlist tag'
    roi: str = 'ROI drawlist tag'
    mu_s: str = 'Mu_s drawlist tag'
    mu_s_images: str = 'Mu_s images drawlist tag'
