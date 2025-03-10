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
    maze = Labyrinthe(sz_x, sz_y)
    maze.generer()
    map = [' '] * (sz_x * sz_y)
    for i in range(sz_y):
        for j in range(sz_x):
            if i == 0 or j == 0 or i == sz_y - 1 or j == sz_x - 1:
                map[j + sz_x * i] = '1'
    return map