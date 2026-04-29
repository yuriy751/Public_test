import os
import cv2
import numpy as np
import dearpygui.dearpygui as dpg
from pathlib import Path

from PIL.ImImagePlugin import SAVE

from .state import STATE
from .tags import TAGS


def _norm_name(x: str) -> str:
    """Каноническое имя файла (без пути)."""
    return Path(x).name if x else ""


def get_boundary_from_table(filename):
    """
    filename может быть путём или именем файла
    """
    mega_list = STATE.tables.boundaries
    if not mega_list:
        return None, 0

    # ⬇️ НОРМАЛИЗАЦИЯ
    target_name = Path(filename).name

    found_item = None
    found_idx = -1

    for i, item in enumerate(mega_list):
        item_name = Path(item.get("filename", "")).name

        if item_name == target_name:
            found_item = item
            found_idx = i
            break

    if found_item is None:
        return None, 0

    raw_p = found_item.get("raw_p", [])
    if not raw_p:
        return None, 0

    boundary_array = raw_p[0]

    # ---- X offset ----
    g_x_min = STATE.boundaries.global_x_min
    x_offset = 0

    if isinstance(g_x_min, list):
        if 0 <= found_idx < len(g_x_min):
            x_offset = int(g_x_min[found_idx])
    elif isinstance(g_x_min, (int, float)):
        x_offset = int(g_x_min)

    return boundary_array, x_offset


def _prepare_image_data(img, target_w, target_h):
    """
    Ресайзит изображение и готовит данные для текстуры.
    """
    img_resized = cv2.resize(img, (target_w, target_h), interpolation=cv2.INTER_AREA)

    if img_resized.ndim == 2:
        img_resized = cv2.cvtColor(img_resized, cv2.COLOR_GRAY2RGBA)
    elif img_resized.shape[2] == 3:
        img_resized = cv2.cvtColor(img_resized, cv2.COLOR_BGR2RGBA)

    data = (img_resized.astype(np.float32) / 255.0).flatten()
    return data


def _update_dynamic_texture(tex_tag, w, h, data):
    parent_reg = TAGS.registry.mu_s

    if not dpg.does_item_exist(tex_tag):
        dpg.add_dynamic_texture(w, h, data, tag=tex_tag, parent=parent_reg)
    else:
        cfg = dpg.get_item_configuration(tex_tag)
        # if cfg.get("width") == w and cfg.get("height") == h:
        #     dpg.set_value(tex_tag, data)
        # else:
        if dpg.does_alias_exist(tex_tag):
            dpg.remove_alias(tex_tag)
        dpg.delete_item(tex_tag)
        new_id = dpg.generate_uuid()
        dpg.add_dynamic_texture(w, h, data, tag=new_id, parent=parent_reg)
        dpg.add_alias(tex_tag, new_id)


def clear_dynamic_texture(
    tex_tag,
    width,
    height,
    gray=True,
    alpha=0.5,
    parent_reg=TAGS.registry.mu_s
):
    """
    Создаёт или обновляет текстуру-заглушку.
    gray=True  -> серая
    gray=False -> чёрная
    """
    if gray:
        val = 0.1
    else:
        val = 0.0

    data = np.full(
        (height, width, 4),
        (val, val, val, alpha),
        dtype=np.float32
    ).flatten()

    if not dpg.does_item_exist(tex_tag):
        dpg.add_dynamic_texture(width, height, data, tag=tex_tag, parent=parent_reg)
        return

    cfg = dpg.get_item_configuration(tex_tag)
    if cfg.get("width") == width and cfg.get("height") == height:
        dpg.set_value(tex_tag, data)
        return

    if dpg.does_alias_exist(tex_tag):
        dpg.remove_alias(tex_tag)

    dpg.delete_item(tex_tag)
    new_id = dpg.generate_uuid()
    dpg.add_dynamic_texture(width, height, data, tag=new_id, parent=parent_reg)
    dpg.add_alias(tex_tag, new_id)


def load_images_mu_s():
    """
    Формирует список путей на основе выбора в галерее.
    """
    print(f'State of parameters:\n'
          f'Known RI: {STATE.param_save.known_ri}\n'
          f'Homogenious: {STATE.param_save.homogenious}\n'
          f'Low is a boundary: {STATE.param_save.low_boundary}\n'
          f'Boundaries amount: {STATE.param_save.boundaries_amount}\n'
          f'RI list: {STATE.param_save.ri_list}\t amount: {len(STATE.param_save.ri_list)}')
    if STATE.param_save.known_ri:
        if STATE.param_save.homogenious:
            if STATE.param_save.low_boundary:
                if len(STATE.param_save.ri_list) != 3:
                    dpg.set_value(TAGS.text_fields.mu_s_filename,
                                  'You have to set correct number of RIs. Must be 3!')
                    return
            else:
                if len(STATE.param_save.ri_list) != 2:
                    dpg.set_value(TAGS.text_fields.mu_s_filename,
                                  'You have to set correct number of RIs. Must be 2!')
                    return
        else:
            if STATE.param_save.low_boundary:
                if len(STATE.param_save.ri_list) != STATE.param_save.boundaries_amount + 2:
                    dpg.set_value(TAGS.text_fields.mu_s_filename,
                                  f'You have to set correct number of RIs. Must be {STATE.param_save.boundaries_amount + 2}!')
                    return
            else:
                if len(STATE.param_save.ri_list) != STATE.param_save.boundaries_amount + 1:
                    dpg.set_value(TAGS.text_fields.mu_s_filename,
                                  f'You have to set correct number of RIs. Must be {STATE.param_save.boundaries_amount + 1}!')
                    return
    else:
        if len(STATE.param_save.ri_list) != 3:
            dpg.set_value(TAGS.text_fields.mu_s_filename,
                          'You have to set correct number of RIs. Must be 3!')
            return

    gallery_values = STATE.gallery_proc
    all_items = gallery_values.image_items if gallery_values.image_items is not None else []
    selected_indices = gallery_values.selected_indices or set()

    mu_s_images = [
        all_items[i]["path"]
        for i in sorted(selected_indices)
        if 0 <= i < len(all_items)
    ]

    STATE.mu_s.images = mu_s_images
    STATE.mu_s.current_index = 0

    count = len(mu_s_images)
    dpg.set_value(TAGS.text_fields.mu_s_counter, f"Loaded: {count}")

    if count > 0:
        show_mu_s_image_by_index(0)
    else:
        print("[Mu_s Gallery] No images selected.")

        tex_tag = TAGS.textures.mu_s
        drawlist_tag = TAGS.drawlists.mu_s

        # разумный дефолт
        w = int(STATE.constants.original_width)
        h = int(STATE.constants.original_height)

        clear_dynamic_texture(tex_tag, w, h, gray=True)
        dpg.delete_item(drawlist_tag, children_only=True)
        dpg.draw_image(tex_tag, pmin=(0, 0), pmax=(w, h), parent=drawlist_tag)

        dpg.set_value(TAGS.text_fields.mu_s_filename, "— no image —")


def draw_focus_line(drawlist_tag, raw_p, x_offset, scale_x, scale_y, original_h):
    """
    Рисует линию фокуса, учитывающую преломление.
    Использует предрассчитанные показатели преломления (ri_list),
    сохраняя при этом оригинальную математику расчета (z_phys += dist * n).
    """
    if not raw_p or not isinstance(raw_p, (list, tuple)) or raw_p[0] is None:
        return
    # Необходимо написать проверку на количество ПП и слоёв, гомогенность, нижней границы

    try:
        # ПРОВЕРКА И ПРИВЕДЕНИЕ ТИПА: гарантируем, что x_offset - это число
        if isinstance(x_offset, (list, np.ndarray)):
            # Если случайно передали список/массив, берем первое значение или 0
            start_x = int(x_offset[0]) if len(x_offset) > 0 else 0
        else:
            start_x = int(x_offset) if x_offset is not None else 0

        air_focus_depth = float(dpg.get_value(TAGS.inputs.focus_position))
        use_low = dpg.get_value(TAGS.checkboxes.low_boundary)

        n_layers_full = STATE.param_save.ri_list

    except (TypeError, ValueError, AttributeError) as e:
        print(f"Draw Focus Error: Ошибка параметров ({e})")
        return

    points = []
    width = len(raw_p[0])
    active_boundaries = raw_p

    for col in range(width):
        # Сбор границ для текущего столбца
        col_borders = []
        for b_arr in active_boundaries:
            if col < len(b_arr) and b_arr[col] is not None and not np.isnan(b_arr[col]):
                col_borders.append(b_arr[col])

        col_borders.sort()

        # Расчет физического фокуса (z_phys)
        remaining_nom = air_focus_depth
        z_phys = 0.0
        last_border_y = 0.0
        layer_index = 0

        for border_y in col_borders:
            dist_nom = border_y - last_border_y

            # Безопасное получение текущего n на случай непредвиденного количества границ
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

        # Если номинальный фокус оказался ниже последней границы
        if remaining_nom > 0:
            current_n = n_layers_full[layer_index] if layer_index < len(n_layers_full) else 1.0
            z_phys += remaining_nom * current_n

        focus_y = z_phys

        # Отрисовка
        if 0 <= focus_y <= original_h:
            # (int + int) * float
            screen_x = (start_x + col) * scale_x
            screen_y = focus_y * scale_y
            points.append([screen_x, screen_y])

    if len(points) > 1:
        dpg.draw_polyline(points, color=(255, 255, 0, 255), thickness=2, parent=drawlist_tag)


def show_mu_s_image_by_index(idx):
    paths = STATE.mu_s.images
    if not paths:
        return

    idx = max(0, min(idx, len(paths) - 1))
    STATE.mu_s.current_index = idx
    filename = paths[idx]
    fs = STATE.project.fs

    # Путь к изображению (обычно это папка с результатами или исходниками с границами)
    img_path = fs.images_with_boundaries() / filename

    img = cv2.imread(str(img_path), cv2.IMREAD_UNCHANGED)
    if img is None:
        print(f"Mu_s Core: Не удалось прочитать изображение {filename}")
        return

    orig_h, orig_w = img.shape[:2]

    # 1. Расчет размеров отображения

    target_w = dpg.get_item_width(TAGS.child_windows.mu_s_focus)
    target_h = dpg.get_item_height(TAGS.child_windows.mu_s_focus)
    target_w, target_h = max(1, target_w), max(1, target_h)

    # 2. Обновление текстуры
    data = _prepare_image_data(img, target_w, target_h)
    tex_tag = TAGS.textures.mu_s
    _update_dynamic_texture(tex_tag, target_w, target_h, data)

    # 3. Очистка и отрисовка базового слоя
    drawlist_tag = TAGS.drawlists.mu_s
    dpg.delete_item(drawlist_tag, children_only=True)
    dpg.draw_image(tex_tag, pmin=(0, 0), pmax=(target_w, target_h), uv_min=[0, 0], uv_max=[1, 1], parent=drawlist_tag)

    # 4. Отрисовка многослойного фокуса
    # Ищем запись в таблице границ по нормализованному имени
    filename_norm = _norm_name(filename)
    table_mega = STATE.tables.boundaries
    entry = next((e for e in table_mega if _norm_name(e.get('filename')) == filename_norm), None)

    if entry and entry.get('raw_p'):
        raw_p = entry['raw_p']

        # Берем смещение X из настроек ROI (так как расчет Mu_t шел именно там)
        x_offset = STATE.boundaries.global_x_min if STATE.boundaries.global_x_min is not None else 0

        # Коэффициенты масштабирования для перевода из пикселей в экранные координаты
        scale_x = STATE.scale.scale * STATE.scale.window_scale
        scale_y = STATE.scale.scale * STATE.scale.window_scale

        # Вызываем нашу новую функцию отрисовки, которая умеет в 5 границ
        draw_focus_line(
            drawlist_tag=drawlist_tag,
            raw_p=raw_p,
            x_offset=x_offset,
            scale_x=scale_x,
            scale_y=scale_y,
            original_h=orig_h
        )
    else:
        print(f"Mu_s Core: Данные границ (raw_p) не найдены для {filename}")

    # Обновление инфо-строки
    dpg.set_value(TAGS.text_fields.mu_s_filename,
                  f"{os.path.basename(filename)} ({idx + 1}/{len(paths)})")


def update_focus_line_only():
    """Обновляет вид (перерисовывает линию с новыми параметрами)."""
    idx = STATE.mu_s.current_index if STATE.mu_s.current_index is not None else 0
    show_mu_s_image_by_index(idx)


def show_next_mu_s():
    paths = STATE.mu_s.images if STATE.mu_s.images is not None else []
    if not paths: return
    curr = STATE.mu_s.current_index if STATE.mu_s.current_index is not None else 0
    show_mu_s_image_by_index((curr + 1) % len(paths))


def show_prev_mu_s():
    paths = STATE.mu_s.images if STATE.mu_s.images is not None else []
    if not paths: return
    curr = STATE.mu_s.current_index if STATE.mu_s.current_index is not None else 0
    show_mu_s_image_by_index((curr - 1) % len(paths))
