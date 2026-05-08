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
from ..tags.validation import (
    REQUIRED_TAGS_FOR_NEW_PROJECT_FLOW,
    validate_required_tags,
)


def _set_black_drawlist_placeholder(drawlist_tag: str) -> None:
    if not dpg.does_item_exist(drawlist_tag):
        print(f"[NEW_PROJECT][WARN] Drawlist tag does not exist: {drawlist_tag}")
        return
    w = max(1, dpg.get_item_width(drawlist_tag))
    h = max(1, dpg.get_item_height(drawlist_tag))
    dpg.delete_item(drawlist_tag, children_only=True)
    dpg.draw_rectangle([0, 0], [w, h], fill=(0, 0, 0, 255), color=(0, 0, 0, 255), parent=drawlist_tag)

def _set_table_template(table_tag: str, headers: list[str]) -> None:
    """
    Создаёт шаблон таблицы (колонки + одна пустая строка),
    чтобы layout интерфейса не «прыгал» при очистке данных.
    """
    if not dpg.does_item_exist(table_tag):
        return

    dpg.delete_item(table_tag, children_only=True)
    for header in headers:
        dpg.add_table_column(label=header, parent=table_tag)

    with dpg.table_row(parent=table_tag):
        for _ in headers:
            dpg.add_text("-")


def input_fields_update():
    tags_dict = TAGS.inputs.__dict__
    default_values_dict = INPUT_DEFAULTS.__dict__
    for key, tag in tags_dict.items():
        if key in default_values_dict and dpg.does_item_exist(tag):
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
        if tag and dpg.does_item_exist(tag):
            dpg.disable_item(tag)


def tables_update():
    if STATE.tables.boundaries:
        process_table_data()  # корректно пересоберёт таблицу
    else:
        _set_table_template(
            TAGS.tables.boundaries,
            ["N", "Med Pixel Pos", "Min Pixel Pos", "Max Pixel Pos", "Med Distance", "Min Distance", "Max Distance"]
        )

    # Mu_s
    update_mu_s_table_gui()
    if not STATE.tables.mu_s:
        _set_table_template(
            TAGS.tables.mu_s,
            ["N", "mu_s 1/mm", "mu_s (std) 1/mm"]
        )

    # Average Intensity
    update_av_int_table_gui()
    if not STATE.tables.av_int:
        _set_table_template(
            TAGS.tables.av_int,
            ["N", "Av int (med), pixel value", "Av int (std), pixel value"]
        )


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

    # При «Новый проект» явно обнуляем drawlists чёрными заглушками,
    # чтобы не оставались старые кадры.
    _set_black_drawlist_placeholder(TAGS.drawlists.imaging)
    _set_black_drawlist_placeholder(TAGS.drawlists.roi)
    _set_black_drawlist_placeholder(TAGS.drawlists.boundary)


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
    missing_tags = validate_required_tags(REQUIRED_TAGS_FOR_NEW_PROJECT_FLOW)
    if missing_tags:
        print("[NEW_PROJECT][ERROR] Missing required tags:")
        for missing in missing_tags:
            print(f"  - {missing}")
        dpg.set_viewport_title('New File')
        return

    # Сбрасываем title сразу, чтобы при ранних ошибках не оставался временный/неверный заголовок.
    dpg.set_viewport_title('New File')
    state_update()
    update_roi_lines()
    input_fields_update()
    sliders_update()
    button_disabled_update()
    checkboxes_update()
    text_fields_update()
    tables_update()
    galleries_update()
    graphics_update()
    windows_update()


    dpg.hide_item(TAGS.mini_windows.new_project)
    project_modified_function_false(STATE.project, 'New File')
