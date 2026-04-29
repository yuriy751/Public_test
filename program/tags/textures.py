# texture.py

from dataclasses import dataclass


@dataclass(frozen=True)
class TextureTags:
    boundaries: str = 'Boundaries texture tag'
    boundary_image: str = 'Image texture for boundary tag'
    mu_s: str = 'Mu_s texture tag'
    mu_s_images: str = 'Mu_s images texture tag'
