# child_windows.py

from dataclasses import dataclass


@dataclass(frozen=True)
class ChildWindowTags:
    text: str = 'Text window tag'
    boundary: str = 'Boundary window tag'
    average_ascan: str = 'Average A-scan window tag'
    optical_thickness: str = 'Optical thickness window tag'
    imaging: str = 'Imaging window tag'
    gallery: str = 'Gallery window tag'
    gallery_processed: str = 'Gallery processed window tag'
    mu_s_focus: str = 'Mu_s image with focus window tag'
    mu_s_images: str = 'Mu_s images childwindow tag'
    mu_s_plot: str = 'Mu_s plots childwindow tag'
