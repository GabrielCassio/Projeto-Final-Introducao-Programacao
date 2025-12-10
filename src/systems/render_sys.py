import pygame
import src.systems.ui as UI
import src.objects.entity.obj_player as obj_player

class RenderSystem:
    def __init__(self, screen, camera):
        self.screen = screen
        self.camera = camera
        # LayeredUpdates organize sprites in layers
        self.render_group = pygame.sprite.LayeredUpdates()
        self.ui = UI.UI()
        self.player = obj_player.Player("Edísio", 300, 300, "src/sprites/psg.png")


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

            # Desenha a UI
            self.ui.display(self.player)

            # (Debug) Drawning the reactangle of sprite
            # pygame.draw.rect(self.screen, (255,0,0), screen_pos, 1)

        # 3. Atualiza o display final
        pygame.display.flip()