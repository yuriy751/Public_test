import dearpygui.dearpygui as dpg
from ..state import STATE
from ..tags import TAGS
from .draw_list_resize import draw_resize
from ..Gallery import layout_gallery
from ..Gallery_proc import layout_boundaries_gallery
from ..ROI import update_roi_lines


def resize_gui():
    draw_resize()
    new_scale = STATE.scale.scale
    window_scale = STATE.scale.window_scale
    # print(f'new_scale = {new_scale}\nwindow_scale = {window_scale}')

    # --- Main windows ---

    dpg.configure_item(
        TAGS.windows.main,
        height=dpg.get_viewport_height() - STATE.constants.const_1,
        width=int(dpg.get_viewport_width()*window_scale)
    )

    if STATE.param_window.visible:
        dpg.set_item_pos(
            TAGS.windows.parameter,
             [dpg.get_viewport_width() - dpg.get_item_width(TAGS.windows.parameter), 2.5 * STATE.constants.const_1]
                         )
    else:
        dpg.set_item_pos(
            TAGS.windows.parameter,
             [dpg.get_viewport_width() - 2.5 * STATE.constants.const_1, 2.5 * STATE.constants.const_1]
                         )

    window_tags = [TAGS.windows.boundaries, TAGS.windows.boundaries_sep, TAGS.windows.mu_s,
                   TAGS.windows.av_int, TAGS.windows.plots, TAGS.windows.save_files,
                   TAGS.child_windows.gallery_processed, TAGS.child_windows.gallery]
    for i in window_tags:
        if dpg.does_item_exist(i):
            dpg.configure_item(
                i,
                width=dpg.get_item_width(TAGS.windows.main),
                height=dpg.get_item_height(TAGS.windows.main)-STATE.constants.const_1
            )
    # --- Child windows ---

    dpg.configure_item(
        TAGS.child_windows.gallery_processed,
        width=dpg.get_item_width(TAGS.windows.main) - STATE.constants.const_2,
        height=dpg.get_item_height(TAGS.windows.main) - STATE.constants.const_2
    )
    dpg.configure_item(
        TAGS.child_windows.gallery,
        width=dpg.get_item_width(TAGS.windows.main) - STATE.constants.const_2,
        height=dpg.get_item_height(TAGS.windows.main) - STATE.constants.const_2
    )

    # --- Lists of tags ---
    draw_child_windows_tags = [TAGS.child_windows.imaging, TAGS.child_windows.boundary, TAGS.child_windows.mu_s_focus]
    plot_child_windows_tags = [TAGS.child_windows.average_ascan, TAGS.child_windows.optical_thickness, TAGS.child_windows.mu_s_plot]
    draw_lists_tags = [TAGS.drawlists.roi, TAGS.drawlists.boundary, TAGS.drawlists.mu_s]
    plots_tags = [TAGS.plots.ascan, TAGS.plots.optical_thickness, TAGS.plots.mu_s]
    tables_tags = [TAGS.tables.boundaries, TAGS.tables.mu_s]

    for i, j in zip(draw_child_windows_tags, plot_child_windows_tags):
        if dpg.does_item_exist(i):
            dpg.configure_item(
                i,
                width=STATE.constants.original_width * new_scale * window_scale,
                height=STATE.constants.original_height * new_scale * window_scale
            )
        if dpg.does_item_exist(j):
            dpg.configure_item(
                j,
                width=dpg.get_item_width(TAGS.windows.main) * 0.95,
                height=dpg.get_item_height(TAGS.windows.main) * 0.23 / window_scale
            )


    for i, j in zip(draw_lists_tags, plots_tags):
        if dpg.does_item_exist(i):
            dpg.configure_item(
                i,
                width=dpg.get_item_width(TAGS.child_windows.imaging),
                height=dpg.get_item_height(TAGS.child_windows.imaging)
            )
        if dpg.does_item_exist(j):
            dpg.configure_item(
                j,
                width=dpg.get_item_width(TAGS.windows.main) * 0.95,
                height=dpg.get_item_height(TAGS.windows.main) * 0.23 / window_scale
            )

    for i in tables_tags:
        if dpg.does_item_exist(i):
            dpg.configure_item(
                i,
                width=dpg.get_item_width(TAGS.windows.boundaries) - dpg.get_item_width(TAGS.child_windows.imaging),
                height=dpg.get_item_height(TAGS.child_windows.imaging)
            )

    # --- Boundary image texture ---

    if dpg.does_item_exist(TAGS.textures.boundary_image):
        try:
            dpg.draw_image(
                TAGS.textures.boundary_image,
                [0, 0],
                [dpg.get_item_width(TAGS.child_windows.boundary), dpg.get_item_height(TAGS.child_windows.boundary)],
                uv_min=[0, 0],
                uv_max=[1, 1],
                parent=TAGS.drawlists.boundary)
        except SystemError:
            pass


    # --- Average_scan window ---
    dpg.configure_item(
        TAGS.tables.av_int,
        width=dpg.get_item_width(TAGS.windows.av_int),
        height=dpg.get_item_height(TAGS.windows.av_int)//2 - 30,
    )
    dpg.configure_item(
        TAGS.plots.average_intensity,
        width=dpg.get_item_width(TAGS.windows.av_int) - 30,
        height=dpg.get_item_height(TAGS.windows.av_int) // 2 - 80
    )

    # --- Others ---
    update_roi_lines()
    # update_size()
    layout_gallery()
    layout_boundaries_gallery()
