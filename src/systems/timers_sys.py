import pygame

class Timers:
    # Clock 
    clock_timer = 0
    def __init__(self):
        self.clock_timer = pygame.time.Clock() # Set the clock of Game Running
        return self.clock_timer
    
    def update(self):
        self.clock_timer.tick(60)  # limit FPS to 60