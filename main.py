from GAME.game import Game
import GAME.defines

def main():
    game = Game(GAME.defines.MAP1_SIZE_X / 2, GAME.defines.MAP1_SIZE_Y / 2 + 1)
    game.run()

if __name__ == "__main__": # Pour profiler : python3 -m cProfile -s tottime main.py | head -n 35
    main()