import pygame

class RenderSystem:
    def __init__(self, screen, camera):
        self.screen = screen
        self.camera = camera
        # LayeredUpdates organize sprites in layers
        self.render_group = pygame.sprite.LayeredUpdates()

    def add_sprite(self, sprite, layer=0):
        # Adding sprite and the layer sprite to system of renderizing group
        sprite._layer = layer
        self.render_group.add(sprite)

    def update(self):
        # Clear the screen with backgroundColor white
        self.screen.fill((255, 255, 255))

        # Drawning sprites
        for sprite in self.render_group:
            # Pega a posição na tela baseada na câmera
            screen_pos = self.camera.apply(sprite.rect)
            # Desenha a imagem do sprite naquela posição
            self.screen.blit(sprite.image, screen_pos)

            # (Debug) Drawning the reactangle of sprite
            # pygame.draw.rect(self.screen, (255,0,0), screen_pos, 1)

        # 3. Atualiza o display final
        pygame.display.flip()