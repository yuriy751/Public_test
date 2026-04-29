# Parameters_calculation.py

from .tags import TAGS
from .state import STATE
import dearpygui.dearpygui as dpg
import numpy as np
from scipy.optimize import curve_fit


def data_choose():
    # 1. Правильная проверка на пустоту
    if not STATE.tables.boundaries:
        print('[Optical_thickness_check] table is empty')
        # Возвращаем 3 пустых списка, чтобы программа не упала при распаковке результата
        return []

    med_total = [row['med_total'] for row in STATE.tables.boundaries]

    return med_total


def ddry_ad_bs(phi_0: float) -> tuple:
    d_dry: float = dpg.get_value(TAGS.inputs.d_0) * (1 - phi_0)
    a_d: float = dpg.get_value(TAGS.inputs.d_0) - d_dry
    b_s: float = dpg.get_value(TAGS.inputs.d_end) - d_dry
    return d_dry, a_d, b_s


def d_fitting(t: np.ndarray, tau_g: float, tau_w: float, phi_0: float) -> np.ndarray:
    d_dry, a_d, b_s = ddry_ad_bs(phi_0)
    d_mass: np.ndarray = a_d * np.exp(-t/tau_w) + dpg.get_value(TAGS.inputs.w) \
                         * b_s * (1 - np.exp(-t/tau_g)) + \
                         (1-dpg.get_value(TAGS.inputs.w) * b_s * (1 - np.exp(-t/tau_w)) + d_dry)
    return d_mass


def n_a_fitting(t: np.ndarray, tau_g: float, tau_w: float, phi_0: float) -> np.ndarray:
    d_dry, a_d, b_s = ddry_ad_bs(phi_0)
    d_mass: np.ndarray = d_fitting(t, tau_g, tau_w, phi_0)
    coef: np.ndarray = d_mass-d_dry
    n_a: np.ndarray = dpg.get_value(TAGS.inputs.n_g) * (b_s/coef * dpg.get_value(TAGS.inputs.w) * (1 - np.exp(-t/tau_g))) + \
                      dpg.get_value(TAGS.inputs.n_w) * (a_d/coef * np.exp(-t/tau_w) + b_s/coef * (1 - dpg.get_value(TAGS.inputs.w) * (1 - np.exp(-t/tau_w))))
    return n_a


def phi_fitting(t: np.ndarray, tau_g: float, tau_w: float, phi_0: float) -> np.ndarray:
    d_dry = ddry_ad_bs(phi_0)[0]
    d_mass: np.ndarray = d_fitting(t, tau_g, tau_w, phi_0)
    phi_mass: np.ndarray = 1 - d_dry/d_mass
    return phi_mass


def n_sum_fitting(t: np.ndarray, tau_g: float, tau_w: float, phi_0: float) -> np.ndarray:
    n_a_mass: np.ndarray = n_a_fitting(t, tau_g, tau_w, phi_0)
    phi_mass: np.ndarray = phi_fitting(t, tau_g, tau_w, phi_0)
    n_sum_mass: np.ndarray = phi_mass * n_a_mass + (1-phi_mass) * dpg.get_value(TAGS.inputs.n_dry)
    return n_sum_mass


def l_fitting(t: np.ndarray, tau_g: float, tau_w: float, phi_0: float) -> np.ndarray:
    d_mass: np.ndarray = d_fitting(t, tau_g, tau_w, phi_0)
    n_sum_mass: np.ndarray = n_sum_fitting(t, tau_g, tau_w, phi_0)
    l_mass: np.ndarray = d_mass*n_sum_mass
    return l_mass


def alpha_fitting(t: np.ndarray, tau_g: float, tau_w: float, phi_0: float) -> tuple:
    d_dry, a_d, b_s = ddry_ad_bs(phi_0)
    d_mass: np.ndarray = d_fitting(t, tau_g, tau_w, phi_0)
    coef: np.ndarray = d_mass-d_dry
    alpha_1: np.ndarray = b_s/coef * dpg.get_value(TAGS.inputs.w) * (1 - np.exp(-t/tau_g))
    alpha_2: np.ndarray = a_d/coef * np.exp(-t/tau_w) + b_s/coef * (1 - dpg.get_value(TAGS.inputs.w) * (1 - np.exp(-t/tau_w)))
    return alpha_1, alpha_2


def parameters_calculation():
    if STATE.tables.boundaries is []:
        dpg.set_value(TAGS.text_fields.plots_info, 'You have to find boundaries firstly')
        return
    time = STATE.time.time_list
    l_exp = np.asarray(data_choose())*dpg.get_value(TAGS.inputs.pixel_size)
    params = curve_fit(l_fitting, time, l_exp, p0=np.array([1.1, 1.1, 0.1]),
                       bounds=(np.array([1, 1, 0.1]), np.array([10000, 10000, 0.4])))
    tau_g, tau_w, phi_0 = params[0]
    dpg.enable_item(TAGS.buttons.plot_processing)
    dpg.set_value(TAGS.inputs.phi_0, phi_0)
    dpg.set_value(TAGS.inputs.tau_w, tau_w)
    dpg.set_value(TAGS.inputs.tau_g, tau_g)
    dpg.set_value(TAGS.text_fields.plots_info, 'All parameters are found')
    dpg.enable_item(TAGS.checkboxes.params)


def geometry_thickness_plot():
    tag = TAGS.series_line.geometric_thickness
    phi_0 = dpg.get_value(TAGS.inputs.phi_0)
    tau_w = dpg.get_value(TAGS.inputs.tau_w)
    tau_g = dpg.get_value(TAGS.inputs.tau_g)
    time: np.ndarray = np.arange(STATE.time.time_list[-1])
    data: np.ndarray = d_fitting(time, tau_g, tau_w, phi_0)
    data_ = [i for i in data]
    time_ = [i for i in time]
    if not dpg.does_item_exist(tag):
        dpg.add_line_series(time_, data_, tag=tag, parent=TAGS.axis.y_geom_thick)
    else:
        dpg.set_value(tag, [time_, data_])
    dpg.fit_axis_data(TAGS.axis.x_geom_thick)
    dpg.fit_axis_data(TAGS.axis.y_geom_thick)


def optical_thickness_plot():
    tag_1 = TAGS.series_line.optical_thickness
    tag_2 = TAGS.series_scatter.optical_thickness
    phi_0 = dpg.get_value(TAGS.inputs.phi_0)
    tau_w = dpg.get_value(TAGS.inputs.tau_w)
    tau_g = dpg.get_value(TAGS.inputs.tau_g)
    time_1: np.ndarray = np.arange(STATE.time.time_list[-1])
    data_1: np.ndarray = l_fitting(time_1, tau_g, tau_w, phi_0)
    time_1_ = [i for i in time_1]
    data_1_ = [i for i in data_1]
    time_2_ = STATE.time.time_list
    data_2: np.ndarray = np.asarray(data_choose())*dpg.get_value(TAGS.inputs.pixel_size)
    data_2_ = [i for i in data_2]
    if not dpg.does_item_exist(tag_1):
        dpg.add_line_series(time_1_, data_1_, tag=tag_1, parent=TAGS.axis.y_opt_thick)
    else:
        dpg.set_value(tag_1, [time_1_, data_1_])
    if not dpg.does_item_exist(tag_2):
        dpg.add_scatter_series(time_2_, data_2_, tag=tag_2, parent=TAGS.axis.y_opt_thick)
    else:
        dpg.set_value(tag_2, [time_2_, data_2_])
    dpg.fit_axis_data(TAGS.axis.x_opt_thick)
    dpg.fit_axis_data(TAGS.axis.y_opt_thick)


def ri_of_liquid_plot():
    tag = TAGS.series_line.liquid_ri
    phi_0 = dpg.get_value(TAGS.inputs.phi_0)
    tau_w = dpg.get_value(TAGS.inputs.tau_w)
    tau_g = dpg.get_value(TAGS.inputs.tau_g)
    time: np.ndarray = np.arange(STATE.time.time_list[-1])
    data: np.ndarray = n_a_fitting(time, tau_g, tau_w, phi_0)
    data_ = [i for i in data]
    time_ = [i for i in time]
    if not dpg.does_item_exist(tag):
        dpg.add_line_series(time_, data_, tag=tag, parent=TAGS.axis.y_liquid_ri)
    else:
        dpg.set_value(tag, [time_, data_])
    dpg.fit_axis_data(TAGS.axis.x_liquid_ri)
    dpg.fit_axis_data(TAGS.axis.y_liquid_ri)


def common_ri_plot():
    tag = TAGS.series_line.total_ri
    phi_0 = dpg.get_value(TAGS.inputs.phi_0)
    tau_w = dpg.get_value(TAGS.inputs.tau_w)
    tau_g = dpg.get_value(TAGS.inputs.tau_g)
    time: np.ndarray = np.arange(STATE.time.time_list[-1])
    data: np.ndarray = n_sum_fitting(time, tau_g, tau_w, phi_0)
    data_ = [i for i in data]
    time_ = [i for i in time]
    if not dpg.does_item_exist(tag):
        dpg.add_line_series(time_, data_, tag=tag, parent=TAGS.axis.y_total_ri)
    else:
        dpg.set_value(tag, [time_, data_])
    dpg.fit_axis_data(TAGS.axis.x_total_ri)
    dpg.fit_axis_data(TAGS.axis.y_total_ri)


def fraction_of_liquid_plot():
    tag = TAGS.series_line.liquid_fraction
    phi_0 = dpg.get_value(TAGS.inputs.phi_0)
    tau_w = dpg.get_value(TAGS.inputs.tau_w)
    tau_g = dpg.get_value(TAGS.inputs.tau_g)
    time: np.ndarray = np.arange(STATE.time.time_list[-1])
    data: np.ndarray = phi_fitting(time, tau_g, tau_w, phi_0)
    data_ = [i for i in data]
    time_ = [i for i in time]
    if not dpg.does_item_exist(tag):
        dpg.add_line_series(time_, data_, tag=tag, parent=TAGS.axis.y_liquid_fract)
    else:
        dpg.set_value(tag, [time_, data_])
    dpg.fit_axis_data(TAGS.axis.x_liquid_fract)
    dpg.fit_axis_data(TAGS.axis.y_liquid_fract)


def fractiom_of_components_plot():
    tag_1 = TAGS.series_line.components_fraction
    tag_2 = TAGS.series_line.components_fraction_2
    phi_0 = dpg.get_value(TAGS.inputs.phi_0)
    tau_w = dpg.get_value(TAGS.inputs.tau_w)
    tau_g = dpg.get_value(TAGS.inputs.tau_g)
    time: np.ndarray = np.arange(STATE.time.time_list[-1])
    data_1, data_2 = alpha_fitting(time, tau_g, tau_w, phi_0)
    data_1_ = [i for i in data_1]
    data_2_ = [i for i in data_2]
    time_ = [i for i in time]
    if not dpg.does_item_exist(tag_1):
        dpg.add_line_series(time_, data_1_, tag=tag_1, parent=TAGS.axis.y_comp_fract)
    else:
        dpg.set_value(tag_1, [time_, data_1_])
    if not dpg.does_item_exist(tag_2):
        dpg.add_line_series(time_, data_2_, tag=tag_2, parent=TAGS.axis.y_comp_fract)
    else:
        dpg.set_value(tag_2, [time_, data_2_])
    dpg.fit_axis_data(TAGS.axis.x_comp_fract)
    dpg.fit_axis_data(TAGS.axis.y_comp_fract)


def draw_all_plots():
    geometry_thickness_plot()
    optical_thickness_plot()
    ri_of_liquid_plot()
    common_ri_plot()
    fraction_of_liquid_plot()
    fractiom_of_components_plot()
    dpg.set_value(TAGS.text_fields.plots_info, 'Graphs are plotted')
    pass
