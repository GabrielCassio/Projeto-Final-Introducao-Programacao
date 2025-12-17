import pygame
# Importing Entites
from src.objects.character.obj_entity import Entity
# importing Systems
from src.systems.timers_sys import Timers

class MovementCommand:
    '''
        Command to move a character entity in a 2D plane.
    '''
    def __init__(self, character: Entity, dx, dy):
        self.character = character
        
        self.prev_x = self.character.pos.x 
        self.prev_y = self.character.pos.y

        print(f"[DEBUG INIT] Input recebido -> dx: {dx}, dy: {dy}")

        self.direction = pygame.Vector2(dx, dy)
        if self.direction.length() > 0:
            self.direction = self.direction.normalize()

        self.speed = self.character.player_speed
        
        now = pygame.time.get_ticks()
        if now < self.character.attack_slow_until:
            self.speed = max(1, int(round(self.speed * self.character.attack_slow_factor)))

        self.has_animation = hasattr(self.character, 'update_animation')

    def execute(self):
        dt = Timers.delta_time
        
        print(f"[DEBUG TIME] dt: {dt}")

        move_amount = self.speed * dt
        
        position_x = self.prev_x + (self.direction.x * move_amount)
        position_y = self.prev_y + (self.direction.y * move_amount)

        print(f"[DEBUG MOVE] Antigo: ({self.prev_x}, {self.prev_y}) -> Novo: ({position_x:.2f}, {position_y:.2f})")

        self.character.move(position_x, position_y)

        if self.has_animation:
             self.character.update_animation(self.direction)
    
    def undo(self):
        self.character.move(self.prev_x, self.prev_y)