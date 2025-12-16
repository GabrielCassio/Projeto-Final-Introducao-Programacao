import pygame

class CameraSystem:
    def __init__(self, screen_width, screen_height, map_width, map_height):
        self.camera_rect = pygame.Rect(0, 0, screen_width, screen_height)
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.map_width = map_width
        self.map_height = map_height
        self.offset_float = pygame.math.Vector2(0, 0)

    def apply(self, entity):
        if hasattr(entity, 'rect'):
            rect = entity.rect
        else:
            rect = entity
        return rect.move(self.camera_rect.topleft[0] * -1, self.camera_rect.topleft[1] * -1)

    def update(self, target):
        # Target Coordinates
        target_x = target.rect.centerx - int(self.screen_width / 2)
        target_y = target.rect.centery - int(self.screen_height / 2)

        # Camera offsets
        self.offset_float.x += (target_x - self.offset_float.x) * 0.05
        self.offset_float.y += (target_y - self.offset_float.y) * 0.05

        self.offset_float.x = max(0, self.offset_float.x)
        self.offset_float.y = max(0, self.offset_float.y)
        self.offset_float.x = min(self.offset_float.x, self.map_width - self.screen_width)
        self.offset_float.y = min(self.offset_float.y, self.map_height - self.screen_height)

        self.camera_rect.x = int(self.offset_float.x)
        self.camera_rect.y = int(self.offset_float.y)