from __future__ import annotations

from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QInputDialog,
    QLineEdit,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSplitter,
    QSpinBox,
    QTabWidget,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from .export_service import export_results
from .gallery_model import GalleryStore
from .mut_service import MuTConfig, choose_refractive_index
from .parameters_service import calculate_parameters_from_table
from .processing_service import run_boundaries_for_image
from .results_service import calculate_results, depth_mapping
from .results_tables import ResultsTabs
from .state_machine import GalleryUiState


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("OCT B-scan Studio | PyQt6")
        self.resize(1400, 820)

        self.state = GalleryUiState()
        self.boundary_outputs = []
        self.calculated_results = []
        self.gallery_store = GalleryStore(Path.cwd() / "qt6_projects")
        self.current_gallery_id = None
        self.auto_refractive_index = None

        self._build_ui()
        self._apply_origin_style()
        self._refresh_buttons()

    def _build_ui(self) -> None:
        root = QWidget(self)
        self.setCentralWidget(root)
        root_layout = QVBoxLayout(root)

        toolbar = QHBoxLayout()
        root_layout.addLayout(toolbar)

        self.new_gallery_btn = QPushButton("New Gallery")
        self.rename_gallery_btn = QPushButton("Rename")
        self.load_btn = QPushButton("Import Images")
        self.delete_btn = QPushButton("Delete Selected")
        self.process_btn = QPushButton("Add to Processing")
        self.export_btn = QPushButton("Export")

        for w in [
            self.new_gallery_btn,
            self.rename_gallery_btn,
            self.load_btn,
            self.delete_btn,
            self.process_btn,
            self.export_btn,
        ]:
            toolbar.addWidget(w)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        root_layout.addWidget(splitter, stretch=1)

        # LEFT: project explorer
        left = QWidget()
        left_layout = QVBoxLayout(left)
        left_layout.addWidget(QLabel("Project Explorer"))
        self.gallery_combo = QComboBox()
        left_layout.addWidget(self.gallery_combo)
        self.project_tree = QTreeWidget()
        self.project_tree.setHeaderLabels(["Folder / Gallery / Image"])
        left_layout.addWidget(self.project_tree)
        splitter.addWidget(left)

        # CENTER: data workspace
        center = QWidget()
        center_layout = QVBoxLayout(center)
        center_layout.addWidget(QLabel("Data Workspace"))
        self.workspace_tabs = QTabWidget()

        images_tab = QWidget()
        images_layout = QVBoxLayout(images_tab)
        self.images = QListWidget()
        self.images.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
        images_layout.addWidget(self.images)

        results_tab = QWidget()
        results_layout = QVBoxLayout(results_tab)
        self.results_tabs = ResultsTabs()
        results_layout.addWidget(self.results_tabs)

        self.workspace_tabs.addTab(images_tab, "Images")
        self.workspace_tabs.addTab(results_tab, "Workbook")
        center_layout.addWidget(self.workspace_tabs)
        splitter.addWidget(center)

        # RIGHT: analysis panel
        right = QWidget()
        right_layout = QVBoxLayout(right)
        right_layout.addWidget(QLabel("Analysis Panel"))

        self.roi_btn = QPushButton("ROI")
        self.boundaries_btn = QPushButton("Boundaries calculation")
        self.intensity_btn = QPushButton("Intensity processing")
        self.parameters_btn = QPushButton("Parameters calculation")
        self.mu_t_btn = QPushButton("Mu_t processing")

        for w in [
            self.roi_btn,
            self.boundaries_btn,
            self.intensity_btn,
            self.parameters_btn,
            self.mu_t_btn,
        ]:
            right_layout.addWidget(w)

        self.boundaries_count = QSpinBox()
        self.boundaries_count.setRange(1, 5)
        self.boundaries_count.setValue(2)
        self.roi_x1 = QSpinBox(); self.roi_x1.setRange(0, 10000); self.roi_x1.setValue(10)
        self.roi_x2 = QSpinBox(); self.roi_x2.setRange(0, 10000); self.roi_x2.setValue(500)
        self.roi_y1 = QSpinBox(); self.roi_y1.setRange(0, 10000); self.roi_y1.setValue(10)
        self.roi_y2 = QSpinBox(); self.roi_y2.setRange(0, 10000); self.roi_y2.setValue(500)

        form = QFormLayout()
        form.addRow("Boundaries count", self.boundaries_count)
        form.addRow("ROI x1", self.roi_x1)
        form.addRow("ROI x2", self.roi_x2)
        form.addRow("ROI y1", self.roi_y1)
        form.addRow("ROI y2", self.roi_y2)
        right_layout.addLayout(form)

        self.info = QLabel("Ready")
        self.info.setWordWrap(True)
        right_layout.addWidget(self.info)
        right_layout.addStretch(1)
        splitter.addWidget(right)

        splitter.setSizes([250, 780, 350])

        self.new_gallery_btn.clicked.connect(self._new_gallery)
        self.rename_gallery_btn.clicked.connect(self._rename_gallery)
        self.gallery_combo.currentIndexChanged.connect(self._switch_gallery)
        self.load_btn.clicked.connect(self._load_images)
        self.delete_btn.clicked.connect(self._delete_selected)
        self.process_btn.clicked.connect(self._add_to_processing)
        self.export_btn.clicked.connect(self._export_results)
        self.images.itemSelectionChanged.connect(self._on_selection_changed)

        self.roi_btn.clicked.connect(self._run_roi)
        self.boundaries_btn.clicked.connect(self._run_boundaries)
        self.intensity_btn.clicked.connect(self._run_intensity)
        self.parameters_btn.clicked.connect(self._run_parameters)
        self.mu_t_btn.clicked.connect(self._run_mu_t)

    def _apply_origin_style(self) -> None:
        self.setStyleSheet(
            """
            QMainWindow, QWidget { background: #f4f6fb; color: #20293a; }
            QPushButton { background: #e9edf7; border: 1px solid #b9c3dd; padding: 6px 10px; }
            QPushButton:hover { background: #dce5f8; }
            QTreeWidget, QListWidget, QTabWidget::pane, QTableWidget {
                background: #ffffff;
                border: 1px solid #cfd7ea;
            }
            QLabel { font-size: 12px; }
            """
        )

    def _notify(self, text: str) -> None:
        self.info.setText(text)

    def _refresh_project_tree(self) -> None:
        self.project_tree.clear()
        for gid, g in self.gallery_store.galleries.items():
            root = QTreeWidgetItem([f"{g.folder.name} / {g.name}"])
            root.setData(0, Qt.ItemDataRole.UserRole, gid)
            for p in g.images:
                root.addChild(QTreeWidgetItem([Path(p).name]))
            self.project_tree.addTopLevelItem(root)

    def _new_gallery(self) -> None:
        gallery = self.gallery_store.create_gallery()
        self.gallery_combo.addItem(gallery.name, gallery.gallery_id)
        self.gallery_combo.setCurrentIndex(self.gallery_combo.count() - 1)
        self._refresh_project_tree()

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
            self._refresh_project_tree()

    def _switch_gallery(self) -> None:
        gid = self.gallery_combo.currentData()
        self.current_gallery_id = gid
        self.images.clear()
        g = self.gallery_store.get(gid) if gid is not None else None
        if g is None:
            self.state.has_images = False
            self.state.has_selected_images = False
            self._refresh_buttons()
            return
        for p in g.images:
            self.images.addItem(QListWidgetItem(p))
        self.state.has_images = self.images.count() > 0
        self.state.has_selected_images = False
        self._refresh_buttons()

    def _load_images(self) -> None:
        files, _ = QFileDialog.getOpenFileNames(
            self, "Select images", str(Path.cwd()), "Images (*.png *.jpg *.jpeg *.tif *.tiff *.bmp)"
        )
        if not files:
            return
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
        self._refresh_project_tree()
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
        self._refresh_project_tree()
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
        self._notify("ROI region accepted")
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
        roi = (self.roi_x1.value(), self.roi_x2.value(), self.roi_y1.value(), self.roi_y2.value())

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
        self._notify(f"Boundaries completed for {len(outputs)} image(s)")
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
        self.workspace_tabs.setCurrentIndex(1)
        dm = depth_mapping(self.calculated_results[0].mean_intensity_by_roi, window=2, step=1)
        self._notify(f"Intensity done for {len(self.calculated_results)} image(s); depth profile points={len(dm.profile)}")

    def _run_mu_t(self) -> None:
        if not self.state.boundaries_ready:
            self._notify("Mu_t requires boundaries")
            return

        mode = "manual"
        if self.state.boundaries_count >= 2 and self.state.last_boundary_is_object_end:
            choice, ok = QInputDialog.getItem(
                self,
                "Mu_t refractive index",
                "Select refractive index source:",
                ["manual", "auto"],
                0,
                False,
            )
            if not ok:
                return
            mode = choice

        manual_n = None
        auto_n = self.auto_refractive_index

        if mode == "manual" or self.state.boundaries_count <= 1 or not self.state.last_boundary_is_object_end:
            text, ok = QInputDialog.getText(self, "Manual n", "Enter refractive index n:", QLineEdit.EchoMode.Normal, "1.38")
            if not ok:
                return
            try:
                manual_n = float(text)
            except ValueError:
                self._notify("Invalid refractive index value")
                return

        try:
            decision = choose_refractive_index(
                MuTConfig(
                    boundaries_count=self.state.boundaries_count,
                    last_boundary_is_object_end=self.state.last_boundary_is_object_end,
                    refractive_index_mode=mode,
                    manual_refractive_index=manual_n,
                    auto_refractive_index=auto_n,
                )
            )
        except Exception as e:
            self._notify(f"Mu_t config error: {e}")
            return

        self._notify(f"Mu_t ready: n={decision.use_refractive_index:.4f} ({decision.source})")

    def _run_parameters(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Select parameters input table",
            str(Path.cwd()),
            "Tables (*.csv)",
        )
        if not path:
            self._notify("Parameters canceled")
            return
        try:
            result = calculate_parameters_from_table(path)
        except Exception as e:
            self._notify(f"Parameters failed: {e}")
            return

        self.auto_refractive_index = result.mean_refractive_index
        self._notify(
            f"Parameters ({result.mode}) done: rows={result.rows}, mean n={result.mean_refractive_index:.4f}"
        )

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
