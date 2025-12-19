import pygame
import os
import random

def tela_creditos(tela, LARGURA, ALTURA):
    clock = pygame.time.Clock()

    pasta_atual = os.path.dirname(__file__)
    caminho_assets = os.path.join(pasta_atual, '..', 'assets')

    fundos = []
    for i in range(1, 7):
        img = pygame.image.load(os.path.join(caminho_assets, 'telas', f'fundo0{i}.png')).convert()
        img = pygame.transform.scale(img, (LARGURA, ALTURA))
        fundos.append(img)

    print(caminho_assets)
    fonte_titulo = pygame.font.Font(os.path.join(caminho_assets, 'fonts', 'PixelifySans-Regular.ttf'), 52)
    fonte_jogo = pygame.font.Font(os.path.join(caminho_assets, 'fonts', 'PixelifySans-Regular.ttf'), 34)
    fonte_secao = pygame.font.Font(os.path.join(caminho_assets, 'fonts', 'PixelifySans-Regular.ttf'), 26)
    fonte_nome = pygame.font.Font(os.path.join(caminho_assets, 'fonts', 'PixelifySans-Regular.ttf'), 24)
    fonte_texto = pygame.font.Font(os.path.join(caminho_assets, 'fonts', 'PixelifySans-Regular.ttf'), 18)
    fonte_small = pygame.font.Font(os.path.join(caminho_assets, 'fonts', 'PixelifySans-Regular.ttf'), 16)

    logo = pygame.image.load(os.path.join(caminho_assets, 'telas', 'cinpixel.png')).convert_alpha()
    largura_logo = 170
    altura_logo = int(logo.get_height() * (largura_logo / logo.get_width()))
    logo = pygame.transform.scale(logo, (largura_logo, altura_logo))

    overlay = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
    overlay.fill((10, 6, 18, 150))

    particulas = []

    def cria_particula():
        return {
            'x': random.randint(0, LARGURA),
            'y': ALTURA + random.randint(0, 20),
            'dy': random.uniform(-0.95, -0.45),
            'vida': random.randint(80, 160),
            'tam': random.choice([1, 2]),
            'cor': random.choice([(120, 90, 200), (170, 120, 255), (90, 60, 160), (220, 150, 100)])
        }

    def texto_borda(fonte, texto, cor_texto, cor_borda, esp):
        base = fonte.render(texto, True, cor_texto)
        s = pygame.Surface((base.get_width() + esp * 2, base.get_height() + esp * 2), pygame.SRCALPHA)
        for dx, dy in [(-esp,0),(esp,0),(0,-esp),(0,esp),(-esp,-esp),(esp,-esp),(-esp,esp),(esp,esp)]:
            b = fonte.render(texto, True, cor_borda)
            s.blit(b, (dx + esp, dy + esp))
        s.blit(base, (esp, esp))
        return s

    def render_linha(texto, tipo):
        if tipo == 'titulo':
            return texto_borda(fonte_titulo, texto, (255, 200, 150), (90, 35, 15), 2)

        if tipo == 'jogo':
            return texto_borda(fonte_jogo, texto, (255, 170, 90), (120, 55, 20), 2)

        if tipo == 'subjogo':
            return texto_borda(fonte_texto, texto, (170, 120, 255), (55, 25, 85), 1)

        if tipo == 'secao':
            return texto_borda(fonte_secao, texto, (170, 120, 255), (55, 25, 85), 1)

        if tipo == 'nome':
            return texto_borda(fonte_nome, texto, (215, 200, 255), (45, 20, 70), 1)

        if tipo == 'texto':
            return texto_borda(fonte_texto, texto, (205, 185, 255), (35, 18, 55), 1)

        if tipo == 'small':
            return fonte_small.render(texto, True, (200, 200, 200))

        return None

    def altura_linha(tipo):
        if tipo == 'titulo':
            return 74
        if tipo == 'jogo':
            return 48
        if tipo == 'subjogo':
            return 34
        if tipo == 'secao':
            return 52
        if tipo == 'nome':
            return 38
        if tipo == 'texto':
            return 34
        if tipo == 'small':
            return 28
        if tipo == 'esp':
            return 32
        if tipo == 'esp_grande':
            return 60
        return 34

    texto_abertura = [
        'No CIn, a gente aprende que código também é narrativa.',
        'Entre bugs, café e madrugada, nasce ÉDISO: THE LEGEND OF THE RESCUE.',
        'Um projeto com cara de dungeon, alma de pixel e vontade de entregar algo vivo.',
    ]

    linhas = [
        ('CRÉDITOS', 'titulo'),
        ('', 'esp'),

        ('ÉDISO: THE LEGEND OF THE RESCUE', 'jogo'),
        ('Uma aventura desenvolvida por estudantes do CIn | UFPE', 'subjogo'),

        ('', 'esp_grande'),

        (texto_abertura[0], 'texto'),
        (texto_abertura[1], 'texto'),
        (texto_abertura[2], 'texto'),

        ('', 'esp_grande'),

        ('DESENVOLVIMENTO', 'secao'),
        ('Ana Clara de Oliveira Cavalcanti', 'nome'),
        ('Bernardo Belfort Leão', 'nome'),
        ('Edisio Uchoa Cavalcanti Neto', 'nome'),
        ('Francisco Faustino de Souza Neto', 'nome'),
        ('Gabriel Cássio Gomes Cileiro', 'nome'),
        ('Victor Lemos de Freitas', 'nome'),

        ('', 'esp_grande'),

        ('MONITORES RESPONSÁVEIS', 'secao'),
        ('Thiago Alves', 'nome'),
        ('Ian Cerqueira', 'nome'),

        ('', 'esp_grande'),

        ('CIn | Centro de Informática - UFPE', 'secao'),
        ('', 'esp_grande'),
    ]

    frame_fundo = 0
    scroll_y = ALTURA + 90
    velocidade = 0.85

    rodando = True
    while rodando:
        clock.tick(60)
        frame_fundo = (frame_fundo + 0.15) % len(fundos)

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                return 'SAIR'

            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE or evento.key == pygame.K_RETURN:
                    return 'MENU'

                if evento.key == pygame.K_UP:
                    velocidade = 1.1
                if evento.key == pygame.K_DOWN:
                    velocidade = 0.35

            if evento.type == pygame.KEYUP:
                if evento.key == pygame.K_UP or evento.key == pygame.K_DOWN:
                    velocidade = 0.55

        tela.blit(fundos[int(frame_fundo)], (0, 0))
        tela.blit(overlay, (0, 0))

        if len(particulas) < 70:
            particulas.append(cria_particula())

        for p in particulas[:]:
            p['y'] += p['dy']
            p['vida'] -= 1
            if p['vida'] <= 0 or p['y'] < -10:
                particulas.remove(p)
                continue
            pygame.draw.rect(
                tela,
                p['cor'],
                pygame.Rect(int(p['x']), int(p['y']), p['tam'], p['tam'])
            )

        y = scroll_y

        i = 0
        while i < len(linhas):
            texto, tipo = linhas[i]
            h = altura_linha(tipo)

            if texto != '':
                surf = render_linha(texto, tipo)
                if surf is not None:
                    x = LARGURA // 2 - surf.get_width() // 2
                    tela.blit(surf, (x, int(y)))

            y += h
            i += 1

        altura_total = 0
        j = 0
        while j < len(linhas):
            altura_total += altura_linha(linhas[j][1])
            j += 1

        y_logo = scroll_y + altura_total + 20
        tela.blit(logo, (LARGURA // 2 - logo.get_width() // 2, int(y_logo)))

        texto_voltar = render_linha('(ESC ou ENTER para voltar)', 'small')
        y_voltar = y_logo + logo.get_height() + 14
        tela.blit(texto_voltar, (LARGURA // 2 - texto_voltar.get_width() // 2, int(y_voltar)))

        scroll_y -= velocidade

        if y_voltar < -80:
            scroll_y = ALTURA + 90

        pygame.display.flip()