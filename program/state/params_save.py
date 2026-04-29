from dataclasses import dataclass, field
from typing import List


@dataclass
class ParamSaveState:
    ri_list: List = field(default_factory=list)
    boundaries_amount: int | None = None
    deformable_sample: bool | None = None
    low_boundary: bool | None = None
    homogenious: bool | None = None
    known_ri: bool | None = None
    amount_of_bounds: int | None = None
    method_name: str | None = None