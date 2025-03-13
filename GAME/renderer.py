import sys
import math
import numpy
from numba import njit, prange
from GAME.defines import WALL_LOW, WALL_HIGH, LIGHT_INTENSITY, LIGHT_OFFSET, MAX_PLAYER_INTERACTION_RANGE, FOV
import GAME.map as mp
from GAME.math import normalize_vector2d, dot_2d, dot_3d, lerp
from GAME.rays import cast_ray

# Implémente la formule de tonemapping de Reinhard 
@njit(fastmath = True)
def tonemap_channel(c: float):
    return c / (c + 1)

@njit(fastmath = True)
def tonemap_color(c: tuple):
    return (tonemap_channel(c[0]), tonemap_channel(c[1]), tonemap_channel(c[2]))

# # Implémente la formule de tonemapping de Reinhard-Jodie
# @njit(fastmath = True)
# def tonemap_color(c: tuple):
#     l = 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]
#     tv = (tonemap_channel(c[0]), tonemap_channel(c[1]), tonemap_channel(c[2]))
#     V = (c[0] / (1 + l), c[1] / (1 + l), c[2] / (1 + l))
#     return (lerp(V[0], tv[0], tv[0]), lerp(V[1], tv[1], tv[1]), lerp(V[2], tv[2], tv[2]))

@njit(fastmath = True)
def gamma_correct(c: tuple):
    return (math.sqrt(c[0]), math.sqrt(c[1]), math.sqrt(c[2])) # (c[0]**(1 / 2.2), c[1]**(1 / 2.2), c[2]**(1 / 2.2))

# Calcule une image et la retourne dans la liste 'buffer'
@njit(parallel = True, fastmath = True)
def render_frame(buffer: list, zbuffer: list, player_x: float, player_y: float, player_z: float, player_angle: float, 
                 _map_data: list, _map_size: tuple, _map_textures: list, 
                 _map_textures_sizes: list, _map_floor_tex_idx: int, _map_ceil_tex_idx: int, RESOLUTION_X: int, RESOLUTION_Y: int):
    HALF_FOV = FOV / 2
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
                    tex_idx = wall_type - 1 # int(ord(wall_type) - ord('1')) 
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
                else:
                    buffer[ray][i] = (0, 0, 0)
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

# Gère tout les calculs visuels
class Renderer:
    def __init__(self, RESOLUTION_X: int, RESOLUTION_Y: int):
        self.res_x = RESOLUTION_X
        self.res_y = RESOLUTION_Y
        self.buffer = numpy.zeros((RESOLUTION_X, RESOLUTION_Y, 3))
        self.zbuffer = numpy.zeros((RESOLUTION_X, RESOLUTION_Y, 1))

    def invert_pixel(self, x: int, y: int):
        self.buffer[x][y] = (1 - self.buffer[x][y][0], 1 - self.buffer[x][y][1], 1 - self.buffer[x][y][2])

    def update(self, in_menu: int, _map: mp.Map, player_x: float, player_y: float, player_z: float, player_angle: float):
        render_frame(self.buffer, self.zbuffer, player_x, player_y, player_z, player_angle, 
                     _map._map, _map.size, _map.textures, _map.textures_size, _map.floor_texture_index, _map.ceiling_texture_index, self.res_x, self.res_y)
        
        if in_menu == 0:
            HALF_RES_X = self.res_x // 2
            HALF_RES_Y = self.res_y // 2
            
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
                        if  i == 0 or i == 4 or j == 0 or j == 4:
                            self.invert_pixel(HALF_RES_X - 2 + j, HALF_RES_Y - 2 + i)
        else:
            for i in range(self.res_y):
                for j in range(self.res_x):
                    for k in range(3):
                        self.buffer[j][i][k] *= .7