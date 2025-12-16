import pygame
import os
import random

def tela_inicial(tela, LARGURA, ALTURA):
    clock = pygame.time.Clock()

    pasta_atual = os.path.dirname(__file__)
    caminho_assets = os.path.join(pasta_atual, '..', 'assets')

    # fundo animado
    fundos = []
    for i in range(1, 7):
        img = pygame.image.load(
            os.path.join(caminho_assets, f'fundo0{i}.png')
        ).convert()
        img = pygame.transform.scale(img, (LARGURA, ALTURA))
        fundos.append(img)

    # caveira
    caveira = pygame.image.load(
        os.path.join(caminho_assets, 'caveira.png')
    ).convert_alpha()
    caveira = pygame.transform.scale(caveira, (26, 26))

    # fontes pixel
    fonte_titulo = pygame.font.Font(
        os.path.join(caminho_assets, 'PixelifySans-Regular.ttf'), 64
    )
    fonte_menu = pygame.font.Font(
        os.path.join(caminho_assets, 'PixelifySans-Regular.ttf'), 28
    )

    # menu
    opcoes = ['INICIAR JOGO', 'OPÇÕES', 'CRÉDITOS', 'SAIR']
    selecionado = 0

    # partículas título
    particulas_titulo = []

    def criar_particula_titulo():
        return {
            'x': LARGURA // 2 + random.randint(-90, 90),
            'y': 140,
            'vida': random.randint(18, 30),
            'dx': random.choice([-1, 0, 1]),
            'dy': random.randint(-2, -1),
            'cor': random.choice([
                (255, 110, 40),
                (255, 150, 60),
                (220, 80, 30)
            ]),
            'tam': random.choice([2, 3])
        }

    # partículas menu (para qualquer opção selecionada)
    particulas_menu = []

    def criar_particula_menu(y_base):
        return {
            'x': LARGURA // 2 + random.randint(-70, 70),
            'y': y_base + random.randint(-2, 2),
            'vida': random.randint(14, 22),
            'dx': random.choice([-1, 0, 1]),
            'dy': random.uniform(-0.8, -0.4),
            'cor': random.choice([
                (230, 150, 100),
                (210, 130, 90),
                (255, 180, 120)
            ]),
            'tam': random.choice([1, 2])
        }

    frame_fundo = 0
    tempo = 0
    caveira_y_atual = 0

    rodando = True
    while rodando:
        clock.tick(60)
        tempo += 1
        frame_fundo = (frame_fundo + 0.15) % len(fundos)

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                return

            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_UP:
                    selecionado = (selecionado - 1) % len(opcoes)
                if evento.key == pygame.K_DOWN:
                    selecionado = (selecionado + 1) % len(opcoes)
                if evento.key == pygame.K_RETURN:
                    if opcoes[selecionado] == 'SAIR':
                        return

        # fundo
        tela.blit(fundos[int(frame_fundo)], (0, 0))

        # fogo do título
        if len(particulas_titulo) < 90:
            particulas_titulo.append(criar_particula_titulo())

        for p in particulas_titulo[:]:
            p['x'] += p['dx']
            p['y'] += p['dy']
            p['vida'] -= 1
            if p['vida'] <= 0:
                particulas_titulo.remove(p)
                continue
            pygame.draw.rect(
                tela,
                p['cor'],
                pygame.Rect(p['x'], p['y'], p['tam'], p['tam'])
            )

        # título com borda
        for dx, dy in [(-2,0),(2,0),(0,-2),(0,2)]:
            borda = fonte_titulo.render('ÉDISO', True, (180, 90, 20))
            tela.blit(borda, (LARGURA//2 - borda.get_width()//2 + dx, 70 + dy))

        titulo = fonte_titulo.render('ÉDISO', True, (255, 170, 90))
        tela.blit(titulo, (LARGURA//2 - titulo.get_width()//2, 70))

        # subtítulo
        for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
            borda = fonte_menu.render(
                'THE LEGEND OF THE RESCUE', True, (80, 40, 120)
            )
            tela.blit(borda, (LARGURA//2 - borda.get_width()//2 + dx, 135 + dy))

        subtitulo = fonte_menu.render(
            'THE LEGEND OF THE RESCUE', True, (170, 120, 255)
        )
        tela.blit(subtitulo, (LARGURA//2 - subtitulo.get_width()//2, 135))

        # menu
        base_y = 240
        alvo_caveira_y = base_y + selecionado * 42 + 6
        caveira_y_atual += (alvo_caveira_y - caveira_y_atual) * 0.2

        # fogo do item selecionado
        y_fogo_menu = base_y + selecionado * 42 - 4
        if len(particulas_menu) < 60:
            particulas_menu.append(criar_particula_menu(y_fogo_menu))

        for p in particulas_menu[:]:
            p['x'] += p['dx']
            p['y'] += p['dy']
            p['vida'] -= 1
            if p['vida'] <= 0:
                particulas_menu.remove(p)
                continue
            pygame.draw.rect(
                tela,
                p['cor'],
                pygame.Rect(p['x'], p['y'], p['tam'], p['tam'])
            )

        for i, opcao in enumerate(opcoes):
            cor = (200, 160, 255) if i == selecionado else (150, 120, 200)

            for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
                borda = fonte_menu.render(opcao, True, (60, 30, 90))
                tela.blit(
                    borda,
                    (LARGURA//2 - borda.get_width()//2 + dx, base_y + i*42 + dy)
                )

            texto = fonte_menu.render(opcao, True, cor)
            tela.blit(
                texto,
                (LARGURA//2 - texto.get_width()//2, base_y + i*42)
            )

        # caveira
        tela.blit(
            caveira,
            (LARGURA//2 - 118, caveira_y_atual)
        )

        pygame.display.flip()