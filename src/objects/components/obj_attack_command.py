import pygame
# Importing systems
from src.systems.render_sys import RenderSystem
#from src.systems.collision_sys import Collision

# Importing Settings
from src.settings import *

# Importamos o projétil da mesma pasta (o ponto . significa diretório atual)
from .obj_projectile import Projectile

class AttackCommand:
    def __init__(self, player_entity):
        """
        Gerencia as ações de combate do jogador.
        :param player_entity: Referência ao objeto Player principal (para pegar posição X, Y e direção).
        """
        # Player Instance
        self.player = player_entity
        # Render Instance
        self.instance_render = RenderSystem()
        # Collision instance
        #self.instance_collision = Collision()
    
    def execute_bow_attack(self):
        """
        Deve ser chamado a cada frame no Update do Player.
        Verifica teclas e retorna o objeto gerado (flecha) ou sinal de ataque.
        """
        
        now = pygame.time.get_ticks()
        
        if (now - self.player.last_shot > self.player.shot_cooldown):
            self.last_shot = now
            
            new_projectile = Projectile(self.player.rect.centerx, self.player.rect.centery, self.player.direction)
            
            self.instance_render.add_sprite(new_projectile, LAYER_OBJECTS)
        

            '''all_assets.add(new_projectile)
            projectiles_group.add(new_projectile)'''
        

    def execute_melee_attack(self):
        """
        Deve ser chamado a cada frame no Update do Player.
        Verifica teclas e retorna o objeto gerado (flecha) ou sinal de ataque.
        """
        now = pygame.time.get_ticks()
        
        result = None
        if (now - self.player.last_melee_time > self.player.melee_cooldown):
            self.player.last_melee_time = now
            print("Ataque Melee realizado!") 
            result = "melee_triggered"

        return result