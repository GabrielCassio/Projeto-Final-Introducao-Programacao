# ui.py
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

        # --- ÍCONE GRANDE (ARMA) ---
        self.box_size = 90 
        try:
            full_path = './assets/graphics/player/attack/ranged/down/attack-ranged-front1.png'
            self.weapon_graphics = pygame.image.load(full_path).convert_alpha()
            self.weapon_graphics = pygame.transform.scale(self.weapon_graphics, (80, 80))
        except:
            self.weapon_graphics = pygame.Surface((80, 80))
            self.weapon_graphics.fill('white')

        # Define onde o ícone vai ficar (Canto inferior esquerdo)
        self.weapon_rect = self.weapon_graphics.get_rect(bottomleft=(20, self.display_surface.get_height() - 20))

    def show_bar(self, current, max_amount, bg_rect, color):
        # Fundo da barra
        pygame.draw.rect(self.display_surface, UI_BG_COLOR, bg_rect)

        # Calculo da largura atual
        if max_amount > 0: ratio = current / max_amount
        else: ratio = 0
        
        current_width = bg_rect.width * ratio
        current_rect = bg_rect.copy()
        current_rect.width = int(current_width)
        
        # Barra colorida
        pygame.draw.rect(self.display_surface, color, current_rect)
        
        # Borda
        border_color = UI_BORDER_COLOR if 'UI_BORDER_COLOR' in globals() else 'black'
        pygame.draw.rect(self.display_surface, border_color, bg_rect, 3)

    # --- NOVO MÉTODO: EXIBIR MOEDAS ---
    def show_coins(self, amount):
        # 1. Renderiza o texto (Tenta pegar TEXT_COLOR do settings, se não tiver usa preto)
        color = TEXT_COLOR if 'TEXT_COLOR' in globals() else '#333333'
        text_surf = self.font.render(str(int(amount)), False, color)
        
        # Pega o retângulo do texto para calcular tamanho da caixa
        text_rect = text_surf.get_rect(bottomright = (self.display_surface.get_width() - 20, self.display_surface.get_height() - 20))

        # 2. Caixa de Fundo (Ajusta largura baseada no texto + espaço pro ícone)
        box_width = text_rect.width + 50 
        box_height = text_rect.height + 20
        
        bg_rect = pygame.Rect(0, 0, box_width, box_height)
        bg_rect.bottomright = (self.display_surface.get_width() - 20, self.display_surface.get_height() - 20)

        # Desenha Fundo e Borda
        pygame.draw.rect(self.display_surface, UI_BG_COLOR, bg_rect)
        pygame.draw.rect(self.display_surface, UI_BORDER_COLOR, bg_rect, 3)

        # 3. Desenha o Texto
        text_rect.centery = bg_rect.centery
        text_rect.right = bg_rect.right - 10
        self.display_surface.blit(text_surf, text_rect)

        # 4. Desenha Ícone da Moeda (Esquerda do texto)
        coin_x = bg_rect.left + 20
        coin_y = bg_rect.centery
        pygame.draw.circle(self.display_surface, 'gold', (coin_x, coin_y), 10)
        pygame.draw.circle(self.display_surface, 'orange', (coin_x, coin_y), 10, 2) # Contorno da moeda

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
            bg_rect.center = self.weapon_rect.center
            
            pygame.draw.rect(self.display_surface, UI_BG_COLOR, bg_rect)
            pygame.draw.rect(self.display_surface, UI_BORDER_COLOR, bg_rect, 3)
            
            # Desenha o ícone por cima
            self.display_surface.blit(self.weapon_graphics, self.weapon_rect)
        
        # 3. Moedas (NOVO)
        self.show_coins(player.coins)