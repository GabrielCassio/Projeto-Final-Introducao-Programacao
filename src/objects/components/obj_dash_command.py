import pygame
# Importing Entities
from src.objects.entity.obj_entity import Entity

class DashCommand:
    def __init__(self, character: Entity):
        self.character = character
    
    def execute(self):
        keys = pygame.key.get_pressed()
        
        if keys[pygame.K_SPACE]:
            now = pygame.time.get_ticks()
            
            if self.character.dash_charges > 0 and (now - self.character.last_dash_click > self.character.spam_protection):
                self.character.last_dash_click = now
                self.character.dash_charges -= 1 
                self.character.last_recharge_time = now 
                
                # Move
                dist = self.character.dash_distance
                if (self.character.direction == 'UP'): self.character.rect.y -= dist
                elif (self.character.direction == 'DOWN'): self.character.rect.y += dist
                elif (self.character.direction == 'LEFT'): self.character.rect.x -= dist
                elif (self.character.direction == 'RIGHT'): self.character.rect.x += dist