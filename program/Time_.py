# Time_.py

from .state import STATE
from .tags import TAGS
from .ui_adapters.input_defaults import INPUT_DEFAULTS
import dearpygui.dearpygui as dpg


def set_tmie_list():
    STATE.boundaries.time_list = []
    amount = dpg.get_value(TAGS.inputs.amount_of_points)
    interval = dpg.get_value(TAGS.inputs.time_interval)
    time = [0, 1]
    for i in range(amount-2):
        time.append(interval*(i+1)+1)
    STATE.time.time_list = time
    if STATE.time.time_list:
        dpg.enable_item(TAGS.buttons.parameter_processing)
    dpg.delete_item(TAGS.mini_windows.time)


def amount_of_points_callback() -> int:
    return len(STATE.tables.boundaries) if len(STATE.tables.boundaries) != 0 else INPUT_DEFAULTS.amount_of_points


def time_window():
    if not dpg.does_item_exist(TAGS.mini_windows.time):
        with dpg.window(tag=TAGS.mini_windows.time,
                        width=300, height=150):
            with dpg.group(horizontal=False):
                dpg.add_input_int(label='Time interval, min',
                                  tag=TAGS.inputs.time_interval,
                                  default_value=INPUT_DEFAULTS.time_interval,
                                  min_value= 1, min_clamped=True,
                                  width=140)
                dpg.add_input_int(label='Amount of points',
                                  tag=TAGS.inputs.amount_of_points,
                                  default_value=amount_of_points_callback(),
                                  min_value=2, min_clamped=True,
                                  width=140)
            with dpg.group(horizontal=True, horizontal_spacing=20):
                dpg.add_button(label='Ok', tag=TAGS.buttons.time_ok,
                               callback=set_tmie_list)
                dpg.add_button(label='Cancel', tag=TAGS.buttons.time_cancel,
                               callback=lambda: dpg.delete_item(TAGS.mini_windows.time))
    else:
        dpg.delete_item(TAGS.mini_windows.time)
    pass
