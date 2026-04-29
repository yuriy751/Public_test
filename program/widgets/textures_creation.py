import dearpygui.dearpygui as dpg
from ..tags import TAGS


def texture_creation():
    with dpg.texture_registry(tag=TAGS.registry.image):
        dpg.add_dynamic_texture(1, 1, [1.0, 1.0, 1.0, 1.0],
                                tag=TAGS.textures.boundary_image)
        pass

    with dpg.texture_registry(tag=TAGS.registry.boundary):
        pass

    with dpg.texture_registry(tag=TAGS.registry.mu_s):
        dpg.add_dynamic_texture(1, 1, [1.0, 1.0, 1.0, 1.0],
                                tag=TAGS.textures.mu_s)
        pass

    with dpg.texture_registry(tag=TAGS.registry.mu_s_images):
        pass