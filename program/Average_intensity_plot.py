# Average_intensity_plot.py

import numpy as np
import dearpygui.dearpygui as dpg
from typing import List

from .state import STATE
from .tags import TAGS


# ======================================================================
# Данные средней интенсивности
# ======================================================================

def get_all_av_int_medians() -> List[List[float]]:
    """
    Возвращает список списков:
    [ [ROI1_mean, ROI2_mean, ..., TOTAL_mean], ... ] по всем изображениям
    """
    av_int_data_list = STATE.tables.av_int or []
    all_images_medians: List[List[float]] = []

    for item_dict in av_int_data_list:
        current_image_medians: List[float] = []

        # ROI
        roi_stats = item_dict.get('roi_stats', [])
        if isinstance(roi_stats, list):
            for roi in roi_stats:
                try:
                    current_image_medians.append(float(roi.get('mean', 0.0)))
                except (ValueError, TypeError):
                    print("Предупреждение: некорректное значение mean в ROI")

        # TOTAL
        try:
            current_image_medians.append(float(item_dict['total']['mean']))
        except (KeyError, ValueError, TypeError):
            print("Предупреждение: некорректное значение total mean")

        if current_image_medians:
            all_images_medians.append(current_image_medians)

    return all_images_medians


# ======================================================================
# Толщина (по данным TABLE MEGA LIST)
# ======================================================================

def get_thickness():
    table = STATE.tables.boundaries or []

    if not table:
        print('[Average_intensity_plot] TABLE MEGA LIST пуст')
        return [], []

    med_list = []

    # Количество слоев берём по первому элементу
    limit = len(table[0].get('med_d', []))

    for row in table:
        med_vals = row.get('med_d', [])[:limit]
        med_list.append(med_vals)

    med_total = [row.get('med_total', 0) for row in table]

    return med_list, med_total


# ======================================================================
# Отрисовка
# ======================================================================

def draw_av_int_plot():
    av_int_table = STATE.tables.av_int or []
    if not av_int_table:
        return

    if not dpg.does_item_exist(TAGS.axis.y_av_int):
        return

    pixel_size = dpg.get_value(TAGS.inputs.pixel_size)

    mass_ = np.asarray(get_all_av_int_medians())
    if mass_.size == 0:
        return

    thickness, thickness_total = get_thickness()

    med_mass = np.asarray(thickness) * pixel_size
    med_mass_total = np.asarray(thickness_total) * pixel_size

    rows, columns = mass_.shape
    x_list = list(range(rows))

    # ===== Абсолютные значения =====
    for i in range(columns - 1):
        y_vals = mass_[:, i].tolist()
        tag = f'Av int {i+2}-{i+1}'

        if not dpg.does_item_exist(tag):
            dpg.add_scatter_series(
                x_list, y_vals,
                label=tag,
                tag=tag,
                parent=TAGS.axis.y_av_int,
                show=True
            )
        else:
            dpg.set_value(tag, [x_list, y_vals])

    total_vals = mass_[:, columns - 1].tolist()

    if not dpg.does_item_exist(TAGS.series_scatter.av_int_med):
        dpg.add_scatter_series(
            x_list, total_vals,
            label='Av int mean total',
            tag=TAGS.series_scatter.av_int_med,
            parent=TAGS.axis.y_av_int,
            show=True
        )
    else:
        dpg.set_value(TAGS.series_scatter.av_int_med, [x_list, total_vals])

    dpg.fit_axis_data(TAGS.axis.x_av_int)
    dpg.fit_axis_data(TAGS.axis.y_av_int)

    # ===== Относительные значения =====
    for i in range(columns - 1):
        rel_vals = (mass_[:, i] / med_mass[:, i]).tolist()
        tag = f'Av int rel {i+2}-{i+1}'

        if not dpg.does_item_exist(tag):
            dpg.add_scatter_series(
                x_list, rel_vals,
                label=tag,
                tag=tag,
                parent=TAGS.axis.y_av_int_rel,
                show=True
            )
        else:
            dpg.set_value(tag, [x_list, rel_vals])

    rel_total = (mass_[:, columns - 1] / med_mass_total).tolist()

    if not dpg.does_item_exist(TAGS.series_scatter.av_int_med_rel):
        dpg.add_scatter_series(
            x_list, rel_total,
            label='Av int mean rel total',
            tag=TAGS.series_scatter.av_int_med_rel,
            parent=TAGS.axis.y_av_int_rel,
            show=True
        )
    else:
        dpg.set_value(TAGS.series_scatter.av_int_med_rel, [x_list, rel_total])

    dpg.fit_axis_data(TAGS.axis.x_av_int)
    dpg.fit_axis_data(TAGS.axis.y_av_int_rel)
