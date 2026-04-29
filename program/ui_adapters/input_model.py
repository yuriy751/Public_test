# input_model.py

# input_snapshot.py

from dataclasses import dataclass


@dataclass
class InputModel:
    # --- Geometry / object ---
    pixel_size: float
    d_0: float
    d_end: float

    # --- OCA ---
    w: float
    n_w: float
    n_g: float

    # --- Calculated parameters ---
    phi_0: float
    tau_w: float
    tau_g: float
    n_dry: float
    d: float

    # ---
    segments: int
    boundary_amounts:int

    # --- Mu_s ---
    wavelength: float
    focus_position: float
    omega: float
    sigma_threshold: float
    mu_s_view_min: float
    mu_s_view_max: float
    n_above: str
    n_under: str

    # --- Time_intervals ---
    amount_of_points: int
    time_interval: int
