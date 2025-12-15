# Importing scene entity
from src.scenes.scene_entity import Scene

# Importing settings
from src.settings import *

class GameHome(Scene):
    '''
        
    '''
    def __init__(self, scene_system):
        super().__init__(scene_system)

    def handle_input(self):
        pass

    def draw(self):
        pass

    def update(self):
        self.handle_input()
        # self.instance_render.render()



    