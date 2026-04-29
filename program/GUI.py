from __future__ import annotations

import sys
from typing import Callable

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QApplication,
    QLabel,
    QMainWindow,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from .state import STATE


class MainWindow(QMainWindow):
    """PyQt6 replacement for the legacy DearPyGui shell.

    The computational pipeline and state management stay untouched; only the UI
    container is migrated so the rest of the project can be incrementally bound
    to Qt widgets.
    """

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("New File")
        self.setMinimumSize(1700, 930)
        self.resize(1700, 950)

        root = QWidget(self)
        root_layout = QVBoxLayout(root)
        root_layout.setContentsMargins(8, 8, 8, 8)

        self.tabs = QTabWidget(root)
        self._build_tabs()
        root_layout.addWidget(self.tabs)
        self.setCentralWidget(root)

    def _build_tabs(self) -> None:
        self._add_placeholder_tab("ROI")
        self._add_placeholder_tab("Boundary calculation")
        self._add_placeholder_tab("Mu_s calculation")
        self._add_placeholder_tab("Average intensity calculation")
        self._add_placeholder_tab("Graphs drawing")
        self._add_placeholder_tab("Save CSV")
        self._add_placeholder_tab("Processing photos")
        self._add_placeholder_tab("Processed photos")

    def _add_placeholder_tab(self, title: str) -> None:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        label = QLabel(
            "This tab shell was migrated to PyQt6.\n"
            "Existing calculation logic is unchanged and can be wired here incrementally."
        )
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)
        self.tabs.addTab(tab, title)


def _ensure_state_defaults() -> None:
    # Keep the same startup-side state expectations used by the old GUI shell.
    STATE.scale.window_scale = 1.0


def gui() -> None:
    _ensure_state_defaults()
    app = QApplication.instance() or QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()
