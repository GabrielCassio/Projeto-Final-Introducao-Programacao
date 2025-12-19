# enemy.py
import pygame
import random
import heapq
from settings import *
from entity import Entity
from support import *


ENEMY_SHEET_DICT = {
    "skeleton": {
        "idle":   {"cols": 8, "rows": 1},
        "move":   {"cols": 10, "rows": 1},
        "attack": {"cols": 9, "rows": 1},
        "hited":  {"cols": 5, "rows": 1},
        "death":  {"cols": 17, "rows": 1},
    },
    "vampire": {
        "idle":   {"cols": 6, "rows": 1},
        "move":   {"cols": 8, "rows": 1},
        "attack": {"cols": 16, "rows": 1},
        "hited":  {"cols": 5, "rows": 1},
        "death":  {"cols": 14, "rows": 1},
    },
    "ghost": {
        "idle":   {"cols": 8, "rows": 1},
        "move":   {"cols": 13, "rows": 1},
        "attack": {"cols": 8, "rows": 1},
        "hited":  {"cols": 1, "rows": 1},
        "death":  {"cols": 10, "rows": 1},
    },
}


ENEMY_STATS = {
    "skeleton": {
        "max_health": 100,
        "speed": 85,
        "attack_damage": 18,
        "attack_radius": 40,
        "notice_radius": 300,
        "attack_cooldown": 1100,
        "invincibility_duration": 250,
    },
    "ghost": {
        "max_health": 60,
        "speed": 115,
        "attack_damage": 15,
        "attack_radius": 220,
        "notice_radius": 420,
        "attack_cooldown": 1700,
        "invincibility_duration": 220,

        "projectile_speed": 140,  
        "projectile_image": "ghost_energyball.png",
        "projectile_scale": 0.75,
        "projectile_life_time": 3500,
        "projectile_cols": 10,
        "projectile_rows": 1,
        "projectile_anim_fps": 12,

        "flee_radius": 140,
        "preferred_distance": 260,
        "strafe_strength": 0.35,
        "strafe_change_ms": 800,
    },
    "vampire": {
        "max_health": 120,
        "speed": 95,
        "attack_damage": 20,
        "attack_radius": 65,
        "notice_radius": 300,
        "attack_cooldown": 1300,
        "invincibility_duration": 280,
    },
    "default": {
        "max_health": 80,
        "speed": 80,
        "attack_damage": 15,
        "attack_radius": 50,
        "notice_radius": 250,
        "attack_cooldown": 1200,
        "invincibility_duration": 250,
    }
}

_IMAGE_CACHE: dict[tuple[str, float], pygame.Surface] = {}
_FRAMES_CACHE: dict[tuple[str, int, int, float], list[pygame.Surface]] = {}


def _load_image_cached(path: str, scale: float = 1.0) -> pygame.Surface | None:
    key = (path, float(scale))
    if key in _IMAGE_CACHE:
        return _IMAGE_CACHE[key]

    try:
        img = pygame.image.load(path).convert_alpha()
        if scale != 1.0:
            w = max(1, int(img.get_width() * scale))
            h = max(1, int(img.get_height() * scale))
            img = pygame.transform.smoothscale(img, (w, h))
        _IMAGE_CACHE[key] = img
        return img
    except Exception:
        return None


class SpriteSheet:
    def __init__(self, image):
        self.sheet = image

    def get_image(self, frame, width, height, scale, colour):
        image = pygame.Surface((width, height), pygame.SRCALPHA).convert_alpha()
        image.blit(self.sheet, (0, 0), (frame * width, 0, width, height))
        image = pygame.transform.scale(image, (int(width * scale), int(height * scale)))
        return image


def slice_strip_simple(raw, cols, rows, scale):
    sheet = SpriteSheet(raw)
    frame_w = raw.get_width() // cols
    frame_h = raw.get_height() // rows
    frames = []
    for i in range(cols * rows):
        frames.append(sheet.get_image(i, frame_w, frame_h, scale, None))
    return frames


def _load_sheet_frames_cached(path: str, cols: int, rows: int, scale: float) -> list[pygame.Surface] | None:
    key = (path, int(cols), int(rows), float(scale))
    if key in _FRAMES_CACHE:
        return _FRAMES_CACHE[key]

    try:
        raw = pygame.image.load(path).convert_alpha()
        frames = slice_strip_simple(raw, cols, rows, scale)
        _FRAMES_CACHE[key] = frames
        return frames
    except Exception:
        return None


class EnemyProjectile(pygame.sprite.Sprite):
    def __init__(self, pos, groups, direction, speed, damage, image_surf=None, life_time=3000, frames=None, anim_fps=12):
        super().__init__(groups)

        self.frames = frames if frames else None
        self.anim_fps = anim_fps
        self.frame_index = 0.0

        if self.frames and len(self.frames) > 0:
            self.image = self.frames[0]
        else:
            if image_surf is None:
                self.image = pygame.Surface((20, 20), pygame.SRCALPHA)
                pygame.draw.circle(self.image, (255, 140, 0, 220), (10, 10), 8)
            else:
                self.image = image_surf

        self.rect = self.image.get_rect(center=pos)

        shrink_x = int(self.rect.width * 0.35)
        shrink_y = int(self.rect.height * 0.35)
        self.hitbox = self.rect.inflate(-shrink_x, -shrink_y)

        self.direction = direction if direction is not None else pygame.math.Vector2()
        self.speed = speed
        self.damage = damage
        self.start_time = pygame.time.get_ticks()
        self.life_time = life_time

    def update(self, dt):
        self.hitbox.center += self.direction * self.speed * dt
        self.rect.center = self.hitbox.center

        if self.frames:
            self.frame_index += self.anim_fps * dt
            if self.frame_index >= len(self.frames):
                self.frame_index = 0.0
            frame = int(self.frame_index)
            prev_center = self.rect.center
            self.image = self.frames[frame]
            self.rect = self.image.get_rect(center=prev_center)

        if pygame.time.get_ticks() - self.start_time > self.life_time:
            self.kill()


class EnemyMeleeHitbox(pygame.sprite.Sprite):
    def __init__(self, owner, groups, size, offset, damage, duration):
        super().__init__(groups)
        self.owner = owner
        self.damage = damage
        self.start_time = pygame.time.get_ticks()
        self.duration = duration

        self.image = pygame.Surface(size, pygame.SRCALPHA)
        r = pygame.Rect((0, 0), size)

        fill_col = (255, 60, 60, 30)
        outline_col = (255, 120, 120, 70)
        radius = max(8, min(size) // 4)

        pygame.draw.rect(self.image, fill_col, r, border_radius=radius)
        pygame.draw.rect(self.image, outline_col, r, width=2, border_radius=radius)

        self.rect = self.image.get_rect(center=owner.rect.center)
        self.offset = pygame.math.Vector2(offset)

    def update(self, dt):
        if not self.owner.alive():
            self.kill()
            return
        self.rect.center = self.owner.rect.center + self.offset
        if pygame.time.get_ticks() - self.start_time >= self.duration:
            self.kill()


class Pathfinder:
    def __init__(self, matrix, obstacle_sprites):
        self.obstacle_sprites = obstacle_sprites
        self.cell_size = 64

    def get_path(self, start, target):
        start_pos = (int(start[0] // self.cell_size), int(start[1] // self.cell_size))
        end_pos = (int(target[0] // self.cell_size), int(target[1] // self.cell_size))

        if start_pos == end_pos:
            return None

        open_list = []
        heapq.heappush(open_list, (0, start_pos))
        came_from = {start_pos: None}
        cost_so_far = {start_pos: 0}

        iterations = 0
        max_iterations = 50

        while open_list:
            iterations += 1
            if iterations > max_iterations:
                break

            _, current = heapq.heappop(open_list)

            if current == end_pos:
                break

            for next_pos in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                neighbor = (current[0] + next_pos[0], current[1] + next_pos[1])
                new_cost = cost_so_far[current] + 1

                neighbor_pixel_pos = (neighbor[0] * self.cell_size, neighbor[1] * self.cell_size)
                neighbor_rect = pygame.Rect(neighbor_pixel_pos[0], neighbor_pixel_pos[1], self.cell_size, self.cell_size)

                collision = False
                for sprite in self.obstacle_sprites:
                    if sprite.hitbox.colliderect(neighbor_rect):
                        collision = True
                        break

                if not collision:
                    if neighbor not in cost_so_far or new_cost < cost_so_far[neighbor]:
                        cost_so_far[neighbor] = new_cost
                        priority = new_cost + self.heuristic(end_pos, neighbor)
                        heapq.heappush(open_list, (priority, neighbor))
                        came_from[neighbor] = current

        if end_pos not in came_from:
            return None

        path = []
        curr = end_pos
        count = 0
        while curr != start_pos and count < 100:
            path.append(curr)
            curr = came_from[curr]
            count += 1
        path.reverse()

        if path:
            next_grid_pos = path[0]
            return pygame.math.Vector2(
                next_grid_pos[0] * self.cell_size + self.cell_size / 2,
                next_grid_pos[1] * self.cell_size + self.cell_size / 2
            )
        return None

    def heuristic(self, a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])


class Enemy(Entity):
    def __init__(self, monster_name, pos, groups, obstacle_sprites, damage_player_callback, trigger_death_callback):
        super().__init__(groups)

        self.sprite_type = 'enemy'
        self.monster_name = monster_name
        self.obstacle_sprites = obstacle_sprites
        self.damage_player_callback = damage_player_callback
        self.trigger_death_callback = trigger_death_callback

        self.has_attacked = False

        self.import_graphics(monster_name)

        self.status = 'idle'
        self.frame_index = 0

        if len(self.animations[self.status]) == 0:
            self.animations[self.status] = [pygame.Surface((32, 32))]
            self.animations[self.status][0].fill('magenta')

        self.image = self.animations[self.status][self.frame_index]
        self.rect = self.image.get_rect(topleft=pos)
        self.hitbox = self.rect.inflate(0, -10)

        stats = ENEMY_STATS.get(monster_name, ENEMY_STATS["default"])

        self.max_health = stats["max_health"]
        self.health = self.max_health

        self.speed = stats["speed"]
        self.attack_damage = stats["attack_damage"]
        self.attack_radius = stats["attack_radius"]
        self.notice_radius = stats["notice_radius"]

        self.can_attack = True
        self.attack_time = 0
        self.attack_cooldown = stats["attack_cooldown"]

        self.vulnerable = True
        self.hit_time = 0
        self.invincibility_duration = stats["invincibility_duration"]

        self.pathfinder = Pathfinder(None, obstacle_sprites)
        self.path_timer = pygame.time.get_ticks() + random.randint(0, 1000)
        self.current_path_target = None

        # projétil
        self.projectile_speed = stats.get("projectile_speed", 300)
        self.projectile_life_time = stats.get("projectile_life_time", 3000)
        self.projectile_anim_fps = stats.get("projectile_anim_fps", 12)

        self.projectile_image = None
        self.projectile_frames = None

        proj_name = stats.get("projectile_image")
        if proj_name:
            proj_scale = stats.get("projectile_scale", 1.0)
            proj_cols = stats.get("projectile_cols", 1)
            proj_rows = stats.get("projectile_rows", 1)
            proj_path = f'./assets/graphics/enemy/{monster_name}/{proj_name}'

            if (proj_cols and proj_cols > 1) or (proj_rows and proj_rows > 1):
                frames = _load_sheet_frames_cached(proj_path, proj_cols, proj_rows, proj_scale)
                if frames and len(frames) > 0:
                    self.projectile_frames = frames
                    self.projectile_image = frames[0]
                else:
                    self.projectile_image = _load_image_cached(proj_path, proj_scale)
            else:
                self.projectile_image = _load_image_cached(proj_path, proj_scale)

        self.flee_radius = stats.get("flee_radius", 0)
        self.preferred_distance = stats.get("preferred_distance", self.attack_radius)
        self.strafe_strength = stats.get("strafe_strength", 0.0)
        self.strafe_change_ms = stats.get("strafe_change_ms", 800)

        self._ghost_mode = "idle"
        self._ghost_strafe = random.choice([-1, 1])
        self._ghost_strafe_time = pygame.time.get_ticks()

    def import_graphics(self, name):
        self.animations = {'idle': [], 'move': [], 'attack': [], 'hited': [], 'death': []}
        config = ENEMY_SHEET_DICT.get(name)
        if not config:
            return

        scale_val = 1
        if name == 'skeleton':
            scale_val = 1.5
        if name == 'ghost':
            scale_val = 0.25
        if name == 'vampire':
            scale_val = 1.5

        path = f'./assets/graphics/enemy/{name}/'

        for anim in self.animations.keys():
            if name == 'ghost' and anim == 'idle':
                continue

            full_path = path + f'{name}_{anim}.png'
            try:
                img = pygame.image.load(full_path).convert_alpha()
                frames = slice_strip_simple(img, config[anim]['cols'], config[anim]['rows'], scale_val)
                self.animations[anim] = frames
            except Exception:
                print(f"Erro ao carregar {anim} de {name}")
                surf = pygame.Surface((32, 32))
                surf.fill('red')
                self.animations[anim] = [surf]

        if name == 'ghost':
            if len(self.animations['move']) > 0:
                first_frame = self.animations['move'][0]
                self.animations['idle'] = [first_frame]
            else:
                print("ERRO CRÍTICO: Ghost não tem nem animação de andar para copiar!")

    def get_player_distance_direction(self, player):
        enemy_vec = pygame.math.Vector2(self.rect.center)
        player_vec = pygame.math.Vector2(player.rect.center)
        distance = (player_vec - enemy_vec).magnitude()
        if distance > 0:
            direction = (player_vec - enemy_vec).normalize()
        else:
            direction = pygame.math.Vector2()
        return (distance, direction)

    def _get_status_ghost(self, player):
        distance, _ = self.get_player_distance_direction(player)

        if distance <= self.flee_radius:
            self.status = 'move'
            self._ghost_mode = 'flee'
            return

        if distance <= self.attack_radius:
            if self.can_attack:
                if self.status != 'attack':
                    self.frame_index = 0
                self.status = 'attack'
                self._ghost_mode = 'shoot'
            else:
                if distance < self.preferred_distance:
                    self.status = 'move'
                    self._ghost_mode = 'flee'
                elif distance > self.preferred_distance + 60:
                    self.status = 'move'
                    self._ghost_mode = 'approach'
                else:
                    self.status = 'idle'
                    self._ghost_mode = 'drift'
            return

        if distance <= self.notice_radius:
            self.status = 'move'
            self._ghost_mode = 'approach'
            return

        self.status = 'idle'
        self._ghost_mode = 'idle'

    def get_status(self, player):
        if self.monster_name == 'ghost':
            self._get_status_ghost(player)
            return

        distance, _ = self.get_player_distance_direction(player)

        if distance <= self.attack_radius:
            if self.can_attack:
                if self.status != 'attack':
                    self.frame_index = 0
                self.status = 'attack'
            else:
                self.status = 'idle'
        elif distance <= self.notice_radius:
            self.status = 'move'
        else:
            self.status = 'idle'

    def actions(self, player):
        if not self.vulnerable:
            return

        if self.status == 'attack':
            self.attack_time = pygame.time.get_ticks()
            current_frame = int(self.frame_index)

            if self.monster_name == 'vampire':
                if current_frame >= 3 and not self.has_attacked:
                    self.damage_player_callback(self, 'melee', self.rect.center, None, self.attack_damage)
                    self.has_attacked = True

            elif self.monster_name == 'ghost':
                if current_frame >= 4 and not self.has_attacked:
                    _, direction = self.get_player_distance_direction(player)
                    self.damage_player_callback(self, 'projectile', self.rect.center, direction, self.attack_damage)
                    self.has_attacked = True

            elif self.monster_name == 'skeleton':
                if current_frame >= 4 and not self.has_attacked:
                    self.damage_player_callback(self, 'melee', self.rect.center, None, self.attack_damage)
                    self.has_attacked = True

        elif self.status == 'move':
            if self.monster_name == 'ghost':
                dist, dir_to_player = self.get_player_distance_direction(player)

                now = pygame.time.get_ticks()
                if now - self._ghost_strafe_time >= self.strafe_change_ms:
                    self._ghost_strafe_time = now
                    self._ghost_strafe = random.choice([-1, 1])

                perp = pygame.math.Vector2(-dir_to_player.y, dir_to_player.x) * self._ghost_strafe

                if self._ghost_mode == 'flee':
                    base = -dir_to_player
                    vec = base + perp * self.strafe_strength
                elif self._ghost_mode == 'approach':
                    base = dir_to_player
                    vec = base + perp * (self.strafe_strength * 0.5)
                else:
                    vec = perp

                if vec.magnitude() > 0:
                    self.direction = vec.normalize()
                else:
                    self.direction = pygame.math.Vector2()
                return

            current_time = pygame.time.get_ticks()

            if current_time - self.path_timer > 1000:
                self.path_timer = current_time
                dist, _ = self.get_player_distance_direction(player)

                if dist < 100:
                    self.current_path_target = None
                else:
                    try:
                        target_pos = self.pathfinder.get_path(self.rect.center, player.rect.center)
                        self.current_path_target = target_pos if target_pos else None
                    except Exception:
                        self.current_path_target = None

            if self.current_path_target:
                vec = self.current_path_target - pygame.math.Vector2(self.rect.center)
                if vec.magnitude() > 0:
                    self.direction = vec.normalize()
                else:
                    self.direction = pygame.math.Vector2()
                    self.current_path_target = None
            else:
                _, self.direction = self.get_player_distance_direction(player)

    def animate(self, dt):
        current_animation = self.animations[self.status]

        self.frame_index += 8 * dt

        if self.frame_index >= len(current_animation):
            if self.status == 'attack':
                self.can_attack = False
                self.has_attacked = False
                self.status = 'idle'
            self.frame_index = 0

        frame = int(self.frame_index)
        if frame >= len(current_animation):
            frame = 0

        self.image = current_animation[frame]
        self.rect = self.image.get_rect(center=self.hitbox.center)

        if self.direction.x < 0:
            self.image = pygame.transform.flip(self.image, True, False)

    def cooldowns(self):
        current_time = pygame.time.get_ticks()
        if not self.can_attack:
            if current_time - self.attack_time >= self.attack_cooldown:
                self.can_attack = True
        if not self.vulnerable:
            if current_time - self.hit_time >= self.invincibility_duration:
                self.vulnerable = True

    def get_damage(self, player, attack_type):
        if self.vulnerable:
            self.health -= 20
            self.vulnerable = False
            self.hit_time = pygame.time.get_ticks()

            enemy_vec = pygame.math.Vector2(self.rect.center)
            player_vec = pygame.math.Vector2(player.rect.center)
            knockback_direction = (enemy_vec - player_vec)
            if knockback_direction.magnitude() > 0:
                self.direction = knockback_direction.normalize()

            if self.health <= 0:
                self.trigger_death_callback(self.rect.center, self.monster_name)
                self.kill()

    def update(self, dt):
        self.move(self.speed, dt)
        self.animate(dt)
        self.cooldowns()
