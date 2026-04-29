# __init__.py

from dataclasses import dataclass

from .windows import WindowTags
from .mini_windows import MiniWindowTags
from .buttons import ButtonTags
from .checkboxes import CheckboxTags, MuSCheckboxTags, BoundariesCheckboxTags, AvIntCheckboxTags
from .child_windows import ChildWindowTags
from .sliders import SliderTags
from .tabs import TabTags
from .tables import TableTags
from .plots import PlotTags
from .axis import AxisTags
from .series import SeriesTags, ScatterSeriesTags
from .textures import TextureTags
from .registry import RegistryTags
from .drawlists import DrawlistTags
from .dialogs import DialogTags
from .menus import MenuTags
from .menu_items import MenuItemTags
from .text_fields import TextFieldTags
from .inputs import InputFieldTags
from .groups_state import GroupState
from .tree_nodes import NodeState


@dataclass(frozen=True)
class Tags:
    windows: WindowTags = WindowTags()
    mini_windows: MiniWindowTags = MiniWindowTags()
    buttons: ButtonTags = ButtonTags()
    checkboxes: CheckboxTags = CheckboxTags()
    mu_s_checkboxes: MuSCheckboxTags = MuSCheckboxTags()
    boundaries_checkboxes: BoundariesCheckboxTags = BoundariesCheckboxTags()
    av_int_checkboxes: AvIntCheckboxTags = AvIntCheckboxTags()
    child_windows: ChildWindowTags = ChildWindowTags()
    sliders: SliderTags = SliderTags()
    tabs: TabTags = TabTags()
    tables: TableTags = TableTags()
    plots: PlotTags = PlotTags()
    axis: AxisTags = AxisTags()
    series_line: SeriesTags = SeriesTags()
    series_scatter: ScatterSeriesTags = ScatterSeriesTags()
    textures: TextureTags = TextureTags()
    registry: RegistryTags = RegistryTags()
    drawlists: DrawlistTags = DrawlistTags()
    dialogs: DialogTags = DialogTags()
    menus: MenuTags = MenuTags()
    menu_items: MenuItemTags = MenuItemTags()
    text_fields: TextFieldTags = TextFieldTags()
    inputs: InputFieldTags = InputFieldTags()
    groups: GroupState = GroupState()
    nodes: NodeState = NodeState()


TAGS = Tags()
