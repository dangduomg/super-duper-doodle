# shared constants


from pathlib import Path
from pygame.locals import *


SRC_ROOT_DIR = Path(__file__).parent
DATA_DIR = SRC_ROOT_DIR / 'data'

SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480
SCREEN_TITLE = 'pygame platformer physics demo'
FPS = 60

QUIT_KEYS = K_q, K_ESCAPE
LEFT_KEY = K_LEFT
RIGHT_KEY = K_RIGHT
JUMP_KEY = K_UP
RUN_KEY = K_s
SHOOT_KEY = K_a
NEW_POS_KEY = K_r

BG_COLOR = 54, 133, 207

GRAVITY = 0.5