from dataclasses import dataclass


@dataclass
class SaveState:
    mu_s: bool = False
    boundaries: bool = False
    av_int: bool = False
    params: bool = False
    save_dir: str | None = None