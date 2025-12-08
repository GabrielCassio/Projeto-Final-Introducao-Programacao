import pygame
import src.systems.display_sys as display_system
import src.systems.timers_sys as timer_system
import src.systems.render_sys as render_system
import src.systems.camera_sys as camera_system
import src.objects.entity.characters.player as obj_player

LAYER_BACKGROUND = 0
LAYER_CHARACTERS = 1
LAYER_FOREGROUND = 2

class App:
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
        self.instance_render = render_system.RenderSystem(self.instance_display_config.surface_screen, self.instance_camera)

        self.player = obj_player.Player("Edísio", "./sprites/psg.png", 300, 300)
        self.instance_render.add_sprite(self.player, LAYER_CHARACTERS)
        # ---------------------------------------------------------
        # Initializating sprites


    def update(self):
       self.instance_timers.update()
       self.instance_render.update()
       '''self.instance_display_config.update()'''