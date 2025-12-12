import pygame
# Importing systems
from src.systems.render_sys import RenderSystem

# Importing Entities
from src.objects.entity.obj_player import Player

# Importing settings
from src.settings import *

class Scenes:
    def __init__(self):
        # Render system instance to render the scenes
        self.instance_render = RenderSystem()

        # Index to the game scene
        self.cur_scene = 'Game Running'

        self.player = None

        self.scenes = {
            'Game Home': self.scene_0,
            'Game Running': self.scene_1,
        }
        self.draw_scenes()

    def draw_scenes(self):
        match (self.cur_scene):
            case 'Game Home': 
                return self.scenes['Game Home']()
            case 'Game Running':
                return self.scenes['Game Running']()
            case _:
                return self.scenes['Game Running']()

    # Home Game page layout   
    def scene_0(self):
        ...
    
    def scene_1(self):
        # Initializing iamges Render
        self.player = Player("Edísio", 300, 300, "src/sprites/psg.png")
        self.instance_render.add_sprite(self.player, LAYER_CHARACTERS)
        ...
    
    def update(self):
        self.player.update()