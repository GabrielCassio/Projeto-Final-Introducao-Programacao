import pygame

# Importing object functions
from src.objects.attacks.obj_damage_attack import roll_player_damage

class CollisionSystem:
    def __init__(self, player, groups: dict):
        self.player = player
        self.groups = groups
        
        # Getting sprite groups
        self.enemies = groups.get('enemies', pygame.sprite.Group())
        self.obstacles = groups.get('obstacles', pygame.sprite.Group())
        self.p_melee = groups.get('melee', pygame.sprite.Group())
        self.p_projectiles = groups.get('projectiles', pygame.sprite.Group())
        
        # Se tiver projéteis de inimigos, adicione aqui depois
        # self.e_projectiles = groups.get('enemy_projectiles', pygame.sprite.Group())

    def update(self):
        self.player_melee_collision()
        self.player_ranged_collision()
        self.player_ranged_wall_collision()
        # self.enemy_attack_collision() # Implementar futuro dano ao player

    def player_melee_collision(self):
        # Verifying collision attakcs vs enemies
        hits = pygame.sprite.groupcollide(
            self.enemies, 
            self.p_melee, 
            False, 
            False, 
            collided=pygame.sprite.collide_mask
        )

        for enemy, attacks in hits.items():
            for atk in attacks:
                if enemy not in atk.hit_list:
                    dmg, is_crit = roll_player_damage(atk.damage)
                    
                    if hasattr(enemy, 'take_damage'):
                        enemy.take_damage(dmg, source_pos=self.player.rect.center, crit=is_crit)
                    
                    atk.hit_list.append(enemy)

    def player_ranged_collision(self):
        # Verifica colisão Projéteis vs Inimigos
        # False, True = Inimigo fica, Projétil morre
        hits = pygame.sprite.groupcollide(
            self.enemies, 
            self.p_projectiles, 
            False, 
            True, 
            collided=pygame.sprite.collide_mask
        )

        for enemy, projs in hits.items():
            for p in projs:
                # Projéteis geralmente tem dano fixo ou calculado na criação
                dmg = p.damage
                is_crit = getattr(p, 'crit', False)
                
                if hasattr(enemy, 'take_damage'):
                    enemy.take_damage(dmg, source_pos=self.player.rect.center, crit=is_crit)

    def player_ranged_wall_collision(self):
        # Verifica colisão Projéteis vs Paredes
        # True, False = Projétil morre, Parede fica
        pygame.sprite.groupcollide(self.p_projectiles, self.obstacles, True, False)