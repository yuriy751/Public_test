from __future__ import annotations

from dataclasses import fields, is_dataclass
from typing import Dict, Iterable, List

from . import TAGS


REQUIRED_TAG_GROUPS: dict[str, tuple[str, ...]] = {
    "drawlists": ("boundary", "roi", "mu_s", "mu_s_images", "imaging"),
    "child_windows": ("boundary", "imaging", "gallery", "gallery_processed", "mu_s_images"),
    "textures": ("boundaries", "boundary_image", "mu_s", "mu_s_images"),
    "tables": ("boundaries", "mu_s", "av_int"),
    "dialogs": ("open_project",),
    "mini_windows": ("new_project",),
}

REQUIRED_TAGS_FOR_NEW_PROJECT_FLOW: dict[str, tuple[str, ...]] = {
    "drawlists": REQUIRED_TAG_GROUPS["drawlists"],
    "textures": REQUIRED_TAG_GROUPS["textures"],
    "tables": REQUIRED_TAG_GROUPS["tables"],
    "child_windows": REQUIRED_TAG_GROUPS["child_windows"],
    "mini_windows": REQUIRED_TAG_GROUPS["mini_windows"],
}

REQUIRED_TAGS_FOR_OPEN_PROJECT_FLOW: dict[str, tuple[str, ...]] = {
    "drawlists": REQUIRED_TAG_GROUPS["drawlists"],
    "textures": REQUIRED_TAG_GROUPS["textures"],
    "tables": REQUIRED_TAG_GROUPS["tables"],
    "child_windows": REQUIRED_TAG_GROUPS["child_windows"],
    "dialogs": REQUIRED_TAG_GROUPS["dialogs"],
}


def _missing_from_group(group_name: str, required_attrs: Iterable[str]) -> list[str]:
    group = getattr(TAGS, group_name, None)
    if group is None:
        return [f"{group_name}.* (group missing)"]

    missing: list[str] = []
    for attr in required_attrs:
        if not hasattr(group, attr):
            missing.append(f"{group_name}.{attr} (attribute missing)")
            continue

        value = getattr(group, attr)
        if not isinstance(value, str) or not value.strip():
            missing.append(f"{group_name}.{attr} (empty/invalid value)")
    return missing


def validate_required_tags(required_by_group: Dict[str, Iterable[str]]) -> List[str]:
    missing: list[str] = []
    for group_name, required_attrs in required_by_group.items():
        missing.extend(_missing_from_group(group_name, required_attrs))
    return missing


def list_dataclass_fields(group_name: str) -> set[str]:
    group = getattr(TAGS, group_name, None)
    if group is None or not is_dataclass(group):
        return set()
    return {f.name for f in fields(group)}
