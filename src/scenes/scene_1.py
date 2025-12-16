# Importing Entity
from src.scenes.scene_entity import Scene

# Import systems
from src.systems.ui_sys import UI

# Importing objects
from src.objects.character.obj_player import Player

# Importing settings
from src.settings import *

class GameRunning(Scene):
    '''
        Classe to initializate the active Game Phase
    '''
    def __init__(self, scene_system):
        super().__init__(scene_system)
        self.player = None
        self.instance_ui = None

    def draw(self):
        self.player = Player("Edísio", 300, 300, "src/sprites/psg.png")
        self.instance_render.add_sprite(self.player, LAYER_CHARACTERS)
        self.instance_ui = UI()

    def handle_input(self):
        self.instance_input.update()
        self.instance_input.execute_movement_command(self.player)
        self.instance_input.execute_attack_command(self.player)
        self.instance_input.execute_dash_command(self.player)

    def update(self):
        self.handle_input()
        # Renderizando sprites
        self.instance_render.render_group.update()
        self.instance_render.render()
        # Updating User Interface
        self.instance_ui.display(self.player)
    
