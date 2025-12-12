import pygame
# Importing Entities
from src.objects.entity.obj_entity import Entity

class DashCommand:
    def __init__(self, character: Entity):
        self.character = character
    
    def execute(self):
        now = pygame.time.get_ticks()
        if (now - self.character.last_dash > self.character.dash_cooldown):
            self.character.last_dash = now
            if (self.character.direction == 'UP'): 
                self.character.rect.y -= 100
            elif (self.character.direction == 'DOWN'): 
                self.character.rect.y += 100
            elif (self.character.direction == 'LEFT'): 
                self.character.rect.x -= 100
            elif (self.character.direction == 'RIGHT'): 
                self.character.rect.x += 100
