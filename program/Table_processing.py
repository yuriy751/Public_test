# Table_processing.py

from pathlib import Path
import cv2
import numpy as np
import dearpygui.dearpygui as dpg
from .tags import TAGS
from .state import STATE


def boundaries_searching_npy(folder: Path, files_name: list[str]):
    """
    Поиск границ на изображениях.
    """
    out_list: list = []
    k = 1

    for name in files_name:
        if dpg.does_item_exist(TAGS.text_fields.table_counts):
            dpg.set_value(
                TAGS.text_fields.table_counts,
                f'Processed {k}/{len(files_name)} images'
            )

        in_ = []
        full_path = folder / name
        if not full_path.is_file():
            continue

        img = cv2.imread(str(full_path))
        if img is None:
            out_list.append([])
            continue

        for boundary_idx in sorted(STATE.constants.colourmap.keys()):
            boundary_idx_mass = np.asarray(STATE.constants.colourmap[boundary_idx])
            mask_exact = np.all(img == boundary_idx_mass, axis=2)
            y, x = np.where(mask_exact)
            in_.append(y)

            if len(x) > 0:
                STATE.boundaries.global_x_min.append(np.min(x).tolist())
                STATE.boundaries.global_x_max.append(np.max(x).tolist())

        out_list.append(in_)
        k += 1

    return out_list


def distances_function(in_list: list):
    """
    Вычисление статистик + СБОР СЫРЫХ ДАННЫХ для Origin Pro.
    """
    # Списки для статистик (как раньше)
    med_pixel_position, min_pixel_position, max_pixel_position = [], [], []
    med_distance, min_distance, max_distance = [], [], []
    med_total_dist, min_total_dist, max_total_dist = [], [], []

    # --- НОВЫЕ Списки для сырых данных (массивов точек) ---
    # Структура: Список [ Изображение 1 [Граница 1 массив, Граница 2 массив...], Изображение 2 ... ]
    raw_pixel_position = []
    raw_distance = []
    raw_total_dist = []  # Тут будет массив разниц для общей толщины

    for i in range(len(in_list)):
        # Временные списки для статистики текущего кадра
        med_pixel_position_in, min_pixel_position_in, max_pixel_position_in = [], [], []
        med_distance_in, min_distance_in, max_distance_in = [], [], []

        # Временные списки для СЫРЫХ данных текущего кадра
        raw_pixel_position_in = []
        raw_distance_in = []
        raw_total_dist_in = []  # Или None, если нет данных

        # Значения для статистики общей толщины
        m_tot, min_tot, max_tot = np.nan, np.nan, np.nan

        # 1. Отбор и сортировка (Верх -> Низ)
        present_boundaries = [b for b in in_list[i] if len(b) > 0]
        # Важно: Сортировка по медиане Y, чтобы порядок границ был правильным (сверху вниз)
        present_boundaries.sort(key=lambda b: np.median(b))

        # 2. Обработка ПОЗИЦИЙ (Positions)
        for bound in present_boundaries:
            arr = np.asarray(bound)

            # Статистика
            med_pixel_position_in.append(np.median(arr).item())
            min_pixel_position_in.append(np.min(arr).item())
            max_pixel_position_in.append(np.max(arr).item())

            # --- Сохраняем сырой массив ---
            # Используем tolist(), чтобы сохранить как обычный список Python внутри структуры,
            # это безопаснее для JSON/хранения, чем np.array разной длины.
            raw_pixel_position_in.append(arr.tolist())

            # 3. Обработка ДИСТАНЦИЙ (Distances)
        if len(present_boundaries) > 1:
            # А) Последовательные дистанции (1-2, 2-3...)
            for v in range(1, len(present_boundaries)):
                arr_curr = np.asarray(present_boundaries[v])
                arr_prev = np.asarray(present_boundaries[v - 1])

                # Обрезаем по минимальной длине, чтобы вычесть массивы
                slice_ = min(len(arr_curr), len(arr_prev))

                if slice_ > 0:
                    diff = np.abs(arr_curr[:slice_] - arr_prev[:slice_])

                    # Статистика
                    med_distance_in.append(np.median(diff).item())
                    min_distance_in.append(np.min(diff).item())
                    max_distance_in.append(np.max(diff).item())

                    # --- Сохраняем сырой массив разниц ---
                    raw_distance_in.append(diff.tolist())
                else:
                    med_distance_in.append(np.nan)
                    min_distance_in.append(np.nan)
                    max_distance_in.append(np.nan)
                    raw_distance_in.append([])  # Пустой список, если нет перекрытия

            # Б) ОБЩАЯ толщина (Самая нижняя - Самая верхняя)
            arr_first = np.asarray(present_boundaries[0])
            arr_last = np.asarray(present_boundaries[-1])

            slice_total = min(len(arr_first), len(arr_last))
            if slice_total > 0:
                diff_total = np.abs(arr_last[:slice_total] - arr_first[:slice_total])
                m_tot = np.median(diff_total).item()
                min_tot = np.min(diff_total).item()
                max_tot = np.max(diff_total).item()

                # --- Сохраняем сырой массив общей толщины ---
                raw_total_dist_in = diff_total.tolist()
            else:
                raw_total_dist_in = []

        # Сохранение результатов текущего кадра (статистика)
        med_pixel_position.append(med_pixel_position_in)
        min_pixel_position.append(min_pixel_position_in)
        max_pixel_position.append(max_pixel_position_in)

        med_distance.append(med_distance_in)
        min_distance.append(min_distance_in)
        max_distance.append(max_distance_in)

        med_total_dist.append(m_tot)
        min_total_dist.append(min_tot)
        max_total_dist.append(max_tot)

        # Сохранение СЫРЫХ результатов текущего кадра
        raw_pixel_position.append(raw_pixel_position_in)
        raw_distance.append(raw_distance_in)
        raw_total_dist.append(raw_total_dist_in)

    return (med_pixel_position, min_pixel_position, max_pixel_position,
            med_distance, min_distance, max_distance,
            med_total_dist, min_total_dist, max_total_dist,
            # Возвращаем новые сырые данные
            raw_pixel_position, raw_distance, raw_total_dist)


def process_table_data():
    fs = STATE.project.fs
    if fs is None or fs.root is None:
        print("[Table] Project is not opened.")
        return

    boundaries_dir = fs.images_with_boundaries()
    if not boundaries_dir.exists():
        print("[Table] No images_with_boundaries directory.")
        return

    # 1. Получаем выбранные файлы
    selected_set = STATE.gallery_proc.final_boundaries_set or set()
    if not selected_set:
        print("[Table] No images selected in Boundaries Gallery.")
        return

    files_to_process: list[str] = []

    for path in selected_set:
        p = Path(path)
        if p.exists() and p.parent == boundaries_dir:
            files_to_process.append(p.name)

    files_to_process.sort()
    if not files_to_process:
        print("[Table] Selected files not found in project.")
        return

    STATE.boundaries.global_x_min = []
    STATE.boundaries.global_x_max = []

    # 2. Обрабатываем файлы
    raw_boundaries = boundaries_searching_npy(
        boundaries_dir,
        files_to_process
    )

    num_boundaries = 2
    for b_list in raw_boundaries:
        present = [b for b in b_list if len(b) > 0]
        if present:
            num_boundaries = len(present)
            break

    num_distances = max(0, num_boundaries - 1)

    # Расчет математики (теперь распаковываем и новые переменные)
    (med_p, min_p, max_p,
     med_d, min_d, max_d,
     med_tot, min_tot, max_tot,
     raw_p, raw_d, raw_tot) = distances_function(raw_boundaries)

    # 3. --- LOGIC MERGE ---

    existing_list = STATE.tables.boundaries if STATE.tables.boundaries is not None else []
    if not isinstance(existing_list, list):
        existing_list = []

    data_map = {item['filename']: item for item in existing_list}

    # Обновляем данные
    for idx, filename in enumerate(files_to_process):
        new_row_data = {
            "filename": filename,
            # Статистика
            "med_p": med_p[idx], "min_p": min_p[idx], "max_p": max_p[idx],
            "med_d": med_d[idx], "min_d": min_d[idx], "max_d": max_d[idx],
            "med_total": med_tot[idx], "min_total": min_tot[idx], "max_total": max_tot[idx],

            # --- НОВЫЕ СЫРЫЕ ДАННЫЕ ---
            # raw_p[idx] - список списков (массивов координат Y для каждой границы)
            # raw_d[idx] - список списков (массивов разниц между границами)
            # raw_tot[idx] - список (массив разниц общей толщины)
            "raw_p": raw_p[idx],
            "raw_d": raw_d[idx],
            "raw_total": raw_tot[idx]
        }
        data_map[filename] = new_row_data

    final_list = sorted(data_map.values(), key=lambda x: x['filename'])

    for i, item in enumerate(final_list):
        item['id'] = i + 1

    STATE.tables.boundaries = final_list

    # 4. --- ОТРИСОВКА ТАБЛИЦЫ (Без изменений в логике отрисовки, только raw данные лежат в памяти) ---

    table_tag = TAGS.tables.boundaries
    if dpg.does_item_exist(table_tag):
        dpg.delete_item(table_tag, children_only=True)

        dpg.add_table_column(label="N", parent=table_tag)
        for i in range(num_boundaries):
            dpg.add_table_column(label=f"Med Pos {i + 1}", parent=table_tag)
            dpg.add_table_column(label=f"Min Pos {i + 1}", parent=table_tag)
            dpg.add_table_column(label=f"Max Pos {i + 1}", parent=table_tag)
        for i in range(num_distances):
            dpg.add_table_column(label=f"Med Dist {i + 1}-{i + 2}", parent=table_tag)
            dpg.add_table_column(label=f"Min Dist {i + 1}-{i + 2}", parent=table_tag)
            dpg.add_table_column(label=f"Max Dist {i + 1}-{i + 2}", parent=table_tag)
        dpg.add_table_column(label="Total Thick Med", parent=table_tag)
        dpg.add_table_column(label="Total Thick Min", parent=table_tag)
        dpg.add_table_column(label="Total Thick Max", parent=table_tag)

        pixel_size = dpg.get_value(TAGS.inputs.pixel_size)

        for row_data in final_list:
            with dpg.table_row(parent=table_tag):
                dpg.add_text(str(row_data["id"]))

                # Позиции
                for i in range(num_boundaries):
                    if i < len(row_data["med_p"]) and not np.isnan(row_data["med_p"][i]):
                        dpg.add_text(str(np.round(row_data["med_p"][i] * pixel_size, 1)))
                        dpg.add_text(str(np.round(row_data["min_p"][i] * pixel_size, 1)))
                        dpg.add_text(str(np.round(row_data["max_p"][i] * pixel_size, 1)))
                    else:
                        dpg.add_text("-")
                        dpg.add_text("-")
                        dpg.add_text("-")

                # Дистанции
                for i in range(num_distances):
                    if i < len(row_data["med_d"]) and not np.isnan(row_data["med_d"][i]):
                        dpg.add_text(str(np.round(row_data["med_d"][i] * pixel_size, 1)))
                        dpg.add_text(str(np.round(row_data["min_d"][i] * pixel_size, 1)))
                        dpg.add_text(str(np.round(row_data["max_d"][i] * pixel_size, 1)))
                    else:
                        dpg.add_text("-")
                        dpg.add_text("-")
                        dpg.add_text("-")

                # Total
                if not np.isnan(row_data["med_total"]):
                    dpg.add_text(str(np.round(row_data["med_total"] * pixel_size, 1)))
                    dpg.add_text(str(np.round(row_data["min_total"] * pixel_size, 1)))
                    dpg.add_text(str(np.round(row_data["max_total"] * pixel_size, 1)))
                else:
                    dpg.add_text("-")
                    dpg.add_text("-")
                    dpg.add_text("-")

    # Обновление глобальных границ для графиков
    if STATE.boundaries.global_x_min is not None \
            and STATE.boundaries.global_x_max is not None:
        # print('aboba')
        x1 = max(STATE.boundaries.global_x_min)
        x2 = min(STATE.boundaries.global_x_max)
        if STATE.boundaries.global_boundary_x1 is not None and \
                STATE.boundaries.global_boundary_x2 is not None:
            if int(x1) > STATE.boundaries.global_boundary_x1:
                STATE.boundaries.global_boundary_x1 = int(x1)
            if int(x2) < STATE.boundaries.global_boundary_x2:
                STATE.boundaries.global_boundary_x2 = int(x2)
        else:
            STATE.boundaries.global_boundary_x1 = x1
            STATE.boundaries.global_boundary_x2 = x2
    else:
        pass
    dpg.enable_item(TAGS.checkboxes.boundaries)
    print(STATE.boundaries.global_x_min, STATE.boundaries.global_x_max)
    print(f"[Table] Updated with RAW data. Total rows: {len(final_list)}.")
