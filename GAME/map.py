from GAME.defines import *
import pygame
import numpy
import os

class Map:
    def __init__(self):
        self.size = (0, 0)
        self._map = ()
        self.floor_texture_index = 0
        self.textures = []
        self.textures_size = []
        self.interaction_data = []

    def load_from_list(self, data: list, interaction_data : list, size_x: int, size_y: int,
                       tex_filenames: list, _floor_texture_index: int, _ceiling_texture_index: int):
        self._map = data
        self.size = (size_x, size_y)
        self.floor_texture_index = _floor_texture_index
        self.ceiling_texture_index = _ceiling_texture_index
        self.interaction_data = interaction_data
        for f in tex_filenames:
            assert type(f) == str, "Les noms de fichiers doivent être des string"

            tex = pygame.image.load(os.path.abspath(f))
            self.textures.append(pygame.surfarray.array3d(tex).astype(numpy.uint8))
            self.textures_size.append(tex.get_size())