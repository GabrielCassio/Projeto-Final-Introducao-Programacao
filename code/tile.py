# tile.py
import pygame 
import math
from settings import *

class Wall(pygame.sprite.Sprite):
    def __init__(self, pos, groups):
        super().__init__(groups)
        self.rect = pygame.Rect(pos, (TILESIZE, TILESIZE))
        self.hitbox = self.rect.inflate(0, -6)

class Collectible(pygame.sprite.Sprite):
    def __init__(self, pos, groups, item_type):
        super().__init__(groups)
        self.item_type = item_type
        
        # Cria a superfície base
        self.image = pygame.Surface((24, 24), pygame.SRCALPHA) # SRCALPHA deixa o fundo transparente
        
        if self.item_type == 'cracha':
            self.image.fill('gold') 
            
        elif self.item_type == 'heart':
            # Coração (Vermelho com cruz branca)
            self.image.fill('red')
            pygame.draw.rect(self.image, 'white', (8, 4, 8, 16))
            pygame.draw.rect(self.image, 'white', (4, 8, 16, 8))
            
        # --- NOVAS VARIAÇÕES DE MOEDA ---
        elif 'coin' in self.item_type:
            # Define a cor baseada no tipo
            if self.item_type == 'coin': 
                color = 'gold'       # Valor 1
                border = 'orange'
            elif self.item_type == 'coin_red': 
                color = '#ff4444'    # Valor 5 (Vermelho claro)
                border = '#880000'
            elif self.item_type == 'coin_green': 
                color = '#44ff44'    # Valor 10 (Verde claro)
                border = '#008800'
            
            # Desenha a moeda circular
            pygame.draw.circle(self.image, color, (12,12), 10)
            pygame.draw.circle(self.image, border, (12,12), 10, 2)
            # Desenha um cifrão ($) simples no meio
            pygame.draw.line(self.image, border, (12, 6), (12, 18), 2)
            
        self.rect = self.image.get_rect(center=pos)
        self.hitbox = self.rect.inflate(-10, -10)
        self.start_y = self.rect.centery
        self.float_speed = 0.005
        self.float_range = 5 
    
    def update(self, dt):
        # Efeito de flutuar
        current_time = pygame.time.get_ticks()
        offset = math.sin(current_time * self.float_speed) * self.float_range
        self.rect.centery = self.start_y + offset