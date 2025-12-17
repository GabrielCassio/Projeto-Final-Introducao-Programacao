import pygame
# Importing systems
from src.systems.render_sys import RenderSystem

# Importing Settings
from src.settings import *

class MeleeCommand:
    '''
        This class call the melee attack action from a player.
    '''
    def __init__(self, player):
        # Keep the player reference
        self.player = player

    def execute(self):
        self.player.action_melee()

class RangedCommand:
    '''
        This class call the ranged attack action from a player.
    '''
    def __init__(self, player):
        # Keep the player reference
        self.player = player

    def execute(self):
        self.player.action_ranged()