# input_snapshot.py

from dataclasses import dataclass
from typing import Dict, Any
from .input_fields import collect_input_fields


@dataclass
class InputSnapshot:
    values: Dict[str, Any]

    @classmethod
    def collect(cls) -> "InputSnapshot":
        return cls(values=collect_input_fields())

    def to_dict(self) -> Dict[str, Any]:
        return self.values