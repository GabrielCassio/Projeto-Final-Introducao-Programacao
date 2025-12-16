import pygame, math

class Badge(pygame.sprite.Sprite):
    '''
        Collectible Badge class.
    '''
    def __init__(self, x, y):
        # Calling the super class pygame.sprite.Sprite an its properties
        super().__init__()

        # Defining the size os thes sprite  
        self.image = pygame.Surface((20, 28), pygame.SRCALPHA)
        
        # O Rect define a posição no mundo. 
        # No código original: x - 10, y - 14. Isso significa que (x,y) é o CENTRO.
        self.rect = self.image.get_rect(center=(x, y))

        # --- Variáveis Lógicas ---
        self.active = True
        self.tempo = 0

    def update(self):
        """
            Chamado automaticamente pelo grupo de sprites ou manualmente na cena.
        """
        if not self.active:
            return

        # Atualiza o tempo da animação
        self.tempo += 0.04

        # Redesenha a imagem com o novo alpha
        self.desenhar_na_imagem()

    def desenhar_na_imagem(self):
        """
        Atualiza a self.image frame a frame para criar o efeito de pulsação.
        """
        # 1. Limpa a imagem anterior (transparente)
        self.image.fill((0, 0, 0, 0))

        # 2. Calcula o alpha (transparência) baseado no tempo
        alpha = int(120 + 80 * math.sin(self.tempo))

        # 3. Desenha os retângulos DENTRO da self.image
        
        # Borda externa
        pygame.draw.rect(
            self.image,
            (220, 220, 220, alpha),
            (0, 0, 20, 28), # Coordenadas locais (0,0 até largura,altura)
            border_radius=4
        )

        # Miolo interno
        pygame.draw.rect(
            self.image,
            (180, 180, 180, alpha),
            (3, 3, 14, 22), # 20-6=14, 28-6=22 (ajuste matemático do original)
            border_radius=3
        )

    # Mantemos este método apenas por compatibilidade caso seu código antigo o chame
    # Mas o ideal é chamar .update()
    def atualizar(self):
        self.update()