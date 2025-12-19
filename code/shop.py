# shop.py - VERSÃO INTEGRADA (Ouro + Pixel Font)
from __future__ import annotations
import math
import pygame
from dataclasses import dataclass
from typing import Callable, Optional, List, Tuple
from settings import * # --- IMPORTAÇÃO DA SUA FONTE ---
try:
    from fonts import carregar_fonte_padrao
except ImportError:
    # Fallback caso dê erro no import
    def carregar_fonte_padrao(size): return pygame.font.SysFont("arial", size, bold=True)

Vec2 = Tuple[float, float]

def clamp(v: float, a: float, b: float) -> float:
    return max(a, min(b, v))

def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t

def now_ms() -> int:
    return pygame.time.get_ticks()

def ensure_player_economy(player) -> None:
    """Conecta o sistema da loja ao sistema de COINS do seu player."""
    
    # Se o player já tem 'coins', usamos elas. Se não, cria zero.
    if not hasattr(player, "coins"):
        player.coins = 0 

    # Cria os métodos que a loja exige, apontando para 'coins'
    if not hasattr(player, "get_gems"):
        player.get_gems = lambda: player.coins

    if not hasattr(player, "spend_gems"):
        def spend_money(amount: int) -> bool:
            if player.coins >= amount:
                player.coins -= amount
                return True
            return False
        player.spend_gems = spend_money

def make_coin_icon(size: int = 20) -> pygame.Surface:
    """Cria uma MOEDA DE OURO estilizada em vez de gema verde."""
    s = pygame.Surface((size, size), pygame.SRCALPHA)
    cx, cy = size // 2, size // 2
    
    # Círculo Dourado
    pygame.draw.circle(s, (255, 215, 0), (cx, cy), size//2 - 1) # Ouro
    pygame.draw.circle(s, (218, 165, 32), (cx, cy), size//2 - 1, 2) # Borda mais escura
    
    # Brilho
    pygame.draw.circle(s, (255, 255, 200), (cx - 3, cy - 3), 2)
    
    return s

def render_text(font: pygame.font.Font, text: str, color: Tuple[int, int, int], shadow: bool = True) -> pygame.Surface:
    base = font.render(text, True, color) # True para Antialias
    if not shadow: return base
    
    sh = font.render(text, True, (0, 0, 0))
    out = pygame.Surface((base.get_width() + 2, base.get_height() + 2), pygame.SRCALPHA)
    out.blit(sh, (2, 2))
    out.blit(base, (0, 0))
    return out

def wrap_text(font: pygame.font.Font, text: str, max_w: int) -> List[str]:
    words = text.split()
    lines = []
    cur = ""
    for w in words:
        test = (cur + " " + w).strip()
        if font.size(test)[0] <= max_w:
            cur = test
        else:
            if cur: lines.append(cur)
            cur = w
    if cur: lines.append(cur)
    return lines

@dataclass
class ShopItemData:
    name: str
    price: int
    description: str
    category: str
    icon_surface: Optional[pygame.Surface]
    apply_effect: Callable

class ShopItemSprite(pygame.sprite.Sprite):
    def __init__(self, data: ShopItemData, card_size: Tuple[int, int]):
        super().__init__()
        self.data = data
        self.card_w, self.card_h = card_size
        self.base_image = pygame.Surface((self.card_w, self.card_h), pygame.SRCALPHA)
        self.image = self.base_image
        self.rect = self.image.get_rect()
        self.selected = False
        self._pulse_seed = (hash(self.data.name) % 1000) / 1000.0

        # CONFIGURAÇÃO DE SCROLL
        self.max_visible_items = 4 # Quantos itens cabem na tela sem vazar?
        self.scroll_offset = 0     # Qual é o primeiro item visível agora?
        self.item_height = 100     # Altura de cada card + espaço

    def rebuild(self, fonts: dict, coin_icon: pygame.Surface, theme: dict):
        w, h = self.card_w, self.card_h
        surf = pygame.Surface((w, h), pygame.SRCALPHA)

        # Cores baseadas no tema
        bg = theme["card_bg"]
        border = theme["card_border_sel"] if self.selected else theme["card_border"]
        
        pygame.draw.rect(surf, bg, (0, 0, w, h), border_radius=8)
        pygame.draw.rect(surf, border, (0, 0, w, h), width=2 if self.selected else 1, border_radius=8)

        # Nome e Categoria
        title = render_text(fonts["title_s"], self.data.name, theme["text"])
        surf.blit(title, (12, 10))
        
        cat = render_text(fonts["small"], self.data.category, theme["muted"])
        surf.blit(cat, (12, 32))

        # Preço (Lado Direito)
        price_txt = render_text(fonts["title_s"], str(self.data.price), theme["good"])
        px = w - 12 - price_txt.get_width()
        surf.blit(price_txt, (px, 12))
        surf.blit(coin_icon, (px - 20, 14))

        if self.selected:
            tag = render_text(fonts["small"], "[E] Comprar", theme["hint"])
            surf.blit(tag, (w - 12 - tag.get_width(), h - 20))

        self.base_image = surf
        self.image = self.base_image

    def update(self, *args):
        if self.selected:
            t = now_ms() * 0.005 + self._pulse_seed
            scale = 1.0 + 0.02 * math.sin(t)
            w, h = self.base_image.get_size()
            self.image = pygame.transform.scale(self.base_image, (int(w*scale), int(h*scale)))
            self.rect = self.image.get_rect(center=self.rect.center)
        else:
            self.image = self.base_image

class Toast:
    def __init__(self, text, ttl=1500, color=(255,255,255)):
        self.text = text
        self.ttl = ttl
        self.start = now_ms()
        self.color = color
    def active(self): return now_ms() - self.start < self.ttl

class Shop:
    def __init__(self, screen, player):
        self.screen = screen
        self.player = player
        ensure_player_economy(self.player) 

        # --- FONTES ---
        self.fonts = {
            "title": carregar_fonte_padrao(40),
            "title_s": carregar_fonte_padrao(20),
            "body": carregar_fonte_padrao(16),
            "small": carregar_fonte_padrao(12),
        }
        
        # Ícones
        self.coin_icon = make_coin_icon(24)
        self.coin_small = make_coin_icon(16)

        # Tema visual
        self.theme = {
            "panel_bg": (20, 20, 20),
            "card_bg": (40, 40, 40),
            "card_border": (100, 100, 100),
            "card_border_sel": (255, 215, 0),
            "text": (255, 255, 255),
            "muted": (150, 150, 150),
            "good": (100, 255, 100),
            "hint": (255, 255, 0)
        }

        # Itens
        self.items = self._create_items()
        self.sprites = pygame.sprite.Group()
        
        # Cria os sprites iniciais
        self.card_size = (300, 90)
        for i, item in enumerate(self.items):
            spr = ShopItemSprite(item, self.card_size)
            # A posição inicial não importa tanto, o run() vai corrigir
            spr.rect.topleft = (50, 100 + i * 100) 
            self.sprites.add(spr)
            
        self.selection = 0
        self.running = False
        self.toast = None

        # --- A CORREÇÃO ESTÁ AQUI (CONFIGURAÇÃO DO SCROLL) ---
        self.max_visible_items = 4  # Quantos itens aparecem na tela?
        self.scroll_offset = 0      # Qual é o primeiro item da lista agora?
        self.item_height = 100      # Altura do card + espaço entre eles
        # -----------------------------------------------------

    def _create_items(self):
        import random # Garante que o random funcione
        data = []
        
        # 1. Poção (Era 10 -> Agora 3)
        def buy_potion(p):
            p.health = min(p.health + 50, p.max_health)
        
        data.append(ShopItemData(
            name="Poção Maior", 
            price=3, 
            description="Recupera +50 de Vida instantaneamente.", 
            category="CONSUMÍVEL", icon_surface=None, apply_effect=buy_potion
        ))

        # 2. Dano (Era 50 -> Agora 15)
        def buy_damage(p):
            if not hasattr(p, 'attack_damage'): p.attack_damage = 10
            p.attack_damage += 5
            
        data.append(ShopItemData(
            name="Pedra de Amolar", 
            price=15, 
            description="Aumenta seu Dano base em +5 permanentemente.", 
            category="UPGRADE", icon_surface=None, apply_effect=buy_damage
        ))

        # 3. Velocidade (Era 80 -> Agora 20)
        def buy_speed(p):
            p.speed += 10
            
        data.append(ShopItemData(
            name="Botas Aladas", 
            price=20, 
            description="Aumenta sua velocidade de movimento.", 
            category="UPGRADE", icon_surface=None, apply_effect=buy_speed
        ))

        # 4. Vida Máxima (Era 150 -> Agora 40)
        def buy_max_health(p):
            if hasattr(p, 'max_health'):
                p.max_health += 20
                p.health += 20 
            
        data.append(ShopItemData(
            name="Coração de Ferro", 
            price=40, 
            description="Aumenta sua Vida Máxima em +20 permanentemente.", 
            category="UPGRADE", icon_surface=None, apply_effect=buy_max_health
        ))

        # 5. Ataque Rápido (Era 120 -> Agora 30)
        def buy_attack_speed(p):
            if hasattr(p, 'attack_cooldown'):
                p.attack_cooldown = max(200, p.attack_cooldown - 50)
            
        data.append(ShopItemData(
            name="Café Expresso", 
            price=30, 
            description="Bata mais rápido! (Reduz Cooldown)", 
            category="COMBATE", icon_surface=None, apply_effect=buy_attack_speed
        ))

        # 6. Double Dash (Era 200 -> Agora 50)
        def buy_double_dash(p):
            if hasattr(p, 'stats'):
                p.stats['energy'] += 40 
                p.energy = p.stats['energy']
            
        data.append(ShopItemData(
            name="Botas de Hermes", 
            price=50, 
            description="Energia Máxima++ (Permite Double Dash).", 
            category="MOVIMENTO", icon_surface=None, apply_effect=buy_double_dash
        ))

        # 7. Alcance (Era 150 -> Agora 40)
        def buy_range(p):
            if not hasattr(p, 'bonus_range'): p.bonus_range = 0
            p.bonus_range += 40
            
        data.append(ShopItemData(
            name="Cabo Longo", 
            price=40, 
            description="Atinge inimigos mais distantes.", 
            category="COMBATE", icon_surface=None, apply_effect=buy_range
        ))

        # 8. Tamanho Gigante (Era 300 -> Agora 75)
        def buy_size(p):
            if not hasattr(p, 'weapon_scale'): p.weapon_scale = 1.0
            p.weapon_scale += 0.5 
            
        data.append(ShopItemData(
            name="Metal Gigante", 
            price=75, 
            description="Sua espada fica GIGANTE!", 
            category="LENDA", icon_surface=None, apply_effect=buy_size
        ))

        # 9. Aposta (Era 20 -> Agora 5)
        def buy_gamble(p):
            outcome = random.choice(['cura', 'dano', 'nada'])
            if outcome == 'cura': p.health = p.max_health 
            elif outcome == 'dano': p.health -= 20 
            
        data.append(ShopItemData(
            name="Poção Misteriosa", 
            price=5, 
            description="Sorte ou Azar? (Cura tudo ou Machuca)", 
            category="SORTE", icon_surface=None, apply_effect=buy_gamble
        ))

        return data
    def _try_buy(self):
        item = self.items[self.selection]
        
        # Verifica se o player tem dinheiro (usando o sistema injetado em ensure_player_economy)
        if self.player.spend_gems(item.price):
            # 1. Aplica o efeito no player
            item.apply_effect(self.player)
            
            # 2. Feedback visual (Toast Sucesso)
            self.toast = Toast(f"Comprou: {item.name}!", color=(100, 255, 100))
            
            # 3. Som (Opcional - se tiver sistema de som)
            # if self.sound_buy: self.sound_buy.play()
            
        else:
            # Feedback visual (Toast Erro)
            self.toast = Toast("Ouro Insuficiente!", color=(255, 50, 50))
            # if self.sound_error: self.sound_error.play()

    def run(self):
        self.running = True
        clock = pygame.time.Clock()
        
        while self.running:
            dt = clock.tick(60)
            
            # --- 1. INPUT ---
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                        
                    # Navegação (W/S ou Setas)
                    if event.key in (pygame.K_w, pygame.K_UP):
                        self.selection = (self.selection - 1) % len(self.items)
                    if event.key in (pygame.K_s, pygame.K_DOWN):
                        self.selection = (self.selection + 1) % len(self.items)
                        
                    # Compra
                    if event.key in (pygame.K_e, pygame.K_RETURN, pygame.K_SPACE):
                        self._try_buy()

            # --- 2. UPDATE VISUAL COM SCROLL ---
            
            # Lógica: Se a seleção saiu da tela, o scroll acompanha
            if self.selection < self.scroll_offset:
                self.scroll_offset = self.selection
            
            if self.selection >= self.scroll_offset + self.max_visible_items:
                self.scroll_offset = self.selection - self.max_visible_items + 1

            # Atualiza posição dos sprites
            # OBS: Usamos list(self.sprites) para garantir a ordem
            items_list = list(self.sprites)
            for i, spr in enumerate(items_list):
                spr.selected = (i == self.selection)
                spr.rebuild(self.fonts, self.coin_small, self.theme)
                
                # Cálculo da posição Y baseado no Scroll
                base_y = 100
                new_y = base_y + (i - self.scroll_offset) * self.item_height
                
                # Lógica de Visibilidade:
                # Se estiver fora da área visível, jogamos para longe (-5000)
                # Não usamos spr.kill() aqui para não perder o sprite da lista
                if i < self.scroll_offset or i >= self.scroll_offset + self.max_visible_items:
                    spr.rect.topleft = (-5000, -5000) # Esconde fora da tela
                else:
                    spr.rect.topleft = (50, new_y) # Mostra na posição certa

            self.sprites.update()

            # --- 3. DRAW ---
            # Fundo escuro semi-transparente
            overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 200))
            self.screen.blit(overlay, (0,0))
            
            # Título
            title = render_text(self.fonts["title"], "MERCADOR", (255, 215, 0))
            self.screen.blit(title, (50, 30))
            
            # Suas Moedas
            coins_txt = render_text(self.fonts["title_s"], f"Ouro: {self.player.coins}", (255, 255, 255))
            self.screen.blit(coins_txt, (self.screen.get_width() - 200, 40))

            # Desenha Cards (Só os que estão dentro da tela vão aparecer)
            # Clip Opcional: Garante que nada desenhe em cima do Título
            clip_rect = pygame.Rect(0, 90, self.screen.get_width(), 600)
            self.screen.set_clip(clip_rect)
            self.sprites.draw(self.screen)
            self.screen.set_clip(None)
            
            # Painel de Detalhes (Direita)
            # Pegamos os dados direto da lista de itens para segurança
            sel_item = self.items[self.selection]
            
            desc_rect = pygame.Rect(400, 100, 350, 200)
            pygame.draw.rect(self.screen, (30,30,35), desc_rect, border_radius=10)
            pygame.draw.rect(self.screen, (100,100,100), desc_rect, width=2, border_radius=10)
            
            # Texto Descrição
            lines = wrap_text(self.fonts["body"], sel_item.description, 330)
            for k, line in enumerate(lines):
                txt = render_text(self.fonts["body"], line, (200,200,200))
                self.screen.blit(txt, (desc_rect.x + 10, desc_rect.y + 10 + k*20))

            # Toast (Mensagem de Compra)
            if self.toast and self.toast.active():
                t_surf = render_text(self.fonts["title_s"], self.toast.text, self.toast.color)
                self.screen.blit(t_surf, (self.screen.get_width()//2 - t_surf.get_width()//2, self.screen.get_height() - 100))

            pygame.display.flip()