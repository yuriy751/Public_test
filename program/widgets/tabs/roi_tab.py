import dearpygui.dearpygui as dpg
from ...ROI import update_roi_lines
from ...state import STATE
from ...tags import TAGS
from ...ui_adapters.input_defaults import INPUT_DEFAULTS
from ...interface_functions.other_callbacks import check_box_x_function, check_box_y_function
from ...interface_functions.draw_list_resize import begining_resize
from ...Boundaries_processing import processed_image_saving


def roi_tab_func():
    with dpg.tab(label="ROI", tag=TAGS.tabs.roi):
        with dpg.child_window(tag=TAGS.windows.boundaries,
                              width=dpg.get_item_width(TAGS.windows.main),
                              height=dpg.get_item_height(TAGS.windows.main) - STATE.constants.const_1,
                              no_scrollbar=False, no_scroll_with_mouse=False, tracked=True,
                              autosize_x=True, autosize_y=True):
            with dpg.group():

                with dpg.group(horizontal=True, horizontal_spacing=40):
                    dpg.add_checkbox(label='', tag=TAGS.checkboxes.x,
                                     callback=check_box_x_function)
                    dpg.add_slider_int(label='x 1', tag=TAGS.sliders.x1, min_value=0,
                                       max_value=STATE.constants.original_width,
                                       width=300, callback=update_roi_lines)
                    dpg.add_slider_int(label='x 2', tag=TAGS.sliders.x2, min_value=0,
                                       max_value=STATE.constants.original_width,
                                       width=300, callback=update_roi_lines)

                with dpg.group(horizontal=True, horizontal_spacing=40):
                    dpg.add_checkbox(label='', tag=TAGS.checkboxes.y,
                                     callback=check_box_y_function)
                    dpg.add_slider_int(label='y 1', tag=TAGS.sliders.y1, min_value=0,
                                       max_value=STATE.constants.original_height,
                                       width=300, callback=update_roi_lines)
                    dpg.add_slider_int(label='y 2', tag=TAGS.sliders.y2, min_value=0,
                                       max_value=STATE.constants.original_height,
                                       width=300, callback=update_roi_lines)
                    dpg.add_input_int(label='Shift', tag=TAGS.inputs.segments,
                                      width=80, min_value=1, min_clamped=True,
                                      max_value=1000, max_clamped=True, default_value=INPUT_DEFAULTS.segments)

                    scale_init, orig_w, orig_h = begining_resize()

                    STATE.scale.scale = scale_init
                with dpg.group(horizontal=True, horizontal_spacing=20):
                    with dpg.group():
                        with dpg.child_window(tag=TAGS.child_windows.imaging,
                                              width=int(orig_w * scale_init),
                                              height=int(orig_h * scale_init), no_scrollbar=True):
                            dpg.add_drawlist(tag=TAGS.drawlists.roi,
                                             width=int(orig_w * scale_init),
                                             height=int(orig_h * scale_init))
                    with dpg.group():
                        dpg.add_button(label='Process images',
                                       tag=TAGS.buttons.process,
                                       enabled=False,
                                       width=int(dpg.get_item_width(TAGS.windows.main)*0.17),
                                       height = 30,
                                       callback = processed_image_saving)
                        with dpg.child_window(width=int(dpg.get_item_width(TAGS.windows.main)*0.17),
                                              height=dpg.get_item_height(TAGS.windows.main)*0.4):
                            dpg.add_text(default_value='',
                                         tag=TAGS.text_fields.imaging_processing)
                with dpg.child_window(tag=TAGS.child_windows.average_ascan, tracked=True,
                                      width=int(orig_w * scale_init),
                                      height=dpg.get_item_height(TAGS.windows.main) - (
                                              STATE.constants.const_2 + STATE.constants.const_1 +
                                              dpg.get_item_height(
                                                  TAGS.child_windows.imaging)),
                                      no_scrollbar=True, no_scroll_with_mouse=True):
                    with dpg.plot(width=int(orig_w * scale_init),
                                  height=dpg.get_item_height(TAGS.windows.main) - (
                                          STATE.constants.const_2 + STATE.constants.const_1 +
                                          dpg.get_item_height(TAGS.child_windows.imaging)),
                                  no_title=True, tag=TAGS.plots.ascan,
                                  callback=update_roi_lines):
                        x_axis = dpg.add_plot_axis(dpg.mvXAxis, label='Depth, pixels',
                                                   tag=TAGS.axis.x_boundaries)
                        y_axis = dpg.add_plot_axis(dpg.mvYAxis, label='Average intensity',
                                                   tag=TAGS.axis.y_boundaries)
                        dpg.add_line_series([], [], tag=TAGS.series_line.ascan,
                                            parent=TAGS.axis.y_boundaries)

    pass

