import pygame

# Importing systems
from src.systems.inputs_sys import InputHandling
from src.systems.render_sys import RenderSystem
from src.systems.camera_sys import CameraSystem

class Scene:
    '''
       The entity class that functions as a superclass for any scene.
    '''

    def __init__(self, scene_system, map_width=4000, map_height=4000) -> None:
        # Instance variable of the scene system class
        self.instance_scene_sys = scene_system
        # Try catch the player reference and map reference
        self.player = None
        self.map_width = map_width
        self.map_height = map_height

        # Instance variable of the main surface to draw
        self.display_surface = pygame.display.get_surface()
        # Instance variable of the render system class
        self.instance_render    = RenderSystem()
        # Instance variable of the input hanlding class
        self.instance_input     = InputHandling()

        # Initializating the camera system --------------------------------------------
        screen_w, screen_h = pygame.display.get_surface().get_size()
        self.camera = CameraSystem(screen_w, screen_h, self.map_width, self.map_height)

        RenderSystem.set_camera(self.camera)
        # -----------------------------------------------------------------------------

    def handle_input(self) -> None:
        pass

    def draw(self) -> None:
        pass

    def update(self) -> None:
        pass
        
