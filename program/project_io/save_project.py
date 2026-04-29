# project_io/save_project.py

import json
import shutil
from pathlib import Path
from zipfile import ZipFile

import dearpygui.dearpygui as dpg
import numpy as np
import cv2

from ..state import STATE
from ..project_io.project_fs import ProjectFS
from ..tags import TAGS
from ..state.Global_paths_changing import project_modified_function_false
from ..ui_adapters.input_fields import collect_input_fields
from .tables_io import save_tables


# ======================================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ======================================================

def normalize_dict_for_json(src: dict) -> dict:
    """
    Приводит dict к JSON-совместимому виду.

    Правила:
    - Path -> str
    - set -> list
    - np.ndarray -> пропускается
    - list[np.ndarray] не трогаем
    """
    out = {}

    for key, value in src.items():

        # --- ProjectFS ---
        if isinstance(value, ProjectFS):
            out[key] = value.to_dict()
            continue

        # np.ndarray полностью игнорируем
        if isinstance(value, np.ndarray):
            continue

        # Path -> str
        if isinstance(value, Path):
            out[key] = str(value)
            continue

        # set -> list
        if isinstance(value, set):
            out[key] = list(value)
            continue

        # list[...] не трогаем
        if isinstance(value, list):
            out[key] = value
            continue

        # всё остальное
        out[key] = value

    return out


def collect_widgets_state() -> dict:
    widgets_state = {}
    buttons = {}
    for tag in TAGS.buttons.__dict__.values():
        if dpg.does_item_exist(tag):
            buttons[tag] = dpg.is_item_enabled(tag)

    checkboxes = {}
    for tag in TAGS.checkboxes.__dict__.values():
        checkboxes[tag] = dpg.get_value(tag)

    sliders = {}
    for tag in TAGS.sliders.__dict__.values():
        sliders[tag] = dpg.get_value(tag)

    widgets_state['buttons'] = buttons
    widgets_state['checkboxes'] = checkboxes
    widgets_state['sliders'] = sliders
    return widgets_state


def cleanup_project_folders(project_fs: ProjectFS) -> None:
    """
    Удаляет рабочие папки проекта после успешного сохранения.
    """
    for folder_fn in (
        project_fs.main_images,
        project_fs.images_for_processing,
        project_fs.images_with_boundaries,
        project_fs.mu_s_images,
    ):
        path = folder_fn()
        if path.exists():
            shutil.rmtree(path)


def save_images_as_npz(src: Path, dst: Path) -> None:
    """
    Конвертирует изображения из папки src в .npz и сохраняет в dst.
    """
    if not src.exists():
        return

    dst.mkdir(parents=True, exist_ok=True)

    for img_path in src.iterdir():
        if not img_path.is_file():
            continue

        try:
            arr = load_image_as_array(img_path)
        except Exception as e:
            print(f"[SAVE][WARN] Failed to load {img_path.name}: {e}")
            continue

        np.savez_compressed(
            dst / img_path.with_suffix(".npz").name,
            image=arr,
            dtype=str(arr.dtype),
            shape=arr.shape,
        )



def load_image_as_array(path: Path) -> np.ndarray:
    """
    Загружает изображение в numpy-массив без изменения битности.

    Поддержка:
    - PNG / JPG / TIFF (через OpenCV)
    - grayscale изображения (2D)

    Возвращает:
    - np.ndarray (H, W)
    """

    if not path.exists():
        raise FileNotFoundError(path)

    suffix = path.suffix.lower()

    # ---------- NPZ ----------
    if suffix == ".npz":
        data = np.load(path, allow_pickle=True)
        if "image" not in data:
            raise ValueError(f"No 'image' array in {path}")
        return data["image"]

    # ---------- IMAGE FILE ----------
    img = cv2.imread(str(path), cv2.IMREAD_UNCHANGED)

    if img is None:
        raise ValueError(f"Failed to load image: {path}")

    # RGB → grayscale (на всякий случай)
    if img.ndim == 3:
        img = img[..., 0]

    return img

# ======================================================
# SAVE CORE
# ======================================================

def save_project_as_octp(project_fs: ProjectFS) -> None:
    """
    Упаковывает рабочую папку проекта в .octp архив.
    """

    if project_fs.root is None or project_fs.octp_file is None:
        raise RuntimeError("ProjectFS is not initialized")

    archive_path = (project_fs.root / project_fs.octp_file).with_suffix(".octp")

    temp_dir = project_fs.root / Path("__temp_save__")
    if temp_dir.exists():
        shutil.rmtree(temp_dir)
    temp_dir.mkdir()
    inputs = collect_input_fields()
    for tag in [TAGS.buttons.image_upload, TAGS.buttons.images_delete, TAGS.buttons.images_process]:
        if dpg.does_item_exist(tag):
            dpg.enable_item(tag)
    # ---------- JSON ----------
    json_map = {
        "inputs.json":inputs,
        "gallery_state.json": STATE.gallery.__dict__,
        "gallery_proc_state.json": STATE.gallery_proc.__dict__,
        "a_scan_state.json": STATE.a_scan.__dict__,
        "mu_s_state.json": STATE.mu_s.__dict__,
        "boundaries_state.json": STATE.boundaries.__dict__,
        "constants_state.json": STATE.constants.__dict__,
        "project_state.json": STATE.project.__dict__,
        "time_state.json": STATE.time.__dict__,
        "average_intensity_state.json": STATE.average_intensity.__dict__,
        "widget_state.json": collect_widgets_state(),
    }

    for name, obj in json_map.items():
        path = temp_dir / name

        print(name)
        print('\t', obj)

        with path.open("w", encoding="utf-8") as f:
            json.dump(
                normalize_dict_for_json(obj),
                f,
                indent=2,
                ensure_ascii=False
            )

    save_tables(STATE.tables, temp_dir)

    # ---------- folders ----------
    image_folders = (
        project_fs.main_images,
        project_fs.images_for_processing,
        project_fs.images_with_boundaries,
        project_fs.mu_s_images,
    )

    for folder_fn in image_folders:
        src = folder_fn()
        dst = temp_dir / src.name
        save_images_as_npz(src, dst)
    print(f'Inside of folders \n{STATE.project.fs.images_for_processing()}:\n\t'
          f'{STATE.project.fs.list_images_for_processing()}\n'
          f'{STATE.project.fs.main_images()}:\n\t{STATE.project.fs.list_main_images()}\n'
          f'{STATE.project.fs.images_with_boundaries()}:\n\t{STATE.project.fs.list_images_with_boundaries()}\n'
          f'{STATE.project.fs.mu_s_images()}:\n\t{STATE.project.fs.list_mu_s_images()}\n')
    # ---------- zip ----------
    with ZipFile(archive_path, "w") as zipf:
        for file in temp_dir.rglob("*"):
            zipf.write(file, arcname=file.relative_to(temp_dir))

    shutil.rmtree(temp_dir)



# ======================================================
# SAVE / SAVE AS
# ======================================================

def save_project() -> None:
    project_fs = STATE.project.fs

    if project_fs and project_fs.octp_file:
        save_project_as_octp(project_fs)
        project_modified_function_false(STATE.project)
    else:
        dpg.configure_item(TAGS.dialogs.save_project, show=True)


def _do_save_project(project_dir: Path, file_name: str) -> None:
    """
    Фактическое сохранение проекта (используется и для обычного Save As,
    и для подтверждённой перезаписи).
    """

    STATE.project.fs = ProjectFS(
        root=project_dir,
        octp_file=file_name
    )

    STATE.project.fs.ensure_structure()
    save_project_as_octp(STATE.project.fs)

    STATE.settings.last_save_project_folder = str(project_dir)
    STATE.settings.save()

    dpg.configure_item(
        TAGS.dialogs.save_project,
        default_path=STATE.settings.last_save_project_folder
    )

    project_modified_function_false(
        STATE.project,
        STATE.project.fs.octp_file
    )


def _confirm_rewrite(sender, app_data, user_data):
    """
    user_data = (project_dir, file_name, dialog_tag)
    """
    project_dir, file_name, dialog_tag = user_data

    _do_save_project(project_dir, file_name)

    # закрываем confirmation window
    dpg.delete_item(dialog_tag)

    # закрываем Save As диалог
    dpg.configure_item(TAGS.dialogs.save_project, show=False)


def save_project_folder_as(sender, app_data, user_data) -> None:
    if not app_data:
        return

    project_dir = Path(app_data["current_path"])
    file_name = app_data["file_name"]
    full_path = project_dir / Path(file_name)

    # ------------------------------
    # файл уже существует → спросить
    # ------------------------------
    if full_path.exists():
        tag = TAGS.mini_windows.rewrite_proj_conf

        if dpg.does_item_exist(tag):
            dpg.delete_item(tag)

        with dpg.window(
            modal=True,
            no_move=True,
            no_resize=True,
            width=420,
            height=160,
            label="Rewrite the project?",
            tag=tag,
            pos=(
                dpg.get_viewport_width() // 2 - 210,
                dpg.get_viewport_height() // 2 - 80,
            ),
        ):
            dpg.add_text(
                f"The file '{file_name}' already exists.\n\n"
                f"Do you want to overwrite it?"
            )

            dpg.add_spacer(height=10)

            with dpg.group(horizontal=True):
                dpg.add_button(
                    label="Yes",
                    width=120,
                    callback=_confirm_rewrite,
                    user_data=(project_dir, file_name, tag),
                )
                dpg.add_button(
                    label="No",
                    width=120,
                    callback=lambda: dpg.delete_item(tag),
                )

        return

    # ------------------------------
    # файл не существует → Save As
    # ------------------------------
    _do_save_project(project_dir, file_name)

    dpg.configure_item(sender, show=False)
