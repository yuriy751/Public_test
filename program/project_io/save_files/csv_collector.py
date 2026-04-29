from pathlib import Path
import csv


def collect_boundaries_csv(table, time_list, selected_fields):
    rows = []

    if not table:
        return rows

    for i, row in enumerate(table):
        out = {
            "filename": row["filename"],
            "time": time_list[i],
        }

        # --- позиции границ ---
        if "med_p" in selected_fields:
            for j, val in enumerate(row.get("med_p", [])):
                out[f"med_p_{j+1}"] = float(val)

        if "min_p" in selected_fields:
            for j, val in enumerate(row.get("min_p", [])):
                out[f"min_p_{j+1}"] = float(val)

        if "max_p" in selected_fields:
            for j, val in enumerate(row.get("max_p", [])):
                out[f"max_p_{j+1}"] = float(val)

        # --- толщины слоёв ---
        if "med_d" in selected_fields:
            for j, val in enumerate(row.get("med_d", [])):
                out[f"med_d_{j+1}"] = float(val)

        if "min_d" in selected_fields:
            for j, val in enumerate(row.get("min_d", [])):
                out[f"min_d_{j+1}"] = float(val)

        if "max_d" in selected_fields:
            for j, val in enumerate(row.get("max_d", [])):
                out[f"max_d_{j+1}"] = float(val)

        # --- total ---
        if "med_total" in selected_fields:
            out["med_total"] = float(row["med_total"])

        if "min_total" in selected_fields:
            out["min_total"] = float(row["min_total"])

        if "max_total" in selected_fields:
            out["max_total"] = float(row["max_total"])

        rows.append(out)

    return rows



def collect_mu_s_csv(table, time_list, selected_fields):
    rows = []

    for i, row in enumerate(table):
        out = {
            'filename': row['filename'],
            'time': time_list[i]
        }

        if 'roi' in selected_fields:
            for j, roi in enumerate(row['roi_stats']):
                out[f'roi{j+1}_median'] = roi['median']
                out[f'roi{j+1}_std'] = roi['std']

        if 'total' in selected_fields:
            out['total_median'] = row['total']['median']
            out['total_std'] = row['total']['std']

        rows.append(out)

    return rows


def collect_av_int_csv(table, time_list, selected_fields):
    rows = []

    for i, row in enumerate(table):
        out = {
            'filename': row['filename'],
            'time': time_list[i]
        }

        if 'roi' in selected_fields:
            for j, roi in enumerate(row['roi_stats']):
                out[f'roi{j+1}_mean'] = roi['mean']
                out[f'roi{j+1}_std'] = roi['std']

        if 'total' in selected_fields:
            out['total_mean'] = row['total']['mean']
            out['total_std'] = row['total']['std']

        rows.append(out)

    return rows


def save_params_csv(params: dict, save_path: Path):
    """
    Сохраняет параметры (int | float) в отдельный CSV файл.
    """

    if not params:
        return

    save_path.parent.mkdir(parents=True, exist_ok=True)

    with save_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["parameter", "value"])

        for key, value in params.items():
            if isinstance(value, (int, float)):
                writer.writerow([key, value])