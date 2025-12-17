import os, pygame, math, heapq

# ---------------------------
# Floating damage numbers
# ---------------------------
_DMG_FONT: pygame.font.Font | None = None

def _get_dmg_font() -> pygame.font.Font:
    global _DMG_FONT
    if _DMG_FONT is None:
        if not pygame.font.get_init():
            pygame.font.init()
        _DMG_FONT = pygame.font.Font(None, 24)
    return _DMG_FONT

class DamageNumber(pygame.sprite.Sprite):
    def __init__(self, x: int, y: int, value: int, *, crit: bool = False, duration_ms: int = 650):
        super().__init__()
        self.value = int(value)
        self.crit = bool(crit)
        self.spawn = pygame.time.get_ticks()
        self.duration_ms = int(duration_ms)
        self.blink_ms = 90
        self.float_speed = 0.85

        # Normal = yellow/white blink; Crit = red/white blink
        self.c1 = (255, 220, 0) if not self.crit else (255, 60, 60)
        self.c2 = (255, 255, 255)

        self.pos = pygame.Vector2(x, y)
        self._last_blink_bucket = -1
        self.image = pygame.Surface((1, 1), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(x, y))
        self._rerender(force=True)

    def _rerender(self, force: bool = False):
        now = pygame.time.get_ticks()
        bucket = (now - self.spawn) // self.blink_ms
        if not force and bucket == self._last_blink_bucket:
            return
        self._last_blink_bucket = bucket

        color = self.c1 if (bucket % 2 == 0) else self.c2
        font = _get_dmg_font()
        txt = font.render(str(self.value), True, color)
        # small outline for readability
        outline = font.render(str(self.value), True, (0, 0, 0))
        w, h = txt.get_size()
        surf = pygame.Surface((w + 2, h + 2), pygame.SRCALPHA)
        surf.blit(outline, (2, 2))
        surf.blit(outline, (0, 2))
        surf.blit(outline, (2, 0))
        surf.blit(outline, (0, 0))
        surf.blit(txt, (1, 1))
        center = self.rect.center
        self.image = surf
        self.rect = self.image.get_rect(center=center)

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.spawn > self.duration_ms:
            self.kill()
            return
        self.pos.y -= self.float_speed
        self.rect.center = (int(self.pos.x), int(self.pos.y))
        self._rerender()


WIDTH, HEIGHT = 1200, 800
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SCREEN_RECT = pygame.Rect(0, 0, WIDTH, HEIGHT)

def resolve_enemy_assets_dir() -> str:
    candidates = [
        os.path.join(SCRIPT_DIR, "Enemy_Animation_Set"),
        os.path.join(SCRIPT_DIR, "Enemy_Animations_Set"),
        os.path.join(SCRIPT_DIR, "enemy_animation_set"),
        os.path.join(SCRIPT_DIR, "enemy_animations_set"),
    ]
    for c in candidates:
        if os.path.isdir(c):
            return c
    return os.path.join(SCRIPT_DIR, "Enemy_Animation_Set")

ENEMY_ASSETS_DIR = resolve_enemy_assets_dir()

BASE_ENEMY_SCALE = 3.0

GHOST_DIVISOR = 4.25
GHOST_SCALE = (BASE_ENEMY_SCALE / GHOST_DIVISOR) * 0.75 * 0.70  # -30% extra
FIREBALL_SCALE = 2.0 * 1.40  # 2x e +40%

ENEMY_SPEED_MULT = 1.5
ENEMY_DAMAGE_MULT = 1.5

ACTIVATION_HALF = 600          # 1200x1200
VISION_MEMORY_MS = 5000        # memória de visão
PATH_CELL = 24                 # melhor contorno de paredes

KNOCKBACK_STRENGTH = 22.0
KNOCKBACK_DECAY = 0.82
KNOCKBACK_MIN = 0.5

ENEMY_SHEET_DICT = {
    "skeleton1": {
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

# -----------------------------
# Corte simples (igual sua ideia)
# -----------------------------
class SpriteSheet:
    def __init__(self, image: pygame.Surface):
        self.sheet = image

    def get_image(self, frame: int, width: int, height: int, scale: float, colour=None) -> pygame.Surface:
        image = pygame.Surface((width, height), pygame.SRCALPHA).convert_alpha()
        image.blit(self.sheet, (0, 0), (frame * width, 0, width, height))
        if scale != 1:
            image = pygame.transform.scale(image, (int(width * scale), int(height * scale)))
        if colour is not None:
            image.set_colorkey(colour)
        return image

def slice_strip_simple(raw: pygame.Surface, cols_hint: int, rows_hint: int, scale: float) -> list[pygame.Surface]:
    """
    Simples e robusto:
    - Se rows_hint == 1: assume frames QUADRADOS de lado = altura do sheet.
      (muito comum e evita erro quando sobra margem no final)
    - Caso contrário: cai no modo clássico width//cols.
    """
    sheet = SpriteSheet(raw)
    rows = max(1, rows_hint)

    if rows == 1:
        frame_h = raw.get_height()
        frame_w = frame_h  # ✅ quadrado
        count = max(1, raw.get_width() // frame_w)
    else:
        frame_h = raw.get_height() // rows
        frame_w = raw.get_width() // max(1, cols_hint)
        count = max(1, cols_hint * rows)

    frames = []
    for i in range(count):
        frames.append(sheet.get_image(i, frame_w, frame_h, scale, None))

    # corta frames totalmente vazios no fim
    i = len(frames) - 1
    while i >= 0 and pygame.mask.from_surface(frames[i]).count() == 0:
        i -= 1
    return frames[:i+1] if i >= 0 else frames

def has_los(p1: tuple[int, int], p2: tuple[int, int], walls_group) -> bool:
    if not walls_group:
        return True
    for w in walls_group:
        if w.rect.clipline(p1, p2):
            return False
    return True

def move_rect_with_walls(rect: pygame.Rect, dx: int, dy: int, walls_group) -> pygame.Rect:
    rect.x += dx
    if walls_group:
        for w in walls_group:
            if rect.colliderect(w.rect):
                if dx > 0:
                    rect.right = w.rect.left
                elif dx < 0:
                    rect.left = w.rect.right

    rect.y += dy
    if walls_group:
        for w in walls_group:
            if rect.colliderect(w.rect):
                if dy > 0:
                    rect.bottom = w.rect.top
                elif dy < 0:
                    rect.top = w.rect.bottom

    rect.clamp_ip(SCREEN_RECT)
    return rect

# -----------------------------
# A* melhorado (menos “burro”)
# -----------------------------
class AStarGrid:
    def __init__(self, walls_group, cell: int = PATH_CELL):
        self.cell = cell
        self.cols = max(1, WIDTH // cell)
        self.rows = max(1, HEIGHT // cell)

        self.blocked = [[False for _ in range(self.cols)] for _ in range(self.rows)]
        if walls_group:
            for r in range(self.rows):
                cy = r * cell + cell // 2
                for c in range(self.cols):
                    cx = c * cell + cell // 2
                    # ✅ muito melhor: bloqueia se o CENTRO cair dentro da parede
                    for w in walls_group:
                        if w.rect.collidepoint(cx, cy):
                            self.blocked[r][c] = True
                            break

    def in_bounds(self, r, c):
        return 0 <= r < self.rows and 0 <= c < self.cols

    def passable(self, r, c):
        return self.in_bounds(r, c) and (not self.blocked[r][c])

    def to_cell(self, x, y):
        c = max(0, min(self.cols - 1, x // self.cell))
        r = max(0, min(self.rows - 1, y // self.cell))
        return (r, c)

    def to_world_center(self, r, c):
        x = c * self.cell + self.cell // 2
        y = r * self.cell + self.cell // 2
        return (x, y)

    def nearest_free(self, r, c, max_radius=10):
        if self.passable(r, c):
            return (r, c)
        for rad in range(1, max_radius + 1):
            for dr in range(-rad, rad + 1):
                for dc in range(-rad, rad + 1):
                    rr, cc = r + dr, c + dc
                    if self.passable(rr, cc):
                        return (rr, cc)
        return (r, c)

    def heuristic(self, a, b):
        (r1, c1) = a
        (r2, c2) = b
        return abs(r1 - r2) + abs(c1 - c2)

    def neighbors8(self, node):
        r, c = node
        cand = [
            (r-1, c), (r+1, c), (r, c-1), (r, c+1),
            (r-1, c-1), (r-1, c+1), (r+1, c-1), (r+1, c+1),
        ]
        out = []
        for rr, cc in cand:
            if self.passable(rr, cc):
                out.append((rr, cc))
        return out

    def astar(self, start, goal, limit=8000):
        start = self.nearest_free(*start)
        goal = self.nearest_free(*goal)
        if start == goal:
            return [start]

        pq = []
        heapq.heappush(pq, (0, start))
        came = {start: None}
        cost = {start: 0}

        it = 0
        while pq and it < limit:
            it += 1
            _, cur = heapq.heappop(pq)

            if cur == goal:
                break

            for nb in self.neighbors8(cur):
                # diagonal custa 1.4 (mais natural)
                dr = abs(nb[0] - cur[0])
                dc = abs(nb[1] - cur[1])
                step = 1.4 if (dr == 1 and dc == 1) else 1.0

                new_cost = cost[cur] + step
                if nb not in cost or new_cost < cost[nb]:
                    cost[nb] = new_cost
                    pr = new_cost + self.heuristic(nb, goal)
                    heapq.heappush(pq, (pr, nb))
                    came[nb] = cur

        if goal not in came:
            return [start]

        path = []
        cur = goal
        while cur is not None:
            path.append(cur)
            cur = came[cur]
        path.reverse()
        return path

# -----------------------------
# Projétil do fantasma
# -----------------------------
_GHOST_FIREBALL_FRAMES: list[pygame.Surface] | None = None

def load_ghost_fireball_frames() -> list[pygame.Surface]:
    global _GHOST_FIREBALL_FRAMES
    if _GHOST_FIREBALL_FRAMES is not None:
        return _GHOST_FIREBALL_FRAMES

    path = os.path.join(ENEMY_ASSETS_DIR, "ghost_energyball.png")
    try:
        raw = pygame.image.load(path).convert_alpha()
        # aqui o sheet é 1 linha (10 frames) → recorte simples
        frames = slice_strip_simple(raw, cols_hint=10, rows_hint=1, scale=FIREBALL_SCALE)
        if not frames:
            raise RuntimeError("Sem frames em ghost_energyball.png")
    except Exception as e:
        print(f"[Ghost fireball] fallback: {e}")
        s = pygame.Surface((48, 48), pygame.SRCALPHA)
        pygame.draw.circle(s, (255, 140, 0), (24, 24), 22)
        pygame.draw.circle(s, (255, 230, 180), (18, 18), 8)
        frames = [s]

    _GHOST_FIREBALL_FRAMES = frames
    return _GHOST_FIREBALL_FRAMES

class EnemyFireball(pygame.sprite.Sprite):
    def __init__(self, x, y, vx, vy, damage=8):
        super().__init__()
        self.frames = load_ghost_fireball_frames()
        self.frame_index = 0
        self.anim_speed_ms = 60
        self.last_anim = pygame.time.get_ticks()

        self.image = self.frames[0]
        self.rect = self.image.get_rect(center=(x, y))
        self.mask = pygame.mask.from_surface(self.image)

        self.vx = float(vx)
        self.vy = float(vy)
        self.damage = int(damage)

    def update(self):
        self.rect.x += int(self.vx)
        self.rect.y += int(self.vy)

        now = pygame.time.get_ticks()
        if len(self.frames) > 1 and (now - self.last_anim) >= self.anim_speed_ms:
            self.last_anim = now
            self.frame_index = (self.frame_index + 1) % len(self.frames)
            old = self.rect.center
            self.image = self.frames[self.frame_index]
            self.rect = self.image.get_rect(center=old)
            self.mask = pygame.mask.from_surface(self.image)

        if (
            self.rect.right < -120 or self.rect.left > WIDTH + 120 or
            self.rect.bottom < -120 or self.rect.top > HEIGHT + 120
        ):
            self.kill()

class EnemyMeleeHitbox(pygame.sprite.Sprite):
    def __init__(self, owner, w, h, duration_ms, damage, offset_x=0, offset_y=0, damage_delay=0):
        super().__init__()
        self.owner = owner
        self.hit_list = []

        self.image = pygame.Surface((w, h), pygame.SRCALPHA)
        self.image.fill((255, 0, 0, 70))
        self.rect = self.image.get_rect(center=owner.rect.center)
        self.mask = pygame.mask.from_surface(self.image)

        self.damage = int(damage)
        self.creation_time = pygame.time.get_ticks()
        self.lifetime = int(duration_ms)
        self.damage_delay = int(damage_delay)
        self.is_active = False

        self.rect.centerx += int(offset_x)
        self.rect.centery += int(offset_y)

    def update(self):
        now = pygame.time.get_ticks()
        alive = now - self.creation_time

        if getattr(self.owner, "action", "") != "death":
            self.rect.center = self.owner.rect.center

        if (not self.is_active) and alive >= self.damage_delay:
            if "melee" in self.owner.groups:
                self.owner.groups["melee"].add(self)
            self.is_active = True
            self.image.fill((255, 0, 0, 180))
            self.mask = pygame.mask.from_surface(self.image)

        if alive > self.lifetime:
            self.kill()

# -----------------------------
# Base Enemy
# -----------------------------
class EnemyBase(pygame.sprite.Sprite):
    def __init__(self, x, y, player_ref, groups_dict):
        super().__init__()
        self.player = player_ref
        self.groups = groups_dict
        self.walls = groups_dict.get("walls", None)

        self.grid: AStarGrid | None = None
        self.next_grid_rebuild = 0

        self.path: list[tuple[int, int]] = []
        self.path_i = 0
        self.next_path_update = 0

        self.hp = 1
        self.attack_damage = 1
        self.speed = 1

        self.active = False
        self.visible_now = False
        self.last_seen_time = -10_000_000
        self.last_known_player_pos = self.player.rect.center

        self.action = "idle"
        self.flip = False
        self.frame_index = 0
        self.anim_speed = 70
        self.last_anim_update = pygame.time.get_ticks()

        self.animations: dict[str, list[pygame.Surface]] = {}
        self.load_all_assets()

        self.image = self.animations.get("idle", [self._fallback()])[0]
        self.rect = self.image.get_rect(center=(x, y))
        self.mask = pygame.mask.from_surface(self.image)

        self.kbx = 0.0
        self.kby = 0.0

    def _fallback(self, color=(0, 0, 0, 0)):
        s = pygame.Surface((50, 50), pygame.SRCALPHA)
        s.fill(color)
        pygame.draw.rect(s, (255, 255, 255, 140), s.get_rect(), 2)
        return s

    def load_all_assets(self):
        if not getattr(self, "sprite_name", None):
            self.animations = {"idle": [self._fallback()]}
            return

        actions = ["idle", "move", "attack", "hited", "death"]
        prefix = self.sprite_name

        for action in actions:
            filename = os.path.join(ENEMY_ASSETS_DIR, f"{prefix}_{action}.png")
            try:
                raw = pygame.image.load(filename).convert_alpha()
                layout = ENEMY_SHEET_DICT.get(prefix, {}).get(action, {"cols": 1, "rows": 1})
                cols = layout.get("cols", 1)
                rows = layout.get("rows", 1)

                # ✅ corte simples (importante!)
                frames = slice_strip_simple(raw, cols_hint=cols, rows_hint=rows, scale=getattr(self, "scale", BASE_ENEMY_SCALE))
                self.animations[action] = frames if frames else [self._fallback()]
            except Exception as e:
                print(f"[Enemy assets] {prefix}/{action}: {e}")
                self.animations[action] = [self._fallback()]

    def update_action(self, new_action: str):
        if new_action != self.action:
            self.action = new_action
            self.frame_index = 0
            self.last_anim_update = pygame.time.get_ticks()

    def animate(self):
        frames = self.animations.get(self.action)
        if not frames:
            return

        now = pygame.time.get_ticks()
        if now - self.last_anim_update > self.anim_speed:
            self.last_anim_update = now
            self.frame_index += 1

            if self.frame_index >= len(frames):
                if self.action == "death":
                    self.kill()
                    return
                if self.action == "hited":
                    self.update_action("idle")
                    return
                self.frame_index = 0

            img = frames[self.frame_index]
            if self.flip:
                img = pygame.transform.flip(img, True, False)

            old = self.rect.center
            self.image = img
            self.rect = self.image.get_rect(center=old)
            self.mask = pygame.mask.from_surface(self.image)

    def apply_knockback(self):
        if abs(self.kbx) < KNOCKBACK_MIN and abs(self.kby) < KNOCKBACK_MIN:
            self.kbx = 0.0
            self.kby = 0.0
            return

        dx = int(round(self.kbx))
        dy = int(round(self.kby))

        if not getattr(self, "ignore_walls", False):
            self.rect = move_rect_with_walls(self.rect, dx, dy, self.walls)
        else:
            self.rect.x += dx
            self.rect.y += dy
            self.rect.clamp_ip(SCREEN_RECT)

        self.kbx *= KNOCKBACK_DECAY
        self.kby *= KNOCKBACK_DECAY

    def take_damage(self, amount: int, source_pos: tuple[int, int] | None = None, crit: bool = False):
        if self.action == "death":
            return

        if source_pos is not None:
            sx, sy = source_pos
            ex, ey = self.rect.center
            dx = ex - sx
            dy = ey - sy
            d = math.hypot(dx, dy) or 1.0
            nx = dx / d
            ny = dy / d
            self.kbx += nx * KNOCKBACK_STRENGTH
            self.kby += ny * KNOCKBACK_STRENGTH

        self.hp -= int(amount)
        # Floating damage number
        if "all" in self.groups:
            dn = DamageNumber(self.rect.centerx, self.rect.top - 10, int(amount), crit=crit)
            self.groups["all"].add(dn)

        if self.hp <= 0:
            self.hp = 0
            self.update_action("death")
        else:
            self.update_action("hited")

    def update_visibility_memory(self):
        now = pygame.time.get_ticks()
        dx = self.rect.centerx - self.player.rect.centerx
        dy = self.rect.centery - self.player.rect.centery
        in_activation = (abs(dx) <= ACTIVATION_HALF and abs(dy) <= ACTIVATION_HALF)

        self.visible_now = False
        if in_activation:
            # ✅ Fantasma (ignore_walls=True) enxerga o player através das paredes
            if getattr(self, "ignore_walls", False):
                self.visible_now = True
            else:
                self.visible_now = has_los(self.player.rect.center, self.rect.center, self.walls)

        if self.visible_now:
            self.last_seen_time = now
            self.last_known_player_pos = self.player.rect.center
            self.active = True
        else:
            self.active = (now - self.last_seen_time <= VISION_MEMORY_MS)

    def rebuild_grid_if_needed(self):
        now = pygame.time.get_ticks()
        if self.walls is None or getattr(self, "ignore_walls", False):
            self.grid = None
            return
        if self.grid is None or now >= self.next_grid_rebuild:
            self.grid = AStarGrid(self.walls, cell=PATH_CELL)
            self.next_grid_rebuild = now + 1200  # um pouco mais rápido

    def compute_path_to(self, target_pos: tuple[int, int]):
        self.rebuild_grid_if_needed()
        if self.grid is None:
            self.path = []
            self.path_i = 0
            return

        ex, ey = self.rect.center
        tx, ty = target_pos
        start = self.grid.to_cell(ex, ey)
        goal = self.grid.to_cell(tx, ty)
        self.path = self.grid.astar(start, goal)
        self.path_i = 0

    def next_waypoint(self) -> tuple[int, int] | None:
        if not self.path or self.grid is None:
            return None
        idx = min(self.path_i + 1, len(self.path) - 1)
        r, c = self.path[idx]
        return self.grid.to_world_center(r, c)

    def move_towards(self, tx: int, ty: int, speed: int):
        ex, ey = self.rect.center
        dx = tx - ex
        dy = ty - ey
        dist = math.hypot(dx, dy)
        if dist < 1:
            return

        vx = dx / dist
        vy = dy / dist
        step_x = int(round(vx * speed))
        step_y = int(round(vy * speed))

        if getattr(self, "ignore_walls", False):
            self.rect.x += step_x
            self.rect.y += step_y
            self.rect.clamp_ip(SCREEN_RECT)
            return

        # move com colisão, tentando eixo X e Y
        old = self.rect.copy()
        self.rect = move_rect_with_walls(self.rect, step_x, 0, self.walls)
        if self.rect.topleft == old.topleft:
            self.rect = move_rect_with_walls(self.rect, 0, step_y, self.walls)
        else:
            self.rect = move_rect_with_walls(self.rect, 0, step_y, self.walls)

    def chase_target_smart(self, target_pos: tuple[int, int]):
        now = pygame.time.get_ticks()

        # fantasma ignora paredes → vai direto
        if getattr(self, "ignore_walls", False):
            self.move_towards(target_pos[0], target_pos[1], self.speed)
            return

        if now >= self.next_path_update or not self.path:
            self.compute_path_to(target_pos)
            self.next_path_update = now + 450  # ✅ mais responsivo

        wp = self.next_waypoint()
        if wp is None:
            self.move_towards(target_pos[0], target_pos[1], self.speed)
            return

        self.move_towards(wp[0], wp[1], self.speed)

        if math.hypot(wp[0] - self.rect.centerx, wp[1] - self.rect.centery) < 18:
            self.path_i = min(self.path_i + 1, len(self.path) - 1)

    def update_ai(self):
        pass

    def update(self):
        self.apply_knockback()

        if self.action in ("death", "hited"):
            self.animate()
            return

        self.update_visibility_memory()
        if not self.active:
            self.update_action("idle")
            self.animate()
            return

        self.update_ai()
        self.animate()

# -----------------------------
# Skeleton (para e bate; sem bug de animação)
# -----------------------------
class SkeletonEnemy(EnemyBase):
    def __init__(self, x, y, player_ref, groups_dict):
        self.sprite_name = "skeleton1"
        self.scale = BASE_ENEMY_SCALE
        self.ignore_walls = False
        super().__init__(x, y, player_ref, groups_dict)

        self.hp = 60
        self.attack_damage = int(round(25 * ENEMY_DAMAGE_MULT))
        self.speed = int(round(4 * ENEMY_SPEED_MULT))

        self.state = "CHASE"
        self.state_timer = 0

        self.charge_time = int(900 * 0.7)
        self.spin_time = int(900 * 0.7)
        self.cooldown_time = int(600 * 0.7)
        self.spin_damage_delay = int(650 * 0.7)
        self._spin_spawned = False

    def update_ai(self):
        now = pygame.time.get_ticks()

        dx = (self.player.rect.centerx - self.rect.centerx)
        self.flip = dx < 0

        target = self.player.rect.center if self.visible_now else self.last_known_player_pos
        dist = math.hypot(target[0] - self.rect.centerx, target[1] - self.rect.centery)

        if self.state == "CHASE":
            self._spin_spawned = False
            self.update_action("move")

            if dist > 80:
                self.chase_target_smart(target)
            else:
                # só começa ataque se estiver vendo AGORA
                if self.visible_now:
                    self.state = "CHARGING"
                    self.state_timer = now
                    self.update_action("idle")
                else:
                    self.update_action("idle")

        elif self.state == "CHARGING":
            self.update_action("idle")
            if now - self.state_timer >= self.charge_time:
                self.state = "SPIN"
                self.state_timer = now
                self.update_action("attack")
                self._spin_spawned = False

        elif self.state == "SPIN":
            # ✅ SEM andar durante o ataque
            self.update_action("attack")
            if not self._spin_spawned:
                self._spin_spawned = True
                spin = EnemyMeleeHitbox(self, 192, 192, self.spin_time, self.attack_damage, damage_delay=self.spin_damage_delay)
                self.groups["all"].add(spin)

            if now - self.state_timer >= self.spin_time:
                self.state = "COOLDOWN"
                self.state_timer = now
                self.update_action("idle")

        elif self.state == "COOLDOWN":
            self.update_action("idle")
            if now - self.state_timer >= self.cooldown_time:
                self.state = "CHASE"

        self.rect.clamp_ip(SCREEN_RECT)

class VampireEnemy(EnemyBase):
    def __init__(self, x, y, player_ref, groups_dict):
        self.sprite_name = "vampire"
        self.scale = BASE_ENEMY_SCALE
        self.ignore_walls = False
        super().__init__(x, y, player_ref, groups_dict)

        self.hp = 80
        self.attack_damage = int(round(35 * ENEMY_DAMAGE_MULT))
        self.speed = int(round(2 * ENEMY_SPEED_MULT))

        self.state = "CHASE"
        self.state_timer = 0

        self.bite_prep = 900
        self.bite_duration = 1400
        self.bite_delay = 900
        self._bite_spawned = False

    def update_ai(self):
        now = pygame.time.get_ticks()

        dx = (self.player.rect.centerx - self.rect.centerx)
        self.flip = dx < 0

        target = self.player.rect.center if self.visible_now else self.last_known_player_pos
        dist = math.hypot(target[0] - self.rect.centerx, target[1] - self.rect.centery)

        if self.state == "CHASE":
            self._bite_spawned = False
            self.update_action("move")

            if dist > 130:
                self.chase_target_smart(target)
            else:
                if self.visible_now:
                    self.state = "BITE_PREP"
                    self.state_timer = now
                    self.update_action("idle")
                else:
                    self.update_action("idle")

        elif self.state == "BITE_PREP":
            self.update_action("idle")
            if now - self.state_timer >= self.bite_prep:
                self.state = "BITE"
                self.state_timer = now
                self.update_action("attack")
                self._bite_spawned = False

        elif self.state == "BITE":
            self.update_action("attack")
            if not self._bite_spawned:
                self._bite_spawned = True
                bite = EnemyMeleeHitbox(self, w=320, h=70, duration_ms=self.bite_duration, damage=self.attack_damage, damage_delay=self.bite_delay)
                self.groups["all"].add(bite)

            if now - self.state_timer >= self.bite_duration:
                self.state = "CHASE"

        self.rect.clamp_ip(SCREEN_RECT)

class GhostEnemy(EnemyBase):
    def __init__(self, x, y, player_ref, groups_dict):
        self.sprite_name = "ghost"
        self.scale = GHOST_SCALE
        self.ignore_walls = True
        super().__init__(x, y, player_ref, groups_dict)

        self.hp = 40
        self.attack_damage = int(round(8 * ENEMY_DAMAGE_MULT))
        self.speed = int(round(2 * ENEMY_SPEED_MULT))

        self.keep_min = 320
        self.keep_max = 560

        self.last_shot = 0
        self.shoot_cooldown_ms = 1600

        self.cast_duration_ms = 520
        self.cast_fire_ms = 180
        self.cast_until = 0
        self.cast_fire_at = 0
        self._cast_fired = False

    def start_cast(self):
        now = pygame.time.get_ticks()
        self.cast_until = now + self.cast_duration_ms
        self.cast_fire_at = now + self.cast_fire_ms
        self._cast_fired = False
        self.update_action("attack")

    def update_ai(self):
        now = pygame.time.get_ticks()

        target = self.player.rect.center if self.visible_now else self.last_known_player_pos
        px, py = target
        ex, ey = self.rect.center
        dx = px - ex
        dy = py - ey
        dist = math.hypot(dx, dy)

        self.flip = dx < 0

        if now < self.cast_until:
            self.update_action("attack")
            if (not self._cast_fired) and now >= self.cast_fire_at and dist > 30:
                self._cast_fired = True
                if dist < 0.001:
                    dist = 1.0
                ux = dx / dist
                uy = dy / dist
                speed = 7.0

                proj = EnemyFireball(self.rect.centerx, self.rect.centery, vx=ux * speed, vy=uy * speed, damage=self.attack_damage)
                self.groups["all"].add(proj)
                if "proj" in self.groups:
                    self.groups["proj"].add(proj)
            return

        self.update_action("move" if dist > 40 else "idle")

        # mantém distância
        if dist > self.keep_max:
            self.move_towards(px, py, self.speed)
        elif dist < self.keep_min:
            if dist < 0.001:
                dist = 1.0
            ux = dx / dist
            uy = dy / dist
            self.rect.centerx -= int(round(ux * self.speed))
            self.rect.centery -= int(round(uy * self.speed))
            self.rect.clamp_ip(SCREEN_RECT)

        # só cast se vendo agora
        if self.visible_now and dist > 160 and (now - self.last_shot) >= self.shoot_cooldown_ms:
            self.last_shot = now
            self.start_cast()

        self.rect.clamp_ip(SCREEN_RECT)

__all__ = ["SkeletonEnemy", "VampireEnemy", "GhostEnemy", "EnemyMeleeHitbox", "EnemyFireball", "ENEMY_SHEET_DICT"]
