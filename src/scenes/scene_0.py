import pygame
# Importing scene entity
from src.scenes.scene_entity import Scene

# Importing settings
from src.settings import *

class GameHome(Scene):
    '''
        
    '''
    def __init__(self, scene_system):
        super().__init__(scene_system)
        self.display_surface = pygame.display.get_surface()

    def draw(self):
        pass

    def draw_background(self):
        
        # Drawning the Background
        self.display_surface.fill(GRAY_800_COLOR)
        FONT_TITLE = pygame.font.Font(TITLES_FONT, 56)
        FONT_UPPER_TITLE = pygame.font.Font(TITLES_FONT, 32)
        FONT_TEXT = pygame.font.Font(TITLES_FONT, 16)

        # Renderize the upper title
        upper_title_surf = FONT_UPPER_TITLE.render("CIN - Centro de Informática", True, RED_400_COLOR)
        self.display_surface.blit(upper_title_surf, upper_title_surf.get_rect(center=(WIDTH//2, 100)))
        
        # Renderize game title
        title_text_surf = FONT_TITLE.render("Édiso: The legend of the rescue", True, RED_500_COLOR)
        self.display_surface.blit(title_text_surf, title_text_surf.get_rect(center=(WIDTH//2, 260)))
        
        all_logs = [
            "Desenvolvido por:"
            "Ana Clara de Oliveira Cavalcante",
            "Bernardo Belfort Leão",
            "Edisio Uchoa Calvacanti Neto",
            "Francisco Faustino de Souza Neto",
            "Gabriel Cássio Gomes Cileiro",
            "Victor Lemos de Freitas"
        ]

        # Renderize logs in the end of the screen
        y_log = HEIGHT - 200
        for log in all_logs:
            log_surf = FONT_TEXT.render(f"> {log}", True, GREEN_800_COLOR)
            self.display_surface.blit(log_surf, (50, y_log))
            y_log += 25
        

    def handle_input(self):
        pass

    def update(self):
        self.handle_input()
        self.draw_background()


    