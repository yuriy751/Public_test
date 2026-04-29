# Average_intensity_calculation.py

import numpy as np
import cv2
import dearpygui.dearpygui as dpg
from pathlib import Path

from .state import STATE
from .tags import TAGS


# ======================================================================
# 1. Утилиты данных
# ======================================================================

def _sort_by_filename(entries):
    """Сортирует записи по имени файла."""
    return sorted(entries, key=lambda x: x.get('filename', ''))


def _safe_get_image_from_item(item):
    """
    Попытка достать numpy image из item через ProjectFS.
    Сначала ищем уже загруженное изображение, потом — на диске в проекте.
    """
    for k in ('image', 'img', 'raw', 'data'):
        if k in item and item[k] is not None:
            return item[k]

    filename = item.get('filename') or Path(item.get('path', '')).name
    if not filename or not STATE.project.is_open():
        return None

    img_path = STATE.project.fs.images_for_processing() / filename
    if img_path.exists():
        img = cv2.imread(str(img_path), cv2.IMREAD_GRAYSCALE)
        if img is not None:
            return img.astype(np.float32)

    return None


def get_boundary_from_table(filename_full):
    """
    Возвращает границу и смещение X для файла через ProjectFS.
    """
    if not STATE.project.is_open() or not STATE.tables.boundaries:
        return None, 0

    mega_list = STATE.tables.boundaries
    target_base = Path(filename_full).name

    found_entry = next(
        (item for item in mega_list
         if Path(item.get('filename', '')).name == target_base
         or (STATE.project.fs.images_for_processing() / Path(item.get('filename', '')).name).exists()),
        None
    )

    if not found_entry:
        return None, 0

    raw_p = found_entry.get('raw_p', [])
    if not raw_p:
        return None, 0

    boundary_array = raw_p[0]
    idx = mega_list.index(found_entry)

    g_x_min = STATE.boundaries.global_x_min
    x_offset = 0
    if isinstance(g_x_min, list) and 0 <= idx < len(g_x_min):
        x_offset = int(g_x_min[idx])
    elif isinstance(g_x_min, (int, float)):
        x_offset = int(g_x_min)

    return np.asarray(boundary_array), x_offset


# ======================================================================
# 2. Расчет статистики
# ======================================================================

def _compute_intensity_stats(filename, image, raw_boundaries):
    if image is None:
        return None

    rows, cols = image.shape

    x1 = int(max(0, min(cols - 1, STATE.boundaries.global_boundary_x1 or 0)))
    x2 = int(max(0, min(cols - 1, STATE.boundaries.global_boundary_x2 or cols)))
    if x2 <= x1:
        x2 = cols - 1

    def get_stats_in_rect(y_top, y_bottom, x_start, x_end):
        y_top = max(0, min(rows - 1, y_top))
        y_bottom = max(0, min(rows - 1, y_bottom))
        if y_bottom <= y_top:
            y_bottom = min(y_top + 1, rows - 1)

        crop = image[y_top:y_bottom + 1, x_start:x_end + 1]
        vals = crop[np.isfinite(crop)]

        return float(np.nanmean(vals)) if vals.size else 0.0, \
               float(np.nanstd(vals)) if vals.size else 0.0, vals

    roi_stats = []
    raw_intensity_arrays = []

    present_rb = [rb for rb in raw_boundaries if rb is not None and len(rb) > 0]
    num_boundaries = len(present_rb)

    if num_boundaries == 0:
        return {'filename': filename, 'roi_stats': [], 'total': {'mean': 0.0, 'std': 0.0}, 'raw_intensity_data': []}

    total_vals = np.array([])
    total_mean = total_std = 0.0

    if num_boundaries == 1:
        rb_top = present_rb[0]
        y_top = int(np.nanmax(rb_top) + 1)
        y_bottom = rows - 1
        mean_val, std_val, vals = get_stats_in_rect(y_top, y_bottom, x1, x2)
        roi_stats.append({'mean': mean_val, 'std': std_val})
        raw_intensity_arrays.append(vals)
        total_mean, total_std, total_vals = mean_val, std_val, vals
    else:
        all_vals_for_total = []
        for i in range(num_boundaries - 1):
            rb_top = present_rb[i]
            rb_bottom = present_rb[i + 1]
            y_top = int(np.nanmax(rb_top) + 1)
            y_bottom = int(np.nanmin(rb_bottom) - 1)
            mean_val, std_val, vals = get_stats_in_rect(y_top, y_bottom, x1, x2)
            roi_stats.append({'mean': mean_val, 'std': std_val})
            raw_intensity_arrays.append(vals)
            all_vals_for_total.append(vals)

        if all_vals_for_total:
            total_vals = np.concatenate(all_vals_for_total)
            total_mean = float(np.nanmean(total_vals)) if total_vals.size else 0.0
            total_std = float(np.nanstd(total_vals)) if total_vals.size else 0.0

    raw_intensity_arrays.append(total_vals)

    return {
        'filename': filename,
        'roi_stats': roi_stats,
        'total': {'mean': total_mean, 'std': total_std},
        'raw_intensity_data': raw_intensity_arrays
    }


# ======================================================================
# 3. Обновление состояния
# ======================================================================

def _upsert_av_int_list(new_record):
    av_int_list = STATE.tables.av_int or []

    filename = new_record.get('filename')
    for i, item in enumerate(av_int_list):
        if item.get('filename') == filename:
            av_int_list[i] = new_record
            break
    else:
        av_int_list.append(new_record)

    STATE.tables.av_int = _sort_by_filename(av_int_list)
    print(f"Av Int Core: Record updated for {filename}.")


def calculate_and_update_av_int(item):
    filename = item.get('filename') or Path(item.get('path', '')).name
    img = _safe_get_image_from_item(item)

    if img is None:
        print(f"Av Int Core: Изображение для {filename} не найдено.")
        return None

    boundary_array_roi, _ = get_boundary_from_table(filename)
    if boundary_array_roi is None:
        print(f"Av Int Core: Границы для {filename} отсутствуют.")
        return None

    table_entry = next((e for e in STATE.tables.boundaries or []
                        if Path(e.get('filename', '')).name == filename), None)
    raw_p = table_entry.get('raw_p', []) if table_entry else []

    new_record = _compute_intensity_stats(filename, img, raw_p)
    _upsert_av_int_list(new_record)
    return new_record


# ======================================================================
# 4. GUI
# ======================================================================

def update_av_int_table_gui():
    table_tag = TAGS.tables.av_int
    av_int_list = STATE.tables.av_int or []

    if not av_int_list:
        if dpg.does_item_exist(table_tag):
            dpg.delete_item(table_tag, children_only=True)
        return

    num_roi = max(len(r.get('roi_stats', [])) for r in av_int_list)

    dpg.delete_item(table_tag, children_only=True)

    dpg.add_table_column(label="N", parent=table_tag)
    dpg.add_table_column(label="Filename", parent=table_tag)
    for i in range(num_roi):
        dpg.add_table_column(label=f"Av int {i+2}-{i+1} mean", parent=table_tag)
        dpg.add_table_column(label=f"Av int {i+2}-{i+1} std", parent=table_tag)
    dpg.add_table_column(label="Total mean", parent=table_tag)
    dpg.add_table_column(label="Total std", parent=table_tag)

    for idx, record in enumerate(av_int_list):
        with dpg.table_row(parent=table_tag):
            dpg.add_text(str(idx + 1))
            filename = record.get('filename', 'N/A')
            dpg.add_text(Path(filename).name)  # <-- здесь Path вместо os.path
            for stats in record.get('roi_stats', []):
                dpg.add_text(f"{stats.get('mean', 0):.2f}")
                dpg.add_text(f"{stats.get('std', 0):.2f}")
            total = record.get('total', {})
            dpg.add_text(f"{total.get('mean', 0):.2f}")
            dpg.add_text(f"{total.get('std', 0):.2f}")


def refresh_av_int_for_selected(sender=None, app_data=None, user_data=None):
    items = STATE.gallery_proc.image_items or []
    selected_indices = sorted(STATE.gallery_proc.selected_indices or [])

    if not selected_indices:
        print("Av Int Core: Нет выбранных изображений.")
        return

    for idx in selected_indices:
        if 0 <= idx < len(items):
            calculate_and_update_av_int(items[idx])

    update_av_int_table_gui()
    dpg.enable_item(TAGS.checkboxes.av_int)
