import pygame
import math
import random

class Trofeu:
    def __init__(self, x, y):
        self.pos = pygame.Vector2(x, y)
        self.raio = 14
        self.rect = pygame.Rect(x - 14, y - 14, 28, 28)

        self.ativo = True
        self.coletando = False
        self.coletado = False

        self.tempo = 0
        self.fade = 255

        self.ondas = [0, 60, 120]
        self.particulas = []

    def iniciar_coleta(self):
        if self.coletado:
            return

        self.coletado = True
        self.coletando = True

        indice = 0
        while indice < 18:
            angulo = random.uniform(0, math.pi * 2)
            distancia = random.uniform(20, 45)

            pos_inicial = pygame.Vector2(
                self.pos.x + math.cos(angulo) * distancia,
                self.pos.y + math.sin(angulo) * distancia
            )

            self.particulas.append({
                'pos': pos_inicial,
                'vel': pygame.Vector2(
                    math.cos(angulo) * random.uniform(0.6, 1.6),
                    math.sin(angulo) * random.uniform(0.6, 1.6) - 1.2
                ),
                'raio': random.uniform(1.5, 3),
                'vida': random.randint(60, 90)
            })
            indice += 1

    def atualizar(self):
        self.tempo += 1

        indice = 0
        while indice < len(self.ondas):
            self.ondas[indice] += 1
            if self.ondas[indice] > 160:
                self.ondas[indice] = 0
            indice += 1

        indice = 0
        while indice < len(self.particulas):
            p = self.particulas[indice]
            p['pos'] += p['vel']
            p['vel'].y += 0.015
            p['vida'] -= 1

            if p['vida'] <= 0:
                self.particulas.pop(indice)
            else:
                indice += 1

        if self.coletando:
            self.fade -= 5
            if self.fade <= 0 and len(self.particulas) == 0:
                self.ativo = False

    def desenhar(self, tela):
        if not self.ativo:
            return

        alpha_fade = max(0, min(255, self.fade))

        efeito = pygame.Surface((300, 300), pygame.SRCALPHA)
        centro = (150, 150)

        pulso = (math.sin(self.tempo * 0.05) + 1) / 2

        brilho = pygame.Surface((300, 300), pygame.SRCALPHA)
        pygame.draw.circle(
            brilho,
            (255, 215, 120),
            centro,
            int(24 + pulso * 6)
        )
        brilho.set_alpha(int(alpha_fade * 0.25))

        aura = pygame.Surface((300, 300), pygame.SRCALPHA)
        pygame.draw.circle(
            aura,
            (255, 200, 90),
            centro,
            int(55 + pulso * 14)
        )
        aura.set_alpha(int(alpha_fade * 0.15))

        brilho.blit(aura, (0, 0))

        for raio in self.ondas:
            alpha = int((alpha_fade * 0.3) - raio * 0.5)
            if alpha > 0:
                pygame.draw.circle(
                    brilho,
                    (255, 220, 150),
                    centro,
                    int(raio),
                    2
                )
                brilho.set_alpha(alpha)

        tela.blit(
            brilho,
            (self.pos.x - 150, self.pos.y - 150),
            special_flags=pygame.BLEND_RGBA_ADD
        )

        corpo = pygame.Surface((40, 40), pygame.SRCALPHA)
        pygame.draw.circle(corpo, (255, 215, 120, alpha_fade), (20, 20), self.raio)
        pygame.draw.circle(corpo, (255, 240, 190, alpha_fade), (20, 20), self.raio - 4)
        tela.blit(corpo, (self.pos.x - 20, self.pos.y - 20))

        for p in self.particulas:
            alpha = int((p['vida'] / 90) * 120)
            superficie = pygame.Surface((20, 20), pygame.SRCALPHA)

            pygame.draw.circle(
                superficie,
                (255, 215, 120, alpha),
                (10, 10),
                int(p['raio'])
            )

            tela.blit(
                superficie,
                (p['pos'].x - 10, p['pos'].y - 10),
                special_flags=pygame.BLEND_RGBA_ADD
            )

        self.rect.center = self.pos