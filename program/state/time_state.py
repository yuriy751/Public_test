# time_state.py

from dataclasses import dataclass, field


@dataclass
class TimeState:
    time_list: list = field(default_factory=list)
