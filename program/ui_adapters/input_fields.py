# input_fields.py

# ui_adapters/input_fields.py

from typing import Dict, Any
import dearpygui.dearpygui as dpg
from ..tags import TAGS


def collect_input_fields() -> Dict[str, Any]:
    """
    Считывает значения всех input-полей из UI по TAGS.inputs
    и возвращает plain dict.
    """
    result: Dict[str, Any] = {}

    for name, tag in TAGS.inputs.__dict__.items():
        if name.startswith("_"):
            continue

        if not dpg.does_item_exist(tag):
            result[name] = None
            continue

        try:
            result[name] = dpg.get_value(tag)
        except Exception:
            result[name] = None

    return result


def apply_input_fields(data: Dict[str, Any]) -> None:
    """
    Загружает значения в input-поля UI по TAGS.inputs.
    """
    for name, value in data.items():
        if not hasattr(TAGS.inputs, name):
            continue

        tag = getattr(TAGS.inputs, name)

        if not dpg.does_item_exist(tag):
            continue

        try:
            dpg.set_value(tag, value)
        except Exception:
            pass
