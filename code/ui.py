# ui.py
import pygame
from settings import *
from fonts import carregar_fonte_padrao

class UI:
    def __init__(self):
        self.display_surface = pygame.display.get_surface()
        
        tamanho = UI_FONT_SIZE if 'UI_FONT_SIZE' in globals() else 18
        self.font = carregar_fonte_padrao(tamanho)

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

    def show_counter(self, amount, icon_color, offset_y, bg_color='UI_BG_COLOR'):
        # 0. Configura cores (Evita erro se não existirem no settings)
        text_color = TEXT_COLOR if 'TEXT_COLOR' in globals() else '#333333'
        bg_col = UI_BG_COLOR 
        border_col = UI_BORDER_COLOR if 'UI_BORDER_COLOR' in globals() else 'black'

        # 1. Cria a imagem do TEXTO
        text_surf = self.font.render(str(int(amount)), False, text_color)
        
        # 2. Define a posição (Calcula o retângulo do texto com o OFFSET)
        text_rect = text_surf.get_rect(bottomright = (
            self.display_surface.get_width() - 20, 
            self.display_surface.get_height() - 20 - offset_y 
        ))

        # 3. Cria a CAIXA DE FUNDO
        box_width = text_rect.width + 50 
        box_height = text_rect.height + 20
        
        bg_rect = pygame.Rect(0, 0, box_width, box_height)
        bg_rect.bottomright = text_rect.bottomright
        bg_rect.y += 0 # Ajuste fino se necessário

        # --- AQUI ESTAVA FALTANDO A PARTE DE DESENHAR ---

        # 4. Desenha Fundo e Borda
        pygame.draw.rect(self.display_surface, bg_col, bg_rect)
        pygame.draw.rect(self.display_surface, border_col, bg_rect, 3)

        # 5. Desenha o Texto
        text_rect.centery = bg_rect.centery
        text_rect.right = bg_rect.right - 10
        self.display_surface.blit(text_surf, text_rect)

        # 6. Desenha o Ícone
        icon_x = bg_rect.left + 20
        icon_y = bg_rect.centery
        
        # Desenha círculo base
        pygame.draw.circle(self.display_surface, icon_color, (icon_x, icon_y), 10)
        pygame.draw.circle(self.display_surface, 'white', (icon_x, icon_y), 10, 2)
        
        # Se for alma (cyan), desenha o brilho no meio
        if icon_color == 'cyan': 
             pygame.draw.circle(self.display_surface, 'white', (icon_x, icon_y), 4)

    def display(self, player):
        # 1. Barras (igual antes)
        self.show_bar(player.health, player.max_health, self.health_bar_rect, HEALTH_COLOR)
        
        if player.can_dash: dash_val, dash_max = 1, 1
        else:
            time = pygame.time.get_ticks() - player.dash_time
            if time > player.dash_cooldown: time = player.dash_cooldown
            dash_val, dash_max = time, player.dash_cooldown
        self.show_bar(dash_val, dash_max, self.energy_bar_rect, ENERGY_COLOR)

        # 2. Arma (igual antes)
        if player.has_cracha:
            bg_rect = pygame.Rect(0, 0, self.box_size, self.box_size)
            bg_rect.center = self.weapon_rect.center
            pygame.draw.rect(self.display_surface, UI_BG_COLOR, bg_rect)
            pygame.draw.rect(self.display_surface, UI_BORDER_COLOR, bg_rect, 3)
            self.display_surface.blit(self.weapon_graphics, self.weapon_rect)
        
        # 3. Contadores (Moedas embaixo, Almas em cima)
        self.show_counter(player.coins, 'gold', 0)    # Offset 0 (embaixo)
        self.show_counter(player.souls, 'cyan', 60)   # Offset 60 (em cima da moeda)