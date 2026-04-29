import dearpygui.dearpygui as dpg
from ..state import STATE
from ..tags import TAGS
from ..project_io.save_project import save_project, cleanup_project_folders
from ..project_io.new_project import  new_project_call_back


def quit_():
    if STATE.project.fs.root:
        cleanup_project_folders(STATE.project.fs)
    dpg.stop_dearpygui()


def quitting_function():
    if not STATE.project.modified:
        quit_()
    dpg.configure_item(TAGS.mini_windows.close, show=True)


def save_quitting_function():
    save_project()
    if not STATE.project.modified:
        dpg.hide_item(TAGS.mini_windows.close)
        quit_()


def help_function():
    print("Help function called!")


def new_project_function():
    if not STATE.project.modified:
        new_project_call_back()
        print('New project')
        return
    dpg.configure_item(TAGS.mini_windows.new_project, show=True)


def save_new_project_function():
    save_project()
    if not STATE.project.modified:
        dpg.hide_item(TAGS.mini_windows.new_project)
        new_project_call_back()
        # print('New project')


def view_boundaries_window_function():
    if dpg.is_item_shown(TAGS.windows.boundaries_sep):
        dpg.hide_item(TAGS.windows.boundaries_sep)
    else:
        dpg.show_item(TAGS.windows.boundaries_sep)
    dpg.render_dearpygui_frame()


# --- Shortcuts ---
def on_key_q(sender, app_data):
    if dpg.is_key_down(dpg.mvKey_LControl) and dpg.is_key_down(dpg.mvKey_Q):
        quitting_function()


def on_key_s(sender, app_data):
    if dpg.is_key_down(dpg.mvKey_LControl) and dpg.is_key_down(dpg.mvKey_S):
        save_project()


def on_key_o(sender, app_data):
    if dpg.is_key_down(dpg.mvKey_LControl) and dpg.is_key_down(dpg.mvKey_O):
        print('on_key_o is called')
        # open_project()


def on_key_n(sender, app_data):
    if dpg.is_key_down(dpg.mvKey_LControl) and dpg.is_key_down(dpg.mvKey_N):
        new_project_function()
