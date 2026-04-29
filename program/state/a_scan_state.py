# a_scan_state.py

from dataclasses import dataclass


@dataclass
class AScanState:
    graph_coordinates = [0, 0, 0, 0]
    x_data_a_scan = None
    y_data_a_scan = None