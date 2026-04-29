# gallery_proc_state.py

from dataclasses import dataclass, field
from typing import List, Any, Set


@dataclass
class GalleryProcState:
    image_items: List[Any] = field(default_factory=list)
    selected_indices: Set[int] = field(default_factory=set)
    last_selected: int | None = None
    final_boundaries_set: Set[str] = field(default_factory=set)

    @classmethod
    def default(cls) -> 'GalleryProcState':
        return cls()