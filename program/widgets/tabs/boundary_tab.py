import dearpygui.dearpygui as dpg
from ...state import STATE
from ...tags import TAGS
from ...interface_functions.draw_list_resize import begining_resize
from ...Boundaries_images_gallery import (
    load_images_for_boundaries, show_next_image, show_prev_image, show_image_by_index
)
from ...Table_processing import process_table_data
from ...Optical_thikness_check import graphic_imaging


def boundary_tab_func():
    with dpg.tab(label='Boundaries calculation', tag=TAGS.tabs.boundaries):
        with dpg.child_window(
                tag=TAGS.windows.boundaries_sep,
                width=dpg.get_item_width(TAGS.windows.main),
                height=dpg.get_item_height(TAGS.windows.main) - STATE.constants.const_1,
                no_scrollbar=True, no_scroll_with_mouse=True):
            with dpg.group(horizontal=True):
                with dpg.group():
                    with dpg.group(horizontal=True):
                        dpg.add_text("", tag=TAGS.text_fields.image_name)

                    scale_init, orig_w, orig_h = begining_resize()

                    STATE.scale.scale = scale_init
                    # Child window for Boundary Image
                    with dpg.child_window(tag=TAGS.child_windows.boundary,
                                          width=int(orig_w * scale_init),
                                          height=int(orig_h * scale_init),
                                          no_scrollbar=True
                                          ):
                        dpg.drawlist(tag=TAGS.drawlists.boundary,
                                     width=int(orig_w * scale_init),
                                     height=int(orig_h * scale_init))

                    with dpg.group(horizontal=True):
                        dpg.add_button(label="Load images", callback=load_images_for_boundaries, width=140)
                        dpg.add_button(label="Show", tag=TAGS.buttons.show_boundary_image,
                                       callback=lambda: show_image_by_index(STATE.boundaries.current_index),
                                       width=140, enabled=len(STATE.boundaries.images) > 0)
                        dpg.add_button(label="Prev", callback=show_prev_image, width=140)
                        dpg.add_button(label="Next", callback=show_next_image, width=140)
                        dpg.add_button(label="Refresh",
                                       callback=lambda: show_image_by_index(STATE.boundaries.current_index),
                                       width=140)
                with dpg.group():
                    dpg.add_text("", tag=TAGS.text_fields.table_counts)
                    with dpg.table(tag=TAGS.tables.boundaries,
                                   width=dpg.get_item_width(TAGS.windows.main) - dpg.get_item_width(
                                       TAGS.windows.boundaries_sep),
                                   height=int(orig_h * scale_init),
                                   borders_innerH=True, borders_outerH=True, borders_innerV=True,
                                   row_background=True, scrollX=True, scrollY=True,
                                   policy=dpg.mvTable_SizingFixedFit
                                   ):
                        dpg.add_table_column(label="N")
                        dpg.add_table_column(label="Med Pixel Pos")
                        dpg.add_table_column(label="Min Pixel Pos")
                        dpg.add_table_column(label="Max Pixel Pos")
                        dpg.add_table_column(label="Med Distance")
                        dpg.add_table_column(label="Min Distance")
                        dpg.add_table_column(label="Max Distance")
                    with dpg.group(horizontal=True):
                        dpg.add_button(label='Refresh table', width=140,
                                       tag=TAGS.buttons.refresh_boundary_table,
                                       callback=process_table_data)
                        dpg.add_button(label='Optical thickness', width=140, callback=graphic_imaging)
            with dpg.child_window(tag=TAGS.child_windows.optical_thickness,
                                  width=dpg.get_item_width(TAGS.windows.main) - 40,
                                  height=dpg.get_item_height(TAGS.windows.main) - (
                                          STATE.constants.const_2 + STATE.constants.const_1 +
                                          dpg.get_item_height(TAGS.child_windows.boundary))
                                  ):
                with dpg.plot(width=dpg.get_item_width(TAGS.windows.main)-40,
                              height=dpg.get_item_height(TAGS.windows.main) - (STATE.constants.const_2 + STATE.constants.const_1 +
                                                                  dpg.get_item_height(TAGS.child_windows.boundary)),
                              tag=TAGS.plots.optical_thickness, no_title=True):
                    dpg.add_plot_legend()
                    x_axis_ = dpg.add_plot_axis(dpg.mvXAxis, label='Data', tag=TAGS.axis.x_opt)
                    y_axis_ = dpg.add_plot_axis(dpg.mvYAxis, label='Opt thick, mkm', tag=TAGS.axis.y_opt)
