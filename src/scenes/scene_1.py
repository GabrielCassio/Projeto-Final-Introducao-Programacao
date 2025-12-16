import pygame

# Importing Entity
from src.scenes.scene_entity import Scene

# Import systems
from src.systems.ui_sys import UI

# Importing objects
from src.objects.character.obj_player import Player
from src.objects.collectibles.obj_badge import Badge
from src.objects.collectibles.obj_coin import Coin
from src.objects.collectibles.obj_trophy import Trophy

# Importing settings
from src.settings import *

class GameRunning(Scene):
    '''
        Class to initialize the active Game Phase.
        Inherits from 'Scene', implying a scene management system exists.
    '''
    def __init__(self, scene_system):
        # 1. Load the original image FIRST into a temporary variable
        img_temp = pygame.image.load('src/sprites/map/map_scene1.png').convert_alpha()
        
        # 2. Get its original size (e.g., 800x600)
        original_width, original_height = img_temp.get_size()

        # 3. Define how many times you want to increase it (e.g., 4 times bigger)
        SCALE_FACTOR = 4.0 
        
        # The code calculates new sizes automatically, keeping the proportion
        new_width = int(original_width * SCALE_FACTOR)
        new_height = int(original_height * SCALE_FACTOR)

        # 4. Now initialize the scene with the perfect calculated sizes
        super().__init__(scene_system, new_width, new_height)

        self.display_surface = pygame.display.get_surface()

        # 5. Finally, create the scaled image using the calculated values
        self.floor_surf = pygame.transform.scale(img_temp, (new_width, new_height))
        self.floor_rect = self.floor_surf.get_rect(topleft=(0, 0))
        
        # Instantiate the Player ("Edísio") at position (300, 300)
        self.player = Player("Edísio", 3550, 3600, "src/sprites/psg.png")
        
        # Instantiate the default UI
        self.instance_ui = UI()

        # Font configuration
        self.fonte_moeda = pygame.font.SysFont('arial', 22, bold=True)
        self.fonte_info = pygame.font.SysFont('arial', 14)

        # Create a list of coins manually at specific positions
        self.moedas_list = [
            Coin(300, 200),
            Coin(350, 240),
            Coin(400, 180),
            Coin(450, 220)
        ]
        
        # Create the Badge object and set Trophy to None (initially)
        self.Badge = Badge(650, 250)
        self.Trophy = None

        # State Flags
        self.boss_morto = False      # Is boss dead?
        self.cracha_coletado = False # Is badge collected?
        
        # --- UI Animation Variables ---
        self.moedas_reais = 0      # Actual coin count
        self.moedas_animadas = 0.0 # Visual coin count (for smooth animation)
        
        self.moeda_offset_y = 0    # Y offset for the "jump" effect
        self.flash_moeda = 0       # Timer for the color flash effect
        self.icon_scale = 1.0      # Scale for the icon pulse effect

    def draw(self):
        self.display_surface.fill(pygame.Color('#25131a'))
        
        self.camera_offset = self.camera.offset_float

        floor_offset_pos = self.floor_rect.topleft - self.camera_offset
        self.display_surface.blit(self.floor_surf, floor_offset_pos)
        
        # Add player to render group
        self.instance_render.add_sprite(self.player, LAYER_CHARACTERS)
        
        # Draw default UI
        self.instance_ui.display(self.player)

        # Add active coins to the render group
        for Coin in self.moedas_list:
            if hasattr(Coin, 'ativa') and Coin.ativa:
                 # Assuming Coin is a Sprite, we add it to the render group
                 self.instance_render.add_sprite(Coin, LAYER_CHARACTERS)

        # Add badge to render group if active
        if self.Badge.active:
            self.instance_render.add_sprite(self.Badge, LAYER_CHARACTERS)

        # Add trophy to render group if active
        if self.Trophy and self.Trophy.ativo:
            self.instance_render.add_sprite(self.Trophy, LAYER_CHARACTERS)

        # --- Render Custom UI (Overlay) ---
        self.draw_custom_hud()

    def draw_custom_hud(self):
        """
        Helper method to draw the specific HUD for coins and icons.
        """
        WIDTH, HEIGHT = self.display_surface.get_size()

        # Colors logic: Normal green or Light green if flashing
        cor_moeda = (120, 230, 170)
        if self.flash_moeda > 0:
            cor_moeda = (170, 255, 210)

        # Round the animated float value to int for display
        valor_hud = int(self.moedas_animadas + 0.5)

        # Positioning (Top Right)
        x_hud = WIDTH - 100
        y_hud = 26 + self.moeda_offset_y # Apply jump offset

        cx = x_hud - 18
        cy = y_hud + 10

        # Draw Coin Icon (Diamond/Gem shape) using polygons
        pontos = [
            (cx, cy - int(7 * self.icon_scale)), # Top
            (cx + int(7 * self.icon_scale), cy), # Right
            (cx, cy + int(7 * self.icon_scale)), # Bottom
            (cx - int(7 * self.icon_scale), cy)  # Left
        ]
        pygame.draw.polygon(self.display_surface, (90, 200, 140), pontos)

        # Inner diamond for detail
        pontos2 = [
            (cx, cy - int(4 * self.icon_scale)),
            (cx + int(4 * self.icon_scale), cy),
            (cx, cy + int(4 * self.icon_scale)),
            (cx - int(4 * self.icon_scale), cy)
        ]
        pygame.draw.polygon(self.display_surface, (150, 255, 200), pontos2)

        # Render Coin Text
        texto_moeda = self.fonte_moeda.render(str(valor_hud), True, cor_moeda)
        self.display_surface.blit(texto_moeda, (x_hud, y_hud))

        # Collected Badge Indicator (Bottom Left Corner)
        if self.cracha_coletado:
            cx_cracha = 44
            cy_cracha = HEIGHT - 44

            pygame.draw.circle(self.display_surface, (20, 20, 30), (cx_cracha, cy_cracha), 34)
            pygame.draw.circle(self.display_surface, (120, 200, 255), (cx_cracha, cy_cracha), 12)

        ''' # Debug Info Text
        info = self.fonte_info.render('B -> kill boss (test)', True, (160, 160, 160))
        self.display_surface.blit(info, (12, 12))'''

    def handle_input(self):
        self.instance_input.update()
        
        # Execute movement and combat commands
        self.instance_input.execute_movement_command(self.player)
        self.instance_input.execute_attack_command(self.player)
        self.instance_input.execute_dash_command(self.player)

        # --- DEBUG / CHEAT ---
        # Press 'B' to kill boss and spawn trophy
        keys = pygame.key.get_pressed()
        if keys[pygame.K_b]:
            if not self.boss_morto:
                self.boss_morto = True
                self.Trophy = Trophy(380, 230)
                print("Boss defeated! Trophy spawned.")

    def update(self):
        self.handle_input()
        self.camera.update(self.player)

        # 1. Update and Check Coins
        for Coin in self.moedas_list:
            if Coin.ativa:
                # IMPORTANT: Pass self.player here for the magnet effect to work
                Coin.update(self.player)
                
                # Check Collision
                if self.player.rect.colliderect(Coin.rect):
                    Coin.ativa = False
                    Coin.kill() # Remove from pygame sprite groups
                    self.moedas_reais += 1
                    
                    # UI Visual Effects ("Juice")
                    self.moeda_offset_y = -8  # Jump up
                    self.flash_moeda = 14     # Flash duration
                    self.icon_scale = 1.25    # Pulse scale

        # 2. Update Badge
        if hasattr(self.Badge, 'update'): self.Badge.update()
        elif hasattr(self.Badge, 'atualizar'): self.Badge.atualizar()
        
        # Check Badge Collision
        if self.Badge.active and self.player.rect.colliderect(self.Badge.rect):
            self.Badge.active = False
            self.Badge.kill()
            self.cracha_coletado = True

        # 3. Update Trophy (if it exists)
        if self.Trophy:
            if hasattr(self.Trophy, 'update'): self.Trophy.update()
            
            if self.Trophy.ativo and self.player.rect.colliderect(self.Trophy.rect):
                self.Trophy.iniciar_coleta() # Start collection logic

        # --- UI MATH / LERP (Linear Interpolation) ---
        # Smoothly move the displayed number towards the real number
        self.moedas_animadas += (self.moedas_reais - self.moedas_animadas) * 0.15
        
        # Snap to value if very close (avoids infinite decimals)
        if abs(self.moedas_reais - self.moedas_animadas) < 0.02:
            self.moedas_animadas = float(self.moedas_reais)

        # Return visual effects to default state smoothly
        self.moeda_offset_y += (0 - self.moeda_offset_y) * 0.2
        self.icon_scale += (1.0 - self.icon_scale) * 0.18
        
        if self.flash_moeda > 0: self.flash_moeda -= 1

        # Update render group sprites
        self.instance_render.render_group.update()