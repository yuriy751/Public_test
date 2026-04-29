# windows.py

from dataclasses import dataclass

@dataclass(frozen=True)
class WindowTags:
    parameter: str = 'Parameter window tag'
    main: str = 'Main window tag'
    boundaries: str = 'Boundaries searching window tag'
    boundaries_sep: str = 'Boundaries searching window (sep) tag'
    mu_s: str = 'Mu_s window tag'
    av_int: str = 'Av int calc window tag'
    plots: str = 'Plots window tag'
    mu_s_images: str = 'Mu_s images window tag'
    save_files: str = 'Save files window tag'
