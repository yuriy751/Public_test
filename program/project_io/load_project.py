import json
import shutil
from pathlib import Path
from zipfile import ZipFile

import cv2
import dearpygui.dearpygui as dpg
import numpy as np

from ..state import STATE
from ..tags import TAGS
from ..project_io.project_fs import ProjectFS
from ..project_io.tables_io import load_tables
from ..ui_adapters.input_fields import apply_input_fields
from ..project_io.new_project import new_project_call_back
from ..Table_processing import process_table_data
from ..Mu_s_Core_Calculations import update_mu_s_table_gui
from ..Average_intensity_calculation import update_av_int_table_gui
from ..Gallery import layout_gallery, update_boundary_texture
from ..Gallery_proc import layout_boundaries_gallery
from ..Boundaries_images_gallery import load_images_for_boundaries
from ..Mu_s_focus_imaging import load_images_mu_s


def show_open_project_dialog() -> None:
    """
    Показывает диалог открытия проекта, предварительно синхронизируя
    путь по последнему открытому проекту из settings.json.
    """
    dpg.configure_item(
        TAGS.dialogs.open_project,
        default_path=str(STATE.settings.last_open_folder),
        show=True
    )


def _load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _apply_state(obj, data: dict) -> None:
    if not data:
        return
    for key, value in data.items():
        if hasattr(obj, key):
            setattr(obj, key, value)


def _apply_project_state(data: dict) -> None:
    """
    Аккуратно восстанавливает project_state без потери активного ProjectFS.
    """
    if not data:
        return

    # fs не перезаписываем из JSON-словаря: актуальный fs уже инициализирован
    # после распаковки и должен остаться объектом ProjectFS.
    if "modified" in data:
        STATE.project.modified = bool(data["modified"])


def _restore_image_bundle(folder: Path) -> None:
    bundle = folder / "images_bundle.npz"
    if not bundle.exists():
        return

    data = np.load(bundle, allow_pickle=True)
    names = data.get("names", [])
    images = data.get("images", [])

    for name, arr in zip(names, images):
        img_name = str(name)
        img_array = arr

        # np.savez с object-массивами может вернуть вложенные object-структуры.
        # Аккуратно разворачиваем до валидного ndarray для OpenCV.
        if isinstance(img_array, np.ndarray) and img_array.dtype == object:
            if img_array.shape == ():
                img_array = img_array.item()
            else:
                img_array = np.asarray(img_array.tolist())

        img_array = np.asarray(img_array)

        if img_array.dtype == object:
            print(f"[OPEN][WARN] Skip '{img_name}': unsupported object dtype after restore.")
            continue

        try:
            cv2.imwrite(str(folder / img_name), img_array)
        except Exception as e:
            print(f"[OPEN][WARN] Failed to restore '{img_name}': {e}")


def open_project(sender, app_data, user_data) -> None:
    if not app_data:
        return

    selected_path = Path(app_data["file_path_name"])
    project_dir = selected_path.parent
    extract_dir = project_dir / "__opened_project__"

    if extract_dir.exists():
        shutil.rmtree(extract_dir)
    extract_dir.mkdir(parents=True, exist_ok=True)

    new_project_call_back()

    with ZipFile(selected_path, "r") as zipf:
        zipf.extractall(extract_dir)

    STATE.project.fs = ProjectFS(root=extract_dir, octp_file=selected_path.name)
    STATE.project.fs.ensure_structure()

    for folder_fn in (
        STATE.project.fs.main_images,
        STATE.project.fs.images_for_processing,
        STATE.project.fs.images_with_boundaries,
        STATE.project.fs.mu_s_images,
    ):
        _restore_image_bundle(folder_fn())

    apply_input_fields(_load_json(STATE.project.fs.inputs()))

    _apply_state(STATE.gallery, _load_json(STATE.project.fs.gallery_state()))
    _apply_state(STATE.gallery_proc, _load_json(STATE.project.fs.gallery_proc_state()))
    _apply_state(STATE.a_scan, _load_json(STATE.project.fs.a_scan_state()))
    _apply_state(STATE.mu_s, _load_json(STATE.project.fs.mu_s_state()))
    _apply_state(STATE.boundaries, _load_json(STATE.project.fs.boundaries_state()))
    _apply_state(STATE.constants, _load_json(STATE.project.fs.constants_state()))
    _apply_project_state(_load_json(STATE.project.fs.project_state()))
    _apply_state(STATE.time, _load_json(STATE.project.fs.time_state()))
    _apply_state(STATE.average_intensity, _load_json(STATE.project.fs.average_intensity_state()))

    widget_state = _load_json(STATE.project.fs.root / "widget_state.json")
    for tag, enabled in widget_state.get("buttons", {}).items():
        if dpg.does_item_exist(tag):
            dpg.enable_item(tag) if enabled else dpg.disable_item(tag)
    for tag, value in widget_state.get("checkboxes", {}).items():
        if dpg.does_item_exist(tag):
            dpg.set_value(tag, value)
    for tag, value in widget_state.get("sliders", {}).items():
        if dpg.does_item_exist(tag):
            dpg.set_value(tag, value)

    STATE.tables = load_tables(STATE.project.fs.root)
    process_table_data()
    update_mu_s_table_gui()
    update_av_int_table_gui()

    update_boundary_texture()
    layout_gallery()
    layout_boundaries_gallery()
    load_images_for_boundaries()
    load_images_mu_s()

    STATE.settings.last_open_folder = str(project_dir)
    STATE.settings.save()
    dpg.configure_item(
        TAGS.dialogs.open_project,
        default_path=str(STATE.settings.last_open_folder),
        show=False
    )
