import pygame, math

# Importing ssettings
from src.settings import *

# Class template do Player
class Entity(pygame.sprite.Sprite):
   # The respective entity could be receive 
   def __init__(self, name: str, x: int, y: int, group_collision: dict):
      # Acessing de parent of the Player class
      super().__init__()
      
      # Playe name
      self.name = name

      # Instance main display
      self.display_surface = pygame.display.get_surface()

      # Rectangle Properties ---------------------------
      self.image = pygame.Surface((20, 10))
      self.image.fill((255, 255, 0)) 
      self.rect = self.image.get_rect()
      self.rect.center = (WIDTH // 2, HEIGHT // 2)
      self.pos = pygame.math.Vector2(0, 0)
      # ------------------------------------------------

      # Status properties --------------------------------------
      self.max_hp = 100
      self.current_hp = 100
      self.last_hit_time = 0
      self.invulnerable_duration = 800

      self.hurt_flash_until = 0
      self.hurt_flash_ms = 140
      # -------------------------------------------------------

      # Attack Properties --------------------------------------
      # Max num of bagdes
      self.max_badge = 3
      # Ammunition of badges
      self.badge_ammo = 3
      # Time to reload the badges
      self.badge_reload_ms = 2000
      # Catch the last tick to calc the reload action
      self.last_badge_reload = pygame.time.get_ticks()
      # Ranged attack cooldown attack
      self.attack_cooldown_ms = 700
      # Time by the last attack
      self.last_attack_time = -10_000

      self.attack_slow_until = 0
      self.attack_slow_factor = 0.55
      self.attack_slow_duration_ms = 260

      self.attacking = False
      self.attack_duration = 400
      self.attack_time = 0
      # ---------------------------------------------------------
      
      # Movement Properties -------------------------
      self.player_speed = 1
      self.rect_movement = (0, 0)
      self.direction = pygame.math.Vector2()

      # Properties by the Dash
      self.max_dash = 2
      self.dash_charges = 2
      self.dash_cooldown_ms = 3000
      self._dash_restore_times: list[int] = []
      self.dash_distance = 85
      self._dash_prev_pressed = False

      # Glitch effect variables by dash
      self.glitch_until = 0
      self.glitch_from = self.rect.center
      self.glitch_to = self.rect.center

      self.global_action_cooldown = 0
      self.after_action_delay = 120
      # --------------------------------------------

      # Animation Properties ------------------------
      # Direction by the sprite position
      self.self_direction = "down"
      # Status Running or Idle by the animation
      self.status = "idle"

      # Throw animation
      self.throw_until = 0
      self.throw_ms = 260
      self.throw_start = 0
      # --------------------------------------------

      # Collision Properties -----------------------
      self.walls = group_collision['obstacles']
      # --------------------------------------------

   def dash_sweep_to_target(self, rect: pygame.Rect, target_center: tuple[int, int], walls: pygame.sprite.Group, step_px: int = 6) -> tuple[int, int]:
      sx, sy = rect.center
      tx, ty = target_center
      vx = tx - sx
      vy = ty - sy
      dist = math.hypot(vx, vy)
      if dist <= 0.001:
         return rect.center

      steps = max(1, int(dist // step_px))
      last_good = rect.copy()
      temp = rect.copy()

      for i in range(1, steps + 1):
         nx = int(sx + vx * (i / steps))
         ny = int(sy + vy * (i / steps))
         temp.center = (nx, ny)

         collision = False
         for w in walls:
            # Tenta pegar .rect (se for Sprite), senão usa o próprio objeto (se for Rect)
            wall_rect = getattr(w, 'rect', w)
            
            if temp.colliderect(wall_rect):
               collision = True
               break
         
         if collision:
                break
                
         last_good.center = temp.center
      return last_good.center