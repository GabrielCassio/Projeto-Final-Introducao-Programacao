# Main file of template by PyGame

# Config paths libs
import pathlib, sys
# Defining source as root
sourceDir = pathlib.Path(__file__).resolve().parents
sys.path.append(str(sourceDir))

import pygame
import app.app_run as app_run

# Instancing Game Application
instance_app_run = app_run.App()
instance_app_run.initializate()

running = True
while (running):

    # pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    instance_app_run.update()

# Exit the game
pygame.quit()