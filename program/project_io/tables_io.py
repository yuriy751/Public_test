# project_io/tables_io.py

import pickle
from pathlib import Path
from ..state.tables_state import TablesState   # путь подставь свой

TABLES_FILE = "tables.pkl"


def save_tables(state: TablesState, root: Path) -> None:
    path = root / TABLES_FILE
    with open(path, "wb") as f:
        pickle.dump(state, f)


def load_tables(root: Path) -> TablesState:
    path = root / TABLES_FILE
    if not path.exists():
        return TablesState()

    with open(path, "rb") as f:
        return pickle.load(f)
