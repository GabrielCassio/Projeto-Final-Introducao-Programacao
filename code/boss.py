import os
import pygame
import random
import math

print("--- [BOSS.PY] FINAL: UI Style Health Bar + Fixes ---")

FRAME_H_DEFAULT = 72

# FASE 1: Slime
SLIME_SHEETS = {
    "walk":  {"file": "slime_walk.png", "count": 8, "scale": 0.6},
    "hited": {"file": "slime_hited.png", "count": 6, "scale": 0.6},
    "death": {"file": "metamorforsis.png", "count": 32, "scale": 1.0}
}

# FASE 2: Demônio
DEMON_FOLDERS_CONFIG = {
    "idle": "01_demon_idle",
    "walk": "02_demon_walk",
    "cleave": "03_demon_cleave",
    "take_hit": "04_demon_take_hit",
    "death": "05_demon_death"
}

# FASE 2: Sprites Especiais
SPECIAL_SHEETS_CONFIG = {
    "jump":      {"file": "demon_jump.png",       "cols": 18, "rows": 1, "scale": 0.7}, 
    "wave":      {"file": "fire_wave.png",        "cols": 10, "rows": 1, "scale": 1.6},
    "explosion": {"file": "circle_explosion.png", "cols": 11,  "rows": 1, "scale": 1}
}

DEMON_STATS = {
    "max_hp": 5000,
    "scale": 1, 
    "attack_range": 80,  
    "attack_w": 380, 
    "attack_h": 220, 
    "attack_offset": 80,
    "attack_cooldown_ms": 7000, 
    "speed_base": 3.5, 
    "speed_max": 9.0,
    "charge_time_base": 2000, 
    "charge_time_min": 600,
    
    # Habilidades
    "jump_cooldown_max": 10000,
    "jump_cooldown_min": 5000,
    "jump_max_height": 150, 

    "jump_damage_impact": 80,
    "wave_speed": 11, 
    "wave_damage": 40,
    "explosion_damage": 60,
    "push_force": 20, 
    "external_wave_interval": 2000,
    "explosion_delay_ms": 2000 
}


DEMON_ATTACKS = {
    "cleave": {
        "range": 90,
        "damage": 30,
        "telegraph_ms": 600,  

        "hitbox": {"w": 220, "h": 160, "offset": 80, "inflate": (0, 0)},

        "hit_frame_index": None,
    },

    "jump": {
        "danger": {"count": 6, "w": 120, "h": 120, "duration_ms": 4000},
        "impact": {"radius": 100, "damage": 10},
        "shockwave": {"max_radius": 300, "growth_speed": 30, "push_force": 20},
        "explosion": {"delay_ms": 2000, "damage": 30, "w": 50, "h": 50},
    },

    "wave": {
        "speed": 4,
        "damage": 20,
        "lifetime_px": 1200,
        "hitbox_inflate": (-18, -18),
    },

    "external_wave": {
        "interval_ms": 2000,
        "speed_mul": 0.8,
    },
}


def _attack_rect(origin_center, dir_vec, hb_cfg):
    """Cria um rect na frente do boss, usando offset e tamanho do dicionário."""
    d = pygame.Vector2(dir_vec)
    if d.length() == 0:
        d = pygame.Vector2(1, 0)
    else:
        d = d.normalize()

    r = pygame.Rect(0, 0, hb_cfg["w"], hb_cfg["h"])
    r.center = pygame.Vector2(origin_center) + d * hb_cfg.get("offset", 0)

    inf = hb_cfg.get("inflate", (0, 0))
    if inf != (0, 0):
        r = r.inflate(inf[0], inf[1])

    return r


def _hb(sprite):
    """Retorna hitbox se existir, senão rect (compatível com código antigo)."""
    return getattr(sprite, "hitbox", sprite.rect)


SLIME_STATS = {
    "activation_radius": 200,

    "anim_interval_ms": 110,   
    "speed_base": 1.4,         
    "speed_max": 2.2,          
    "accel": 0.18,             


    "slow_radius": 90,         
    "min_speed_factor_near": 0.45,  

    "knockback_strength": 4.0,
    "knockback_decay": 0.78,    
    "knockback_deadzone": 0.05,

    "flash_ms": 150,
}

_DMG_FONT = None
def _get_dmg_font():
    global _DMG_FONT
    if _DMG_FONT is None:
        if not pygame.font.get_init(): pygame.font.init()
        _DMG_FONT = pygame.font.Font(None, 40)
    return _DMG_FONT

def _find_folder_recursive(start_path, target_folder_name):
    for root, dirs, _ in os.walk(start_path):
        if target_folder_name in dirs: return os.path.join(root, target_folder_name)
    current = start_path
    for _ in range(3):
        parent = os.path.dirname(current)
        if parent == current: break
        for root, dirs, _ in os.walk(parent):
            if target_folder_name in dirs: return os.path.join(root, target_folder_name)
        current = parent
    return None

def _find_file_recursive(root_search, filename):
    if not root_search: return None
    for root, dirs, files in os.walk(root_search):
        for f in files:
            if filename.lower() == f.lower(): return os.path.join(root, f)
    return None

def _resolve_boss_root(start_dir):
    """
    Resolve o root da pasta do boss após a reorganização.
    """
    candidate = os.path.join(start_dir, "assets", "graphics", "enemy", "boss")
    if os.path.isdir(candidate):
        return candidate

    cur = start_dir
    for _ in range(6):
        candidate = os.path.join(cur, "assets", "graphics", "enemy", "boss")
        if os.path.isdir(candidate):
            return candidate
        parent = os.path.dirname(cur)
        if parent == cur: break
        cur = parent

    cur = start_dir
    for _ in range(6):
        enemy_root = os.path.join(cur, "assets", "graphics", "enemy")
        if os.path.isdir(enemy_root):
            found = _find_folder_recursive(enemy_root, "boss")
            if found: return found
        parent = os.path.dirname(cur)
        if parent == cur: break
        cur = parent

    return start_dir

def _slice_sheet(path, cols, rows=1, scale=1.0):
    if not path or not os.path.isfile(path): 
        print(f"[Boss ERROR] Arquivo NÃO encontrado: {path}")
        return []
    try:
        sheet = pygame.image.load(path).convert_alpha()
        sw, sh = sheet.get_size()
        cw, ch = sw // cols, sh // rows
        frames = []
        for i in range(cols):
            s = pygame.Surface((cw, ch), pygame.SRCALPHA)
            s.blit(sheet, (0,0), (i*cw, 0, cw, ch))
            if scale != 1.0: s = pygame.transform.smoothscale(s, (int(cw*scale), int(ch*scale)))
            frames.append(s)
        return frames
    except Exception as e: 
        print(f"[Boss CRITICAL] Erro ao fatiar {path}: {e}")
        return []

def _load_frames_from_folder(root_dir, folder_fragment, scale=1.0):
    target = None
    for root, dirs, _ in os.walk(root_dir):
        for d in dirs:
            if folder_fragment.lower() in d.lower(): target = os.path.join(root, d); break
        if target: break
    if not target: return [pygame.Surface((64,64))]
    frames = []
    if os.path.isdir(target):
        for f in sorted(os.listdir(target)):
            if f.endswith(".png"):
                try:
                    img = pygame.image.load(os.path.join(target, f)).convert_alpha()
                    if scale != 1.0:
                        w, h = img.get_size()
                        img = pygame.transform.smoothscale(img, (int(w*scale), int(h*scale)))
                    frames.append(img)
                except: pass
    return frames if frames else [pygame.Surface((64,64))]



class BossHealthBar(pygame.sprite.Sprite):
    def __init__(self, boss, groups):
        super().__init__()
        if groups:
            if "ui" in groups: groups["ui"].add(self)
            elif "all" in groups: groups["all"].add(self)

        self.boss = boss
        self.screen_rect = boss.screen_rect
        
        self.bar_width = 600 
        self.bar_height = 14 
        

        self.image = pygame.Surface((self.bar_width, self.bar_height), pygame.SRCALPHA)
        self.rect = self.image.get_rect()

    def update(self):
        if not self.boss.alive():
            self.kill()
            return


        is_active = getattr(self.boss, 'active', True) 

        if not is_active:
            self.image = pygame.Surface((0,0))
            return


        self.image = pygame.Surface((self.bar_width, self.bar_height), pygame.SRCALPHA)
        self.image.fill((0, 0, 0, 180)) 
        
        hp_pct = max(0, self.boss.current_hp / self.boss.max_hp)
        fill_width = int(self.bar_width * hp_pct)
        
        if fill_width > 0:
            pygame.draw.rect(self.image, (180, 30, 30), (0, 0, fill_width, self.bar_height))
        
        pygame.draw.rect(self.image, (200, 200, 200), (0, 0, self.bar_width, self.bar_height), 2)
        
        self.rect = self.image.get_rect(midbottom=(self.screen_rect.centerx, self.screen_rect.height - 50))

class DamageNumber(pygame.sprite.Sprite):
    def __init__(self, x, y, value, crit=False):
        super().__init__()
        self.value = int(value)
        self.crit = crit
        self.spawn = pygame.time.get_ticks()
        self.duration_ms = 800
        
        self.color_normal = (255, 50, 50) if self.crit else (255, 220, 0)
        self.color_white = (255, 255, 255)
        
        self.pos = pygame.Vector2(x, y)
        self.image = pygame.Surface((1,1), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(x,y))
        self._rerender()

    def _rerender(self):
        elapsed = pygame.time.get_ticks() - self.spawn
        if (elapsed // 80) % 2 == 0: color = self.color_white
        else: color = self.color_normal

        font = _get_dmg_font()
        txt_str = f"{self.value}!" if self.crit else str(self.value)
        txt = font.render(txt_str, True, color)
        outline = font.render(txt_str, True, (0,0,0))
        
        surf = pygame.Surface((txt.get_width() + 4, txt.get_height() + 4), pygame.SRCALPHA)
        for ox, oy in [(-2,0), (2,0), (0,-2), (0,2)]: surf.blit(outline, (2+ox, 2+oy))
        surf.blit(txt, (2, 2))
        
        self.image = surf
        self.rect = self.image.get_rect(center=(int(self.pos.x), int(self.pos.y)))

    def update(self):
        if pygame.time.get_ticks() - self.spawn > self.duration_ms: self.kill(); return
        self.pos.y -= 1.0 
        self._rerender()

class DangerIndicator(pygame.sprite.Sprite):
    def __init__(self, rect_area, duration_ms, groups):
        super().__init__()
        if groups and "all" in groups:
            groups["all"].add(self)

        self.rect = rect_area
        self.duration = duration_ms
        self.spawn_time = pygame.time.get_ticks()
        self.image = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        self.radius = max(6, min(self.rect.width, self.rect.height) // 6)

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.spawn_time > self.duration:
            self.kill()
            return

        progress = (now - self.spawn_time) / self.duration
        t = 1.0 - (1.0 - progress) * (1.0 - progress)

        fill_alpha   = int(8 + 22 * t)    
        border_alpha = int(24 + 36 * t)  

        self.image.fill((0, 0, 0, 0))
        r = self.image.get_rect()

        pygame.draw.rect(self.image, (255, 0, 0, fill_alpha), r, 0, border_radius=self.radius)
        pygame.draw.rect(self.image, (255, 0, 0, border_alpha), r, 1, border_radius=self.radius)

class ShockwavePush(pygame.sprite.Sprite):
    def __init__(self, center_pos, max_radius, player, groups, push_force=20, growth_speed=30):
        super().__init__()
        if groups and "all" in groups:
            groups["all"].add(self)

        self.center = pygame.Vector2(center_pos)
        self.player = player

        self.max_radius = int(max_radius)
        self.current_radius = 10

        self.growth_speed = float(growth_speed)
        self.push_force = float(push_force)

        self.alpha = 50
        self.image = pygame.Surface((self.max_radius * 2, self.max_radius * 2), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(int(self.center.x), int(self.center.y)))

    def update(self):
        self.current_radius += self.growth_speed

        dim = int(self.current_radius * 2)
        if dim < 4:
            dim = 4

        self.image = pygame.Surface((dim, dim), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (255, 0, 0, 80), (dim // 2, dim // 2), int(self.current_radius), 6)
        self.rect = self.image.get_rect(center=(int(self.center.x), int(self.center.y)))

        p_vec = pygame.Vector2(self.player.rect.center)
        dist = p_vec.distance_to(self.center)

        if dist < self.current_radius:
            push_dir = p_vec - self.center
            if push_dir.length() == 0:
                push_dir = pygame.Vector2(1, 0)
            else:
                push_dir = push_dir.normalize()

            self.player.rect.x += int(push_dir.x * self.push_force)
            self.player.rect.y += int(push_dir.y * self.push_force)

        if self.current_radius >= self.max_radius:
            self.kill()
class CircleExplosion(pygame.sprite.Sprite):
    def __init__(self, center, frames, damage, groups, hitbox_size=None):
        super().__init__()

        if groups:
            if "all" in groups:
                groups["all"].add(self)
            if "proj" in groups:
                groups["proj"].add(self)

        self.damage = int(damage)

        if not frames:
            s = pygame.Surface((100, 100), pygame.SRCALPHA)
            pygame.draw.circle(s, (255, 200, 0), (50, 50), 40)
            self.frames = [s] * 6
        else:
            self.frames = frames

        self.frame_index = 0
        self.last_anim = pygame.time.get_ticks()

        self.image = self.frames[0]
        self.rect = self.image.get_rect(center=center)

        if hitbox_size:
            self.hitbox = pygame.Rect(0, 0, int(hitbox_size[0]), int(hitbox_size[1]))
            self.hitbox.center = self.rect.center
        else:
            self.hitbox = self.rect.copy()

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_anim > 50:
            self.last_anim = now
            self.frame_index += 1
            if self.frame_index >= len(self.frames):
                self.kill()
                return

            self.image = self.frames[self.frame_index]
            self.rect = self.image.get_rect(center=self.rect.center)
            self.hitbox.center = self.rect.center
class FireWave(pygame.sprite.Sprite):
    def __init__(self, x, y, direction_vec, speed, frames, damage, groups,
                 hitbox_inflate=(0, 0), lifetime_px=1200):
        super().__init__()
        if groups:
            if "all" in groups:
                groups["all"].add(self)
            if "proj" in groups:
                groups["proj"].add(self)

        self.damage = int(damage)

        self.pos = pygame.Vector2(x, y)
        self.start_pos = pygame.Vector2(x, y)

        d = pygame.Vector2(direction_vec)
        if d.length() == 0:
            d = pygame.Vector2(1, 0)
        else:
            d = d.normalize()
        self.direction = d

        self.speed = float(speed)
        self.lifetime_px = float(lifetime_px)
        self.hitbox_inflate = (int(hitbox_inflate[0]), int(hitbox_inflate[1]))

        if not frames:
            s = pygame.Surface((40, 40), pygame.SRCALPHA)
            pygame.draw.circle(s, (255, 100, 0), (20, 20), 15)
            self.frames = [s]
        else:
            self.frames = frames

        angle = math.degrees(math.atan2(-self.direction.y, self.direction.x)) + 90
        self.rotated_frames = [pygame.transform.rotate(f, angle) for f in self.frames]

        self.frame_index = 0
        self.last_anim = pygame.time.get_ticks()

        self.image = self.rotated_frames[0]
        self.rect = self.image.get_rect(center=(int(self.pos.x), int(self.pos.y)))

        self.hitbox = self.rect.inflate(self.hitbox_inflate[0], self.hitbox_inflate[1])

    def update(self):
        self.pos += self.direction * self.speed
        self.rect.center = (int(self.pos.x), int(self.pos.y))
        self.hitbox.center = self.rect.center

        now = pygame.time.get_ticks()
        if now - self.last_anim > 80:
            self.last_anim = now
            self.frame_index = (self.frame_index + 1) % len(self.rotated_frames)
            self.image = self.rotated_frames[self.frame_index]

        if self.pos.distance_to(self.start_pos) > self.lifetime_px:
            self.kill()

class DemonBoss(pygame.sprite.Sprite):
    def __init__(self, pos_midbottom, player, groups, screen_rect):
        super().__init__()
        self.player = player
        self.groups_ref = groups
        self.screen_rect = screen_rect

        self.atk = DEMON_ATTACKS

        base = os.path.dirname(os.path.abspath(__file__))
        boss_root = _resolve_boss_root(base)

        sprites_root = _find_folder_recursive(boss_root, "individual sprites")
        self.anims = {}
        if sprites_root:
            for k, folder in DEMON_FOLDERS_CONFIG.items():
                self.anims[k] = _load_frames_from_folder(sprites_root, folder, DEMON_STATS["scale"])
        else:
            for k in DEMON_FOLDERS_CONFIG:
                self.anims[k] = [pygame.Surface((100, 100))]

        sheets_root = _find_folder_recursive(boss_root, "sprite_file")
        self.special_anims = {}
        if sheets_root:
            for key, data in SPECIAL_SHEETS_CONFIG.items():
                path = _find_file_recursive(sheets_root, data["file"])
                if path:
                    self.special_anims[key] = _slice_sheet(path, data["cols"], data["rows"], data["scale"])
                else:
                    self.special_anims[key] = []
        else:
            print("[Boss ERROR] Pasta 'sprite_file' não encontrada")
            self.special_anims = {"jump": [], "wave": [], "explosion": []}

        self.state = "idle"
        self.facing_right = True

        self.max_hp = DEMON_STATS["max_hp"]
        self.current_hp = DEMON_STATS["max_hp"]

        self.frames = self.anims["idle"]
        self.frame_index = 0
        self.last_anim = pygame.time.get_ticks()

        self.image = self.frames[0]
        self.rect = self.image.get_rect(midbottom=pos_midbottom)
        self.mask = pygame.mask.from_surface(self.image)

        self.cooldown_end_time = 0
        self.charge_start_time = 0
        self.attack_vector = pygame.Vector2(1, 0)

        self.is_jumping = False
        self.jump_visual_offset = 0
        self.ground_anchor = self.rect.bottom
        self.pending_explosions = []
        self.last_jump_time = pygame.time.get_ticks()

        self.last_external_wave = pygame.time.get_ticks()

        self.speed = DEMON_STATS["speed_base"]

        self.explosion_trigger_time = 0

        BossHealthBar(self, self.groups_ref)

    def take_damage(self, amount, source_pos=None, crit=False):
        if self.state == "death" or self.is_jumping:
            return

        self.current_hp = max(0, self.current_hp - int(amount))

        if self.groups_ref and "all" in self.groups_ref:
            self.groups_ref["all"].add(
                DamageNumber(self.rect.centerx, self.rect.centery, int(amount), crit=crit)
            )

        if self.current_hp <= 0:
            self.state = "death"
            self.frame_index = 0
        elif self.state not in ["pre_attack", "attacking"]:
            self.state = "take_hit"
            self.frame_index = 0
            self.last_anim = pygame.time.get_ticks()

    def _start_jump(self):
        self.state = "jump_start"
        self.is_jumping = True
        self.last_jump_time = pygame.time.get_ticks()

        self.frame_index = 0
        self.jump_visual_offset = 0

        self.pending_explosions = []
        self.ground_anchor = self.rect.bottom

        j = self.atk["jump"]["danger"]
        for _ in range(j["count"]):
            rx = random.randint(100, self.screen_rect.width - 100)
            ry = random.randint(100, self.screen_rect.height - 100)
            self.pending_explosions.append((rx, ry))

            area = pygame.Rect(0, 0, j["w"], j["h"])
            area.center = (rx, ry)
            DangerIndicator(area, j["duration_ms"], self.groups_ref)

    def _perform_land_impact(self):
        j = self.atk["jump"]


        sw = j["shockwave"]
        ShockwavePush(
            self.rect.center,
            sw["max_radius"],
            self.player,
            self.groups_ref,
            push_force=sw["push_force"],
            growth_speed=sw["growth_speed"],
        )


        wcfg = self.atk["wave"]
        for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            vec = pygame.Vector2(dx, dy)
            FireWave(
                self.rect.centerx,
                self.rect.centery,
                vec,
                wcfg["speed"],
                self.special_anims.get("wave", []),
                wcfg["damage"],
                self.groups_ref,
                hitbox_inflate=wcfg["hitbox_inflate"],
                lifetime_px=wcfg["lifetime_px"],
            )

        imp = j["impact"]
        dist = pygame.Vector2(self.player.rect.center).distance_to(self.rect.center)
        if dist < imp["radius"]:
            if hasattr(self.player, "take_damage"):
                self.player.take_damage(imp["damage"])

        self.explosion_trigger_time = pygame.time.get_ticks() + j["explosion"]["delay_ms"]

    def _manage_external_waves(self, hp_pct, now):
        if hp_pct >= 0.5:
            return

        ext = self.atk["external_wave"]
        if now - self.last_external_wave > ext["interval_ms"]:
            self.last_external_wave = now

            count = 1
            if hp_pct < 0.30:
                count = 2
            if hp_pct < 0.15:
                count = 3

            wcfg = self.atk["wave"]

            for _ in range(count):
                side = random.choice(["top", "bottom", "left", "right"])
                w, h = self.screen_rect.width, self.screen_rect.height

                if side == "top":
                    start = pygame.Vector2(random.randint(0, w), -100)
                elif side == "bottom":
                    start = pygame.Vector2(random.randint(0, w), h + 100)
                elif side == "left":
                    start = pygame.Vector2(-100, random.randint(0, h))
                else:
                    start = pygame.Vector2(w + 100, random.randint(0, h))

                target = pygame.Vector2(self.player.rect.center)
                direction = target - start

                FireWave(
                    start.x,
                    start.y,
                    direction,
                    wcfg["speed"] * ext["speed_mul"],
                    self.special_anims.get("wave", []),
                    wcfg["damage"],
                    self.groups_ref,
                    hitbox_inflate=wcfg["hitbox_inflate"],
                    lifetime_px=wcfg["lifetime_px"],
                )


    def _deal_damage(self):
        cfg = self.atk["cleave"]
        hitbox = _attack_rect(self.rect.center, self.attack_vector, cfg["hitbox"])
        if hitbox.colliderect(self.player.rect):
            if hasattr(self.player, "take_damage"):
                self.player.take_damage(cfg["damage"])

    def update(self):
        now = pygame.time.get_ticks()

        hp_pct = self.current_hp / self.max_hp if self.max_hp else 0.0
        hp_loss = 1.0 - hp_pct
        self.speed = DEMON_STATS["speed_base"] + (DEMON_STATS["speed_max"] - DEMON_STATS["speed_base"]) * hp_loss

        self._manage_external_waves(hp_pct, now)

        if self.explosion_trigger_time > 0 and now >= self.explosion_trigger_time:
            jexp = self.atk["jump"]["explosion"]
            for pos in self.pending_explosions:
                CircleExplosion(
                    pos,
                    self.special_anims.get("explosion", []),
                    jexp["damage"],
                    self.groups_ref,
                    hitbox_size=(jexp["w"], jexp["h"]),
                )
            self.pending_explosions.clear()
            self.explosion_trigger_time = 0


        if self.is_jumping:
            if now - self.last_anim > 80:
                self.last_anim = now

                if self.state == "jump_start":
                    self.frame_index += 1
                    progress = self.frame_index / 6.0
                    self.jump_visual_offset = -int(DEMON_STATS["jump_max_height"] * progress)

                    if self.frame_index > 5:
                        self.state = "jump_air"
                        self.frame_index = 6
                        self.jump_visual_offset = -DEMON_STATS["jump_max_height"]

                elif self.state == "jump_air":
                    self.frame_index += 1
                    self.jump_visual_offset = -DEMON_STATS["jump_max_height"]

                    if (now - self.last_jump_time) > 1500:
                        self.state = "jump_land"
                        self.frame_index = 12
                    elif self.frame_index > 11:
                        self.frame_index = 6

                elif self.state == "jump_land":
                    self.frame_index += 1
                    land_progress = (self.frame_index - 12) / 5.0
                    self.jump_visual_offset = -int(DEMON_STATS["jump_max_height"] * (1.0 - land_progress))

                    if self.frame_index == 14:
                        self._perform_land_impact()

                    if self.frame_index >= 17:
                        self.is_jumping = False
                        self.state = "cooldown_chase"
                        self.cooldown_end_time = now + 1500

                        self.frame_index = 0
                        self.jump_visual_offset = 0
                        self.frames = self.anims["idle"]
                        self.rect.bottom = self.ground_anchor
                        return

            jump_frames = self.special_anims.get("jump", [])
            if jump_frames:
                idx = min(self.frame_index, len(jump_frames) - 1)
                img = jump_frames[idx]
                img = pygame.transform.flip(img, self.facing_right, False)
                self.image = img
                self.rect.bottom = self.ground_anchor + int(self.jump_visual_offset)
            return

        current_jump_cd = DEMON_STATS["jump_cooldown_max"] - (
            (DEMON_STATS["jump_cooldown_max"] - DEMON_STATS["jump_cooldown_min"]) * hp_loss
        )

        if self.state in ["chase", "idle"] and (now - self.last_jump_time) > current_jump_cd:
            self._start_jump()
            return

        STATE_TO_ANIM = {
            "idle": "idle",
            "chase": "walk",
            "cooldown_chase": "walk",
            "pre_attack": "idle",
            "attacking": "cleave",
            "take_hit": "take_hit",
            "death": "death",
        }
        anim_key = STATE_TO_ANIM.get(self.state, "idle")
        frames = self.anims.get(anim_key, self.anims["idle"])

        if self.frames != frames:
            self.frames = frames
            self.frame_index = 0

        if now - self.last_anim > 100:
            self.last_anim = now

            if self.state == "death":
                if self.frame_index < len(frames) - 1:
                    self.frame_index += 1
                else:
                    self.kill()
                    return

            elif self.state == "take_hit":
                if self.frame_index < len(frames) - 1:
                    self.frame_index += 1
                else:
                    self.state = "chase"

            elif self.state == "attacking":
                if self.frame_index < len(frames) - 1:
                    self.frame_index += 1

                    cfg = self.atk["cleave"]
                    hit_frame = cfg["hit_frame_index"]
                    if hit_frame is None:
                        hit_frame = len(frames) // 2

                    if self.frame_index == hit_frame:
                        self._deal_damage()

                else:
                    self.state = "cooldown_chase"
                    self.cooldown_end_time = now + DEMON_STATS["attack_cooldown_ms"]

            else:
                self.frame_index = (self.frame_index + 1) % len(frames)

        if self.state == "idle":
            self.state = "chase"

        if self.state == "chase":
            p_vec = pygame.Vector2(self.player.rect.center)
            m_vec = pygame.Vector2(self.rect.center)
            diff = p_vec - m_vec
            dist = diff.length()

            cfg = self.atk["cleave"]

            if dist < cfg["range"]:
                self.state = "pre_attack"
                self.charge_start_time = now

                if dist > 0:
                    self.attack_vector = diff.normalize()
                else:
                    self.attack_vector = pygame.Vector2(1, 0)

                tele_hitbox = _attack_rect(self.rect.center, self.attack_vector, cfg["hitbox"])
                DangerIndicator(tele_hitbox, cfg["telegraph_ms"], self.groups_ref)

            else:
                if dist > 0:
                    direction = diff.normalize()
                    if direction.x != 0:
                        self.facing_right = direction.x > 0
                    self.rect.center += direction * self.speed

        elif self.state == "pre_attack":
            cfg = self.atk["cleave"]
            if now - self.charge_start_time > cfg["telegraph_ms"]:
                self.state = "attacking"
                self.frame_index = 0

        elif self.state == "cooldown_chase":
            p_vec = pygame.Vector2(self.player.rect.center)
            m_vec = pygame.Vector2(self.rect.center)
            diff = p_vec - m_vec

            if diff.length() > 0:
                direction = diff.normalize()
                if direction.x != 0:
                    self.facing_right = direction.x > 0
                self.rect.center += direction * (self.speed * 0.5)

            if now > self.cooldown_end_time:
                self.state = "chase"

        if self.frame_index >= len(self.frames):
            self.frame_index = 0

        img = self.frames[self.frame_index]
        img = pygame.transform.flip(img, self.facing_right, False)

        old_center = self.rect.center
        self.image = img
        self.rect = self.image.get_rect(center=old_center)
        self.mask = pygame.mask.from_surface(self.image)


class DemonSlimeBoss(pygame.sprite.Sprite):
    def __init__(self, x, y, player, groups, screen_rect):
        super().__init__()
        self.player = player
        self.groups_ref = groups
        self.screen_rect = screen_rect
        self.cfg = SLIME_STATS

        base_dir = os.path.dirname(os.path.abspath(__file__))
        boss_root = _resolve_boss_root(base_dir)

        ba_root = boss_root
        sub = _find_folder_recursive(boss_root, "boss")
        if sub:
            ba_root = sub
        else:
            sub = _find_folder_recursive(boss_root, "boss_animations")
            if sub:
                ba_root = sub

        self.anims = {"walk": [], "hited": [], "death": []}

        try:
            p1 = _find_file_recursive(ba_root, SLIME_SHEETS["walk"]["file"])
            self.anims["walk"] = _slice_sheet(
                p1,
                SLIME_SHEETS["walk"]["count"],
                scale=SLIME_SHEETS["walk"]["scale"]
            )
        except Exception:
            self.anims["walk"] = []

        try:
            p2 = _find_file_recursive(ba_root, SLIME_SHEETS["hited"]["file"])
            self.anims["hited"] = _slice_sheet(
                p2,
                SLIME_SHEETS["hited"]["count"],
                scale=SLIME_SHEETS["hited"]["scale"]
            )
        except Exception:
            self.anims["hited"] = []

        try:
            p3 = _find_file_recursive(ba_root, SLIME_SHEETS["death"]["file"])
            self.anims["death"] = _slice_sheet(
                p3,
                SLIME_SHEETS["death"]["count"],
                scale=SLIME_SHEETS["death"]["scale"]
            )
        except Exception:
            self.anims["death"] = []

        if not self.anims["walk"]:
            self.anims["walk"] = [pygame.Surface((50, 50), pygame.SRCALPHA)]
        if not self.anims["hited"]:
            self.anims["hited"] = self.anims["walk"]
        if not self.anims["death"]:
            self.anims["death"] = self.anims["walk"]

        self.state = "walk"
        self.max_hp = 1000
        self.current_hp = 1000
        self.frame_index = 0
        self.last_anim = pygame.time.get_ticks()

        self.image = self.anims["walk"][0]
        self.rect = self.image.get_rect(center=(x, y))

        self.hitbox_pos = pygame.Vector2(x, y)
        self.facing_right = True
        self.is_dying = False
        self.flash_until = 0
        self.knockback_force = pygame.Vector2(0, 0)

        self.active = False
        self.activation_radius = self.cfg["activation_radius"]

        self._last_update_ms = pygame.time.get_ticks()
        self._speed = self.cfg["speed_base"]

        self.health_bar = BossHealthBar(self, self.groups_ref)

    def check_activation(self):
        if self.active:
            return
        dist = pygame.Vector2(self.player.rect.center).distance_to(self.hitbox_pos)
        if dist < self.activation_radius:
            self.active = True
            print("Boss ACORDOU!")

    def take_damage(self, amount, source_pos=None, crit=False):
        if self.is_dying:
            return

        self.active = True
        self.current_hp -= int(amount)
        self.flash_until = pygame.time.get_ticks() + self.cfg["flash_ms"]

        if "all" in self.groups_ref:
            try:
                self.groups_ref["all"].add(
                    DamageNumber(self.rect.centerx, self.rect.centery, amount, crit)
                )
            except:
                pass

        if source_pos:
            push_dir = self.hitbox_pos - pygame.Vector2(source_pos)
            if push_dir.length() == 0:
                push_dir = pygame.Vector2(1, 0)
            else:
                push_dir = push_dir.normalize()
            self.knockback_force = push_dir * self.cfg["knockback_strength"]

        if self.current_hp <= 0:
            self.is_dying = True
            self.state = "death"
            self.frame_index = 0
            self.knockback_force *= 0

    def _dt_scale_60fps(self, now_ms: int) -> float:
        """Retorna escala de dt onde 1.0 ≈ 1 frame a 60fps."""
        dt_ms = max(1, now_ms - self._last_update_ms)
        self._last_update_ms = now_ms
        dt = dt_ms / 16.6667
        return max(0.25, min(3.0, dt))  # clamp anti-picos

    def _desired_speed(self, dist_to_player: float) -> float:
        hp_pct = max(0.0, min(1.0, self.current_hp / self.max_hp))
        hp_loss = 1.0 - hp_pct

        base = self.cfg["speed_base"]
        vmax = self.cfg["speed_max"]
        desired = base + (vmax - base) * hp_loss

        slow_r = self.cfg["slow_radius"]
        if dist_to_player < slow_r:
            t = max(0.0, dist_to_player / slow_r)  # 0..1
            near_min = self.cfg["min_speed_factor_near"]
            factor = near_min + (1.0 - near_min) * t
            desired *= factor

        return desired

    def update(self):
        self.check_activation()
        if not self.active and not self.is_dying:
            return

        now = pygame.time.get_ticks()
        dt = self._dt_scale_60fps(now)

        if now - self.last_anim > self.cfg["anim_interval_ms"]:
            self.last_anim = now
            self.frame_index += 1
            current_anim_list = self.anims.get(self.state, self.anims["walk"])

            if self.frame_index >= len(current_anim_list):
                if self.state == "death":
                    boss = DemonBoss(self.rect.midbottom, self.player, self.groups_ref, self.screen_rect)

                    if self.groups_ref:
                        if "all" in self.groups_ref:
                            self.groups_ref["all"].add(boss)
                        if "enemies" in self.groups_ref:
                            self.groups_ref["enemies"].add(boss)

                    if hasattr(self, "health_bar"):
                        self.health_bar.kill()
                    self.kill()
                    return

                elif self.state == "hited":
                    self.state = "walk"
                    self.frame_index = 0
                else:
                    self.frame_index = 0

        if not self.is_dying and self.state == "walk":
            self.hitbox_pos += self.knockback_force * dt
            decay = self.cfg["knockback_decay"]
            self.knockback_force *= (decay ** dt)
            if self.knockback_force.length() < self.cfg["knockback_deadzone"]:
                self.knockback_force *= 0

            target = pygame.Vector2(self.player.rect.center)
            diff = target - self.hitbox_pos
            dist = diff.length()

            if dist > 0:
                direction = diff / dist
                if direction.x != 0:
                    self.facing_right = direction.x > 0

                desired = self._desired_speed(dist)
                a = self.cfg["accel"]
                self._speed += (desired - self._speed) * a * dt

                self.hitbox_pos += direction * self._speed * dt

        # --- atualização visual ---
        current_anim_list = self.anims.get(self.state, self.anims["walk"])
        if self.frame_index >= len(current_anim_list):
            self.frame_index = 0

        image = current_anim_list[self.frame_index]
        if not self.facing_right:
            image = pygame.transform.flip(image, True, False)

        self.image = image
        self.rect = self.image.get_rect(center=(int(self.hitbox_pos.x), int(self.hitbox_pos.y)))
