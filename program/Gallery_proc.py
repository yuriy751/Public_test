# Gallery_proc.py

import dearpygui.dearpygui as dpg
from pathlib import Path
import cv2
import numpy as np

from .tags import TAGS
from .state import STATE
# from .Gallery import load_image_as_texture


# ============================================================
# Paths helpers
# ============================================================

def _get_images_with_boundaries_dir() -> Path | None:
    if not STATE.project.is_open():
        return None
    return STATE.project.fs.root / "images_with_boundaries"


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

def refresh_boundaries_gallery():
    """
    Сканирует папку images_with_boundaries и обновляет галерею.
    """
    boundaries_dir = _get_images_with_boundaries_dir()
    if boundaries_dir is None or not boundaries_dir.exists():
        return

    clear_boundaries_gallery_data()

    try:
        files = sorted(
            p for p in boundaries_dir.iterdir()
            if p.suffix.lower() in ('.png', '.jpg', '.jpeg', '.bmp', '.tiff')
        )
    except Exception as e:
        print(f"[Boundaries gallery] Error reading folder: {e}")
        return

    for p in files:
        tex = load_image_as_texture(str(p))
        if tex is None:
            continue
        STATE.gallery_proc.image_items.append({
            "path": str(p),
            "texture": tex
        })

    layout_boundaries_gallery()


def clear_boundaries_gallery_data():
    """Очистка памяти и GPU-текстур"""
    for item in STATE.gallery_proc.image_items:
        if dpg.does_item_exist(item["texture"]):
            dpg.delete_item(item["texture"])

    STATE.gallery_proc.image_items.clear()
    STATE.gallery_proc.selected_indices.clear()
    STATE.gallery_proc.last_selected = None


def layout_boundaries_gallery():
    parent_tag = TAGS.child_windows.gallery_processed
    if not dpg.does_item_exist(parent_tag):
        return

    dpg.delete_item(parent_tag, children_only=True)

    items = STATE.gallery_proc.image_items
    if not items:
        dpg.add_text("No processed images found.", parent=parent_tag)
        return

    gallery_width = dpg.get_item_width(parent_tag)
    thumb_size = STATE.constants.thumb_size
    cell_w = thumb_size + 20
    columns = max(1, gallery_width // cell_w)

    col = 0
    row_group = None

    for idx, item in enumerate(items):
        tex = item["texture"]
        selected = idx in STATE.gallery_proc.selected_indices
        tint = (200, 255, 200, 255) if selected else (255, 255, 255, 255)

        if col == 0:
            row_group = dpg.add_group(horizontal=True, parent=parent_tag)

        with dpg.group(parent=row_group):
            dpg.add_image_button(
                tex,
                tag=f"bound_img_btn_{idx}",
                tint_color=tint,
                callback=boundaries_image_click_callback,
                user_data=idx
            )
            dpg.add_text(Path(item["path"]).name, wrap=thumb_size)

        col += 1
        if col >= columns:
            col = 0


def boundaries_image_click_callback(sender, app_data, user_data):
    idx = user_data
    selected = STATE.gallery_proc.selected_indices
    last = STATE.gallery_proc.last_selected

    if dpg.is_key_down(dpg.mvKey_LControl):
        selected.symmetric_difference_update({idx})
    elif dpg.is_key_down(dpg.mvKey_LShift) and last is not None:
        for i in range(min(last, idx), max(last, idx) + 1):
            selected.add(i)
    else:
        selected.clear()
        selected.add(idx)

    STATE.gallery_proc.last_selected = idx
    layout_boundaries_gallery()


def save_boundaries_selection(sender, app_data, user_data):
    """
    Сохраняет выбранные изображения с границами
    (пути внутри images_with_boundaries)
    """
    result_set = set()
    items = STATE.gallery_proc.image_items

    for idx in STATE.gallery_proc.selected_indices:
        if 0 <= idx < len(items):
            result_set.add(items[idx]["path"])

    STATE.gallery_proc.final_boundaries_set = result_set
    print(f"[Boundaries] Saved {len(result_set)} images")
