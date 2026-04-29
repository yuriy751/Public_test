# new_project.py

import dearpygui.dearpygui as dpg
from ..tags import TAGS
from ..state import STATE
from ..state.user_setteing_state import UserSettingsState
from ..project_io.save_project import cleanup_project_folders
from ..ui_adapters.input_defaults import INPUT_DEFAULTS
from ..ROI import update_roi_lines
from ..Gallery import layout_gallery, update_boundary_texture
from ..Gallery_proc import layout_boundaries_gallery
from ..state.Global_paths_changing import project_modified_function_false
from ..Table_processing import process_table_data
from ..Mu_s_Core_Calculations import update_mu_s_table_gui
from ..Average_intensity_calculation import update_av_int_table_gui
from ..Boundaries_images_gallery import load_images_for_boundaries
from ..Mu_s_focus_imaging import clear_dynamic_texture, load_images_mu_s


def input_fields_update():
    tags_dict = TAGS.inputs.__dict__
    default_values_dict = INPUT_DEFAULTS.__dict__
    for key, tag in tags_dict.items():
        if default_values_dict.get(key) and dpg.does_item_exist(tag):
            dpg.set_value(tag, default_values_dict[key])


def sliders_update():
    tags_dict = TAGS.sliders.__dict__
    for tag in tags_dict.values():
        if dpg.does_item_exist(tag):
            dpg.set_value(tag, 0)



def button_disabled_update():
    tags_dict = (TAGS.buttons.process, TAGS.buttons.viewing_photos, TAGS.buttons.parameter_processing,
                 TAGS.buttons.images_process, TAGS.buttons.image_upload, TAGS.buttons.images_delete,
                 TAGS.buttons.plot_processing, TAGS.buttons.show_boundary_image)
    for tag in tags_dict:
        dpg.disable_item(tag)


def tables_update():
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


def state_update():
    if STATE.project.fs.root:
        cleanup_project_folders(STATE.project.fs)
    STATE.reset()
    STATE.settings = UserSettingsState.load()


def galleries_update():
    update_boundary_texture()
    layout_gallery()
    layout_boundaries_gallery()
    load_images_for_boundaries()
    clear_dynamic_texture(TAGS.textures.mu_s,
                          dpg.get_item_width(TAGS.textures.mu_s),
                          dpg.get_item_height(TAGS.textures.mu_s))
    load_images_mu_s()


def graphics_update():
    for tag in TAGS.series_scatter.__dict__.values():
        if dpg.does_item_exist(tag):
            dpg.set_value(tag, [[], []])
    for tag in TAGS.series_line.__dict__.values():
        if dpg.does_item_exist(tag):
            dpg.set_value(tag, [[], []])
    pass


def windows_update():
    dpg.hide_item(TAGS.windows.boundaries_sep)
    tags = (TAGS.mini_windows.time, TAGS.windows.mu_s_images)
    for tag in tags:
        if dpg.does_item_exist(tag):
            dpg.delete_item(tag)


def checkboxes_update():
    for tag in TAGS.checkboxes.__dict__.values():
        if dpg.does_item_exist(tag):
            if tag == TAGS.checkboxes.low_boundary:
                dpg.set_value(tag, True)
            else:
                dpg.set_value(tag, False)


def text_fields_update():
    for tag in TAGS.text_fields.__dict__.values():
        if dpg.does_item_exist(tag):
            dpg.set_value(tag, '')


def new_project_call_back():
    update_roi_lines()
    input_fields_update()
    sliders_update()
    button_disabled_update()
    checkboxes_update()
    text_fields_update()
    tables_update()
    state_update()
    galleries_update()
    graphics_update()
    windows_update()


    dpg.hide_item(TAGS.mini_windows.new_project)
    project_modified_function_false(STATE.project, 'New File')
