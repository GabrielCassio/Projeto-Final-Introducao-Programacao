import pygame

def input_keyboard_handling(x_coordinate: int, y_coordinate: int, velocity: int) -> tuple:
    # Calc the current direction of player
    direction = pygame.Vector2(0, 0)

    # Catching the list of all pressed keys
    keys = pygame.key.get_pressed()
    
    # Verify the type of current event
    if (keys[pygame.K_UP] or keys[pygame.K_s]):
        direction.y -= 1
    if (keys[pygame.K_LEFT] or keys[pygame.K_a]):
        direction.x -= 1
    if (keys[pygame.K_DOWN] or keys[pygame.K_w]):
        direction.y += 1
    if (keys[pygame.K_RIGHT] or keys[pygame.K_d]):
        direction.x += 1

    # Verify the current 
    if (direction.length() > 0): direction = direction.normalize()

    x_coordinate += direction.x * velocity
    y_coordinate += direction.y * velocity
    
    return (x_coordinate, y_coordinate)