import pygame
# Importing the identity classes
from src.objects.character.obj_entity import Entity
# Importing Commands
from src.objects.commands.obj_movement_command import MovementCommand
from src.objects.commands.obj_dash_command import DashCommand
from src.objects.commands.obj_attack_command import MeleeCommand, RangedCommand

class InputHandling:

    def __init__(self) -> None:
       # Declaring input handling variables
       self.command_history = []
       self.pressed_buttons = pygame.key.get_pressed()
       self.pressed_mouse = pygame.mouse.get_pressed()
        
    def execute_movement_command(self, character: Entity) -> None:
        '''
            Command to move a character entity in a 2D plane.
        '''
        # Command instance
        move_command = None
        
        # Descloc variables
        desloc_x, desloc_y = 0, 0
        if (self.pressed_buttons[pygame.K_UP] or self.pressed_buttons[pygame.K_w]):
            character.self_direction = "up"
            desloc_y -= 1
        if (self.pressed_buttons[pygame.K_LEFT] or self.pressed_buttons[pygame.K_a]):
            character.self_direction = "left"
            desloc_x -= 1
        if (self.pressed_buttons[pygame.K_DOWN] or self.pressed_buttons[pygame.K_s]):
            character.self_direction = "down"
            desloc_y += 1
        if (self.pressed_buttons[pygame.K_RIGHT] or self.pressed_buttons[pygame.K_d]):
            character.self_direction = "right"
            desloc_x += 1
        
        # Verify if our have a desloc movement
        if (desloc_x != 0 or desloc_y != 0):
            move_command = MovementCommand(character, dx=desloc_x, dy=desloc_y)
            move_command.execute()

        if (move_command != None): self.command_history.append(move_command)

    def execute_melee_attack_command(self, character: Entity) -> None:
        '''
            Execute melee attack command
        '''
        melee_attack_comand = MeleeCommand(character)

        if (self.pressed_buttons[pygame.K_r]):
            print("Melee Attack Command Executed")
            melee_attack_comand.execute()
    
        self.command_history.append(melee_attack_comand)
    
    def execute_ranged_attack_command(self, character: Entity) -> None:
        '''
            Execute ranged attack command
        '''
        ranged_attack_comand = RangedCommand(character)

        if (self.pressed_buttons[pygame.K_t] or self.pressed_mouse[0]):
            print("Ranged Attack Command Executed")
            ranged_attack_comand.execute()
    
        self.command_history.append(ranged_attack_comand)
    

    def execute_dash_command(self, character: Entity) -> None:
        '''
            Execute dash command
        '''
        dash_command = None
        if (self.pressed_buttons[pygame.K_SPACE]):
            dash_command = DashCommand(character)
            dash_command.execute()
        
        if (dash_command != None): self.command_history.append(dash_command)

    def update(self) -> None:
        self.pressed_buttons = pygame.key.get_pressed()
