# project_io/checkboxes_save.py

from ..tags import TAGS
import dearpygui.dearpygui as dpg


def group_callback(sender, app_data):
    if sender == TAGS.checkboxes.boundaries:
        dpg.configure_item(TAGS.groups.boundaries, show=app_data)
    elif sender == TAGS.checkboxes.mu_s:
        dpg.configure_item(TAGS.groups.mu_s, show=app_data)
    elif sender == TAGS.checkboxes.av_int:
        dpg.configure_item(TAGS.groups.av_int, show=app_data)
    pass


def all_callback(sender, app_data):
    obj = None
    if sender == TAGS.checkboxes.all_boundaries:
        obj = TAGS.boundaries_checkboxes
    elif sender == TAGS.checkboxes.all_mu_s:
        obj = TAGS.mu_s_checkboxes
    elif sender == TAGS.checkboxes.all_av_int:
        obj = TAGS.av_int_checkboxes

    if obj is not None:
        for tag in obj.__dict__.values():
            dpg.set_value(tag, app_data)


def each_callback(sender, app_data):
    if not app_data:
        if sender in TAGS.boundaries_checkboxes.__dict__.values():
            dpg.set_value(TAGS.checkboxes.all_boundaries, False)
        elif sender in TAGS.mu_s_checkboxes.__dict__.values():
            dpg.set_value(TAGS.checkboxes.all_mu_s, False)
        elif sender in TAGS.av_int_checkboxes.__dict__.values():
            dpg.set_value(TAGS.checkboxes.all_av_int, False)