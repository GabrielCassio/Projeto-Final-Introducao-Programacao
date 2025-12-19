import pygame
import math

class Moeda:
    def __init__(self, x, y):
        self.pos = pygame.Vector2(x, y)
        self.tamanho_base = 9
        self.rect = pygame.Rect(
            x - self.tamanho_base,
            y - self.tamanho_base,
            self.tamanho_base * 2,
            self.tamanho_base * 2
        )

        self.ativa = True

        self.angulo = 0
        self.tempo = 0

        self.distancia_pull = 90
        self.forca_pull = 0.6

    def atualizar(self, jogador):
        if not self.ativa:
            return

        self.angulo += 1.2
        self.tempo += 0.04

        centro_jogador = pygame.Vector2(jogador.rect.center)
        distancia = self.pos.distance_to(centro_jogador)

        if distancia < self.distancia_pull:
            direcao = centro_jogador - self.pos
            if direcao.length() != 0:
                self.pos += direcao.normalize() * self.forca_pull

        self.rect.center = self.pos

    def desenhar(self, tela):
        if not self.ativa:
            return

        x = int(self.pos.x)
        y = int(self.pos.y)

        ondulacao = math.sin(self.tempo) * 1.5
        tamanho = self.tamanho_base + int(ondulacao)

        ang = math.radians(self.angulo)

        def ponto(dx, dy):
            rx = dx * math.cos(ang) - dy * math.sin(ang)
            ry = dx * math.sin(ang) + dy * math.cos(ang)
            return (x + int(rx), y + int(ry))

        losango = [
            ponto(0, -tamanho),
            ponto(tamanho, 0),
            ponto(0, tamanho),
            ponto(-tamanho, 0)
        ]

        pygame.draw.polygon(tela, (80, 220, 140), losango)

        sombra = [
            ponto(0, 0),
            ponto(tamanho, 0),
            ponto(0, tamanho)
        ]

        pygame.draw.polygon(tela, (40, 160, 100), sombra)

        reflexo = [
            ponto(0, -tamanho),
            ponto(tamanho * 0.5, -tamanho * 0.3),
            ponto(0, 0)
        ]

        pygame.draw.polygon(tela, (160, 255, 200), reflexo)

        pygame.draw.line(
            tela,
            (200, 255, 220),
            ponto(0, -tamanho),
            ponto(0, tamanho),
            1
        )