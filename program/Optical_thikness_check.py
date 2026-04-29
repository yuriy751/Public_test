# Optical_thickness_check.py

import dearpygui.dearpygui as dpg
import numpy as np
from .state import STATE
from .tags import TAGS


def data_choose():
    # 1. Правильная проверка на пустоту
    if not STATE.tables.boundaries:
        print('[Optical_thickness_check] table is empty')
        # Возвращаем 3 пустых списка, чтобы программа не упала при распаковке результата
        return [], [], []

    med_list = []
    min_list = []
    max_list = []

    # Получаем лимит один раз перед циклом
    # Ваша логика: range(NumBoundaries - 1) эквивалентна срезу [:limit]
    limit = len(STATE.tables.boundaries[0]['med_d'])

    for row in STATE.tables.boundaries:
        # 2. Обращаемся к ключам напрямую, без перебора for j in keys()
        # Используем срезы списков (slicing) вместо цикла for k in range

        # Берем список по ключу 'med_d' и отрезаем нужное количество элементов
        med_vals = row['med_d'][:limit]
        min_vals = row['min_d'][:limit]
        max_vals = row['max_d'][:limit]

        med_list.append(med_vals)
        min_list.append(min_vals)
        max_list.append(max_vals)

    med_total = [row['med_total'] for row in STATE.tables.boundaries]
    min_total = [row['min_total'] for row in STATE.tables.boundaries]
    max_total = [row['max_total'] for row in STATE.tables.boundaries]

    return med_list, min_list, max_list, med_total, min_total, max_total


def graphic_imaging():
    if not dpg.does_item_exist(TAGS.axis.y_opt):
        print('[Optical_thickness_check] y_axis opt doesn\'t exist')
        return
    pixel_size = dpg.get_value(TAGS.inputs.pixel_size)
    med, min_l, max_l, med_total, min_total, max_total = data_choose()
    med_mass: np.ndarray = np.asarray(med)*pixel_size
    min_l_mass: np.ndarray = np.asarray(min_l)*pixel_size
    max_l_mass: np.ndarray = np.asarray(max_l)*pixel_size
    columns, rows = med_mass.shape
    x_list = [i for i in range(columns)]
    v = 1
    for i in range(rows):
        med_, min_, max_ = [], [], []
        for j in range(columns):
            med_.append(med_mass[j, i])
            min_.append(min_l_mass[j, i])
            max_.append(max_l_mass[j, i])
        if not dpg.does_item_exist(f'Optical thickness med {v}-{v+1}'):
            dpg.add_scatter_series(x_list, med_, label=f'median {v}-{v+1}', tag=f'Optical thickness med {v}-{v+1}',
                                   parent=TAGS.axis.y_opt, show=True)
        else:
            dpg.set_value(f'Optical thickness med {v}-{v+1}', [x_list, med_])

        if not dpg.does_item_exist(f'Optical thickness min {v}-{v+1}'):
            dpg.add_scatter_series(x_list, min_, label=f'min {v}-{v+1}', tag=f'Optical thickness min {v}-{v+1}',
                                   parent=TAGS.axis.y_opt, show=True)
        else:
            dpg.set_value(f'Optical thickness min {v}-{v+1}', [x_list, min_])

        if not dpg.does_item_exist(f'Optical thickness max {v}-{v+1}'):
            dpg.add_scatter_series(x_list, max_, label=f'max {v}-{v+1}', tag=f'Optical thickness max {v}-{v+1}',
                                   parent=TAGS.axis.y_opt, show=True)
        else:
            dpg.set_value(f'Optical thickness max {v}-{v+1}', [x_list, max_])
        v += 1
    med_total_pixel, min_total_pixel, max_total_pixel = [], [], []
    for i in range(len(med_total)):
        med_total_pixel.append(med_total[i]*pixel_size)
        min_total_pixel.append(min_total[i]*pixel_size)
        max_total_pixel.append(max_total[i]*pixel_size)
    if not dpg.does_item_exist(TAGS.series_scatter.opt_thick_med):
        dpg.add_scatter_series(x_list, med_total_pixel, label='median_total',
                               tag=TAGS.series_scatter.opt_thick_med,
                               parent=TAGS.axis.y_opt, show=True)
    else:
        dpg.set_value(TAGS.series_scatter.opt_thick_med, [x_list, med_total_pixel])

    if not dpg.does_item_exist(TAGS.series_scatter.opt_thick_min):
        dpg.add_scatter_series(x_list, min_total_pixel, label='min_total',
                               tag=TAGS.series_scatter.opt_thick_min,
                               parent=TAGS.axis.y_opt, show=True)
    else:
        dpg.set_value(TAGS.series_scatter.opt_thick_min, [x_list, min_total_pixel])

    if not dpg.does_item_exist(TAGS.series_scatter.opt_thick_max):
        dpg.add_scatter_series(x_list, max_total_pixel, label='max_total',
                               tag=TAGS.series_scatter.opt_thick_max,
                               parent=TAGS.axis.y_opt, show=True)
    else:
        dpg.set_value(TAGS.series_scatter.opt_thick_max, [x_list, max_total_pixel])
    dpg.fit_axis_data(TAGS.axis.x_opt)
    dpg.fit_axis_data(TAGS.axis.y_opt)
    print(STATE.boundaries.global_boundary_x1,
          STATE.boundaries.global_boundary_x2)
