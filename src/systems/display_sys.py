import pygame

class DisplayConfiguration():
    # /// Variables Config \\\
    # AR dimensions List
    dimensions_ar = {
        "FULL HD": (1920, 1080),
        "HD":(1280, 720),
        "NINTH HD": (640, 360)
        }
    
    surface_screen = None
    surface_icon = "./src/sprites/game_icon/window_icon.png"

    def test():
        pass

    def __init__(self):
        # /// Default configurations \\\
        pygame.display.set_caption("Édiso: The Game")

        # In PyGame, every time when you use an image, first load it
        icon_game_display = pygame.image.load(self.surface_icon)
        pygame.display.set_icon(icon_game_display)

        # For default the AR is 1280x720
        default_ar = self.dimensions_ar["HD"]
        print(default_ar)

        self.surface_screen = pygame.display.set_mode(default_ar) # Set of AR Game to default 1280x720
        
    def update(self):
        pygame.display.flip()
        # Fill screen with white color
        self.surface_screen.fill((255, 255, 255))


