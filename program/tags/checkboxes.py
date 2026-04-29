# checkboxes.py

from dataclasses import dataclass


@dataclass(frozen=True)
class CheckboxTags:
    x: str = 'Check x tag'
    y: str = 'Check y tag'

    low_boundary: str = 'Check low_boundary tag'
    homogenious: str = 'Homogenious tag'
    deformable: str = 'Deformable tag'
    known_ri: str = 'known_ri tag'

    mu_s: str = 'Check mu_s tag'
    boundaries: str = 'Check boundaries tag'
    av_int: str = 'Check av_int tag'
    params: str = 'Check params tag'

    images_default: str = 'Images default tag'
    images_boundarise: str = 'Images boundarise tag'
    images_mu_s: str = 'Images mu_s tag'

    all_mu_s: str = 'Check all_mu_s tag'
    all_boundaries: str = 'Check all_boundaries tag'
    all_av_int: str = 'Check all_av_int tag'


@dataclass(frozen=True)
class MuSCheckboxTags:
    roi: str = 'ROI mu_s'
    total: str = 'Total mu_s'
    raw: str = 'Raw mu_s'


@dataclass(frozen=True)
class AvIntCheckboxTags:
    roi: str = 'ROI av_int'
    total: str = 'Total av_int'
    raw: str = 'Raw av_int'


@dataclass(frozen=True)
class BoundariesCheckboxTags:
    med_p: str = 'Med_p boundaries'
    min_p: str = 'Min_p boundaries'
    max_p: str = 'Max_p boundaries'
    med_d: str = 'Med_d boundaries'
    min_d: str = 'Min_d boundaries'
    max_d: str = 'Max_d boundaries'
    med_total: str = 'Med_total boundaries'
    min_total: str = 'Min_total boundaries'
    max_total: str = 'Max_total boundaries'
    raw_p: str = 'Raw_p boundaries'
    raw_d: str = 'Raw_d boundaries'
    raw_total: str = 'Raw_total boundaries'
