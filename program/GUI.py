from __future__ import annotations

import sys
from dataclasses import dataclass

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QApplication,
    QCheckBox,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QSlider,
    QSpinBox,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from .state import STATE
from .ui_adapters.input_defaults import INPUT_DEFAULTS


@dataclass(slots=True)
class RoiControls:
    x_enabled: QCheckBox
    y_enabled: QCheckBox
    x1: QSlider
    x2: QSlider
    y1: QSlider
    y2: QSlider
    segments: QSpinBox


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("New File")
        self.setMinimumSize(1700, 930)
        self.resize(1700, 950)

        root = QWidget(self)
        root_layout = QVBoxLayout(root)
        root_layout.setContentsMargins(8, 8, 8, 8)

        self.tabs = QTabWidget(root)
        root_layout.addWidget(self.tabs)
        self.setCentralWidget(root)

        self._build_tabs()

    def _build_tabs(self) -> None:
        self.tabs.addTab(self._build_roi_tab(), "ROI")
        self.tabs.addTab(self._placeholder_tab("Boundary calculation"), "Boundary calculation")
        self.tabs.addTab(self._placeholder_tab("Mu_s calculation"), "Mu_s calculation")
        self.tabs.addTab(self._placeholder_tab("Average intensity calculation"), "Average intensity calculation")
        self.tabs.addTab(self._placeholder_tab("Graphs drawing"), "Graphs drawing")
        self.tabs.addTab(self._placeholder_tab("Save CSV"), "Save CSV")
        self.tabs.addTab(self._placeholder_tab("Processing photos"), "Processing photos")
        self.tabs.addTab(self._placeholder_tab("Processed photos"), "Processed photos")

    def _build_roi_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)

        controls_box = QGroupBox("ROI controls")
        controls_grid = QGridLayout(controls_box)

        x_enabled = QCheckBox("Enable X")
        y_enabled = QCheckBox("Enable Y")

        max_w = int(STATE.constants.original_width)
        max_h = int(STATE.constants.original_height)

        x1 = self._make_slider(0, max_w)
        x2 = self._make_slider(0, max_w)
        y1 = self._make_slider(0, max_h)
        y2 = self._make_slider(0, max_h)

        segments = QSpinBox()
        segments.setRange(1, 1000)
        segments.setValue(INPUT_DEFAULTS.segments)

        controls_grid.addWidget(x_enabled, 0, 0)
        controls_grid.addWidget(QLabel("X1"), 0, 1)
        controls_grid.addWidget(x1, 0, 2)
        controls_grid.addWidget(QLabel("X2"), 1, 1)
        controls_grid.addWidget(x2, 1, 2)

        controls_grid.addWidget(y_enabled, 2, 0)
        controls_grid.addWidget(QLabel("Y1"), 2, 1)
        controls_grid.addWidget(y1, 2, 2)
        controls_grid.addWidget(QLabel("Y2"), 3, 1)
        controls_grid.addWidget(y2, 3, 2)
        controls_grid.addWidget(QLabel("Shift"), 4, 1)
        controls_grid.addWidget(segments, 4, 2)

        actions_row = QHBoxLayout()
        process_btn = QPushButton("Process images")
        process_btn.setEnabled(False)
        actions_row.addWidget(process_btn)
        actions_row.addStretch(1)

        processing_log = QTextEdit()
        processing_log.setReadOnly(True)
        processing_log.setPlaceholderText("Processing log will appear here...")

        layout.addWidget(controls_box)
        layout.addLayout(actions_row)
        layout.addWidget(processing_log, 1)

        self.roi = RoiControls(
            x_enabled=x_enabled,
            y_enabled=y_enabled,
            x1=x1,
            x2=x2,
            y1=y1,
            y2=y2,
            segments=segments,
        )
        self._wire_roi_state()
        return tab

    @staticmethod
    def _make_slider(minimum: int, maximum: int) -> QSlider:
        slider = QSlider(Qt.Orientation.Horizontal)
        slider.setRange(minimum, maximum)
        return slider

    @staticmethod
    def _placeholder_tab(title: str) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        label = QLabel(f"{title} UI is being migrated to PyQt6.")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)
        return tab

    def _wire_roi_state(self) -> None:
        # This method is a dedicated extension point for wiring existing
        # computational callbacks to Qt signals during migration.
        pass


def _ensure_state_defaults() -> None:
    STATE.scale.window_scale = 1.0


def gui() -> None:
    _ensure_state_defaults()
    app = QApplication.instance() or QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()
