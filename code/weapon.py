import pygame 
from support import import_folder

class Weapon(pygame.sprite.Sprite):
    def __init__(self, player, groups):
        super().__init__(groups)
        
        self.frame_index = 0
        self.animation_speed = 20
        direction = player.status.split('_')[0]
        
        full_path = f'./assets/graphics/player/attack/melee/{direction}'
        self.frames = import_folder(full_path)

        if direction == 'left' or direction == 'right':
            scaled_frames = []
            scale_factor = 1.5
            for frame in self.frames:
                new_size = (int(frame.get_width() * scale_factor), int(frame.get_height() * scale_factor))
                scaled_surf = pygame.transform.scale(frame, new_size)
                scaled_frames.append(scaled_surf)
            self.frames = scaled_frames
        
        if len(self.frames) > 0:
            self.image = self.frames[self.frame_index]
        else:
            self.image = pygame.Surface((40, 40))
            self.image.fill('white')


        self.rect = self.image.get_rect(center=player.rect.center)
        
        if direction == 'right':
            self.rect.midleft = player.rect.midright + pygame.math.Vector2(0, 0)
        
        elif direction == 'left':
            self.rect.midright = player.rect.midleft + pygame.math.Vector2(0, 0)
        
        elif direction == 'down':
            self.rect.midtop = player.rect.midbottom + pygame.math.Vector2(0, 0)
        
        elif direction == 'up':
            self.rect.midbottom = player.rect.midtop + pygame.math.Vector2(-2, 0)


    def update(self, dt):
        if len(self.frames) == 0: return

        self.frame_index += self.animation_speed * dt
        if self.frame_index >= len(self.frames):
            self.kill() 
        else:
            self.image = self.frames[int(self.frame_index)]