import pygame

# Importing scenes
from src.scenes.scene_0 import GameHome
from src.scenes.scene_1 import GameRunning

# Importing systems
from src.systems.render_sys import RenderSystem

class ScenesSystem:
    def __init__(self):
        # Render instance
        self.instance_render = RenderSystem()
        # Player instance
        self.player = None
        # Dictionary of Scene classes
        self.scenes = {
            'Game Home': GameHome(self),
            'Game Running': GameRunning(self),
        }

        # Defining default scene to the game
        self.current_scene = self.scenes['Game Home']

    def switch_scene(self, name_scene: str):
        '''
            Function to change the scene game
        '''
        self.current_scene = self.scenes[name_scene]
    
    def update(self):
        '''
            Keep the current scene to update it
        '''
        self.current_scene.update()
        self.current_scene.draw()
        self.instance_render.render()