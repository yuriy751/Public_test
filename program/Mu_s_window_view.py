# Mu_s_window_view.py

import dearpygui.dearpygui as dpg
from .state import STATE
from .tags import TAGS
from .ui_adapters.input_defaults import INPUT_DEFAULTS
import numpy as np
from matplotlib import cm
from pathlib import Path
import cv2  # Для ресайза и преобразования в BGR/RGBA (очень надежно)


# --- Вспомогательные функции для обработки данных ---

def process_and_get_texture_data(image_path, target_width, target_height, colormap=cm.viridis):
    """
    1. Загружает .txt, логарифмирует, нормирует.
    2. Применяет Colormap (получает RGBA).
    3. Использует cv2 для ресайза в target_width x target_height.
    4. Преобразует данные в 1D float32 RGBA для DPG.
    """
    try:
        # 1. Загрузка и логарифмирование
        image = np.loadtxt(image_path).astype(np.float32)
        min_value = min(dpg.get_value(TAGS.inputs.mu_s_view_min),
                        dpg.get_value(TAGS.inputs.mu_s_view_max))
        max_value = max(dpg.get_value(TAGS.inputs.mu_s_view_min),
                        dpg.get_value(TAGS.inputs.mu_s_view_max))
        image[image < min_value] = min_value
        image[image > max_value] = max_value

        diff = max_value - min_value

        normalized_image = ((image-min_value)/diff).astype(np.float32)

        # 3. Применение Colormap (получаем MxNx4 RGBA float64)
        colored_image_float = colormap(normalized_image)

        # 4. Преобразование в 8-битное изображение (0-255) для cv2
        # Умножаем на 255 и преобразуем в 8-битный беззнаковый int.
        colored_image_uint8 = (colored_image_float * 255).astype(np.uint8)

        # 5. Ресайз с помощью cv2
        # cv2 ожидает BGR или RGB порядок. matplotlib выводит RGB(A).
        # cv2.resize работает с 3D/4D массивами
        img_resized = cv2.resize(colored_image_uint8,
                                 (target_width, target_height),
                                 interpolation=cv2.INTER_AREA)

        # 6. Преобразование в финальный 1D float32 RGBA для DPG
        if img_resized.shape[2] == 3:
            # Если cv2 убрал альфа-канал (что иногда бывает), добавим его
            img_resized = cv2.cvtColor(img_resized, cv2.COLOR_RGB2RGBA)

        # Финальное преобразование: RGBA uint8 -> 1D RGBA float32 [0.0, 1.0]
        data = (img_resized.astype(np.float32) / 255.0).flatten()

        return data

    except Exception as e:
        print(f"Ошибка в обработке {image_path}: {e}")
        return None


def _update_dynamic_texture(tex_tag, w, h, data):
    """
    Надёжное обновление/пересоздание динамической текстуры с использованием паттерна Alias.
    (Код взят из вашего рабочего примера)
    """
    # Используем ваш тег для регистра текстур
    parent_reg = TAGS.registry.mu_s_images

    if not dpg.does_item_exist(tex_tag):
        # Если текстура не существует, создаем ее
        dpg.add_dynamic_texture(w, h, data, tag=tex_tag, parent=parent_reg)
    else:
        cfg = dpg.get_item_configuration(tex_tag)

        # Если размеры совпадают, просто обновляем данные
        if cfg.get("width") == w and cfg.get("height") == h:
            dpg.set_value(tex_tag, data)
        else:
            # Если размеры изменились: удаляем, создаем новую с новым ID и переназначаем алиас
            if dpg.does_alias_exist(tex_tag):
                dpg.remove_alias(tex_tag)

            # Удаляем старую текстуру (если она существует)
            if dpg.does_item_exist(cfg.get('id')):  # Используем фактический ID, а не алиас
                dpg.delete_item(cfg.get('id'))

            new_id = dpg.generate_uuid()
            dpg.add_dynamic_texture(w, h, data, tag=new_id, parent=parent_reg)
            dpg.add_alias(tex_tag, new_id)


# --- Основные функции UI-логики ---

def update_mu_s_image_display(index):
    """
    Обновляет отображаемое изображение в окне, используя данные из CONSTANTS.
    """
    paths = STATE.mu_s.images_windows

    TEXTURE_TAG = TAGS.textures.mu_s_images
    COUNTER_TAG = TAGS.text_fields.mu_s_images_counter
    DRAWLIST_TAG = TAGS.drawlists.mu_s_images

    if not (0 <= index < len(paths)):
        return

    path = paths[index]

    # Размеры Drawlist (целевые размеры для ресайза)
    if not dpg.does_item_exist(DRAWLIST_TAG): return
    drawlist_width = dpg.get_item_width(DRAWLIST_TAG)
    drawlist_height = dpg.get_item_height(DRAWLIST_TAG)

    if drawlist_width == 0 or drawlist_height == 0:
        print("Drawlist имеет нулевой размер, невозможно отрисовать.")
        return

    # 1. Обработка изображения и получение ресайзенных данных
    # Целевые W/H - это размеры Drawlist, так как мы хотим, чтобы текстура соответствовала контейнеру
    data = process_and_get_texture_data(path, drawlist_width, drawlist_height)

    if data is None:
        return

    # 2. Обновление/пересоздание текстуры
    # Используем надежную функцию _update_dynamic_texture
    _update_dynamic_texture(TEXTURE_TAG, drawlist_width, drawlist_height, data)

    # 3. Обновление Drawlist
    if dpg.does_item_exist(DRAWLIST_TAG):
        dpg.delete_item(DRAWLIST_TAG, children_only=True)

        # Отрисовка изображения: поскольку текстура уже имеет размер Drawlist,
        # просто рисуем ее от (0, 0) до (W, H). Масштабирование уже выполнено cv2.
        dpg.draw_image(TEXTURE_TAG,
                       pmin=(0, 0),
                       pmax=(drawlist_width, drawlist_height),
                       parent=DRAWLIST_TAG
                       )

    # 4. Обновление счетчика
    dpg.set_value(COUNTER_TAG,
                  f'Image {index + 1} / {len(paths)}: {Path(path).name}')

    # 5. Обновление состояния
    STATE.mu_s.current_index_window = index


def load_images():  # Ваша исходная функция load_images (переименована для чистоты)
    fs = STATE.project.fs
    COUNTER_TAG = TAGS.text_fields.mu_s_images_counter

    if fs is None:
        dpg.set_value(COUNTER_TAG, "Project isn't opened")
        return

    path_to_images = fs.mu_s_images()
    if not path_to_images.exists():
        dpg.set_value(COUNTER_TAG, "Folder with images isn't found")
        return

    image_files = sorted([p for p in path_to_images.iterdir() if p.suffix == '.txt'])

    if not image_files:
        STATE.mu_s.images_windows = []
        STATE.mu_s.current_index_window = -1
        dpg.set_value(COUNTER_TAG, "Нет изображений (.txt)")
        return

    STATE.mu_s.images_windows = [str(p) for p in image_files]
    STATE.mu_s.current_index_window = 0

    update_mu_s_image_display(STATE.mu_s.current_index_window)


def previous_image():
    paths = STATE.mu_s.images_windows
    current_index = STATE.mu_s.current_index_window

    if not paths or current_index <= 0: return
    update_mu_s_image_display(current_index - 1)


def next_image():
    paths = STATE.mu_s.images_windows
    current_index = STATE.mu_s.current_index_window

    if not paths or current_index >= len(paths) - 1: return
    update_mu_s_image_display(current_index + 1)


def delete_window():
    dpg.delete_item(TAGS.windows.mu_s_images)


def show_img():
    """
    Перерисовывает текущее изображение, используя текущие значения Min/Max
    из полей ввода DPG (которые считываются внутри process_and_get_texture_data).
    """
    # Получаем текущий индекс из состояния приложения
    current_index = STATE.mu_s.current_index_window if STATE.mu_s.current_index_window else -1

    if current_index >= 0:
        # Вызываем функцию отображения с текущим индексом
        # (update_mu_s_image_display вызовет process_and_get_texture_data)
        update_mu_s_image_display(current_index)
    else:
        print("Нет загруженного изображения для отображения.")


# --- Функция создания окна (с небольшим улучшением для инициализации) ---

def mu_s_window_creation():
    """
    Создает окно для просмотра изображений mu_s.
    """
    WINDOW_TAG = TAGS.windows.mu_s_images

    if not dpg.does_item_exist(WINDOW_TAG):

        # Размеры окна
        W = STATE.constants.original_width // 2
        H = STATE.constants.original_height // 2

        with dpg.window(label='Mu_s images', tag=WINDOW_TAG,
                        width=W + 400,
                        height=H + 100,
                        no_scrollbar=True, no_resize=True, no_collapse=True, no_close=True):

            # --- Заголовок и кнопка закрытия ---
            with dpg.group(horizontal=True, horizontal_spacing=20):
                dpg.add_button(label='Close window',
                               tag=TAGS.buttons.close_mu_s_image_window,
                               callback=delete_window)
                dpg.add_text(tag=TAGS.text_fields.mu_s_images_counter,
                             default_value="Images are not loaded")
                dpg.add_input_float(label='Min', tag=TAGS.inputs.mu_s_view_min,
                                    default_value=INPUT_DEFAULTS.mu_s_view_min,
                                    width=100, format='%.4f', callback=show_img)
                dpg.add_input_float(label='Max', tag=TAGS.inputs.mu_s_view_max,
                                    default_value=INPUT_DEFAULTS.mu_s_view_max,
                                    width=100, format='%.4f', callback=show_img)

            # --- Область для отображения изображения ---
            with dpg.child_window(tag=TAGS.child_windows.mu_s_images,
                                  width=W,
                                  height=H
                                  ):
                dpg.add_drawlist(tag=TAGS.drawlists.mu_s_images,
                                 width=W,
                                 height=H
                                 )

            # --- Кнопки навигации ---
            with dpg.group(horizontal=True, horizontal_spacing=20):
                dpg.add_button(label='Load images',
                               tag=TAGS.buttons.load_mu_s_images,
                               callback=load_images)
                dpg.add_button(label='Prev image',
                               tag=TAGS.buttons.prev_mu_s_image,
                               callback=previous_image)
                dpg.add_button(label='Next image',
                               tag=TAGS.buttons.next_mu_s_image,
                               callback=next_image)

            # Попытка загрузить изображения сразу после создания окна
            load_images()

    else:
        delete_window()
