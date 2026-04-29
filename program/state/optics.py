from dataclasses import dataclass, field
from typing import List


@dataclass
class OpticsState:
    deformable: bool = False
    homogenious: bool = True
    low_boundary: bool = True
    known_ri: bool = False
    n_layers: List = field(default_factory=list)