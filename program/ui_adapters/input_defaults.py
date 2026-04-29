# input_defaults.py

from dataclasses import dataclass
from .input_model import InputModel


@dataclass
class InputDefaults(InputModel):
    pixel_size: float = 2.67
    d_0: float = 500
    d_end: float = 500

    # --- OCA ---
    w: float = 0.7
    n_w: float = 1.33
    n_g: float = 1.47

    # --- Calculated parameters ---
    phi_0: float = -1
    tau_w: float = -1
    tau_g: float = -1
    n_dry: float = -1
    d: float = -1

    # ---
    segments: int = 130
    boundary_amounts: int = 2

    # --- Mu_s ---
    wavelength: float = 930
    focus_position: int = 0
    omega: float = 1.0
    sigma_threshold: float = 3.0
    mu_s_view_min: float = 0.0
    mu_s_view_max: float = 3.0
    n_above: float = 1.0
    n_under: float = 1.0

    # --- Time_intervals ---
    amount_of_points: int = 10
    time_interval: int = 1


INPUT_DEFAULTS = InputDefaults()