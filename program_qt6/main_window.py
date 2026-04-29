from __future__ import annotations

from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QComboBox,
    QInputDialog,
    QFileDialog,
    QFormLayout,
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

from .export_service import export_results
from .gallery_model import GalleryStore
from .results_tables import ResultsTabs
from .processing_service import run_boundaries_for_image
from .results_service import calculate_results
from .state_machine import GalleryUiState


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("OCT B-scan | PyQt6 Pilot")
        self.resize(1200, 700)

        self.state = GalleryUiState()
        self.boundary_outputs = []
        self.calculated_results = []
        self.gallery_store = GalleryStore(Path.cwd() / "qt6_projects")
        self.current_gallery_id = None
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
        self.export_btn = QPushButton("Export results")
        row.addWidget(self.load_btn)
        row.addWidget(self.delete_btn)
        row.addWidget(self.process_btn)
        row.addWidget(self.export_btn)

        gallery_row = QHBoxLayout()
        layout.addLayout(gallery_row)
        self.gallery_combo = QComboBox()
        self.new_gallery_btn = QPushButton("New gallery")
        self.rename_gallery_btn = QPushButton("Rename gallery")
        gallery_row.addWidget(QLabel("Gallery:"))
        gallery_row.addWidget(self.gallery_combo)
        gallery_row.addWidget(self.new_gallery_btn)
        gallery_row.addWidget(self.rename_gallery_btn)

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

        self.roi_x1 = QSpinBox(); self.roi_x1.setRange(0, 10000); self.roi_x1.setValue(10)
        self.roi_x2 = QSpinBox(); self.roi_x2.setRange(0, 10000); self.roi_x2.setValue(500)
        self.roi_y1 = QSpinBox(); self.roi_y1.setRange(0, 10000); self.roi_y1.setValue(10)
        self.roi_y2 = QSpinBox(); self.roi_y2.setRange(0, 10000); self.roi_y2.setValue(500)
        roi_form = QFormLayout()
        roi_form.addRow("ROI x1", self.roi_x1)
        roi_form.addRow("ROI x2", self.roi_x2)
        roi_form.addRow("ROI y1", self.roi_y1)
        roi_form.addRow("ROI y2", self.roi_y2)
        layout.addLayout(roi_form)

        self.images = QListWidget()
        self.images.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
        layout.addWidget(self.images)

        self.results_tabs = ResultsTabs()
        layout.addWidget(self.results_tabs)

        self.info = QLabel("Pilot state: gallery flow and button gating")
        self.info.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(self.info)

        self.load_btn.clicked.connect(self._load_images)
        self.new_gallery_btn.clicked.connect(self._new_gallery)
        self.rename_gallery_btn.clicked.connect(self._rename_gallery)
        self.gallery_combo.currentIndexChanged.connect(self._switch_gallery)
        self.delete_btn.clicked.connect(self._delete_selected)
        self.process_btn.clicked.connect(self._add_to_processing)
        self.export_btn.clicked.connect(self._export_results)
        self.roi_btn.clicked.connect(self._run_roi)
        self.boundaries_btn.clicked.connect(self._run_boundaries)
        self.intensity_btn.clicked.connect(self._run_intensity)
        self.parameters_btn.clicked.connect(self._run_parameters)
        self.mu_t_btn.clicked.connect(lambda: self._notify("Mu_t processing stub"))

        self.images.itemSelectionChanged.connect(self._on_selection_changed)

    def _new_gallery(self) -> None:
        gallery = self.gallery_store.create_gallery()
        self.gallery_combo.addItem(gallery.name, gallery.gallery_id)
        self.gallery_combo.setCurrentIndex(self.gallery_combo.count() - 1)

    def _rename_gallery(self) -> None:
        if self.current_gallery_id is None:
            self._notify("Create/select gallery first")
            return
        text, ok = QInputDialog.getText(self, "Rename gallery", "New name:")
        if not ok:
            return
        self.gallery_store.rename_gallery(self.current_gallery_id, text)
        idx = self.gallery_combo.currentIndex()
        g = self.gallery_store.get(self.current_gallery_id)
        if g is not None:
            self.gallery_combo.setItemText(idx, g.name)

    def _switch_gallery(self) -> None:
        gid = self.gallery_combo.currentData()
        self.current_gallery_id = gid
        self.images.clear()
        g = self.gallery_store.get(gid) if gid is not None else None
        if g is None:
            return
        for p in g.images:
            self.images.addItem(QListWidgetItem(p))

    def _notify(self, text: str) -> None:
        self.info.setText(text)

    def _load_images(self) -> None:
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Select images",
            str(Path.cwd()),
            "Images (*.png *.jpg *.jpeg *.tif *.tiff *.bmp)",
        )
        if self.current_gallery_id is None:
            self._new_gallery()
        g = self.gallery_store.get(self.current_gallery_id)
        for f in files:
            self.images.addItem(QListWidgetItem(f))
            if g is not None and f not in g.images:
                g.images.append(f)
        self.state.has_images = self.images.count() > 0
        self.state.has_selected_images = len(self.images.selectedItems()) > 0
        if not self.state.has_images:
            self.state.clear_processing()
        self._refresh_buttons()

    def _delete_selected(self) -> None:
        g = self.gallery_store.get(self.current_gallery_id) if self.current_gallery_id is not None else None
        for item in self.images.selectedItems():
            text = item.text()
            self.images.takeItem(self.images.row(item))
            if g is not None and text in g.images:
                g.images.remove(text)

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

        selected = self.images.selectedItems()
        if not selected:
            self._notify("Select images for boundaries")
            return

        count = self.boundaries_count.value()
        roi = (
            self.roi_x1.value(),
            self.roi_x2.value(),
            self.roi_y1.value(),
            self.roi_y2.value(),
        )

        outputs = []
        for item in selected:
            result = run_boundaries_for_image(item.text(), roi, boundaries_count=count)
            if result is not None:
                outputs.append(result)

        if not outputs:
            self._notify("Boundaries failed: check ROI and image files")
            return

        self.boundary_outputs = outputs
        self.calculated_results = []

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
            f"Boundaries completed for {len(outputs)} image(s). count={count}, last_is_object_end={is_object_end}"
        )
        self._refresh_buttons()

    def _run_intensity(self) -> None:
        if not self.boundary_outputs:
            self._notify("Run boundaries first")
            return
        self.calculated_results = []
        for out in self.boundary_outputs:
            res = calculate_results(out.image_path, out)
            if res is not None:
                self.calculated_results.append(res)
        if not self.calculated_results:
            self._notify("Intensity processing failed")
            return
        self.results_tabs.load_results(self.calculated_results)
        self._notify(f"Intensity processing done for {len(self.calculated_results)} image(s)")

    def _run_parameters(self) -> None:
        if not self.calculated_results:
            self._notify("Run intensity processing first")
            return
        lines = sum(len(r.boundary_stats) for r in self.calculated_results)
        pairs = sum(len(r.thickness_stats) for r in self.calculated_results)
        self._notify(f"Parameters calculated: boundary rows={lines}, thickness rows={pairs}")

    def _export_results(self) -> None:
        if not self.calculated_results:
            self._notify("Nothing to export. Run intensity first.")
            return
        out_dir = QFileDialog.getExistingDirectory(self, "Select export folder", str(Path.cwd()))
        if not out_dir:
            return
        folder = export_results(self.calculated_results, out_dir)
        self._notify(f"Export done: {folder}")

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
