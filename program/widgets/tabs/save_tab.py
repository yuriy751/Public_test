import dearpygui.dearpygui as dpg
from ...state import STATE
from ...tags import TAGS
from ...project_io.checkboxes_save import group_callback, all_callback, each_callback
from ...project_io.save_files.save_files import save_files_dialog_show
from ...project_io.save_images.save_images import save_image_dialog_show


def save_tab_func():
    with dpg.tab(label='Save files', tag=TAGS.tabs.save_files_csv):
        with dpg.child_window(
                tag=TAGS.windows.save_files,
                width=dpg.get_item_width(TAGS.windows.main),
                height=dpg.get_item_height(TAGS.windows.main) - STATE.constants.const_1,
                no_scrollbar=True,
                no_scroll_with_mouse=True,
                tracked=True
        ):
            with dpg.table(
                    header_row=False,
                    resizable=False,
                    policy=dpg.mvTable_SizingFixedFit,
                    borders_innerV=False,
                    borders_innerH=False,
                    borders_outerH=False,
                    borders_outerV=False
            ):
                # ===== columns =====
                dpg.add_table_column()
                dpg.add_table_column()
                dpg.add_table_column()
                dpg.add_table_column()
                dpg.add_table_column()
                dpg.add_table_column()

                with dpg.table_row():
                    dpg.add_checkbox(label='Save orig images',
                                     tag=TAGS.checkboxes.images_default,
                                     enabled=False)
                    dpg.add_checkbox(label='Save boundaries images',
                                     tag=TAGS.checkboxes.images_boundarise,
                                     enabled=False)
                    dpg.add_checkbox(label='Save mu_s images',
                                     tag=TAGS.checkboxes.images_mu_s,
                                     enabled=False)
                    dpg.add_text(label='')
                    dpg.add_button(label='Save images',
                                   tag=TAGS.buttons.save_images,
                                   callback=save_image_dialog_show)
                    dpg.add_text(label='',
                                 tag=TAGS.text_fields.save_images_info)
                # ===== row 2: main checkboxes =====
                with dpg.table_row():
                    dpg.add_checkbox(
                        label='Save boundaries data',
                        tag=TAGS.checkboxes.boundaries,
                        callback=group_callback,
                        enabled=False
                    )
                    dpg.add_checkbox(
                        label='Save mu_s data',
                        tag=TAGS.checkboxes.mu_s,
                        callback=group_callback,
                        enabled=False
                    )
                    dpg.add_checkbox(
                        label='Save average intensity data',
                        tag=TAGS.checkboxes.av_int,
                        callback=group_callback,
                        enabled=False
                    )
                    dpg.add_checkbox(
                        label='Save parameters data',
                        tag=TAGS.checkboxes.params,
                        enabled=False
                    )
                    dpg.add_button(label='Save files', tag=TAGS.buttons.save_files, callback=save_files_dialog_show)
                    dpg.add_text(label='', tag=TAGS.text_fields.save_files_info)

                # ===== row 3: detailed checkboxes =====
                with dpg.table_row():
                    # --- boundaries ---
                    with dpg.group(tag=TAGS.groups.boundaries, show=False):
                        dpg.add_checkbox(label='All', tag=TAGS.checkboxes.all_boundaries, callback=all_callback)
                        for field in TAGS.boundaries_checkboxes.__dict__.values():
                            dpg.add_checkbox(label=field, tag=field, callback=each_callback)

                    # --- mu_s ---
                    with dpg.group(tag=TAGS.groups.mu_s, show=False):
                        dpg.add_checkbox(label='All', tag=TAGS.checkboxes.all_mu_s, callback=all_callback)
                        for field in TAGS.mu_s_checkboxes.__dict__.values():
                            dpg.add_checkbox(label=field, tag=field, callback=each_callback)

                    # --- av_int ---
                    with dpg.group(tag=TAGS.groups.av_int, show=False):
                        dpg.add_checkbox(label='All', tag=TAGS.checkboxes.all_av_int, callback=all_callback)
                        for field in TAGS.av_int_checkboxes.__dict__.values():
                            dpg.add_checkbox(label=field, tag=field, callback=each_callback)

                    dpg.add_spacer()
                    dpg.add_spacer()