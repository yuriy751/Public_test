import dearpygui.dearpygui as dpg
from ...state import STATE
from ...tags import TAGS
from ...ui_adapters.input_defaults import INPUT_DEFAULTS
from ...Mu_s_focus_imaging import (
    update_focus_line_only, load_images_mu_s, show_next_mu_s, show_prev_mu_s, show_mu_s_image_by_index
)
from ...Mu_s_plot import draw_mu_s_plot
from ...Mu_s_window_view import mu_s_window_creation
from ...Mu_s_Core_Calculations import refresh_mu_s_for_selected


def mu_s_tab_func():
    with dpg.tab(label='Mu_s calculation', tag=TAGS.tabs.mu_s):
        with dpg.child_window(tag=TAGS.windows.mu_s,
                              width=dpg.get_viewport_width() - int(
                                  STATE.constants.Fraction * dpg.get_viewport_width()),
                              height=dpg.get_viewport_height() - STATE.constants.const_1,
                              no_scrollbar=True, no_scroll_with_mouse=True, tracked=True
                              ):
            with dpg.group(horizontal=True, horizontal_spacing=20):
                dpg.add_input_float(label='Wavelength, nm',
                                    tag=TAGS.inputs.wavelength,
                                    width=STATE.constants.const_3,
                                    default_value=INPUT_DEFAULTS.wavelength,
                                    format='%.1f')
                dpg.add_input_int(label='Focus position in air, pixel',
                                  tag=TAGS.inputs.focus_position,
                                  width=STATE.constants.const_3,
                                  default_value=INPUT_DEFAULTS.focus_position,
                                  callback=update_focus_line_only)
                dpg.add_input_float(label='Omega',
                                    tag=TAGS.inputs.omega,
                                    width=STATE.constants.const_3,
                                    default_value=INPUT_DEFAULTS.omega,
                                    format='%.2f')
            with dpg.group(horizontal=True):
                with dpg.group():
                    with dpg.group(horizontal=True):
                        dpg.add_text('', tag=TAGS.text_fields.mu_s_filename)
                        dpg.add_text('', tag=TAGS.text_fields.mu_s_counter)
                    with dpg.child_window(
                            tag=TAGS.child_windows.mu_s_focus,
                            width=int(STATE.constants.original_width * STATE.scale.scale *
                                      STATE.scale.window_scale),
                            height=int(STATE.constants.original_height *
                                       STATE.scale.scale *
                                       STATE.scale.window_scale),
                            no_scrollbar=True
                    ):
                        dpg.add_drawlist(tag=TAGS.drawlists.mu_s,
                                         width=int(
                                             STATE.constants.original_width *
                                             STATE.scale.scale *
                                             STATE.scale.window_scale),
                                         height=int(
                                             STATE.constants.original_height *
                                             STATE.scale.scale *
                                             STATE.scale.window_scale)
                                         )
                    with dpg.group(horizontal=True, horizontal_spacing=20):
                        dpg.add_button(label='Load images',
                                       tag=TAGS.buttons.mu_s_load,
                                       callback=load_images_mu_s)
                        dpg.add_button(label='Show',
                                       tag=TAGS.buttons.mu_s_show,
                                       callback=lambda: show_mu_s_image_by_index(0))
                        dpg.add_button(label='Previous image',
                                       tag=TAGS.buttons.mu_s_prev,
                                       callback=show_prev_mu_s)
                        dpg.add_button(label='Next image',
                                       tag=TAGS.buttons.mu_s_next,
                                       callback=show_next_mu_s)
                        dpg.add_button(label='Focus line',
                                       tag=TAGS.buttons.mu_s_focus_line,
                                       callback=update_focus_line_only)

                with dpg.group():
                    dpg.add_text('', tag=TAGS.text_fields.mu_s_table_counts)
                    with dpg.table(
                            tag=TAGS.tables.mu_s,
                            width=dpg.get_item_width(TAGS.windows.mu_s)
                                  - dpg.get_item_width(TAGS.child_windows.mu_s_focus),
                            height=dpg.get_item_height(TAGS.child_windows.mu_s_focus),
                            borders_innerH=True, borders_outerH=True, borders_innerV=True,
                            row_background=True, scrollX=True, scrollY=True,
                            policy=dpg.mvTable_SizingFixedFit
                    ):
                        dpg.add_table_column(label="N")
                        dpg.add_table_column(label="mu_s 1/mm")
                        dpg.add_table_column(label="mu_s (std) 1/mm")
                    with dpg.group(horizontal=True, horizontal_spacing=20):
                        dpg.add_button(label='Refresh table',
                                       tag=TAGS.buttons.mu_s_refresh_table,
                                       callback=refresh_mu_s_for_selected)
                        dpg.add_button(label='View mu_s images', callback=mu_s_window_creation)
                        dpg.add_button(label='Mu_s plot', callback=draw_mu_s_plot)
            with dpg.child_window(
                tag=TAGS.child_windows.mu_s_plot,
                width=dpg.get_item_width(TAGS.child_windows.mu_s_focus),
                height=dpg.get_item_height(TAGS.windows.mu_s) * 0.23 / STATE.scale.window_scale
            ):
                with dpg.plot(
                        tag=TAGS.plots.mu_s,
                        width=dpg.get_item_width(TAGS.windows.mu_s) - 30,
                        height=dpg.get_item_height(TAGS.windows.mu_s) -
                               int(STATE.constants.original_height *
                                   STATE.scale.scale *
                                   STATE.scale.window_scale) - 170, no_title=True
                ):
                    dpg.add_plot_legend()
                    x_axis_mu_s = dpg.add_plot_axis(dpg.mvXAxis, label='Data',
                                                    tag=TAGS.axis.x_mu_s)
                    y_axis_mu_s = dpg.add_plot_axis(dpg.mvYAxis, label='Mu_s, 1/mm',
                                                    tag=TAGS.axis.y_mu_s)