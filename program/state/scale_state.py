from dataclasses import dataclass


@dataclass
class ScaleState:
    scale: float | None = None
    window_scale: float | None = None