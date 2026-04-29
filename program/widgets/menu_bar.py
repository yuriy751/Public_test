import dearpygui.dearpygui as dpg
from ..tags import TAGS
from ..project_io.save_project import save_project
from ..interface_functions.buttons_callbacks import (
    quitting_function, help_function, on_key_q, on_key_s, on_key_o, on_key_n
)
from ..project_io.new_project import new_project_call_back


def menu_bar_func():
    with dpg.viewport_menu_bar():
        with dpg.handler_registry():
            dpg.add_key_press_handler(dpg.mvKey_F11, callback=dpg.toggle_viewport_fullscreen)
            dpg.add_key_press_handler(dpg.mvKey_F5, callback=lambda: print('Wow'))
            dpg.add_key_press_handler(dpg.mvKey_F8, callback=help_function)
            dpg.add_key_press_handler(dpg.mvKey_Q, callback=on_key_q)
            dpg.add_key_press_handler(dpg.mvKey_S, callback=on_key_s)
            # dpg.add_key_press_handler(dpg.mvKey_O, callback=on_key_o)
            dpg.add_key_press_handler(dpg.mvKey_N, callback=on_key_n)
        with dpg.menu(label='File', tag=TAGS.menus.file):
            dpg.add_menu_item(label='New Project (Ctrl + N)',
                              tag=TAGS.menu_items.new_project,
                              callback=new_project_call_back
                              )
            dpg.add_menu_item(label='Open Project (Ctrl + O)',
                              tag=TAGS.menu_items.open_project,
                              # callback=open_project
                              )
            dpg.add_menu_item(label='Save Project (Ctrl + S)',
                              tag=TAGS.menu_items.save,
                              callback=save_project
                              )
            dpg.add_menu_item(label='Save Project As',
                              tag=TAGS.menu_items.save_as,
                              callback=lambda: dpg.show_item(TAGS.dialogs.save_project))
            dpg.add_menu_item(label='Quit (Ctrl + Q)',
                              tag=TAGS.menu_items.quit,
                              callback=quitting_function
                              )
        with dpg.menu(label='Settings', tag=TAGS.menus.settings):
            dpg.add_menu_item(label='Full screen (F11)',
                              tag=TAGS.menu_items.fullscreen,
                              callback=dpg.toggle_viewport_fullscreen)
        with dpg.menu(label='Help', tag=TAGS.menus.help):
            dpg.add_menu_item(label='Help',
                              tag=TAGS.menu_items.help)
            dpg.add_menu_item(label='About...',
                              tag=TAGS.menu_items.about)