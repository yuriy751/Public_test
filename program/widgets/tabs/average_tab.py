import dearpygui.dearpygui as dpg
from ...state import STATE
from ...tags import TAGS
from ...Average_intensity_calculation import refresh_av_int_for_selected
from ...Average_intensity_plot import draw_av_int_plot


def average_tab_func():
    with dpg.tab(label='Average intensity calculation', tag=TAGS.tabs.average_intensity):
        with dpg.child_window(tag=TAGS.windows.av_int,
                              width=dpg.get_item_width(TAGS.windows.main),
                              height=dpg.get_item_height(TAGS.windows.main) - STATE.constants.const_1,
                              no_scrollbar=True, no_scroll_with_mouse=True, tracked=True
                              ):
            with dpg.group(horizontal=True, horizontal_spacing=20):
                dpg.add_button(label='Refresh table',
                               tag=TAGS.buttons.average_table_process,
                               callback=refresh_av_int_for_selected)
                dpg.add_button(label='Plot',
                               tag=TAGS.buttons.average_intensity_plot,
                               callback=draw_av_int_plot)
            with dpg.table(tag=TAGS.tables.av_int,
                           width=dpg.get_item_width(TAGS.windows.av_int),
                           height=dpg.get_item_height(TAGS.windows.av_int) // 2 - 30,
                           borders_innerH=True, borders_outerH=True, borders_innerV=True,
                           row_background=True, scrollX=True, scrollY=True,
                           policy=dpg.mvTable_SizingFixedFit
                           ):
                dpg.add_table_column(label="N")
                dpg.add_table_column(label="Av int (med), pixel value")
                dpg.add_table_column(label="Av int (std), pixel value")
            with dpg.plot(tag=TAGS.plots.average_intensity,
                          width=dpg.get_item_width(TAGS.windows.av_int) - 30,
                          height=dpg.get_item_height(TAGS.windows.av_int) // 2 - 80):
                dpg.add_plot_legend()
                x_axis_av_int = dpg.add_plot_axis(dpg.mvXAxis, label='Data',
                                                  tag=TAGS.axis.x_av_int)
                y_axis_av_int = dpg.add_plot_axis(dpg.mvYAxis, label='Average intensity, pixel value',
                                                  tag=TAGS.axis.y_av_int),
                y_axis_av_int_2 = dpg.add_plot_axis(dpg.mvYAxis2,
                                                    label='Average relative intensity, pixel value/mkm',
                                                    tag=TAGS.axis.y_av_int_rel)