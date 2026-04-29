from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np

from program.Boundaries_processing import detect_boundaries


@dataclass
class BoundariesOutput:
    image_path: str
    boundaries: list[list[float]]


def run_boundaries_for_image(
    image_path: str,
    roi: tuple[int, int, int, int],
    boundaries_count: int,
    shift: int = 12,
) -> BoundariesOutput | None:
    img_gray = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if img_gray is None:
        return None

    x1, x2, y1, y2 = roi
    h_img, w_img = img_gray.shape
    x1, x2 = max(0, int(x1)), min(w_img, int(x2))
    y1, y2 = max(0, int(y1)), min(h_img, int(y2))
    if x2 <= x1 or y2 <= y1:
        return None

    boundaries = detect_boundaries(
        img_gray=img_gray,
        x1=x1,
        x2=x2,
        y1=y1,
        y2=y2,
        n_bounds=boundaries_count,
        shift=shift,
    )

    serializable = [b.astype(float).tolist() for b in boundaries]
    return BoundariesOutput(image_path=str(Path(image_path)), boundaries=serializable)
