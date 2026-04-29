from __future__ import annotations

from dataclasses import dataclass
from statistics import median

import cv2
import numpy as np

from .processing_service import BoundariesOutput


@dataclass
class BoundaryStats:
    line_index: int
    min_y: float
    max_y: float
    median_y: float


@dataclass
class ThicknessStats:
    pair: tuple[int, int]
    min_t: float
    max_t: float
    median_t: float


@dataclass
class ImageResults:
    image_path: str
    boundary_stats: list[BoundaryStats]
    thickness_stats: list[ThicknessStats]
    mean_intensity_by_roi: list[float]


def calculate_results(image_path: str, boundaries_output: BoundariesOutput) -> ImageResults | None:
    gray = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if gray is None:
        return None

    boundaries = [np.array(b, dtype=float) for b in boundaries_output.boundaries]
    if not boundaries:
        return None

    bstats: list[BoundaryStats] = []
    for i, b in enumerate(boundaries, start=1):
        clean = b[np.isfinite(b)]
        if clean.size == 0:
            continue
        bstats.append(BoundaryStats(i, float(clean.min()), float(clean.max()), float(median(clean.tolist()))))

    thickness_stats: list[ThicknessStats] = []
    for i in range(len(boundaries) - 1):
        t = boundaries[i + 1] - boundaries[i]
        clean = t[np.isfinite(t)]
        if clean.size == 0:
            continue
        thickness_stats.append(
            ThicknessStats((i + 1, i + 2), float(clean.min()), float(clean.max()), float(median(clean.tolist())))
        )

    h, w = gray.shape
    intensities: list[float] = []
    if len(boundaries) == 1:
        b = boundaries[0]
        vals = []
        for x in range(min(w, len(b))):
            y0 = int(np.clip(b[x], 0, h - 1))
            vals.extend(gray[y0:, x].tolist())
        intensities.append(float(np.mean(vals)) if vals else 0.0)
    else:
        for i in range(len(boundaries) - 1):
            top = boundaries[i]
            bot = boundaries[i + 1]
            vals = []
            for x in range(min(w, len(top), len(bot))):
                y1 = int(np.clip(min(top[x], bot[x]), 0, h - 1))
                y2 = int(np.clip(max(top[x], bot[x]), 0, h - 1))
                vals.extend(gray[y1:y2 + 1, x].tolist())
            intensities.append(float(np.mean(vals)) if vals else 0.0)

    return ImageResults(
        image_path=image_path,
        boundary_stats=bstats,
        thickness_stats=thickness_stats,
        mean_intensity_by_roi=intensities,
    )
