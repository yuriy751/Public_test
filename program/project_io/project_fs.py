# project_io/project_fs.py

from dataclasses import dataclass
from pathlib import Path
from typing import List


@dataclass
class ProjectFS:
    """
    Файловая система проекта.

    root       — рабочая папка проекта
    octp_file  — имя файла архива (.octp)
    """
    root: Path | None = None
    octp_file: str | None = None

    # -------------------------------------------------
    # JSON файлы состояния
    # -------------------------------------------------

    def inputs(self) -> Path:
        return self.root / Path("inputs.json")

    def gallery_state(self) -> Path:
        return self.root / Path("gallery_state.json")

    def gallery_proc_state(self) -> Path:
        return self.root / Path("gallery_proc_state.json")

    def a_scan_state(self) -> Path:
        return self.root / Path("a_scan_state.json")

    def mu_s_state(self) -> Path:
        return self.root / Path("mu_s_state.json")

    def boundaries_state(self) -> Path:
        return self.root / Path("boundaries_state.json")

    def constants_state(self) -> Path:
        return self.root / Path("constants_state.json")

    def project_state(self) -> Path:
        return self.root / Path("project_state.json")

    def time_state(self) -> Path:
        return self.root / Path("time_state.json")

    def average_intensity_state(self) -> Path:
        return self.root / Path("average_intensity_state.json")

    # -------------------------------------------------
    # Папки
    # -------------------------------------------------

    def main_images(self) -> Path:
        return self.root / Path("main_images")

    def images_for_processing(self) -> Path:
        return self.root / Path("images_for_processing")

    def images_with_boundaries(self) -> Path:
        return self.root / Path("images_with_boundaries")

    def mu_s_images(self) -> Path:
        return self.root / Path("mu_s_images")

    # -------------------------------------------------
    # Удобные методы
    # -------------------------------------------------

    def list_main_images(self) -> List[Path]:
        return sorted(self.main_images().glob("*.png"))

    def list_images_for_processing(self) -> List[Path]:
        return sorted(self.images_for_processing().glob("*.png"))

    def list_images_with_boundaries(self) -> List[Path]:
        return sorted(self.images_with_boundaries().glob("*.png"))

    def list_mu_s_images(self) -> List[Path]:
        return sorted(self.mu_s_images().glob("*.txt"))

    # --- serialization ---

    def to_dict(self) -> dict:
        return {
            "root": str(self.root) if self.root else None,
            "octp_file": self.octp_file,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ProjectFS":
        if data is None:
            return cls()
        root = Path(data["root"]) if data.get("root") else None
        octp_file = data.get("octp_file")
        return cls(root=root, octp_file=octp_file)

    # -------------------------------------------------
    # Lifecycle
    # -------------------------------------------------

    def ensure_structure(self) -> None:
        """
        Создаёт рабочую структуру проекта.
        """
        if self.root is None:
            raise RuntimeError("ProjectFS.root is None")

        self.root.mkdir(parents=True, exist_ok=True)

        self.main_images().mkdir(exist_ok=True)
        self.images_for_processing().mkdir(exist_ok=True)
        self.images_with_boundaries().mkdir(exist_ok=True)
        self.mu_s_images().mkdir(exist_ok=True)
