# plots.py

from dataclasses import dataclass


@dataclass(frozen=True)
class PlotTags:
    optical_thickness: str = 'Optical thickness plot tag'
    ascan: str = 'A-scan plot tag'
    mu_s: str = 'Mu_s plot tag'
    average_intensity: str = 'Average intensity plot tag'
    geometric_thickness: str = 'Geometric thickness plot tag'
    optical_thickness_: str = 'Optical thickness plot_ tag'
    liquid_ri: str = 'Liquid refractive index plot tag'
    total_ri: str = 'Total refractive index plot tag'
    liquid_fraction: str = 'Fraction of liquid in sample plot tag'
    components_fraction: str = 'Fraction of components in liquid plot tag'
    # mu_s_: str = 'Mu_s plot_ tag'
    # average_pixel_intensity: str = 'Average pixel intensity plot tag'
