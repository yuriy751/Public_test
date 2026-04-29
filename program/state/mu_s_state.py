# mu_s_state.py

from dataclasses import dataclass, field
from typing import List, Any


@dataclass
class MuSState:
    images: List[Any] = field(default_factory=list)
    current_index: int = 0

    values: List[float] = field(default_factory=list)
    std_values: List[float] = field(default_factory=list)

    images_windows: List[Any] = field(default_factory=list)
    current_index_window: int = 0

    @classmethod
    def default(cls) -> 'MuSState':
        return cls()
