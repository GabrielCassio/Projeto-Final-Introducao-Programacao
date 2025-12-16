import pygame
from src.settings import *

class EntityButton(pygame.sprite.Sprite):
    def __init__(self, text: str, x: int, y: int, w: int, h:int, variant: str ='primary', action: bool=None):
        # Calling the class super
        super().__init__()

        # Button variables
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.variant = variant
        self.action = action
        self.hovered = False
        
        # Colors
        if variant == 'primary':
            self.background_color = GREEN_900_COLOR
            self.border_color = GREEN_500_COLOR
            self.text_color = GREEN_100_COLOR
        elif variant == 'danger':
            self.background_color = RED_900_COLOR
            self.border_color = RED_500_COLOR
            self.text_color = GREEN_100_COLOR
        else: # secondary
            self.background_color = GRAY_900_COLOR
            self.border_color = GRAY_500_COLOR
            self.text_color = GREEN_100_COLOR

