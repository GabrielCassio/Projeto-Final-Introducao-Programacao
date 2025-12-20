import pygame

class SpriteSheet():
    def __init__(self, image):
        self.sheet = image

    def get_image(self, frame, width, height, scale, colour):
        """
        frame: O índice do bonequinho (0, 1, 2...)
        width: Largura de UM bonequinho
        height: Altura de UM bonequinho
        scale: Tamanho final (1 = original, 2 = dobro)
        colour: A cor do fundo para remover (Chroma Key) - geralmente preto (0,0,0)
        """
        image = pygame.Surface((width, height)).convert_alpha()
        
        image.blit(self.sheet, (0, 0), ((frame * width), 0, width, height))
        
        image = pygame.transform.scale(image, (width * scale, height * scale))
        
        image.set_colorkey(colour)

        return image
    