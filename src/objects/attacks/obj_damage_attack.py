import pygame, random

# Importing configs by attack
from .obj_config_attack import *

def roll_player_damage(base_damage: int) -> tuple[int, bool]:
    '''
        Rolls the player's damage, considering critical hits.
    '''
    is_crit = (random.random() < PLAYER_CRIT_CHANCE)
    dmg = int(base_damage * (PLAYER_CRIT_MULT if is_crit else 1))
    return dmg, is_crit