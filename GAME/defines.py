import math
from GAME.math import normalize_vector3d
from GAME.maze import *

# Paramètres de la fenêtre et du jeu
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
MAX_FRAME_RATE = 5000
FOV = 80 * math.pi / 180    # Champ de vision (fov) en radians du joueur
HALF_FOV = FOV / 2          # Moitié du fov
# MAX_DEPTH = 100

LIGHT_INTENSITY = 1         # Intensité de la lumière du joueur
LIGHT_OFFSET = 0.05         # Décalage entre le joueur et sa lumière

FULL_RES = False

WALL_LOW = -1.5               # Point bas du mur
WALL_HIGH = 1.8               # Point haut du mur

MOVE_SPEED = 2              # Vitesse de déplacement
ENTITY_DAMAGE = 5
ROTATION_SPEED = 2          # Vitesse de rotation
LOAD_TIME = 2               # Temps de chargement
MAX_PLAYER_INTERACTION_RANGE = 2    # Distance maximum d'interaction
ENTITY_WALK_SOUND_SPEED = .8
ENTITY_RUN_SOUND_SPEED = .25

GAME_TITLE = "Jeu NSI"
MENU_OUTLINE = 10
MENU_OUTLINE2 = 5

INVENTORY_SIZE = 64

if FULL_RES:
    RESOLUTION_X = SCREEN_WIDTH
    RESOLUTION_Y = SCREEN_HEIGHT
else:
    RESOLUTION_X = 256          # Résolution de la fenêtre
    RESOLUTION_Y = int(RESOLUTION_X * SCREEN_HEIGHT / SCREEN_WIDTH)

HALF_RES_X = RESOLUTION_X // 2
HALF_RES_Y = RESOLUTION_Y // 2

# Map de test
MAP1_SIZE_X = 65 # 257 # 2047
MAP1_SIZE_Y = 65 # 257 # 2047

MAP1, MAP1_INTERACT = maze_to_map(MAP1_SIZE_X, MAP1_SIZE_Y)