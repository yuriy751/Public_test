# Global_paths_changing.py

import dearpygui.dearpygui as dpg
from .project_state import ProjectState


def project_modified_function_true(state: ProjectState) -> bool:
    """
    Отмечает проект как изменённый и обновляет заголовок окна.
    """
    if not state.modified:
        state.mark_modified()

        title = dpg.get_viewport_title()
        if not title.endswith("*"):
            dpg.set_viewport_title(title + "*")

    return True


def project_modified_function_false(
    state: ProjectState,
    new_title: str | None = None
) -> bool:
    """
    Отмечает проект как сохранённый и обновляет заголовок окна.
    """
    state.mark_saved()

    if new_title:
        dpg.set_viewport_title(new_title)
    else:
        title = dpg.get_viewport_title()
        if title.endswith("*"):
            dpg.set_viewport_title(title[:-1])

    return False
