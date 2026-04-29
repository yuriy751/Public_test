from pathlib import Path

import pytest

pytest.importorskip("numpy")
pytest.importorskip("pandas")

from program_qt6.parameters_service import calculate_parameters_from_table


def test_parameters_3cols(tmp_path: Path):
    p = tmp_path / "x.csv"
    p.write_text("t,opt,geo\n0,1.4,1.0\n1,2.8,2.0\n")
    out = calculate_parameters_from_table(str(p))
    assert out.mode == "3-columns"
    assert abs(out.mean_refractive_index - 1.4) < 1e-6


def test_parameters_2cols(tmp_path: Path):
    p = tmp_path / "y.csv"
    p.write_text("t,opt\n0,1.0\n1,1.5\n2,2.0\n")
    out = calculate_parameters_from_table(str(p))
    assert out.mode == "2-columns"
    assert 1.0 <= out.mean_refractive_index <= 2.0
