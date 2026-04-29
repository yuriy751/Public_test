# mini_windows.py

from dataclasses import dataclass


@dataclass(frozen=True)
class MiniWindowTags:
    new_project: str = 'New project window tag'
    close: str = 'Close window tag'
    rewrite_proj_conf: str = 'Rewite proj conf tag'
    time: str = 'Time window tag'
    ris: str = 'Ris window tag'