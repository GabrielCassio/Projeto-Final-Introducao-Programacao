import pygame
import math
import random  
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

        self.max_health = 200
        self.health = 200
        self.coins = 0
        self.souls = 25
        self.has_cracha = False

        self.crit_chance = 0.20
        self.crit_mult = 2
        self.base_melee_damage = 10

        self.base_ranged_damage = 10
        self.ranged_always_crit = True

        self.attacking = False
        self.attack_type = 'melee'
        self.attack_time = 0          
        self.attack_duration = 0       
        self.last_attack_time = -10000 


        self.melee_attack_slow_factor = 0.55
        self.ranged_attack_slow_factor = 0.70

        self.attack_cooldown_melee = 700
        self.attack_duration_melee = 260

        self.attack_cooldown_ranged = 700
        self.attack_duration_ranged = 260

        self.max_badge = 3
        self.badge_ammo = 3
        self.badge_reload_ms = 2000
        self.last_badge_reload = pygame.time.get_ticks()

        self.vulnerable = True
        self.hurt_time = 0
        self.invulnerability_duration = 800  

        self.dashing = False
        self.dash_speed = 450
        self.dash_duration = 160   
        self.dash_time = 0
        self.dash_cooldown = 1000
        self.can_dash = True

        self.create_attack = create_attack
        self.destroy_attack = destroy_attack
        self.create_cracha = create_cracha

    def import_player_assets(self):
        path = './assets/graphics/player/idle_and_run/'
        self.animations = import_character_assets(path)

    def roll_damage(self, base_damage: int) -> tuple[int, bool]:
        is_crit = (random.random() < self.crit_chance)
        dmg = int(base_damage * (self.crit_mult if is_crit else 1))
        return dmg, is_crit

    def _can_attack(self, now: int, atk_type: str) -> bool:
        cd = self.attack_cooldown_melee if atk_type == 'melee' else self.attack_cooldown_ranged
        return (now - self.last_attack_time) >= cd

    def recharge_badge(self):
        if not self.has_cracha:
            return
        if self.badge_ammo >= self.max_badge:
            return

        now = pygame.time.get_ticks()
        if now - self.last_badge_reload >= self.badge_reload_ms:
            self.badge_ammo += 1
            self.last_badge_reload = now

    def input(self):
        keys = pygame.key.get_pressed()
        mouse_buttons = pygame.mouse.get_pressed()
        now = pygame.time.get_ticks()

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

        if (mouse_buttons[0] or keys[pygame.K_r]) and (not self.attacking) and (not self.dashing) and self._can_attack(now, 'melee'):
            self.attacking = True
            self.attack_type = 'melee'
            self.attack_time = now
            self.attack_duration = self.attack_duration_melee
            self.last_attack_time = now
            self.create_attack()

        if (mouse_buttons[2] or keys[pygame.K_t]) and (not self.attacking) and (not self.dashing) and self.has_cracha:
            if self.badge_ammo > 0 and self._can_attack(now, 'ranged'):
                self.badge_ammo -= 1
                self.last_badge_reload = now 

                self.attacking = True
                self.attack_type = 'ranged'
                self.attack_time = now
                self.attack_duration = self.attack_duration_ranged
                self.last_attack_time = now

                direction = self.status.split('_')[0]
                self.create_cracha(direction)

        if keys[pygame.K_SPACE] and self.can_dash and (not self.dashing):
            self.dashing = True
            self.can_dash = False
            self.dash_time = now

    def get_status(self):
        if self.direction.x == 0 and self.direction.y == 0:
            if 'idle' not in self.status and 'attack' not in self.status:
                self.status = self.status + '_idle'

        if self.attacking:
            self.status = self.status.replace('_ranged', '')
            self.status = self.status.replace('_attack', '')

    def cooldowns(self):
        current_time = pygame.time.get_ticks()

        if self.attacking:
            if current_time - self.attack_time >= self.attack_duration:
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
            if clean_status in self.animations:
                self.status = clean_status
            else:
                return

        current_animation = self.animations[self.status]
        if not current_animation:
            return

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
        return 255 if value >= 0 else 0

    def heal(self, amount):
        if self.health < self.max_health:
            self.health += amount
            if self.health > self.max_health:
                self.health = self.max_health
            print(f"Curado! Vida atual: {self.health}")

    def update(self, dt):
        self.recharge_badge() 
        self.input()
        self.cooldowns()
        self.get_status()
        self.animate(dt)

        current_speed = self.speed

        if self.attacking:
            if self.attack_type == 'melee':
                current_speed = self.speed * self.melee_attack_slow_factor
            else:
                current_speed = self.speed * self.ranged_attack_slow_factor

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
        if self.alpha <= 0:
            self.kill()
        else:
            self.image.set_alpha(self.alpha)
