import pygame
from src.objects.character.obj_entity import Entity

class MovementCommand:

    def __init__(self, character: Entity, dx, dy, player_speed = 5):
        # Keeping the instance ogf character
        self.character = character
        self.speed = player_speed
        self.position_x = self.character.rect.x
        self.position_y = self.character.rect.y

        # Calc the current direction of player
        self.direction = pygame.Vector2(dx, dy)
        
         # Verify the current 
        if (self.direction.length() > 0): 
            self.direction = self.direction.normalize()
        
    def execute(self):
        self.position_x += (self.direction.x * self.speed)
        self.position_y += (self.direction.y * self.speed)
        self.character.move(self.position_x, self.position_y)
    
    def undo(self):
        rev_position_x = (self.position_x - (self.direction.x * self.speed))
        rev_position_y = (self.position_y - (self.direction.x * self.speed)) 
        self.character.move(rev_position_x, rev_position_y)