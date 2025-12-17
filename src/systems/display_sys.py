import pygame

class DisplayConfiguration():
    # /// Variables Config \\\
    # Defining the ar for default
    current_ar = 'HD'

    # AR dimensions Dictionary
    all_dimensions_ar = {
        'FULL HD': (1920, 1080),
        'HD':(1280, 720),
        'NINTH HD': (640, 360)}

    # Id surface screen of the game
    surface_screen = None
    # Path of icon of the main window
    surface_icon = "src/sprites/game_icon/window_icon.png"

    def __init__(self):
        # /// Default configurations \\\
        pygame.display.set_caption("Édiso: The Game")

        # In PyGame, every time when you use an image, first load it
        icon_game_display = pygame.image.load(self.surface_icon)
        pygame.display.set_icon(icon_game_display)

        # For default the AR is 1280x720
        self.dimension_ar = self.all_dimensions_ar[self.current_ar]
        print(self.dimension_ar)

        self.surface_screen = pygame.display.set_mode(self.dimension_ar, pygame.RESIZABLE | pygame.SCALED) # Set of AR Game to default 1280x720
