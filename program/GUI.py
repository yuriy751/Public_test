import dearpygui.dearpygui as dpg

from .tags import TAGS
from .state import STATE
from .widgets import *
from .widgets import tabs
from .widgets.parameters_window.parameters_window import parameters_window_func
from .interface_functions.resize import resize_gui


def gui():
    dpg.create_context()
    dpg.create_viewport(title='New File', min_width=1700, min_height=930, resizable=True, width=1700, height=950,
                        disable_close=False
                        )
    dpg.set_viewport_resize_callback(callback=resize_gui)

    # --- Disable theme ---
    with dpg.theme() as disabled_theme:
        with dpg.theme_component(dpg.mvInputFloat, enabled_state=False):
            dpg.add_theme_color(dpg.mvThemeCol_Text, [200, 200, 200])
            dpg.add_theme_color(dpg.mvThemeCol_Button, [100, 100, 100])

        with dpg.theme_component(dpg.mvInputInt, enabled_state=False):
            dpg.add_theme_color(dpg.mvThemeCol_Text, [200, 200, 200])
            dpg.add_theme_color(dpg.mvThemeCol_Button, [100, 100, 100])

        with dpg.theme_component(dpg.mvButton, enabled_state=False):
            dpg.add_theme_color(dpg.mvThemeCol_Text, [200, 200, 200])
            dpg.add_theme_color(dpg.mvThemeCol_Button, [100, 100, 100])

    dpg.bind_theme(disabled_theme)

    texture_creation()

    # --- File dialogs ---
    last_processing_folder()
    last_save_project_folder()
    last_open_folder()
    last_save_folder_for_files()
    last_save_folder_for_images()

    # --- Asking windows ---
    new_project_window()
    close_window()
    open_project_window()

    # --- Menu bar ---
    menu_bar_func()

    with dpg.window(tag=TAGS.windows.main,
                    pos=(0, STATE.constants.const_1),
                    no_close=True, no_collapse=True, no_move=True, no_resize=True, no_title_bar=True, no_scrollbar=True,
                    no_scroll_with_mouse=True,
                    height=dpg.get_viewport_height() - STATE.constants.const_1,
                    width=dpg.get_viewport_width()-40):
        STATE.scale.window_scale = dpg.get_item_width(TAGS.windows.main) / dpg.get_viewport_width()
        parameters_window_func()

        with dpg.tab_bar():

            # --- ROI tab ---
            tabs.roi_tab_func()

            # --- Boundary calculation ---
            tabs.boundary_tab_func()

            # --- Mu_s calculation ---
            tabs.mu_s_tab_func()

            # --- Average intensity calculation ---
            tabs.average_tab_func()

            # --- Graphs drawing ---
            tabs.graph_tab_func()

            # --- Save CSV ---
            tabs.save_tab_func()

            # --- Processing photos ---
            tabs.processing_tab_func()

            # --- Processed photos ---
            tabs.processed_tab_func()

    # --- Run ---
    dpg.show_viewport()
    dpg.setup_dearpygui()
    dpg.start_dearpygui()
    dpg.destroy_context()
