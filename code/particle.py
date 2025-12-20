import pygame
import random
from fonts import carregar_fonte_padrao

class Particle(pygame.sprite.Sprite):
    def __init__(self, pos, groups, color='red', size=4):
        super().__init__(groups)
        
        self.image = pygame.Surface((size, size))
        self.image.fill(color)
        self.rect = self.image.get_rect(center=pos)

        self.direction = pygame.math.Vector2(random.uniform(-1, 1), random.uniform(-1, 1))
        if self.direction.magnitude() != 0:
            self.direction = self.direction.normalize()
            
        self.speed = random.randint(100, 250) 
        self.pos = pygame.math.Vector2(self.rect.center)

        self.start_time = pygame.time.get_ticks()
        self.life_duration = random.randint(200, 400) 
        
        self.original_size = size
        self.current_size = size

    def update(self, dt):
        self.pos += self.direction * self.speed * dt
        self.rect.center = self.pos

        current_time = pygame.time.get_ticks()
        time_passed = current_time - self.start_time

        if time_passed >= self.life_duration:
            self.kill()
        else:
            ratio = 1 - (time_passed / self.life_duration)
            new_size = int(self.original_size * ratio)
            if new_size > 0:
                self.image = pygame.transform.scale(self.image, (new_size, new_size))

class FloatingText(pygame.sprite.Sprite):
    def __init__(self, pos, text, groups, color='white', size=20):
        super().__init__(groups)
        
        self.font = carregar_fonte_padrao(size)
            
        self.image = self.font.render(str(text), True, color)
        self.rect = self.image.get_rect(center=pos)
        
        self.pos = pygame.math.Vector2(self.rect.center)
        self.direction = pygame.math.Vector2(0, -1) 
        self.speed = 30 
        self.alpha = 255 
        self.fade_speed = 4 
        
    def update(self, dt):
        self.pos += self.direction * self.speed * dt
        self.rect.center = self.pos
        
        self.alpha -= self.fade_speed
        if self.alpha <= 0:
            self.kill()
        else:
            self.image.set_alpha(self.alpha)