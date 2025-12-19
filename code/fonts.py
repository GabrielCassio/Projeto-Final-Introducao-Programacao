import pygame
import os
import sys

BASE_DIR = os.path.dirname(__file__)
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

def carregar_fonte_padrao(tamanho: int) -> pygame.font.Font:
    caminho_assets = os.path.join(BASE_DIR, "..", "assets", 'fonts')
    caminho_ttf = os.path.join(caminho_assets, "PixelifySans-Regular.ttf")
    try:
        return pygame.font.Font(caminho_ttf, tamanho)
    except Exception:
        return pygame.font.SysFont("arial", tamanho)