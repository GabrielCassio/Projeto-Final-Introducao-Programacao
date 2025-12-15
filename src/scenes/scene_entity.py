# scene_base.py
# Importing systems
from src.systems.inputs_sys import InputHandling
from src.systems.render_sys import RenderSystem

class Scene:
    def __init__(self, scene_system):
        self.instance_scene_sys = scene_system
        self.instance_render    = RenderSystem()
        self.instance_input     = InputHandling()

    def handle_input(self):
        pass

    def draw(self):
        pass

    def update(self):
        pass