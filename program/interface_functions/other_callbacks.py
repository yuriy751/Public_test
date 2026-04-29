import dearpygui.dearpygui as dpg

from ..tags import TAGS
from ..dynamics_tags import DYNAMIS_TAGS
from ..math_methods.tree_node_creation import create_tree_node_content
from ..state import STATE
from ..state.Global_paths_changing import project_modified_function_true


def project_modified_function_true_modified():
    STATE.project.modified = project_modified_function_true(STATE.project)


def save_keys(state):
    keys = []
    for key in state.__dict__.keys():
        keys.append(key)
    return keys


# --- Disable and enable functions ---
def check_box_x_function():
    if dpg.get_value(TAGS.checkboxes.x):
        dpg.disable_item(TAGS.sliders.x1)
        dpg.disable_item(TAGS.sliders.x2)
    else:
        dpg.enable_item(TAGS.sliders.x1)
        dpg.enable_item(TAGS.sliders.x2)


def check_box_y_function():
    if dpg.get_value(TAGS.checkboxes.y):
        dpg.disable_item(TAGS.sliders.y1)
        dpg.disable_item(TAGS.sliders.y2)
    else:
        dpg.enable_item(TAGS.sliders.y1)
        dpg.enable_item(TAGS.sliders.y2)


def n_under_callback():
    if dpg.does_item_exist(TAGS.checkboxes.low_boundary):
        if dpg.get_value(TAGS.checkboxes.low_boundary):
            dpg.show_item(TAGS.inputs.n_under)
        else:
            dpg.hide_item(TAGS.inputs.n_under)


def parameters_save_callback():
    output = ''
    ri_list = [dpg.get_value(TAGS.inputs.n_above)]

    output += (f'Deforamble sample: {dpg.get_value(TAGS.checkboxes.deformable)}\n'
               f'Bottom edge is boundary: {dpg.get_value(TAGS.checkboxes.low_boundary)}\n'
               f'Homgenious: {dpg.get_value(TAGS.checkboxes.homogenious)}\n'
               f'RI is known: {dpg.get_value(TAGS.checkboxes.known_ri)}\n'
               f'Boundaries amount: {dpg.get_value(TAGS.inputs.boundaries_amount)}\n'
               f'n0: {dpg.get_value(TAGS.inputs.n_above):.2f}\n')
    k =  0
    if STATE.ris.__dict__:
        if not dpg.get_value(TAGS.checkboxes.homogenious):
            for i in range(len(STATE.ris.get_sorted_layers())):
                # print(STATE.ris.get_sorted_layers()[i])
                output += f'n{i+1} = {STATE.ris.get_sorted_layers()[i]:.2f}\n'
                ri_list.append(STATE.ris.get_sorted_layers()[i])
                k += 1
        else:
            if dpg.get_value(TAGS.checkboxes.low_boundary):
                num = dpg.get_value(TAGS.inputs.boundaries_amount) - 1
            else:
                num = dpg.get_value(TAGS.inputs.boundaries_amount)
            for i in range(num):
                output += f'n{i+1}: {STATE.ris.get_sorted_layers()[0]:.2f}\n'
                ri_list.append(STATE.ris.get_sorted_layers()[i])
                k += 1
    if dpg.get_value(TAGS.checkboxes.low_boundary):
        output += f'n{k+1}: {dpg.get_value(TAGS.inputs.n_under):.2f}\n'
        ri_list.append(dpg.get_value(TAGS.inputs.n_under))
    dpg.set_value(TAGS.text_fields.sample_parameters, output)
    STATE.param_save.ri_list = ri_list
    STATE.param_save.boundaries_amount = dpg.get_value(TAGS.inputs.boundaries_amount)
    STATE.param_save.known_ri = dpg.get_value(TAGS.checkboxes.known_ri)
    STATE.param_save.homogenious = dpg.get_value(TAGS.checkboxes.homogenious)
    STATE.param_save.low_boundary = dpg.get_value(TAGS.checkboxes.low_boundary)
    STATE.param_save.deformable_sample = dpg.get_value(TAGS.checkboxes.deformable)

    # STATE.param_save.method_name
    if dpg.does_item_exist(TAGS.nodes.method_tree_node):
        dpg.delete_item(TAGS.nodes.method_tree_node, children_only=True)

    if DYNAMIS_TAGS.methods.__dict__:
        keys_ = save_keys(DYNAMIS_TAGS.methods)
        for i in keys_:
            DYNAMIS_TAGS.methods.delete_tag(i)

    if STATE.method_vars.__dict__:
        keys_ = save_keys(STATE.method_vars)
        for i in keys_:
            STATE.method_vars.delete_var(i)

    if STATE.param_save.deformable_sample:
        STATE.param_save.method_name = 'Method for deformable'
    else:
        STATE.param_save.method_name = 'Method for non deformable'

    create_tree_node_content()
    project_modified_function_true_modified()


def ri_is_known_callback():
    if dpg.get_value(TAGS.checkboxes.known_ri):
        dpg.enable_item(TAGS.buttons.ri_s_parameters)
        dpg.hide_item(TAGS.inputs.n_dry)
    else:
        dpg.disable_item(TAGS.buttons.ri_s_parameters)
        dpg.show_item(TAGS.inputs.n_dry)
        if STATE.ris.__dict__:
            keys_ = save_keys(STATE.ris)
            for i in keys_:
                STATE.ris.delete_n(i)


def use_bottom_edge_callback():
    if dpg.get_value(TAGS.checkboxes.low_boundary):
        dpg.show_item(TAGS.inputs.n_under)
    else:
        dpg.hide_item(TAGS.inputs.n_under)


def homogenious_callback():
    if dpg.get_value(TAGS.checkboxes.homogenious):
        STATE.optics.homogenious = True
    else:
        STATE.optics.homogenious = False


def deformable_callback():
    if dpg.get_value(TAGS.checkboxes.deformable):
        dpg.hide_item(TAGS.inputs.d)
        dpg.show_item(TAGS.inputs.tau_w)
        dpg.show_item(TAGS.inputs.tau_g)
    else:
        dpg.show_item(TAGS.inputs.d)
        dpg.hide_item(TAGS.inputs.tau_w)
        dpg.hide_item(TAGS.inputs.tau_g)