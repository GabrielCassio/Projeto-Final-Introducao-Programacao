import pygame
from settings import *

class UI:
    def __init__(self):
        self.display_surface = pygame.display.get_surface()
        
        try:
            self.font = pygame.font.Font(UI_FONT, UI_FONT_SIZE)
        except:
            self.font = pygame.font.SysFont('arial', UI_FONT_SIZE)

        # Barras
        self.health_bar_rect = pygame.Rect(10, 10, HEALTH_BAR_WIDTH, BAR_HEIGHT)
        self.energy_bar_rect = pygame.Rect(10, 34, ENERGY_BAR_WIDTH, BAR_HEIGHT)

        # --- ÍCONE GRANDE ---
        # Tamanho da caixa do fundo (Quadrada)
        self.box_size = 90 
        
        try:
            full_path = './assets/graphics/player/attack/ranged/down/attack-ranged-front1.png'
            self.weapon_graphics = pygame.image.load(full_path).convert_alpha()
            # Escala para 80x80 (Um pouco menor que a caixa para ter margem)
            self.weapon_graphics = pygame.transform.scale(self.weapon_graphics, (80, 80))
        except:
            self.weapon_graphics = pygame.Surface((80, 80))
            self.weapon_graphics.fill('white')

        # Define onde o ícone vai ficar (Canto inferior esquerdo)
        # 20 pixels de margem da esquerda e de baixo
        self.weapon_rect = self.weapon_graphics.get_rect(bottomleft=(20, self.display_surface.get_height() - 20))


    def show_bar(self, current, max_amount, bg_rect, color):
        pygame.draw.rect(self.display_surface, UI_BG_COLOR, bg_rect)
        if max_amount > 0: ratio = current / max_amount
        else: ratio = 0
        current_width = bg_rect.width * ratio
        current_rect = bg_rect.copy()
        current_rect.width = int(current_width)
        pygame.draw.rect(self.display_surface, color, current_rect)
        
        border_color = UI_BORDER_COLOR if 'UI_BORDER_COLOR' in globals() else 'black'
        pygame.draw.rect(self.display_surface, border_color, bg_rect, 3)

    def display(self, player):
        # 1. Barras
        self.show_bar(player.health, player.max_health, self.health_bar_rect, HEALTH_COLOR)
        
        if player.can_dash:
            dash_val, dash_max = 1, 1
        else:
            time = pygame.time.get_ticks() - player.dash_time
            if time > player.dash_cooldown: time = player.dash_cooldown
            dash_val, dash_max = time, player.dash_cooldown
            
        self.show_bar(dash_val, dash_max, self.energy_bar_rect, ENERGY_COLOR)

        # 2. Ícone da Arma (Se tiver)
        if player.has_cracha:
            # Caixa de fundo
            bg_rect = pygame.Rect(0, 0, self.box_size, self.box_size)
            # Centraliza a caixa em relação ao ícone
            bg_rect.center = self.weapon_rect.center
            
            pygame.draw.rect(self.display_surface, UI_BG_COLOR, bg_rect)
            pygame.draw.rect(self.display_surface, UI_BORDER_COLOR, bg_rect, 3)
            
            # Desenha o ícone por cima
            self.display_surface.blit(self.weapon_graphics, self.weapon_rect)