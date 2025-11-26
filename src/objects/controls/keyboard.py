import pygame

def keyboard_movement(x_coordinate: int, y_coordinate: int, x_velocity: int, y_velocity: int) -> tuple:

    # Catch the current event
    event = pygame.event.get()

    # Verify the type of current event
    if (event.type == pygame.KEYDOWN):
        if (event.key == pygame.K_UP):
            y_coordinate -= y_velocity
        if (event.key == pygame.K_LEFT):
            x_coordinate -= x_velocity 
        if (event.key == pygame.K_DOWN):
            y_coordinate += y_velocity
        if (event.key == pygame.K_RIGHT):
            x_coordinate -= x_velocity
    
    return (x_coordinate, y_coordinate)