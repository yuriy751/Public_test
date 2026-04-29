from pathlib import Path


def remove_rows_by_filenames(table_list: list, filenames: set[str]) -> list:
    """
    Удаляет записи из таблицы по filename и переиндексирует id.
    """
    if not table_list:
        return []

    filtered = [
        row for row in table_list
        if Path(row.get("filename", "")).name not in filenames
    ]

    for i, row in enumerate(filtered):
        row["id"] = i + 1

    return filtered