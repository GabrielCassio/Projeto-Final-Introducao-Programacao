import pygame
import os
import math
import random
import json

def tela_opcoes(tela, LARGURA, ALTURA):
    clock = pygame.time.Clock()

    pasta_atual = os.path.dirname(__file__)
    caminho_assets = os.path.join(pasta_atual, '..', 'assets')
    caminho_audio = os.path.join(caminho_assets, 'audios')


    caminho_config = os.path.join(caminho_assets, 'audios', 'config.json')

    def carregar_config():
        padrao = {
            "volume_musica": 0.75,
            "volume_efeitos": 0.75,
            "mutado_musica": False,
            "mutado_efeitos": False,
            "esquema_controle": "TECLADO"
        }
        try:
            with open(caminho_config, "r", encoding="utf-8") as f:
                data = json.load(f)
            for k in padrao:
                if k not in data:
                    data[k] = padrao[k]
            return data
        except Exception:
            return padrao

    def salvar_config(volume_musica, volume_efeitos, mutado_musica, mutado_efeitos, esquema_controle):
        data = {
            "volume_musica": float(volume_musica),
            "volume_efeitos": float(volume_efeitos),
            "mutado_musica": bool(mutado_musica),
            "mutado_efeitos": bool(mutado_efeitos),
            "esquema_controle": str(esquema_controle)
        }
        try:
            with open(caminho_config, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    som_troca = None
    som_ok = None
    try:
        som_troca = pygame.mixer.Sound(os.path.join(caminho_audio, 'somtroca.ogg'))
        som_ok = pygame.mixer.Sound(os.path.join(caminho_audio, 'somok.ogg'))
    except Exception:
        pass

    def play_som(s):
        if s is not None:
            s.play()


    fundos = []
    for i in range(1, 7):
        img = pygame.image.load(os.path.join(caminho_assets, 'telas', f'fundo0{i}.png')).convert()
        img = pygame.transform.scale(img, (LARGURA, ALTURA))
        fundos.append(img)

    caveira = pygame.image.load(os.path.join(caminho_assets, 'telas', 'caveira.png')).convert_alpha()
    caveira = pygame.transform.scale(caveira, (26, 26))

    fonte_titulo = pygame.font.Font(os.path.join(caminho_assets, 'fonts', 'PixelifySans-Regular.ttf'), 52)
    fonte_menu = pygame.font.Font(os.path.join(caminho_assets, 'fonts', 'PixelifySans-Regular.ttf'), 26)
    fonte_small = pygame.font.Font(os.path.join(caminho_assets, 'fonts', 'PixelifySans-Regular.ttf'), 16)

    overlay = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
    overlay.fill((8, 4, 18, 165))

    ROXO = (170, 120, 255)
    ROXO_CLARO = (220, 190, 255)
    ROXO_ESCURO = (60, 30, 90)
    ROXO_APAGADO = (120, 90, 160)
    TEXTO = (230, 230, 235)
    SOMBRA = (12, 6, 20)
    LARANJA = (255, 170, 90)
    LARANJA_ESCURO = (90, 35, 15)

    def clamp(v, a, b):
        return max(a, min(b, v))

    def render_outline(fonte, txt, cor, cor_borda, esp=2):
        base = fonte.render(txt, True, cor)
        s = pygame.Surface((base.get_width() + esp*2, base.get_height() + esp*2), pygame.SRCALPHA)
        for dx, dy in [(-esp,0),(esp,0),(0,-esp),(0,esp),(-esp,-esp),(esp,-esp),(-esp,esp),(esp,esp)]:
            b = fonte.render(txt, True, cor_borda)
            s.blit(b, (dx + esp, dy + esp))
        s.blit(base, (esp, esp))
        return s

    def desenhar_painel(x, y, w, h, t):
        pygame.draw.rect(tela, (0, 0, 0, 120), (x+6, y+8, w, h), border_radius=22)
        pygame.draw.rect(tela, (18, 10, 30, 230), (x, y, w, h), border_radius=22)
        pygame.draw.rect(tela, (90, 60, 150, 140), (x, y, w, h), 2, border_radius=22)
        pygame.draw.rect(tela, (40, 22, 65, 120), (x+6, y+6, w-12, h-12), 2, border_radius=18)

        brilho_h = 18
        brilho = pygame.Surface((w-16, brilho_h), pygame.SRCALPHA)
        brilho.fill((255, 255, 255, 0))
        for i in range(brilho_h):
            a = int(65 * (1 - i/(brilho_h-1)))
            pygame.draw.rect(brilho, (210, 180, 255, a), (0, i, w-16, 1))
        tela.blit(brilho, (x+8, y+10))

        random.seed(12345)
        for i in range(28):
            px = x + 18 + (i * 23) % (w - 40)
            py = y + 36 + (i * 37) % (h - 64)
            a = 25 + (i * 3) % 35
            pygame.draw.rect(tela, (180, 140, 255, a), (px, py, 2, 2))

        wave = math.sin(t * 0.02) * 2.0
        pygame.draw.line(tela, (170, 120, 255, 90), (x+18, y+52+wave), (x+18, y+h-26), 1)
        pygame.draw.line(tela, (60, 30, 90, 140), (x+w-18, y+52-wave), (x+w-18, y+h-26), 1)

    def barra_volume(x, y, w, h, valor, ativo, t):
        pygame.draw.rect(tela, (0, 0, 0, 140), (x+3, y+4, w, h), border_radius=10)

        pygame.draw.rect(tela, (35, 16, 55), (x, y, w, h), border_radius=9)
        pygame.draw.rect(tela, (60, 30, 90), (x, y, w, h), 2, border_radius=9)

        for i in range(1, 9):
            tx = x + int(w * i/9)
            pygame.draw.rect(tela, (60, 30, 90), (tx, y+3, 1, h-6))

        preench = int(w * clamp(valor, 0.0, 1.0))
        if preench > 0:
            if ativo:
                pulse = 0.5 + 0.5*math.sin(t * 0.06)
                glow_a = int(60 + 55*pulse)
                glow = pygame.Surface((preench, h), pygame.SRCALPHA)
                glow.fill((200, 160, 255, glow_a))
                tela.blit(glow, (x, y))

            pygame.draw.rect(tela, (200, 160, 255), (x, y, preench, h), border_radius=9)
            pygame.draw.rect(tela, ROXO, (x+2, y+2, max(0, preench-4), h-4), border_radius=7)

        knob_x = x + preench
        knob_x = clamp(knob_x, x+6, x+w-6)
        ky = y + h//2

        pygame.draw.polygon(
            tela, (0, 0, 0, 140),
            [(knob_x, ky-7), (knob_x+7, ky), (knob_x, ky+7), (knob_x-7, ky)]
        )

        corpo = ROXO_CLARO if ativo else (170, 150, 200)
        pygame.draw.polygon(
            tela, corpo,
            [(knob_x, ky-6), (knob_x+6, ky), (knob_x, ky+6), (knob_x-6, ky)]
        )
        pygame.draw.polygon(
            tela, ROXO_ESCURO,
            [(knob_x, ky-6), (knob_x+6, ky), (knob_x, ky+6), (knob_x-6, ky)],
            1
        )
        pygame.draw.circle(tela, (255, 255, 255, 120), (int(knob_x-2), int(ky-2)), 2)

    def botao_mute(cx, cy, muted, ativo, t):
        r = 13
        pygame.draw.circle(tela, (0, 0, 0, 140), (cx+2, cy+3), r)
        pygame.draw.circle(tela, (25, 12, 38), (cx, cy), r)
        pygame.draw.circle(tela, ROXO_ESCURO, (cx, cy), r, 2)

        if ativo:
            pulse = 0.5 + 0.5*math.sin(t * 0.08)
            a = int(70 + 80*pulse)
            ring = pygame.Surface((r*2+6, r*2+6), pygame.SRCALPHA)
            pygame.draw.circle(ring, (200, 160, 255, a), (r+3, r+3), r+1, 2)
            tela.blit(ring, (cx-(r+3), cy-(r+3)))

        if not muted:
            pygame.draw.polygon(
                tela, ROXO_CLARO,
                [(cx-6, cy-3), (cx-2, cy-3), (cx+2, cy-6), (cx+2, cy+6), (cx-2, cy+3), (cx-6, cy+3)]
            )
            pygame.draw.arc(tela, ROXO, (cx-1, cy-7, 12, 14), -0.7, 0.7, 2)
            pygame.draw.arc(tela, (200, 160, 255), (cx+1, cy-9, 14, 18), -0.6, 0.6, 2)
        else:
            pygame.draw.line(tela, (180, 140, 255), (cx-6, cy-6), (cx+6, cy+6), 3)
            pygame.draw.line(tela, (120, 90, 160), (cx+6, cy-6), (cx-6, cy+6), 3)


    cfg = carregar_config()
    volume_musica = float(cfg["volume_musica"])
    volume_efeitos = float(cfg["volume_efeitos"])
    mutado_musica = bool(cfg["mutado_musica"])
    mutado_efeitos = bool(cfg["mutado_efeitos"])
    esquema_controle = str(cfg["esquema_controle"])


    def salvar_agora():
        salvar_config(volume_musica, volume_efeitos, mutado_musica, mutado_efeitos, esquema_controle)

    itens = ['MUSICA', 'EFEITOS', 'CONTROLES', 'VOLTAR']
    selecionado = 0
    caveira_y = 0

    frame = 0
    t = 0
    rodando = True

    wobble = [random.uniform(0, math.tau) for _ in itens]

    while rodando:
        clock.tick(60)
        t += 1
        frame = (frame + 0.15) % len(fundos)

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                salvar_agora()
                return 'SAIR'

            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    salvar_agora()
                    return 'MENU'

                if evento.key == pygame.K_UP:
                    selecionado = (selecionado - 1) % len(itens)
                    play_som(som_troca)

                if evento.key == pygame.K_DOWN:
                    selecionado = (selecionado + 1) % len(itens)
                    play_som(som_troca)

                if evento.key == pygame.K_LEFT:
                    if itens[selecionado] == 'MUSICA':
                        volume_musica = max(0.0, volume_musica - 0.05)
                        mutado_musica = (volume_musica == 0.0)
                        play_som(som_troca)
                        salvar_agora()

                    elif itens[selecionado] == 'EFEITOS':
                        volume_efeitos = max(0.0, volume_efeitos - 0.05)
                        mutado_efeitos = (volume_efeitos == 0.0)
                        play_som(som_troca)
                        salvar_agora()

                    elif itens[selecionado] == 'CONTROLES':
                        esquema_controle = 'CONTROLE' if esquema_controle == 'TECLADO' else 'TECLADO'
                        play_som(som_troca)
                        salvar_agora()

                if evento.key == pygame.K_RIGHT:
                    if itens[selecionado] == 'MUSICA':
                        volume_musica = min(1.0, volume_musica + 0.05)
                        mutado_musica = False
                        play_som(som_troca)
                        salvar_agora()

                    elif itens[selecionado] == 'EFEITOS':
                        volume_efeitos = min(1.0, volume_efeitos + 0.05)
                        mutado_efeitos = False
                        play_som(som_troca)
                        salvar_agora()

                    elif itens[selecionado] == 'CONTROLES':
                        esquema_controle = 'CONTROLE' if esquema_controle == 'TECLADO' else 'TECLADO'
                        play_som(som_troca)
                        salvar_agora()

                if evento.key == pygame.K_RETURN:
                    play_som(som_ok)

                    if itens[selecionado] == 'MUSICA':
                        mutado_musica = not mutado_musica
                        volume_musica = 0.0 if mutado_musica else max(volume_musica, 0.75)
                        salvar_agora()

                    elif itens[selecionado] == 'EFEITOS':
                        mutado_efeitos = not mutado_efeitos
                        volume_efeitos = 0.0 if mutado_efeitos else max(volume_efeitos, 0.75)
                        salvar_agora()

                    elif itens[selecionado] == 'CONTROLES':
                        esquema_controle = 'CONTROLE' if esquema_controle == 'TECLADO' else 'TECLADO'
                        salvar_agora()

                    elif itens[selecionado] == 'VOLTAR':
                        salvar_agora()
                        return 'MENU'

        # desenhar
        tela.blit(fundos[int(frame)], (0, 0))
        tela.blit(overlay, (0, 0))

        # painel
        painel_w = LARGURA - 110
        painel_h = ALTURA - 110
        painel_x = (LARGURA - painel_w)//2
        painel_y = (ALTURA - painel_h)//2 + 6
        desenhar_painel(painel_x, painel_y, painel_w, painel_h, t)

        # título
        tit_borda = render_outline(fonte_titulo, 'OPÇÕES', (255, 170, 90), (90, 35, 15), 2)
        tela.blit(tit_borda, (LARGURA//2 - tit_borda.get_width()//2, painel_y + 14))

        dica_txt = '< > ajusta / alterna   |   ENTER confirma   |   ESC volta'
        dica = fonte_small.render(dica_txt, True, TEXTO)
        faixa = pygame.Surface((dica.get_width()+18, dica.get_height()+10), pygame.SRCALPHA)
        pygame.draw.rect(faixa, (10, 6, 18, 120), (0, 0, faixa.get_width(), faixa.get_height()), border_radius=10)
        pygame.draw.rect(faixa, (60, 30, 90, 120), (0, 0, faixa.get_width(), faixa.get_height()), 1, border_radius=10)
        faixa.blit(dica, (9, 5))
        tela.blit(faixa, (LARGURA//2 - faixa.get_width()//2, painel_y + 78))

        # layout
        base_y = painel_y + 140
        espac = 70

        caveira_y += ((base_y + selecionado * espac + 2) - caveira_y) * 0.20

        # highlight
        hx = painel_x + 28
        hy = base_y + selecionado * espac - 8
        hw = painel_w - 56
        hh = 56

        pygame.draw.rect(tela, (0, 0, 0, 90), (hx+3, hy+4, hw, hh), border_radius=16)

        hl = pygame.Surface((hw, hh), pygame.SRCALPHA)
        pygame.draw.rect(hl, (40, 20, 65, 140), (0, 0, hw, hh), border_radius=16)
        pygame.draw.rect(hl, (200, 160, 255, 70), (2, 2, hw-4, hh-4), 2, border_radius=14)

        scan_x = int((t * 3) % (hw + 60)) - 60
        pygame.draw.rect(hl, (230, 210, 255, 35), (scan_x, 0, 60, hh), border_radius=16)
        tela.blit(hl, (hx, hy))

        for i, item in enumerate(itens):
            y = base_y + i * espac
            ativo = (i == selecionado)
            dy = int(math.sin(t * 0.03 + wobble[i]) * (1 if ativo else 0.5))

            if item == 'MUSICA':
                label = 'MÚSICA'
            elif item == 'EFEITOS':
                label = 'EFEITOS'
            elif item == 'CONTROLES':
                label = 'CONTROLES'
            else:
                label = 'VOLTAR'

            cor_label = ROXO if ativo else ROXO_APAGADO
            lbl = render_outline(fonte_menu, label, cor_label, ROXO_ESCURO, 1)
            tela.blit(lbl, (painel_x + 70, y + dy))

            if item == 'MUSICA':
                x_slider = painel_x + 240
                barra_volume(x_slider, y + 10 + dy, 260, 18, volume_musica, ativo, t)
                botao_mute(x_slider + 290, y + 19 + dy, mutado_musica, ativo, t)

                pct = '0%' if mutado_musica else f'{int(volume_musica*100)}%'
                pct_s = render_outline(fonte_small, pct, TEXTO, SOMBRA, 1)
                tela.blit(pct_s, (x_slider + 322, y + 6 + dy))

                hint = render_outline(fonte_small, '< > ajusta   |   ENTER muta', TEXTO, SOMBRA, 1)
                tela.blit(hint, (x_slider, y + 34 + dy))

            elif item == 'EFEITOS':
                x_slider = painel_x + 240
                barra_volume(x_slider, y + 10 + dy, 260, 18, volume_efeitos, ativo, t)
                botao_mute(x_slider + 290, y + 19 + dy, mutado_efeitos, ativo, t)

                pct = '0%' if mutado_efeitos else f'{int(volume_efeitos*100)}%'
                pct_s = render_outline(fonte_small, pct, TEXTO, SOMBRA, 1)
                tela.blit(pct_s, (x_slider + 322, y + 6 + dy))

                hint = render_outline(fonte_small, '< > ajusta   |   ENTER muta', TEXTO, SOMBRA, 1)
                tela.blit(hint, (x_slider, y + 34 + dy))

            elif item == 'CONTROLES':
                x_val = painel_x + 330
                val = render_outline(
                    fonte_menu,
                    esquema_controle,
                    (ROXO_CLARO if ativo else ROXO_APAGADO),
                    ROXO_ESCURO,
                    1
                )
                tela.blit(val, (x_val, y + dy))

            elif item == 'VOLTAR':
                pass

        tela.blit(caveira, (painel_x + 30, int(caveira_y)))
        pygame.display.flip()