import dearpygui.dearpygui as dpg

from .tags import TAGS
from .state import STATE


def save_keys():
    keys = []
    for key in STATE.ris.__dict__.keys():
        keys.append(key)
    return keys


def save_callback():
    if STATE.ris.__dict__:
        keys_ = save_keys()
        for i in keys_:
            STATE.ris.delete_n(i)

    for i in range(dpg.get_value(TAGS.inputs.boundaries_amount)):
        STATE.ris.create_new_n(f'n_{i+1}', dpg.get_value(f'n_{i+1} tag'))
    dpg.delete_item(TAGS.mini_windows.ris)


def cancel_callback():
    dpg.delete_item(TAGS.mini_windows.ris)


def boundaries_amount_changing():
    if not dpg.get_value(TAGS.checkboxes.known_ri):
        return
    if STATE.ris.__dict__:
        keys_ = save_keys()
        for i in keys_:
            STATE.ris.delete_n(i)
    if dpg.get_value(TAGS.text_fields.sample_parameters) == '':
        dpg.set_value(TAGS.text_fields.sample_parameters, 'You have changed amount of boundaries\n'
                                                          'Fill RIs window again')


def ris_window():
    if not dpg.does_item_exist(TAGS.mini_windows.ris):
        with dpg.window(tag=TAGS.mini_windows.ris,
                        width=300,
                        height=240,
                        no_resize=True,
                        no_close=True,
                        modal=True):
            if not dpg.get_value(TAGS.checkboxes.homogenious):
                for i in range(dpg.get_value(TAGS.inputs.boundaries_amount)):
                    dpg.add_input_float(label=f'n_{i+1}', tag=f'n_{i+1} tag',
                                        format='%.2f', default_value=1.0, min_value=1.0, max_value=4.0,
                                        min_clamped=True, max_clamped=True)
            else:
                dpg.add_input_float(label=f'n_{1}', tag=f'n_{1} tag',
                                    format='%.2f', default_value=1.0, min_value=1.0, max_value=4.0,
                                    min_clamped=True, max_clamped=True)
            with dpg.group(horizontal=True, horizontal_spacing=20):
                dpg.add_button(label='Save', tag=TAGS.buttons.save_ris, callback=save_callback)
                dpg.add_button(label='Cancel', callback=cancel_callback)
    else:
        dpg.delete_item(TAGS.mini_windows.ris)