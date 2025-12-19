import pygame
import random

class Particle(pygame.sprite.Sprite):
    def __init__(self, pos, groups, color='red', size=4):
        super().__init__(groups)
        
        # Cria um quadrado pequeno da cor escolhida
        self.image = pygame.Surface((size, size))
        self.image.fill(color)
        self.rect = self.image.get_rect(center=pos)

        # Física da partícula
        # Velocidade aleatória em X e Y para explodir para todos os lados
        self.direction = pygame.math.Vector2(random.uniform(-1, 1), random.uniform(-1, 1))
        if self.direction.magnitude() != 0:
            self.direction = self.direction.normalize()
            
        self.speed = random.randint(100, 250) # Velocidade variável
        self.pos = pygame.math.Vector2(self.rect.center)

        # Tempo de vida
        self.start_time = pygame.time.get_ticks()
        self.life_duration = random.randint(200, 400) # Dura entre 0.2 e 0.4 segundos
        
        # Efeito de encolher (opcional, mas fica legal)
        self.original_size = size
        self.current_size = size

    def update(self, dt):
        # Movimento
        self.pos += self.direction * self.speed * dt
        self.rect.center = self.pos

        current_time = pygame.time.get_ticks()
        time_passed = current_time - self.start_time

        # Lógica de morte e encolhimento
        if time_passed >= self.life_duration:
            self.kill()
        else:
            # Calcula o tamanho baseado no tempo de vida restante (vai de 100% a 0%)
            ratio = 1 - (time_passed / self.life_duration)
            new_size = int(self.original_size * ratio)
            # Garante que não fique com tamanho 0 ou negativo
            if new_size > 0:
                self.image = pygame.transform.scale(self.image, (new_size, new_size))

class FloatingText(pygame.sprite.Sprite):
    def __init__(self, pos, text, groups, color='white', size=20):
        super().__init__(groups)
        
        # Configuração da Fonte (Pode importar do settings se tiver UI_FONT)
        try:
            self.font = pygame.font.Font(UI_FONT, size)
        except:
            self.font = pygame.font.SysFont('arial', size, bold=True)
            
        # Renderiza o texto
        self.image = self.font.render(str(text), True, color)
        self.rect = self.image.get_rect(center=pos)
        
        # Movimento e Tempo de Vida
        self.pos = pygame.math.Vector2(self.rect.center)
        self.direction = pygame.math.Vector2(0, -1) # Sempre sobe
        self.speed = 30 # Velocidade de subida
        self.alpha = 255 # Transparência (0 a 255)
        self.fade_speed = 4 # Velocidade que desaparece
        
    def update(self, dt):
        # Move para cima
        self.pos += self.direction * self.speed * dt
        self.rect.center = self.pos
        
        # Efeito de Fade Out (Desaparecer)
        self.alpha -= self.fade_speed
        if self.alpha <= 0:
            self.kill()
        else:
            self.image.set_alpha(self.alpha)