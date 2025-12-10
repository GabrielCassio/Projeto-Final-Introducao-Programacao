import pygame
from src.objects.entity.obj_entity import Entity
from src.objects.components.obj_input import InputHandling

# This class create a new Player Object
# This class inherints de class of the pygame - pygame.sprite.Sprite
class Player(Entity):

    # Class initialization
    def __init__(self, name: str, x: int, y: int, path_sprite: str):
       # Acessing de parent of the Player class
       super().__init__(self, x, y, path_sprite)

       # Initializating the sprite of player
       self.load_sprite(x, y, path_sprite)

    def load_sprite(self, x: int, y: int, path_sprite: str):
        # Loading sprite/skin to this player
        self.image = pygame.image.load(path_sprite).convert_alpha()
        # Catching rect collision of the sprite
        self.rect = self.image.get_rect()
        # Position tuple of the char
        self.rect.center = (x, y)

    def animation(self):
        
        # Position variation
        delta_pos_horizontal = self.rect.x - self.old_position.x
        delta_pos_vertical = self.rect.y - self.old_position.y

        if (delta_pos_horizontal > 0): self.sprite_direction = 'right'
        elif (delta_pos_horizontal < 0): self.sprite_direction = 'left'

        if (delta_pos_vertical > 0): self.sprite_direction = 'down'
        elif (delta_pos_vertical < 0): self.sprite_direction = 'up'

    def update(self):
        # Calling de function of movement
        InputHandling.player_movement(self)
        self.animation()
