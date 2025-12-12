import pygame
# Importamos o projétil da mesma pasta (o ponto . significa diretório atual)
from .obj_projectile import Projectile

class PlayerAction:
    def __init__(self, player_entity):
        """
        Gerencia as ações de combate do jogador.
        :param player_entity: Referência ao objeto Player principal (para pegar posição X, Y e direção).
        """
        self.player = player_entity

        # --- CONFIGURAÇÃO: Ataque a Distância (Arco) ---
        self.bow_skill = True
        self.last_shot_time = 0
        self.shot_cooldown = 400  # 400ms (0.4 segundos) entre flechas

        # --- CONFIGURAÇÃO: Ataque Melee (Soco/Espada) ---
        self.melee_skill = True
        self.last_melee_time = 0
        self.melee_cooldown = 800 # 800ms (0.8 segundos) entre ataques físicos
        self.melee_range = 50     # Alcance do soco em pixels

    def handle_input(self):
        """
        Deve ser chamado a cada frame no Update do Player.
        Verifica teclas e retorna o objeto gerado (flecha) ou sinal de ataque.
        """
        keys = pygame.key.get_pressed()
        now = pygame.time.get_ticks()
        
        result = None
      
        if keys[pygame.K_r] and self.bow_skill:
            if now - self.last_shot_time > self.shot_cooldown:
                self.last_shot_time = now
                result = self._create_projectile()

        elif keys[pygame.K_f] and self.melee_skill:
            if now - self.last_melee_time > self.melee_cooldown:
                self.last_melee_time = now
                print("Ataque Melee realizado!") 
                result = "melee_triggered"

        return result

    def _create_projectile(self):
        direction = getattr(self.player, 'sprite_direction', 'right')

        return Projectile(
            x=self.player.rect.centerx,
            y=self.player.rect.centery,
            direction=direction
        )
