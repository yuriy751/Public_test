# state/project_state.py

from dataclasses import dataclass, field
from pathlib import Path
from ..project_io.project_fs import ProjectFS


@dataclass
class ProjectState:
    """
    Логическое состояние проекта.

    НЕ хранит путей напрямую.
    Вся файловая структура — в ProjectFS.
    """

    fs: ProjectFS = field(default_factory=ProjectFS)
    modified: bool = False

    # --------------------------------------------------
    # Lifecycle
    # --------------------------------------------------

    def open(self, root: Path, octp_file: Path) -> None:
        """
        Открытие или создание проекта.
        """
        self.fs = ProjectFS(root=root, octp_file=octp_file)
        self.fs.ensure_structure()
        self.modified = False

    def close(self) -> None:
        self.fs = None
        self.modified = False

    # --------------------------------------------------
    # State flags
    # --------------------------------------------------

    def mark_modified(self) -> None:
        self.modified = True

    def mark_saved(self) -> None:
        self.modified = False

    # --------------------------------------------------
    # Guards
    # --------------------------------------------------

    def is_open(self) -> bool:
        return self.fs is not None
