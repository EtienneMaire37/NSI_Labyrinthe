from random import randint, choice
from GAME.pile import Pile
from GAME.maze import *

class Case:
    def __init__(self):
        self.wallS = self.wallW = True
        self.vue = False

class Labyrinthe:
    def __init__(self, largeur, hauteur):
        self.largeur = largeur
        self.hauteur = hauteur
        self.laby = [[Case() for j in range(self.hauteur)] for i in range(self.largeur)]

    def __directions_possibles(self, i, j):
        directions = []
        if 0 <= j < self.hauteur - 1 and 0 <= i < self.largeur:
            if not self.laby[i][j + 1].vue:
                directions.append('S')
        if 1 <= j < self.hauteur + 1 and 0 <= i < self.largeur:
            if not self.laby[i][j - 1].vue:
                directions.append('N')

        if 0 <= i < self.largeur - 1 and 0 <= j < self.hauteur:
            if not self.laby[i + 1][j].vue:
                directions.append('E')
        if 1 <= i < self.largeur + 1 and 0 <= j < self.hauteur:
            if not self.laby[i - 1][j].vue:
                directions.append('W')
        return directions

    def __abattre_mur(self, i, j, dir, pile):
        if dir == 'S':
            self.laby[i][j].wallS = False
            # self.laby[i][j + 1].murN = False
            self.laby[i][j + 1].vue = True
            pile.empiler((i, j + 1))
        if dir == 'N':
            self.laby[i][j - 1].wallS = False
            self.laby[i][j - 1].vue = True
            pile.empiler((i, j - 1))
        if dir == 'W':
            self.laby[i][j].wallW = False
            self.laby[i - 1][j].vue = True
            pile.empiler((i - 1, j))
        if dir == 'E':
            self.laby[i + 1][j].wallW = False
            self.laby[i + 1][j].vue = True
            pile.empiler((i + 1, j))

    def generer(self):
        x = randint(0, self.largeur - 1)
        y = randint(0, self.hauteur - 1)
        self.laby[x][y].vue = True
        pile = Pile()
        pile.empiler((x, y))

        while not pile.est_vide():
            dp = self.__directions_possibles(x, y)
            if len(dp) == 0:
                (x, y) = pile.depiler()
            else:
                self.__abattre_mur(x, y, dp[randint(0, len(dp) - 1)], pile)
                (x, y) = pile.sommet()

def maze_to_map(sz_x: int, sz_y: int):
    mz_sz_x = sz_x // 2
    mz_sz_y = sz_y // 2
    maze = Labyrinthe(mz_sz_x, mz_sz_y)
    maze.generer()
    map_grid = [' '] * (sz_x * sz_y)

    for i in range(mz_sz_y - 2):
        for j in range(mz_sz_x - 2):
            y_cell = i + 1
            x_cell = j + 1
            cell = maze.laby[y_cell][x_cell]
            if cell.wallW:
                pos = (x_cell + y_cell * sz_x) * 2 - 1
                map_grid[pos] = '1'
            if cell.wallS:
                pos = (x_cell + y_cell * sz_x) * 2 + sz_x
                map_grid[pos] = '1'
            if cell.wallW and cell.wallS:
                pos = (x_cell + y_cell * sz_x) * 2 + sz_x - 1
                map_grid[pos] = '1'

    for y in range(sz_y):
        for x in range(sz_x):
            if x == 0 or x == sz_x - 1 or y == 0 or y == sz_y - 1:
                map_grid[x + y * sz_x] = '1'

    map_grid[sz_x // 2 + sz_x * sz_y // 2] = ' '
    map_grid[sz_x // 2 + sz_x * sz_y // 2 + 1] = ' '
    map_grid[sz_x // 2 + sz_x * sz_y // 2 + sz_x] = ' '
    map_grid[sz_x // 2 + sz_x * sz_y // 2 + sz_x + 1] = ' '

    # for i in range(sz_y):
    #     print(map_grid[i * sz_x:i * sz_x + sz_x])
    return map_grid