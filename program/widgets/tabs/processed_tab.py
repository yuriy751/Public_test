import dearpygui.dearpygui as dpg
from ...state import STATE
from ...tags import TAGS
from ...Gallery_proc import save_boundaries_selection


def processed_tab_func():
    with dpg.tab(label='Processed photos', tag=TAGS.tabs.processed_photos):
        dpg.add_button(label='Images to process', callback=save_boundaries_selection)
        with dpg.child_window(tag=TAGS.child_windows.gallery_processed,
                              width=dpg.get_item_width(TAGS.windows.main) - STATE.constants.const_2,
                              height=dpg.get_item_height(TAGS.windows.main) - STATE.constants.const_2,
                              autosize_y=False
                              ):
            pass