import pytest

pytest.importorskip("cv2")
pytest.importorskip("numpy")

from program_qt6.results_service import depth_mapping


def test_depth_mapping_windowed():
    d = depth_mapping([1.0, 2.0, 3.0, 4.0], window=2, step=1)
    assert d.profile == [1.5, 2.5, 3.5]


def test_depth_mapping_short_input():
    d = depth_mapping([1.0], window=3, step=1)
    assert d.profile == [1.0]
