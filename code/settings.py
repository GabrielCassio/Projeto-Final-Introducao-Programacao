# Tamanho da Janela (O que você vê no Windows)
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720

# Tamanho Interno (Resolução baixa para Pixel Art de 16px)
# 320x180 é exatamente 1/4 de 720p. Isso dá um zoom nítido.
GAME_WIDTH = 320
GAME_HEIGHT = 180

FPS = 60
TILESIZE = 16

# --- UI CONFIGS ---
BAR_HEIGHT = 20
HEALTH_BAR_WIDTH = 200
ENERGY_BAR_WIDTH = 140
ITEM_BOX_SIZE = 80
UI_FONT = './assets/graphics/font/joystix.ttf' # Se não tiver esta fonte, ele usa a padrão
UI_FONT_SIZE = 18

# Cores Gerais
WATER_COLOR = '#71ddee'
UI_BG_COLOR = '#222222'
UI_BORDER_COLOR = '#111111'
TEXT_COLOR = '#EEEEEE'

# Cores das Barras
HEALTH_COLOR = 'red'
ENERGY_COLOR = 'cyan' # Cor da barra de Dash
UI_BORDER_COLOR_ACTIVE = 'gold'


ENEMIES = ['skeleton', 'vampire', 'ghost']

SHIFT_X = 16 * 16
SHIFT_Y = 16 * 15

SHIFT_X_PLAYER = None
SHIFT_Y_PLAYER = None 

SHIFT_X_ENEMIES = 32 
SHIFT_Y_ENEMIES = 100