# tabs.py

from dataclasses import dataclass


@dataclass(frozen=True)
class TabTags:
    roi: str = 'ROI tag'
    boundaries: str = 'Boundaries program tag'
    mu_s: str = 'Mu s program tag'
    average_intensity: str = 'Average intensity program tag'
    graphics: str = 'Graphics program tag'
    processing_photos: str = 'Processing photos tag'
    processed_photos: str = 'Processed photos tag'
    save_files_csv: str = 'Save files csv tag'
