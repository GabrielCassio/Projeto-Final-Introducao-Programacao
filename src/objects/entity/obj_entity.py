import pygame

# Class template do Player
class Entity(pygame.sprite.Sprite):
   # The respective entity could be receive 
   def __init__(self, name: str, x: int, y: int, path_sprite: str):
      # Acessing de parent of the Player class
      super().__init__()

      # Playe name
      self.name = name

      # Physics Properties -------------------------
      self.velocity = 5
      self.old_position = pygame.Vector2(x, y)
      self.direction = "default"
      # --------------------------------------------

      # Sprite Properties --------------------------
      self.sprite_index = 0
      self.sprite_direction = "default"
      # --------------------------------------------