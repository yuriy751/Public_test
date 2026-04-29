import dearpygui.dearpygui as dpg
from ...state import STATE
from ...tags import TAGS


def graph_tab_func():
    with dpg.tab(label='Graphics', tag=TAGS.tabs.graphics):
        with dpg.child_window(tag=TAGS.windows.plots,
                              width=dpg.get_item_width(TAGS.windows.main),
                              height=dpg.get_item_height(TAGS.windows.main) - STATE.constants.const_1
                              ):
            dpg.add_tree_node(tag=TAGS.nodes.method_tree_node)