import pygame
from src.settings import *

class Projectile(pygame.sprite.Sprite):
    '''
        
    '''
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
