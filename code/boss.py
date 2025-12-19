import os
import pygame
import random
import math

print("--- [BOSS.PY] FINAL: UI Style Health Bar + Fixes ---")

# =========================
# CONFIGURAÇÕES
# =========================
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
    "jump":      {"file": "demon_jump.png",       "cols": 18, "rows": 1, "scale": 1.25}, 
    "wave":      {"file": "fire_wave.png",        "cols": 10, "rows": 1, "scale": 1.6},
    "explosion": {"file": "circle_explosion.png", "cols": 11,  "rows": 1, "scale": 1}
}

DEMON_STATS = {
    "max_hp": 5000,
    "scale": 2.5, 
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

# =========================
# UTILITÁRIOS
# =========================
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
    # 1) caminho direto
    candidate = os.path.join(start_dir, "assets", "graphics", "enemy", "boss")
    if os.path.isdir(candidate):
        return candidate

    # 2) sobe até 5 níveis
    cur = start_dir
    for _ in range(6):
        candidate = os.path.join(cur, "assets", "graphics", "enemy", "boss")
        if os.path.isdir(candidate):
            return candidate
        parent = os.path.dirname(cur)
        if parent == cur: break
        cur = parent

    # 3) fallback: recursivo
    cur = start_dir
    for _ in range(6):
        enemy_root = os.path.join(cur, "assets", "graphics", "enemy")
        if os.path.isdir(enemy_root):
            found = _find_folder_recursive(enemy_root, "boss")
            if found: return found
        parent = os.path.dirname(cur)
        if parent == cur: break
        cur = parent

    # 4) último fallback
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

# =========================
# CLASSES VISUAIS (UI & PROJÉTEIS)
# =========================

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
        
        # Não precisamos mais de 'activation_distance' aqui na UI, 
        # quem controla isso agora é o próprio Boss.
        
        self.image = pygame.Surface((self.bar_width, self.bar_height), pygame.SRCALPHA)
        self.rect = self.image.get_rect()

    def update(self):
        # 1. Se o boss morreu, tchau barra
        if not self.boss.alive():
            self.kill()
            return

        # 2. VERIFICAÇÃO DE ATIVAÇÃO
        # Usamos getattr para segurança, caso algum boss antigo não tenha 'active'
        is_active = getattr(self.boss, 'active', True) 

        if not is_active:
            # Se o boss está dormindo, a barra fica invisível
            self.image = pygame.Surface((0,0))
            return

        # 3. Desenho normal da barra
        self.image = pygame.Surface((self.bar_width, self.bar_height), pygame.SRCALPHA)
        self.image.fill((0, 0, 0, 180)) # Fundo preto semi-transparente
        
        hp_pct = max(0, self.boss.current_hp / self.boss.max_hp)
        fill_width = int(self.bar_width * hp_pct)
        
        if fill_width > 0:
            # Cor vermelha sangue
            pygame.draw.rect(self.image, (180, 30, 30), (0, 0, fill_width, self.bar_height))
        
        # Borda
        pygame.draw.rect(self.image, (200, 200, 200), (0, 0, self.bar_width, self.bar_height), 2)
        
        # Posiciona no centro inferior da tela
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
    def __init__(self, center_pos, max_radius, player, groups):
        super().__init__()
        if groups and "all" in groups: groups["all"].add(self)
        self.center = pygame.Vector2(center_pos)
        self.player = player
        self.max_radius = max_radius
        self.current_radius = 10
        self.growth_speed = 30
        self.alpha = 50 
        self.image = pygame.Surface((max_radius*2, max_radius*2), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=center_pos)

    def update(self):
        self.current_radius += self.growth_speed
        dim = int(self.current_radius * 2)
        if dim > 0:
            self.image = pygame.Surface((dim, dim), pygame.SRCALPHA)
            pygame.draw.circle(self.image, (255, 0, 0, self.alpha), (self.current_radius, self.current_radius), int(self.current_radius))
            pygame.draw.circle(self.image, (255, 0, 0, 150), (self.current_radius, self.current_radius), int(self.current_radius), 8)
            self.rect = self.image.get_rect(center=(int(self.center.x), int(self.center.y)))
        
        p_vec = pygame.Vector2(self.player.rect.center)
        dist = p_vec.distance_to(self.center)
        if dist < self.current_radius: 
            push_dir = p_vec - self.center
            if push_dir.length() == 0: push_dir = pygame.Vector2(1, 0)
            else: push_dir = push_dir.normalize()
            force = DEMON_STATS["push_force"]
            self.player.rect.x += int(push_dir.x * force)
            self.player.rect.y += int(push_dir.y * force)
        if self.current_radius >= self.max_radius: self.kill()

class CircleExplosion(pygame.sprite.Sprite):
    def __init__(self, center, frames, damage, groups):
        super().__init__()
        if groups and "all" in groups: groups["all"].add(self)
        if not frames:
            s = pygame.Surface((100, 100), pygame.SRCALPHA)
            pygame.draw.circle(s, (255, 200, 0), (50,50), 40)
            self.frames = [s, s, s, s, s]
        else:
            self.frames = frames
        self.frame_index = 0
        self.last_anim = pygame.time.get_ticks()
        self.image = self.frames[0]
        self.rect = self.image.get_rect(center=center)

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_anim > 50:
            self.last_anim = now
            self.frame_index += 1
            if self.frame_index >= len(self.frames): self.kill(); return
            self.image = self.frames[self.frame_index]
            self.rect = self.image.get_rect(center=self.rect.center)

class FireWave(pygame.sprite.Sprite):
    def __init__(self, x, y, direction_vec, speed, frames, damage, groups):
        super().__init__()
        if groups:
            if "all" in groups: groups["all"].add(self)
            if "proj" in groups: groups["proj"].add(self)
        
        if not frames:
            s = pygame.Surface((40, 40), pygame.SRCALPHA)
            pygame.draw.circle(s, (255, 100, 0), (20,20), 15)
            self.frames = [s]; self.rotated_frames = [s]
        else:
            self.frames = frames
            if direction_vec.length() == 0: direction_vec = pygame.Vector2(1,0)
            angle = math.degrees(math.atan2(-direction_vec.y, direction_vec.x)) + 90
            self.rotated_frames = [pygame.transform.rotate(f, angle) for f in self.frames]

        self.damage = damage
        self.speed = speed
        self.direction = direction_vec.normalize()
        self.pos = pygame.Vector2(x, y)
        self.start_pos = pygame.Vector2(x, y)
        self.frame_index = 0
        self.last_anim = pygame.time.get_ticks()
        self.image = self.rotated_frames[0]
        self.rect = self.image.get_rect(center=(x,y))

    def update(self):
        self.pos += self.direction * self.speed
        self.rect.center = (int(self.pos.x), int(self.pos.y))
        now = pygame.time.get_ticks()
        if now - self.last_anim > 80:
            self.last_anim = now
            self.frame_index = (self.frame_index + 1) % len(self.rotated_frames)
            self.image = self.rotated_frames[self.frame_index]
        if self.pos.distance_to(self.start_pos) > 1200: self.kill()

# =========================
# DEMON BOSS
# =========================
class DemonBoss(pygame.sprite.Sprite):
    def __init__(self, pos_midbottom, player, groups, screen_rect):
        super().__init__()
        self.player = player
        self.groups_ref = groups
        self.screen_rect = screen_rect
        
        base = os.path.dirname(os.path.abspath(__file__))
        boss_root = _resolve_boss_root(base)
        sprites_root = _find_folder_recursive(boss_root, "individual sprites")
        self.anims = {}
        if sprites_root:
            for k, folder in DEMON_FOLDERS_CONFIG.items():
                self.anims[k] = _load_frames_from_folder(sprites_root, folder, DEMON_STATS["scale"])
        else:
            for k in DEMON_FOLDERS_CONFIG: self.anims[k] = [pygame.Surface((100,100))]

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

        # Estado Inicial
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
        self.attack_vector = pygame.Vector2(0,0)
        
        self.is_jumping = False
        self.jump_visual_offset = 0 
        self.ground_anchor = self.rect.bottom 
        self.pending_explosions = []
        self.last_jump_time = pygame.time.get_ticks()
        self.last_external_wave = pygame.time.get_ticks()
        self.speed = DEMON_STATS["speed_base"]
        self.explosion_trigger_time = 0

        # CRIA A BARRA DE VIDA (FIXA EM BAIXO)
        BossHealthBar(self, self.groups_ref)

    def take_damage(self, amount, source_pos=None, crit=False):
        if self.state == "death" or self.is_jumping: return
        self.current_hp = max(0, self.current_hp - int(amount))
        
        if "all" in self.groups_ref:
            # Dano mais baixo (CenterY)
            self.groups_ref["all"].add(DamageNumber(self.rect.centerx, self.rect.centery, int(amount), crit=crit))
            
        if self.current_hp <= 0: self.state = "death"; self.frame_index = 0
        elif self.state not in ["pre_attack", "attacking"]:
            self.state = "take_hit"; self.frame_index = 0; self.last_anim = pygame.time.get_ticks()

    def _start_jump(self):
        self.state = "jump_start"
        self.is_jumping = True
        self.last_jump_time = pygame.time.get_ticks()
        self.frame_index = 0
        self.jump_visual_offset = 0
        self.pending_explosions = []
        self.ground_anchor = self.rect.bottom

        num_explosions = 6
        for _ in range(num_explosions):
            rx = random.randint(100, self.screen_rect.width - 100)
            ry = random.randint(100, self.screen_rect.height - 100)
            self.pending_explosions.append((rx, ry))
            area = pygame.Rect(0,0,120,120)
            area.center = (rx, ry)
            DangerIndicator(area, 4000, self.groups_ref)

    def _perform_land_impact(self):
        ShockwavePush(self.rect.center, 550, self.player, self.groups_ref)
        cardinals = [(1,0), (-1,0), (0,1), (0,-1)]
        for dx, dy in cardinals:
            vec = pygame.Vector2(dx, dy)
            FireWave(self.rect.centerx, self.rect.centery, vec, 
                     DEMON_STATS["wave_speed"], self.special_anims["wave"], 
                     DEMON_STATS["wave_damage"], self.groups_ref)
        dist = pygame.Vector2(self.player.rect.center).distance_to(self.rect.center)
        if dist < 150:
            if hasattr(self.player, "take_damage"): self.player.take_damage(DEMON_STATS["jump_damage_impact"])
        self.explosion_trigger_time = pygame.time.get_ticks() + DEMON_STATS["explosion_delay_ms"]

    def _manage_external_waves(self, hp_pct, now):
        if hp_pct >= 0.5: return
        if now - self.last_external_wave > DEMON_STATS["external_wave_interval"]:
            self.last_external_wave = now
            count = 1
            if hp_pct < 0.30: count = 2
            if hp_pct < 0.15: count = 3
            for _ in range(count):
                side = random.choice(["top", "bottom", "left", "right"])
                w, h = self.screen_rect.width, self.screen_rect.height
                start = pygame.Vector2(0,0)
                if side=="top": start = pygame.Vector2(random.randint(0,w), -100)
                elif side=="bottom": start = pygame.Vector2(random.randint(0,w), h+100)
                elif side=="left": start = pygame.Vector2(-100, random.randint(0,h))
                else: start = pygame.Vector2(w+100, random.randint(0,h))
                
                target = pygame.Vector2(self.player.rect.center)
                direction = target - start
                FireWave(start.x, start.y, direction, 
                         DEMON_STATS["wave_speed"] * 0.8, 
                         self.special_anims["wave"], 
                         DEMON_STATS["wave_damage"], self.groups_ref)

    def update(self):
        now = pygame.time.get_ticks()
        hp_pct = self.current_hp / self.max_hp
        hp_loss = 1.0 - hp_pct
        self.speed = DEMON_STATS["speed_base"] + (DEMON_STATS["speed_max"] - DEMON_STATS["speed_base"]) * hp_loss
        
        self._manage_external_waves(hp_pct, now)

        if self.explosion_trigger_time > 0 and now >= self.explosion_trigger_time:
            for pos in self.pending_explosions:
                CircleExplosion(pos, self.special_anims["explosion"], DEMON_STATS["explosion_damage"], self.groups_ref)
            self.pending_explosions.clear()
            self.explosion_trigger_time = 0

        # --- PULO ---
        if self.is_jumping:
            if now - self.last_anim > 80: 
                self.last_anim = now
                if self.state == "jump_start":
                    self.frame_index += 1
                    progress = self.frame_index / 6.0
                    self.jump_visual_offset = -int(DEMON_STATS["jump_max_height"] * progress)
                    if self.frame_index > 5: 
                        self.state = "jump_air"; self.frame_index = 6
                        self.jump_visual_offset = -DEMON_STATS["jump_max_height"]

                elif self.state == "jump_air":
                    self.frame_index += 1
                    self.jump_visual_offset = -DEMON_STATS["jump_max_height"]
                    if (now - self.last_jump_time) > 1500:
                        self.state = "jump_land"; self.frame_index = 12
                    elif self.frame_index > 11: 
                        self.frame_index = 6
                
                elif self.state == "jump_land":
                    self.frame_index += 1
                    land_progress = (self.frame_index - 12) / 5.0
                    self.jump_visual_offset = -int(DEMON_STATS["jump_max_height"] * (1.0 - land_progress))
                    if self.frame_index == 14: self._perform_land_impact()
                    
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
            idx = min(self.frame_index, len(jump_frames)-1)
            if jump_frames:
                img = jump_frames[idx]
                img = pygame.transform.flip(img, self.facing_right, False)
                self.image = img
                self.rect.bottom = self.ground_anchor + int(self.jump_visual_offset)
            return

        current_jump_cd = DEMON_STATS["jump_cooldown_max"] - (
            (DEMON_STATS["jump_cooldown_max"] - DEMON_STATS["jump_cooldown_min"]) * hp_loss
        )

        if not self.is_jumping and self.state in ["chase", "idle"]:
            if now - self.last_jump_time > current_jump_cd:
                self._start_jump(); return

        STATE_TO_ANIM = {
            "idle": "idle", "chase": "walk", "cooldown_chase": "walk",
            "pre_attack": "idle", "attacking": "cleave",
            "take_hit": "take_hit", "death": "death"
        }
        anim_key = STATE_TO_ANIM.get(self.state, "idle")
        frames = self.anims.get(anim_key, self.anims["idle"])
        
        if self.frames != frames: self.frames = frames; self.frame_index = 0
        
        if now - self.last_anim > 100:
            self.last_anim = now
            if self.state == "death":
                if self.frame_index < len(frames)-1: self.frame_index += 1
                else: self.kill(); return
            elif self.state == "take_hit":
                if self.frame_index < len(frames)-1: self.frame_index += 1
                else: self.state = "chase"
            elif self.state == "attacking":
                 if self.frame_index < len(frames)-1: 
                     self.frame_index += 1
                     if self.frame_index == len(frames)//2: self._deal_damage()
                 else: 
                     self.state = "cooldown_chase"
                     self.cooldown_end_time = now + DEMON_STATS["attack_cooldown_ms"]
            else:
                self.frame_index = (self.frame_index + 1) % len(frames)

        if self.state == "chase":
            p_vec = pygame.Vector2(self.player.rect.center)
            m_vec = pygame.Vector2(self.rect.center)
            diff = p_vec - m_vec
            dist = diff.length()
            if dist < DEMON_STATS["attack_range"]:
                self.state = "pre_attack"; self.charge_start_time = now
                if dist > 0: self.attack_vector = diff.normalize()
                else: self.attack_vector = pygame.Vector2(1,0)
                hitbox = pygame.Rect(0,0, DEMON_STATS["attack_w"], DEMON_STATS["attack_h"])
                hitbox.center = m_vec + self.attack_vector * DEMON_STATS["attack_offset"]
                DangerIndicator(hitbox, DEMON_STATS["charge_time_min"], self.groups_ref)
            else:
                if dist > 0:
                    direction = diff.normalize()
                    if direction.x != 0: self.facing_right = direction.x > 0
                    self.rect.center += direction * self.speed
        
        elif self.state == "pre_attack":
            if now - self.charge_start_time > DEMON_STATS["charge_time_min"]:
                self.state = "attacking"; self.frame_index = 0
        
        elif self.state == "cooldown_chase":
            p_vec = pygame.Vector2(self.player.rect.center)
            m_vec = pygame.Vector2(self.rect.center)
            diff = p_vec - m_vec
            if diff.length() > 0:
                direction = diff.normalize()
                if direction.x != 0: self.facing_right = direction.x > 0
                self.rect.center += direction * (self.speed * 0.5)
            if now > self.cooldown_end_time: self.state = "chase"

        if self.frame_index >= len(self.frames): self.frame_index = 0
        
        img = self.frames[self.frame_index]
        img = pygame.transform.flip(img, self.facing_right, False)
        old_center = self.rect.center
        self.image = img
        self.rect = self.image.get_rect(center=old_center)
        self.mask = pygame.mask.from_surface(self.image)

    def _deal_damage(self):
        hitbox = pygame.Rect(0,0, DEMON_STATS["attack_w"], DEMON_STATS["attack_h"])
        hitbox.center = self.rect.center + self.attack_vector * DEMON_STATS["attack_offset"]
        if hitbox.colliderect(self.player.rect):
             if hasattr(self.player, "take_damage"): self.player.take_damage(60)

    def update(self):
        now = pygame.time.get_ticks()
        
        hp_pct = self.current_hp / self.max_hp
        hp_loss = 1.0 - hp_pct
        self.speed = DEMON_STATS["speed_base"] + (DEMON_STATS["speed_max"] - DEMON_STATS["speed_base"]) * hp_loss
        
        self._manage_external_waves(hp_pct, now)

        if self.explosion_trigger_time > 0 and now >= self.explosion_trigger_time:
            for pos in self.pending_explosions:
                CircleExplosion(pos, self.special_anims["explosion"], DEMON_STATS["explosion_damage"], self.groups_ref)
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
                        self.state = "jump_air"; self.frame_index = 6
                        self.jump_visual_offset = -DEMON_STATS["jump_max_height"]

                elif self.state == "jump_air":
                    self.frame_index += 1
                    self.jump_visual_offset = -DEMON_STATS["jump_max_height"]
                    if (now - self.last_jump_time) > 1500:
                        self.state = "jump_land"; self.frame_index = 12
                    elif self.frame_index > 11: 
                        self.frame_index = 6
                
                elif self.state == "jump_land":
                    self.frame_index += 1
                    land_progress = (self.frame_index - 12) / 5.0
                    self.jump_visual_offset = -int(DEMON_STATS["jump_max_height"] * (1.0 - land_progress))
                    if self.frame_index == 14: self._perform_land_impact()
                    
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
            idx = min(self.frame_index, len(jump_frames)-1)
            if jump_frames:
                img = jump_frames[idx]
                img = pygame.transform.flip(img, self.facing_right, False)
                self.image = img
                self.rect.bottom = self.ground_anchor + int(self.jump_visual_offset)
            return

        current_jump_cd = DEMON_STATS["jump_cooldown_max"] - (
            (DEMON_STATS["jump_cooldown_max"] - DEMON_STATS["jump_cooldown_min"]) * hp_loss
        )

        if not self.is_jumping and self.state in ["chase", "idle"]:
            if now - self.last_jump_time > current_jump_cd:
                self._start_jump(); return

        STATE_TO_ANIM = {
            "idle": "idle", "chase": "walk", "cooldown_chase": "walk",
            "pre_attack": "idle", "attacking": "cleave",
            "take_hit": "take_hit", "death": "death"
        }
        anim_key = STATE_TO_ANIM.get(self.state, "idle")
        frames = self.anims.get(anim_key, self.anims["idle"])
        
        if self.frames != frames: self.frames = frames; self.frame_index = 0
        
        if now - self.last_anim > 100:
            self.last_anim = now
            if self.state == "death":
                if self.frame_index < len(frames)-1: self.frame_index += 1
                else: self.kill(); return
            elif self.state == "take_hit":
                if self.frame_index < len(frames)-1: self.frame_index += 1
                else: self.state = "chase"
            elif self.state == "attacking":
                 if self.frame_index < len(frames)-1: 
                     self.frame_index += 1
                     if self.frame_index == len(frames)//2: self._deal_damage()
                 else: 
                     self.state = "cooldown_chase"
                     self.cooldown_end_time = now + DEMON_STATS["attack_cooldown_ms"]
            else:
                self.frame_index = (self.frame_index + 1) % len(frames)

        if self.state == "chase":
            p_vec = pygame.Vector2(self.player.rect.center)
            m_vec = pygame.Vector2(self.rect.center)
            diff = p_vec - m_vec
            dist = diff.length()
            if dist < DEMON_STATS["attack_range"]:
                self.state = "pre_attack"; self.charge_start_time = now
                if dist > 0: self.attack_vector = diff.normalize()
                else: self.attack_vector = pygame.Vector2(1,0)
                hitbox = pygame.Rect(0,0, DEMON_STATS["attack_w"], DEMON_STATS["attack_h"])
                hitbox.center = m_vec + self.attack_vector * DEMON_STATS["attack_offset"]
                DangerIndicator(hitbox, DEMON_STATS["charge_time_min"], self.groups_ref)
            else:
                if dist > 0:
                    direction = diff.normalize()
                    if direction.x != 0: self.facing_right = direction.x > 0
                    self.rect.center += direction * self.speed
        
        elif self.state == "pre_attack":
            if now - self.charge_start_time > DEMON_STATS["charge_time_min"]:
                self.state = "attacking"; self.frame_index = 0
        
        elif self.state == "cooldown_chase":
            p_vec = pygame.Vector2(self.player.rect.center)
            m_vec = pygame.Vector2(self.rect.center)
            diff = p_vec - m_vec
            if diff.length() > 0:
                direction = diff.normalize()
                if direction.x != 0: self.facing_right = direction.x > 0
                self.rect.center += direction * (self.speed * 0.5)
            if now > self.cooldown_end_time: self.state = "chase"

        if self.frame_index >= len(self.frames): self.frame_index = 0
        
        img = self.frames[self.frame_index]
        img = pygame.transform.flip(img, self.facing_right, False)
        old_center = self.rect.center
        self.image = img
        self.rect = self.image.get_rect(center=old_center)
        self.mask = pygame.mask.from_surface(self.image)

# =========================
# FASE 1: SLIME BOSS
# =========================
class DemonSlimeBoss(pygame.sprite.Sprite):
    def __init__(self, x, y, player, groups, screen_rect):
        super().__init__()
        self.player = player
        self.groups_ref = groups
        self.screen_rect = screen_rect
        
        # --- SPRITES ---
        base_dir = os.path.dirname(os.path.abspath(__file__))
        boss_root = _resolve_boss_root(base_dir)
        ba_root = boss_root
        sub = _find_folder_recursive(boss_root, "boss")
        if sub: ba_root = sub
        else:
            sub = _find_folder_recursive(boss_root, "boss_animations")
            if sub: ba_root = sub
        
        self.anims = {}
        try:
            p1 = _find_file_recursive(ba_root, SLIME_SHEETS["walk"]["file"])
            self.anims["walk"] = _slice_sheet(p1, SLIME_SHEETS["walk"]["count"], scale=SLIME_SHEETS["walk"]["scale"])
        except: self.anims["walk"] = []

        try:
            p2 = _find_file_recursive(ba_root, SLIME_SHEETS["hited"]["file"])
            self.anims["hited"] = _slice_sheet(p2, 6, scale=SLIME_SHEETS["hited"]["scale"])
        except: self.anims["hited"] = []

        try:
            p3 = _find_file_recursive(ba_root, SLIME_SHEETS["death"]["file"])
            self.anims["death"] = _slice_sheet(p3, SLIME_SHEETS["death"]["count"], scale=SLIME_SHEETS["death"]["scale"])
        except: self.anims["death"] = []
        
        if not self.anims["walk"]: self.anims["walk"] = [pygame.Surface((50,50))]
        if not self.anims["hited"]: self.anims["hited"] = self.anims["walk"]
        if not self.anims["death"]: self.anims["death"] = self.anims["walk"]

        # --- STATUS ---
        self.state = "walk"
        self.max_hp = 1000
        self.current_hp = 1000
        self.frame_index = 0
        self.last_anim = pygame.time.get_ticks()
        
        self.image = self.anims["walk"][0]
        self.rect = self.image.get_rect(center=(x,y))
        
        self.hitbox_pos = pygame.Vector2(x, y)

        self.facing_right = True
        self.hop_offset = 0
        self.is_dying = False
        self.flash_until = 0
        self.knockback_force = pygame.Vector2(0,0)
        
        # --- ATIVAÇÃO ---
        self.active = False
        self.activation_radius = 500  
        
        # Barra de Vida
        self.health_bar = BossHealthBar(self, self.groups_ref)

    def check_activation(self):
        if self.active: return
            
        p_vec = pygame.Vector2(self.player.rect.center)
        me_vec = self.hitbox_pos
        dist = p_vec.distance_to(me_vec)
        
        if dist < self.activation_radius:
            self.active = True
            print("Boss ACORDOU!")

    def take_damage(self, amount, source_pos=None, crit=False):
        if self.is_dying: return
        self.active = True
        
        self.current_hp -= int(amount)
        self.flash_until = pygame.time.get_ticks() + 150
        
        if "all" in self.groups_ref: 
            try: self.groups_ref["all"].add(DamageNumber(self.rect.centerx, self.rect.centery, amount, crit))
            except: pass
            
        if source_pos:
            push_dir = self.hitbox_pos - pygame.Vector2(source_pos)
            if push_dir.length() == 0: push_dir = pygame.Vector2(1, 0)
            else: push_dir = push_dir.normalize()
            self.knockback_force = push_dir * 5

        if self.current_hp <= 0: 
            self.is_dying = True
            self.state = "death"
            self.frame_index = 0
            self.knockback_force *= 0

    def update(self):
        # 1. Verifica se o player ativou o boss
        self.check_activation()

        # Se não está ativo e não está morrendo, não faz nada
        if not self.active and not self.is_dying:
            return

        now = pygame.time.get_ticks()

        # Animação (usa 100ms de delay)
        if now - self.last_anim > 100:
            self.last_anim = now
            self.frame_index += 1
            
            # Pega a lista de animação atual
            current_anim_list = self.anims.get(self.state, self.anims["walk"])
            
            # Verifica se a animação acabou
            if self.frame_index >= len(current_anim_list):
                
                # --- LÓGICA DE TRANSIÇÃO (Slime -> Demônio) ---
                if self.state == "death":
                    # O Slime terminou de morrer. Nasce o Demônio IMEDIATAMENTE.
                    # Cria o DemonBoss na mesma posição (midbottom)
                    boss = DemonBoss(self.rect.midbottom, self.player, self.groups_ref, self.screen_rect)
                    
                    if self.groups_ref:
                        if "all" in self.groups_ref: self.groups_ref["all"].add(boss)
                        if "enemies" in self.groups_ref: self.groups_ref["enemies"].add(boss)
                    
                    # Remove barra de vida antiga e o objeto Slime
                    if hasattr(self, 'health_bar'): self.health_bar.kill() 
                    self.kill()
                    return # Sai da função imediatamente
                
                elif self.state == "hited":
                    self.state = "walk"
                    self.frame_index = 0
                
                else:
                    # Loop normal (andar)
                    self.frame_index = 0

        # --- LÓGICA DE MOVIMENTO (Só se não estiver morrendo) ---
        if not self.is_dying:
            if self.state == "walk":
                # Aplica o knockback (empurrão)
                self.hitbox_pos += self.knockback_force
                self.knockback_force *= 0.8 

                # Persegue o player
                target = pygame.Vector2(self.player.rect.center)
                diff = target - self.hitbox_pos
                if diff.length() > 0:
                    direction = diff.normalize()
                    self.hitbox_pos += direction * 2.5 # Velocidade do Slime
                    
                    # Ajusta o lado que está olhando
                    if direction.x != 0:
                        self.facing_right = direction.x > 0

        # --- ATUALIZAÇÃO VISUAL ---
        current_anim_list = self.anims.get(self.state, self.anims["walk"])
        
        # Proteção para índice fora do limite
        if self.frame_index >= len(current_anim_list): 
            self.frame_index = 0
        
        image = current_anim_list[self.frame_index]
        
        # Espelhamento
        if not self.facing_right:
            image = pygame.transform.flip(image, True, False)
            
        self.image = image
        self.rect = self.image.get_rect(center=(int(self.hitbox_pos.x), int(self.hitbox_pos.y)))