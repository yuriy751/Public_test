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
from ..project_io.new_project import (
    state_update,
    input_fields_update,
    sliders_update,
    button_disabled_update,
    checkboxes_update,
    text_fields_update,
    tables_update,
    galleries_update,
    graphics_update,
    windows_update,
)
from ..Table_processing import process_table_data
from ..Mu_s_Core_Calculations import update_mu_s_table_gui
from ..Average_intensity_calculation import update_av_int_table_gui
from ..Gallery import layout_gallery, update_boundary_texture
from ..Gallery_proc import layout_boundaries_gallery
from ..Boundaries_images_gallery import load_images_for_boundaries
from ..Mu_s_focus_imaging import load_images_mu_s
from ..interface_functions.resize import resize_gui
from ..state.Global_paths_changing import project_modified_function_false


def _get_existing_drawlist_tags(*names: str) -> tuple[str, ...]:
    """
    Безопасно получает drawlist-теги по именам атрибутов.
    Пропускает отсутствующие атрибуты и пишет предупреждение в лог.
    """
    tags: list[str] = []
    for name in names:
        tag = getattr(TAGS.drawlists, name, None)
        if tag:
            tags.append(tag)
        else:
            print(f"[OPEN][WARN] Drawlist tag attribute is missing: TAGS.drawlists.{name}")
    return tuple(tags)


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


def _restore_set_fields(obj, field_names: tuple[str, ...]) -> None:
    """
    После JSON-десериализации возвращает list -> set
    для полей, которые в runtime должны быть set.
    """
    for name in field_names:
        if not hasattr(obj, name):
            continue
        value = getattr(obj, name)
        if isinstance(value, list):
            setattr(obj, name, set(value))


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


def _normalize_image_items_paths(image_items: list, base_folder: Path) -> None:
    """
    Нормализует пути в image_items после загрузки проекта:
    старые абсолютные пути из другой машины/папки заменяются на
    пути внутри распакованного проекта.
    """
    if not isinstance(image_items, list):
        return

    for item in image_items:
        if not isinstance(item, dict):
            continue
        raw_path = item.get("path")
        if not raw_path:
            continue

        filename = Path(str(raw_path)).name
        if not filename:
            continue

        candidate = base_folder / filename
        item["path"] = str(candidate)


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


def _safe_drawlist_cleanup() -> None:
    known_drawlists = _get_existing_drawlist_tags("boundary", "roi", "mu_s", "mu_s_images")
    missing_tags: list[str] = []

    for tag in known_drawlists:
        if not dpg.does_item_exist(tag):
            missing_tags.append(tag)
            continue
        try:
            dpg.delete_item(tag, children_only=True)
        except Exception as e:
            print(f"[OPEN][WARN] Drawlist cleanup warning for '{tag}': {e}")

    if missing_tags:
        print(f"[OPEN][WARN] Drawlist tags not found during recovery: {missing_tags}")


def _recover_ui_after_open_error(selected_path: Path, open_error: Exception) -> None:
    print(f"[OPEN][ERROR] Failed to open project '{selected_path}': {open_error}")

    recovery_steps = (
        ("state reset", state_update),
        ("input controls reset", lambda: (
            input_fields_update(),
            sliders_update(),
            button_disabled_update(),
            checkboxes_update(),
            text_fields_update(),
        )),
        ("tables reset", tables_update),
        ("galleries reset", galleries_update),
        ("drawlists cleanup", _safe_drawlist_cleanup),
        ("draw/plot reset", graphics_update),
        ("windows reset", windows_update),
        ("project flags reset", lambda: (
            dpg.set_viewport_title("New File"),
            project_modified_function_false(STATE.project, "New File"),
        )),
    )

    recovery_errors: list[str] = []
    for step_name, step_fn in recovery_steps:
        try:
            step_fn()
        except Exception as e:
            recovery_errors.append(f"{step_name}: {e}")

    if recovery_errors:
        print("[OPEN][ERROR] Recovery encountered errors:")
        for error_text in recovery_errors:
            print(f"[OPEN][ERROR]   - {error_text}")


def open_project(sender, app_data, user_data) -> None:
    if not app_data:
        return

    selected_path = Path(app_data["file_path_name"])
    project_dir = selected_path.parent
    extract_dir = project_dir / "__opened_project__"
    try:
        if extract_dir.exists():
            shutil.rmtree(extract_dir)
        extract_dir.mkdir(parents=True, exist_ok=True)

        # Предварительно очищаем рабочее состояние перед загрузкой архива.
        # Здесь ожидается "чистый" путь без деградации.
        state_update()
        input_fields_update()
        sliders_update()
        button_disabled_update()
        checkboxes_update()
        text_fields_update()
        tables_update()
        galleries_update()
        graphics_update()
        windows_update()
        dpg.set_viewport_title("New File")
        project_modified_function_false(STATE.project, "New File")

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
        _restore_set_fields(STATE.gallery, ("selected_indices",))
        _restore_set_fields(STATE.gallery_proc, ("selected_indices", "final_boundaries_set"))
        _normalize_image_items_paths(STATE.gallery.image_items, STATE.project.fs.images_for_processing())
        _normalize_image_items_paths(STATE.gallery_proc.image_items, STATE.project.fs.images_with_boundaries())
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
        resize_gui()

        STATE.settings.last_open_folder = str(project_dir)
        STATE.settings.save()
        dpg.configure_item(
            TAGS.dialogs.open_project,
            default_path=str(STATE.settings.last_open_folder),
            show=False
        )

        # Заголовок окна должен соответствовать открытому файлу проекта.
        dpg.set_viewport_title(selected_path.name)
    except Exception as e:
        _recover_ui_after_open_error(selected_path, e)
