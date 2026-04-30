from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

from PyQt6.QtCore import Qt, QRect
from PyQt6.QtGui import QPainter, QPen, QPixmap
from PyQt6.QtWidgets import (
    QApplication, QCheckBox, QGridLayout, QGroupBox, QHBoxLayout, QLabel,
    QMainWindow, QPushButton, QSlider, QSpinBox, QTabWidget, QTableWidget,
    QTableWidgetItem, QTextEdit, QVBoxLayout, QWidget,
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
    image_view: QLabel
    log: QTextEdit


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("New File")
        self.setMinimumSize(1700, 930)
        self.resize(1700, 950)
        self._base_pixmap: QPixmap | None = None

        root = QWidget(self)
        root_layout = QVBoxLayout(root)
        self.tabs = QTabWidget(root)
        root_layout.addWidget(self.tabs)
        self.setCentralWidget(root)

        self.tabs.addTab(self._build_roi_tab(), "ROI")
        self.tabs.addTab(self._placeholder_tab("Boundary calculation"), "Boundary calculation")
        self.tabs.addTab(self._placeholder_tab("Mu_s calculation"), "Mu_s calculation")
        self.tabs.addTab(self._placeholder_tab("Average intensity calculation"), "Average intensity calculation")

    def _build_roi_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        controls_box = QGroupBox("ROI controls")
        controls_grid = QGridLayout(controls_box)

        max_w = int(STATE.constants.original_width)
        max_h = int(STATE.constants.original_height)
        x_enabled = QCheckBox("Enable X")
        y_enabled = QCheckBox("Enable Y")
        x1, x2 = self._make_slider(0, max_w), self._make_slider(0, max_w)
        y1, y2 = self._make_slider(0, max_h), self._make_slider(0, max_h)
        segments = QSpinBox(); segments.setRange(1, 1000); segments.setValue(INPUT_DEFAULTS.segments)

        controls_grid.addWidget(x_enabled, 0, 0); controls_grid.addWidget(QLabel("X1"), 0, 1); controls_grid.addWidget(x1, 0, 2)
        controls_grid.addWidget(QLabel("X2"), 1, 1); controls_grid.addWidget(x2, 1, 2)
        controls_grid.addWidget(y_enabled, 2, 0); controls_grid.addWidget(QLabel("Y1"), 2, 1); controls_grid.addWidget(y1, 2, 2)
        controls_grid.addWidget(QLabel("Y2"), 3, 1); controls_grid.addWidget(y2, 3, 2)
        controls_grid.addWidget(QLabel("Shift"), 4, 1); controls_grid.addWidget(segments, 4, 2)

        image_view = QLabel("No image loaded")
        image_view.setAlignment(Qt.AlignmentFlag.AlignCenter)
        image_view.setMinimumHeight(420)
        image_view.setStyleSheet("border: 1px solid #666;")

        actions = QHBoxLayout()
        load_preview = QPushButton("Load first project image")
        process_btn = QPushButton("Process images")
        process_btn.setEnabled(False)
        actions.addWidget(load_preview); actions.addWidget(process_btn); actions.addStretch(1)

        log = QTextEdit(); log.setReadOnly(True)

        layout.addWidget(controls_box)
        layout.addLayout(actions)
        layout.addWidget(image_view, 1)
        layout.addWidget(log, 1)

        self.roi = RoiControls(x_enabled, y_enabled, x1, x2, y1, y2, segments, image_view, log)
        self._wire_roi_state(load_preview)
        return tab

    def _wire_roi_state(self, load_preview_btn: QPushButton) -> None:
        self.roi.x1.valueChanged.connect(self._update_roi_preview)
        self.roi.x2.valueChanged.connect(self._update_roi_preview)
        self.roi.y1.valueChanged.connect(self._update_roi_preview)
        self.roi.y2.valueChanged.connect(self._update_roi_preview)
        load_preview_btn.clicked.connect(self._load_first_image_preview)

    def _load_first_image_preview(self) -> None:
        items = STATE.gallery.image_items
        if not items:
            self.roi.log.append("No images in STATE.gallery.image_items")
            return
        first_path = Path(items[0].get("path", ""))
        if not first_path.exists():
            self.roi.log.append(f"Image does not exist: {first_path}")
            return
        pix = QPixmap(str(first_path))
        if pix.isNull():
            self.roi.log.append(f"Cannot load image: {first_path}")
            return

        self._base_pixmap = pix
        self.roi.log.append(f"Loaded image: {first_path.name}")
        self._update_roi_preview()

    def _update_roi_preview(self) -> None:
        if self._base_pixmap is None:
            return
        pix = self._base_pixmap.copy()
        p = QPainter(pix)
        p.setPen(QPen(Qt.GlobalColor.red, 2))
        x1, x2 = sorted((self.roi.x1.value(), self.roi.x2.value()))
        y1, y2 = sorted((self.roi.y1.value(), self.roi.y2.value()))
        p.drawRect(QRect(x1, y1, max(1, x2 - x1), max(1, y2 - y1)))
        p.end()
        self.roi.image_view.setPixmap(pix.scaled(self.roi.image_view.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))

    @staticmethod
    def _make_slider(minimum: int, maximum: int) -> QSlider:
        slider = QSlider(Qt.Orientation.Horizontal); slider.setRange(minimum, maximum); return slider

    @staticmethod
    def _placeholder_tab(title: str) -> QWidget:
        tab = QWidget(); lay = QVBoxLayout(tab); lab = QLabel(f"{title} UI is being migrated to PyQt6.")
        lab.setAlignment(Qt.AlignmentFlag.AlignCenter); lay.addWidget(lab); return tab


def _ensure_state_defaults() -> None:
    STATE.scale.window_scale = 1.0


def gui() -> None:
    _ensure_state_defaults()
    app = QApplication.instance() or QApplication(sys.argv)
    window = MainWindow(); window.show(); app.exec()
