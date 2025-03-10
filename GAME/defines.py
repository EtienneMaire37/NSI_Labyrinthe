import math
from GAME.math import normalize_vector3d
from GAME.maze import *

# Paramètres de la fenêtre et du jeu
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
MAX_FRAME_RATE = 5000
FOV = 80 * math.pi / 180    # Champ de vision (fov) en radians du joueur
HALF_FOV = FOV / 2          # Moitié du fov
MAX_DEPTH = 500

LIGHT_INTENSITY = 1         # Intensité de la lumière du joueur
LIGHT_OFFSET = 0.05         # Décalage entre le joueur et sa lumière

FULL_RES = False

WALL_LOW = -1.5               # Point bas du mur
WALL_HIGH = 1.8               # Point haut du mur

MOVE_SPEED = 2              # Vitesse de déplacement
ENTITY_MOVE_SPEED = 1       # Vitesse des entités
ENTITY_DAMAGE = 5
ROTATION_SPEED = 1.5          # Vitesse de rotation
LOAD_TIME = 2               # Temps de chargement

RESOLUTION_X = 256          # Résolution de la fenêtre
RESOLUTION_Y = int(RESOLUTION_X * SCREEN_HEIGHT / SCREEN_WIDTH)

if FULL_RES:
    RESOLUTION_X = SCREEN_WIDTH
    RESOLUTION_Y = SCREEN_HEIGHT

HALF_RES_X = RESOLUTION_X // 2
HALF_RES_Y = RESOLUTION_Y // 2

LIGHT_INTENSITY = 6         # Intensité de la lumière du soleil
LIGHT_ANGLE = normalize_vector3d((-1, -0.5, -1))
FILL_COLOR = (0.529, 0.808, 0.922)
AMBIENT_LIGHT = (0.8, 0.9, 1)

# Map de test
MAP1_SIZE_X = 32 # 256
MAP1_SIZE_Y = 32 # 256
'''MAP1 = (
    "11111111111111111"
    "1               1"
    "1      111  2   1"
    "1 22         2  1"
    "1               1"
    "1   3333 1111 3 3"
    "111 1111 1111 3 3"
    "1 1           3 3"
    "1 1 1111 3333 333"
    "1 1 1111 1111   1"
    "1               1"
    "1  2            1"
    "1   2  333   22 1"
    "1               1"
    "11111111111111111"
)'''

MAP1 = maze_to_map(MAP1_SIZE_X, MAP1_SIZE_Y)