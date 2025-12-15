import pygame
# Importing Entity
from src.objects.button.obj_entity_button import EntityButton


class ButtonCommand:
    def __init__(self, button: EntityButton):
        self.button = button

    def execute(self, mouse_pos, event_type):
        if self.rect.collidepoint(mouse_pos):
            self.hovered = True
            if event_type == pygame.MOUSEBUTTONDOWN:
                if self.action:
                    self.action()
        else:
            self.hovered = False