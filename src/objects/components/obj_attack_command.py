import pygame
from src.systems.render_sys import RenderSystem
from src.settings import *
from .obj_projectile import Projectile, MeleeHitbox

class AttackCommand:
    def __init__(self, player_entity):
        self.player = player_entity
        self.instance_render = RenderSystem()
    
    def execute_bow_attack(self):
        keys = pygame.key.get_pressed()
        now = pygame.time.get_ticks()
        
        if now < self.player.global_action_cooldown:
            return

        if keys[pygame.K_r] and self.player.bow_skill:
            if (now - self.player.last_shot > self.player.shot_cooldown):
                
                self.player.last_shot = now 
                
                self.player.global_action_cooldown = now + self.player.delay_after_action
                
                new_projectile = Projectile(self.player.rect.centerx, self.player.rect.centery, self.player.direction)
                self.instance_render.add_sprite(new_projectile, LAYER_OBJECTS)
    
    def execute_melee_attack(self):
            keys = pygame.key.get_pressed()
            mouse_buttons = pygame.mouse.get_pressed()
            now = pygame.time.get_ticks()

            if self.player.pending_second_hit:
                if now >= self.player.second_hit_timer:
                    hitbox = MeleeHitbox(self.player.rect, self.player.direction, self.player.frames_atk_2, style='sweep')
                    self.instance_render.add_sprite(hitbox, LAYER_OBJECTS)
                    self.player.pending_second_hit = False
                return 

            if now < self.player.global_action_cooldown:
                return

            if (keys[pygame.K_e] or mouse_buttons[0]):            
                self.player.locked_attack_direction = self.player.direction
                
                hitbox = MeleeHitbox(self.player.rect, self.player.locked_attack_direction, self.player.frames_atk_1, style='thrust')
                
                self.instance_render.add_sprite(hitbox, LAYER_OBJECTS)
                
                self.player.pending_second_hit = True
                self.player.second_hit_timer = now + self.player.time_atk_1
                
                total_lock = self.player.time_atk_1 + self.player.time_atk_2 + self.player.delay_after_action
                self.player.global_action_cooldown = now + total_lock