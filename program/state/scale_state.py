from dataclasses import dataclass


@dataclass
class ScaleState:
    scale: float = 1.0
    window_scale: float = 1.0
