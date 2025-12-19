import pygame
import random

from settings import *
from support import import_csv_layout
from player import Player

# Inimigos (não mexi)
from enemy import Enemy, EnemyProjectile, EnemyMeleeHitbox

# Boss (slime -> demon)
from boss import DemonSlimeBoss, DemonBoss

from weapon import Weapon
from cracha import Cracha
from ui import UI
from particle import Particle, FloatingText
from tile import Wall, Collectible, FireBarrier


# ==============================
# BOSS SPAWN SETTINGS
# ==============================
# Se o seu map_entities.csv NÃO tem 88/89, o boss nunca vai spawnar.
# Para não depender do CSV, este fallback spawna 1 slime perto do player
# quando não encontrar nenhum marcador.
BOSS_FORCE_SPAWN_IF_NONE = True
BOSS_FORCE_OFFSET = (700, 0)   # (dx, dy) relativo ao player_pos (tile do player)


class MultiGroup:
    """Proxy: add() repassa para vários grupos (útil pro boss colocar projétil em 'proj')."""
    def __init__(self, *groups):
        self._groups = [g for g in groups if g is not None]

    def add(self, *sprites):
        for g in self._groups:
            g.add(*sprites)

    def remove(self, *sprites):
        for g in self._groups:
            g.remove(*sprites)

    def empty(self):
        for g in self._groups:
            g.empty()


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

        # UI do boss (barra de vida etc. - normalmente update() sem dt)
        self.ui_sprites = pygame.sprite.Group()

        # groups_ref pro boss.py (slime virar demon depende disso)
        self.boss_groups = {
            "all": self.visible_sprites,
            "enemies": self.attackable_sprites,
            "ui": self.ui_sprites,
            "proj": MultiGroup(self.visible_sprites, self.enemy_attack_sprites),
            "walls": self.obstacle_sprites,
        }

        self.current_attack = None
        self.ui = UI()

        self.debug = False
        self.setup_map()

    # ---------------- Player attacks ----------------
    def create_attack(self):
        self.current_attack = Weapon(self.player, [self.visible_sprites, self.attack_sprites])

    def destroy_attack(self):
        if self.current_attack:
            self.current_attack.kill()
            self.current_attack = None

    def create_cracha(self, status):
        if 'up' in status:
            direction = pygame.math.Vector2(0, -1)
        elif 'down' in status:
            direction = pygame.math.Vector2(0, 1)
        elif 'left' in status:
            direction = pygame.math.Vector2(-1, 0)
        elif 'right' in status:
            direction = pygame.math.Vector2(1, 0)
        else:
            direction = pygame.math.Vector2(0, 1)

        Cracha(self.player.rect.center, direction,
               [self.visible_sprites, self.attack_sprites],
               self.obstacle_sprites)

    # ---------------- Enemy callback ----------------
    def trigger_enemy_attack(self, owner, type, pos, direction, damage):
        if type == 'projectile':
            EnemyProjectile(
                pos, [self.visible_sprites, self.enemy_attack_sprites],
                direction, speed=300, damage=damage
            )
        elif type == 'melee':
            try:
                EnemyMeleeHitbox(owner, [self.enemy_attack_sprites],
                                 size=(100, 100), offset=(0, 0),
                                 damage=damage, duration=200)
            except TypeError:
                EnemyMeleeHitbox(owner, [self.enemy_attack_sprites],
                                 size=(100, 100), offset=(0, 0),
                                 damage=damage, duration_ms=200)

    # ---------------- Drops/VFX ----------------
    def trigger_death_logic(self, pos, particle_type):
        self.trigger_particles(pos, amount=5, color='grey')
        Collectible((pos[0] - 10, pos[1] - 10), [self.visible_sprites, self.item_sprites], 'soul')

        rng = random.randint(0, 100)
        if rng < 15:
            return
        if rng < 35:
            Collectible(pos, [self.visible_sprites, self.item_sprites], 'heart')
            return

        coin_rng = random.randint(0, 100)
        if coin_rng < 60:
            Collectible(pos, [self.visible_sprites, self.item_sprites], 'coin')
        elif coin_rng < 90:
            Collectible(pos, [self.visible_sprites, self.item_sprites], 'coin_red')
        else:
            Collectible(pos, [self.visible_sprites, self.item_sprites], 'coin_green')

    def trigger_particles(self, pos, amount=10, color='red'):
        for _ in range(amount):
            Particle(pos, [self.visible_sprites, self.particle_sprites], color)

    # ---------------- Boss spawn ----------------
    def _spawn_boss_slime(self, pos_list):
        if not pos_list:
            return
        screen_rect = self.display_surface.get_rect()
        for (bx, by) in pos_list:
            slime = DemonSlimeBoss(bx, by, self.player, self.boss_groups, screen_rect)
            self.visible_sprites.add(slime)
            self.attackable_sprites.add(slime)
    # ---------------- Gameplay logic (mantive seu comportamento) ----------------
    def check_barrier_interaction(self):
        if hasattr(self, 'fire_barrier') and self.fire_barrier.alive():
            if self.player.hitbox.colliderect(self.fire_barrier.hitbox.inflate(10, 10)):
                cost = 30
                if self.player.souls >= cost:
                    self.player.souls -= cost
                    self.fire_barrier.kill()
                    self.trigger_particles(self.fire_barrier.rect.center, 20, 'orange')
                    FloatingText(self.player.rect.center, "Caminho Aberto!", [self.visible_sprites], 'gold', 20)
                    FloatingText(self.player.rect.center, f"-{cost} Almas", [self.visible_sprites], 'cyan', 15)
                else:
                    if not hasattr(self, 'msg_timer'):
                        self.msg_timer = 0
                    if pygame.time.get_ticks() - self.msg_timer > 1000:
                        missing = cost - self.player.souls
                        msg = "Falta 1 Alma!" if missing == 1 else f"Faltam {missing} Almas!"
                        FloatingText(self.player.rect.center, msg, [self.visible_sprites], 'white', 15)
                        self.msg_timer = pygame.time.get_ticks()

    def player_attack_logic(self):
        if self.attack_sprites:
            for attack_sprite in self.attack_sprites:
                collision_sprites = pygame.sprite.spritecollide(attack_sprite, self.attackable_sprites, False)
                for target_sprite in collision_sprites:
                    if hasattr(target_sprite, 'get_damage'):
                        target_sprite.get_damage(self.player, attack_sprite)
                        self.trigger_particles(target_sprite.rect.center, amount=8, color='#bd1919')
                        self.visible_sprites.add_shake(6, 10)
                        if isinstance(attack_sprite, Cracha):
                            attack_sprite.kill()
                    elif hasattr(target_sprite, "take_damage"):
                        amount = 20
                        if hasattr(self.player, "get_full_weapon_damage"):
                            try:
                                amount = int(self.player.get_full_weapon_damage())
                            except Exception:
                                amount = 20
                        try:
                            target_sprite.take_damage(amount, source_pos=self.player.rect.center, crit=False)
                        except TypeError:
                            target_sprite.take_damage(amount)
                        if isinstance(attack_sprite, Cracha):
                            attack_sprite.kill()

    def enemy_attack_logic(self):
        enemy_hits = pygame.sprite.spritecollide(self.player, self.enemy_attack_sprites, False)
        for attack in enemy_hits:
            dmg = getattr(attack, "damage", 0)
            if dmg:
                self.damage_player(dmg, 'magic')
            if isinstance(attack, EnemyProjectile):
                attack.kill()

        for enemy in self.attackable_sprites:
            if enemy.__class__.__name__.startswith("Demon"):
                continue
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
            if self.player.health <= 0:
                print("GAME OVER")

    def item_collection_logic(self):
        collected_items = pygame.sprite.spritecollide(self.player, self.item_sprites, True)
        for item in collected_items:
            if item.item_type == 'cracha':
                self.player.has_cracha = True
                print("ARMA EQUIPADA!")
            elif item.item_type == 'heart':
                self.player.heal(20)
                self.trigger_particles(self.player.rect.center, 5, 'red')
            elif item.item_type == 'soul':
                self.player.souls += 1
                self.trigger_particles(self.player.rect.center, 5, 'cyan')
            elif 'coin' in item.item_type:
                val = 1
                if item.item_type == 'coin_red':
                    val = 5
                elif item.item_type == 'coin_green':
                    val = 10
                self.player.coins += val
                self.trigger_particles(self.player.rect.center, 5, 'gold')

    def input_debug(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_m]:
            self.debug = not self.debug
            pygame.time.wait(200)

    def input_zoom(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_q]:
            self.visible_sprites.change_zoom(-0.02)
        if keys[pygame.K_e]:
            self.visible_sprites.change_zoom(0.02)

    # update seguro (sprites com update(dt) e update())
    def _smart_update_group(self, group, dt):
        for spr in group.sprites():
            try:
                spr.update(dt)
            except TypeError:
                spr.update()

    def setup_map(self):
        print("--- CARREGANDO MAPA ---")
        try:
            map_image = pygame.image.load('./assets/maps/map.png').convert_alpha()
            self.visible_sprites.floor_surf = map_image
            self.visible_sprites.floor_rect = map_image.get_rect(topleft=(0, 0))
        except FileNotFoundError:
            self.visible_sprites.floor_surf = pygame.Surface((1000, 1000))
            self.visible_sprites.floor_rect = self.visible_sprites.floor_surf.get_rect()

        # >>> DEBUG: confirma que está lendo esses CSVs mesmo
        print("[Level] lendo:", './assets/maps/map_entities.csv')

        layouts = {
            'boundary': import_csv_layout('./assets/maps/map_boundary.csv'),
            'entities': import_csv_layout('./assets/maps/map_entities.csv')
        }

        # DEBUG: quais valores existem no entities?
        try:
            vals = set()
            for row in layouts['entities'] or []:
                vals.update(row)
            vals.discard('-1')
            sample = sorted(vals)[:30]
            print(f"[Level] entities valores (amostra): {sample}")
        except Exception:
            pass

        player_created = False
        player_pos = (200, 200)
        boss_spawns = []

        # 1) varre entidades
        if layouts['entities']:
            for row_index, row in enumerate(layouts['entities']):
                for col_index, val in enumerate(row):
                    if val == '-1':
                        continue

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

                    elif val in ('88', '89'):
                        center_x = final_x + (TILESIZE // 2)
                        center_y = final_y + (TILESIZE // 2)
                        boss_spawns.append((center_x, center_y))

        if not player_created:
            self.player = Player(
                player_pos,
                [self.visible_sprites],
                self.obstacle_sprites,
                self.create_attack,
                self.destroy_attack,
                self.create_cracha
            )

        # 2) paredes
        if layouts['boundary']:
            for row_index, row in enumerate(layouts['boundary']):
                for col_index, val in enumerate(row):
                    if val != '-1':
                        x = col_index * TILESIZE
                        y = row_index * TILESIZE
                        Wall((x + SHIFT_X, y + SHIFT_Y), [self.obstacle_sprites])

        # 3) itens / barreira
        item_x = player_pos[0]
        item_y = player_pos[1] + 100
        Collectible((item_x, item_y), [self.visible_sprites, self.item_sprites], 'cracha')

        barrier_pos = (player_pos[0] + 16, player_pos[1] - 240)
        self.fire_barrier = FireBarrier(barrier_pos, [self.visible_sprites, self.obstacle_sprites])

        # 4) spawn boss
        if not boss_spawns and BOSS_FORCE_SPAWN_IF_NONE:
            dx, dy = BOSS_FORCE_OFFSET
            boss_spawns = [(player_pos[0] + dx, player_pos[1] + dy)]
            print(f"[Level] Nenhum 88/89 no CSV. Fallback spawn boss perto do player em {boss_spawns[0]}.")

        self._spawn_boss_slime(boss_spawns)

    def run(self, dt):
        self.input_debug()
        self.input_zoom()

        if hasattr(self, 'player'):
            self.visible_sprites.custom_draw(self.player, self.debug, self.obstacle_sprites)

            self._smart_update_group(self.visible_sprites, dt)
            self._smart_update_group(self.particle_sprites, dt)
            self._smart_update_group(self.enemy_attack_sprites, dt)
            self._smart_update_group(self.ui_sprites, dt)
            self.ui_sprites.draw(self.display_surface)

            self.player_attack_logic()
            self.enemy_attack_logic()
            self.item_collection_logic()

            if self.attackable_sprites:
                for enemy in self.attackable_sprites:
                    if hasattr(enemy, 'get_status'):
                        enemy.get_status(self.player)
                        enemy.actions(self.player)

            self.ui.display(self.player)

            try:
                self.check_barrier_interaction()
            except Exception:
                pass


class YSortCameraGroup(pygame.sprite.Group):
    def __init__(self, surface):
        super().__init__()
        self.display_surface = surface

        # Começa neutro (boss.py já tem scale próprio; zoom 2.5 vira escala dupla).
        self.zoom_scale = 2.0

        self.screen_width = self.display_surface.get_size()[0]
        self.screen_height = self.display_surface.get_size()[1]

        self.internal_width = max(1, int(self.screen_width / self.zoom_scale))
        self.internal_height = max(1, int(self.screen_height / self.zoom_scale))

        self.internal_surf = pygame.Surface((self.internal_width, self.internal_height), pygame.SRCALPHA)
        self.internal_rect = self.internal_surf.get_rect(center=(self.screen_width // 2, self.screen_height // 2))

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

    def change_zoom(self, amount):
        self.zoom_scale += amount
        if self.zoom_scale < 0.5:
            self.zoom_scale = 0.5
        if self.zoom_scale > 3.5:
            self.zoom_scale = 3.5

        self.internal_width = max(1, int(self.screen_width / self.zoom_scale))
        self.internal_height = max(1, int(self.screen_height / self.zoom_scale))

        self.internal_surf = pygame.Surface((self.internal_width, self.internal_height), pygame.SRCALPHA)
        self.internal_rect = self.internal_surf.get_rect(center=(self.screen_width // 2, self.screen_height // 2))

        self.half_w = self.internal_width // 2
        self.half_h = self.internal_height // 2

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
            if self.offset.x - 100 < sprite.rect.right and \
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
        self.display_surface.blit(scaled_surf, (0, 0))
