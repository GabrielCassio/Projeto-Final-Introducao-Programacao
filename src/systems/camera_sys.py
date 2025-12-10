# src/systems/camera.py
import pygame

class Camera:
    def __init__(self, width, height):
        self.camera_rect = pygame.Rect(0, 0, width, height)
        self.world_width = width
        self.world_height = height

    def apply(self, entity_rect):
        return entity_rect.move(self.camera_rect.topleft[0] * -1, self.camera_rect.topleft[1] * -1)

    def update(self, target_rect):

        x = -target_rect.centerx + int(self.camera_rect.width / 2)
        y = -target_rect.centery + int(self.camera_rect.height / 2)


        self.camera_rect.topleft = (x * -1, y * -1)