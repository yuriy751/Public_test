from program_qt6.mut_service import MuTConfig, choose_refractive_index


def test_manual_required_when_single_boundary():
    d = choose_refractive_index(
        MuTConfig(
            boundaries_count=1,
            last_boundary_is_object_end=False,
            refractive_index_mode="manual",
            manual_refractive_index=1.41,
        )
    )
    assert d.source == "manual_required"
    assert abs(d.use_refractive_index - 1.41) < 1e-9


def test_auto_mode_when_allowed():
    d = choose_refractive_index(
        MuTConfig(
            boundaries_count=2,
            last_boundary_is_object_end=True,
            refractive_index_mode="auto",
            auto_refractive_index=1.37,
        )
    )
    assert d.source == "auto"
    assert abs(d.use_refractive_index - 1.37) < 1e-9
