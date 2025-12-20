import pygame
from math import sin

class Entity(pygame.sprite.Sprite):
    def __init__(self, groups):
        super().__init__(groups)
        
        self.frame_index = 0
        self.animation_speed = 10
        self.direction = pygame.math.Vector2()
        
        self.obstacle_sprites = None 

    def move(self, speed, dt):
        if self.direction.magnitude() != 0:
            self.direction = self.direction.normalize()

        if not hasattr(self, 'hitbox_pos'):
            self.hitbox_pos = pygame.math.Vector2(self.hitbox.topleft)

        self.hitbox_pos.x += self.direction.x * speed * dt
        self.hitbox.x = round(self.hitbox_pos.x) 
        self.collision('horizontal')

        self.hitbox_pos.y += self.direction.y * speed * dt
        self.hitbox.y = round(self.hitbox_pos.y) 
        self.collision('vertical')

        self.rect.center = self.hitbox.center

    def collision(self, direction):
        if direction == 'horizontal':
            for sprite in self.obstacle_sprites:
                if sprite.hitbox.colliderect(self.hitbox):
                    if self.direction.x > 0: 
                        self.hitbox.right = sprite.hitbox.left
                        self.hitbox_pos.x = self.hitbox.x 
                    if self.direction.x < 0: 
                        self.hitbox.left = sprite.hitbox.right
                        self.hitbox_pos.x = self.hitbox.x

        if direction == 'vertical':
            for sprite in self.obstacle_sprites:
                if sprite.hitbox.colliderect(self.hitbox):
                    if self.direction.y > 0: 
                        self.hitbox.bottom = sprite.hitbox.top
                        self.hitbox_pos.y = self.hitbox.y
                    if self.direction.y < 0:
                        self.hitbox.top = sprite.hitbox.bottom
                        self.hitbox_pos.y = self.hitbox.y