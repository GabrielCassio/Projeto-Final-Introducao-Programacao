import pygame
from src.objects.entity.obj_entity import Entity
from src.systems.inputs_sys import InputHandling
from src.objects.components.obj_attack_command import AttackCommand

# This class create a new Player Object
# This class inherints de class of the pygame - pygame.sprite.Sprite
class Player(Entity):

    # Class initialization
    def __init__(self, name: str, x: int, y: int, path_sprite: str):
        # Acessing de parent of the Player class
        super().__init__(self, x, y, path_sprite)
        self.load_sprite(x, y, path_sprite)

        self.direction = 'RIGHT' 
        
        # Dash
        self.max_dashes = 2
        self.dash_charges = self.max_dashes
        self.dash_cooldown_time = 2000 
        self.last_recharge_time = 0
        self.dash_distance = 60 
        self.last_dash_click = 0
        self.spam_protection = 200 

        # Combate
        self.melee_skill = True
        self.bow_skill = True
        self.global_action_cooldown = 0 
        self.time_atk_1 = 300 
        self.time_atk_2 = 500 
        self.delay_after_action = 400
        self.frames_atk_1 = 18 
        self.frames_atk_2 = 30 
        
        # Combo
        self.pending_second_hit = False
        self.second_hit_timer = 0
        
        # Ranged
        self.last_shot = 0
        self.shot_cooldown = 500

        # Initializating the sprite of player
        self.load_sprite(x, y, path_sprite)
        self.attack_cmd = AttackCommand(self)

    def move(self, new_position_x: int, new_position_y: int) -> None:

        # Store old position
        self.old_position.x = self.rect.x
        self.old_position.y = self.rect.y

        # Loading new position
        self.rect.x = new_position_x
        self.rect.y = new_position_y

    def load_sprite(self, x: int, y: int, path_sprite: str):
        # Loading sprite/skin to this player
        self.image = pygame.image.load(path_sprite).convert_alpha()
        # Catching rect collision of the sprite
        self.rect = self.image.get_rect()
        # Position tuple of the char
        self.rect.center = (x, y)

    def animation(self):
        
        # Position variation
        delta_pos_horizontal = self.rect.x - self.old_position.x
        delta_pos_vertical = self.rect.y - self.old_position.y

        if (delta_pos_horizontal > 0): self.sprite_direction = 'right'
        elif (delta_pos_horizontal < 0): self.sprite_direction = 'left'

        if (delta_pos_vertical > 0): self.sprite_direction = 'down'
        elif (delta_pos_vertical < 0): self.sprite_direction = 'up'
    


    def recharge_stamina(self):
        now = pygame.time.get_ticks()
        if self.dash_charges < self.max_dashes:
            if now - self.last_recharge_time > self.dash_cooldown_time:
                self.dash_charges += 1
                self.last_recharge_time = now

    def update(self):
        self.animation()
        self.recharge_stamina()

        self.attack_cmd.execute_bow_attack() 
