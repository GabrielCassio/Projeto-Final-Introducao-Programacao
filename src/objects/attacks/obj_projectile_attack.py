import pygame, os

from src.settings import WIDTH, HEIGHT

class BadgeProjectile(pygame.sprite.Sprite):
    _CACHE = None

    def __init__(self, x, y, direction, damage=3, crit=False, speed=10):
        super().__init__()
        
        self.direction_vec = pygame.Vector2(0, 0)
        anim_direction = "down"

        if isinstance(direction, pygame.Vector2):
            self.direction_vec = direction.normalize() if direction.length() > 0 else pygame.Vector2(0,1)
            if abs(self.direction_vec.x) > abs(self.direction_vec.y):
                anim_direction = "right" if self.direction_vec.x > 0 else "left"
            else:
                anim_direction = "down" if self.direction_vec.y > 0 else "up"
        elif isinstance(direction, str):
            anim_direction = direction
            vec_map = {
                "up": pygame.Vector2(0, -1), "down": pygame.Vector2(0, 1),
                "left": pygame.Vector2(-1, 0), "right": pygame.Vector2(1, 0)
            }
            self.direction_vec = vec_map.get(direction, pygame.Vector2(0, 1))

        if BadgeProjectile._CACHE is None:
            BadgeProjectile._CACHE = self._load_badge_frames(scale=2.0)
        
        self.frames = BadgeProjectile._CACHE.get(anim_direction, BadgeProjectile._CACHE["down"])
        
        self.crit = bool(crit)
        self.damage = int(damage)
        self.speed = speed
        
        self.frame_index = 0
        self.anim_speed_ms = 60
        self.last_anim = pygame.time.get_ticks()

        self.image = self.frames[0]
        self.rect = self.image.get_rect(center=(x, y))
        self.mask = pygame.mask.from_surface(self.image)
        
        self.pos = pygame.Vector2(self.rect.center)

    def update(self):
        self.pos += self.direction_vec * self.speed
        self.rect.center = round(self.pos.x), round(self.pos.y)

        now = pygame.time.get_ticks()
        if len(self.frames) > 1 and now - self.last_anim > self.anim_speed_ms:
            self.last_anim = now
            self.frame_index = (self.frame_index + 1) % len(self.frames)
            
            old_center = self.rect.center
            self.image = self.frames[self.frame_index]
            self.rect = self.image.get_rect(center=old_center)
            self.mask = pygame.mask.from_surface(self.image)

        if (self.rect.right < -50 or self.rect.left > WIDTH + 50 or
            self.rect.bottom < -50 or self.rect.top > HEIGHT + 50):
            self.kill()

    @classmethod
    def _load_badge_frames(cls, scale=2.0):
        base_dir = os.path.dirname('src/sprites/emtities/player/')
        print(base_dir)
        path_to_sprites = os.path.join(base_dir, 'attack', 'ranged')
        
        dirs = ["up", "down", "left", "right"]
        frames_dict = {}

        for d in dirs:
            frames_dict[d] = cls._load_frames_from_folder(os.path.join(path_to_sprites, d), scale=scale)

        if frames_dict["left"] and not frames_dict["right"]:
            frames_dict["right"] = cls._flip_frames(frames_dict["left"])
        if frames_dict["right"] and not frames_dict["left"]:
            frames_dict["left"] = cls._flip_frames(frames_dict["right"])

        for d in dirs:
            if not frames_dict[d]:
                s = pygame.Surface((18, 10), pygame.SRCALPHA)
                pygame.draw.rect(s, (200, 200, 220), (0, 0, 18, 10), border_radius=2)
                pygame.draw.rect(s, (80, 80, 100), (2, 2, 14, 6), border_radius=1)
                frames_dict[d] = [s]

        return frames_dict

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
                    img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
                frames.append(img)
            except:
                pass
        return frames

    @staticmethod
    def _flip_frames(frames):
        return [pygame.transform.flip(f, True, False) for f in frames]