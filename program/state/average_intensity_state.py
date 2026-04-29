# average_intensity_state.py

from dataclasses import dataclass, field
from typing import List


@dataclass
class AverageIntensityState:
    values: List[float] = field(default_factory=list)
    std_values: List[float] = field(default_factory=list)
    # av_int_table = []

    @classmethod
    def default(cls) -> 'AverageIntensityState':
        return cls()
