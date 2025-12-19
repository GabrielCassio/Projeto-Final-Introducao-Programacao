import pygame 
import math 
import random
from settings import *
from support import import_csv_layout
from player import Player
from enemy import Enemy, EnemyProjectile, EnemyMeleeHitbox
from weapon import Weapon 
from cracha import Cracha
from ui import UI
from particle import Particle
from tile import Wall, Collectible

class Level:
    def __init__(self, surface):
        self.display_surface = surface 
        self.visible_sprites = YSortCameraGroup(self.display_surface) 
        self.obstacle_sprites = pygame.sprite.Group()

        self.attack_sprites = pygame.sprite.Group()
        self.attackable_sprites = pygame.sprite.Group() 
        self.enemy_attack_sprites = pygame.sprite.Group()

        self.item_sprites = pygame.sprite.Group()
        self.particle_sprites = pygame.sprite.Group()

        self.current_attack = None
        self.ui = UI()
        
        self.debug = False 
        
        self.setup_map()

    def create_attack(self):
        self.current_attack = Weapon(self.player, [self.visible_sprites, self.attack_sprites])

    def destroy_attack(self):
        if self.current_attack:
            self.current_attack.kill()
            self.current_attack = None
    
    def create_cracha(self, status):
        if 'up' in status: direction = pygame.math.Vector2(0, -1)
        elif 'down' in status: direction = pygame.math.Vector2(0, 1)
        elif 'left' in status: direction = pygame.math.Vector2(-1, 0)
        elif 'right' in status: direction = pygame.math.Vector2(1, 0)
        else: direction = pygame.math.Vector2(0, 1)

        Cracha(
            self.player.rect.center, 
            direction, 
            [self.visible_sprites, self.attack_sprites], 
            self.obstacle_sprites,
        )

    def trigger_enemy_attack(self, owner, type, pos, direction, damage):
        if type == 'projectile':
            EnemyProjectile(
                pos, 
                [self.visible_sprites, self.enemy_attack_sprites], 
                direction, 
                speed=300, 
                damage=damage
            )
        elif type == 'melee':
            EnemyMeleeHitbox(
                owner, 
                [self.enemy_attack_sprites], 
                size=(100,100), 
                offset=(0,0), 
                damage=damage, 
                duration=200
            )
    
    def trigger_death_logic(self, pos, particle_type):
        self.trigger_particles(pos, amount=5, color='grey')
        
        # --- NOVA LÓGICA DE DROP (RNG) ---
        rng = random.randint(0, 100)
        
        # 0 a 15: Nada (15% de chance de não cair nada -> Antes era 50%)
        # 16 a 35: Coração (20% de chance)
        # 36 a 100: DINHEIRO (65% de chance!)
        
        if rng < 15:
            pass # Nada acontece
        elif rng < 35:
            Collectible(pos, [self.visible_sprites, self.item_sprites], 'heart')
        else:
            # Caiu dinheiro! Mas qual tipo?
            coin_rng = random.randint(0, 100)
            
            if coin_rng < 60: # 60% de ser moeda normal (1)
                Collectible(pos, [self.visible_sprites, self.item_sprites], 'coin')
            elif coin_rng < 90: # 30% de ser moeda Vermelha (5)
                Collectible(pos, [self.visible_sprites, self.item_sprites], 'coin_red')
            else: # 10% de ser moeda Verde (10)
                Collectible(pos, [self.visible_sprites, self.item_sprites], 'coin_green')

    def trigger_particles(self, pos, amount=10, color='red'):
        for i in range(amount):
            Particle(pos, [self.visible_sprites, self.particle_sprites], color)

    def player_attack_logic(self):
        if self.attack_sprites:
            for attack_sprite in self.attack_sprites:
                collision_sprites = pygame.sprite.spritecollide(attack_sprite, self.attackable_sprites, False)
                if collision_sprites:
                    for target_sprite in collision_sprites:
                        if hasattr(target_sprite, 'get_damage'):
                            target_sprite.get_damage(self.player, attack_sprite)
                            self.trigger_particles(target_sprite.rect.center, amount=8, color='#bd1919') 
                            self.visible_sprites.add_shake(6, 10) 
                            if isinstance(attack_sprite, Cracha):
                                attack_sprite.kill()

    def enemy_attack_logic(self):
        enemy_hits = pygame.sprite.spritecollide(self.player, self.enemy_attack_sprites, False)
        if enemy_hits:
            for attack in enemy_hits:
                self.damage_player(attack.damage, 'magic')
                if isinstance(attack, EnemyProjectile):
                    attack.kill()

        for enemy in self.attackable_sprites:
            enemy_hitbox = enemy.hitbox.inflate(-10, -10)
            if enemy_hitbox.colliderect(self.player.hitbox):
                 self.damage_player(10, 'touch')

    def damage_player(self, amount, attack_type):
        if self.player.vulnerable:
            self.player.health -= amount
            self.player.vulnerable = False
            self.player.hurt_time = pygame.time.get_ticks()
            self.trigger_particles(self.player.rect.center, amount=10, color='white')
            self.visible_sprites.add_shake(10, 15)
            print(f"Dano recebido: {amount}. Vida restante: {self.player.health}")
            if self.player.health <= 0:
                print("GAME OVER")

    def item_collection_logic(self):
        collected_items = pygame.sprite.spritecollide(self.player, self.item_sprites, True)
        for item in collected_items:
            if item.item_type == 'cracha':
                self.player.has_cracha = True
                print("ITEM COLETADO!")
            
            elif item.item_type == 'heart':
                self.player.heal(20)
                self.trigger_particles(self.player.rect.center, 5, 'red')
                
            # --- LÓGICA DOS VALORES ---
            elif item.item_type == 'coin':
                self.player.coins += 1
                self.trigger_particles(self.player.rect.center, 5, 'gold')
            elif item.item_type == 'coin_red':
                self.player.coins += 5
                self.trigger_particles(self.player.rect.center, 8, '#ff4444')
            elif item.item_type == 'coin_green':
                self.player.coins += 10
                self.trigger_particles(self.player.rect.center, 12, '#44ff44')

    def input_debug(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_m]:
            self.debug = not self.debug
            pygame.time.wait(200)

    # --- NOVO: INPUT DE ZOOM ---
    def input_zoom(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_q]: # Afasta
            self.visible_sprites.change_zoom(-0.02)
        if keys[pygame.K_e]: # Aproxima
            self.visible_sprites.change_zoom(0.02)
    # ---------------------------

    def setup_map(self):
        print("--- CARREGANDO MAPA ---")
        try:
            map_image = pygame.image.load('./assets/maps/map.png').convert_alpha()
            self.visible_sprites.floor_surf = map_image
            self.visible_sprites.floor_rect = map_image.get_rect(topleft=(0,0))
        except FileNotFoundError:
            self.visible_sprites.floor_surf = pygame.Surface((1000, 1000))
            self.visible_sprites.floor_rect = self.visible_sprites.floor_surf.get_rect()

        layouts = {
            'boundary': import_csv_layout('./assets/maps/map_boundary.csv'),
            'entities': import_csv_layout('./assets/maps/map_entities.csv')
        }

        map_rect = self.visible_sprites.floor_rect 

        player_created = False
        player_pos = (200, 200)
        
        if layouts['entities']:
            for row_index, row in enumerate(layouts['entities']):
                for col_index, val in enumerate(row):
                    if val != '-1': 
                        x = col_index * TILESIZE
                        y = row_index * TILESIZE
                        
                        final_x = x + SHIFT_X
                        final_y = y + SHIFT_Y

                        

                        if val == '97':
                            self.player = Player(
                                (final_x + 50, final_y + 100), 
                                [self.visible_sprites], 
                                self.obstacle_sprites,
                                self.create_attack, 
                                self.destroy_attack, 
                                self.create_cracha
                            )
                            print('spawnei no lugar certo')
                            player_pos = (final_x, final_y)
                            player_created = True
                        
                        elif val == '86':
                             monster_choice = random.choice(ENEMIES)
                             Enemy(
                                monster_choice, 
                                (final_x + SHIFT_X_ENEMIES, final_y + SHIFT_Y_ENEMIES), 
                                [self.visible_sprites, self.attackable_sprites], 
                                self.obstacle_sprites,
                                self.trigger_enemy_attack,
                                self.trigger_death_logic 
                            )
        
        if not player_created:
            self.player = Player(
                player_pos, 
                [self.visible_sprites], 
                self.obstacle_sprites,
                self.create_attack,
                self.destroy_attack,
                self.create_cracha
            )

        if layouts['boundary']: 
            for row_index, row in enumerate(layouts['boundary']):
                for col_index, val in enumerate(row):
                    if val != '-1': 
                        x = col_index * TILESIZE
                        y = row_index * TILESIZE
                        Wall((x + SHIFT_X, y + SHIFT_Y), [self.obstacle_sprites])

        item_x = player_pos[0]
        item_y = player_pos[1] + 100 
        Collectible((item_x, item_y), [self.visible_sprites, self.item_sprites], 'cracha')

    def run(self, dt):
        self.input_debug()
        self.input_zoom() # Chamando a função de zoom

        if hasattr(self, 'player'):
            self.visible_sprites.custom_draw(self.player, self.debug, self.obstacle_sprites)
            self.visible_sprites.update(dt) 
            self.particle_sprites.update(dt)

            self.enemy_attack_sprites.update(dt)

            self.player_attack_logic()
            self.enemy_attack_logic()
            self.item_collection_logic() 
            
            if self.attackable_sprites:
                for enemy in self.attackable_sprites:
                    if hasattr(enemy, 'get_status'):
                        enemy.get_status(self.player)
                        enemy.actions(self.player)
            
            self.ui.display(self.player)
            
            if self.debug:
                debug_surf = pygame.font.Font(None, 20).render(f"FPS: {int(pygame.time.Clock().get_fps())} | ZOOM: {self.visible_sprites.zoom_scale:.2f}", True, 'white')
                self.display_surface.blit(debug_surf, (10, 50))


# ==========================================
# Classes Auxiliares
# ==========================================


class YSortCameraGroup(pygame.sprite.Group):
    def __init__(self, surface):
        super().__init__()
        self.display_surface = surface
        self.zoom_scale = 2.5
        
        self.screen_width = self.display_surface.get_size()[0]
        self.screen_height = self.display_surface.get_size()[1]

        self.internal_width = int(self.screen_width / self.zoom_scale)
        self.internal_height = int(self.screen_height / self.zoom_scale)
        
        self.internal_surf = pygame.Surface((self.internal_width, self.internal_height), pygame.SRCALPHA)
        self.internal_rect = self.internal_surf.get_rect(center = (self.screen_width // 2, self.screen_height // 2))
        
        self.offset = pygame.math.Vector2()
        self.half_w = self.internal_width // 2
        self.half_h = self.internal_height // 2
        
        self.floor_surf = None
        self.floor_rect = None

        self.shake_duration = 0
        self.shake_intensity = 0

    def add_shake(self, intensity, duration):
        self.shake_intensity = intensity
        self.shake_duration = duration

    # --- NOVO: Função para alterar o Zoom ---
    def change_zoom(self, amount):
        self.zoom_scale += amount
        # Limites do Zoom (0.5x até 3.5x)
        if self.zoom_scale < 0.5: self.zoom_scale = 0.5
        if self.zoom_scale > 3.5: self.zoom_scale = 3.5

        # Recalcula a geometria da câmera
        self.internal_width = int(self.screen_width / self.zoom_scale)
        self.internal_height = int(self.screen_height / self.zoom_scale)
        
        self.internal_surf = pygame.Surface((self.internal_width, self.internal_height), pygame.SRCALPHA)
        self.internal_rect = self.internal_surf.get_rect(center = (self.screen_width // 2, self.screen_height // 2))
        
        self.half_w = self.internal_width // 2
        self.half_h = self.internal_height // 2
    # ----------------------------------------

    def custom_draw(self, player, debug_mode=False, obstacle_sprites=None):
        target_offset_x = player.rect.centerx - self.half_w
        target_offset_y = player.rect.centery - self.half_h

        shake_offset_x = 0
        shake_offset_y = 0
        if self.shake_duration > 0:
            shake_offset_x = random.randint(-self.shake_intensity, self.shake_intensity)
            shake_offset_y = random.randint(-self.shake_intensity, self.shake_intensity)
            self.shake_duration -= 1
        
        self.offset.x = target_offset_x + shake_offset_x
        self.offset.y = target_offset_y + shake_offset_y

        self.internal_surf.fill('black') 

        if self.floor_surf:
            floor_offset_pos = self.floor_rect.topleft - self.offset
            self.internal_surf.blit(self.floor_surf, floor_offset_pos)
        
        for sprite in sorted(self.sprites(), key=lambda sprite: sprite.rect.centery):
            if  self.offset.x - 100 < sprite.rect.right and \
                sprite.rect.left < self.offset.x + self.internal_width + 100 and \
                self.offset.y - 100 < sprite.rect.bottom and \
                sprite.rect.top < self.offset.y + self.internal_height + 100:
                
                offset_pos = sprite.rect.topleft - self.offset
                self.internal_surf.blit(sprite.image, offset_pos)

                if debug_mode:
                    rect_offset = sprite.rect.topleft - self.offset
                    debug_rect = pygame.Rect(rect_offset, sprite.rect.size)
                    pygame.draw.rect(self.internal_surf, 'white', debug_rect, 1)

                    if hasattr(sprite, 'hitbox'):
                        hitbox_offset = sprite.hitbox.topleft - self.offset
                        debug_hitbox = pygame.Rect(hitbox_offset, sprite.hitbox.size)
                        pygame.draw.rect(self.internal_surf, 'red', debug_hitbox, 1)

        if debug_mode and obstacle_sprites:
            for wall in obstacle_sprites:
                if (wall.rect.right > self.offset.x and 
                    wall.rect.left < self.offset.x + self.internal_width and
                    wall.rect.bottom > self.offset.y and 
                    wall.rect.top < self.offset.y + self.internal_height):
                    
                    wall_offset = wall.hitbox.topleft - self.offset
                    wall_rect = pygame.Rect(wall_offset, wall.hitbox.size)
                    pygame.draw.rect(self.internal_surf, 'yellow', wall_rect, 1)

        scaled_surf = pygame.transform.scale(self.internal_surf, (self.screen_width, self.screen_height))
        self.display_surface.blit(scaled_surf, (0,0))