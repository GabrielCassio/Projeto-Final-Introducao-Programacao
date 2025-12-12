# scene_base.py
class Scene:
    def __init__(self, scene_system):
        self.scene_system = scene_system

    def handle_input(self, events, keys):
        pass

    def update(self):
        pass

    def draw(self, surface):
        pass