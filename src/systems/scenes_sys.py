import pygame

# Importing systems
from src.systems.render_sys import RenderSystem
from src.scenes.scene_0 import GameHome
from src.scenes.scene_1 import GameRunning

# Importing Entities
from src.objects.character.obj_player import Player

# Importing settings
from src.settings import *

class ScenesSystem:
    def __init__(self):
        # Render system instance to render the scenes
        self.instance_render = RenderSystem()

        self.player = None

        self.scenes = {
            'Game Home': GameHome(self),
            'Game Running': GameRunning(self),
        }

        # Defining default scene to the game
        self.current_scene = self.scenes['Game Home']

    def switch_scene(self, name_scene: str):
        self.current_scene = self.scenes[name_scene]

    # Home Game page layout   
    def scene_0(self):
        ...
    
    def scene_1(self):
        # Initializing iamges Render
        self.player = Player("Edísio", 300, 300, "src/sprites/psg.png")
        self.instance_render.add_sprite(self.player, LAYER_CHARACTERS)

    
    def update(self):
        '''
            Keep the current scene to 
        '''