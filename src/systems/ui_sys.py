import pygame

# Importing settings
from src.settings import *

class UI(pygame.sprite.Sprite):
  '''
    Class that designs the entire user interface in the game.
  '''
  def __init__(self):
    super().__init__()
    # General
    self.display_surface = pygame.display.get_surface()
    self.font = pygame.font.Font(TITLES_FONT, UI_FONT_SIZE)
    
    # bar setup
    self.health_bar_rect = pygame.Rect(10, 10, HEALTH_BAR_WIDTH, BAR_HEIGHT)
    self.energy_bar_rect = pygame.Rect(10, 34, ENERGY_BAR_WIDTH, BAR_HEIGHT)

  def display(self, player): 
    pygame.draw.rect(self.display_surface, UI_BG_COLOR, self.health_bar_rect)
    pygame.draw.rect(self.display_surface, UI_BORDER_COLOR, self.health_bar_rect, 3)
    