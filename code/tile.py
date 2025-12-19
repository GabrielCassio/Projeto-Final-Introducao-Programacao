# tile.py
import pygame 
import math
from settings import *
import random

class Wall(pygame.sprite.Sprite):
    def __init__(self, pos, groups):
        super().__init__(groups)
        self.rect = pygame.Rect(pos, (TILESIZE, TILESIZE))
        self.hitbox = self.rect.inflate(0, -6)

# tile.py

class Collectible(pygame.sprite.Sprite):
    def __init__(self, pos, groups, item_type):
        super().__init__(groups)
        self.item_type = item_type
        
        self.image = pygame.Surface((24, 24), pygame.SRCALPHA)
        
        if self.item_type == 'cracha':
            self.image.fill('gold') 
            
        elif self.item_type == 'heart':
            self.image.fill('red')
            pygame.draw.rect(self.image, 'white', (8, 4, 8, 16))
            pygame.draw.rect(self.image, 'white', (4, 8, 16, 8))
            
        elif 'coin' in self.item_type:
            if self.item_type == 'coin': color, border = 'gold', 'orange'
            elif self.item_type == 'coin_red': color, border = '#ff4444', '#880000'
            elif self.item_type == 'coin_green': color, border = '#44ff44', '#008800'
            
            pygame.draw.circle(self.image, color, (12,12), 10)
            pygame.draw.circle(self.image, border, (12,12), 10, 2)
            pygame.draw.line(self.image, border, (12, 6), (12, 18), 2)
        
        # --- NOVO: VISUAL DA ALMA ---
        elif self.item_type == 'soul':
            # Chama de "fogo azul"
            # Base
            pygame.draw.circle(self.image, 'cyan', (12, 14), 8)
            # Ponta da chama
            pygame.draw.polygon(self.image, 'cyan', [(4, 14), (20, 14), (12, 0)])
            # Centro branco (brilho)
            pygame.draw.circle(self.image, 'white', (12, 14), 4)

        self.rect = self.image.get_rect(center=pos)
        self.hitbox = self.rect.inflate(-10, -10)
        self.start_y = self.rect.centery
        self.float_speed = 0.005
        self.float_range = 5 
    
    def update(self, dt):
        current_time = pygame.time.get_ticks()
        offset = math.sin(current_time * self.float_speed) * self.float_range
        self.rect.centery = self.start_y + offset

class FireBarrier(pygame.sprite.Sprite):
    def __init__(self, pos, groups):
        super().__init__(groups)
        
        # --- CONFIGURAÇÃO DE TAMANHO ---
        self.tiles_wide = 5 # Quantos tiles de largura?
        self.pixel_width = TILESIZE * self.tiles_wide # Ex: 64 * 5 = 320 pixels
        
        # Cria a superfície Larga (Largura x Altura normal)
        self.image = pygame.Surface((self.pixel_width, TILESIZE))
        self.image.fill('red') 
        
        self.rect = self.image.get_rect(topleft=pos)
        
        # Hitbox ocupa toda a largura (Player não passa em lugar nenhum)
        self.hitbox = self.rect.inflate(0, 0)
        
        self.frame_time = 0

    def update(self, dt):
        # ANIMAÇÃO DE FOGO
        current_time = pygame.time.get_ticks()
        if current_time - self.frame_time > 50:
            self.frame_time = current_time
            
            # Limpa o fundo
            self.image.fill('#5e0e0e') 
            
            # --- LOOP AJUSTADO ---
            # Agora ele vai de 0 até self.pixel_width (largura total)
            # Desenhando chamas lado a lado
            for x in range(0, self.pixel_width, 8):
                
                # Altura aleatória da chama
                height = random.randint(10, TILESIZE)
                
                # Cores quentes aleatórias
                color = random.choice(['#ff3333', '#ff8833', '#ffff33'])
                
                # Desenha o retangulo da chama
                rect_flame = pygame.Rect(x, TILESIZE - height, 8, height)
                pygame.draw.rect(self.image, color, rect_flame)