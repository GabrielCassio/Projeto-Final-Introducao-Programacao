import pygame
import systems.display_sys as display_system
import systems.timers_sys as timer_system

class App:
    # \\\\\\\\\\ Instance Systems ///////////////
    instance_display_config = display_system.DisplayConfiguration()
    instance_timers = timer_system.Timers()

    def initializate(self):
        num_sucess_init_mods, num_fail_init_mods = pygame.init() # Setup the PyGame initializer
        state_initializer = pygame.get_init() # State of the starter by PyGame

        print(f"Nome do Arquivo: {__file__}")
        print(f"Todos os módulos foram inicializados com sucesso?\n- Sucessos: {num_sucess_init_mods}\n- Falhas: {num_fail_init_mods}")

        # \\\\\\\\\\ Initialization System of Windows /////////////
        self.instance_display_config.init()

        # \\\\\\\\\\ Initialization Timers ///////////////
        self.instance_timers.init()

         # \\\\\\\\\\ Initialization Scenes ///////////////

    def update(self):
       self.instance_timers.update()
       self.instance_display_config.update()

