from collections import OrderedDict
import numpy as np
from pathlib import Path


class RawNPZCollector:
    def __init__(self):
        self.data = OrderedDict()

    def add(self, key: str, array: np.ndarray):
        if array is None:
            return
        self.data[key] = np.asarray(array)

    def save(self, path: Path):
        if not self.data:
            return
        path.parent.mkdir(parents=True, exist_ok=True)
        np.savez(path, **self.data)


def save_boundaries_raw_npz(
    table: list[dict],
    save_path: Path,
    selected_fields: list[str],
):
    """
    Сохраняет raw-данные boundaries в один .npz.
    Ожидает table как list[dict].
    """

    # --- защита от пустоты ---
    if not table:
        return

    raw_keys = [k for k in selected_fields if k.startswith("raw")]
    if not raw_keys:
        return

    raw_data = {}

    for row in table:
        filename = row.get("filename")
        if not filename:
            continue

        for key in raw_keys:
            val = row.get(key)

            if val is None:
                continue

            # важно: object dtype для неоднородных массивов
            raw_data[f"{filename}_{key}"] = np.asarray(val, dtype=object)

    if not raw_data:
        return

    save_path.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(save_path, **raw_data)



def collect_mu_s_raw_npz(table, collector: RawNPZCollector):
    for row in table:
        fname = row['filename']
        arrays = row.get('raw_mu_s_data', [])

        for i, arr in enumerate(arrays[:-1]):
            collector.add(f"{fname}/roi{i+1}", arr)

        if arrays:
            collector.add(f"{fname}/total", arrays[-1])


def collect_av_int_raw_npz(table, collector: RawNPZCollector):
    for row in table:
        fname = row['filename']
        arrays = row.get('raw_intensity_data', [])

        for i, arr in enumerate(arrays[:-1]):
            collector.add(f"{fname}/roi{i+1}", arr)

        if arrays:
            collector.add(f"{fname}/total", arrays[-1])
