import pygame
from src.settings import *

class UI(pygame.sprite.Sprite):
  def __init__(self):
    super().__init__()
    # General
    self.display_surface = pygame.display.get_surface()
    self.font = pygame.font.Font(UI_FONT, UI_FONT_SIZE)
    
    # bar setup
    self.health_bar_rect = pygame.Rect(10, 10, HEALTH_BAR_WIDTH, BAR_HEIGHT)
    self.energy_bar_rect = pygame.Rect(10, 34, ENERGY_BAR_WIDTH, BAR_HEIGHT)
  
  def show_bar(self, current, max_amount, bg_rect, color):
    # draw bg
    pygame.draw.rect(self.display_surface, UI_BG_COLOR, bg_rect)
    
    # converting stat to pixel
    ratio = current / max_amount
    current_width = bg_rect.width * ratio
    current_rect = bg_rect.copy()
    current_rect.width = current_width
    
    # draw the bar
    pygame.draw.rect(self.display_surface, color, current_rect)
    pygame.draw.rect(self.display_surface, UI_BORDER_COLOR, bg_rect, 3)

  def display(self, player): 
    self.show_bar(player.health, player.stats['health'], self.health_bar_rect, HEALTH_COLOR)
    