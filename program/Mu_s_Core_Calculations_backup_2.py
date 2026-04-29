import dearpygui.dearpygui as dpg
import numpy as np
import cv2
import os
from pathlib import Path

from .tags import TAGS
from .state import STATE


def base_name_of_file(x: str):
    return Path(x).name if x else ''


def _sort_by_filename(entries):
    """Сортирует записи по имени файла."""
    return sorted(entries, key=lambda x: x.get('filename', ''))


def get_calculation_parameters():
    """Считывает параметры из GUI."""
    delta = dpg.get_value(TAGS.inputs.pixel_size) * 1e-3
    air_focus_depth = dpg.get_value(TAGS.inputs.focus_position)
    lambda_0 = dpg.get_value(TAGS.inputs.wavelength) * 1e-6
    omega_i = dpg.get_value(TAGS.inputs.omega) * 1e-3

    return {
        "air_focus_depth": air_focus_depth,
        "delta": delta,
        "lambda_0": lambda_0,
        "omega_i": omega_i
    }


def _safe_get_image_from_item(item):
    """Попробовать достать numpy image из item (из галереи)."""
    for k in ('image', 'img', 'raw', 'data'):
        if k in item and item[k] is not None:
            return item[k]
    path = item.get('path') or item.get('filename')
    if path and os.path.exists(path):
        img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
        if img is not None:
            return img.astype(np.float32)
    return None


def get_boundary_info(path):
    boundary_list = STATE.tables.boundaries

    target = base_name_of_file(path)

    found_idx = -1
    found_entry = None
    if not boundary_list:
        print('Я вышел на boundary_list')
        return None, None, None

    for i, item in enumerate(boundary_list):
        # print(item)
        if base_name_of_file(item.get('filename')) == target:
            found_entry = item
            found_idx = i
            break

    if found_entry is None:
        print('Я вышел на found_entry')
        return None, None, None

    raw_p = found_entry.get('raw_p', [])
    if not raw_p:
        print('Я вышел на raw_p')
        return None, None, None

    x_offset = max(0, STATE.boundaries.global_boundary_x1)
    length = len(raw_p[0])

    return raw_p, x_offset, length


def calculate_sigma_threshold(sum_intensity, roi_mask, depth_slice=20):
    """
    Адаптивный расчет порога сигнала по нижней части ROI
    """

    # берём только ROI
    roi_data = sum_intensity[:, roi_mask]

    if roi_data.size == 0:
        return 0.0

    # нижний слой
    bottom_slice = roi_data[-depth_slice:, :]

    # убираем нули
    non_zero = bottom_slice[bottom_slice > 0]

    if non_zero.size == 0:
        return 0.0

    mean_val = np.mean(non_zero)
    std_val = np.std(non_zero)

    # можно поиграть коэффициентом
    threshold = max(mean_val + 3 * std_val, 1e-5)

    return threshold


def focus_position(raw_p, air_focus_depth, img_width, x_offset):
    """
    Вычисляет физическое положение фокуса (аналогично draw_focus_line),
    но без отрисовки.

    Все позиции вне ROI (до x_offset и после ROI) = 0.
    Возвращается массив длиной img_width.
    """
    # Необходимо написать проверку на количество ПП и слоёв, гомогенность, нижней границы

    focus_positions = np.zeros(img_width, dtype=np.float32)

    if not raw_p or not isinstance(raw_p, (list, tuple)) or raw_p[0] is None:
        return focus_positions

    roi_width = len(raw_p[0])
    n_layers_full = getattr(STATE.param_save, "ri_list", [1.0])

    for col in range(roi_width):
        global_col = x_offset + col
        if global_col >= img_width:
            break  # защитная граница

        # --- Сбор границ для текущего столбца ---
        col_borders = []
        for b_arr in raw_p:
            if col < len(b_arr) and b_arr[col] is not None and not np.isnan(b_arr[col]):
                col_borders.append(b_arr[col])
        col_borders.sort()

        # --- Основной расчет физического фокуса ---
        remaining_nom = air_focus_depth
        z_phys = 0.0
        last_border_y = 0.0
        layer_index = 0

        for border_y in col_borders:
            dist_nom = border_y - last_border_y
            current_n = n_layers_full[layer_index] if layer_index < len(n_layers_full) else 1.0

            if remaining_nom <= dist_nom:
                z_phys += remaining_nom * current_n
                remaining_nom = 0
                break
            else:
                z_phys += dist_nom * current_n
                remaining_nom -= dist_nom
                last_border_y = border_y
                layer_index += 1

        if remaining_nom > 0:
            current_n = n_layers_full[layer_index] if layer_index < len(n_layers_full) else 1.0
            z_phys += remaining_nom * current_n

        focus_positions[global_col] = z_phys

    return focus_positions


def fast_process_image(img, raw_p, focus_positions, params, x_offset=0):
    """
    Физически корректный расчет mu_t:
    - img = ПОЛНОЕ изображение
    - raw_p = ROI границы
    - focus_positions = массив по ширине изображения
    - используется x_offset для ROI
    - вне ROI: img=0, mu_t=0
    """

    if img is None or raw_p is None:
        return None

    img = img.astype(np.float32)
    n_layers = getattr(STATE.param_save, "ri_list", [1.0])
    delta = params['delta']
    omega_i = params['omega_i']
    lambda_0 = params['lambda_0']

    rows, cols_full = img.shape

    roi_width = len(raw_p[0])
    x_start = max(0, x_offset)
    x_end = min(cols_full, x_start + roi_width)

    # =========================
    # 1. Подготовка границ full size
    # =========================
    boundaries = []
    for b in raw_p:
        b_arr = np.full(cols_full, np.nan, dtype=np.float32)
        b_roi = np.asarray(b, dtype=np.float32)
        width = min(len(b_roi), x_end - x_start)
        b_arr[x_start:x_start + width] = b_roi[:width]

        # заполнение NaN (интерполяция по столбцу)
        valid = np.isfinite(b_arr)
        if np.any(valid):
            b_arr[~valid] = np.interp(
                np.flatnonzero(~valid),
                np.flatnonzero(valid),
                b_arr[valid]
            )
        else:
            b_arr[:] = 0
        boundaries.append(b_arr)

    # =========================
    # 2. Карта n(z, x)
    # =========================
    n_map = np.ones((rows, cols_full), dtype=np.float32)
    for col in range(cols_full):
        col_boundaries = np.sort([b[col] for b in boundaries])
        last_y = 0
        layer_idx = 0
        for border_y in col_boundaries:
            y0 = int(max(0, round(last_y)))
            y1 = int(min(rows, round(border_y)))
            current_n = n_layers[layer_idx] if layer_idx < len(n_layers) else 1.0
            n_map[y0:y1, col] = current_n
            last_y = border_y
            layer_idx += 1
        y0 = int(max(0, round(last_y)))
        current_n = n_layers[layer_idx] if layer_idx < len(n_layers) else 1.0
        n_map[y0:, col] = current_n

    # =========================
    # 3. Геометрия
    # =========================
    surface = boundaries[0]
    z_pixels = np.arange(rows)[:, None]
    z_relative = (z_pixels - surface[None, :]) * delta

    # =========================
    # 4. Фокус
    # =========================
    z_focus = (focus_positions * delta)[None, :]

    # =========================
    # 5. Rayleigh
    # =========================
    z_i_map = (np.pi * n_map * (omega_i ** 2)) / lambda_0

    # =========================
    # 6. Beam
    # =========================
    h_matrix = 1.0 / ((((z_relative - z_focus) / z_i_map) ** 2) + 1.0)

    # =========================
    # 7. Убираем воздух и всё, что ниже объекта (п. 3)
    # =========================
    mask_air = z_relative < 0
    img[mask_air] = 0.0
    h_matrix[mask_air] = 1.0

    # Проверяем условие из STATE
    low_boundaries = STATE.param_save.low_boundary

    # Если есть хотя бы верхняя и нижняя граница, и флаг True
    mask_below = None
    if low_boundaries and len(boundaries) > 1:
        print('[BOUNDARIES] I am here!')
        bottom_surface = boundaries[-1]  # берем самую нижнюю границу
        mask_below = z_pixels >= bottom_surface[None, :]

        # ВАЖНО: Обнуляем исходный сигнал ниже границы ДО интегрирования.
        # Это убирает мощный блик от границы из интеграла и решает проблему
        # искусственного занижения/завышения mu_t в просветленной ткани.
        img[mask_below] = 0.0
        h_matrix[mask_below] = 1.0

    # =========================
    # 8. Интенсивность (и перевод в линейный масштаб - п. 1)
    # =========================
    img_lin = img

    I_new = img_lin / (h_matrix + 1e-12)

    # =========================
    # 9. Интеграл
    # =========================
    sum_intensity = np.cumsum(I_new[::-1, :], axis=0)[::-1, :]
    sum_shifted = np.roll(sum_intensity, -1, axis=0)
    sum_shifted[-1, :] = 0.0

    # =========================
    # 10. mu_t (с регуляризацией - п. 2)
    # =========================
    mu_t = np.zeros_like(I_new, dtype=np.float32)

    # Вводим epsilon для аппроксимации знаменателя.
    # Это предотвратит деление на ноль и сгладит резкие пятна на дне,
    # где полезный сигнал сравним с уровнем шума.
    # Значение epsilon стоит подобрать эмпирически (зависит от разрядности камеры ОКТ).
    epsilon = 1e-6

    mask_valid = sum_shifted > 1e-12
    mu_t[mask_valid] = I_new[mask_valid] / (2.0 * delta * sum_shifted[mask_valid] + epsilon)

    # =========================
    # 11. Фильтрация и маска ROI
    # =========================
    roi_mask = np.zeros(cols_full, dtype=bool)
    roi_mask[x_start:x_end] = True

    sigma_threshold = calculate_sigma_threshold(
        sum_intensity,
        roi_mask,
        depth_slice=20
    )

    mu_t[sum_intensity < sigma_threshold] = 0.0

    # Окончательно зачищаем мусор ниже нижней границы,
    # если вдруг регуляризация дала артефакты
    if low_boundaries and len(boundaries) > 1 and mask_below is not None:
        mu_t[mask_below] = 0.0

    # Обнуляем вне ROI
    roi_mask = np.zeros(cols_full, dtype=bool)
    roi_mask[x_start:x_end] = True
    mu_t[:, ~roi_mask] = 0.0

    return mu_t



def _compute_roi_stats(filename, mu_t_matrix, raw_boundaries):
    if mu_t_matrix is None:
        return None
    rows, cols = mu_t_matrix.shape
    x1 = STATE.boundaries.global_boundary_x1 if STATE.boundaries.global_boundary_x1 is not None else 0
    x2 = STATE.boundaries.global_boundary_x2 if STATE.boundaries.global_boundary_x2 is not None else cols
    x1 = int(max(0, min(cols - 1, int(x1)))) if x1 is not None else 0
    x2 = int(max(0, min(cols - 1, int(x2)))) if x2 is not None else cols - 1
    if x2 <= x1:
        x2 = cols - 1

    # Вспомогательная функция, которая теперь также возвращает сырые значения (vals)
    def get_stats_in_rect(y_top, y_bottom, x_start, x_end):
        y_top = max(0, min(rows - 1, y_top))
        y_bottom = max(0, min(rows - 1, y_bottom))
        if y_bottom <= y_top:
            y_bottom = min(y_top + 1, rows - 1)
        crop = mu_t_matrix[y_top:y_bottom + 1, x_start:x_end + 1]
        vals = crop[(np.isfinite(crop)) & (crop > 0)]
        med = float(np.nanmedian(vals)) if vals.size > 0 else 0.0
        st = float(np.nanstd(vals)) if vals.size > 0 else 0.0
        return med, st, vals  # <--- ДОБАВЛЕН ВОЗВРАТ СЫРЫХ ДАННЫХ

    roi_stats = []
    raw_mu_s_arrays = []  # <--- НОВЫЙ СПИСОК ДЛЯ СЫРЫХ МАССИВОВ

    present_rb = [rb for rb in raw_boundaries if rb and len(rb) > 0]
    num_boundaries = len(present_rb)

    total_median, total_std, total_vals = 0.0, 0.0, np.array([])  # Инициализация для Total

    if num_boundaries == 0:
        return {'filename': filename, 'roi_stats': [], 'total': {'median': 0.0, 'std': 0.0}, 'raw_mu_s_data': []}

    if num_boundaries == 1:
        rb_top = present_rb[0]
        y_top = int(np.nanmax(rb_top) + 1)
        y_bottom = rows - 1

        median, std, vals = get_stats_in_rect(y_top, y_bottom, x1, x2)

        roi_stats.append({'median': median, 'std': std})
        raw_mu_s_arrays.append(vals)  # Сохраняем массив
        total_median, total_std = median, std
        total_vals = vals

    else:
        # Инициализируем общий массив для Total
        all_vals_for_total = []

        for i in range(num_boundaries - 1):
            rb_top = present_rb[i]
            rb_bottom = present_rb[i + 1]
            y_top = int(np.nanmax(rb_top) + 1)
            y_bottom = int(np.nanmin(rb_bottom) - 1)

            median, std, vals = get_stats_in_rect(y_top, y_bottom, x1, x2)

            roi_stats.append({'median': median, 'std': std})
            raw_mu_s_arrays.append(vals)  # Сохраняем массив
            all_vals_for_total.append(vals)

        # Пересчитываем Total на основе объединенных массивов (если не пусто)
        if all_vals_for_total:
            total_vals = np.concatenate(all_vals_for_total)
            if total_vals.size > 0:
                total_median = float(np.nanmedian(total_vals))
                total_std = float(np.nanstd(total_vals))

    # Записываем сырые данные. total_vals может быть пустым, если не было ROI.
    raw_mu_s_arrays.append(total_vals)

    new_record = {
        'filename': filename,
        'roi_stats': roi_stats,
        'total': {'median': total_median, 'std': total_std},
        'raw_mu_s_data': raw_mu_s_arrays  # <--- НОВОЕ ПОЛЕ: Сырые массивы Mu_s для ROI и Total
    }
    return new_record


def save_mu_s_matrix_to_file(filename: str, mu_t_matrix):
    """
    Сохраняет матрицу mu_t_matrix в .txt файл в подпапку 'Mu_s photos'.
    filename — basename изображения (например: 'Default_0047_Mode2D.png')
    """
    if mu_t_matrix is None:
        print("Mu_s Core: Матрица mu_s пуста, сохранение отменено.")
        return

    fs = STATE.project.fs
    if fs is None:
        print("Mu_s Core: Проект не открыт, сохранение невозможно.")
        return

    mu_s_dir = fs.mu_s_images()
    mu_s_dir.mkdir(parents=True, exist_ok=True)

    base_name = Path(filename).stem
    output_path = mu_s_dir / f"{base_name}.txt"

    try:
        np.savetxt(output_path, mu_t_matrix, fmt="%.6f", delimiter="\t")
        print(f"Mu_s Core: Матрица mu_s сохранена: {output_path}")
    except Exception as e:
        print(f"Mu_s Core: Ошибка сохранения {output_path}: {e}")


# ---------------------------
# ОСНОВНАЯ ЛОГИКА ОБНОВЛЕНИЯ ДАННЫХ
# ---------------------------
def _upsert_mu_s_list(new_record):
    """
    Обновляет или добавляет запись в CONSTANTS.CONSTANTS['Mu_s values']['Mu_s table list'].
    """
    mu_s_list = STATE.tables.mu_s
    if not isinstance(mu_s_list, list):
        mu_s_list = []

    filename = new_record.get('filename')

    for i, item in enumerate(mu_s_list):
        if base_name_of_file(item.get('filename')) == filename:
            mu_s_list[i] = new_record
            break
    else:
        mu_s_list.append(new_record)

    mu_s_list = _sort_by_filename(mu_s_list)
    STATE.tables.mu_s = mu_s_list
    print(f"Mu_s Core: Updated/Inserted record for {filename}. List size: {len(mu_s_list)}")

    return mu_s_list


def calculate_and_update_mu_s(item):
    """
    Полный цикл расчета mu_s (новая физическая модель):
    - без выравнивания
    - с многослойностью
    - с корректным расчетом фокуса
    """

    filename = base_name_of_file(
        item.get('filename') or item.get('path')
    )

    params = get_calculation_parameters()
    img = _safe_get_image_from_item(item)

    if img is None:
        print(f"Mu_s Core: Изображение для {filename} не найдено.")
        dpg.set_value(TAGS.text_fields.mu_s_table_counts, 'No images to process')
        return None

    # =========================
    # 1. Получаем границы
    # =========================
    raw_p, x_offset, length = get_boundary_info(filename)

    if raw_p is None:
        print(f"Mu_s Core: Границы для {filename} отсутствуют.")
        return None

    # =========================
    # 2. Расчет фокуса (новая модель)
    # =========================
    focus_profile = focus_position(
        raw_p,
        params['air_focus_depth'],
        img.shape[1],
        x_offset
    )

    # =========================
    # 3. Расчет mu_t (новая физика)
    # =========================
    mu_t_matrix = fast_process_image(
        img,
        raw_p,
        focus_profile,
        params,
        x_offset
    )

    if mu_t_matrix is None:
        print(f"Mu_s Core: Ошибка расчета mu_t для {filename}")
        return None

    # =========================
    # 4. Сохранение
    # =========================
    save_mu_s_matrix_to_file(filename, mu_t_matrix)

    # =========================
    # 5. Статистика по ROI
    # =========================
    table_mega = STATE.tables.boundaries

    table_entry = next(
        (e for e in table_mega if base_name_of_file(e.get('filename')) == filename),
        None
    )

    raw_boundaries = table_entry.get('raw_p', []) if table_entry else []

    new_record = _compute_roi_stats(
        filename,
        mu_t_matrix,
        raw_boundaries
    )

    _upsert_mu_s_list(new_record)

    return new_record


# ======================================================================
# 3. GUI ВЫВОД РЕЗУЛЬТАТОВ (БЕЗ ИЗМЕНЕНИЙ)
# ======================================================================

def update_mu_s_table_gui():
    table_tag = TAGS.tables.mu_s
    mu_s_list = STATE.tables.mu_s

    if not mu_s_list:
        print("Mu_s Core: Список mu_s пуст, таблица не обновлена.")
        if dpg.does_item_exist(table_tag):
            dpg.delete_item(table_tag, children_only=True)
        return

    num_roi = 0
    for record in mu_s_list:
        roi_stats = record.get('roi_stats', [])
        if roi_stats:
            num_roi = len(roi_stats)
            break

    if dpg.does_item_exist(table_tag):
        dpg.delete_item(table_tag, children_only=True)
    else:
        print(f"Ошибка: Таблица с тегом {table_tag} не существует.")
        return

    dpg.add_table_column(label="N", parent=table_tag)
    dpg.add_table_column(label="Filename", parent=table_tag)

    for i in range(num_roi):
        dpg.add_table_column(label=f"Mu_s {i + 2}-{i + 1} Med (1/mm)", parent=table_tag)
        dpg.add_table_column(label=f"Mu_s {i + 2}-{i + 1} Std (1/mm)", parent=table_tag)

    dpg.add_table_column(label="Total Med (1/mm)", parent=table_tag)
    dpg.add_table_column(label="Total Std (1/mm)", parent=table_tag)

    for idx, record in enumerate(mu_s_list):
        filename = record.get('filename', 'N/A')
        total_median = record.get('total', {}).get('median', 0.0)
        total_std = record.get('total', {}).get('std', 0.0)
        roi_stats = record.get('roi_stats', [])

        row_data = [str(idx+1), filename]

        for stats in roi_stats:
            row_data.append(f"{stats.get('median', 0.0):.4f}")
            row_data.append(f"{stats.get('std', 0.0):.4f}")

        row_data.append(f"{total_median:.4f}")
        row_data.append(f"{total_std:.4f}")

        with dpg.table_row(parent=table_tag):
            for item in row_data:
                dpg.add_text(item)
    print(f"Mu_s Core: Таблица '{table_tag}' обновлена, {len(mu_s_list)} записей, {num_roi} ROI.")


def refresh_mu_s_for_selected(sender=None, app_data=None, user_data=None):

    if STATE.param_save.known_ri:
        if STATE.param_save.homogenious:
            if STATE.param_save.low_boundary:
                if len(STATE.param_save.ri_list) != 3:
                    dpg.set_value(TAGS.text_fields.mu_s_table_counts,
                                  'You have to set correct number of RIs. Must be 3!')
                    return
            else:
                if len(STATE.param_save.ri_list) != 2:
                    dpg.set_value(TAGS.text_fields.mu_s_table_counts,
                                  'You have to set correct number of RIs. Must be 2!')
                    return
        else:
            if STATE.param_save.low_boundary:
                if len(STATE.param_save.ri_list) != STATE.param_save.boundaries_amount + 2:
                    dpg.set_value(TAGS.text_fields.mu_s_table_counts,
                                  f'You have to set correct number of RIs. Must be {STATE.param_save.boundaries_amount + 2}!')
                    return
            else:
                if len(STATE.param_save.ri_list) != STATE.param_save.boundaries_amount + 1:
                    dpg.set_value(TAGS.text_fields.mu_s_table_counts,
                                  f'You have to set correct number of RIs. Must be {STATE.param_save.boundaries_amount + 1}!')
                    return
    else:
        if len(STATE.param_save.ri_list) != 3:
            dpg.set_value(TAGS.text_fields.mu_s_table_counts,
                          'You have to set correct number of RIs. Must be 3!')
            return

    gallery = STATE.gallery_proc
    items = gallery.image_items if gallery.image_items is not None else []
    selected_indices = sorted(list(gallery.selected_indices)) if gallery.selected_indices is not None else {}

    if not selected_indices:
        print("Mu_s Core: Нет выбранных индексов для обработки.")
        return

    print(f"Mu_s Core: Запуск расчета для {len(selected_indices)} элементов.")
    processed = 0
    total = len(selected_indices)

    for idx in selected_indices:
        if not (0 <= idx < len(items)):
            continue
        item = items[idx]

        result = calculate_and_update_mu_s(item)

        if result is not None:
            processed += 1

            # 🔥 ОБНОВЛЕНИЕ СЧЁТЧИКА
            dpg.set_value(
                TAGS.text_fields.mu_s_table_counts,
                f"Processed: {processed} / {total}"
            )

    print("Mu_s Core: Расчет завершен.")
    dpg.enable_item(TAGS.checkboxes.images_mu_s)
    update_mu_s_table_gui()
    dpg.enable_item(TAGS.checkboxes.mu_s)