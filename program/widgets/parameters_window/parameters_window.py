import dearpygui.dearpygui as dpg
from ...tags import TAGS
from ...state import STATE
from ...ui_adapters.input_defaults import INPUT_DEFAULTS
from .poping_up import update_panel
from ...interface_functions.other_callbacks import (
    project_modified_function_true_modified, parameters_save_callback, ri_is_known_callback, use_bottom_edge_callback,
homogenious_callback, deformable_callback
)
from ...RIs_ import ris_window, boundaries_amount_changing



def parameters_window_func():
    with dpg.window(tag=TAGS.windows.parameter,
                    pos=(dpg.get_viewport_width()-2.5*STATE.constants.const_1, 2.5*STATE.constants.const_1),
                    no_close=True, no_collapse=True, no_move=True,
                    height=dpg.get_viewport_height(),
                    width=int(STATE.constants.Fraction * dpg.get_viewport_width()),
                    no_resize=True, autosize=False, no_scrollbar=True, no_title_bar=False, no_scroll_with_mouse=True,
                    label='Parameters'):
        with dpg.group(horizontal=True, horizontal_spacing=40):
            dpg.add_button(label='+', tag=TAGS.buttons.popup_param_window, callback=update_panel)
            with dpg.group():
                dpg.add_input_float(
                    label='Pixel size',
                    tag=TAGS.inputs.pixel_size,
                    default_value=INPUT_DEFAULTS.pixel_size, step=0.01,
                    width=STATE.constants.const_3,
                    format='%.2f',
                    callback=project_modified_function_true_modified
                    )

                dpg.add_text('\n')
                dpg.add_input_int(label='Boundaries amount',
                                  tag=TAGS.inputs.boundaries_amount,
                                  width=STATE.constants.const_3,
                                  min_value=1, min_clamped=True,
                                  max_value=5, max_clamped=True,
                                  default_value=INPUT_DEFAULTS.boundary_amounts,
                                  callback=boundaries_amount_changing)

                dpg.add_text('\nObject properties')
                dpg.add_checkbox(label='Deformable sample',
                                 tag=TAGS.checkboxes.deformable,
                                 default_value=STATE.optics.deformable,
                                 callback=deformable_callback
                                 )
                dpg.add_checkbox(label='Bottom edge is boundary',
                                 tag=TAGS.checkboxes.low_boundary,
                                 default_value=STATE.optics.low_boundary,
                                 callback=use_bottom_edge_callback
                                 )
                dpg.add_checkbox(label='Homogenious sample',
                                 tag=TAGS.checkboxes.homogenious,
                                 default_value=STATE.optics.homogenious,
                                 callback=homogenious_callback
                                 )
                dpg.add_checkbox(label='RI is known',
                                 tag=TAGS.checkboxes.known_ri,
                                 default_value=STATE.optics.known_ri,
                                 callback=ri_is_known_callback)
                dpg.add_button(label='RIs of sample',
                               tag=TAGS.buttons.ri_s_parameters,
                               enabled=False,
                               callback=ris_window)
                #
                # dpg.add_text('\nObject parameters')
                # dpg.add_input_float(label='Thickness, mkm',
                #                     tag=TAGS.inputs.d_0,
                #                     width=STATE.constants.const_3,
                #                     format='%.1f', min_value=0,
                #                     default_value=INPUT_DEFAULTS.d_0,
                #                     min_clamped=True,
                #                     callback=project_modified_function_true_modified)
                # dpg.add_input_float(label='End thickness',
                #                     tag=TAGS.inputs.d_end,
                #                     width=STATE.constants.const_3,
                #                     format='%.1f', min_value=0,
                #                     min_clamped=True,
                #                     default_value=INPUT_DEFAULTS.d_end,
                #                     callback=project_modified_function_true_modified,
                #                     show=False)

                dpg.add_text('\nExternal medium')
                dpg.add_input_float(label='n_above',
                                    tag=TAGS.inputs.n_above,
                                    width=STATE.constants.const_3,
                                    default_value=INPUT_DEFAULTS.n_above,
                                    format='%.2f')
                dpg.add_input_float(label='n_under',
                                    tag=TAGS.inputs.n_under,
                                    width=STATE.constants.const_3,
                                    default_value=INPUT_DEFAULTS.n_under,
                                    format='%.2f')

                dpg.add_text('\nOCA parameters')
                dpg.add_input_float(label='Water fraction',
                                    tag=TAGS.inputs.w,
                                    width=STATE.constants.const_3,
                                    format='%.2f', min_clamped=True,
                                    max_clamped=True,
                                    default_value=INPUT_DEFAULTS.w,
                                    min_value=0, max_value=1,
                                    callback=project_modified_function_true_modified)
                dpg.add_input_float(label='RI of water',
                                    tag=TAGS.inputs.n_w,
                                    width=STATE.constants.const_3,
                                    min_value=1.0, max_value=3, step=0.01,
                                    default_value=INPUT_DEFAULTS.n_w,
                                    min_clamped=True, max_clamped=True,
                                    callback=project_modified_function_true_modified)
                dpg.add_input_float(label='RI of 2nd comp',
                                    tag=TAGS.inputs.n_g,
                                    width=STATE.constants.const_3,
                                    min_value=1.0, max_value=3, step=0.01,
                                    default_value=INPUT_DEFAULTS.n_g,
                                    min_clamped=True, max_clamped=True,
                                    callback=project_modified_function_true_modified)

                dpg.add_text('\nParameters results')
                dpg.add_input_float(label='phi_0', readonly=True, tag=TAGS.inputs.phi_0,
                                    width=STATE.constants.const_3,
                                    default_value=INPUT_DEFAULTS.phi_0)
                dpg.add_input_float(label='d', readonly=True, tag=TAGS.inputs.d,
                                    width=STATE.constants.const_3,
                                    default_value=INPUT_DEFAULTS.d)
                dpg.add_input_float(label='tau_w', readonly=True, tag=TAGS.inputs.tau_w,
                                    width=STATE.constants.const_3,
                                    default_value=INPUT_DEFAULTS.tau_w,
                                    show=False)
                dpg.add_input_float(label='tau_g', readonly=True, tag=TAGS.inputs.tau_g,
                                    width=STATE.constants.const_3,
                                    default_value=INPUT_DEFAULTS.tau_g,
                                    show=False)
                dpg.add_input_float(label='n_dry', readonly=True, tag=TAGS.inputs.n_dry,
                                    width=STATE.constants.const_3,
                                    default_value=INPUT_DEFAULTS.n_dry)

                dpg.add_button(label='Save input data',
                               tag=TAGS.buttons.save_params,
                               width=dpg.get_item_width(TAGS.windows.parameter)-40-dpg.get_item_width(TAGS.buttons.popup_param_window),
                               callback=parameters_save_callback)

                with dpg.child_window(horizontal_scrollbar=True, tag=TAGS.child_windows.text):
                     dpg.add_text(tag=TAGS.text_fields.sample_parameters)