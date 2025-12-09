import pygame
import src.objects.components.controls.obj_keyboard as obj_keyboard

# This class create a new Player Object
# This class inherints de class of the pygame - pygame.sprite.Sprite
class Player(pygame.sprite.Sprite):

    # Class initialization
    def __init__(self, name: str, path_sprite: str, x: int, y: int):
       # Acessing de parent of the Player class
       super().__init__()

       # Setting infos for the class Player
       # Name of player
       self.name = name
       # Image of skin
       self.image = None
       # Velocity of player
       self.velocity = 5

       # Initializating the sprite of player
       self.load_sprite(path_sprite, x, y)

    def load_sprite(self, path_sprite: str, x: int, y: int):
        # Loading sprite/skin to this player
        self.image = pygame.image.load(path_sprite).convert_alpha()
        # Catching rect collision of the sprite
        self.rect = self.image.get_rect()
        # Position tuple of the char
        self.rect.center = (x, y)

    def update(self):
        # Calling de function of movement
       self.rect.x, self.rect.y = obj_keyboard.input_keyboard_handling(self.rect.x, self.rect.y, self.velocity)