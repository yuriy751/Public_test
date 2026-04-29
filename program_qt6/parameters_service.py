from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd


@dataclass
class ParametersResult:
    mode: str
    mean_refractive_index: float
    rows: int


def calculate_parameters_from_table(path: str) -> ParametersResult:
    df = pd.read_csv(path)
    cols = [c.strip().lower() for c in df.columns]

    if len(cols) >= 3:
        # expected: time, optical_thickness, geometric_thickness
        t = df.iloc[:, 0].to_numpy(dtype=float)
        opt = df.iloc[:, 1].to_numpy(dtype=float)
        geo = df.iloc[:, 2].to_numpy(dtype=float)
        valid = np.isfinite(t) & np.isfinite(opt) & np.isfinite(geo) & (geo != 0)
        n = opt[valid] / geo[valid]
        mean_n = float(np.mean(n)) if n.size else 1.38
        return ParametersResult(mode="3-columns", mean_refractive_index=mean_n, rows=int(valid.sum()))

    if len(cols) >= 2:
        # expected: time, optical_thickness
        # fallback estimate: normalized slope-based proxy around water/tissue range
        t = df.iloc[:, 0].to_numpy(dtype=float)
        opt = df.iloc[:, 1].to_numpy(dtype=float)
        valid = np.isfinite(t) & np.isfinite(opt)
        if valid.sum() < 2:
            return ParametersResult(mode="2-columns", mean_refractive_index=1.38, rows=int(valid.sum()))
        slope = np.polyfit(t[valid], opt[valid], 1)[0]
        mean_n = float(np.clip(abs(slope), 1.0, 2.0))
        return ParametersResult(mode="2-columns", mean_refractive_index=mean_n, rows=int(valid.sum()))

    raise ValueError("Input table must have at least 2 columns")
