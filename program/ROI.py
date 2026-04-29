# ROI.py

import dearpygui.dearpygui as dpg
from .state import STATE
from .tags import TAGS
from .state.Global_paths_changing import project_modified_function_true
from .A_scan_graph import a_scan_graph_data


def update_roi_lines(sender=None, app_data=None, user_data=None):
    if not dpg.does_item_exist(TAGS.drawlists.roi):
        return
    dpg.delete_item(TAGS.drawlists.roi, children_only=True)
    scale = STATE.scale.scale * STATE.scale.window_scale
    width = dpg.get_item_width(TAGS.child_windows.imaging)
    height = dpg.get_item_height(TAGS.child_windows.imaging)

    if dpg.does_item_exist(TAGS.textures.boundaries):
        dpg.draw_image(TAGS.textures.boundaries, [0, 0], [width, height], uv_min=[0, 0],
                       uv_max=[1, 1], parent=TAGS.drawlists.roi)

    x1 = int(dpg.get_value(TAGS.sliders.x1)*scale)
    x2 = int(dpg.get_value(TAGS.sliders.x2)*scale)
    y1 = int(dpg.get_value(TAGS.sliders.y1)*scale)
    y2 = int(dpg.get_value(TAGS.sliders.y2)*scale)

    if 0 <= x1 <= width:
        dpg.draw_line([x1, 0], [x1, height], color=[255, 0, 0, 255], thickness=2.0,
                      parent=TAGS.drawlists.roi)
    if 0 <= x2 <= width:
        dpg.draw_line([x2, 0], [x2, height], color=[0, 0, 255, 255], thickness=2.0,
                      parent=TAGS.drawlists.roi)
    if 0 <= y1 <= height:
        dpg.draw_line([0, y1], [width, y1], color=[0, 255, 0, 255], thickness=2.0,
                      parent=TAGS.drawlists.roi)
    if 0 <= y2 <= height:
        dpg.draw_line([0, y2], [width, y2], color=[255, 255, 0, 255], thickness=2.0,
                      parent=TAGS.drawlists.roi)
    if dpg.get_viewport_title() != 'New File' or (x1, x2, y1, y2) != (0, 0, 0, 0):
        STATE.project.modified = project_modified_function_true(STATE.project)
    a_scan_graph()
    a_scan_graph_data()

    if (
            (STATE.a_scan.x_data_a_scan is not None
             and STATE.a_scan.y_data_a_scan is not None)
            and (len(STATE.a_scan.x_data_a_scan)
                 == len(STATE.a_scan.y_data_a_scan))
    ):
        dpg.set_value(TAGS.series_line.ascan,
                      [STATE.a_scan.y_data_a_scan,
                       STATE.a_scan.x_data_a_scan])
        dpg.fit_axis_data(TAGS.axis.x_boundaries)  # Чтобы увидеть линию по горизонтали
        dpg.fit_axis_data(TAGS.axis.y_boundaries)  # Чтобы увидеть линию по вертикали
    else:
        return


def a_scan_graph():
    vals = [
        dpg.get_value(TAGS.sliders.x1), dpg.get_value(TAGS.sliders.x2),
        dpg.get_value(TAGS.sliders.y1), dpg.get_value(TAGS.sliders.y2)
    ]
    x1_val, x2_val, y1_val, y2_val = vals[0], vals[1], vals[2], vals[3]

    # Обновляем GRAPH COORDINATES (x_min, x_max, y_min, y_max)
    # x_min
    STATE.a_scan.graph_coordinates[0] = min(x1_val, x2_val)
    # x_max
    STATE.a_scan.graph_coordinates[1] = max(x1_val, x2_val)
    # y_min
    STATE.a_scan.graph_coordinates[2] = min(y1_val, y2_val)
    # y_max
    STATE.a_scan.graph_coordinates[3] = max(y1_val, y2_val)
