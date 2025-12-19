import pygame 
import math 
from settings import *
from support import import_character_assets
from entity import Entity

class Player(Entity):
    def __init__(self, pos, groups, obstacle_sprites, create_attack, destroy_attack, create_cracha):
        super().__init__(groups)
        
        self.image = pygame.Surface((16, 16)) 
        self.image.fill('green') 
        self.rect = self.image.get_rect(topleft=pos)
        self.hitbox = self.rect.inflate(0, -6) 

        self.import_player_assets() 
        self.status = 'down'

        self.obstacle_sprites = obstacle_sprites
        self.speed = 150 
        
        # Stats
        self.max_health = 100 
        self.health = 100
        self.has_cracha = False 

        # Combate
        self.attacking = False
        self.attack_cooldown = 400 
        self.attack_time = 0
        self.attack_type = 'melee'
        
        # Dano no Player
        self.vulnerable = True
        self.hurt_time = 0
        self.invulnerability_duration = 500

        # Dash
        self.dashing = False
        self.dash_speed = 450 
        self.dash_duration = 200 
        self.dash_time = 0
        self.dash_cooldown = 1000 
        self.can_dash = True
        
        # Callbacks
        self.create_attack = create_attack
        self.destroy_attack = destroy_attack
        self.create_cracha = create_cracha

    def import_player_assets(self):
        path = './assets/graphics/player/idle_and_run/'
        self.animations = import_character_assets(path)

    def input(self):
        # --- CORREÇÃO AQUI ---
        # Removemos o "if not self.attacking:" que envolvia tudo.
        # Agora o movimento é lido sempre.
        keys = pygame.key.get_pressed()
        mouse_buttons = pygame.mouse.get_pressed() 

        # Movimento
        if keys[pygame.K_UP] or keys[pygame.K_w]: 
            self.direction.y = -1
            self.status = 'up'
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]: 
            self.direction.y = 1
            self.status = 'down'
        else: 
            self.direction.y = 0

        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: 
            self.direction.x = 1
            self.status = 'right'
        elif keys[pygame.K_LEFT] or keys[pygame.K_a]: 
            self.direction.x = -1
            self.status = 'left'
        else: 
            self.direction.x = 0

        # Ataque Espada (Aqui sim checamos se já não está atacando)
        if (mouse_buttons[0] or keys[pygame.K_r]) and not self.attacking and not self.dashing:
            self.attacking = True
            self.attack_type = 'melee'
            self.attack_time = pygame.time.get_ticks()
            self.create_attack()

        # Ataque Crachá
        if (mouse_buttons[2] or keys[pygame.K_t]) and not self.attacking and not self.dashing and self.has_cracha:
            self.attacking = True
            self.attack_type = 'ranged'
            self.attack_time = pygame.time.get_ticks()
            direction = self.status.split('_')[0]
            self.create_cracha(direction)

        # Dash
        if keys[pygame.K_SPACE] and self.can_dash and not self.dashing:
            self.dashing = True
            self.can_dash = False
            self.dash_time = pygame.time.get_ticks()

    def get_status(self):
        if self.direction.x == 0 and self.direction.y == 0:
            if not 'idle' in self.status and not 'attack' in self.status:
                self.status = self.status + '_idle'

        if self.attacking:
            self.status = self.status.replace('_ranged', '')
            self.status = self.status.replace('_attack', '')

    def cooldowns(self):
        current_time = pygame.time.get_ticks()
        
        if self.attacking:
            if current_time - self.attack_time >= self.attack_cooldown:
                self.attacking = False
                self.destroy_attack()

        if self.dashing:
            if current_time - self.dash_time >= self.dash_duration:
                self.dashing = False
        
        if not self.can_dash:
            if current_time - self.dash_time >= self.dash_cooldown:
                self.can_dash = True
        
        if not self.vulnerable:
            if current_time - self.hurt_time >= self.invulnerability_duration:
                self.vulnerable = True
                self.image.set_alpha(255) 

    def animate(self, dt):
        if self.status not in self.animations:
            clean_status = self.status.split('_')[0]
            if clean_status in self.animations: self.status = clean_status
            else: return 

        current_animation = self.animations[self.status]
        if not current_animation: return 

        self.frame_index += self.animation_speed * dt
        if self.frame_index >= len(current_animation):
            self.frame_index = 0

        frame = int(self.frame_index)
        self.image = current_animation[frame]
        self.rect.center = self.hitbox.center

        if not self.vulnerable:
            alpha = self.wave_value()
            self.image.set_alpha(alpha)
        else:
            self.image.set_alpha(255)
            
    def wave_value(self):
        value = math.sin(pygame.time.get_ticks())
        if value >= 0: return 255
        else: return 0

    def update(self, dt):
        self.input()
        self.cooldowns()
        self.get_status()
        self.animate(dt)
        
        current_speed = self.speed
        
        # --- AJUSTE DE VELOCIDADE DURANTE ATAQUE ---
        if self.attacking:
            # Reduz a velocidade para 40% durante o ataque.
            # Você pode se mover, mas devagar. Fica com uma sensação melhor de "peso".
            current_speed = self.speed * 0.7
        
        if self.dashing:
            current_speed = self.dash_speed
            GhostSprite(self.rect.center, self.image, self.groups()[0])

        self.move(current_speed, dt)

class GhostSprite(pygame.sprite.Sprite):
    def __init__(self, pos, original_image, groups):
        super().__init__(groups)
        self.image = original_image.copy()
        self.rect = self.image.get_rect(center=pos)
        self.alpha = 255
        self.image.set_alpha(self.alpha)
        self.fade_speed = 15 

    def update(self, dt=None):
        self.alpha -= self.fade_speed
        if self.alpha <= 0: self.kill() 
        else: self.image.set_alpha(self.alpha)