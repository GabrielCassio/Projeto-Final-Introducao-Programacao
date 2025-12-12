# Eu não consegui aprender modularização o suficiente ainda, então deixei ele aqui, amanhã, vou estudar, e fazer as alterações no escopo do codigo... 
# Se estiver precisando com urgencia, apresenta isso.

import sys
import pygame

pygame.init()
WIDTH, HEIGHT = 1200, 800

# Classes
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
        if self.direction == 'up':
            self.rect.y -= self.speed
        elif self.direction == 'down':
            self.rect.y += self.speed
        elif self.direction == 'left':
            self.rect.x -= self.speed
        elif self.direction == 'right':
            self.rect.x += self.speed
            
        if self.rect.x > WIDTH or self.rect.x < 0 or self.rect.y > HEIGHT or self.rect.y < 0:
            self.kill()

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((50, 50))
        self.image.fill((128, 128, 128))
        self.rect = self.image.get_rect()
        self.rect.center = (WIDTH // 2, HEIGHT // 2)

        # Status
        self.bow_skill = True
        self.player_speed = 5 
        
        self.self_direction = 'right' 
        self.last_dash = 0
        self.dash_cooldown = 1000
        
        self.last_shot = 0
        self.shot_cooldown = 400 # Meio segundo entre flechas

    def update(self):
        self.movement()
        self.attack() # Chamamos o ataque aqui para checar a tecla todo frame

    def movement(self):
        keys = pygame.key.get_pressed()
        
        if keys[pygame.K_w]:
            self.rect.y -= self.player_speed
            self.self_direction = 'up'
        if keys[pygame.K_s]:
            self.rect.y += self.player_speed
            self.self_direction = 'down'
        if keys[pygame.K_a]:
            self.rect.x -= self.player_speed
            self.self_direction = 'left'
        if keys[pygame.K_d]:
            self.rect.x += self.player_speed
            self.self_direction = 'right'

        # Dash (Simplificado para o exemplo)
        if keys[pygame.K_SPACE]:
            now = pygame.time.get_ticks()
            if now - self.last_dash > self.dash_cooldown:
                self.last_dash = now
                if self.self_direction == 'up': 
                    self.rect.y -= 100
                elif self.self_direction == 'down': 
                    self.rect.y += 100
                elif self.self_direction == 'left': 
                    self.rect.x -= 100
                elif self.self_direction == 'right': 
                    self.rect.x += 100

    def attack(self):
        keys = pygame.key.get_pressed()
        now = pygame.time.get_ticks()

        if keys[pygame.K_r] and self.bow_skill:
            if now - self.last_shot > self.shot_cooldown:
                self.last_shot = now
                
                new_projectile = Projectile(self.rect.centerx, self.rect.centery, self.self_direction)
                
                all_assets.add(new_projectile)
                projectiles_group.add(new_projectile)

screen_display = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock() # Importante para controlar FPS


all_assets = pygame.sprite.Group()
projectiles_group = pygame.sprite.Group() 

# Criar Jogador
edipo = Player()
all_assets.add(edipo)

running = True 

while running:
    clock.tick(60) 
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen_display.fill((0, 0, 0))

    all_assets.update()
    all_assets.draw(screen_display)

    pygame.display.flip()

pygame.quit()
