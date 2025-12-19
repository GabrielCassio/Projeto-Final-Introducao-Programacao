import pygame
from math import sin

class Entity(pygame.sprite.Sprite):
    def __init__(self, groups):
        super().__init__(groups)
        
        self.frame_index = 0
        self.animation_speed = 10
        self.direction = pygame.math.Vector2()
        
        # Placeholder para evitar erros se esquecermos de passar no filho
        self.obstacle_sprites = None 

    def move(self, speed, dt):
        # 1. Normalizar vetor (impedir que diagonal seja mais rápida)
        if self.direction.magnitude() != 0:
            self.direction = self.direction.normalize()

        # 2. Criar posição flutuante (se não existir)
        # O Rect do Pygame só aceita inteiros, então precisamos dessa variável
        # para guardar posições como 100.5, 100.6, etc.
        if not hasattr(self, 'hitbox_pos'):
            self.hitbox_pos = pygame.math.Vector2(self.hitbox.topleft)

        # 3. Movimento Horizontal
        self.hitbox_pos.x += self.direction.x * speed * dt
        self.hitbox.x = round(self.hitbox_pos.x) 
        self.collision('horizontal')

        # 4. Movimento Vertical
        self.hitbox_pos.y += self.direction.y * speed * dt
        self.hitbox.y = round(self.hitbox_pos.y) 
        self.collision('vertical')

        # 5. Atualiza o desenho (rect) para seguir a física (hitbox)
        self.rect.center = self.hitbox.center

    def collision(self, direction):
        if direction == 'horizontal':
            for sprite in self.obstacle_sprites:
                if sprite.hitbox.colliderect(self.hitbox):
                    if self.direction.x > 0: # Direita
                        self.hitbox.right = sprite.hitbox.left
                        self.hitbox_pos.x = self.hitbox.x # Trava a posição flutuante
                    if self.direction.x < 0: # Esquerda
                        self.hitbox.left = sprite.hitbox.right
                        self.hitbox_pos.x = self.hitbox.x

        if direction == 'vertical':
            for sprite in self.obstacle_sprites:
                if sprite.hitbox.colliderect(self.hitbox):
                    if self.direction.y > 0: # Baixo
                        self.hitbox.bottom = sprite.hitbox.top
                        self.hitbox_pos.y = self.hitbox.y
                    if self.direction.y < 0: # Cima
                        self.hitbox.top = sprite.hitbox.bottom
                        self.hitbox_pos.y = self.hitbox.y