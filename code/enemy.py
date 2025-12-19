import pygame
import random
import heapq
from settings import *
from entity import Entity
from support import *

# ==========================================
# Configuração dos Spritesheets
# ==========================================
ENEMY_SHEET_DICT = {
    "skeleton": { 
        "idle":   {"cols": 8, "rows": 1},
        "move":   {"cols": 10, "rows": 1},
        "attack": {"cols": 9, "rows": 1},
        "hited":  {"cols": 5, "rows": 1},
        "death":  {"cols": 17, "rows": 1},
    },
    "vampire": {
        "idle":   {"cols": 6, "rows": 1},
        "move":   {"cols": 8, "rows": 1},
        "attack": {"cols": 16, "rows": 1},
        "hited":  {"cols": 5, "rows": 1},
        "death":  {"cols": 14, "rows": 1},
    },
    "ghost": {
        "idle":   {"cols": 8, "rows": 1},
        "move":   {"cols": 13, "rows": 1},
        "attack": {"cols": 8, "rows": 1},
        "hited":  {"cols": 1, "rows": 1},
        "death":  {"cols": 10, "rows": 1},
    },
}

# ==========================================
# Utilitários de Gráfico
# ==========================================
class SpriteSheet:
    def __init__(self, image):
        self.sheet = image

    def get_image(self, frame, width, height, scale, colour):
        image = pygame.Surface((width, height), pygame.SRCALPHA).convert_alpha()
        image.blit(self.sheet, (0, 0), (frame * width, 0, width, height))
        image = pygame.transform.scale(image, (int(width * scale), int(height * scale)))
        return image

def slice_strip_simple(raw, cols, rows, scale):
    sheet = SpriteSheet(raw)
    frame_w = raw.get_width() // cols
    frame_h = raw.get_height() // rows
    frames = []
    for i in range(cols * rows):
        frames.append(sheet.get_image(i, frame_w, frame_h, scale, None))
    return frames

# ==========================================
# Classes de Ataque (Projétil e Hitbox)
# ==========================================
class EnemyProjectile(pygame.sprite.Sprite):
    def __init__(self, pos, groups, direction, speed, damage):
        super().__init__(groups)
        self.image = pygame.Surface((20, 20))
        self.image.fill('orange')
        self.rect = self.image.get_rect(center=pos)
        self.hitbox = self.rect.inflate(0,0)
        
        self.direction = direction
        self.speed = speed
        self.damage = damage
        self.start_time = pygame.time.get_ticks()
        self.life_time = 3000

    def update(self, dt):
        self.hitbox.center += self.direction * self.speed * dt
        self.rect.center = self.hitbox.center
        if pygame.time.get_ticks() - self.start_time > self.life_time:
            self.kill()

class EnemyMeleeHitbox(pygame.sprite.Sprite):
    def __init__(self, owner, groups, size, offset, damage, duration):
        super().__init__(groups)
        self.owner = owner
        self.damage = damage
        self.start_time = pygame.time.get_ticks()
        self.duration = duration
        
        self.image = pygame.Surface(size, pygame.SRCALPHA)
        self.image.fill((255, 0, 0, 80)) # Transparente para debug
        
        self.rect = self.image.get_rect(center=owner.rect.center)
        self.offset = pygame.math.Vector2(offset)
        
    def update(self, dt):
        if not self.owner.alive():
            self.kill()
            return
        self.rect.center = self.owner.rect.center + self.offset
        if pygame.time.get_ticks() - self.start_time >= self.duration:
            self.kill()

# ==========================================
# CÉREBRO: Pathfinding (A*) OTIMIZADO
# ==========================================

class Pathfinder:
    def __init__(self, matrix, obstacle_sprites):
        self.obstacle_sprites = obstacle_sprites
        self.cell_size = 64 # Tamanho da "célula" de navegação

    def get_path(self, start, target):
        # Converte posições de pixels para grid
        start_pos = (int(start[0] // self.cell_size), int(start[1] // self.cell_size))
        end_pos = (int(target[0] // self.cell_size), int(target[1] // self.cell_size))

        if start_pos == end_pos:
            return None

        # A* Algoritmo Simplificado
        open_list = []
        heapq.heappush(open_list, (0, start_pos))
        came_from = {}
        cost_so_far = {}
        came_from[start_pos] = None
        cost_so_far[start_pos] = 0

        # --- OTIMIZAÇÃO: Limite de iterações para não travar ---
        iterations = 0
        max_iterations = 50 

        while open_list:
            iterations += 1
            if iterations > max_iterations:
                break

            _, current = heapq.heappop(open_list)

            if current == end_pos:
                break
            
            # Checa vizinhos (Cima, Baixo, Esquerda, Direita)
            for next_pos in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                neighbor = (current[0] + next_pos[0], current[1] + next_pos[1])
                
                new_cost = cost_so_far[current] + 1
                
                # Verifica se é passável (não tem parede)
                neighbor_pixel_pos = (neighbor[0] * self.cell_size, neighbor[1] * self.cell_size)
                neighbor_rect = pygame.Rect(neighbor_pixel_pos[0], neighbor_pixel_pos[1], self.cell_size, self.cell_size)
                
                collision = False
                for sprite in self.obstacle_sprites:
                    if sprite.hitbox.colliderect(neighbor_rect):
                        collision = True
                        break
                
                if not collision:
                    if neighbor not in cost_so_far or new_cost < cost_so_far[neighbor]:
                        cost_so_far[neighbor] = new_cost
                        priority = new_cost + self.heuristic(end_pos, neighbor)
                        heapq.heappush(open_list, (priority, neighbor))
                        came_from[neighbor] = current
        
        # Reconstrói o caminho
        path = []
        curr = end_pos
        count = 0
        
        if curr not in came_from:
            return None

        while curr != start_pos and count < 100:
            path.append(curr)
            curr = came_from[curr]
            count += 1
        path.reverse()
        
        # Retorna o próximo passo em pixels
        if path:
            next_grid_pos = path[0]
            return pygame.math.Vector2(next_grid_pos[0] * self.cell_size + self.cell_size/2, 
                                       next_grid_pos[1] * self.cell_size + self.cell_size/2)
        return None

    def heuristic(self, a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

# ==========================================
# Classe Enemy (Principal)
# ==========================================
class Enemy(Entity):
    def __init__(self, monster_name, pos, groups, obstacle_sprites, damage_player_callback):
        super().__init__(groups)
        
        self.sprite_type = 'enemy'
        self.monster_name = monster_name
        self.obstacle_sprites = obstacle_sprites
        self.damage_player_callback = damage_player_callback
        
        # Carrega gráficos
        self.import_graphics(monster_name)
        
        self.status = 'idle'
        self.frame_index = 0
        
        # --- SEGURANÇA EXTRA: Se falhou tudo, garante que tem algo na lista ---
        if len(self.animations[self.status]) == 0:
             self.animations[self.status] = [pygame.Surface((32,32))]
             self.animations[self.status][0].fill('magenta')
        
        self.image = self.animations[self.status][self.frame_index]
        self.rect = self.image.get_rect(topleft=pos)
        self.hitbox = self.rect.inflate(0, -10)
        
        # Stats Específicos
        if monster_name == 'skeleton':
            self.health = 100
            self.speed = 80
            self.attack_damage = 20
            self.attack_radius = 34
            self.notice_radius = 30
        elif monster_name == 'ghost':
            self.health = 60
            self.speed = 100
            self.attack_damage = 15
            self.attack_radius = 40
            self.notice_radius = 30
        elif monster_name == 'vampire':
            self.health = 150
            self.speed = 110
            self.attack_damage = 30
            self.attack_radius = 70
            self.notice_radius = 30

        # Combate
        self.can_attack = True
        self.attack_time = 0
        self.attack_cooldown = 1200
        self.vulnerable = True
        self.hit_time = 0
        self.invincibility_duration = 300
        
        # Inteligência (Pathfinding)
        self.pathfinder = Pathfinder(None, obstacle_sprites)
        self.path_timer = pygame.time.get_ticks() + random.randint(0, 1000)
        self.current_path_target = None 

    def import_graphics(self, name):
        self.animations = {'idle': [], 'move': [], 'attack': [], 'hited': [], 'death': []}
        config = ENEMY_SHEET_DICT.get(name)
        if not config: return 

        # --- AJUSTE DE TAMANHO (ESQUELETO PEQUENO) ---
        scale_val = 1
        if name == 'skeleton':
            scale_val = 1
        if name == 'ghost':
            scale_val = 0.25
        # ---------------------------------------------

        path = f'./assets/graphics/enemy/{name}/'
        for anim in self.animations.keys():
            full_path = path + f'{name}_{anim}.png'
            try:
                img = pygame.image.load(full_path).convert_alpha()
                frames = slice_strip_simple(img, config[anim]['cols'], config[anim]['rows'], scale_val)
                self.animations[anim] = frames
            except Exception as e:
                print(f"!!! ERRO AO CARREGAR: {full_path}")
                print(e)
            
            # --- TRAVA DE SEGURANÇA (O FIX IMPORTANTE) ---
            # Verifica se a lista está vazia DEPOIS de tentar carregar
            if len(self.animations[anim]) == 0:
                print(f"--> Criando placeholder vermelho para {name} {anim}")
                surf = pygame.Surface((32, 32))
                surf.fill('red')
                self.animations[anim] = [surf]

    def get_player_distance_direction(self, player):
        enemy_vec = pygame.math.Vector2(self.rect.center)
        player_vec = pygame.math.Vector2(player.rect.center)
        distance = (player_vec - enemy_vec).magnitude()
        if distance > 0: direction = (player_vec - enemy_vec).normalize()
        else: direction = pygame.math.Vector2()
        return (distance, direction)

    def get_status(self, player):
        distance, direction = self.get_player_distance_direction(player)

        if distance <= self.attack_radius and self.can_attack:
            if self.status != 'attack':
                self.frame_index = 0
            self.status = 'attack'
        elif distance <= self.notice_radius:
            self.status = 'move'
        else:
            self.status = 'idle'

    def actions(self, player):
        if self.status == 'attack':
            self.attack_time = pygame.time.get_ticks()
            
            if self.monster_name == 'vampire':
                if int(self.frame_index) == 3:
                      self.damage_player_callback(self, 'melee', self.rect.center, None, self.attack_damage)
            
            elif self.monster_name == 'ghost':
                if int(self.frame_index) == 4: 
                      _, direction = self.get_player_distance_direction(player)
                      self.damage_player_callback(self, 'projectile', self.rect.center, direction, self.attack_damage)
            
            elif self.monster_name == 'skeleton':
                if int(self.frame_index) == 4:
                    self.damage_player_callback(self, 'melee', self.rect.center, None, self.attack_damage)

        elif self.status == 'move':
            current_time = pygame.time.get_ticks()
            
            # --- LÓGICA DE MOVIMENTO INTELIGENTE (OTIMIZADA) ---
            if current_time - self.path_timer > 1000:
                self.path_timer = current_time
                
                dist, _ = self.get_player_distance_direction(player)
                
                if dist < 100:
                    self.current_path_target = None
                else:
                    target_pos = self.pathfinder.get_path(self.rect.center, player.rect.center)
                    if target_pos:
                        self.current_path_target = target_pos
                    else:
                        self.current_path_target = None 
            
            if self.current_path_target:
                vec = self.current_path_target - pygame.math.Vector2(self.rect.center)
                if vec.magnitude() > 0:
                    self.direction = vec.normalize()
                else:
                    self.direction = pygame.math.Vector2()
                    self.current_path_target = None 
            else:
                _, self.direction = self.get_player_distance_direction(player)

    def animate(self, dt):
        current_animation = self.animations[self.status]
        self.frame_index += 8 * dt
        if self.frame_index >= len(current_animation):
            if self.status == 'attack':
                self.can_attack = False
                self.status = 'idle'
            self.frame_index = 0

        self.image = current_animation[int(self.frame_index)]
        self.rect = self.image.get_rect(center=self.hitbox.center)
        if self.direction.x < 0:
            self.image = pygame.transform.flip(self.image, True, False)

    def cooldowns(self):
        current_time = pygame.time.get_ticks()
        if not self.can_attack:
            if current_time - self.attack_time >= self.attack_cooldown:
                self.can_attack = True
        if not self.vulnerable:
            if current_time - self.hit_time >= self.invincibility_duration:
                self.vulnerable = True

    def get_damage(self, player, attack_type):
        if self.vulnerable:
            self.health -= 20
            self.vulnerable = False
            self.hit_time = pygame.time.get_ticks()
            if self.health <= 0:
                self.kill()

    def update(self, dt):
        self.move(self.speed, dt)
        self.animate(dt)
        self.cooldowns()