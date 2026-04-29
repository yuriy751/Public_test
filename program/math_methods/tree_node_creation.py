import dearpygui.dearpygui as dpg

from ..tags import TAGS
from ..dynamics_tags import DYNAMIS_TAGS
from ..state import STATE


def create_tree_node_content():

    if STATE.param_save.method_name == 'Method for deformable':
        DYNAMIS_TAGS.methods.create_new_tag('d_0', 'd_0 input tag')
        DYNAMIS_TAGS.methods.create_new_tag('d_end', 'd_end input tag')
        dpg.add_input_float(tag=DYNAMIS_TAGS.methods.d_0,
                            label='d_0, mkm',
                            default_value=500.0,
                            format='%.2f',
                            parent=TAGS.nodes.method_tree_node)
        dpg.add_input_float(tag=DYNAMIS_TAGS.methods.d_end,
                            label='d_end, mkm',
                            default_value=500.0,
                            format='%.2f',
                            parent=TAGS.nodes.method_tree_node)
    elif STATE.param_save.method_name == 'Method for non deformable':
        dynamic_tags_dict = {
            'm_dry': 'm_dry input tag',
            'm_1st_c': 'm_1st_c input tag',
            'm_2nd_c': 'm_2nd_c input tag',
            'ro_1st_c': 'ro_1st_c input tag',
            'ro_2nd_c': 'ro_2nd_c input tag'
        }
        for i in dynamic_tags_dict.keys():
            DYNAMIS_TAGS.methods.create_new_tag(i, dynamic_tags_dict[i])
            tag_value = getattr(DYNAMIS_TAGS.methods, i)
            if 'm' in i:
                dpg.add_input_float(tag=tag_value,
                                    label=i + ', g',
                                    default_value=0.0001,
                                    format='%.5f',
                                    parent=TAGS.nodes.method_tree_node,
                                    min_value=0.00001,
                                    min_clamped=True)
            elif 'ro' in i:
                dpg.add_input_float(tag=tag_value,
                                    label=i + ', g/cm^3',
                                    default_value=1,
                                    format='%.3f',
                                    parent=TAGS.nodes.method_tree_node,
                                    min_value=0.00001,
                                    min_clamped=True)
    else:
        dpg.add_text(default_value='Something', parent=TAGS.nodes.method_tree_node)