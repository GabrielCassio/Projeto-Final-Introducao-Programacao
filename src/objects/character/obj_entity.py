import pygame
from src.settings import *

# Class template do Player
class Entity(pygame.sprite.Sprite):
   # The respective entity could be receive 
   def __init__(self, name: str, x: int, y: int, path_sprite: str):
      # Acessing de parent of the Player class
      super().__init__()

      # ------------------------------------------------
      self.image = pygame.Surface((20, 10))
      self.image.fill((255, 255, 0)) 
      self.rect = self.image.get_rect()
      self.rect.center = (WIDTH // 2, HEIGHT // 2)

      # Status
      self.bow_skill = True
      self.player_speed = 5 
      
      #self.self_direction = 'right' 
      self.last_dash = 0
      self.dash_cooldown = 1000
      
      self.last_shot = 0
      self.shot_cooldown = 400 # Meio segundo entre flechas
      # ---------------------------------------------------------
      
      # Playe name
      self.name = name

      # Physics Properties -------------------------
      self.velocity = 5
      self.old_position = pygame.Vector2(x, y)
      # --------------------------------------------

      # Sprite Properties --------------------------
      self.sprite_index = 0
      self.direction = "DOWN"
      # --------------------------------------------