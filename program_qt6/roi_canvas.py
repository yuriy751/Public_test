from __future__ import annotations

from PyQt6.QtCore import QPoint, QRect, Qt, pyqtSignal
from PyQt6.QtGui import QColor, QPainter, QPen, QPixmap
from PyQt6.QtWidgets import QLabel


class RoiCanvas(QLabel):
    roi_changed = pyqtSignal(int, int, int, int)

    def __init__(self) -> None:
        super().__init__()
        self.setMinimumHeight(280)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setStyleSheet("background:#111; color:#ddd;")
        self._pixmap: QPixmap | None = None
        self._start: QPoint | None = None
        self._end: QPoint | None = None

    def set_image(self, path: str) -> None:
        p = QPixmap(path)
        if p.isNull():
            self._pixmap = None
            self.setText("Preview unavailable")
            self.update()
            return
        self._pixmap = p
        self.setText("")
        self.update()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._start = event.position().toPoint()
            self._end = self._start
            self.update()

    def mouseMoveEvent(self, event):
        if self._start is not None:
            self._end = event.position().toPoint()
            self.update()

    def mouseReleaseEvent(self, event):
        if self._start is not None and self._end is not None:
            r = QRect(self._start, self._end).normalized()
            self.roi_changed.emit(r.left(), r.right(), r.top(), r.bottom())
        self._start = None
        self._end = None
        self.update()

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        if self._pixmap is not None:
            scaled = self._pixmap.scaled(self.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            x = (self.width() - scaled.width()) // 2
            y = (self.height() - scaled.height()) // 2
            painter.drawPixmap(x, y, scaled)

        if self._start is not None and self._end is not None:
            painter.setPen(QPen(QColor(0, 255, 200), 2))
            painter.drawRect(QRect(self._start, self._end).normalized())
