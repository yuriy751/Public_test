# gallery_state.py

from dataclasses import dataclass, field
from typing import List, Any, Set
import numpy as np


@dataclass
class GalleryState:
    image_items: List[Any] = field(default_factory=list)
    selected_indices: Set[int] = field(default_factory=set)
    last_selected: int | None = None
    current_image: np.ndarray | None = None

    @classmethod
    def default(cls) -> 'GalleryState':
        return cls()
