import pygame

# This class create a new Player Object
class Player(pygame.sprite.Sprite):

    # Class initialization
    def __init__(self, name: str, path_sprite: str, x: int, y: int):
       super().__init__()
       # Setting infos for the class Player
       self.name = name
       self.image = None
       self.position = {'x': x, 'y': y}

       # Initializating the sprite of player
       self.load_sprite(path_sprite)
       self.rect.topleft = (x, y)

    def load_sprite(self, path_sprite: str):
        # Loading sprite/skin to this player
        self.image = pygame.image.load(path_sprite).convert_alpha()
        self.rect = self.image.get_rect()


    def update(self):
        ...