import pygame
from src.objects.character.obj_entity import Entity

# This class create a new Player Object
# This class inherints de class of the pygame - pygame.sprite.Sprite
class Player(Entity):

    # Class initialization
    def __init__(self, name: str, x: int, y: int, path_sprite: str):
       # Acessing de parent of the Player class
       super().__init__(self, x, y, path_sprite)

       # Load the image
       original_image = pygame.image.load(path_sprite).convert_alpha()

       # Initializating the sprite of player
       SCALE_FACTOR = 2.4 # Match the map scale
       w, h = original_image.get_size()
       self.image = pygame.transform.scale(original_image, (int(w * SCALE_FACTOR), int(h * SCALE_FACTOR)))
       
       # Create Rect based on the NEW size

       self.rect = self.image.get_rect(topleft = (x, y))

       
       self.stats = {'health': 100, 'energy': 60, 'attack': 10, 'magic': 4, 'speed': 6}
       self.max_stats = {'health': 300, 'energy': 140, 'attack': 20, 'magic': 10, 'speed': 10}
       self.upgrade_cost = {'health': 100, 'energy': 100, 'attack': 100, 'magic': 100, 'speed': 100}
       self.health = self.stats['health']
       self.energy = self.stats['energy']
       self.exp = 120
       self.speed = self.stats['speed']

    def move(self, new_position_x: int, new_position_y: int) -> None:

        # Store old position
        self.old_position.x = self.rect.x
        self.old_position.y = self.rect.y

        # Loading new position
        self.rect.x = new_position_x
        self.rect.y = new_position_y

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
        self.animation()
