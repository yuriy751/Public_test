#!/usr/bin/env python3
from __future__ import annotations

import ast
from pathlib import Path

from program.tags.validation import list_dataclass_fields

FILES_TO_CHECK = [
    Path("program/project_io/new_project.py"),
    Path("program/Gallery.py"),
]


def extract_tag_usages(path: Path) -> dict[str, set[str]]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    usages: dict[str, set[str]] = {}

    for node in ast.walk(tree):
        if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Attribute):
            group_node = node.value
            if isinstance(group_node.value, ast.Name) and group_node.value.id == "TAGS":
                group_name = group_node.attr
                attr_name = node.attr
                if not attr_name.startswith('__'):
                    usages.setdefault(group_name, set()).add(attr_name)
    return usages


def main() -> int:
    errors: list[str] = []
    all_usages: dict[str, set[str]] = {}

    for file in FILES_TO_CHECK:
        usages = extract_tag_usages(file)
        for group, attrs in usages.items():
            all_usages.setdefault(group, set()).update(attrs)

    for group, attrs in sorted(all_usages.items()):
        available = list_dataclass_fields(group)
        if not available:
            continue
        missing = sorted(attr for attr in attrs if attr not in available)
        if missing:
            errors.append(f"{group}: missing attributes {missing}")

    if errors:
        print("[TAG_SCHEMA][FAIL]")
        for err in errors:
            print(f"  - {err}")
        return 1

    print("[TAG_SCHEMA][OK] All TAGS.* usages from new_project.py and Gallery.py are present in tag dataclasses.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
