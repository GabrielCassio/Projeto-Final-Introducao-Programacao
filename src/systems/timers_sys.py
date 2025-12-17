import pygame

class Timers:
    # Clock 
    delta_time = 0.0
    def __init__(self):
        self.clock_timer = pygame.time.Clock() # Set the clock of Game Running
    
    def update(self):
        Timers.delta_time = self.clock_timer.tick(60) / 1000.0
  