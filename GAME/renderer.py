import sys
import math
import numpy
from numba import njit, prange
from GAME.defines import WALL_LOW, WALL_HIGH, LIGHT_INTENSITY, LIGHT_OFFSET, MAX_PLAYER_INTERACTION_RANGE, FOV, MENU_OUTLINE, MENU_OUTLINE2, HALF_FOV
import GAME.map as mp
from GAME.math import normalize_vector2d, dot_2d, dot_3d, lerp
from GAME.rays import cast_ray
from GAME.entity import Entity

# # Implémente la formule de tonemapping de Reinhard 
# @njit(fastmath = True, cache = True)
# def tonemap_channel(c: float):
#     return c / (c + 1)

@njit(fastmath = True, cache = True)
def tonemap_channel(c: float):
    return math.tanh(c)

@njit(fastmath = True, cache = True)
def tonemap_color(c: tuple):
    return (tonemap_channel(c[0]), tonemap_channel(c[1]), tonemap_channel(c[2]))

# # Implémente la formule de tonemapping de Reinhard-Jodie
# @njit(fastmath = True)
# def tonemap_color(c: tuple):
#     l = 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]
#     tv = (tonemap_channel(c[0]), tonemap_channel(c[1]), tonemap_channel(c[2]))
#     V = (c[0] / (1 + l), c[1] / (1 + l), c[2] / (1 + l))
#     return (lerp(V[0], tv[0], tv[0]), lerp(V[1], tv[1], tv[1]), lerp(V[2], tv[2], tv[2]))

@njit(fastmath = True, cache = True)
def gamma_correct(c: tuple):
    return (c[0]**.9, c[1]**.9, c[2]**.9)# (math.sqrt(c[0]), math.sqrt(c[1]), math.sqrt(c[2])) # (c[0]**(1 / 2.2), c[1]**(1 / 2.2), c[2]**(1 / 2.2))

# Calcule une image et la retourne dans la liste 'buffer'
@njit(parallel = True, fastmath = True, cache = True)
def render_frame(buffer: list, zbuffer: list, player_x: float, player_y: float, player_z: float, 
                 player_angle: float, _map_data: list, _map_size: tuple, _map_textures: list,
                 _map_textures_sizes: list, _map_floor_tex_idx: int, _map_ceil_tex_idx: int,
                 entities: numpy.ndarray, RESOLUTION_X: int, RESOLUTION_Y: int):
    # HALF_FOV = FOV / 2
    # HALF_RES_X = RESOLUTION_X // 2
    HALF_RES_Y = RESOLUTION_Y // 2
    for ray in prange(RESOLUTION_X):
        ray_angle = player_angle + (ray / RESOLUTION_X) * FOV
        project_dist = math.cos(ray / RESOLUTION_X * FOV - HALF_FOV)
        dX = -math.sin(ray_angle - HALF_FOV) 
        dY = math.cos(ray_angle - HALF_FOV) 
        if dX == 0:
            dX = 0.001
        if dY == 0:
            dY = 0.001
        wall_dist, hit, map_x, map_y, last_offset, step_x, step_y = cast_ray(dX, dY, player_x, player_y, ray_angle, _map_data, _map_size)
        pos_x, pos_y = wall_dist * dX + player_x, wall_dist * dY + player_y
        if hit:     # Le rayon a touché quelque chose
            off_x = pos_x - map_x       # Décalage par rapport au coin de la cellule
            off_y = pos_y - map_y

            wall_type = _map_data[map_y * _map_size[0] + map_x] # Texture à appliquer

            # Calcul de la normale de la surface
            normal = [0, 0]
            if last_offset == 1:
                normal = [step_x, 0]
            if last_offset == 2:
                normal = [0, step_y]
            normalize_vector2d(normal)
            
            wall_height = RESOLUTION_Y / max(wall_dist * project_dist, 0.01)   # Hauteur du mur à afficher
            wall_low_y = int(HALF_RES_Y - (wall_height / 2 * (WALL_LOW - player_z)))
            wall_high_y = int(HALF_RES_Y - (wall_height / 2 * (WALL_HIGH - player_z)))

            shade = LIGHT_INTENSITY / (max(0.01, (wall_dist + LIGHT_OFFSET)))**2 * max(0, dot_2d(normal, (dX, dY)))   # Calcul de l'éclairage
            for y in prange(wall_high_y, wall_low_y + 1):
                v = (y - wall_high_y) / (wall_low_y - wall_high_y + 1)
                if 0 <= y < RESOLUTION_Y: 
                    tex_idx = (wall_type - 1) % len(_map_textures) # int(ord(wall_type) - ord('1')) 
                    uv = ((off_x + off_y) % 1, v)

                    color = (1, 0, 0)

                    if tex_idx < len(_map_textures):
                        tex_width = _map_textures_sizes[tex_idx][1]
                        tex_height = _map_textures_sizes[tex_idx][0]

                        tex = (_map_textures[tex_idx][int(uv[0] * tex_height), int(uv[1] * tex_width), 0] / 255,
                        _map_textures[tex_idx][int(uv[0] * tex_height), int(uv[1] * tex_width), 1] / 255, 
                        _map_textures[tex_idx][int(uv[0] * tex_height), int(uv[1] * tex_width), 2] / 255)

                        color = gamma_correct(tonemap_color((float(shade * tex[0]), float(shade * tex[1]), float(shade * tex[2]))))
                        
                    buffer[ray][y] = color
                    zbuffer[ray][y] = wall_dist
                    
            for i in prange(wall_high_y + 1):
                if _map_ceil_tex_idx < len(_map_textures):
                    z = -(HALF_RES_Y / (i - HALF_RES_Y) / project_dist) * (WALL_HIGH - player_z)
                    dX = -math.sin(ray_angle - HALF_FOV) 
                    dY = math.cos(ray_angle - HALF_FOV) 
                    p_x = dX * z + player_x
                    p_y = dY * z + player_y
                    uv = (p_x % 1, p_y % 1)

                    shade = LIGHT_INTENSITY / (max(0.01, (z + LIGHT_OFFSET)))**3 # Approximation puisqu'on ne calcule pas la normale pour le plafond

                    tex_width = _map_textures_sizes[_map_ceil_tex_idx][1]
                    tex_height = _map_textures_sizes[_map_ceil_tex_idx][0]

                    idx_x = int(uv[0] * tex_height)
                    idx_y = int(uv[1] * tex_width)

                    tex = (_map_textures[_map_ceil_tex_idx][idx_x, idx_y, 0] / 255,
                    _map_textures[_map_ceil_tex_idx][idx_x, idx_y, 1] / 255, 
                    _map_textures[_map_ceil_tex_idx][idx_x, idx_y, 2] / 255)

                    buffer[ray][i] = gamma_correct(tonemap_color((float(shade * tex[0]), float(shade * tex[1]), float(shade * tex[2]))))
                    zbuffer[ray][i] = math.sqrt((WALL_HIGH - player_z)**2 + z**2)
                else:
                    buffer[ray][i] = (0, 0, 0)
                    zbuffer[ray][i] = 100
            for i in prange(wall_low_y + 1, RESOLUTION_Y):
                if _map_floor_tex_idx < len(_map_textures):
                    z = - (HALF_RES_Y / (i - HALF_RES_Y) / project_dist) * (WALL_LOW - player_z)
                    dX = -math.sin(ray_angle - HALF_FOV) 
                    dY = math.cos(ray_angle - HALF_FOV) 
                    p_x = dX * z + player_x
                    p_y = dY * z + player_y
                    uv = (p_x % 1, p_y % 1)

                    shade = LIGHT_INTENSITY / (max(0.01, (z + LIGHT_OFFSET)))**3 # Approximation puisqu'on ne calcule pas la normale pour le sol

                    tex_width = _map_textures_sizes[_map_floor_tex_idx][1]
                    tex_height = _map_textures_sizes[_map_floor_tex_idx][0]

                    idx_x = int(uv[0] * tex_height)
                    idx_y = int(uv[1] * tex_width)

                    tex = (_map_textures[_map_floor_tex_idx][idx_x, idx_y, 0] / 255,
                    _map_textures[_map_floor_tex_idx][idx_x, idx_y, 1] / 255, 
                    _map_textures[_map_floor_tex_idx][idx_x, idx_y, 2] / 255)

                    buffer[ray][i] = gamma_correct(tonemap_color((float(shade * tex[0]), float(shade * tex[1]), float(shade * tex[2]))))
                    zbuffer[ray][i] = math.sqrt((WALL_LOW - player_z)**2 + z**2)
        
        # Affiche les entités
        for entity in entities:
            pos_x, pos_y, pos_z = entity['position']
            size_x, size_y = entity['size']
            tex = entity['texture']
            alpha = entity['alpha']
            tex_h, tex_w = tex.shape[1], tex.shape[0]

            vector_to_entity = (float(pos_x - player_x), float(pos_y - player_y))
            distance_to_entity = math.sqrt(vector_to_entity[0]**2 + vector_to_entity[1]**2)

            vector_to_entity = (vector_to_entity[0] / float(distance_to_entity), vector_to_entity[1] / float(distance_to_entity))
                
            angle_to_entity = math.acos(dot_2d(vector_to_entity, (0, 1)))
            if vector_to_entity[0] > 0:
                angle_to_entity *= -1
            angle_to_entity %= math.pi * 2

            angle_to_intersection = math.acos(dot_2d((dX, dY), (0, 1)))
            if dX > 0:
                angle_to_intersection *= -1
            angle_to_intersection %= math.pi * 2
            
            if distance_to_entity > 0.05:
                if (size_x / (2 * distance_to_entity)) < math.pi:
                    angle_diff_to_entity = math.acos(dot_2d(vector_to_entity, (dX, dY)))

                    sprite_height = size_y / distance_to_entity * 3 * RESOLUTION_Y
                    sprite_low = pos_z - size_y / 2
                    sprite_high = pos_z + size_y / 2
                    sprite_low_y = int(HALF_RES_Y - (sprite_height / 2 * (sprite_low - player_z / 4)))
                    sprite_high_y = int(HALF_RES_Y - (sprite_height / 2 * (sprite_high - player_z / 4)))
                    
                    if angle_diff_to_entity < size_x / distance_to_entity / 2:
                        for y in prange(max(min(sprite_high_y, RESOLUTION_Y), 0), max(min(sprite_low_y, RESOLUTION_Y), 0)):
                            real_distance_to_entity = distance_to_entity  # Simplification mais ca suffit dans ce cas (on suppose que l'entité fait partie d'un arc de cercle dans les calculs de distance (pas d'affichage))
                            if real_distance_to_entity < zbuffer[ray][y][0]:
                                v = (y - sprite_high_y) / (sprite_low_y - sprite_high_y)
                                u = min(2, max(0, (2 - (((((float(angle_to_intersection - angle_to_entity) + math.pi) % (2 * math.pi)) - math.pi + (size_x / (2 * distance_to_entity))) % (2 * math.pi)) / (size_x / (2 * distance_to_entity)))))) / 2
                                w = tex_w
                                h = tex_h
                                idx_x = int(u * w)
                                idx_y = int(v * h)
                                if tex[idx_x, idx_y, 0] != alpha[0] or tex[idx_x, idx_y, 1] != alpha[1] or tex[idx_x, idx_y, 2] != alpha[2]:
                                    shade = LIGHT_INTENSITY / distance_to_entity * .3 # Pour les rendre plus sombres
                                    zbuffer[ray][y][0] = real_distance_to_entity
                                    buffer[ray][y] = gamma_correct(tonemap_color((tex[idx_x, idx_y, 0] / 255 * shade, 
                                                    tex[idx_x, idx_y, 1] / 255 * shade, 
                                                    tex[idx_x, idx_y, 2] / 255 * shade)))

# Gestion de la police de caractères
FONT_SIZE = 8
def get_char_matrix(c):
    # Police 8x8
    font = {
        ' ': [0x00] * 8,
        '?': [0x3C, 0x42, 0x06, 0x0C, 0x18, 0x00, 0x18, 0x00],
        
        'A': [0x18,0x3C,0x66,0x7E,0x66,0x66,0x66,0x00],
        'B': [0x7C,0x66,0x66,0x7C,0x66,0x66,0x7C,0x00],
        'C': [0x3C,0x66,0x60,0x60,0x60,0x66,0x3C,0x00],
        'D': [0x78,0x6C,0x66,0x66,0x66,0x6C,0x78,0x00],
        'E': [0x7E,0x60,0x60,0x7C,0x60,0x60,0x7E,0x00],
        'F': [0x7E,0x60,0x60,0x7C,0x60,0x60,0x60,0x00],
        'G': [0x3C,0x66,0x60,0x6E,0x66,0x66,0x3C,0x00],
        'H': [0x66,0x66,0x66,0x7E,0x66,0x66,0x66,0x00],
        'I': [0x3C,0x18,0x18,0x18,0x18,0x18,0x3C,0x00],
        'J': [0x1E,0x0C,0x0C,0x0C,0x0C,0x6C,0x38,0x00],
        'K': [0x66,0x6C,0x78,0x70,0x78,0x6C,0x66,0x00],
        'L': [0x60,0x60,0x60,0x60,0x60,0x60,0x7E,0x00],
        'M': [0x63,0x77,0x7F,0x6B,0x63,0x63,0x63,0x00],
        'N': [0x66,0x76,0x7E,0x7E,0x6E,0x66,0x66,0x00],
        'O': [0x3C,0x66,0x66,0x66,0x66,0x66,0x3C,0x00],
        'P': [0x7C,0x66,0x66,0x7C,0x60,0x60,0x60,0x00],
        'Q': [0x3C,0x66,0x66,0x66,0x6A,0x6C,0x36,0x00],
        'R': [0x7C,0x66,0x66,0x7C,0x6C,0x66,0x66,0x00],
        'S': [0x3C,0x66,0x60,0x3C,0x06,0x66,0x3C,0x00],
        'T': [0x7E,0x18,0x18,0x18,0x18,0x18,0x18,0x00],
        'U': [0x66,0x66,0x66,0x66,0x66,0x66,0x3C,0x00],
        'V': [0x66,0x66,0x66,0x66,0x66,0x3C,0x18,0x00],
        'W': [0x63,0x63,0x63,0x6B,0x7F,0x77,0x63,0x00],
        'X': [0x66,0x66,0x3C,0x18,0x3C,0x66,0x66,0x00],
        'Y': [0x66,0x66,0x66,0x3C,0x18,0x18,0x18,0x00],
        'Z': [0x7E,0x06,0x0C,0x18,0x30,0x60,0x7E,0x00],
        
        'a': [0x00,0x3C,0x06,0x3E,0x66,0x66,0x3E,0x00],
        'b': [0x60,0x60,0x7C,0x66,0x66,0x66,0x7C,0x00],
        'c': [0x00,0x3C,0x66,0x60,0x60,0x66,0x3C,0x00],
        'd': [0x06,0x06,0x3E,0x66,0x66,0x66,0x3E,0x00],
        'e': [0x00,0x3C,0x66,0x7E,0x60,0x62,0x3C,0x00],
        'f': [0x1C,0x36,0x30,0x7C,0x30,0x30,0x30,0x00],
        'g': [0x00,0x3E,0x66,0x66,0x3E,0x06,0x3C,0x00],
        'h': [0x60,0x60,0x7C,0x66,0x66,0x66,0x66,0x00],
        'i': [0x18,0x00,0x38,0x18,0x18,0x18,0x3C,0x00],
        'j': [0x0C,0x00,0x0C,0x0C,0x0C,0x6C,0x38,0x00],
        'k': [0x60,0x66,0x6C,0x78,0x78,0x6C,0x66,0x00],
        'l': [0x38,0x18,0x18,0x18,0x18,0x18,0x3C,0x00],
        'm': [0x00,0x76,0x7F,0x6B,0x6B,0x63,0x63,0x00],
        'n': [0x00,0x7C,0x66,0x66,0x66,0x66,0x66,0x00],
        'o': [0x00,0x3C,0x66,0x66,0x66,0x66,0x3C,0x00],
        'p': [0x00,0x7C,0x66,0x66,0x7C,0x60,0x60,0x00],
        'q': [0x00,0x3E,0x66,0x66,0x3E,0x06,0x06,0x00],
        'r': [0x00,0x7C,0x66,0x60,0x60,0x60,0x60,0x00],
        's': [0x00,0x3E,0x60,0x3C,0x06,0x06,0x7C,0x00],
        't': [0x30,0x7C,0x30,0x30,0x30,0x34,0x18,0x00],
        'u': [0x00,0x66,0x66,0x66,0x66,0x66,0x3E,0x00],
        'v': [0x00,0x66,0x66,0x66,0x66,0x3C,0x18,0x00],
        'w': [0x00,0x63,0x6B,0x6B,0x7F,0x36,0x36,0x00],
        'x': [0x00,0x66,0x3C,0x18,0x3C,0x66,0x66,0x00],
        'y': [0x00,0x66,0x66,0x66,0x3E,0x06,0x3C,0x00],
        'z': [0x00,0x7E,0x0C,0x18,0x30,0x60,0x7E,0x00],
        
        '0': [0x3C,0x42,0x42,0x42,0x42,0x42,0x3C,0x00],
        '1': [0x18,0x38,0x18,0x18,0x18,0x18,0x7E,0x00],
        '2': [0x3C,0x42,0x02,0x0C,0x30,0x40,0x7E,0x00],
        '3': [0x7E,0x02,0x04,0x1C,0x02,0x42,0x3C,0x00],
        '4': [0x04,0x0C,0x14,0x24,0x7E,0x04,0x04,0x00],
        '5': [0x7E,0x40,0x7C,0x02,0x02,0x42,0x3C,0x00],
        '6': [0x1C,0x20,0x40,0x7C,0x42,0x42,0x3C,0x00],
        '7': [0x7E,0x02,0x04,0x08,0x10,0x10,0x10,0x00],
        '8': [0x3C,0x42,0x42,0x3C,0x42,0x42,0x3C,0x00],
        '9': [0x3C,0x42,0x42,0x3E,0x02,0x04,0x38,0x00],
        
        '!': [0x18,0x18,0x18,0x18,0x18,0x00,0x18,0x00],
        ',': [0x00,0x00,0x00,0x00,0x00,0x18,0x18,0x30],
        ';': [0x00,0x18,0x18,0x00,0x18,0x18,0x30,0x00], 
        '.': [0x00,0x00,0x00,0x00,0x00,0x00,0x18,0x00],
        '/': [0x02,0x04,0x08,0x10,0x20,0x40,0x80,0x00],
        '\\':[0x80,0x40,0x20,0x10,0x08,0x04,0x02,0x00],
        '%': [0x63,0x66,0x0C,0x18,0x30,0x66,0xC6,0x00],
        '$': [0x18,0x3E,0x60,0x3C,0x06,0x7C,0x18,0x00],
        ':': [0x00,0x18,0x18,0x00,0x00,0x18,0x18,0x00]
    }
    
    matrix = font.get(c, font['?'])
    # return [[int(bit) for bit in format(row, '016b')] for row in matrix]
    return [[int(bit) for bit in format(row, '08b')] for row in matrix]

def idle_animation(time, amplitude = 0.5, speed = 1, offset = 0):
    """
    Retourne un tuple (x_offset, y_offset, rotation_angle) pour faire une animation basique de la caméra
    Paramètres:
    - time: Temps actuel en secondes
    - amplitude: Amplitude du mouvement
    - speed: Vitesse de mouvement
    - offset: Décalage
    """
    
    x = math.sin(time * 0.7 * speed + offset) * amplitude * 0.8
    
    y = (math.cos(time * 1.2 * speed + offset * 2) * 
        (amplitude * 0.6) * 
        (0.5 + 0.5 * math.sin(time * 0.3 * speed)))
    
    z = (math.sin(time * 0.5 * speed + offset * 0.8) * 
        amplitude * 0.4 * 
        (0.7 + 0.3 * math.cos(time * 0.35 * speed)))
    
    rot = (math.sin(time * 0.5 * speed + offset * 3) * 
          amplitude * 0.15 * 
          (0.8 + 0.2 * math.cos(time * 0.9 * speed)))

    return (x, y, z, rot)

# Gère tout les calculs visuels
class Renderer:
    def __init__(self, RESOLUTION_X: int, RESOLUTION_Y: int):
        self.res_x = RESOLUTION_X
        self.res_y = RESOLUTION_Y
        self.buffer = numpy.zeros((RESOLUTION_X, RESOLUTION_Y, 3))
        self.zbuffer = numpy.zeros((RESOLUTION_X, RESOLUTION_Y, 1))
        entity_dtype = numpy.dtype([
            ('position', numpy.float64, (3,)),
            ('size', numpy.float64, (2,)),
            ('texture', numpy.uint8, (64, 96, 3)),
            ('alpha', numpy.uint8, (3,))
        ])
        self.entities = numpy.empty(0, dtype=entity_dtype)

    def clean_entities(self):
        entity_dtype = numpy.dtype([
            ('position', numpy.float64, (3,)),
            ('size', numpy.float64, (2,)),
            ('texture', numpy.uint8, (64, 96, 3)),
            ('alpha', numpy.uint8, (3,))
        ])
        self.entities = numpy.empty(0, dtype=entity_dtype)

    def add_entity(self, entity: Entity):
        new_entity = numpy.array([(
            entity.position,
            entity.size,
            entity.texture,
            entity.alpha_color
        )], dtype=self.entities.dtype)
        self.entities = numpy.concatenate((self.entities, new_entity))


    def invert_pixel(self, x: int, y: int):
        self.buffer[x][y] = (1 - self.buffer[x][y][0], 1 - self.buffer[x][y][1], 1 - self.buffer[x][y][2])

    def print_char(self, x, y, c, color):
        font_matrix = get_char_matrix(c)
        for j in range(FONT_SIZE):
            for i in range(FONT_SIZE):
                if font_matrix[i][j] == 1:
                    self.buffer[j + x][i + y] = color
                    # self.invert_pixel(j + 18, i + 18)

    def print_str(self, x, y, str, color):
        x_offset = 0
        max_x, max_y = x, y
        for i in range(len(str)):
            match str[i]:
                case '\n':
                    y += FONT_SIZE
                    max_y = max(max_y, y)
                    x -= x_offset
                    x_offset = 0
                case _:
                    self.print_char(x, y, str[i], color)
                    x += FONT_SIZE
                    x_offset += FONT_SIZE
                    max_x = max(max_x, x)
        return (x, y, max_x, max_y + FONT_SIZE)

    def draw_menu_frame(self):
        for i in range(MENU_OUTLINE, self.res_y - MENU_OUTLINE):
            for j in range(MENU_OUTLINE, self.res_x - MENU_OUTLINE):
                # self.invert_pixel(j, i)
                if i == MENU_OUTLINE or i == self.res_y - MENU_OUTLINE - 1 or j == MENU_OUTLINE or j == self.res_x - MENU_OUTLINE - 1 or (MENU_OUTLINE + MENU_OUTLINE2 <= i <= self.res_y - MENU_OUTLINE - MENU_OUTLINE2 - 1 and MENU_OUTLINE + MENU_OUTLINE2 <= j <= self.res_x - MENU_OUTLINE - MENU_OUTLINE2 - 1):
                    self.buffer[j][i] = (1, 1, 1)

    def draw_rectangle_outline(self, x_low, y_low, x_high, y_high, color):
        for i in range(y_low, y_high):
            for j in range(x_low, x_high):
                if j == x_low or j == x_high - 1 or i == y_low or i == y_high - 1:
                    self.buffer[j][i] = color

    def draw_button(self, x, y, text, color):
        _x, _y, max_x, max_y = self.print_str(x + 2, y + 2, text, color)
        self.draw_rectangle_outline(x, y, max_x + 2, max_y + 2, color)
        return x, y, max_x + 2, max_y + 2
    
    def dim_screen(self):
        for i in range(self.res_y):
                for j in range(self.res_x):
                    for k in range(3):
                        self.buffer[j][i][k] *= .5

    def delete_entity(self, index):
        numpy.delete(self.entities, index)

    def update(self, mv_speed: float, click_btn: int, mouse_x: int, mouse_y: int, timer: float, in_menu: int, _map: mp.Map, player_x: float, player_y: float, player_z: float, player_angle: float):
        if in_menu != 3:
            anim = idle_animation(timer, .03 + (mv_speed - 2) * .05)

            render_frame(self.buffer, self.zbuffer, player_x + anim[0], player_y + anim[1], player_z + anim[2], player_angle + anim[3], 
                        _map._map, _map.size, _map.textures, _map.textures_size, _map.floor_texture_index, _map.ceiling_texture_index, self.entities, self.res_x, self.res_y)
            
        if in_menu == 0:
            HALF_RES_X = self.res_x // 2
            HALF_RES_Y = self.res_y // 2

            beacon_pos = (_map.size[0] // 2 + 1.5, _map.size[1] // 2 + 1.5)
            delta_x = beacon_pos[0] - player_x
            delta_y = beacon_pos[1] - player_y

            angle_to_beacon = math.atan2(delta_x, delta_y)

            rel_angle_to_beacon = -((angle_to_beacon + player_angle + math.pi) % (2 * math.pi) - math.pi)

            beacon_pixel = rel_angle_to_beacon / FOV + 0.5

            for i in range(2, self.res_x - 2):
                self.buffer[i][self.res_y - 2] = (.8, .8, .8)

            if 0 <= beacon_pixel < 1:
                screen_x = int(beacon_pixel * (self.res_x - 4) + 2)
                if 2 <= screen_x < self.res_x - 2:
                    c = (.3, .4, 1)
                    for i in range(-1, 2):
                        self.buffer[screen_x - 1][self.res_y - 2 + i] = c
                        self.buffer[screen_x][self.res_y - 2 + i] = c
                        self.buffer[screen_x + 1][self.res_y - 2 + i] = c
            
            self.invert_pixel(HALF_RES_X, HALF_RES_Y)

            dX = -math.sin(player_angle) 
            dY = math.cos(player_angle) 
            if dX == 0:
                dX = 0.001
            if dY == 0:
                dY = 0.001
            wall_dist, hit, map_x, map_y, last_offset, step_x, step_y = cast_ray(dX, dY, player_x, player_y, player_angle, _map._map, _map.size)
            wall_dist += 0.01
            pos_x, pos_y = wall_dist * dX + player_x, wall_dist * dY + player_y
            if hit and _map.interaction_data[math.floor(pos_x) + math.floor(pos_y) * _map.size[0]] != 0 and wall_dist < MAX_PLAYER_INTERACTION_RANGE:
                for i in range(5):
                    for j in range(5):
                        if i == 0 or i == 4 or j == 0 or j == 4:
                            self.invert_pixel(HALF_RES_X - 2 + j, HALF_RES_Y - 2 + i)
            return 0
        else:
            """
            Boutons:
            1 : Jouer
            2 : Recharger la map
            3 : Rejouer
            4 : Controles
            """
            """
            Menus:
            1 : Menu principal
            2 : Terminal
            3 : Game over
            4 : Controles
            5 : Retour (controles)
            """
            match in_menu:
                case 1:
                    self.dim_screen()
                    self.print_str(18, 18, "Menu principal", (1, 1, 1))
                    btn = 0
                    c = 1
                    if click_btn == 1:
                        c = .7
                    x, y, max_x, max_y = self.draw_button(18, 36, "Jouer", (c, c, c))
                    # print(x, y, max_x, max_y)
                    if mouse_x >= x and mouse_y >= y and mouse_x < max_x and mouse_y < max_y:
                        btn = 1
                    
                    c = 1
                    if click_btn == 4:
                        c = .7
                    x, y, max_x, max_y = self.draw_button(18, 36 + 16, "Controles", (c, c, c))
                    # print(x, y, max_x, max_y)
                    if mouse_x >= x and mouse_y >= y and mouse_x < max_x and mouse_y < max_y:
                        btn = 4
                    return btn
                case 2:
                    self.dim_screen()
                    self.draw_menu_frame()
                    self.print_str(18, 18, "Terminal", (0, 0, 0))
                    c = 1
                    if click_btn == 2:
                        c = .7
                    c = 1 - c
                    x, y, max_x, max_y = self.draw_button(18, 36, "Recharger la map", (c, c, c))
                    if mouse_x >= x and mouse_y >= y and mouse_x < max_x and mouse_y < max_y:
                        return 2
                case 3:
                    for i in range(self.res_y):
                        for j in range(self.res_x):
                            self.buffer[j][i] = (0, 0, 0)
                    self.print_str(18, 18, "GAME OVER", (1, 0, 0))
                    c = 1
                    if click_btn == 3:
                        c = .7
                    x, y, max_x, max_y = self.draw_button(18, 36, "Rejouer", (c, c, c))
                    # print(x, y, max_x, max_y)
                    if mouse_x >= x and mouse_y >= y and mouse_x < max_x and mouse_y < max_y:
                        return 3
                case 4:
                    self.dim_screen()
                    self.print_str(18, 18, "Controles\n\nZQSD     Se deplacer\nE        Interagir\nLSHIFT   Courir", (1, 1, 1))
                    c = 1
                    if click_btn == 5:
                        c = .7
                    x, y, max_x, max_y = self.draw_button(18, 18 + 6 * 16, "Retour", (c, c, c))
                    # print(x, y, max_x, max_y)
                    if mouse_x >= x and mouse_y >= y and mouse_x < max_x and mouse_y < max_y:
                        return 5
                case _:
                    self.print_str(18, 18, "Menu non defini", (0, 0, 0))
            return 0