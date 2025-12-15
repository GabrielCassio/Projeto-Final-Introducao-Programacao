import pygame
'''import src.systems.ui_sys as UI
import src.objects.entity.obj_player as obj_player'''

class RenderSystem:

    # LayeredUpdates organize sprites in layers
    render_group = pygame.sprite.LayeredUpdates()
    main_screen_surface = None
    main_camera = None

    def __init__(self):
       pass

    @classmethod
    def initialization(cls, screen, camera):
        cls.main_screen_surface = screen
        cls.main_camera = camera

    def add_sprite(self, sprite, layer=0):
        # Adding sprite and the layer sprite to system of renderizing group
        sprite._layer = layer
        self.render_group.add(sprite)

    # Use the render function when you want to clear the screen
    def render(self):
        # Clear the screen with backgroundColor white
        self.main_screen_surface.fill((255, 255, 255))

        # Drawning sprites
        for sprite in self.render_group:
            # Pega a posição na tela baseada na câmera
            screen_pos = self.main_camera.apply(sprite.rect)
            # Desenha a imagem do sprite naquela posição
            self.main_screen_surface.blit(sprite.image, screen_pos)
    
    def update(self):
        pygame.display.flip()
