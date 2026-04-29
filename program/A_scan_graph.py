# A_scan_graph.py

from .state import STATE
import numpy as np
import cv2


def a_scan_graph_data():
    """
    Формирует данные для A-scan графика по текущему изображению и ROI
    """

    # === CURRENT IMG ===
    image = STATE.gallery.current_image
    if image is None:
        STATE.a_scan.x_data_a_scan = None
        STATE.a_scan.y_data_a_scan = None
        return

    if image.ndim == 3:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # === GRAPH COORDINATES (ROI) ===
    try:
        x1, x2, y1, y2 = STATE.a_scan.graph_coordinates
    except (TypeError, ValueError):
        STATE.a_scan.x_data_a_scan = None
        STATE.a_scan.y_data_a_scan = None
        return

    # Проверка ROI
    if x1 >= x2 or y1 >= y2:
        STATE.a_scan.x_data_a_scan = None
        STATE.a_scan.y_data_a_scan = None
        return

    # Клэмп ROI в границы изображения
    h, w = image.shape
    x1 = max(0, min(x1, w))
    x2 = max(0, min(x2, w))
    y1 = max(0, min(y1, h))
    y2 = max(0, min(y2, h))

    roi = image[y1:y2, x1:x2]

    # Проверка на пустой ROI
    if roi.size == 0 or roi.shape[1] == 0:
        STATE.a_scan.x_data_a_scan = None
        STATE.a_scan.y_data_a_scan = None
        return

    # === DATA ===
    STATE.a_scan.y_data_a_scan = np.arange(y1, y2).astype(np.float32).tolist()
    STATE.a_scan.x_data_a_scan = np.mean(roi, axis=1).astype(np.float32).tolist()
