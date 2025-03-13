import math
from GAME.defines import *
from GAME.math import *

# Trace un rayon à travers la scène en utilisant l'algorithme de raycasting DDA
@njit(fastmath = True)
def cast_ray(dX: float, dY: float, player_x: float, player_y: float, ray_angle: float, _map_data: list, _map_size: tuple):
    step_size_x = math.sqrt((dY / dX)**2 + 1) 
    step_size_y = math.sqrt((dX / dY)**2 + 1) 
    step_x = 0
    step_y = 0
    rlength_x = 0
    rlength_y = 0
    target_x = int(player_x)
    target_y = int(player_y)
    if dX < 0:
        step_x = -1
        rlength_x = (player_x - target_x) * step_size_x
    else:
        step_x = 1
        rlength_x = (target_x + 1 - player_x) * step_size_x
    if dY < 0:
        step_y = -1
        rlength_y = (player_y - target_y) * step_size_y
    else:
        step_y = 1
        rlength_y = (target_y + 1 - player_y) * step_size_y
    depth = 1
    last_offset = 0
    hit = False
    # while depth < MAX_DEPTH:   
    while True: 
        if rlength_x < rlength_y:
            target_x += step_x
            depth = rlength_x
            rlength_x += step_size_x
            last_offset = 1
        else:
            target_y += step_y
            depth = rlength_y
            rlength_y += step_size_y
            last_offset = 2
        if target_x >= _map_size[0] or target_y >= _map_size[1] or target_x < 0 or target_y < 0:
            break              
        if _map_data[target_y * _map_size[0] + target_x] != 0:
            hit = True
            break
    if hit:
        return depth, True, target_x, target_y, last_offset, step_x, step_y
        
    return 0, False, 0, 0, 0, 0, 0