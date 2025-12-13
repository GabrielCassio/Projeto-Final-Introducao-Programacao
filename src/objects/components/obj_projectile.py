import pygame
from src.settings import *

class Projectile(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        super().__init__()
        
        self.image = pygame.Surface((20, 10))
        self.image.fill((255, 255, 0)) 
        self.rect = self.image.get_rect()
        self.rect.center = (x, y) 
        
        self.direction = direction
        self.speed = 10 

    def update(self):
        if self.direction == 'UP':
            self.rect.y -= self.speed
        elif self.direction == 'DOWN':
            self.rect.y += self.speed
        elif self.direction == 'LEFT':
            self.rect.x -= self.speed
        elif self.direction == 'RIGHT':
            self.rect.x += self.speed
            
        if self.rect.x > WIDTH or self.rect.x < 0 or self.rect.y > HEIGHT or self.rect.y < 0:
            self.kill()

class MeleeHitbox(pygame.sprite.Sprite):
    def __init__(self, player_rect, direction, duration_frames, style='thrust'):
        super().__init__()
        
        if style == 'sweep':
            width = 100
            height = 50
        else: # thrust
            width = 50
            height = 100

        self.image = pygame.Surface((width, height))
        self.image.fill((255, 255, 0))
        self.rect = self.image.get_rect()
        
        if direction == 'UP': 
            self.rect.midbottom = player_rect.midtop
        elif direction == 'DOWN': 
            self.rect.midtop = player_rect.midbottom
        elif direction == 'LEFT': 
            self.rect.midright = player_rect.midleft
        elif direction == 'RIGHT': 
            self.rect.midleft = player_rect.midright
        else:
            self.rect.center = player_rect.center
            
        self.lifetime = duration_frames

    def update(self):
        self.lifetime -= 1
        if self.lifetime <= 0:
            self.kill()