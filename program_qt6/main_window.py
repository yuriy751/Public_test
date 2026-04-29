from __future__ import annotations

from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from .state_machine import GalleryUiState


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("OCT B-scan | PyQt6 Pilot")
        self.resize(1200, 700)

        self.state = GalleryUiState()
        self._build_ui()
        self._refresh_buttons()

    def _build_ui(self) -> None:
        root = QWidget(self)
        self.setCentralWidget(root)

        layout = QVBoxLayout(root)
        row = QHBoxLayout()
        layout.addLayout(row)

        self.load_btn = QPushButton("Load images")
        self.delete_btn = QPushButton("Delete selected")
        self.process_btn = QPushButton("Add to processing")
        row.addWidget(self.load_btn)
        row.addWidget(self.delete_btn)
        row.addWidget(self.process_btn)

        row2 = QHBoxLayout()
        layout.addLayout(row2)

        self.roi_btn = QPushButton("ROI")
        self.boundaries_btn = QPushButton("Boundaries calculation")
        self.intensity_btn = QPushButton("Intensity processing")
        self.mu_t_btn = QPushButton("Mu_t processing")
        self.parameters_btn = QPushButton("Parameters calculation")

        row2.addWidget(self.roi_btn)
        row2.addWidget(self.boundaries_btn)
        row2.addWidget(self.intensity_btn)
        row2.addWidget(self.mu_t_btn)
        row2.addWidget(self.parameters_btn)

        ctrl = QHBoxLayout()
        layout.addLayout(ctrl)
        ctrl.addWidget(QLabel("Boundaries count:"))
        self.boundaries_count = QSpinBox()
        self.boundaries_count.setRange(1, 5)
        self.boundaries_count.setValue(2)
        ctrl.addWidget(self.boundaries_count)

        self.images = QListWidget()
        self.images.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
        layout.addWidget(self.images)

        self.info = QLabel("Pilot state: gallery flow and button gating")
        self.info.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(self.info)

        self.load_btn.clicked.connect(self._load_images)
        self.delete_btn.clicked.connect(self._delete_selected)
        self.process_btn.clicked.connect(self._add_to_processing)
        self.roi_btn.clicked.connect(self._run_roi)
        self.boundaries_btn.clicked.connect(self._run_boundaries)
        self.intensity_btn.clicked.connect(lambda: self._notify("Intensity processing stub"))
        self.parameters_btn.clicked.connect(lambda: self._notify("Parameters calculation stub"))
        self.mu_t_btn.clicked.connect(lambda: self._notify("Mu_t processing stub"))

        self.images.itemSelectionChanged.connect(self._on_selection_changed)

    def _notify(self, text: str) -> None:
        self.info.setText(text)

    def _load_images(self) -> None:
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Select images",
            str(Path.cwd()),
            "Images (*.png *.jpg *.jpeg *.tif *.tiff *.bmp)",
        )
        for f in files:
            self.images.addItem(QListWidgetItem(f))
        self.state.has_images = self.images.count() > 0
        self.state.has_selected_images = len(self.images.selectedItems()) > 0
        if not self.state.has_images:
            self.state.clear_processing()
        self._refresh_buttons()

    def _delete_selected(self) -> None:
        for item in self.images.selectedItems():
            self.images.takeItem(self.images.row(item))

        self.state.has_images = self.images.count() > 0
        self.state.has_selected_images = len(self.images.selectedItems()) > 0
        if not self.state.has_images:
            self.state.clear_processing()
        self._refresh_buttons()

    def _add_to_processing(self) -> None:
        if not self.state.has_selected_images:
            self._notify("Select images first")
            return
        self._notify("Selected images added to processing queue")

    def _run_roi(self) -> None:
        if not self.state.has_selected_images:
            self._notify("ROI requires selected images")
            return
        self.state.roi_ready = True
        self._notify("ROI completed (stub)")
        self._refresh_buttons()

    def _run_boundaries(self) -> None:
        if not self.state.roi_ready:
            self._notify("Boundaries require ROI")
            return

        count = self.boundaries_count.value()
        self.state.boundaries_count = count
        self.state.boundaries_ready = True

        is_object_end = QMessageBox.question(
            self,
            "Boundary type",
            "Is the last boundary the object/external-medium boundary?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        ) == QMessageBox.StandardButton.Yes
        self.state.last_boundary_is_object_end = is_object_end

        self._notify(
            f"Boundaries completed: count={count}, last_is_object_end={is_object_end}"
        )
        self._refresh_buttons()

    def _on_selection_changed(self) -> None:
        self.state.has_selected_images = len(self.images.selectedItems()) > 0
        self._refresh_buttons()

    def _refresh_buttons(self) -> None:
        enabled = self.state.button_enabled()
        self.delete_btn.setEnabled(self.state.has_selected_images)
        self.process_btn.setEnabled(self.state.has_selected_images)
        self.roi_btn.setEnabled(enabled["roi"])
        self.boundaries_btn.setEnabled(enabled["boundaries"])
        self.intensity_btn.setEnabled(enabled["intensity"])
        self.parameters_btn.setEnabled(enabled["parameters"])
        self.mu_t_btn.setEnabled(enabled["mu_t"])
