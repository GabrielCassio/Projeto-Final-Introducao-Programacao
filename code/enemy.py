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
# Stats / Balance (POR TIPO)
# ==========================================
ENEMY_STATS = {
    "skeleton": {
        "max_health": 100,
        "speed": 85,
        "attack_damage": 18,
        "attack_radius": 40,
        "notice_radius": 300,
        "attack_cooldown": 1100,
        "invincibility_duration": 250,
    },
    "ghost": {
        "max_health": 60,
        "speed": 105,
        "attack_damage": 15,
        "attack_radius": 200,  
        "notice_radius": 300,
        "attack_cooldown": 3000,
        "invincibility_duration": 220,
    },
    "vampire": {
        "max_health": 120,
        "speed": 95,            # era 110: vira bruiser, não míssil
        "attack_damage": 20,
        "attack_radius": 65,
        "notice_radius": 300,
        "attack_cooldown": 1300,
        "invincibility_duration": 280,
    },
    "default": {
        "max_health": 80,
        "speed": 80,
        "attack_damage": 15,
        "attack_radius": 50,
        "notice_radius": 250,
        "attack_cooldown": 1200,
        "invincibility_duration": 250,
    }
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
        self.hitbox = self.rect.inflate(0, 0)

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
        self.image.fill((255, 0, 0, 80))  # Transparente para debug

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
        self.cell_size = 64  # Tamanho da "célula" de navegação

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
            return pygame.math.Vector2(
                next_grid_pos[0] * self.cell_size + self.cell_size / 2,
                next_grid_pos[1] * self.cell_size + self.cell_size / 2
            )
        return None

    def heuristic(self, a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

# ==========================================
# Classe Enemy (Principal)
# ==========================================
class Enemy(Entity):
    def __init__(self, monster_name, pos, groups, obstacle_sprites, damage_player_callback, trigger_death_callback):
        super().__init__(groups)

        self.sprite_type = 'enemy'
        self.monster_name = monster_name
        self.obstacle_sprites = obstacle_sprites
        self.damage_player_callback = damage_player_callback
        self.trigger_death_callback = trigger_death_callback

        self.has_attacked = False

        # Carrega gráficos
        self.import_graphics(monster_name)

        self.status = 'idle'
        self.frame_index = 0

        # --- SEGURANÇA EXTRA: Se falhou tudo, garante que tem algo na lista ---
        if len(self.animations[self.status]) == 0:
            self.animations[self.status] = [pygame.Surface((32, 32))]
            self.animations[self.status][0].fill('magenta')

        self.image = self.animations[self.status][self.frame_index]
        self.rect = self.image.get_rect(topleft=pos)
        self.hitbox = self.rect.inflate(0, -10)

        # Stats (via dicionário)
        stats = ENEMY_STATS.get(monster_name, ENEMY_STATS["default"])

        self.max_health = stats["max_health"]
        self.health = self.max_health

        self.speed = stats["speed"]
        self.attack_damage = stats["attack_damage"]
        self.attack_radius = stats["attack_radius"]
        self.notice_radius = stats["notice_radius"]

        # Combate (por inimigo)
        self.can_attack = True
        self.attack_time = 0
        self.attack_cooldown = stats["attack_cooldown"]

        self.vulnerable = True
        self.hit_time = 0
        self.invincibility_duration = stats["invincibility_duration"]

        # Inteligência (Pathfinding)
        self.pathfinder = Pathfinder(None, obstacle_sprites)
        self.path_timer = pygame.time.get_ticks() + random.randint(0, 1000)
        self.current_path_target = None

    def import_graphics(self, name):
        self.animations = {'idle': [], 'move': [], 'attack': [], 'hited': [], 'death': []}
        config = ENEMY_SHEET_DICT.get(name)
        if not config:
            return

        # Ajuste de escala
        scale_val = 1
        if name == 'skeleton':
            scale_val = 1.5
        if name == 'ghost':
            scale_val = 0.25
        if name == 'vampire':
            scale_val = 1.5

        path = f'./assets/graphics/enemy/{name}/'

        for anim in self.animations.keys():
            # --- PULO DO GATO: Se for Ghost e Idle, pula o carregamento do arquivo ---
            if name == 'ghost' and anim == 'idle':
                continue
            # ------------------------------------------------------------------------

            full_path = path + f'{name}_{anim}.png'
            try:
                img = pygame.image.load(full_path).convert_alpha()
                frames = slice_strip_simple(img, config[anim]['cols'], config[anim]['rows'], scale_val)
                self.animations[anim] = frames
            except Exception as e:
                # Se der erro nos outros, cria o quadrado vermelho de segurança
                # Mas pro Ghost Idle não vai cair aqui pq demos 'continue' acima
                print(f"Erro ao carregar {anim} de {name}")
                surf = pygame.Surface((32, 32))
                surf.fill('red')
                self.animations[anim] = [surf]

        # --- CORREÇÃO DO GHOST (GAMBIARRA OFICIAL) ---
        if name == 'ghost':
            # Verifica se a animação de andar carregou corretamente
            if len(self.animations['move']) > 0:
                # Pega o primeiro frame do movimento e define como a lista de idle
                first_frame = self.animations['move'][0]
                self.animations['idle'] = [first_frame]
            else:
                print("ERRO CRÍTICO: Ghost não tem nem animação de andar para copiar!")
        # ---------------------------------------------

    def get_player_distance_direction(self, player):
        enemy_vec = pygame.math.Vector2(self.rect.center)
        player_vec = pygame.math.Vector2(player.rect.center)
        distance = (player_vec - enemy_vec).magnitude()
        if distance > 0:
            direction = (player_vec - enemy_vec).normalize()
        else:
            direction = pygame.math.Vector2()
        return (distance, direction)

    def get_status(self, player):
        distance, direction = self.get_player_distance_direction(player)

        # 1. Se estiver dentro da área de ataque
        if distance <= self.attack_radius:
            if self.can_attack:
                # Se a arma tá carregada -> ATACA
                if self.status != 'attack':
                    self.frame_index = 0
                self.status = 'attack'
            else:
                # --- A MUDANÇA MÁGICA ---
                # Se a arma tá recarregando (Cooldown), NÃO ANDA. Fica parado olhando.
                self.status = 'idle'
                # ------------------------

        # 2. Se estiver fora do ataque, mas viu o player -> PERSEGUE
        elif distance <= self.notice_radius:
            self.status = 'move'

        # 3. Se player tá muito longe -> DORME
        else:
            self.status = 'idle'

    def actions(self, player):
        # 1. Trava de Knockback
        if not self.vulnerable:
            return

        # 2. Lógica de Ataque (igual antes)
        if self.status == 'attack':
            self.attack_time = pygame.time.get_ticks()
            current_frame = int(self.frame_index)

            if self.monster_name == 'vampire':
                if current_frame >= 3 and not self.has_attacked:
                    self.damage_player_callback(self, 'melee', self.rect.center, None, self.attack_damage)
                    self.has_attacked = True

            elif self.monster_name == 'ghost':
                if current_frame >= 4 and not self.has_attacked:
                    _, direction = self.get_player_distance_direction(player)
                    self.damage_player_callback(self, 'projectile', self.rect.center, direction, self.attack_damage)
                    self.has_attacked = True

            elif self.monster_name == 'skeleton':
                if current_frame >= 4 and not self.has_attacked:
                    self.damage_player_callback(self, 'melee', self.rect.center, None, self.attack_damage)
                    self.has_attacked = True

        # 3. Lógica de Movimento (AQUI ESTÁ A CORREÇÃO DE SEGURANÇA)
        elif self.status == 'move':
            current_time = pygame.time.get_ticks()

            # Recalcula caminho a cada 1 segundo (para não pesar o processador)
            if current_time - self.path_timer > 1000:
                self.path_timer = current_time
                dist, _ = self.get_player_distance_direction(player)

                # Se estiver muito perto, não precisa de pathfinding complexo
                if dist < 100:
                    self.current_path_target = None
                else:
                    # Tenta achar caminho inteligente
                    try:
                        target_pos = self.pathfinder.get_path(self.rect.center, player.rect.center)
                        if target_pos:
                            self.current_path_target = target_pos
                        else:
                            self.current_path_target = None
                    except:
                        self.current_path_target = None

            # --- EXECUÇÃO DO MOVIMENTO ---
            if self.current_path_target:
                # Se tem um alvo do A*, vai até ele
                vec = self.current_path_target - pygame.math.Vector2(self.rect.center)
                if vec.magnitude() > 0:
                    self.direction = vec.normalize()
                else:
                    self.direction = pygame.math.Vector2()
                    self.current_path_target = None
            else:
                # --- PLANO B (FALLBACK) ---
                # Se não tem caminho calculado (ou falhou), vai em linha reta pro player
                # Isso garante que ele NUNCA fique parado se estiver no status 'move'
                _, self.direction = self.get_player_distance_direction(player)

    def animate(self, dt):
        current_animation = self.animations[self.status]

        # Avança os frames
        self.frame_index += 8 * dt  # 8 é a velocidade da animação

        # Se a animação acabou (chegou no último frame)
        if self.frame_index >= len(current_animation):

            # Se estava atacando, agora para
            if self.status == 'attack':
                self.can_attack = False
                self.has_attacked = False  # <--- O FIX ESTÁ AQUI! Reseta a memória
                self.status = 'idle'

            # Reseta o frame para 0 (loop)
            self.frame_index = 0

        # Aplica a imagem correta
        # Proteção para não quebrar se o frame_index passar do limite por um instante
        frame = int(self.frame_index)
        if frame >= len(current_animation):
            frame = 0

        self.image = current_animation[frame]
        self.rect = self.image.get_rect(center=self.hitbox.center)

        # Espelha a imagem se estiver andando para a esquerda
        # Mas só espelha se tiver velocidade, senão fica piscando
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
            # Dano base
            self.health -= 20
            self.vulnerable = False
            self.hit_time = pygame.time.get_ticks()

            # --- NOVO: LÓGICA DE KNOCKBACK ---
            # 1. Pega os centros
            enemy_vec = pygame.math.Vector2(self.rect.center)
            player_vec = pygame.math.Vector2(player.rect.center)

            # 2. Subtrai (Inimigo - Player) para achar a direção OPOSTA
            knockback_direction = (enemy_vec - player_vec)

            # 3. Normaliza (para o vetor ter tamanho 1 e não voar infinito)
            if knockback_direction.magnitude() > 0:
                self.direction = knockback_direction.normalize()

            # --- FIM DO KNOCKBACK ---

            if self.health <= 0:
                self.trigger_death_callback(self.rect.center, self.monster_name)
                self.kill()

    def update(self, dt):
        self.move(self.speed, dt)
        self.animate(dt)
        self.cooldowns()
