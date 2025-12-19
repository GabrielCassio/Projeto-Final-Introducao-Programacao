# tile.py
import os
import math
import random
import pygame

from settings import *

# ----------------------------
# Helpers / cache de assets
# ----------------------------
_ASSET_CACHE = {}

def _asset_path(*parts) -> str:
    # tile.py está em /code; assets está "no mesmo grau" => ../assets/tiles/...
    base_dir = os.path.dirname(__file__)
    return os.path.abspath(os.path.join(base_dir, "..", *parts))

def load_image_cached(rel_path: str, scale_to=None) -> pygame.Surface:
    """
    rel_path exemplo: ("assets","tiles","cracha_vermelho.png")
    scale_to: (w,h) ou None
    """
    key = (rel_path, scale_to)
    if key in _ASSET_CACHE:
        return _ASSET_CACHE[key]

    full = _asset_path(*rel_path)
    surf = pygame.image.load(full).convert_alpha()
    if scale_to is not None:
        surf = pygame.transform.smoothscale(surf, scale_to)

    _ASSET_CACHE[key] = surf
    return surf

def load_spritesheet_frames_cached(rel_path: str, frame_size=None, scale_to=None) -> list[pygame.Surface]:
    """
    Lê sprite sheet horizontal.
    - frame_size None => tenta inferir: frame_w = sheet.get_height() (frames quadrados)
    - scale_to opcional => redimensiona cada frame
    """
    key = (rel_path, frame_size, scale_to)
    if key in _ASSET_CACHE:
        return _ASSET_CACHE[key]

    full = _asset_path(*rel_path)
    sheet = pygame.image.load(full).convert_alpha()
    sheet_w, sheet_h = sheet.get_size()

    if frame_size is None:
        # Inferência robusta (bem comum em spritesheet: frames quadrados)
        frame_w = sheet_h
        frame_h = sheet_h
    else:
        frame_w, frame_h = frame_size

    frames = []
    cols = max(1, sheet_w // frame_w)
    for i in range(cols):
        rect = pygame.Rect(i * frame_w, 0, frame_w, frame_h)
        frame = sheet.subsurface(rect).copy()
        if scale_to is not None:
            frame = pygame.transform.smoothscale(frame, scale_to)
        frames.append(frame)

    _ASSET_CACHE[key] = frames
    return frames


class Wall(pygame.sprite.Sprite):
    def __init__(self, pos, groups):
        super().__init__(groups)
        self.rect = pygame.Rect(pos, (TILESIZE, TILESIZE))
        self.hitbox = self.rect.inflate(0, -6)


class Collectible(pygame.sprite.Sprite):
    def __init__(self, pos, groups, item_type):
        super().__init__(groups)
        self.item_type = item_type

        # Tamanho padrão do collectible na tela (ajuste se quiser)
        self.render_size = (24, 24)

        # --- animação (apenas para soul) ---
        self.frames = None
        self.frame_index = 0
        self.anim_timer = 0.0
        self.anim_speed = 0.08  # segundos por frame

        # --------------------------------
        # Visual por tipo
        # --------------------------------
        if self.item_type == "cracha":
            self.image = load_image_cached(
                ("assets", "tiles", "cracha_vermelho.png"),
                scale_to=self.render_size
            )

        elif self.item_type == "soul":
            # spritesheet em linha (horizontal)
            self.frames = load_spritesheet_frames_cached(
                ("assets", "tiles", "soul.png"),
                frame_size=None,              # tenta inferir
                scale_to=self.render_size
            )
            self.image = self.frames[0]

        else:
            # fallback: mantém seus desenhos para heart/coin etc.
            self.image = pygame.Surface(self.render_size, pygame.SRCALPHA)

            if self.item_type == "heart":
                self.image.fill("red")
                pygame.draw.rect(self.image, "white", (8, 4, 8, 16))
                pygame.draw.rect(self.image, "white", (4, 8, 16, 8))

            elif "coin" in self.item_type:
                if self.item_type == "coin":
                    color, border = "gold", "orange"
                elif self.item_type == "coin_red":
                    color, border = "#ff4444", "#880000"
                elif self.item_type == "coin_green":
                    color, border = "#44ff44", "#008800"
                else:
                    color, border = "gold", "orange"

                pygame.draw.circle(self.image, color, (12, 12), 10)
                pygame.draw.circle(self.image, border, (12, 12), 10, 2)
                pygame.draw.line(self.image, border, (12, 6), (12, 18), 2)

            else:
                # qualquer outro item desconhecido
                self.image.fill((255, 255, 255, 80))

        # --------------------------------
        # Rect/Hitbox + flutuação
        # --------------------------------
        self.rect = self.image.get_rect(center=pos)
        self.hitbox = self.rect.inflate(-10, -10)

        self.start_y = self.rect.centery
        self.float_speed = 0.005
        self.float_range = 5

    def update(self, dt):
        # dt pode vir em segundos (comum) — vou assumir isso aqui.
        # Flutuação (como você já fazia)
        current_time = pygame.time.get_ticks()
        offset = math.sin(current_time * self.float_speed) * self.float_range
        self.rect.centery = self.start_y + offset

        # Animação da soul (se tiver frames)
        if self.frames:
            self.anim_timer += dt
            if self.anim_timer >= self.anim_speed:
                self.anim_timer -= self.anim_speed
                self.frame_index = (self.frame_index + 1) % len(self.frames)
                self.image = self.frames[self.frame_index]

                # mantém o center (não "pula" visualmente)
                center = self.rect.center
                self.rect = self.image.get_rect(center=center)
                self.hitbox = self.rect.inflate(-10, -10)


class FireBarrier(pygame.sprite.Sprite):
    def __init__(self, pos, groups):
        super().__init__(groups)

        self.tiles_wide = 5
        self.pixel_width = TILESIZE * self.tiles_wide

        self.image = pygame.Surface((self.pixel_width, TILESIZE))
        self.image.fill("red")

        self.rect = self.image.get_rect(topleft=pos)
        self.hitbox = self.rect.inflate(0, 0)

        self.frame_time = 0

    def update(self, dt):
        current_time = pygame.time.get_ticks()
        if current_time - self.frame_time > 50:
            self.frame_time = current_time

            self.image.fill("#5e0e0e")

            for x in range(0, self.pixel_width, 8):
                height = random.randint(10, TILESIZE)
                color = random.choice(["#ff3333", "#ff8833", "#ffff33"])
                rect_flame = pygame.Rect(x, TILESIZE - height, 8, height)
                pygame.draw.rect(self.image, color, rect_flame)
