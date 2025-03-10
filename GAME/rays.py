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
    while depth < MAX_DEPTH:    
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
        if _map_data[target_y * _map_size[0] + target_x] != ' ':
            hit = True
            break
    if hit:
        return depth, True, target_x, target_y, last_offset, step_x, step_y
        
    return 0, False, 0, 0, 0, 0, 0

@njit(fastmath = True)
def ray_entity_intersection(player_x: float, player_y: float, ray_angle: float, 
                            entity_pos: list, entity_size: list,
                            _map_data: list, _map_size: tuple):
    dX = math.sin(ray_angle) 
    dY = math.cos(ray_angle) 
    if dX == 0:
        dX = 0.001
    if dY == 0:
        dY = 0.001
    
    vector_to_entity = (float(entity_pos[0] - player_x), float(entity_pos[1] - player_y))
    distance_to_entity = math.sqrt(vector_to_entity[0]**2 + vector_to_entity[1]**2)

    vector_to_entity = (vector_to_entity[0] / float(distance_to_entity), vector_to_entity[1] / float(distance_to_entity))

    distance_to_wall = cast_ray(dX, dY, player_x, player_y, _map_data, _map_size)[0]

    if distance_to_entity > 0.05:
        if (entity_size[0] / (2 * distance_to_entity)) < math.pi:
            angle_diff_to_entity = math.acos(dot_2d(vector_to_entity, (dX, dY)))
            if angle_diff_to_entity < entity_size[0] / distance_to_entity / 2:
                if distance_to_entity < distance_to_wall:
                    return (True, distance_to_entity)
    return (False, 0)

@njit(fastmath = True, parallel = True)
def ray_entities_intersection(player_x: float, player_y: float, ray_angle: float, 
                              _map_data: list, _map_size: tuple,
                              entities_pos: list, entities_size: list):
    inter = (False, 0, 0)
    for i in range(len(entities_pos)):
        current_inter = ray_entity_intersection(player_x, player_y, ray_angle, entities_pos[i], entities_size[i], _map_data, _map_size)
        if current_inter[0]:
            if current_inter[1] < inter[1] or (not inter[0]):
                inter = (current_inter[0], current_inter[1], i)
    return inter