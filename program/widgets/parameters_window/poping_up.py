import dearpygui.dearpygui as dpg
import time
from ...tags import TAGS
from ...state import STATE
from ...interface_functions.other_callbacks import project_modified_function_true_modified
from ...interface_functions.resize import resize_gui
from ...Mu_s_focus_imaging import show_mu_s_image_by_index


def update_panel():
    if STATE.param_window.visible:
        STATE.param_window.visible = False
        dpg.configure_item(TAGS.buttons.popup_param_window, label="+")
        new_position = int(dpg.get_viewport_width() - 2.5 * STATE.constants.const_1)
        new_width = dpg.get_item_width(TAGS.windows.main) + dpg.get_item_width(TAGS.windows.parameter)
        dif = abs(new_position - dpg.get_item_pos(TAGS.windows.parameter)[0])
        dif_w = abs(dpg.get_item_width(TAGS.windows.main)-new_width)
        while dif > 0 or dif_w > 0:
            dif = dif - STATE.param_window.speed
            dif_w = dif_w - STATE.param_window.speed
            if dif_w > 0:
                dpg.configure_item(TAGS.windows.main, width=dpg.get_item_width(TAGS.windows.main)+STATE.param_window.speed)
            else:
                dpg.configure_item(TAGS.windows.main, width=new_width)
            if dif > 0:
                dpg.configure_item(TAGS.windows.parameter, pos=(new_position - dif, 2.5 * STATE.constants.const_1))
            else:
                dpg.configure_item(TAGS.windows.parameter, pos=(new_position, 2.5 * STATE.constants.const_1))
            time.sleep(STATE.param_window.sleep_time)
            STATE.scale.window_scale = dpg.get_item_width(TAGS.windows.main) / dpg.get_viewport_width()
            resize_gui()
    else:
        STATE.param_window.visible = True
        dpg.configure_item(TAGS.buttons.popup_param_window, label="-")
        new_position = dpg.get_viewport_width() - dpg.get_item_width(TAGS.windows.parameter)
        new_width = dpg.get_item_width(TAGS.windows.main) - dpg.get_item_width(TAGS.windows.parameter)
        dif = abs(new_position - dpg.get_item_pos(TAGS.windows.parameter)[0])
        dif_w = abs(dpg.get_item_width(TAGS.windows.main) - new_width)
        while dif > 0 or dif_w > 0:
            dif = dif - STATE.param_window.speed
            dif_w = dif_w - STATE.param_window.speed
            if dif_w > 0:
                dpg.configure_item(TAGS.windows.main, width=dpg.get_item_width(TAGS.windows.main)-STATE.param_window.speed)
            else:
                dpg.configure_item(TAGS.windows.main, width=new_width)
            if dif > 0:
                dpg.configure_item(TAGS.windows.parameter, pos=(new_position+dif, 2.5*STATE.constants.const_1))
            else:
                dpg.configure_item(TAGS.windows.parameter, pos=(new_position, 2.5 * STATE.constants.const_1))
            time.sleep(STATE.param_window.sleep_time)
            STATE.scale.window_scale = dpg.get_item_width(TAGS.windows.main) / dpg.get_viewport_width()
            resize_gui()
    show_mu_s_image_by_index(STATE.mu_s.current_index)

    project_modified_function_true_modified()
