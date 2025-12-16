import pygame
# Importing Entity
from src.objects.button.obj_entity_button import EntityButton
# importing settings
from src.settings import *

class Button(EntityButton):
    '''
        Description:\n
        Create a custom button.

        Paramters:\n
        text (str): placeholder text inner the button\n
        x (int): x coordinate to the button position\n
        y (int): y coordinate to the button position\n
        w (int): button width\n
        h (int): button heigth\n
        variant (str): name of the button color\n
        action (bool): action effect when clicked it
    '''
    def __init__(self, text, x, y, w, h, variant = 'primary', action = None):
        super().__init__(text, x, y, w, h, variant, action)
    
    def draw(self, surface):

        # Draw variables
        offset_y = 0
        current_background_color = 0

        # Hover effect
        if (self.hovered): offset_y = -4
        else: offset_y = 0

        # Color condition on click
        if ((self.hovered) and (self.variant == "primary")):  current_background_color = GREEN_800_COLOR
        else: current_background_color = self.background_color
        
        # Solid shadow
        shadow_rect = pygame.Rect(self.rect.x + 4, self.rect.y + 4, self.rect.width, self.rect.height)
        pygame.draw.rect(surface, self.border_color, shadow_rect)
        
        # Button shape
        btn_rect = pygame.Rect(self.rect.x, self.rect.y + offset_y, self.rect.width, self.rect.height)
        pygame.draw.rect(surface, current_background_color, btn_rect)
        pygame.draw.rect(surface, self.border_color, btn_rect, 4) 
        
       
        corners = [
            (btn_rect.topleft, (4, 4)), 
            (btn_rect.topright, (-4, 4)),
            (btn_rect.bottomleft, (4, -4)),
            (btn_rect.bottomright, (-4, -4))
        ]
        
        # Texto
        text_surf = FONT_BUTTON.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=btn_rect.center)
        surface.blit(text_surf, text_rect)