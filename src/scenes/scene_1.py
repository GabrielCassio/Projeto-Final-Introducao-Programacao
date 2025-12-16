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
        Classe to initializate the active Game Phase
    '''
    def __init__(self, scene_system):
        
        super().__init__(scene_system, 4000, 4000)

        self.display_surface = pygame.display.get_surface()
        self.player = Player("Edísio", 300, 300, "src/sprites/psg.png")
        self.instance_ui = UI()

        self.fonte_moeda = pygame.font.SysFont('arial', 22, bold=True)
        self.fonte_info = pygame.font.SysFont('arial', 14)

        self.moedas_list = [
            Coin(300, 200),
            Coin(350, 240),
            Coin(400, 180),
            Coin(450, 220)
        ]
        
        self.Badge = Badge(650, 250)
        self.Trophy = None

        self.boss_morto = False
        self.cracha_coletado = False
        
        self.moedas_reais = 0
        self.moedas_animadas = 0.0
        
        # Variáveis visuais da UI
        self.moeda_offset_y = 0
        self.flash_moeda = 0
        self.icon_scale = 1.0

    def draw(self):
        self.display_surface.fill('white')
        self.instance_render.add_sprite(self.player, LAYER_CHARACTERS)
        self.instance_ui.display(self.player)

        # Adicionar moedas ativas ao render
        for Coin in self.moedas_list:
            if hasattr(Coin, 'ativa') and Coin.ativa:
                 # Assumindo que Coin é um Sprite, adicionamos ao render group
                 # Se o sistema exigir 'add_sprite', usamos aqui:
                 self.instance_render.add_sprite(Coin, LAYER_CHARACTERS)

        # Adicionar crachá ao render
        if self.Badge.active:
            self.instance_render.add_sprite(self.Badge, LAYER_CHARACTERS)

        # Adicionar troféu ao render
        if self.Trophy and self.Trophy.ativo:
            self.instance_render.add_sprite(self.Trophy, LAYER_CHARACTERS)

        # --- Renderizar UI Customizada (Do Código B) ---
        self.draw_custom_hud()

    def draw_custom_hud(self):
        """
        Método auxiliar para desenhar a HUD específica de moedas e ícones
        trazida do Código B.
        """
        WIDTH, HEIGHT = self.display_surface.get_size()

        # Cores
        cor_moeda = (120, 230, 170)
        if self.flash_moeda > 0:
            cor_moeda = (170, 255, 210)

        valor_hud = int(self.moedas_animadas + 0.5)

        x_hud = WIDTH - 100
        y_hud = 26 + self.moeda_offset_y

        cx = x_hud - 18
        cy = y_hud + 10

        # Desenho do ícone de Coin (Geminha)
        pontos = [
            (cx, cy - int(7 * self.icon_scale)),
            (cx + int(7 * self.icon_scale), cy),
            (cx, cy + int(7 * self.icon_scale)),
            (cx - int(7 * self.icon_scale), cy)
        ]
        pygame.draw.polygon(self.display_surface, (90, 200, 140), pontos)

        pontos2 = [
            (cx, cy - int(4 * self.icon_scale)),
            (cx + int(4 * self.icon_scale), cy),
            (cx, cy + int(4 * self.icon_scale)),
            (cx - int(4 * self.icon_scale), cy)
        ]
        pygame.draw.polygon(self.display_surface, (150, 255, 200), pontos2)

        # Texto da Coin
        texto_moeda = self.fonte_moeda.render(str(valor_hud), True, cor_moeda)
        self.display_surface.blit(texto_moeda, (x_hud, y_hud))

        # Indicador de Crachá Coletado (Canto inferior esquerdo)
        if self.cracha_coletado:
            cx_cracha = 44
            cy_cracha = HEIGHT - 44

            pygame.draw.circle(self.display_surface, (20, 20, 30), (cx_cracha, cy_cracha), 34)
            pygame.draw.circle(self.display_surface, (120, 200, 255), (cx_cracha, cy_cracha), 12)

        ''' # Texto de Debug/Info
        info = self.fonte_info.render('B -> matar boss (teste)', True, (160, 160, 160))
        self.display_surface.blit(info, (12, 12))'''

    def handle_input(self):
        self.instance_input.update()
        self.instance_input.execute_movement_command(self.player)
        self.instance_input.execute_attack_command(self.player)
        self.instance_input.execute_dash_command(self.player)

        keys = pygame.key.get_pressed()
        if keys[pygame.K_b]:
            if not self.boss_morto:
                self.boss_morto = True
                self.Trophy = Trophy(380, 230)
                print("Boss derrotado! Troféu spawnado.")

    def update(self):
        self.handle_input()

        self.camera.update(self.player)

        # 1. Atualizar e Checar Moedas
        for Coin in self.moedas_list:
            if Coin.ativa:
                # IMPORTANTE: Passamos self.player aqui para o imã funcionar
                Coin.update(self.player)
                
                # Checar Colisão
                if self.player.rect.colliderect(Coin.rect):
                    Coin.ativa = False
                    Coin.kill() # Remove do grupo de sprites do pygame se estiver lá
                    self.moedas_reais += 1
                    
                    # Efeitos Visuais UI
                    self.moeda_offset_y = -8
                    self.flash_moeda = 14
                    self.icon_scale = 1.25

        # 2. Atualizar Crachá
        if hasattr(self.Badge, 'update'): self.Badge.update()
        elif hasattr(self.Badge, 'atualizar'): self.Badge.atualizar()
        
        if self.Badge.active and self.player.rect.colliderect(self.Badge.rect):
            self.Badge.active = False
            self.Badge.kill()
            self.cracha_coletado = True

        # 3. Atualizar Troféu (se existir)
        if self.Trophy:
            if hasattr(self.Trophy, 'update'): self.Trophy.update()
            
            if self.Trophy.ativo and self.player.rect.colliderect(self.Trophy.rect):
                self.Trophy.iniciar_coleta()

        self.moedas_animadas += (self.moedas_reais - self.moedas_animadas) * 0.15
        if abs(self.moedas_reais - self.moedas_animadas) < 0.02:
            self.moedas_animadas = float(self.moedas_reais)

        self.moeda_offset_y += (0 - self.moeda_offset_y) * 0.2
        self.icon_scale += (1.0 - self.icon_scale) * 0.18
        if self.flash_moeda > 0: self.flash_moeda -= 1

        # Renderizando sprites
        self.instance_render.render_group.update()

