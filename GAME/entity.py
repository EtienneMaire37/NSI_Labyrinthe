import pygame
import numpy
import os
import random 
import math

class Entity:
    def __init__(self, pos_x: float, pos_y: float, pos_z: float, size_x: float, size_y: float, tex_file: str, alpha: tuple):
        self.position = (pos_x, pos_y, pos_z)
        self.size = (size_x, size_y)
        tex = pygame.image.load(os.path.abspath(tex_file))
        self.texture = pygame.surfarray.array3d(tex).astype(numpy.uint8)
        self.texture_size = tex.get_size()
        self.alpha_color = alpha
        
        self.ai_state = "patrol"  # "patrol" or "chase"
        self.patrol_path = []
        self.current_patrol_target = 0
        self.path = []
        self.detection_radius = 5.0
        self.hearing_radius = 3.0
        self.speed = 0.05
        self.last_seen_player_pos = (0, 0)