# Gallery.py

import os
import shutil
from pathlib import Path

import cv2
import numpy as np
import dearpygui.dearpygui as dpg

from .tags import TAGS
from .state import STATE
from .state.Global_paths_changing import project_modified_function_true
from .project_io.tables_utils import remove_rows_by_filenames
from .Mu_s_Core_Calculations import update_mu_s_table_gui
from .Table_processing import process_table_data
from .Average_intensity_calculation import update_av_int_table_gui
from .ROI import update_roi_lines
from .Gallery_proc import layout_boundaries_gallery
from .Boundaries_images_gallery import load_images_for_boundaries, show_image_by_index
from .Mu_s_focus_imaging import show_mu_s_image_by_index
from .interface_functions.draw_list_resize import draw_resize


# ============================================================
# Guards
# ============================================================

def _require_project():
    if not STATE.project.is_open():
        raise RuntimeError("Gallery operation requires an open project")


# ============================================================
# Filesystem helpers (через ProjectFS)
# ============================================================

def import_image_to_project(src: Path) -> Path:
    """
    Копирует изображение в images_for_processing проекта.
    Имя гарантированно уникально.
    """
    _require_project()

    dst_dir = STATE.project.fs.images_for_processing()
    dst_dir.mkdir(parents=True, exist_ok=True)

    dst = dst_dir / src.name
    shutil.copy2(src, dst)
    return dst


def save_current_image_for_roi():
    """
    Сохраняет текущее изображение в main_images/image_for_roi.png
    """
    _require_project()

    if STATE.gallery.current_image is None:
        return

    dst = STATE.project.fs.main_images() / "image_for_roi.png"
    cv2.imwrite(str(dst), STATE.gallery.current_image)


# ============================================================
# Textures
# ============================================================

def load_image_as_texture(path: str):
    img = cv2.imread(path, cv2.IMREAD_UNCHANGED)
    if img is None:
        return None

    if img.ndim == 2:
        img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGBA)
    else:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGBA)

    h, w = img.shape[:2]
    scale = STATE.constants.thumb_size / max(w, h)
    new_w = max(1, int(w * scale))
    new_h = max(1, int(h * scale))

    img_resized = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_AREA)
    data = (img_resized.astype(np.float32) / 255.0).flatten()

    tex_tag = f"tex_{dpg.generate_uuid()}"
    dpg.add_static_texture(
        new_w,
        new_h,
        data,
        parent=TAGS.registry.boundary,
        tag=tex_tag
    )
    return tex_tag


# ============================================================
# Gallery logic
# ============================================================

def add_images_to_gallery(paths):
    """
    Импорт изображений в проект + добавление в галерею.
    """
    _require_project()

    existing = {item["path"] for item in STATE.gallery.image_items}
    changed = False

    for p in paths:
        src = Path(p)
        if not src.exists():
            continue

        dst = import_image_to_project(src)
        dst_str = str(dst)

        if dst_str in existing:
            continue

        tex = load_image_as_texture(dst_str)
        if tex is None:
            continue

        STATE.gallery.image_items.append({
            "path": dst_str,
            "texture": tex
        })
        changed = True

    if changed:
        layout_gallery()
        project_modified_function_true(STATE.project)


def layout_gallery():
    if not dpg.does_item_exist(TAGS.child_windows.gallery):
        return

    dpg.delete_item(TAGS.child_windows.gallery, children_only=True)

    if not STATE.gallery.image_items:
        return

    gallery_width = dpg.get_item_width(TAGS.child_windows.gallery)
    cell_w = STATE.constants.thumb_size + 20
    columns = max(1, gallery_width // cell_w)

    row_group = None
    col = 0

    for idx, item in enumerate(STATE.gallery.image_items):
        selected = idx in STATE.gallery.selected_indices
        tint = (200, 200, 255, 255) if selected else (255, 255, 255, 255)

        if col == 0:
            row_group = dpg.add_group(
                horizontal=True,
                parent=TAGS.child_windows.gallery
            )

        with dpg.group(parent=row_group):
            dpg.add_image_button(
                item["texture"],
                tag=f"img_btn_{idx}",
                tint_color=tint,
                callback=image_click_callback,
                user_data=idx
            )
            dpg.add_text(
                os.path.basename(item["path"]),
                wrap=STATE.constants.thumb_size
            )

        col += 1
        if col >= columns:
            col = 0


def image_click_callback(sender, app_data, user_data):
    idx = user_data

    if dpg.is_key_down(dpg.mvKey_LControl):
        if idx in STATE.gallery.selected_indices:
            STATE.gallery.selected_indices.discard(idx)
        else:
            STATE.gallery.selected_indices.add(idx)

    elif dpg.is_key_down(dpg.mvKey_LShift) and STATE.gallery.last_selected is not None:
        lo = min(STATE.gallery.last_selected, idx)
        hi = max(STATE.gallery.last_selected, idx)
        for i in range(lo, hi + 1):
            STATE.gallery.selected_indices.add(i)

    else:
        STATE.gallery.selected_indices.clear()
        STATE.gallery.selected_indices.add(idx)

    STATE.gallery.last_selected = idx
    layout_gallery()


def delete_images():
    """
    Удаляет выбранные изображения ФИЗИЧЕСКИ из проекта.
    Синхронно обновляет:
      - галереи
      - STATE.tables (boundaries, mu_s, av_int)
      - GUI-таблицы
    """
    _require_project()

    if not STATE.gallery.selected_indices:
        return

    removed_filenames: set[str] = set()

    # ---------- 1. Удаление файлов + gallery ----------
    for idx in sorted(STATE.gallery.selected_indices, reverse=True):
        item = STATE.gallery.image_items[idx]
        filename = Path(item["path"]).name
        filename_2 = Path(item["path"]).stem
        removed_filenames.add(filename)

        dirs_to_check = [
            STATE.project.fs.images_for_processing(),
            STATE.project.fs.images_with_boundaries(),
            STATE.project.fs.mu_s_images(),
        ]

        for dir_path in dirs_to_check:
            file_path = dir_path / filename
            file_path_2 = dir_path / (filename_2 + '.txt')
            print(f'[Gallery] {file_path}\n'
                  f'[Gallery] {file_path_2}')
            if file_path.exists():
                try:
                    file_path.unlink()
                    print(f'Удалил всё остальное')
                except Exception as e:
                    print(f"[Delete] Failed to delete {file_path}: {e}")
            elif file_path_2.exists():
                try:
                    file_path_2.unlink()
                    print(f'Удалил mu_s')
                except Exception as e:
                    print(f"[Delete] Failed to delete {file_path_2}: {e}")

        del STATE.gallery.image_items[idx]

    STATE.gallery.selected_indices.clear()
    STATE.gallery.last_selected = None

    layout_gallery()

    # ---------- 2. gallery_proc ----------
    if hasattr(STATE, "gallery_proc") and hasattr(STATE.gallery_proc, "image_items"):
        STATE.gallery_proc.image_items = [
            item for item in STATE.gallery_proc.image_items
            if Path(item["path"]).name not in removed_filenames
        ]
        STATE.gallery_proc.selected_indices.clear()
        layout_boundaries_gallery()

    # ---------- Boundaries gallery ----------
    if hasattr(STATE.gallery_proc, "final_boundaries_set"):
        STATE.gallery_proc.final_boundaries_set = {
            p for p in STATE.gallery_proc.final_boundaries_set
            if Path(p).name not in removed_filenames
        }

    # Перезагружаем boundaries gallery
    load_images_for_boundaries()

    # Если текущий индекс вышел за границу — поправим
    if STATE.boundaries.images:
        show_image_by_index(
            min(
                STATE.boundaries.current_index,
                len(STATE.boundaries.images) - 1
            )
        )
    else:
        dpg.set_value(
            TAGS.text_fields.image_name,
            "Select images in Gallery and press 'Images to process'"
        )

        # ---------- Mu_s gallery ----------
    STATE.mu_s.images = [
        p for p in STATE.mu_s.images
        if Path(p).name not in removed_filenames
    ]

    if STATE.mu_s.images:
        STATE.mu_s.current_index = min(
            STATE.mu_s.current_index or 0,
            len(STATE.mu_s.images) - 1
        )
        show_mu_s_image_by_index(STATE.mu_s.current_index)
        dpg.set_value(
            TAGS.text_fields.mu_s_counter,
            f"Loaded: {len(STATE.mu_s.images)}"
        )
    else:
        STATE.mu_s.current_index = 0
        dpg.set_value(TAGS.text_fields.mu_s_counter, "Loaded: 0")

    # ---------- 3. TABLES CORE ----------
    STATE.tables.boundaries = remove_rows_by_filenames(
        STATE.tables.boundaries, removed_filenames
    )

    STATE.tables.mu_s = remove_rows_by_filenames(
        STATE.tables.mu_s, removed_filenames
    )

    STATE.tables.av_int = remove_rows_by_filenames(
        STATE.tables.av_int, removed_filenames
    )

    # ---------- 4. GUI UPDATE ----------
    # Boundaries
    table_tag = TAGS.tables.boundaries
    if dpg.does_item_exist(table_tag):
        dpg.delete_item(table_tag, children_only=True)
    if STATE.tables.boundaries:
        process_table_data()  # корректно пересоберёт таблицу
    else:
        print("[Delete] Boundaries table cleared.")

    # Mu_s
    update_mu_s_table_gui()

    # Average Intensity
    update_av_int_table_gui()

    # ---------- 5. Project state ----------
    # Проверить, остались ли изображения и убрать возможность ставить галочки, а также поменять значения на Flase
    # print(any(STATE.project.fs.images_for_processing().iterdir()))
    if not any(STATE.project.fs.images_for_processing().iterdir()):
        print('There is no images left')
        check_boxes_list = [
            TAGS.checkboxes.images_default,
            TAGS.checkboxes.images_boundarise,
            TAGS.checkboxes.images_mu_s
        ]
        for check_box in check_boxes_list:
            dpg.set_value(check_box, False)
            dpg.disable_item(check_box)

    project_modified_function_true(STATE.project)

    print(
        f"[Delete] Removed {len(removed_filenames)} images: "
        f"{sorted(removed_filenames)}"
    )



def on_images_selected(sender, app_data):
    selections = app_data.get("selections", {})
    if not selections:
        return

    add_images_to_gallery(list(selections.values()))

    STATE.settings.last_processing_folder = app_data["current_path"]
    STATE.settings.save()

    dpg.configure_item(
        TAGS.dialogs.choose_images,
        default_path=STATE.settings.last_processing_folder
    )
    dpg.enable_item(TAGS.checkboxes.images_default)


# ============================================================
# Image processing (selection → current_image)
# ============================================================

def images_to_process():
    _require_project()

    sorted_sel = sorted(STATE.gallery.selected_indices)
    STATE.boundaries.chosen_photos = sorted_sel

    if not sorted_sel:
        return

    if len(sorted_sel) == 1:
        path = STATE.gallery.image_items[sorted_sel[0]]["path"]
        STATE.gallery.current_image = cv2.imread(path)

    else:
        path1 = STATE.gallery.image_items[sorted_sel[0]]["path"]
        path2 = STATE.gallery.image_items[sorted_sel[-1]]["path"]

        img1 = cv2.imread(path1, cv2.IMREAD_GRAYSCALE)
        img2 = cv2.imread(path2, cv2.IMREAD_GRAYSCALE)

        if img1.shape != img2.shape:
            img2 = cv2.resize(img2, (img1.shape[1], img1.shape[0]))

        zeros = np.zeros_like(img1)
        STATE.gallery.current_image = cv2.merge([img2, zeros, img1])

    if STATE.gallery.current_image is None:
        return

    # --------------------------------------------------
    # Save for ROI
    # --------------------------------------------------
    save_current_image_for_roi()

    # --------------------------------------------------
    # Update geometry
    # --------------------------------------------------
    h, w = STATE.gallery.current_image.shape[:2]
    STATE.constants.original_height = h
    STATE.constants.original_width = w

    for tag in vars(TAGS.sliders).values():
        max_val = w if "x" in tag else h
        dpg.configure_item(tag, max_value=max_val)

    update_boundary_texture()
    update_roi_lines()

    try:
        from .interface_functions.resize import resize_gui
        resize_gui()
    except Exception:
        pass

    if STATE.project.fs.octp_file is not None:
        if dpg.does_item_exist(TAGS.buttons.process):
            dpg.enable_item(TAGS.buttons.process)
        if dpg.does_item_exist(TAGS.buttons.viewing_photos):
            dpg.enable_item(TAGS.buttons.viewing_photos)

    win_w = dpg.get_item_width(TAGS.windows.boundaries)
    win_h = dpg.get_item_height(TAGS.windows.boundaries)

    if win_w < 50 or win_h < 50:
        return

    draw_resize()
    scale_ = STATE.scale.scale * STATE.scale.window_scale

    new_w = int(STATE.constants.original_width * scale_)
    new_h = int(STATE.constants.original_height * scale_)

    # --- Обновляем размеры окна с картинкой и drawlist ---
    dpg.configure_item(TAGS.child_windows.imaging, width=new_w, height=new_h)
    dpg.configure_item(TAGS.drawlists.roi, width=new_w, height=new_h)
    dpg.configure_item(TAGS.child_windows.average_ascan, width=new_w,
                       height=(dpg.get_viewport_height()
                               - (STATE.constants.const_2 +
                                  STATE.constants.const_1 +
                                  dpg.get_item_height(TAGS.child_windows.imaging))))
    dpg.configure_item(TAGS.plots.ascan, width=new_w,
                       height=dpg.get_item_height(TAGS.child_windows.average_ascan))
    update_roi_lines()


# ============================================================
# Boundary texture
# ============================================================

def update_boundary_texture():
    scale = STATE.scale.scale

    width = int(max(1, STATE.constants.original_width * scale * STATE.scale.window_scale))
    height = int(max(1, STATE.constants.original_height * scale * STATE.scale.window_scale))

    # --------------------------------------------------
    # Формируем изображение
    # --------------------------------------------------
    if STATE.gallery.current_image is None:
        # Серая RGBA-текстура
        gray_value = 0.1  # 50% серого
        data = np.full(
            (height, width, 4),
            (gray_value, gray_value, gray_value, 0.5),
            dtype=np.float32
        ).flatten()
    else:
        resized = cv2.resize(
            STATE.gallery.current_image,
            (width, height),
            interpolation=cv2.INTER_AREA
        )

        if resized.ndim == 2:
            resized = cv2.cvtColor(resized, cv2.COLOR_GRAY2RGBA)
        elif resized.shape[2] == 3:
            resized = cv2.cvtColor(resized, cv2.COLOR_BGR2RGBA)

        data = (resized.astype(np.float32) / 255.0).flatten()

    # --------------------------------------------------
    # Создание / обновление текстуры
    # --------------------------------------------------
    if not dpg.does_item_exist(TAGS.textures.boundaries):
        dpg.add_dynamic_texture(
            width,
            height,
            data,
            tag=TAGS.textures.boundaries,
            parent=TAGS.registry.boundary
        )
        return

    cfg = dpg.get_item_configuration(TAGS.textures.boundaries)
    tex_w = cfg.get("width")
    tex_h = cfg.get("height")

    if tex_w == width and tex_h == height:
        dpg.set_value(TAGS.textures.boundaries, data)
        return

    if dpg.does_alias_exist(TAGS.textures.boundaries):
        dpg.remove_alias(TAGS.textures.boundaries)

    dpg.delete_item(TAGS.textures.boundaries)

    new_id = dpg.generate_uuid()
    dpg.add_dynamic_texture(
        width,
        height,
        data,
        tag=new_id,
        parent=TAGS.registry.boundary
    )

    dpg.add_alias(TAGS.textures.boundaries, new_id)

