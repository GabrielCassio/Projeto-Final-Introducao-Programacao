import pygame, math, random

class Trophy(pygame.sprite.Sprite):
    '''
        Collectible trophy class.
    '''
    def __init__(self, x, y):
        # Calling the super class pygame.sprite.Sprite an its properties
        super().__init__()
        

        # A imagem precisa ser GRANDE para caber a aura e partículas (300x300)
        self.image_size = 300
        self.centro_img = self.image_size // 2 # 150
        
        self.image = pygame.Surface((self.image_size, self.image_size), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(x, y))

        # Como o rect é gigante (300px), precisamos de um rect menor só para colisão física
        self.hitbox = pygame.Rect(0, 0, 28, 28)
        self.hitbox.center = self.rect.center

        # --- Estado e Lógica ---
        self.pos = pygame.Vector2(x, y)
        self.raio = 14
        
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

        # Gera partículas (Explosão visual)
        for _ in range(18):
            angulo = random.uniform(0, math.pi * 2)
            distancia = random.uniform(20, 45)

            # Posição relativa ao centro do troféu
            offset_x = math.cos(angulo) * distancia
            offset_y = math.sin(angulo) * distancia
            
            pos_local = pygame.Vector2(offset_x, offset_y)

            self.particulas.append({
                'pos_rel': pos_local, 
                'vel': pygame.Vector2(
                    math.cos(angulo) * random.uniform(0.6, 1.6),
                    math.sin(angulo) * random.uniform(0.6, 1.6) - 1.2
                ),
                'raio': random.uniform(1.5, 3),
                'vida': random.randint(60, 90)
            })

    def update(self):
        # Se o fade acabou, removemos o sprite
        if not self.ativo:
            self.kill()
            return

        self.tempo += 1

        # Atualizar Ondas
        for i in range(len(self.ondas)):
            self.ondas[i] += 1
            if self.ondas[i] > 160:
                self.ondas[i] = 0

        # Atualizar Partículas
        # Iteração inversa para poder remover itens da lista seguramente
        for i in range(len(self.particulas) - 1, -1, -1):
            p = self.particulas[i]
            p['pos_rel'] += p['vel']
            p['vel'].y += 0.015 # Gravidade
            p['vida'] -= 1

            if p['vida'] <= 0:
                self.particulas.pop(i)

        # Lógica de Fade Out
        if self.coletando:
            self.fade -= 5
            if self.fade <= 0 and len(self.particulas) == 0:
                self.ativo = False

        # Atualizar Hitbox para seguir o Rect (caso o troféu se mova)
        self.hitbox.center = self.rect.center

        # Renderizar visual na self.image
        self.desenhar_na_imagem()

    def desenhar_na_imagem(self):

        self.image.fill((0, 0, 0, 0)) # Limpa
        
        alpha_fade = max(0, min(255, self.fade))
        cx, cy = self.centro_img, self.centro_img # (150, 150)

        # --- Efeito de Pulso ---
        pulso = (math.sin(self.tempo * 0.05) + 1) / 2

        # --- Camada de Brilho/Aura ---
        # Nota: Desenhamos direto na self.image com transparência
        
        # Aura Externa
        raio_aura = int(55 + pulso * 14)
        cor_aura = (255, 200, 90, int(alpha_fade * 0.15))
        
        # Pygame draw circle suporta alpha direto se passar 4 valores de cor
        # Mas precisamos de uma surface temporária para alpha perfeito em círculos preenchidos
        surf_aura = pygame.Surface((self.image_size, self.image_size), pygame.SRCALPHA)
        pygame.draw.circle(surf_aura, cor_aura, (cx, cy), raio_aura)
        self.image.blit(surf_aura, (0,0))

        # Brilho Central
        raio_brilho = int(24 + pulso * 6)
        cor_brilho = (255, 215, 120, int(alpha_fade * 0.25))
        
        surf_brilho = pygame.Surface((self.image_size, self.image_size), pygame.SRCALPHA)
        pygame.draw.circle(surf_brilho, cor_brilho, (cx, cy), raio_brilho)
        self.image.blit(surf_brilho, (0,0))

        # --- Ondas (Aneis) ---
        for raio in self.ondas:
            alpha = int((alpha_fade * 0.3) - raio * 0.5)
            if alpha > 0:
                pygame.draw.circle(
                    self.image,
                    (255, 220, 150, alpha), # Cor com alpha
                    (cx, cy),
                    int(raio),
                    2 # espessura
                )

        # --- Corpo do Troféu ---
        pygame.draw.circle(self.image, (255, 215, 120, alpha_fade), (cx, cy), self.raio)
        pygame.draw.circle(self.image, (255, 240, 190, alpha_fade), (cx, cy), self.raio - 4)

        # --- Partículas ---
        for p in self.particulas:
            alpha_p = int((p['vida'] / 90) * 255)
            if alpha_p < 0: alpha_p = 0
            
            # Converte posição relativa para coordenada da imagem
            px = cx + p['pos_rel'].x
            py = cy + p['pos_rel'].y
            
            # Desenha partícula
            surf_particula = pygame.Surface((int(p['raio']*2)+2, int(p['raio']*2)+2), pygame.SRCALPHA)
            pygame.draw.circle(
                surf_particula,
                (255, 215, 120, alpha_p),
                (surf_particula.get_width()//2, surf_particula.get_height()//2),
                int(p['raio'])
            )
            # Blit centralizado na posição da partícula
            self.image.blit(surf_particula, (px - surf_particula.get_width()//2, py - surf_particula.get_height()//2))