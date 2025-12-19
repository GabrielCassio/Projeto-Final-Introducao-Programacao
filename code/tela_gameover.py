import pygame
import os
import random

def tela_game_over(tela, LARGURA, ALTURA):
    clock = pygame.time.Clock()

    pasta_atual = os.path.dirname(__file__)
    caminho_assets = os.path.join(pasta_atual, '..', 'assets')

    fundos = []
    try:
        for i in range(1, 7):
            img = pygame.image.load(os.path.join(caminho_assets, 'telas', f'fundo0{i}.png')).convert()
            img = pygame.transform.scale(img, (LARGURA, ALTURA))
            fundos.append(img)
    except:
        fundos.append(pygame.Surface((LARGURA, ALTURA)))
        fundos[0].fill((0, 0, 0))

    try:
        fonte_titulo = pygame.font.Font(os.path.join(caminho_assets, 'fonts', 'PixelifySans-Regular.ttf'), 90)
        fonte_texto = pygame.font.Font(os.path.join(caminho_assets, 'fonts', 'PixelifySans-Regular.ttf'), 30)
    except:
        fonte_titulo = pygame.font.Font(None, 100)
        fonte_texto = pygame.font.Font(None, 40)

    overlay = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
    overlay.fill((40, 0, 0, 200))

    particulas = []

    def cria_particula():
        return {
            'x': random.randint(0, LARGURA),
            'y': ALTURA + random.randint(0, 20),
            'dy': random.uniform(-1.5, -0.5),
            'vida': random.randint(60, 120),
            'tam': random.choice([2, 3, 4]),
            'cor': random.choice([(200, 50, 50), (255, 100, 0), (100, 100, 100), (80, 0, 0)])
        }

    def texto_borda(fonte, texto, cor_texto, cor_borda, esp=2):
        base = fonte.render(texto, True, cor_texto)
        s = pygame.Surface((base.get_width() + esp * 2, base.get_height() + esp * 2), pygame.SRCALPHA)
        for dx, dy in [(-esp,0),(esp,0),(0,-esp),(0,esp),(-esp,-esp),(esp,-esp),(-esp,esp),(esp,esp)]:
            b = fonte.render(texto, True, cor_borda)
            s.blit(b, (dx + esp, dy + esp))
        s.blit(base, (esp, esp))
        return s

    opcoes = [
        {"texto": "Tentar Novamente", "retorno": "INICIAR JOGO"},
        {"texto": "Voltar ao Menu", "retorno": "MENU"}
    ]
    selecionado = 0

    surf_gameover = texto_borda(fonte_titulo, "GAME OVER", (255, 50, 50), (50, 0, 0), 4)
    rect_gameover = surf_gameover.get_rect(center=(LARGURA // 2, ALTURA // 3))

    frame_fundo = 0
    pygame.event.clear()

    while True:
        clock.tick(60)
        mouse_pos = pygame.mouse.get_pos()
        
        frame_fundo = (frame_fundo + 0.15) % len(fundos)

        tela.blit(fundos[int(frame_fundo)], (0, 0))
        tela.blit(overlay, (0, 0))

        if len(particulas) < 80:
            particulas.append(cria_particula())

        for p in particulas[:]:
            p['y'] += p['dy']
            p['vida'] -= 1
            if p['vida'] <= 0 or p['y'] < -10:
                particulas.remove(p)
                continue
            
            if random.random() < 0.05:
                p['tam'] = max(1, p['tam'] + random.choice([-1, 1]))

            pygame.draw.rect(
                tela,
                p['cor'],
                pygame.Rect(int(p['x']), int(p['y']), p['tam'], p['tam'])
            )

        tela.blit(surf_gameover, rect_gameover)

        for i, opcao in enumerate(opcoes):
            texto_exibir = opcao["texto"]
            cor = (200, 200, 200)
            
            rect_temp = fonte_texto.render(f"> {texto_exibir} <", True, (255,255,255)).get_rect(center=(LARGURA // 2, ALTURA // 2 + 60 + i * 50))

            if rect_temp.collidepoint(mouse_pos):
                selecionado = i

            if i == selecionado:
                cor = (255, 215, 0)
                texto_exibir = f"> {texto_exibir} <"
            
            surf_opcao = texto_borda(fonte_texto, texto_exibir, cor, (0, 0, 0), 2)
            rect_opcao = surf_opcao.get_rect(center=(LARGURA // 2, ALTURA // 2 + 60 + i * 50))
            tela.blit(surf_opcao, rect_opcao)

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                import sys; sys.exit()

            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_UP:
                    selecionado = (selecionado - 1) % len(opcoes)
                elif evento.key == pygame.K_DOWN:
                    selecionado = (selecionado + 1) % len(opcoes)
                elif evento.key == pygame.K_RETURN or evento.key == pygame.K_SPACE:
                    return opcoes[selecionado]["retorno"]
                elif evento.key == pygame.K_ESCAPE:
                    return "MENU"

            if evento.type == pygame.MOUSEBUTTONDOWN:
                if evento.button == 1:
                    rect_atual = fonte_texto.render(f"> {opcoes[selecionado]['texto']} <", True, (255,255,255)).get_rect(center=(LARGURA // 2, ALTURA // 2 + 60 + selecionado * 50))
                    if rect_atual.collidepoint(mouse_pos):
                        return opcoes[selecionado]["retorno"]

        pygame.display.flip()