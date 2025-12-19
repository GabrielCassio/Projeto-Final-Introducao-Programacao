import pygame 
import os 
from support import import_folder

class Cracha(pygame.sprite.Sprite):
    def __init__(self, pos, direction, groups, obstacle_sprites):
        super().__init__(groups)
        
        self.direction = direction
        self.speed = 300 
        self.obstacle_sprites = obstacle_sprites
        self.life_time = 1000 
        self.start_time = pygame.time.get_ticks()

        # Tradutor de direção
        folder_name = 'down' 
        if direction.y == -1: folder_name = 'up'
        elif direction.y == 1: folder_name = 'down'
        elif direction.x == -1: folder_name = 'left'
        elif direction.x == 1: folder_name = 'right'

        # Caminho Absoluto (Nuclear)
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(script_dir)
        full_path = os.path.join(project_root, 'assets', 'graphics', 'player', 'attack', 'ranged', folder_name)
        
        # Carrega os frames originais
        original_frames = import_folder(full_path)
        self.frames = []

        # --- AJUSTES VISUAIS (DIMINUIR E INVERTER) ---
        # Mude este valor para ajustar o tamanho:
        # 1.0 = Tamanho normal
        # 0.5 = Metade do tamanho
        # 0.3 = Um terço (bem pequeno)
        scale_factor = 0.8 

        for frame in original_frames:
            # 1. Calcula novo tamanho
            new_width = int(frame.get_width() * scale_factor)
            new_height = int(frame.get_height() * scale_factor)
            
            # 2. Redimensiona a imagem
            processed_frame = pygame.transform.scale(frame, (new_width, new_height))

            # 3. Inverte APENAS se for para a esquerda
            if folder_name == 'left':
                # flip(surface, x_bool, y_bool) -> Inverte no eixo X
                processed_frame = pygame.transform.flip(processed_frame, True, False)
            
            self.frames.append(processed_frame)
        # ---------------------------------------------

        self.frame_index = 0
        self.animation_speed = 20 

        if len(self.frames) > 0:
            self.image = self.frames[self.frame_index]
        else:
            print(f"!!! ARQUIVOS NÃO ENCONTRADOS EM: {full_path}")
            self.image = pygame.Surface((20, 20))
            self.image.fill('white')

        self.rect = self.image.get_rect(center=pos)
        self.hitbox = self.rect.inflate(0, 0)
        self.pos = pygame.math.Vector2(self.rect.center)

    def move(self, dt):
        self.pos += self.direction * self.speed * dt
        self.rect.center = self.pos
        self.hitbox.center = self.pos

    def animate(self, dt):
        if len(self.frames) == 0: return

        self.frame_index += self.animation_speed * dt
        if self.frame_index >= len(self.frames):
            self.frame_index = 0 

        self.image = self.frames[int(self.frame_index)]

    def collision(self):
        for sprite in self.obstacle_sprites:
            if sprite.hitbox.colliderect(self.hitbox):
                self.kill()

    def update(self, dt):
        self.move(dt)
        self.animate(dt)
        self.collision()
        
        current_time = pygame.time.get_ticks()
        if current_time - self.start_time >= self.life_time:
            self.kill()