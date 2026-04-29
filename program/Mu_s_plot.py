# Mu_s_plot.py

from .state import STATE
from .tags import TAGS
import numpy as np
from typing import List
import dearpygui.dearpygui as dpg


def get_all_mu_s_medians() -> List[List[float]]:
    """
    Извлекает медианные значения mu_s из roi_stats и 'total' для каждого изображения.

    Returns:
        Список списков (List[List[float]]), где каждый внутренний список содержит
        медианы ROI, за которыми следует общая медиана ('total')['median']) для
        соответствующего изображения.
    """
    try:
        mu_s_data_list = STATE.tables.mu_s
        all_images_medians = []

        for item_dict in mu_s_data_list:
            current_image_medians = []

            # 1. Извлечение медиан из roi_stats (список словарей)
            try:
                roi_stats = item_dict['roi_stats']
                if isinstance(roi_stats, list):
                    for roi in roi_stats:
                        try:
                            median = roi['median']
                            current_image_medians.append(float(median))
                        except (KeyError, ValueError, TypeError) as e:
                            # Обработка ошибки, если 'median' отсутствует или не число
                            print(f"Предупреждение: Не удалось извлечь медиану ROI. Ошибка: {e}")

            except KeyError:
                print("Предупреждение: Ключ 'roi_stats' не найден.")

            # 2. Извлечение общей медианы из 'total'
            try:
                total_median = item_dict['total']['median']
                current_image_medians.append(float(total_median))
            except KeyError as e:
                print(f"Предупреждение: Ключ {e} в 'total' не найден.")
            except (ValueError, TypeError) as e:
                print(f"Предупреждение: Не удалось преобразовать общую медиану в float. Ошибка: {e}")

            if current_image_medians:
                all_images_medians.append(current_image_medians)

        return all_images_medians

    except KeyError as e:
        print(f"Ошибка: Не найден ключ {e} в структуре констант.")
        return []


def draw_mu_s_plot():
    if not STATE.tables.mu_s:
        return
    if not dpg.does_item_exist(TAGS.axis.y_mu_s):
        return
    list_ = get_all_mu_s_medians()
    mass_: np.ndarray = np.asarray(list_)
    rows, columns = mass_.shape     # количество изображений, количество ROI + Total
    x_list = [i for i in range(rows)]
    print(mass_.shape)
    for i in range(columns-1):
        list_inner = []
        for j in range(rows):
            list_inner.append(mass_[j, i])
        # print(list_inner, len(list_inner))
        if not dpg.does_item_exist(f'Mu_s {i+2}-{i+1}'):
            dpg.add_scatter_series(x_list, list_inner, label=f'Mu_s {i+2}-{i+1}', tag=f'Mu_s {i+2}-{i+1}',
                                   parent=TAGS.axis.y_mu_s, show=True)
        else:
            dpg.set_value(f'Mu_s {i+2}-{i+1}', [x_list, list_inner])
    total = mass_[:, columns-1]
    list_inner_total = []
    for j in range(rows):
        list_inner_total.append(total[j])
    # print('\n', list_inner, len(list_inner))
    if not dpg.does_item_exist(TAGS.series_scatter.mu_s_med):
        dpg.add_scatter_series(x_list, list_inner_total, label='Mu_s med total',
                               tag=TAGS.series_scatter.mu_s_med,
                               parent=TAGS.axis.y_mu_s, show=True)
    else:
        dpg.set_value(TAGS.series_scatter.mu_s_med, [x_list, list_inner_total])
    dpg.fit_axis_data(TAGS.axis.x_mu_s)
    dpg.fit_axis_data(TAGS.axis.y_mu_s)
