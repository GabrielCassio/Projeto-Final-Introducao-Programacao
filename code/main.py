import pygame, sys
from settings import *
from level import Level
from audio import *

# Importando fonte
from fonts import carregar_fonte_padrao

# Importando telas
from tela_creditos import tela_creditos
from tela_inicial import tela_inicial
from tela_opcoes import tela_opcoes
from tela_gameover import tela_game_over

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.FULLSCREEN | pygame.SCALED | pygame.RESIZABLE)
        pygame.display.set_caption('Édiso: The Legend Of Rescue')
        self.clock = pygame.time.Clock()

        self.status = 'menu'
        self.font = pygame.font.Font(None, 50)

        self.level = Level(self.screen)
        self.running = True

        # Loading font
        self.fonte = carregar_fonte_padrao(18)
        self.audio = AudioManager()

    def reset_level(self):
        self.level = Level(self.screen)

    def run_menu(self):
        aplicar_config_audio(self.audio)
        self.audio.tocar_musica("MENU")
        self.status = tela_inicial(self.screen, WINDOW_WIDTH, WINDOW_HEIGHT)
    
    def run_menu_opcoes(self):
        aplicar_config_audio(self.audio)
        self.audio.tocar_musica("MENU")
        self.status = tela_opcoes(self.screen, WINDOW_WIDTH, WINDOW_HEIGHT)

    def run_menu_creditos(self):
        aplicar_config_audio(self.audio)
        self.audio.tocar_musica("CREDITOS")
        self.status = tela_creditos(self.screen, WINDOW_WIDTH, WINDOW_HEIGHT)

    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            
                # Evita sair com ESC se estiver na tela de Game Over (pois lá o ESC volta pro menu)
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE and self.status != 'game_over':
                         pygame.quit()
                         sys.exit()

            # --- Selecionando a tela com base nas Strings de retorno ---
            if self.status == "SAIR":
                self.running = False
            elif self.status == "OPÇÕES":
                self.status = "opções"
            elif self.status == "CRÉDITOS":
                self.status = "créditos"
            elif self.status == "INICIAR JOGO":
                self.reset_level() # Garante nível novo ao iniciar do menu
                self.status = "level"
            elif self.status == "MENU": 
                self.status = "menu"

            # --- Executando a lógica da tela atual ---
            if self.status == 'menu':
                self.run_menu()
            elif self.status == 'opções':
                self.run_menu_opcoes()
            elif self.status == 'créditos':
                self.run_menu_creditos()
            
            elif self.status == 'level':
                self.screen.fill(pygame.Color('#25131a'))
                dt = self.clock.tick(FPS) / 1000
                self.level.run(dt)

                # Checa se morreu
                if hasattr(self.level, 'player') and self.level.player.health <= 0:
                        self.status = 'game_over'
            
            elif self.status == 'game_over':
                action = tela_game_over(self.screen, WINDOW_WIDTH, WINDOW_HEIGHT)

                # 2. Baseado na resposta, tomamos a ação
                if action == "INICIAR JOGO":
                    self.reset_level() 
                    self.status = "level"
                
                elif action == "MENU":
                    self.reset_level()
                    self.status = "menu"
 
            pygame.display.update()

if __name__ == '__main__':
    game = Game()
    game.run()