import pygame
import numpy
import os
import random 
import math
from GAME.defines import ENTITY_WALK_SOUND_SPEED

class Entity:
    def __init__(self, pos_x: float, pos_y: float, pos_z: float, size_x: float, size_y: float, tex_file: str, alpha: tuple, walk_sound: str):
        self.position = (pos_x, pos_y, pos_z)
        self.size = (size_x, size_y)
        tex = pygame.image.load(os.path.abspath(tex_file))
        self.texture = pygame.surfarray.array3d(tex).astype(numpy.uint8)
        self.texture_size = tex.get_size()
        self.alpha_color = alpha
        self.walk_sound = pygame.mixer.Sound(file = walk_sound)
        self.walk_sound_timer = random.random() * ENTITY_WALK_SOUND_SPEED

        self.ai_state = "patrol"  # "patrol" or "chase"
        self.patrol_path = []
        self.current_patrol_target = 0
        self.path = []
        self.detection_radius = 5.0
        self.hearing_radius = 3.0
        self.speed = 2.5
        self.run_speed = 3.5
        self.last_seen_player_pos = (0, 0)