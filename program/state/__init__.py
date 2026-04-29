# __init__.py

from dataclasses import dataclass, field, fields

from .project_state import ProjectState
from .gallery_state import GalleryState
from .gallery_proc_state import GalleryProcState
from .boundaries_state import BoundariesState
from .average_intensity_state import AverageIntensityState
from .mu_s_state import MuSState
from .global_constants import Constants
from .time_state import TimeState
from .user_setteing_state import UserSettingsState
from .a_scan_state import AScanState
from .tables_state import TablesState
from .ris_state import RIsState
from .param_window_state import ParamWindowState
from .params_save import ParamSaveState
from .method_vars_state import MethodVarsState
from .optics import OpticsState
from .scale_state import ScaleState


@dataclass
class AppState:
    project: ProjectState = field(default_factory=ProjectState)
    gallery: GalleryState = field(default_factory=GalleryState)
    gallery_proc: GalleryProcState = field(default_factory=GalleryProcState)
    boundaries: BoundariesState = field(default_factory=BoundariesState)
    average_intensity: AverageIntensityState = field(default_factory=AverageIntensityState)
    mu_s: MuSState = field(default_factory=MuSState)
    a_scan: AScanState = field(default_factory=AScanState)
    time: TimeState = field(default_factory=TimeState)
    constants: Constants = field(default_factory=Constants)
    settings: UserSettingsState = field(default_factory=UserSettingsState)
    tables: TablesState = field(default_factory=TablesState)
    ris: RIsState = field(default_factory=RIsState)
    param_window: ParamWindowState = field(default_factory=ParamWindowState)
    param_save: ParamSaveState = field(default_factory=ParamSaveState)
    method_vars: MethodVarsState = field(default_factory=MethodVarsState)
    optics: OpticsState = field(default_factory=OpticsState)
    scale: ScaleState = field(default_factory=ScaleState)

    def reset(self):
        for f in fields(self):
            # Проверяем, есть ли у поля default_factory
            if f.default_factory is not list: # На всякий случай
                setattr(self, f.name, f.default_factory())
            else:
                setattr(self, f.name, f.default)

STATE = AppState()
STATE.settings = UserSettingsState.load()
