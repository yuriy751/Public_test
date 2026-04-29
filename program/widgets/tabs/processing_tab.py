import dearpygui.dearpygui as dpg
from ...state import STATE
from ...tags import TAGS
from ...Gallery import delete_images, images_to_process


def processing_tab_func():
    with dpg.tab(label='Processing photos', tag=TAGS.tabs.processing_photos):
        with dpg.group(horizontal=True):
            dpg.add_button(label="Upload images",
                           tag=TAGS.buttons.image_upload,
                           callback=lambda: dpg.show_item(TAGS.dialogs.choose_images),
                           enabled=False)

            dpg.add_button(label='Delete images',
                           tag=TAGS.buttons.images_delete,
                           callback=delete_images,
                           enabled=False)

            dpg.add_button(label='Images to process',
                           tag=TAGS.buttons.images_process,
                           callback=images_to_process,
                           enabled=False)

        with dpg.child_window(tag=TAGS.child_windows.gallery,
                              width=dpg.get_item_width(TAGS.windows.main) - STATE.constants.const_2,
                              height=dpg.get_item_height(TAGS.windows.main) - STATE.constants.const_2,
                              autosize_y=False):
            pass