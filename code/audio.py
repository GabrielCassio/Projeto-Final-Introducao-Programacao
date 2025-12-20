import os
import pygame
import sys
import json

BASE_DIR = os.path.dirname(__file__)
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

class AudioManager:
    def __init__(self):
        if not pygame.mixer.get_init():
            pygame.mixer.init()

        pasta_atual = os.path.dirname(__file__)
        caminho_audio = os.path.join(pasta_atual, "..", "assets", "audios")

        self.musicas = {
            "MENU": os.path.join(caminho_audio, "menu.ogg"),
            "CREDITOS": os.path.join(caminho_audio, "creditos.ogg"),
        }

        self.musica_atual = None
        self.music_volume = 0.75
        self.sfx_volume = 0.75

    def tocar_musica(self, nome: str):
        if nome == self.musica_atual:
            return

        caminho = self.musicas.get(nome)
        if not caminho:
            return

        try:
            pygame.mixer.music.stop()
            pygame.mixer.music.load(caminho)
            pygame.mixer.music.set_volume(self.music_volume)
            pygame.mixer.music.play(-1)
            self.musica_atual = nome
        except Exception:
            self.musica_atual = None

    def parar_musica(self):
        try:
            pygame.mixer.music.stop()
        except Exception:
            pass
        self.musica_atual = None

    def set_volume(self, valor: float):
        self.set_music_volume(valor)

    def set_music_volume(self, valor: float):
        self.music_volume = max(0.0, min(1.0, float(valor)))
        try:
            pygame.mixer.music.set_volume(self.music_volume)
        except Exception:
            pass

    def set_volume_sfx(self, valor: float):
        self.sfx_volume = max(0.0, min(1.0, float(valor)))

    def tocar_sfx(self, caminho_arquivo: str):
        try:
            s = pygame.mixer.Sound(caminho_arquivo)
            s.set_volume(self.sfx_volume)
            s.play()
        except Exception:
            pass

def carregar_config() -> dict:
    caminho_config = os.path.join(BASE_DIR, "..", "assets", "audios", "config.json")
    padrao = {
        "volume_musica": 0.75,
        "volume_efeitos": 0.75,
        "mutado_musica": False,
        "mutado_efeitos": False,
        "esquema_controle": "TECLADO",
    }
    try:
        with open(caminho_config, "r", encoding="utf-8") as f:
            data = json.load(f)
        for k, v in padrao.items():
            if k not in data:
                data[k] = v
        return data
    except Exception:
        return padrao


def aplicar_config_audio(audio: AudioManager):
    cfg = carregar_config()

    vol_m = float(cfg.get("volume_musica", 0.75))
    mute_m = bool(cfg.get("mutado_musica", False))
    audio.set_music_volume(0.0 if mute_m else vol_m)

    vol_s = float(cfg.get("volume_efeitos", 0.75))
    mute_s = bool(cfg.get("mutado_efeitos", False))
    audio.set_volume_sfx(0.0 if mute_s else vol_s)