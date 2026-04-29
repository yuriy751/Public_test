from __future__ import annotations

from PyQt6.QtWidgets import QTableWidget, QTableWidgetItem, QTabWidget

from .results_service import ImageResults


class ResultsTabs(QTabWidget):
    def load_results(self, results: list[ImageResults]) -> None:
        self.clear()
        self._add_boundaries_tab(results)
        self._add_thickness_tab(results)
        self._add_intensity_tab(results)

    def _add_boundaries_tab(self, results: list[ImageResults]) -> None:
        rows = sum(len(r.boundary_stats) for r in results)
        table = QTableWidget(rows, 5)
        table.setHorizontalHeaderLabels(["image", "line", "min", "max", "median"])
        row = 0
        for r in results:
            for b in r.boundary_stats:
                table.setItem(row, 0, QTableWidgetItem(r.image_path))
                table.setItem(row, 1, QTableWidgetItem(str(b.line_index)))
                table.setItem(row, 2, QTableWidgetItem(f"{b.min_y:.3f}"))
                table.setItem(row, 3, QTableWidgetItem(f"{b.max_y:.3f}"))
                table.setItem(row, 4, QTableWidgetItem(f"{b.median_y:.3f}"))
                row += 1
        self.addTab(table, "Boundaries")

    def _add_thickness_tab(self, results: list[ImageResults]) -> None:
        rows = sum(len(r.thickness_stats) for r in results)
        table = QTableWidget(rows, 5)
        table.setHorizontalHeaderLabels(["image", "pair", "min", "max", "median"])
        row = 0
        for r in results:
            for t in r.thickness_stats:
                table.setItem(row, 0, QTableWidgetItem(r.image_path))
                table.setItem(row, 1, QTableWidgetItem(f"{t.pair[0]}-{t.pair[1]}"))
                table.setItem(row, 2, QTableWidgetItem(f"{t.min_t:.3f}"))
                table.setItem(row, 3, QTableWidgetItem(f"{t.max_t:.3f}"))
                table.setItem(row, 4, QTableWidgetItem(f"{t.median_t:.3f}"))
                row += 1
        self.addTab(table, "Thickness")

    def _add_intensity_tab(self, results: list[ImageResults]) -> None:
        rows = sum(len(r.mean_intensity_by_roi) for r in results)
        table = QTableWidget(rows, 3)
        table.setHorizontalHeaderLabels(["image", "roi_index", "mean_intensity"])
        row = 0
        for r in results:
            for i, v in enumerate(r.mean_intensity_by_roi, start=1):
                table.setItem(row, 0, QTableWidgetItem(r.image_path))
                table.setItem(row, 1, QTableWidgetItem(str(i)))
                table.setItem(row, 2, QTableWidgetItem(f"{v:.3f}"))
                row += 1
        self.addTab(table, "Intensity")
