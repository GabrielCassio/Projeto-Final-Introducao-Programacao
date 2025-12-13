import pygame
# Importing the identity classes
from src.objects.entity.obj_entity import Entity
# Importing Commands
from src.objects.components.obj_movement_command import MovementCommand
from src.objects.components.obj_dash_command import DashCommand
from src.objects.components.obj_attack_command import AttackCommand

class InputHandling:
    def __init__(self) -> None:
        # Declaring input handling variables
        self.command_history = []
        self.pressed_buttons = None

    def execute_movement_command(self, character: Entity) -> None:
        '''
            Movimentação de personagem em um plano.
        '''
        # Command instance
        move_command = None
        # Descloc variables
        desloc_x, desloc_y = 0, 0
        if (self.pressed_buttons[pygame.K_UP] or self.pressed_buttons[pygame.K_w]):
            character.direction = "UP"
            desloc_y -= 1
        if (self.pressed_buttons[pygame.K_LEFT] or self.pressed_buttons[pygame.K_a]):
            character.direction = "LEFT"
            desloc_x -= 1
        if (self.pressed_buttons[pygame.K_DOWN] or self.pressed_buttons[pygame.K_s]):
            character.direction = "DOWN"
            desloc_y += 1
        if (self.pressed_buttons[pygame.K_RIGHT] or self.pressed_buttons[pygame.K_d]):
            character.direction = "RIGHT"
            desloc_x += 1
        
        # Verify if our have a desloc movement
        if (desloc_x != 0 or desloc_y != 0):
            move_command = MovementCommand(character, dx=desloc_x, dy=desloc_y)
            move_command.execute()

        if (move_command != None): self.command_history.append(move_command)

    def execute_attack_command(self, character: Entity) -> None:
        attack_comand = AttackCommand(character)

        if (self.pressed_buttons[pygame.K_r] and character.bow_skill):
            attack_comand.execute_bow_attack()
            
        if character.melee_skill:
             attack_comand.execute_melee_attack()

        self.command_history.append(attack_comand)

    def execute_dash_command(self, character: Entity) -> None:
        dash_command = None
        if (self.pressed_buttons[pygame.K_SPACE]):
            dash_command = DashCommand(character)
            dash_command.execute()
        
        if (dash_command != None): self.command_history.append(dash_command)


    def update(self) -> None:
        self.pressed_buttons = pygame.key.get_pressed()
