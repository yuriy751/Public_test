# tags/group.py

from dataclasses import dataclass


@dataclass(frozen=True)
class GroupState:
    boundaries: str = 'Boundaries group state'
    mu_s: str = 'Mu_s group state'
    av_int: str = 'Av_int group state'