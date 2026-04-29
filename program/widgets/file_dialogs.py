import dearpygui.dearpygui as dpg
from ..tags import TAGS
from ..state import STATE
from ..Gallery import on_images_selected
from ..project_io.save_project import save_project_folder_as
from ..project_io.save_files.save_files import save_selected_tables
from ..project_io.save_images.save_images import save_images_to_folder


# --- File dialogs ---
def last_processing_folder():
    with dpg.file_dialog(directory_selector=False, show=False,
                         callback=on_images_selected, file_count=0,
                         tag=TAGS.dialogs.choose_images, modal=False, width=600, height=400,
                         default_path=STATE.settings.last_processing_folder):
        dpg.add_file_extension(".png")
        dpg.add_file_extension(".bmp")


def last_save_project_folder():
    with dpg.file_dialog(directory_selector=False, show=False, file_count=1,
                         tag=TAGS.dialogs.save_project, modal=False,
                         width=600, height=400, default_path=STATE.settings.last_save_project_folder,
                         callback=save_project_folder_as
                         ):
        dpg.add_file_extension(".octp")


def last_open_folder():
    with dpg.file_dialog(directory_selector=False, show=False,
                         # callback=open_project,
                         tag=TAGS.dialogs.open_project,
                         modal=False, width=600, height=400,
                         default_path=STATE.settings.last_open_folder):
        dpg.add_file_extension(".octp")


def last_save_folder_for_files():
    with dpg.file_dialog(directory_selector=True, show=False, tag=TAGS.dialogs.save_files_to_project, modal=True,
                         default_path=STATE.settings.last_save_folder_for_files, callback=save_selected_tables,
                         width=600, height=400):
        pass


def last_save_folder_for_images():
    with dpg.file_dialog(directory_selector=True, show=False, tag=TAGS.dialogs.save_images_to_project, modal=True,
                         default_path=STATE.settings.last_save_folder_for_images, callback=save_images_to_folder,
                         width=600, height=400):
        pass