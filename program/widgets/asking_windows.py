import dearpygui.dearpygui as dpg
from ..tags import TAGS
from ..interface_functions.buttons_callbacks import quit_, save_quitting_function, save_new_project_function
from ..project_io.new_project import new_project_call_back


def new_project_window():
    with dpg.window(label='New project', modal=False, width=450, height=150, no_resize=True,
                    tag=TAGS.mini_windows.new_project,
                    show=False, pos=(dpg.get_viewport_width() // 2, dpg.get_viewport_height() // 2)):
        dpg.add_text('Save your project', pos=(170, 60))
        with dpg.group(horizontal=True):
            dpg.add_button(label='Save', width=136, pos=(0, 100), callback=save_new_project_function
                           )
            dpg.add_button(label='New project', width=136, pos=(136 + 20, 100),
                           callback=new_project_call_back)

            dpg.add_button(label='Cancel', width=136, pos=(2 * 136 + 40, 100),
                           callback=lambda: dpg.hide_item(TAGS.mini_windows.new_project))


def close_window():
    with dpg.window(label='Close', modal=False, width=450, height=150, no_resize=True,
                    tag=TAGS.mini_windows.close, show=False,
                    pos=(dpg.get_viewport_width() // 2, dpg.get_viewport_height() // 2)):
        dpg.add_text('Save your project', pos=(170, 60))
        with dpg.group(horizontal=True):
            # Используем теги Save-quit, Quit-quit, Cancel-quit для логики закрытия
            dpg.add_button(label='Save', width=136, pos=(0, 100),
                           tag=TAGS.buttons.save_quit,
                           callback=save_quitting_function)
            dpg.add_button(label='Quit', width=136, pos=(136 + 20, 100),
                           tag=TAGS.buttons.quit_quit,
                           callback=quit_)
            dpg.add_button(label='Cancel', width=136, pos=(2 * 136 + 40, 100),
                           tag=TAGS.buttons.cancel_quit,
                           callback=lambda: dpg.hide_item(TAGS.mini_windows.close))


def open_project_window():
    pass