from dataclasses import dataclass


@dataclass
class ParamWindowState:
    visible: bool = False
    in_process: bool = False
    speed: int = 100
    sleep_time: float = 0
