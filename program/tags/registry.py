# registry.py

from dataclasses import dataclass


@dataclass(frozen=True)
class RegistryTags:
    boundary: str = 'Boundary reg tex tag'
    image: str = 'Image reg tex tag'
    mu_s: str = 'Mu_s reg tex tag'
    mu_s_images: str = 'Mu_s images reg tex tag'
