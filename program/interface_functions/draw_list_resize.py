import dearpygui.dearpygui as dpg
from ..state import STATE
from ..tags import TAGS


def draw_resize():
    if STATE.constants.original_width > 0 and \
            STATE.constants.original_height > 0:
        scale_ = float(0.6*dpg.get_item_height(TAGS.windows.main)/STATE.constants.original_height)
        # print(f'{scale_ = }')
        scale_ = max(0.01, min(scale_, 1.0))
    else:
        scale_ = 1.0

    STATE.scale.scale = scale_


def begining_resize():
    orig_w = STATE.constants.original_width
    orig_h = STATE.constants.original_height
    if orig_w > 0 and orig_h > 0:
        sw = max(1, dpg.get_item_width(
            TAGS.windows.boundaries) - STATE.constants.const_2)
        sh = max(1, 0.75 * dpg.get_item_height(
            TAGS.windows.boundaries) - STATE.constants.const_2)
        scale_init = min(sw / orig_w, sh / orig_h)
        scale_init = max(0.01, min(scale_init, 1.0))
    else:
        scale_init = 1.0

    return scale_init, orig_w, orig_h