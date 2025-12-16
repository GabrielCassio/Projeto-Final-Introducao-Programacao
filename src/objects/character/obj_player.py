import pygame
from src.objects.character.obj_entity import Entity

class Player(Entity):

    def __init__(self, name: str, x: int, y: int, path_sprite: str):
        # Fixed: Do not pass 'self' to super().__init__
        super().__init__(self, x, y, path_sprite)

        # Setup
        self.walls = []

        # Load the image
        original_image = pygame.image.load(path_sprite).convert_alpha()

        # Initializing the sprite of player
        SCALE_FACTOR = 2.4 
        w, h = original_image.get_size()
        self.image = pygame.transform.scale(original_image, (int(w * SCALE_FACTOR), int(h * SCALE_FACTOR)))
        
        # 1. VISUAL RECT (Total size of the image)
        self.rect = self.image.get_rect(topleft = (x, y))

        # 2. PHYSICS HITBOX (The magic happens here)
        # .inflate(width_change, height_change) shrinks the rect relative to its center.
        # -10 on width: Makes the hitbox slightly thinner.
        # -70 on height: Cuts off the head and torso from collision (adjust this value based on your sprite height).
        self.hitbox = self.rect.inflate(-10, -70)
        
        # Stats setup
        self.stats = {'health': 100, 'energy': 60, 'attack': 10, 'magic': 4, 'speed': 6}
        self.max_stats = {'health': 300, 'energy': 140, 'attack': 20, 'magic': 10, 'speed': 10}
        self.upgrade_cost = {'health': 100, 'energy': 100, 'attack': 100, 'magic': 100, 'speed': 100}
        self.health = self.stats['health']
        self.energy = self.stats['energy']
        self.exp = 120
        self.speed = self.stats['speed']

    def move(self, new_position_x: int, new_position_y: int) -> None:
        
        # Guardar posição antiga da HITBOX
        old_hitbox_rect = self.hitbox.copy() # Usamos copy para salvar o rect inteiro

        self.old_position.x = self.rect.x
        self.old_position.y = self.rect.y

        # --- EIXO X (Horizontal) ---
        self.rect.x = new_position_x
        # Sincroniza: O centro X continua igual (alinhado no meio do corpo)
        self.hitbox.centerx = self.rect.centerx 
        
        if hasattr(self, 'walls') and self.walls:
            if self.hitbox.collidelist(self.walls) != -1:
                self.hitbox.centerx = old_hitbox_rect.centerx # Volta X
                self.rect.centerx = self.hitbox.centerx       # Puxa visual

        # --- EIXO Y (Vertical) ---
        self.rect.y = new_position_y
        
        # AQUI É A MUDANÇA: Sincroniza pelo PÉ (Bottom) e não pelo centro
        self.hitbox.bottom = self.rect.bottom
        
        if hasattr(self, 'walls') and self.walls:
            if self.hitbox.collidelist(self.walls) != -1:
                # Bateu! Volta a hitbox para a posição Y antiga
                self.hitbox.bottom = old_hitbox_rect.bottom
                # Puxa o visual de volta alinhando pelos pés
                self.rect.bottom = self.hitbox.bottom

    def load_sprite(self, x: int, y: int, path_sprite: str):
        self.image = pygame.image.load(path_sprite).convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        # Important: Re-create the hitbox if the sprite changes
        self.hitbox = self.rect.inflate(-10, -70) 

    def animation(self):
        # Animation logic continues to use self.rect
        delta_pos_horizontal = self.rect.x - self.old_position.x
        delta_pos_vertical = self.rect.y - self.old_position.y

        if (delta_pos_horizontal > 0): self.sprite_direction = 'right'
        elif (delta_pos_horizontal < 0): self.sprite_direction = 'left'

        if (delta_pos_vertical > 0): self.sprite_direction = 'down'
        elif (delta_pos_vertical < 0): self.sprite_direction = 'up'

    def update(self):
        self.animation()