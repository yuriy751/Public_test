from __future__ import annotations

from dataclasses import dataclass


@dataclass
class MuTConfig:
    boundaries_count: int
    last_boundary_is_object_end: bool
    refractive_index_mode: str  # "manual" | "auto"
    manual_refractive_index: float | None = None
    auto_refractive_index: float | None = None


@dataclass
class MuTDecision:
    use_refractive_index: float
    source: str


def choose_refractive_index(cfg: MuTConfig) -> MuTDecision:
    must_be_manual = cfg.boundaries_count <= 1 or not cfg.last_boundary_is_object_end

    if must_be_manual:
        if cfg.manual_refractive_index is None:
            raise ValueError("Manual refractive index is required for current boundary configuration")
        return MuTDecision(use_refractive_index=float(cfg.manual_refractive_index), source="manual_required")

    if cfg.refractive_index_mode == "auto":
        if cfg.auto_refractive_index is None:
            raise ValueError("Auto refractive index requested but not available")
        return MuTDecision(use_refractive_index=float(cfg.auto_refractive_index), source="auto")

    if cfg.manual_refractive_index is None:
        raise ValueError("Manual refractive index is required in manual mode")
    return MuTDecision(use_refractive_index=float(cfg.manual_refractive_index), source="manual")
