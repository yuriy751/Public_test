# Boundaries_images_gallery.py

import os
import cv2
import numpy as np
import dearpygui.dearpygui as dpg
from .state import STATE
from .tags import TAGS
from .interface_functions.draw_list_resize import draw_resize

AUTO_FIT_TO_CONTAINER = True

def resize():
    draw_resize()
    scale_ = STATE.scale.scale
    new_w, new_h = STATE.constants.original_width*scale_, STATE.constants.original_height*scale_
    dpg.configure_item(TAGS.child_windows.boundary,
                       width=int(new_w),
                       height=int(new_h))
    dpg.configure_item(TAGS.drawlists.boundary,
                       width=int(new_w),
                       height=int(new_h))
    dpg.configure_item(TAGS.tables.boundaries,
                       height=int(new_h))
    dpg.configure_item(TAGS.plots.optical_thickness,
                       height=dpg.get_item_height(TAGS.windows.main) - (
                                   STATE.constants.const_2 + STATE.constants.const_1 +
                                   dpg.get_item_height(TAGS.child_windows.boundary)
                                   ))

def _get_container_size():
    tag = TAGS.drawlists.boundary
    if dpg.does_item_exist(tag):
        return dpg.get_item_width(tag), dpg.get_item_height(tag)
    return None, None


def load_images_for_boundaries():
    """
    Загружает список изображений не из папки, а из выбранного множества
    CONSTANTS['Boundaries values']['FINAL_BOUNDARIES_SET'].
    """
    # Получаем set выбранных путей. Если он пуст или не существует, берем пустой set.
    selected_set = STATE.gallery_proc.final_boundaries_set

    STATE.boundaries.images.clear()

    # Превращаем set в сортированный список
    if selected_set:
        # Сортируем пути по алфавиту
        sorted_paths = sorted(list(selected_set))
        STATE.boundaries.images = sorted_paths

    STATE.boundaries.current_index = 0

    count = len(STATE.boundaries.images)

    if count > 0:
        print(f"[Gallery] Загружено {count} изображений из выборки.")
        dpg.set_value(TAGS.text_fields.image_name,
                      f"Selected: {count} images. Now you can press 'Show'")
    else:
        print("[Gallery] Нет выбранных изображений.")
        dpg.set_value(TAGS.text_fields.image_name,
                      "Select images in Gallery and press 'Images to process'")

    # Активируем кнопку только если есть что показывать
    dpg.configure_item(TAGS.buttons.show_boundary_image, enabled=(count > 0))
    # resize()


def _prepare_image_data(img, target_size=None):
    """Возвращает (w, h, data) для текстуры из PIL или OpenCV изображения."""
    if target_size:
        img = cv2.resize(img, target_size, interpolation=cv2.INTER_AREA)
    if img.ndim == 2:
        img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGBA)
    elif img.shape[2] == 3:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGBA)
    h, w = img.shape[:2]
    data = (img.astype(np.float32) / 255.0).flatten()
    return w, h, data


def _update_dynamic_texture(tex_tag, w, h, data):
    """Обновление или создание динамической текстуры."""
    if not dpg.does_item_exist(tex_tag):
        dpg.add_dynamic_texture(w, h, data, tag=tex_tag,
                                parent=TAGS.registry.image)
    else:
        cfg = dpg.get_item_configuration(tex_tag)
        if cfg.get("width") == w and cfg.get("height") == h:
            dpg.set_value(tex_tag, data)
        else:
            # Полное пересоздание текстуры
            if dpg.does_alias_exist(tex_tag):
                dpg.remove_alias(tex_tag)
            dpg.delete_item(tex_tag)
            new_id = dpg.generate_uuid()
            dpg.add_dynamic_texture(w, h, data, tag=new_id,
                                    parent=TAGS.registry.image)
            dpg.add_alias(tex_tag, new_id)


def show_image_by_index(idx):
    """Показывает изображение по индексу. Вызывать только после показа окна!"""
    if not STATE.boundaries.images:
        print("[Gallery] Нет изображений для показа.")
        return

    idx = max(0, min(idx, len(STATE.boundaries.images)-1))
    STATE.boundaries.current_index = idx
    path = STATE.boundaries.images[idx]

    img = cv2.imread(path, cv2.IMREAD_UNCHANGED)
    if img is None:
        print(f"[Gallery] Не удалось открыть {path}")
        return

    drawlist_tag = TAGS.drawlists.boundary
    if not dpg.does_item_exist(drawlist_tag):
        print("[Gallery] Drawlist всё ещё не существует! Убедитесь, что окно открыто.")
        dpg.add_drawlist(tag=drawlist_tag,
                         width=dpg.get_item_width(TAGS.child_windows.boundary),
                         height=dpg.get_item_height(TAGS.child_windows.boundary),
                         parent=TAGS.child_windows.boundary)
        print('[Gallery] теперь создано')

    # Автоподгонка под размер drawlist
    if AUTO_FIT_TO_CONTAINER:
        cont_w, cont_h = _get_container_size()
        print(cont_w, cont_h)
        if cont_w and cont_h:
            target = (max(1, cont_w-10), max(1, cont_h-10))
            print('[Gallery] sm')
        else:
            target = None
    else:
        target = None

    target_size = (target[0], target[1]) if target else (img.shape[1], img.shape[0])
    # print(target_size)
    w, h, data = _prepare_image_data(img, target_size)
    # scale_ = min(dpg.get_item_width(drawlist_tag)/w, dpg.get_item_height(drawlist_tag)/h)
    tex_tag = TAGS.textures.boundary_image
    # w_, h_ = int(w*scale_), int(scale_*h)
    _update_dynamic_texture(tex_tag, w, h, data)

    # Удаляем старые элементы drawlist
    dpg.delete_item(drawlist_tag, children_only=True)
    # Добавляем изображение в drawlist
    dpg.draw_image(tex_tag, pmin=(0, 0), pmax=(w, h), parent=drawlist_tag)
    # Отображаем имя файла
    dpg.set_value(TAGS.text_fields.image_name, os.path.basename(path) +
                  f"\t{STATE.boundaries.current_index + 1}"
                  f"/{len(STATE.boundaries.images)}")
    print(f"[Gallery] Показано {os.path.basename(path)} ({w}x{h})")
    # resize()


def show_next_image():
    if not STATE.boundaries.images:
        return
    idx = (STATE.boundaries.current_index + 1) \
          % len(STATE.boundaries.images)
    show_image_by_index(idx)


def show_prev_image():
    if not STATE.boundaries.images:
        return
    idx = (STATE.boundaries.current_index - 1) \
          % len(STATE.boundaries.images)
    show_image_by_index(idx)
