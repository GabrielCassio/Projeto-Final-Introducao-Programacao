import pygame
import os
import random
import math

def tela_inicial(tela, LARGURA, ALTURA):
    clock = pygame.time.Clock()

    pasta_atual = os.path.dirname(__file__)
    caminho_assets = os.path.join(pasta_atual, '..', 'assets', 'telas')
    caminho_audio = os.path.join(caminho_assets, 'audio')

    som_troca = None
    som_ok = None
    try:
        if not pygame.mixer.get_init():
            pygame.mixer.init()
        som_troca = pygame.mixer.Sound(os.path.join(caminho_audio, 'somtroca.ogg'))
        som_ok = pygame.mixer.Sound(os.path.join(caminho_audio, 'somok.ogg'))
    except Exception:
        pass

    def play_som(s):
        if s is not None:
            try:
                s.play()
            except Exception:
                pass

    fundos = []
    for i in range(1, 7):
        img = pygame.image.load(os.path.join(caminho_assets, f'fundo0{i}.png')).convert()
        img = pygame.transform.scale(img, (LARGURA, ALTURA))
        fundos.append(img)


    caveira = pygame.image.load(os.path.join(caminho_assets, 'caveira.png')).convert_alpha()
    caveira = pygame.transform.scale(caveira, (26, 26))
    caveira_w = caveira.get_width()

    print(caminho_assets)
    fonte_titulo = pygame.font.Font(os.path.join(caminho_assets, '..', 'fonts', 'PixelifySans-Regular.ttf'), 52)
    fonte_menu = pygame.font.Font(os.path.join(caminho_assets, '..', 'fonts', 'PixelifySans-Regular.ttf'), 26)

    opcoes = ['INICIAR JOGO', 'OPÇÕES', 'CRÉDITOS', 'SAIR']
    selecionado = 0


    particulas_titulo = []
    particulas_menu = []

    def criar_particula_titulo():
        return {
            'x': LARGURA // 2 + random.randint(-85, 85),
            'y': 118,
            'vida': random.randint(18, 30),
            'dx': random.choice([-1, 0, 1]),
            'dy': random.randint(-2, -1),
            'cor': random.choice([(255, 110, 40), (255, 150, 60), (220, 80, 30)]),
            'tam': random.choice([2, 3])
        }

    def criar_particula_menu(y_base):
        return {
            'x': LARGURA // 2 + random.randint(-70, 70),
            'y': y_base + random.randint(-2, 2),
            'vida': random.randint(14, 22),
            'dx': random.choice([-1, 0, 1]),
            'dy': random.uniform(-0.8, -0.4),
            'cor': random.choice([(230, 150, 100), (210, 130, 90), (255, 180, 120)]),
            'tam': random.choice([1, 2])
        }


    caveira_x = 0.0
    caveira_y = 0.0
    caveira_init = False

    frame_fundo = 0.0
    t = 0

    while True:
        clock.tick(60)
        t += 1
        frame_fundo = (frame_fundo + 0.15) % len(fundos)

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                return 'SAIR'

            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_UP:
                    selecionado = (selecionado - 1) % len(opcoes)
                    play_som(som_troca)

                elif evento.key == pygame.K_DOWN:
                    selecionado = (selecionado + 1) % len(opcoes)
                    play_som(som_troca)

                elif evento.key == pygame.K_RETURN:
                    play_som(som_ok)
                    return opcoes[selecionado]

                elif evento.key == pygame.K_ESCAPE:
                    return 'SAIR'


        tela.blit(fundos[int(frame_fundo)], (0, 0))

        if len(particulas_titulo) < 90:
            particulas_titulo.append(criar_particula_titulo())

        for p in particulas_titulo[:]:
            p['x'] += p['dx']
            p['y'] += p['dy']
            p['vida'] -= 1
            if p['vida'] <= 0:
                particulas_titulo.remove(p)
                continue
            pygame.draw.rect(tela, p['cor'], pygame.Rect(p['x'], p['y'], p['tam'], p['tam']))


        for dx, dy in [(-2,0),(2,0),(0,-2),(0,2)]:
            borda = fonte_titulo.render('ÉDISO', True, (180, 90, 20))
            tela.blit(borda, (LARGURA//2 - borda.get_width()//2 + dx, 70 + dy))

        titulo = fonte_titulo.render('ÉDISO', True, (255, 170, 90))
        tela.blit(titulo, (LARGURA//2 - titulo.get_width()//2, 70))

        for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
            borda = fonte_menu.render('THE LEGEND OF THE RESCUE', True, (80, 40, 120))
            tela.blit(borda, (LARGURA//2 - borda.get_width()//2 + dx, 135 + dy))

        subtitulo = fonte_menu.render('THE LEGEND OF THE RESCUE', True, (170, 120, 255))
        tela.blit(subtitulo, (LARGURA//2 - subtitulo.get_width()//2, 135))

        base_y = 240
        espac = 42

        y_fogo_menu = base_y + selecionado * espac - 4
        if len(particulas_menu) < 60:
            particulas_menu.append(criar_particula_menu(y_fogo_menu))

        for p in particulas_menu[:]:
            p['x'] += p['dx']
            p['y'] += p['dy']
            p['vida'] -= 1
            if p['vida'] <= 0:
                particulas_menu.remove(p)
                continue
            pygame.draw.rect(tela, p['cor'], pygame.Rect(p['x'], p['y'], p['tam'], p['tam']))

        x_sel = 0
        y_sel = 0
        w_sel = 0

        for i, opcao in enumerate(opcoes):
            cor = (200, 160, 255) if i == selecionado else (150, 120, 200)

            for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
                borda = fonte_menu.render(opcao, True, (60, 30, 90))
                x = LARGURA//2 - borda.get_width()//2
                y = base_y + i*espac
                tela.blit(borda, (x + dx, y + dy))

            texto = fonte_menu.render(opcao, True, cor)
            x = LARGURA//2 - texto.get_width()//2
            y = base_y + i*espac
            tela.blit(texto, (x, y))

            if i == selecionado:
                x_sel = x
                y_sel = y
                w_sel = texto.get_width()


        padding = 14  
        alvo_x = x_sel - caveira_w - padding
        alvo_y = y_sel + 6

        bob = math.sin(t * 0.12) * 2.0

        if not caveira_init:
            caveira_x = float(alvo_x)
            caveira_y = float(alvo_y)
            caveira_init = True

        caveira_x += (alvo_x - caveira_x) * 0.26
        caveira_y += (alvo_y - caveira_y) * 0.26

        tela.blit(caveira, (int(caveira_x), int(caveira_y + bob)))

        pygame.display.flip()