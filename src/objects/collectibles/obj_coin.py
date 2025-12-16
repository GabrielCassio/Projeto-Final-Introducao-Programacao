import pygame, math

class Coin(pygame.sprite.Sprite):
    '''
        Collectible Coin class.
    '''
    def __init__(self, x, y):
        # Calling the super class pygame.sprite.Sprite an its properties
        super().__init__()
        
        # --- Configuração do Sprite ---
        # Criamos uma área transparente (40x40) onde o desenho vai acontecer
        self.image_size = 40 
        self.image = pygame.Surface((self.image_size, self.image_size), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(x, y))

        # --- Lógica Física/Posição Global ---
        self.pos = pygame.Vector2(x, y)
        self.tamanho_base = 9
        self.ativa = True

        # --- Variáveis de Animação ---
        self.angulo = 0
        self.tempo = 0

        # --- Variáveis de Magnetismo ---
        self.distancia_pull = 90
        self.forca_pull = 0.6

    def update(self, jogador=None):
        if not self.ativa:
            # Se não estiver ativa, removemos do grupo de renderização (opcional) ou apenas paramos
            return

        # 1. Atualizar contadores de animação
        self.angulo += 1.2
        self.tempo += 0.04

        # 2. Física de Magnetismo (Puxar para o jogador)
        if jogador:
            centro_jogador = pygame.Vector2(jogador.rect.center)
            distancia = self.pos.distance_to(centro_jogador)

            if distancia < self.distancia_pull:
                direcao = centro_jogador - self.pos
                if direcao.length() != 0:
                    self.pos += direcao.normalize() * self.forca_pull

        # 3. Sincronizar a posição do Rect com a posição física
        self.rect.center = round(self.pos.x), round(self.pos.y)

        # 4. Redesenhar a moeda (Atualizar a self.image)
        self.atualizar_imagem_desenhada()

    def atualizar_imagem_desenhada(self):
        """
        Recria o desenho vetorial 3D frame a frame DENTRO da imagem do sprite.
        """
        # Limpa a imagem anterior (preenche com transparente)
        self.image.fill((0, 0, 0, 0))

        # Define o centro local (dentro do quadrado 40x40)
        cx = self.image_size // 2
        cy = self.image_size // 2

        # Matemática da animação
        ondulacao = math.sin(self.tempo) * 1.5
        tamanho = self.tamanho_base + int(ondulacao)
        ang = math.radians(self.angulo)

        # Função auxiliar para calcular pontos relativos ao centro da IMAGEM
        def ponto(dx, dy):
            rx = dx * math.cos(ang) - dy * math.sin(ang)
            ry = dx * math.sin(ang) + dy * math.cos(ang)
            return (cx + int(rx), cy + int(ry))

        # --- Desenho dos Polígonos ---

        # 1. Corpo principal (Losango)
        losango = [
            ponto(0, -tamanho),
            ponto(tamanho, 0),
            ponto(0, tamanho),
            ponto(-tamanho, 0)
        ]
        pygame.draw.polygon(self.image, (80, 220, 140), losango)

        # 2. Sombra (Lateral)
        sombra = [
            ponto(0, 0),
            ponto(tamanho, 0),
            ponto(0, tamanho)
        ]
        pygame.draw.polygon(self.image, (40, 160, 100), sombra)

        # 3. Reflexo (Brilho)
        reflexo = [
            ponto(0, -tamanho),
            ponto(tamanho * 0.5, -tamanho * 0.3),
            ponto(0, 0)
        ]
        pygame.draw.polygon(self.image, (160, 255, 200), reflexo)

        # 4. Linha central
        pygame.draw.line(self.image, (200, 255, 220), ponto(0, -tamanho), ponto(0, tamanho), 1)