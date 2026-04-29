# series.py

from dataclasses import dataclass


@dataclass(frozen=True)
class SeriesTags:
    ascan: str = 'A-scan seria tag'
    geometric_thickness: str = 'Geometric thickness seria tag'
    optical_thickness: str = 'Optical thickness seria tag'
    liquid_ri: str = 'RI of liquid seria tag'
    total_ri: str = 'Total RI seria tag'
    liquid_fraction: str = 'Liquid fraction seria tag'
    components_fraction: str = 'Components fraction seria tag'
    components_fraction_2: str = 'Components fraction seria 2 tag'
    mu_s: str = 'Mu_s seria tag'
    av_int: str = 'Av_int seria tag'


@dataclass(frozen=True)
class ScatterSeriesTags:
    opt_thick_med: str = 'Optical thickness med total tag'
    opt_thick_min: str = 'Optical thickness min total'
    opt_thick_max: str = 'Optical thickness max total'
    mu_s_med: str = 'Mu_s med total tag'
    av_int_med: str = 'Av int med total tag'
    av_int_med_rel: str = 'Av int med total rel tag'
    optical_thickness: str = 'Optical thickness tag'
    mu_s: str = 'Mu_s tag'
    average_intensity: str = 'Average intensity tag'
    average_intensity_rel: str = 'Average intensity rel tag'
