# inputs.py

from dataclasses import dataclass


@dataclass(frozen=True)
class InputFieldTags:
    phi_0: str = 'Phi_0 tag'
    tau_w: str = 'Tau_w tag'
    tau_g: str = 'Tau_g tag'
    segments: str = 'Segments tag'
    boundaries_amount: str = 'Boundaries amount tag'
    pixel_size: str = 'Pixel size tag'
    d_0: str = 'd_0 tag'
    d_end: str = 'd_end tag'
    d:str = 'd tag'
    n_dry: str = 'n_dry tag'
    w: str = 'w tag'
    n_w: str = 'n_w tag'
    n_g: str = 'n_g tag'
    wavelength: str = 'wavelength tag'
    focus_position: str = 'focus_position tag'
    omega: str = 'omega tag'
    n_oca: str = 'n_oca tag'
    mu_s_view_min: str = 'Mu_s view min value tag'
    mu_s_view_max: str = 'Mu_s view max value tag'
    time_interval: str = 'Time interval tag'
    amount_of_points: str = 'Amount of points tag'
    sigma_threshold: str = 'Sigma threshold tag'
    n_above: str = 'n_above tag'
    n_under: str = 'n_under tag'

    def create_new_tags(self, name, value):
        if not hasattr(self, name):
            setattr(self, name, value)

    def delete_tags(self, name):
        if hasattr(self, name):
            delattr(self, name)

