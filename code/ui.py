# ui.py
import os
import pygame
from settings import *
from fonts import carregar_fonte_padrao

_UI_CACHE = {}

def _asset_path(*parts) -> str:
    base_dir = os.path.dirname(__file__)  
    return os.path.abspath(os.path.join(base_dir, "..", *parts)) 

def _load_image_cached(rel_path: tuple, scale_to=None) -> pygame.Surface:
    key = (rel_path, scale_to)
    if key in _UI_CACHE:
        return _UI_CACHE[key]
    full = _asset_path(*rel_path)
    surf = pygame.image.load(full).convert_alpha()
    if scale_to is not None:
        surf = pygame.transform.smoothscale(surf, scale_to)
    _UI_CACHE[key] = surf
    return surf

def _load_spritesheet_frames_cached(rel_path: tuple, frame_size=None, scale_to=None) -> list[pygame.Surface]:
    key = (rel_path, frame_size, scale_to)
    if key in _UI_CACHE:
        return _UI_CACHE[key]

    full = _asset_path(*rel_path)
    sheet = pygame.image.load(full).convert_alpha()
    sheet_w, sheet_h = sheet.get_size()

    if frame_size is None:
        frame_w = sheet_h
        frame_h = sheet_h
    else:
        frame_w, frame_h = frame_size

    cols = max(1, sheet_w // frame_w)
    frames = []
    for i in range(cols):
        rect = pygame.Rect(i * frame_w, 0, frame_w, frame_h)
        frame = sheet.subsurface(rect).copy()
        if scale_to is not None:
            frame = pygame.transform.smoothscale(frame, scale_to)
        frames.append(frame)

    _UI_CACHE[key] = frames
    return frames


class UI:
    def __init__(self):
        self.display_surface = pygame.display.get_surface()

        tamanho = UI_FONT_SIZE if 'UI_FONT_SIZE' in globals() else 18
        self.font = carregar_fonte_padrao(tamanho)

        # Barras
        self.health_bar_rect = pygame.Rect(10, 10, HEALTH_BAR_WIDTH, BAR_HEIGHT)
        self.energy_bar_rect = pygame.Rect(10, 34, ENERGY_BAR_WIDTH, BAR_HEIGHT)

        self.box_size = 90
        self.big_icon_size = (80, 80)
        self.small_icon_size = (24, 24)

        self.weapon_graphics = pygame.Surface(self.big_icon_size, pygame.SRCALPHA)
        self.weapon_graphics.fill((255, 255, 255, 60))

        self.cracha_big = None
        self.cracha_small = None
        try:
            self.cracha_big = _load_image_cached(("assets", "tiles", "cracha_vermelho.png"), scale_to=self.big_icon_size)
            self.cracha_small = _load_image_cached(("assets", "tiles", "cracha_vermelho.png"), scale_to=self.small_icon_size)
        except:
            pass

        self.soul_frames = None
        self.soul_frame_index = 0
        self.soul_frame_time = 0
        self.soul_frame_delay_ms = 80  
        try:
            self.soul_frames = _load_spritesheet_frames_cached(
                ("assets", "tiles", "soul.png"),
                frame_size=None,  
                scale_to=self.small_icon_size
            )
        except:
            self.soul_frames = None

        base_graphic = self.cracha_big if self.cracha_big else self.weapon_graphics
        self.weapon_rect = base_graphic.get_rect(
            bottomleft=(20, self.display_surface.get_height() - 20)
        )

    def show_bar(self, current, max_amount, bg_rect, color):
        pygame.draw.rect(self.display_surface, UI_BG_COLOR, bg_rect)

        ratio = (current / max_amount) if max_amount > 0 else 0
        current_width = int(bg_rect.width * ratio)

        current_rect = bg_rect.copy()
        current_rect.width = current_width

        pygame.draw.rect(self.display_surface, color, current_rect)

        border_color = UI_BORDER_COLOR if 'UI_BORDER_COLOR' in globals() else 'black'
        pygame.draw.rect(self.display_surface, border_color, bg_rect, 3)

    def show_counter(self, amount, offset_y, icon_surface=None, icon_color='gold'):
        text_color = TEXT_COLOR if 'TEXT_COLOR' in globals() else '#333333'
        bg_col = UI_BG_COLOR
        border_col = UI_BORDER_COLOR if 'UI_BORDER_COLOR' in globals() else 'black'

        text_surf = self.font.render(str(int(amount)), False, text_color)

        text_rect = text_surf.get_rect(bottomright=(
            self.display_surface.get_width() - 20,
            self.display_surface.get_height() - 20 - offset_y
        ))

        box_width = text_rect.width + 50
        box_height = text_rect.height + 20

        bg_rect = pygame.Rect(0, 0, box_width, box_height)
        bg_rect.bottomright = text_rect.bottomright

        pygame.draw.rect(self.display_surface, bg_col, bg_rect)
        pygame.draw.rect(self.display_surface, border_col, bg_rect, 3)

        text_rect.centery = bg_rect.centery
        text_rect.right = bg_rect.right - 10
        self.display_surface.blit(text_surf, text_rect)

        icon_x = bg_rect.left + 20
        icon_y = bg_rect.centery

        if icon_surface is not None:
            icon_rect = icon_surface.get_rect(center=(icon_x, icon_y))
            self.display_surface.blit(icon_surface, icon_rect)
        else:
            pygame.draw.circle(self.display_surface, icon_color, (icon_x, icon_y), 10)
            pygame.draw.circle(self.display_surface, 'white', (icon_x, icon_y), 10, 2)
            if icon_color == 'cyan':
                pygame.draw.circle(self.display_surface, 'white', (icon_x, icon_y), 4)

    def display(self, player):
        self.show_bar(player.health, player.max_health, self.health_bar_rect, HEALTH_COLOR)

        if player.can_dash:
            dash_val, dash_max = 1, 1
        else:
            time = pygame.time.get_ticks() - player.dash_time
            if time > player.dash_cooldown:
                time = player.dash_cooldown
            dash_val, dash_max = time, player.dash_cooldown
        self.show_bar(dash_val, dash_max, self.energy_bar_rect, ENERGY_COLOR)

        if player.has_cracha:
            bg_rect = pygame.Rect(0, 0, self.box_size, self.box_size)
            bg_rect.center = self.weapon_rect.center
            pygame.draw.rect(self.display_surface, UI_BG_COLOR, bg_rect)
            pygame.draw.rect(self.display_surface, UI_BORDER_COLOR, bg_rect, 3)

            if self.cracha_big:
                self.display_surface.blit(self.cracha_big, self.weapon_rect)
            else:
                self.display_surface.blit(self.weapon_graphics, self.weapon_rect)

        self.show_counter(player.coins, 0, icon_surface=None, icon_color='gold')

        soul_icon = None
        if self.soul_frames:
            now = pygame.time.get_ticks()
            if now - self.soul_frame_time >= self.soul_frame_delay_ms:
                self.soul_frame_time = now
                self.soul_frame_index = (self.soul_frame_index + 1) % len(self.soul_frames)
            soul_icon = self.soul_frames[self.soul_frame_index]

        self.show_counter(player.souls, 60, icon_surface=soul_icon, icon_color='cyan')
