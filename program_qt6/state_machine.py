from __future__ import annotations

from dataclasses import dataclass


@dataclass
class GalleryUiState:
    has_images: bool = False
    has_selected_images: bool = False
    roi_ready: bool = False
    boundaries_ready: bool = False
    boundaries_count: int = 0
    last_boundary_is_object_end: bool = False

    def clear_processing(self) -> None:
        self.roi_ready = False
        self.boundaries_ready = False
        self.boundaries_count = 0
        self.last_boundary_is_object_end = False

    def button_enabled(self) -> dict[str, bool]:
        roi = self.has_selected_images
        boundaries = self.roi_ready
        intensity = self.boundaries_ready
        parameters = (
            self.boundaries_ready
            and self.boundaries_count >= 2
            and self.last_boundary_is_object_end
        )
        mu_t = self.boundaries_ready

        return {
            "roi": roi,
            "boundaries": boundaries,
            "intensity": intensity,
            "parameters": parameters,
            "mu_t": mu_t,
        }
