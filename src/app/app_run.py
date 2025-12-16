import pygame
# Importing systems
import src.systems.display_sys as display_system
import src.systems.timers_sys as timer_system
import src.systems.render_sys as render_system
import src.systems.camera_sys as camera_system
import src.systems.inputs_sys as inputs_system
import src.systems.collision_sys as collision_system
import src.systems.scenes_sys as scenes_system
import src.systems.ui_sys as ui_system

# Importing settings do application layer
from settings import *

class App:
    '''
        Abstraction Game Loop to integrate systems.
    '''
    # Initializate Game
    def __init__(self):
        num_sucess_init_mods, num_fail_init_mods = pygame.init() # Setup the PyGame initializer
        state_initializer = pygame.get_init() # State of the starter by PyGame

        # Feedback para o terminal
        print(f"Nome do Arquivo: {__file__}")
        print(f"Todos os módulos foram inicializados com sucesso?\n- Sucessos: {num_sucess_init_mods}\n- Falhas: {num_fail_init_mods}")

        # ------------ Initialization Systems ---------------------
        # \\\\\\\\\\ Initialization System of Windows /////////////
        self.instance_display_config = display_system.DisplayConfiguration()
        display_width, display_height = self.instance_display_config.dimension_ar

        # \\\\\\\\\\ Initialization Cameras ///////////////
        self.instance_camera = camera_system.Camera(display_width, display_height)

        # \\\\\\\\\\ Initialization Timers ///////////////
        self.instance_timers = timer_system.Timers()

        # \\\\\\\\\\ Initialization Render ///////////////
        self.instance_render = render_system.RenderSystem()
        self.instance_render.initialization(self.instance_display_config.surface_screen, self.instance_camera)

        # \\\\\\\\\\ Initialization Scenes///////////////
        self.instance_collision = collision_system.Collision()

        # \\\\\\\\\\ Initialization Scenes///////////////
        self.instance_scenes = scenes_system.ScenesSystem()

        # \\\\\\\\\\ Initialization Inputs Handling ///////////////
        self.instance_input = inputs_system.InputHandling()
        # ----------------------------------------------------------


    def update(self):
       # Update Timers
       self.instance_timers.update()

       # Update Scene
       self.instance_scenes.update()
       self.instance_render.update()