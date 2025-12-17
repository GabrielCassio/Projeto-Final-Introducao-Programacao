import pygame, os, random

# Importing Entities
from src.objects.character.obj_entity import Entity

# Importing Attacks
from src.objects.attacks.obj_melee_attack import PlayerMeleeSlash
from src.objects.attacks.obj_projectile_attack import BadgeProjectile

# Importing settings
from src.settings import *

class Player(Entity):

    def __init__(self, name: str, x: int, y: int, group_collision: dict) -> None: # , walls_group: pygame.sprite.Group
        # Initiate de Entity superclassto characters
        super().__init__(name, x, y, group_collision) # , walls_group

        # Sprite player loader by the Assets to player
        '''Before ------------------------------------------------------
        original_image = pygame.image.load(path_sprite).convert_alpha()

        # Initializing the sprite of player
        SCALE_FACTOR = 2.4 
        w, h = original_image.get_size()
        self.image = pygame.transform.scale(original_image, (int(w * SCALE_FACTOR), int(h * SCALE_FACTOR)))
        '''
        
        # Sprite player loader by the Assets to player
        # After -------------------------------------------------------

        # Declaring instance variable to group_collision
        self.group_collision = group_collision
        # Dictionary of animations by player in different directions
        self.animations = {
            # Static animation
            "idle": {"up": [], "down": [], "left": [], "right": []},
            # Running animation
            "run": {"up": [], "down": [], "left": [], "right": []},
        }

        # importing player assets
        self.import_player_assets()
        self.image = self.animations["idle"]["down"][0]
        self.rect = self.image.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        self.mask = pygame.mask.from_surface(self.image)

        # 1. VISUAL RECT (Total size of the image)
        self.rect = self.image.get_rect(topleft = (x, y))

        # 2. PHYSICS HITBOX (The magic happens here)
        # .inflate(width_change, height_change) shrinks the rect relative to its center.
        # -10 on width: Makes the hitbox slightly thinner.
        # -70 on height: Cuts off the head and torso from collision (adjust this value based on your sprite height).
        self.hitbox = self.rect.inflate(-10, -70)
        self.pos = pygame.Vector2(float(self.hitbox.x), float(self.hitbox.y))

        self.rect.centerx = self.hitbox.centerx
        self.rect.bottom = self.hitbox.bottom

        # Stats setup
        self.stats = {'health': 100, 'energy': 60, 'attack': 10, 'magic': 4, 'speed': 300}
        self.max_stats = {'health': 300, 'energy': 140, 'attack': 20, 'magic': 10, 'speed': 10}
        self.upgrade_cost = {'health': 100, 'energy': 100, 'attack': 100, 'magic': 100, 'speed': 100}
        self.health = self.stats['health']
        self.energy = self.stats['energy']
        self.exp = 120
        self.player_speed = self.stats['speed']

    def move(self, new_position_x: float, new_position_y: float) -> None:
        
        # Guardamos a posição antiga do HITBOX para colisão
        old_hitbox_rect = self.hitbox.copy()

        # 1. Atualizamos o vetor preciso (Float)
        self.pos.x = new_position_x
        
        # 2. Atualizamos o Hitbox físico (Int) baseado no vetor
        self.hitbox.x = round(self.pos.x)
        
        # 3. Colisão X
        if hasattr(self, 'walls') and self.walls:
            if self.hitbox.collidelist(self.walls) != -1:
                # Se bateu, volta o hitbox para onde estava
                self.hitbox.centerx = old_hitbox_rect.centerx
                # E OBRIGATORIAMENTE volta o vetor float também, senão ele "entra" na parede
                self.pos.x = self.hitbox.x

        # 4. Sincroniza o Rect visual com o Hitbox físico
        self.rect.centerx = self.hitbox.centerx

        # 1. Atualizamos o vetor preciso (Float)
        self.pos.y = new_position_y
        self.hitbox.y = round(self.pos.y)

        # 3. Colisão Y
        if hasattr(self, 'walls') and self.walls:
            if self.hitbox.collidelist(self.walls) != -1:
                # Se bateu, volta
                self.hitbox.bottom = old_hitbox_rect.bottom
                # Sincroniza o vetor float de volta
                self.pos.y = self.hitbox.y

        # 4. Sincroniza o Rect visual
        self.rect.bottom = self.hitbox.bottom

        # Atualiza status de movimento para animação
        # Se a posição mudou significativamente, estamos movendo
        if old_hitbox_rect.center != self.hitbox.center:
            self.rect_movement = (1, 1) 
        else:
            self.rect_movement = (0, 0)

    def _fallback(self):
        s = pygame.Surface((50, 50), pygame.SRCALPHA)
        s.fill((255, 255, 255))
        return s

    def import_player_assets(self):
        base = os.path.join('src/sprites/entities', 'Player')
        dirs = ["up", "down", "left", "right"]

        for d in dirs:
            folder = os.path.join(base, "idle_and_run", d)
            if not os.path.isdir(folder):
                self.animations["idle"][d] = [self._fallback()]
                self.animations["run"][d] = [self._fallback()]
                continue

            files = sorted([f for f in os.listdir(folder) if f.lower().endswith(".png")])
            idle = None
            run = []
            for fn in files:
                img = pygame.image.load(os.path.join(folder, fn)).convert_alpha()
                img = pygame.transform.scale(img, (img.get_width() * 2, img.get_height() * 2))
                if "frame_00" in fn.lower():
                    idle = img
                else:
                    run.append(img)

            if idle is None:
                idle = run[0] if run else self._fallback()
            if not run:
                run = [idle]

            self.animations["idle"][d] = [idle]
            self.animations["run"][d] = run
    
    def recharge_badge(self):
        now = pygame.time.get_ticks()
        if self.badge_ammo < self.max_badge:
            if now - self.last_badge_reload >= self.badge_reload_ms:
                self.badge_ammo += 1
                self.last_badge_reload = now
        else:
            self.last_badge_reload = now

    def recharge_dash(self):
        now = pygame.time.get_ticks()
        self._dash_restore_times.sort()
        while self._dash_restore_times and self._dash_restore_times[0] <= now:
            self._dash_restore_times.pop(0)
            self.dash_charges = min(self.max_dash, self.dash_charges + 1)

    def take_damage(self, amount):
        now = pygame.time.get_ticks()
        if now - self.last_hit_time > self.invulnerable_duration:
            self.health -= int(amount)
            self.health = max(0, self.health)
            self.last_hit_time = now
            self.hurt_flash_until = now + self.hurt_flash_ms
    
    def draw_with_effects(self, surface: pygame.Surface):
        now = pygame.time.get_ticks()

        if now < self.glitch_until:
            fx, fy = self.glitch_from
            tx, ty = self.glitch_to
            for i in range(4):
                t = i / 3.0
                x = int(fx + (tx - fx) * t) + random.randint(-6, 6)
                y = int(fy + (ty - fy) * t) + random.randint(-6, 6)
                img = self.image.copy()
                img.set_alpha(120 + random.randint(-40, 40))
                r = img.get_rect(center=(x, y))
                surface.blit(img, r)

        if now < self.throw_until:
            recoil = {
                "up": (0, 2), "down": (0, -2),
                "left": (2, 0), "right": (-2, 0),
            }[self.self_direction]

            img = self.image
            r = img.get_rect(center=(self.rect.centerx + recoil[0], self.rect.centery + recoil[1]))
            surface.blit(img, r)
        else:
            img = self.image
            r = self.rect

            if now < self.hurt_flash_until:
                red = img.copy()
                red.fill((120, 0, 0, 0), special_flags=pygame.BLEND_RGBA_ADD)
                img = red

            surface.blit(img, r)
    
    def animate(self):
        if self.rect_movement == (0, 0):
            self.status = "idle"
            self.image = self.animations["idle"][self.self_direction][0]
        else:
            self.status = "run"
            frames = self.animations["run"][self.self_direction]
            idx = (pygame.time.get_ticks() // 90) % len(frames)
            self.image = frames[idx]
        self.mask = pygame.mask.from_surface(self.image)

    def action_dash(self):        
        keys = pygame.key.get_pressed()
        now = pygame.time.get_ticks()
        pressed = keys[pygame.K_SPACE]
        dash_edge = pressed and (not self._dash_prev_pressed)
        self._dash_prev_pressed = pressed

        if not dash_edge or self.dash_charges <= 0:
            return

        self.dash_charges -= 1
        self._dash_restore_times.append(now + self.dash_cooldown_ms)

        old_center = self.rect.center
        
        d_x, d_y = 0, 0
        if self.self_direction == "up":    d_y = -self.dash_distance
        elif self.self_direction == "down":  d_y = self.dash_distance
        elif self.self_direction == "left":  d_x = -self.dash_distance
        elif self.self_direction == "right": d_x = self.dash_distance

        target_x = self.hitbox.centerx + d_x
        target_y = self.hitbox.centery + d_y
        
        safe_center = self.dash_sweep_to_target(self.hitbox, (target_x, target_y), self.walls, step_px=8)
        
        self.hitbox.center = safe_center

        self.pos.x = float(self.hitbox.x)
        self.pos.y = float(self.hitbox.y)

        self.rect.centerx = self.hitbox.centerx
        self.rect.bottom = self.hitbox.bottom

        self.glitch_from = old_center
        self.glitch_to = self.rect.center
        self.glitch_until = now + 140
        self.global_action_cooldown = max(self.global_action_cooldown, now + 80)

        self.glitch_from = old_center
        self.glitch_to = self.rect.center
        self.glitch_until = now + 140
        self.global_action_cooldown = max(self.global_action_cooldown, now + 80)

    def get_status(self):
        if self.direction.magnitude() == 0:
            self.status = 'idle_' + self.self_direction
        else:
            self.status = 'walk_' + self.self_direction

        if self.attacking:
            self.direction.x = 0
            self.direction.y = 0
            self.status = 'attack_' + self.self_direction

    def cooldowns(self):
        current_time = pygame.time.get_ticks()

        if self.attacking:
            if current_time - self.attack_time >= self.attack_duration:
                self.attacking = False

    def action_melee(self):
        if self.attacking:
            return

        now = pygame.time.get_ticks()
        if now - self.last_attack_time < 400:
            return

        self.attacking = True
        self.attack_time = now
        self.last_attack_time = now

        slash = PlayerMeleeSlash(
            player_rect=self.hitbox,
            direction=self.self_direction,
            damage=self.stats['attack']
        )
        
        self.group_collision['all'].add(slash)
        self.group_collision['melee'].add(slash)

    def action_ranged(self):
        if self.attacking:
            return

        now = pygame.time.get_ticks()
        
        if now - self.last_attack_time < self.attack_cooldown_ms:
            return

        if self.badge_ammo <= 0:
            return

        self.attacking = True
        self.attack_time = now
        self.last_attack_time = now
        
        self.badge_ammo -= 1
        self.last_badge_reload = now 

        px, py = self.hitbox.center
        proj = BadgeProjectile(
            x=px, y=py,
            direction=self.self_direction,
            damage=self.stats['magic']
        )
        
        self.group_collision['all'].add(proj)
        self.group_collision['projectiles'].add(proj)
    
    def update(self):
        self.cooldowns()
        self.get_status()
        self.recharge_badge()
        self.recharge_dash()
        self.action_dash()
        self.animate()

        self.rect_movement = (0, 0)