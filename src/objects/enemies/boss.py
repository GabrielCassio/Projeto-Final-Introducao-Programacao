from __future__ import annotations
import math, random
from dataclasses import dataclass
from typing import Optional, Tuple, Dict

import pygame

Vec2 = Tuple[float, float]


def now_ms() -> int:
    return pygame.time.get_ticks()


def clamp(x: float, a: float, b: float) -> float:
    return max(a, min(b, x))


def normalize(dx: float, dy: float) -> Vec2:
    mag = math.hypot(dx, dy)
    if mag <= 1e-6:
        return (0.0, 0.0)
    return (dx / mag, dy / mag)


def player_is_dashing(player) -> bool:
    t = now_ms()
    # no teu Player tem glitch_until
    if getattr(player, "is_dashing", False):
        return True
    for attr in ("dash_iframes_until", "glitch_until"):
        try:
            if t < int(getattr(player, attr, 0)):
                return True
        except Exception:
            pass
    return False


def safe_player_damage(player, amount: int):
    if not hasattr(player, "take_damage"):
        return
    try:
        player.take_damage(int(amount))
    except TypeError:
        try:
            player.take_damage()
        except TypeError:
            pass


def ensure_groups(groups_for_enemy: Dict) -> Dict:
    g = dict(groups_for_enemy) if isinstance(groups_for_enemy, dict) else {}
    g.setdefault("all", pygame.sprite.Group())
    g.setdefault("proj", pygame.sprite.Group())
    g.setdefault("melee", pygame.sprite.Group())
    g.setdefault("walls", pygame.sprite.Group())
    return g


# ----------------- FX / HITBOXES -----------------

class Telegraph(pygame.sprite.Sprite):
    """Somente visual, sem dano."""
    def __init__(self, rect: pygame.Rect, ttl_ms: int, groups_all: pygame.sprite.Group, alpha: int = 60):
        super().__init__(groups_all)
        self.image = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
        self.image.fill((255, 0, 0, alpha))
        self.rect = rect.copy()
        self.mask = pygame.mask.from_surface(self.image)
        self.damage = 0
        self._born = now_ms()
        self._ttl = int(ttl_ms)

    def update(self, *args):
        if now_ms() - self._born >= self._ttl:
            self.kill()


class EnemyMeleeHitbox(pygame.sprite.Sprite):
    """Hitbox de melee do inimigo. Vai em all + enemy_melee."""
    def __init__(
        self,
        rect: pygame.Rect,
        damage: int,
        ttl_ms: int,
        groups_all: pygame.sprite.Group,
        groups_melee: pygame.sprite.Group,
        alpha: int = 220,
    ):
        super().__init__(groups_all, groups_melee)
        self.image = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
        self.image.fill((255, 0, 0, alpha))
        self.rect = rect.copy()
        self.mask = pygame.mask.from_surface(self.image)

        self.damage = int(damage)
        self.hit_list = []  # teu main usa isso
        self._born = now_ms()
        self._ttl = int(ttl_ms)

    def update(self, *args):
        if now_ms() - self._born >= self._ttl:
            self.kill()


class LavaWave(pygame.sprite.Sprite):
    """Projétil do boss. Vai em all + enemy_projectiles."""
    def __init__(
        self,
        center: Tuple[int, int],
        direction: Vec2,
        speed_px_s: float,
        damage: int,
        ttl_ms: int,
        arena_rect: pygame.Rect,
        groups_all: pygame.sprite.Group,
        groups_proj: pygame.sprite.Group,
        size: Tuple[int, int],
    ):
        super().__init__(groups_all, groups_proj)
        self.image = pygame.Surface(size, pygame.SRCALPHA)
        self.image.fill((255, 0, 0, 210))
        self.rect = self.image.get_rect(center=center)
        self.mask = pygame.mask.from_surface(self.image)

        self.dx, self.dy = normalize(direction[0], direction[1])
        if self.dx == 0.0 and self.dy == 0.0:
            self.dx, self.dy = 1.0, 0.0

        self.speed = float(speed_px_s)
        self.damage = int(damage)
        self.hit_list = []  # defensivo (não usado no teu main, mas não atrapalha)

        self.arena = arena_rect.copy()
        self._born = now_ms()
        self._ttl = int(ttl_ms)
        self._last = now_ms()

        self.fx = float(self.rect.x)
        self.fy = float(self.rect.y)

    def update(self, *args):
        t = now_ms()
        dt = max(0.0, (t - self._last) / 1000.0)
        self._last = t

        self.fx += self.dx * self.speed * dt
        self.fy += self.dy * self.speed * dt
        self.rect.x = int(self.fx)
        self.rect.y = int(self.fy)

        if t - self._born >= self._ttl:
            self.kill()
            return

        if not self.arena.inflate(500, 500).colliderect(self.rect):
            self.kill()


class Explosion(pygame.sprite.Sprite):
    """Telegraph -> Boom. Vai em all + enemy_projectiles."""
    def __init__(
        self,
        center: Tuple[int, int],
        size: Tuple[int, int],
        tele_ms: int,
        boom_ms: int,
        damage: int,
        groups_all: pygame.sprite.Group,
        groups_proj: pygame.sprite.Group,
    ):
        super().__init__(groups_all, groups_proj)
        self.tele_ms = int(tele_ms)
        self.boom_ms = int(boom_ms)
        self.damage_active = int(damage)

        self.phase = "tele"
        self.phase_t = now_ms()

        self.image = pygame.Surface(size, pygame.SRCALPHA)
        self.image.fill((255, 0, 0, 70))
        self.rect = self.image.get_rect(center=center)
        self.mask = pygame.mask.from_surface(self.image)

        self.damage = 0
        self.hit_list = []

    def update(self, *args):
        t = now_ms()
        elapsed = t - self.phase_t

        if self.phase == "tele" and elapsed >= self.tele_ms:
            self.phase = "boom"
            self.phase_t = t
            self.image.fill((255, 0, 0, 235))
            self.damage = self.damage_active
            self.mask = pygame.mask.from_surface(self.image)
            return

        if self.phase == "boom" and elapsed >= self.boom_ms:
            self.kill()


class DashChargeHitbox(pygame.sprite.Sprite):
    """Hitbox do dash do boss. Vai em all + enemy_melee."""
    def __init__(
        self,
        owner,
        size: Tuple[int, int],
        damage: int,
        ttl_ms: int,
        groups_all: pygame.sprite.Group,
        groups_melee: pygame.sprite.Group,
        alpha: int = 180,
    ):
        super().__init__(groups_all, groups_melee)
        self.owner = owner
        self.image = pygame.Surface(size, pygame.SRCALPHA)
        self.image.fill((255, 0, 0, alpha))
        self.rect = self.image.get_rect(center=getattr(owner, "rect").center)
        self.mask = pygame.mask.from_surface(self.image)
        self.damage = int(damage)
        self.hit_list = []
        self._born = now_ms()
        self._ttl = int(ttl_ms)

    def update(self, *args):
        if not hasattr(self.owner, "rect"):
            self.kill()
            return
        self.rect.center = self.owner.rect.center
        if now_ms() - self._born >= self._ttl:
            self.kill()


class SuperWave(pygame.sprite.Sprite):
    """
    Não entra em enemy_projectiles/enemy_melee, então faz dano manual (se não, teu main não pega).
    Respeita dash do player via glitch_until.
    """
    def __init__(
        self,
        rect: pygame.Rect,
        direction: str,  # lr/rl/tb/bt
        speed_px_s: float,
        damage: int,
        player,
        arena_rect: pygame.Rect,
        groups_all: pygame.sprite.Group,
        alpha: int = 235,
    ):
        super().__init__(groups_all)
        self.image = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
        self.image.fill((255, 0, 0, alpha))
        self.rect = rect.copy()
        self.mask = pygame.mask.from_surface(self.image)

        self.direction = direction
        self.speed = float(speed_px_s)
        self.damage = int(damage)
        self.player = player
        self.arena = arena_rect.copy()

        self._hit_once = False
        self._last = now_ms()

        self.fx = float(self.rect.x)
        self.fy = float(self.rect.y)

    def update(self, *args):
        t = now_ms()
        dt = max(0.0, (t - self._last) / 1000.0)
        self._last = t

        if self.direction == "lr":
            self.fx += self.speed * dt
        elif self.direction == "rl":
            self.fx -= self.speed * dt
        elif self.direction == "tb":
            self.fy += self.speed * dt
        else:
            self.fy -= self.speed * dt

        self.rect.x = int(self.fx)
        self.rect.y = int(self.fy)

        if (not self._hit_once) and hasattr(self.player, "rect"):
            if self.rect.colliderect(self.player.rect):
                if not player_is_dashing(self.player):
                    safe_player_damage(self.player, self.damage)
                self._hit_once = True

        if not self.arena.inflate(1400, 1400).colliderect(self.rect):
            self.kill()


# ----------------- TUNING -----------------

@dataclass
class SlimeBossTuning:
    max_hp: int = 960

    base_speed: float = 85.0
    bonus_speed_at_0hp: float = 95.0

    melee_cd_ms: int = 850
    melee_range: float = 62.0
    melee_windup_ms: int = 240
    melee_active_ms: int = 140
    melee_damage: int = 22
    melee_size: Tuple[int, int] = (56, 34)

    jump_base_cd_ms: int = 7600
    jump_min_cd_ms: int = 3000
    jump_windup_ms: int = 650
    slam_active_ms: int = 220
    slam_damage: int = 30
    slam_inflate: int = 120

    wave_speed: float = 340.0
    wave_damage: int = 16
    wave_ttl_ms: int = 2300
    wave_size_h: Tuple[int, int] = (86, 26)
    wave_size_v: Tuple[int, int] = (26, 86)

    exp_base_cd_ms: int = 15000
    exp_min_cd_ms: int = 8500
    exp_cast_windup_ms: int = 450
    exp_count: int = 16
    exp_size: Tuple[int, int] = (58, 58)
    exp_tele_ms: int = 700
    exp_boom_ms: int = 260
    exp_damage: int = 26

    dash_base_cd_ms: int = 6500
    dash_min_cd_ms: int = 2800
    dash_windup_ms: int = 520
    dash_duration_ms: int = 520
    dash_speed: float = 520.0
    dash_damage: int = 34
    dash_hitbox: Tuple[int, int] = (52, 52)

    scripted_threshold_hp: int = 96
    super_cast_ms: int = 850
    super_tele_ms: int = 650
    super_damage: int = 80
    super_speed: float = 600.0
    super_thickness: int = 120


# ----------------- BOSS -----------------

class SlimeBoss(pygame.sprite.Sprite):
    def __init__(
        self,
        x: int,
        y: int,
        player,
        groups_for_enemy: dict,
        arena_rect: Optional[pygame.Rect] = None,
        tuning: Optional[SlimeBossTuning] = None,
        size: int = 34,
    ):
        self.g = ensure_groups(groups_for_enemy)
        super().__init__(self.g["all"])

        self.player = player
        self.t = tuning if tuning is not None else SlimeBossTuning()

        if arena_rect is None:
            surf = pygame.display.get_surface()
            arena_rect = surf.get_rect() if surf else pygame.Rect(0, 0, 1280, 720)
        self.arena = arena_rect.copy()

        self.image = pygame.Surface((size, size), pygame.SRCALPHA)
        self.base_color = (255, 140, 0)
        self.image.fill((*self.base_color, 255))
        self.rect = self.image.get_rect(center=(x, y))
        self.mask = pygame.mask.from_surface(self.image)

        self.max_hp = int(self.t.max_hp)
        self.hp = int(self.t.max_hp)
        self.dead = False

        self.fx = float(self.rect.x)
        self.fy = float(self.rect.y)

        self.facing = (1.0, 0.0)

        self.state = "idle"
        self.state_until = 0

        t0 = now_ms()
        self.next_melee = t0 + 300
        self.next_jump = t0 + 900
        self.next_exp = t0 + 2200
        self.next_dash = t0 + 1400

        self._scripted_done = False
        self._super_plan = None  # (direction, wave_rect, cast_ms)
        self._dash_dir = (1.0, 0.0)

        self._last = t0

        self._dash_hitbox_sprite = None
        self.walls = self.g.get("walls") or pygame.sprite.Group()

        self.rect.clamp_ip(self.arena)
        self.fx = float(self.rect.x)
        self.fy = float(self.rect.y)

    # ---------- API ----------

    def take_damage(self, amount: int, source_pos=None, crit: bool = False):
        if self.dead:
            return
        self.hp -= int(amount)
        if self.hp <= 0:
            self.hp = 0
            self.dead = True
            self.kill()

    # ---------- helpers ----------

    def hp_lost_frac(self) -> float:
        return 1.0 - (self.hp / max(1, self.max_hp))

    def speed(self) -> float:
        return self.t.base_speed + self.t.bonus_speed_at_0hp * self.hp_lost_frac()

    def jump_cd(self) -> int:
        frac = self.hp_lost_frac()
        cd = self.t.jump_base_cd_ms - frac * (self.t.jump_base_cd_ms - self.t.jump_min_cd_ms)
        return int(clamp(cd, self.t.jump_min_cd_ms, self.t.jump_base_cd_ms))

    def exp_cd(self) -> int:
        frac = self.hp_lost_frac()
        cd = self.t.exp_base_cd_ms - frac * (self.t.exp_base_cd_ms - self.t.exp_min_cd_ms)
        return int(clamp(cd, self.t.exp_min_cd_ms, self.t.exp_base_cd_ms))

    def dash_cd(self) -> int:
        frac = self.hp_lost_frac()
        cd = self.t.dash_base_cd_ms - frac * (self.t.dash_base_cd_ms - self.t.dash_min_cd_ms)
        return int(clamp(cd, self.t.dash_min_cd_ms, self.t.dash_base_cd_ms))

    def begin(self, name: str, duration_ms: int):
        self.state = name
        self.state_until = now_ms() + int(duration_ms)

    def dist_to_player(self) -> float:
        if not hasattr(self.player, "rect"):
            return 999999.0
        bx, by = self.rect.center
        px, py = self.player.rect.center
        return math.hypot(px - bx, py - by)

    def update_visual(self):
        frac = self.hp / max(1, self.max_hp)
        pulse = (math.sin(now_ms() * 0.012) + 1.0) * 0.5
        r, g, b = self.base_color

        if frac <= 0.10:
            mult = 0.55 + 0.45 * pulse
            col = (min(255, int(r)), min(255, int(80 + 140 * mult)), min(255, int(80 + 120 * mult)))
        elif frac <= 0.35:
            mult = 0.75 + 0.25 * pulse
            col = (min(255, int(r)), min(255, int(g * mult)), min(255, int(b * mult)))
        else:
            col = (r, g, b)

        self.image.fill((*col, 255))
        self.mask = pygame.mask.from_surface(self.image)

    # ---------- spawns ----------

    def spawn_melee_tele(self):
        w, h = self.t.melee_size
        cx, cy = self.rect.center
        fx, fy = self.facing
        offset = 28
        r = pygame.Rect(0, 0, w, h)
        r.center = (int(cx + fx * offset), int(cy + fy * offset))
        Telegraph(r, self.t.melee_windup_ms, self.g["all"], alpha=65)

    def spawn_melee_hit(self):
        w, h = self.t.melee_size
        cx, cy = self.rect.center
        fx, fy = self.facing
        offset = 28
        r = pygame.Rect(0, 0, w, h)
        r.center = (int(cx + fx * offset), int(cy + fy * offset))
        EnemyMeleeHitbox(r, self.t.melee_damage, self.t.melee_active_ms, self.g["all"], self.g["melee"], alpha=220)

        if self.hp <= int(self.max_hp * 0.70):
            r2 = r.copy()
            r2.centerx += int(fy * 18)
            r2.centery += int(-fx * 18)
            EnemyMeleeHitbox(r2, int(self.t.melee_damage * 0.75), int(self.t.melee_active_ms * 0.9), self.g["all"], self.g["melee"], alpha=180)

    def spawn_slam_tele(self):
        r = self.rect.inflate(self.t.slam_inflate, self.t.slam_inflate)
        Telegraph(r, self.t.jump_windup_ms, self.g["all"], alpha=55)

    def spawn_slam_hit(self):
        r = self.rect.inflate(self.t.slam_inflate, self.t.slam_inflate)
        EnemyMeleeHitbox(r, self.t.slam_damage, self.t.slam_active_ms, self.g["all"], self.g["melee"], alpha=235)

    def spawn_waves(self):
        cx, cy = self.rect.center

        LavaWave((cx, cy), (1, 0), self.t.wave_speed, self.t.wave_damage, self.t.wave_ttl_ms, self.arena, self.g["all"], self.g["proj"], self.t.wave_size_h)
        LavaWave((cx, cy), (-1, 0), self.t.wave_speed, self.t.wave_damage, self.t.wave_ttl_ms, self.arena, self.g["all"], self.g["proj"], self.t.wave_size_h)
        LavaWave((cx, cy), (0, 1), self.t.wave_speed, self.t.wave_damage, self.t.wave_ttl_ms, self.arena, self.g["all"], self.g["proj"], self.t.wave_size_v)
        LavaWave((cx, cy), (0, -1), self.t.wave_speed, self.t.wave_damage, self.t.wave_ttl_ms, self.arena, self.g["all"], self.g["proj"], self.t.wave_size_v)

        if self.hp <= int(self.max_hp * 0.35):
            diag = 0.78
            LavaWave((cx, cy), (diag, diag), self.t.wave_speed * 0.92, int(self.t.wave_damage * 0.85), int(self.t.wave_ttl_ms * 0.95), self.arena, self.g["all"], self.g["proj"], (72, 26))
            LavaWave((cx, cy), (-diag, diag), self.t.wave_speed * 0.92, int(self.t.wave_damage * 0.85), int(self.t.wave_ttl_ms * 0.95), self.arena, self.g["all"], self.g["proj"], (72, 26))
            LavaWave((cx, cy), (diag, -diag), self.t.wave_speed * 0.92, int(self.t.wave_damage * 0.85), int(self.t.wave_ttl_ms * 0.95), self.arena, self.g["all"], self.g["proj"], (72, 26))
            LavaWave((cx, cy), (-diag, -diag), self.t.wave_speed * 0.92, int(self.t.wave_damage * 0.85), int(self.t.wave_ttl_ms * 0.95), self.arena, self.g["all"], self.g["proj"], (72, 26))

    def cast_explosions(self):
        px, py = (self.arena.centerx, self.arena.centery)
        if hasattr(self.player, "rect"):
            px, py = self.player.rect.center

        count = int(self.t.exp_count)
        near = int(count * 0.55)

        for i in range(count):
            if i < near:
                ox = random.randint(-220, 220)
                oy = random.randint(-220, 220)
                x = int(clamp(px + ox, self.arena.left + 30, self.arena.right - 30))
                y = int(clamp(py + oy, self.arena.top + 30, self.arena.bottom - 30))
            else:
                x = random.randint(self.arena.left + 30, self.arena.right - 30)
                y = random.randint(self.arena.top + 30, self.arena.bottom - 30)

            Explosion((x, y), self.t.exp_size, self.t.exp_tele_ms, self.t.exp_boom_ms, self.t.exp_damage, self.g["all"], self.g["proj"])

    def plan_super_wave(self):
        direction = random.choice(["lr", "rl", "tb", "bt"])
        thick = int(self.t.super_thickness)

        if direction in ("lr", "rl"):
            y = random.randint(self.arena.top + thick // 2, self.arena.bottom - thick // 2)
            wave_rect = pygame.Rect(0, 0, self.arena.w + 700, thick)
            wave_rect.centery = y
            if direction == "lr":
                wave_rect.right = self.arena.left - 80
            else:
                wave_rect.left = self.arena.right + 80
            tele_rect = pygame.Rect(self.arena.left, y - thick // 2, self.arena.w, thick)
        else:
            x = random.randint(self.arena.left + thick // 2, self.arena.right - thick // 2)
            wave_rect = pygame.Rect(0, 0, thick, self.arena.h + 700)
            wave_rect.centerx = x
            if direction == "tb":
                wave_rect.bottom = self.arena.top - 80
            else:
                wave_rect.top = self.arena.bottom + 80
            tele_rect = pygame.Rect(x - thick // 2, self.arena.top, thick, self.arena.h)

        cast_ms = max(int(self.t.super_cast_ms), int(self.t.super_tele_ms))
        Telegraph(tele_rect, cast_ms, self.g["all"], alpha=55)
        self._super_plan = (direction, wave_rect, cast_ms)

    def spawn_super_wave(self):
        direction, wave_rect, _ = self._super_plan
        SuperWave(
            rect=wave_rect,
            direction=direction,
            speed_px_s=self.t.super_speed,
            damage=self.t.super_damage,
            player=self.player,
            arena_rect=self.arena,
            groups_all=self.g["all"],
            alpha=235,
        )

    def spawn_dash_tele(self):
        cx, cy = self.rect.center
        dx, dy = self._dash_dir
        length = 220
        w = 34
        r = pygame.Rect(0, 0, length, w)
        r.center = (int(cx + dx * (length * 0.5)), int(cy + dy * (length * 0.5)))
        Telegraph(r.inflate(20, 12), self.t.dash_windup_ms, self.g["all"], alpha=55)

    def start_dash_hitbox(self):
        self._dash_hitbox_sprite = DashChargeHitbox(
            owner=self,
            size=self.t.dash_hitbox,
            damage=self.t.dash_damage,
            ttl_ms=self.t.dash_duration_ms,
            groups_all=self.g["all"],
            groups_melee=self.g["melee"],
            alpha=170,
        )

    # ---------- movement ----------

    def _move_with_collisions(self, vx: float, vy: float, dt_s: float):
        ox, oy = self.fx, self.fy

        self.fx += vx * dt_s
        self.rect.x = int(self.fx)
        if pygame.sprite.spritecollideany(self, self.walls, collided=pygame.sprite.collide_rect):
            self.fx = ox
            self.rect.x = int(self.fx)

        self.fy += vy * dt_s
        self.rect.y = int(self.fy)
        if pygame.sprite.spritecollideany(self, self.walls, collided=pygame.sprite.collide_rect):
            self.fy = oy
            self.rect.y = int(self.fy)

        self.rect.clamp_ip(self.arena)
        self.fx = float(self.rect.x)
        self.fy = float(self.rect.y)

    def chase(self, dt_s: float):
        if not hasattr(self.player, "rect"):
            return
        bx, by = self.rect.center
        px, py = self.player.rect.center
        dx, dy = (px - bx, py - by)
        ndx, ndy = normalize(dx, dy)

        if ndx != 0.0 or ndy != 0.0:
            self.facing = (ndx, ndy)

        spd = self.speed()
        self._move_with_collisions(ndx * spd, ndy * spd, dt_s)

    def dash_move(self, dt_s: float):
        dx, dy = self._dash_dir
        self._move_with_collisions(dx * self.t.dash_speed, dy * self.t.dash_speed, dt_s)

    # ---------- update ----------

    def update(self, *args):
        if self.dead:
            return

        t = now_ms()
        dt_s = max(0.0, (t - self._last) / 1000.0)
        self._last = t

        self.update_visual()

        # resolve estado quando timer acaba
        if self.state != "idle" and t >= self.state_until:
            if self.state == "melee_windup":
                self.spawn_melee_hit()
            elif self.state == "jump_windup":
                self.spawn_slam_hit()
                self.spawn_waves()
            elif self.state == "exp_cast":
                self.cast_explosions()
            elif self.state == "super_cast":
                self.spawn_super_wave()
            elif self.state == "dash_windup":
                self.start_dash_hitbox()
                self.begin("dash_move", self.t.dash_duration_ms)
                return
            elif self.state == "dash_move":
                self._dash_hitbox_sprite = None

            self.state = "idle"

        # dash contínuo
        if self.state == "dash_move":
            self.dash_move(dt_s)
            return

        # super 10% (1x)
        if (not self._scripted_done) and (self.hp <= self.t.scripted_threshold_hp):
            self._scripted_done = True
            self.plan_super_wave()
            _, _, cast_ms = self._super_plan
            self.begin("super_cast", cast_ms)
            return

        # melee se perto
        if self.dist_to_player() <= self.t.melee_range and t >= self.next_melee:
            self.next_melee = t + self.t.melee_cd_ms
            self.spawn_melee_tele()
            self.begin("melee_windup", self.t.melee_windup_ms)
            return

        # dash (hp < 35%)
        if self.hp <= int(self.max_hp * 0.35) and t >= self.next_dash:
            self.next_dash = t + self.dash_cd()

            if hasattr(self.player, "rect"):
                bx, by = self.rect.center
                px, py = self.player.rect.center
                self._dash_dir = normalize(px - bx, py - by)
                if self._dash_dir == (0.0, 0.0):
                    self._dash_dir = self.facing
            else:
                self._dash_dir = self.facing

            if self._dash_dir == (0.0, 0.0):
                self._dash_dir = (1.0, 0.0)

            self.spawn_dash_tele()
            self.begin("dash_windup", self.t.dash_windup_ms)
            return

        # jump slam
        if t >= self.next_jump:
            self.next_jump = t + self.jump_cd()
            self.spawn_slam_tele()
            self.begin("jump_windup", self.t.jump_windup_ms)
            return

        # explosões (hp < 50%)
        if self.hp < (self.max_hp // 2) and t >= self.next_exp:
            self.next_exp = t + self.exp_cd()
            self.begin("exp_cast", self.t.exp_cast_windup_ms)
            return

        # chase
        self.chase(dt_s)


class DemonSlimeBoss(SlimeBoss):
    """Adapter pra manter o main igual."""
    def __init__(self, x, y, player, groups_for_enemy, screen_rect):
        super().__init__(x=x, y=y, player=player, groups_for_enemy=groups_for_enemy, arena_rect=screen_rect)