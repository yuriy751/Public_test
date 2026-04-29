from __future__ import annotations

import csv
import json
from dataclasses import asdict
from pathlib import Path

from .results_service import ImageResults


def export_results(results: list[ImageResults], out_dir: str) -> Path:
    root = Path(out_dir)
    root.mkdir(parents=True, exist_ok=True)

    raw_json = root / "results_raw.json"
    raw_json.write_text(json.dumps([asdict(r) for r in results], ensure_ascii=False, indent=2))

    table_csv = root / "results_table.csv"
    with table_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["image_path", "line", "min_y", "max_y", "median_y", "mean_intensity_roi"])
        for r in results:
            intens = r.mean_intensity_by_roi
            for i, b in enumerate(r.boundary_stats):
                mean_int = intens[i - 1] if i - 1 < len(intens) else ""
                writer.writerow([r.image_path, b.line_index, b.min_y, b.max_y, b.median_y, mean_int])

    return root
