import dearpygui.dearpygui as dpg
import os
import shutil
from pathlib import Path

from ...tags import TAGS
from ...state import STATE


def save_image_dialog_show():
    if (dpg.get_value(TAGS.checkboxes.images_default) or
            dpg.get_value(TAGS.checkboxes.images_boundarise) or
            dpg.get_value(TAGS.checkboxes.images_mu_s)):
        dpg.show_item(TAGS.dialogs.save_images_to_project)
    else:
        return


def save_images_to_folder(sender, app_data):
    # Путь, выбранный в диалоге
    target_root = app_data["file_path_name"]

    dirs_to_check = [
        STATE.project.fs.images_for_processing(),
        STATE.project.fs.images_with_boundaries(),
        STATE.project.fs.mu_s_images(),
    ]

    checkboxes_to_check = [
        TAGS.checkboxes.images_default,
        TAGS.checkboxes.images_boundarise,
        TAGS.checkboxes.images_mu_s,
    ]

    for src_dir, checkbox in zip(dirs_to_check, checkboxes_to_check):
        if not dpg.get_value(checkbox):
            continue

        if not os.path.exists(src_dir):
            continue

        # Имя папки (например "images_for_processing")
        folder_name = os.path.basename(src_dir)

        # Куда копируем
        dst_dir = os.path.join(target_root, str(Path(STATE.project.fs.octp_file).stem)+ '_' + folder_name)
        os.makedirs(dst_dir, exist_ok=True)

        # Копируем только изображения
        for file_name in os.listdir(src_dir):
            src_file = os.path.join(src_dir, file_name)

            if not os.path.isfile(src_file):
                continue

            if file_name.lower().endswith((".png", ".jpg", ".jpeg", ".tiff", ".bmp", '.txt')):
                dst_file = os.path.join(dst_dir, file_name)
                shutil.copy2(src_file, dst_file)

        STATE.settings.last_save_folder_for_images = str(target_root)
        STATE.settings.save()

        dpg.configure_item(
            TAGS.dialogs.save_images_to_project,
            default_path=STATE.settings.last_save_folder_for_images
        )

        dpg.set_value(
            TAGS.text_fields.save_images_info,
            f"\tFiles are saved in {target_root}"
        )

