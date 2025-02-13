import pygame
from GAME.game import Game
from GAME.renderer import Renderer
from GAME.map import Map
from GAME.defines import *

game = Game(MAP1_SIZE_X / 2, MAP1_SIZE_Y / 2)
renderer = Renderer()

map1 = Map()
map1.load_from_list(MAP1, MAP1_SIZE_X, MAP1_SIZE_Y, 
                    ["RESOURCES\\contener.png", "RESOURCES\\585.png", "RESOURCES\\contener_blue.png", "RESOURCES\\588.png"], 
                    3)

while True:
    game.handleEvents()
    game.update(map1)
    renderer.update(map1, game.player_x, game.player_y, game.player_z, game.player_angle, FILL_COLOR)
    game.display(renderer.buffer)