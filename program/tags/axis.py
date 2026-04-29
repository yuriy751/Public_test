# axis.py

from dataclasses import dataclass


@dataclass(frozen=True)
class AxisTags:
    x_opt: str = 'X axis opt tag'
    y_opt: str = 'Y axis opt tag'
    x_boundaries: str = 'X axis boundaries tag'
    y_boundaries: str = 'Y axis boundaries'
    x_mu_s: str = 'X axis mu_s tag'
    y_mu_s: str = 'Y axis mu_s tag'
    x_av_int: str = 'X axis av_int tag'
    y_av_int: str = 'Y axis av_int tag'
    y_av_int_rel: str = 'Y axis av_int_rel tag'
    x_opt_thick: str = 'X axis opt_thick tag'
    y_opt_thick: str = 'Y axis opt_thick tag'
    x_liquid_ri: str = 'X axis liquid_ri tag'
    y_liquid_ri: str = 'Y axis liquid_ri tag'
    x_total_ri: str = 'X axis total_ri tag'
    y_total_ri: str = 'Y axis total_ri tag'
    x_liquid_fract: str = 'X axis liquid_fract tag'
    y_liquid_fract: str = 'Y axis liquid_fract tag'
    x_comp_fract: str = 'X axis comp_fract tag'
    y_comp_fract: str = 'Y axis comp_fract tag'
    x_mu_s_: str = 'X axis mu_s_ tag'
    y_mu_s_: str = 'Y axis mu_s_ tag'
    x_av_int_: str = 'X axis av_int_ tag'
    y_av_int_: str = 'Y axis av_int_ tag'
    x_geom_thick: str = 'X axis geom_thick tag'
    y_geom_thick: str = 'Y axis geom_thick tag'
