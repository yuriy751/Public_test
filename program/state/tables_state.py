from dataclasses import dataclass, field
from typing import List


@dataclass
class TablesState:
    mu_s: List = field(default_factory=list)
    boundaries: List = field(default_factory=list)
    av_int: List = field(default_factory=list)