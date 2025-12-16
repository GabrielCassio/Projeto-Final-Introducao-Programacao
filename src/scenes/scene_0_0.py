import pygame, os, random, sys

# Importing scene entity
from src.scenes.scene_entity import Scene

# Importing settings
from src.settings import *

# Imorting Assets
from src.sprites.home_screen_assets import *

class GameHome(Scene):
    '''
        Initial Scene of the Game/ Home Scene
    '''
    def __init__(self, scene_system):
        # Calling the superclass scene and passing de system scene instance
        super().__init__(scene_system)
    
        
        self.width = self.display_surface.get_width()
        self.height = self.display_surface.get_height()
        
        # --- CARREGAMENTO DE ASSETS ---
        pasta_atual = os.path.dirname(__file__)
        # Ajuste o caminho abaixo conforme a estrutura real das suas pastas
        # Ex: Se este arquivo está em /src/scenes, o assets está em ../../assets
        caminho_assets = os.path.join(pasta_atual, '..', 'sprites', 'home_screen_assets')
        caminho_fonts = os.path.join(pasta_atual, '..', 'fonts')
        
        # Fundo animado
        self.fundos = []
        for i in range(1, 7):
            try:
                caminho_img = os.path.join(caminho_assets, f'fundo0{i}.png')
                img = pygame.image.load(caminho_img).convert()
                img = pygame.transform.scale(img, (self.width, self.height))
                self.fundos.append(img)
            except FileNotFoundError:
                print(f"ERRO: Imagem {caminho_img} não encontrada.")
                # Cria fallback preto se falhar
                surf = pygame.Surface((self.width, self.height))
                self.fundos.append(surf)

        # Caveira
        try:
            self.caveira = pygame.image.load(os.path.join(caminho_assets, 'caveira.png')).convert_alpha()
            self.caveira = pygame.transform.scale(self.caveira, (26, 26))
        except:
            self.caveira = pygame.Surface((26, 26))
            self.caveira.fill((255, 255, 255))

        # Fontes
        try:
            caminho_fonte = os.path.join(caminho_fonts, 'PixelifySans-Regular.ttf')
            self.fonte_titulo = pygame.font.Font(caminho_fonte, 64)
            self.fonte_menu = pygame.font.Font(caminho_fonte, 28)
        except:
            print("Fonte não encontrada, usando padrão do sistema.")
            self.fonte_titulo = pygame.font.SysFont('arial', 64)
            self.fonte_menu = pygame.font.SysFont('arial', 28)

        # --- VARIÁVEIS DE ESTADO ---
        self.opcoes = ['INICIAR JOGO', 'OPÇÕES', 'CRÉDITOS', 'SAIR']
        self.selecionado = 0
        
        self.particulas_titulo = []
        self.particulas_menu = []
        
        self.frame_fundo = 0
        self.tempo = 0
        self.caveira_y_atual = 240
    
    def criar_particula_titulo(self):
        return {
            'x': self.width // 2 + random.randint(-90, 90),
            'y': 140,
            'vida': random.randint(18, 30),
            'dx': random.choice([-1, 0, 1]),
            'dy': random.randint(-2, -1),
            'cor': random.choice([(255, 110, 40), (255, 150, 60), (220, 80, 30)]),
            'tam': random.choice([2, 3])
        }

    def criar_particula_menu(self, y_base):
        return {
            'x': self.width // 2 + random.randint(-70, 70),
            'y': y_base + random.randint(-2, 2),
            'vida': random.randint(14, 22),
            'dx': random.choice([-1, 0, 1]),
            'dy': random.uniform(-0.8, -0.4),
            'cor': random.choice([(230, 150, 100), (210, 130, 90), (255, 180, 120)]),
            'tam': random.choice([1, 2])
        }
    
    def executar_acao(self):
        opcao = self.opcoes[self.selecionado]
        if opcao == 'SAIR':
            pygame.quit()
            sys.exit()
        elif opcao == 'INICIAR JOGO':
            # Lógica para trocar de cena
            print("Iniciando Jogo...") 
            self.instance_scene_sys.switch_scene('Game Running') 
        elif (opcao == 'OPÇÕES'):
            self.instance_scene_sys.switch_scene('Home Options')
            print(f"Você selecionou: {opcao}")
        elif (opcao == 'CRÉDITOS'):
            self.instance_scene_sys.swicth_scene('Home Credits')
            print(f"Você selecionou: {opcao}")

    def handle_input(self):
        # Captura eventos apenas se o loop principal não o fizer
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_UP:
                    self.selecionado = (self.selecionado - 1) % len(self.opcoes)
                if evento.key == pygame.K_DOWN:
                    self.selecionado = (self.selecionado + 1) % len(self.opcoes)
                if evento.key == pygame.K_RETURN:
                    self.executar_acao()
                    
    def draw_background(self):
        if self.fundos:
            self.display_surface.blit(self.fundos[int(self.frame_fundo)], (0, 0))
        else:
            self.display_surface.fill((0, 0, 0))
    
    def draw(self):
        self.draw_background()
        
        # 1. Partículas do Título
        for p in self.particulas_titulo:
            pygame.draw.rect(
                self.display_surface,
                p['cor'],
                pygame.Rect(p['x'], p['y'], p['tam'], p['tam'])
            )

        # 2. Título (ÉDISO)
        # Borda
        for dx, dy in [(-2,0),(2,0),(0,-2),(0,2)]:
            borda = self.fonte_titulo.render('ÉDISO', True, (180, 90, 20))
            self.display_surface.blit(borda, (self.width//2 - borda.get_width()//2 + dx, 70 + dy))
        # Frente
        titulo = self.fonte_titulo.render('ÉDISO', True, (255, 170, 90))
        self.display_surface.blit(titulo, (self.width//2 - titulo.get_width()//2, 70))

        # 3. Subtítulo
        # Borda
        for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
            borda = self.fonte_menu.render('THE LEGEND OF THE RESCUE', True, (80, 40, 120))
            self.display_surface.blit(borda, (self.width//2 - borda.get_width()//2 + dx, 135 + dy))
        # Frente
        subtitulo = self.fonte_menu.render('THE LEGEND OF THE RESCUE', True, (170, 120, 255))
        self.display_surface.blit(subtitulo, (self.width//2 - subtitulo.get_width()//2, 135))

        # 4. Partículas do Menu
        for p in self.particulas_menu:
            pygame.draw.rect(
                self.display_surface,
                p['cor'],
                pygame.Rect(p['x'], p['y'], p['tam'], p['tam'])
            )

        # 5. Menu
        base_y = 240
        for i, opcao in enumerate(self.opcoes):
            cor = (200, 160, 255) if i == self.selecionado else (150, 120, 200)

            # Borda do texto
            for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
                borda = self.fonte_menu.render(opcao, True, (60, 30, 90))
                self.display_surface.blit(
                    borda, 
                    (self.width//2 - borda.get_width()//2 + dx, base_y + i*42 + dy)
                )

            # Texto principal
            texto = self.fonte_menu.render(opcao, True, cor)
            self.display_surface.blit(
                texto, 
                (self.width//2 - texto.get_width()//2, base_y + i*42)
            )

        # 6. Caveira
        self.display_surface.blit(
            self.caveira,
            (self.width//2 - 118, self.caveira_y_atual)
        )

    def update(self):
        self.tempo += 1
        
        # Animação do fundo
        if self.fundos:
            self.frame_fundo = (self.frame_fundo + 0.15) % len(self.fundos)

        # Atualiza input
        self.handle_input()

        # Partículas Título
        if len(self.particulas_titulo) < 90:
            self.particulas_titulo.append(self.criar_particula_titulo())

        for p in self.particulas_titulo[:]:
            p['x'] += p['dx']
            p['y'] += p['dy']
            p['vida'] -= 1
            if p['vida'] <= 0:
                self.particulas_titulo.remove(p)

        # Física da Caveira (Lerp)
        base_y = 240
        alvo_caveira_y = base_y + self.selecionado * 42 + 6
        self.caveira_y_atual += (alvo_caveira_y - self.caveira_y_atual) * 0.2

        # Partículas Menu
        y_fogo_menu = base_y + self.selecionado * 42 - 4
        if len(self.particulas_menu) < 60:
            self.particulas_menu.append(self.criar_particula_menu(y_fogo_menu))

        for p in self.particulas_menu[:]:
            p['x'] += p['dx']
            p['y'] += p['dy']
            p['vida'] -= 1
            if p['vida'] <= 0:
                self.particulas_menu.remove(p)



    