import csv
from pathlib import Path
import numpy as np
import dearpygui.dearpygui as dpg
from typing import Any


def save_csv(rows: list[dict], path: Path):
    if not rows:
        return

    # собрать ВСЕ ключи из всех строк
    fieldnames = []
    seen = set()

    for row in rows:
        for key in row.keys():
            if key not in seen:
                seen.add(key)
                fieldnames.append(key)

    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def serialize_array(data) -> str:
    """
    Приводит любые вложенные структуры (list, ndarray, числа)
    к строке для записи в CSV.
    """

    if data is None:
        return ""

    # numpy array → "1.0;2.0;3.0"
    if isinstance(data, np.ndarray):
        return ";".join(str(x) for x in data.flatten())

    # list → "a|b|c" (рекурсивно)
    if isinstance(data, list):
        return "|".join(serialize_array(x) for x in data)

    # numpy scalar → python scalar
    if isinstance(data, np.generic):
        return str(data.item())

    # обычные числа
    if isinstance(data, (int, float)):
        return str(data)

    # строки
    if isinstance(data, str):
        return data

    # fallback (на всякий случай)
    return str(data)


def get_selected_fields(
    enabled_checkbox: str,
    all_checkbox: str,
    fields_checkboxes: Any,
) -> list[str]:
    """
    Универсальная функция получения выбранных полей таблицы.

    enabled_checkbox  – главный чекбокс (вкл/выкл таблицу)
    all_checkbox      – чекбокс 'All'
    fields_checkboxes – dataclass с tag'ами чекбоксов полей
    """

    # Таблица выключена
    if not dpg.get_value(enabled_checkbox):
        return []

    # Все возможные поля
    all_fields = list(fields_checkboxes.__dict__.keys())

    # Выбран All
    if dpg.get_value(all_checkbox):
        return all_fields

    selected = []
    for field_name, tag in fields_checkboxes.__dict__.items():
        if dpg.get_value(tag):
            selected.append(field_name)

    return selected


def to_npz_safe(value):
    if isinstance(value, np.ndarray):
        return value
    return np.array(value, dtype=object)


def normalize_csv_value(val):
    """
    Приводит значение к CSV-дружелюбному виду
    """

    if val is None:
        return ""

    # numpy scalar → python scalar
    if isinstance(val, np.generic):
        return val.item()

    # обычные числа
    if isinstance(val, (int, float)):
        return val

    # строки
    if isinstance(val, str):
        return val

    # fallback
    return str(val)