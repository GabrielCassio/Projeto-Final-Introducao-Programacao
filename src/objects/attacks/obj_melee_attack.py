import pygame, os, random

# Importing configs by attack
from src.objects.attacks.obj_damage_attack import roll_player_damage

class PlayerMeleeSlash(pygame.sprite.Sprite):
    _CACHE = None

    def __init__(self, player_rect, direction, damage=10):
        print("Creating PlayerMeleeSlash attack")
        super().__init__()
        
        if PlayerMeleeSlash._CACHE is None:
            PlayerMeleeSlash._CACHE = self._load_melee_frames_padded()
        
        self.frames = PlayerMeleeSlash._CACHE.get(direction, PlayerMeleeSlash._CACHE["down"])

        self.direction = direction
        self.damage = int(damage)
        self.hit_list = []

        self.frame_index = 0
        self.anim_speed_ms = 45
        self.last_anim = pygame.time.get_ticks()

        self.image = self.frames[0]
        self.rect = self.image.get_rect(center=player_rect.center)
        self.mask = pygame.mask.from_surface(self.image)

        base = max(player_rect.width, player_rect.height) // 2
        offset = base + 8 

        if self.direction == "up":
            self.rect.centery -= offset
        elif self.direction == "down":
            self.rect.centery += offset
        elif self.direction == "left":
            self.rect.centerx -= offset
        elif self.direction == "right":
            self.rect.centerx += offset

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_anim > self.anim_speed_ms:
            self.last_anim = now
            self.frame_index += 1
            if self.frame_index >= len(self.frames):
                self.kill()
                return
            old_center = self.rect.center
            self.image = self.frames[self.frame_index]
            self.rect = self.image.get_rect(center=old_center)
            self.mask = pygame.mask.from_surface(self.image)

    @classmethod
    def _load_melee_frames_padded(cls, scale=3.4, extra_pad=26):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        path_to_sprites = os.path.join(base_dir, '..', '..', '..', 'sprites', 'entities', 'Player', 'attack', 'melee')
        
        dirs = ["up", "down", "left", "right"]
        raw = {}
        
        for d in dirs:
            full_path = os.path.join(path_to_sprites, d)
            raw[d] = cls._load_frames_from_folder(full_path, scale=scale)

        if not raw["right"] and raw["left"]:
            raw["right"] = cls._flip_frames(raw["left"])
        if not raw["left"] and raw["right"]:
            raw["left"] = cls._flip_frames(raw["right"])

        for _d in ("left", "right"):
            if raw.get(_d):
                raw[_d] = [cls._scale_surface(_f, 1.30) for _f in raw[_d]]

        for d in dirs:
            if not raw[d]:
                s = pygame.Surface((90, 90), pygame.SRCALPHA)
                pygame.draw.circle(s, (220, 220, 220, 180), (45, 45), 40)
                raw[d] = [s]

        max_w, max_h = 0, 0
        for d in dirs:
            for f in raw[d]:
                max_w = max(max_w, f.get_width())
                max_h = max(max_h, f.get_height())
        max_w += extra_pad * 2
        max_h += extra_pad * 2

        padded = {d: [] for d in dirs}
        for d in dirs:
            for f in raw[d]:
                canvas = pygame.Surface((max_w, max_h), pygame.SRCALPHA)
                r = f.get_rect(center=(max_w // 2, max_h // 2))
                canvas.blit(f, r)
                padded[d].append(canvas)

        return padded

    @staticmethod
    def _load_frames_from_folder(folder, scale=1.0):
        frames = []
        if not os.path.isdir(folder):
            return frames
        files = sorted([f for f in os.listdir(folder) if f.lower().endswith(".png")])
        for fn in files:
            try:
                img = pygame.image.load(os.path.join(folder, fn)).convert_alpha()
                if scale != 1.0:
                    w = int(img.get_width() * scale)
                    h = int(img.get_height() * scale)
                    img = pygame.transform.scale(img, (w, h))
                frames.append(img)
            except:
                pass
        return frames

    @staticmethod
    def _flip_frames(frames):
        return [pygame.transform.flip(f, True, False) for f in frames]

    @staticmethod
    def _scale_surface(s, factor):
        if factor == 1.0: return s
        w = max(1, int(round(s.get_width() * factor)))
        h = max(1, int(round(s.get_height() * factor)))
        return pygame.transform.scale(s, (w, h))