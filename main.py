import pygame
import cProfile
from GAME.game import Game
from GAME.renderer import Renderer
from GAME.map import Map
from GAME.defines import *

def main():
    game = Game(MAP1_SIZE_X / 2, MAP1_SIZE_Y / 2 + 1)
    renderer = Renderer()

    # print(maze_to_map(32, 32))

    map1 = Map()
    map1.load_from_list(MAP1, MAP1_SIZE_X, MAP1_SIZE_Y,
                        ["RESOURCES/pack/TILE_2C.PNG", "RESOURCES/082.png", "RESOURCES/pack/TECH_1C.PNG", "RESOURCES/pack/TECH_1E.PNG", "RESOURCES/pack/TECH_2F.PNG", "RESOURCES/pack/CONSOLE_1B.PNG", "RESOURCES/pack/TECH_3B.PNG", "RESOURCES/pack/SUPPORT_4A.PNG"], 0, 1)

    while True:
        game.handleEvents()
        game.update(map1)
        renderer.update(map1, game.player_x, game.player_y, game.player_z, game.player_angle)
        game.display(renderer.buffer)

if __name__ == "__main__": # Pour profiler : python3 -m cProfile -s tottime main.py | head -n 35
    main()