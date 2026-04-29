# boundaries_state.py

from dataclasses import dataclass, field
from typing import List, Any


@dataclass
class BoundariesState:
    images: List[Any] = field(default_factory=list)
    current_index: int = 0

    global_x_min: list = field(default_factory=list)
    global_x_max: list = field(default_factory=list)
    global_boundary_x1 = None
    global_boundary_x2 = None

    chosen_photos = None
