import pygame

class RenderSystem:

    # LayeredUpdates organize sprites in layers
    render_group = pygame.sprite.LayeredUpdates()
    main_screen_surface = None
    main_camera = None

    def __init__(self):
       pass

    @classmethod
    def initialization(cls, screen):
        cls.main_screen_surface = screen
        cls.main_camera = None

    @classmethod
    def set_camera(cls, camera):
        cls.main_camera = camera

    def add_sprite(self, sprite, layer=0):
        # Adding sprite and the layer sprite to system of renderizing group
        sprite._layer = layer
        self.render_group.add(sprite)

    # Use the render function when you want to clear the screen
    def render(self):
        if not self.main_camera:
            return
    
        # Drawning sprites
        for sprite in self.render_group:
            # Catching the posttion by the camera
            screen_pos = self.main_camera.apply(sprite.rect)
            # Draw the sprite image in that position
            self.main_screen_surface.blit(sprite.image, screen_pos)
    
    def update(self):
        pygame.display.flip()
