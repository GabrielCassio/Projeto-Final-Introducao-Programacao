import pygame
import os
from src.objects.character.obj_entity import Entity

class Player(Entity):
    def __init__(self, name: str, x: int, y: int, path_sprite: str):
        super().__init__(name, x, y, path_sprite) # Corrigido chamada do super

        # --- CONFIGURAÇÃO DE TAMANHO ---
        # Mude este número para aumentar ou diminuir o personagem
        self.scale_factor = 2.5

        # --- SETUP BÁSICO ---
        self.name = name
        self.walls = [] 
        
        # Direção e Status
        self.self_direction = "down"
        self.status = "idle"
        
        # Variável de movimento
        self.rect_movement = (0, 0) 

        # Estrutura do Dicionário de Animações
        self.animations = {
            "idle": {"up": [], "down": [], "left": [], "right": []},
            "run": {"up": [], "down": [], "left": [], "right": []},
        }

        # --- CARREGAR ASSETS ---
        self.import_player_assets()
        
        # Imagem inicial
        self.image = self.animations["idle"]["down"][0]
        self.rect = self.image.get_rect(topleft=(x, y))
        
        # Hitbox ajustado (Fica proporcional ao tamanho do sprite agora)
        # Ajuste esses valores (-10, -70) se o hitbox ficar estranho com o tamanho novo
        self.hitbox = self.rect.inflate(-20, -50) 

        # --- STATS ---
        self.stats = {'health': 100, 'energy': 60, 'attack': 10, 'magic': 4, 'speed': 6}
        self.speed = self.stats['speed']
        self.health = self.stats['health']
        self.energy = self.stats['energy']
        self.attack = self.stats['attack']
        self.magic = self.stats['magic']
        
        self.old_position = pygame.math.Vector2(x, y)

    def _fallback(self):
        """ Cria um quadrado branco caso a imagem falhe """
        s = pygame.Surface((32 * self.scale_factor, 32 * self.scale_factor), pygame.SRCALPHA)
        s.fill((255, 255, 255))
        return s

    def import_player_assets(self):
        base = "src/sprites/player" 
        dirs = ["up", "down", "left", "right"]

        for d in dirs:
            folder = os.path.join(base, "idle_and_run", d)
            
            if not os.path.isdir(folder):
                print(f"AVISO: Pasta não encontrada: {folder}")
                self.animations["idle"][d] = [self._fallback()]
                self.animations["run"][d] = [self._fallback()]
                continue

            files = sorted([f for f in os.listdir(folder) if f.lower().endswith(".png")])
            
            idle = None
            run = []
            
            for fn in files:
                img = pygame.image.load(os.path.join(folder, fn)).convert_alpha()
                
                # --- AQUI ESTÁ O AUMENTO DE TAMANHO ---
                w, h = img.get_size()
                img = pygame.transform.scale(img, (int(w * self.scale_factor), int(h * self.scale_factor)))
                # --------------------------------------

                if "frame_00" in fn.lower():
                    idle = img
                else:
                    run.append(img)

            if idle is None:
                idle = run[0] if run else self._fallback()
            if not run:
                run = [idle]

            self.animations["idle"][d] = [idle]
            self.animations["run"][d] = run

    def move(self, new_position_x: int, new_position_y: int) -> None:
        # Salva posição antiga
        self.old_position.x = self.rect.x
        self.old_position.y = self.rect.y
        old_hitbox_rect = self.hitbox.copy()

        # Atualiza Retângulo Visual
        self.rect.x = new_position_x
        self.hitbox.centerx = self.rect.centerx 

        # Colisão X
        if hasattr(self, 'walls') and self.walls:
            if self.hitbox.collidelist(self.walls) != -1:
                self.hitbox.centerx = old_hitbox_rect.centerx
                self.rect.centerx = self.hitbox.centerx

        self.rect.y = new_position_y
        self.hitbox.bottom = self.rect.bottom

        # Colisão Y
        if hasattr(self, 'walls') and self.walls:
            if self.hitbox.collidelist(self.walls) != -1:
                self.hitbox.bottom = old_hitbox_rect.bottom
                self.rect.bottom = self.hitbox.bottom

        # Calcula movimento para animação
        dx = self.rect.x - self.old_position.x
        dy = self.rect.y - self.old_position.y
        
        self.rect_movement = (dx, dy)

        if dx > 0: self.self_direction = 'right'
        elif dx < 0: self.self_direction = 'left'
        if dy > 0: self.self_direction = 'down'
        elif dy < 0: self.self_direction = 'up'

    def animate(self):
        # Verifica se está parado
        # Usamos 0.1 como margem de erro
        if abs(self.rect_movement[0]) < 0.1 and abs(self.rect_movement[1]) < 0.1:
            self.status = "idle"
            self.image = self.animations["idle"][self.self_direction][0]
        else:
            self.status = "run"
            frames = self.animations["run"][self.self_direction]
            if not frames: frames = [self._fallback()]
            
            idx = (pygame.time.get_ticks() // 120) % len(frames)
            self.image = frames[idx]

        # RE-CENTRALIZA O SPRITE NO HITBOX (Importante quando muda de tamanho)
        self.rect = self.image.get_rect(center=self.hitbox.center)
        self.rect.bottom = self.hitbox.bottom

    def update(self):
        self.animate()
        
        # --- CORREÇÃO DO IDLE ---
        # Resetamos o movimento para zero no final de cada frame.
        # Se o jogador continuar apertando a tecla, o método 'move()' será chamado 
        # no próximo frame e preencherá essa variável novamente.
        # Se ele soltar a tecla, 'move()' não é chamado, e isso aqui garante que ele fique parado.
        self.rect_movement = (0, 0)