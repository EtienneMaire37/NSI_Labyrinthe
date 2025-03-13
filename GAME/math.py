import math
from numba import njit

# Normalise un vecteur en deux dimensions sous la forme d'un tuple (x, y)
@njit(fastmath = True, cache = True)
def normalize_vector2d(vec: tuple):
    length = math.sqrt(vec[0]**2 + vec[1]**2)
    # assert length != 0, "La longueur du vecteur ne doit pas etre 0"
    if length == 0:
        return (float(0), float(0))
    return (vec[0] / length, vec[1] / length)

# Normalise un vecteur en trois dimensions sous la forme d'un tuple (x, y, z)
@njit(fastmath = True, cache = True)
def normalize_vector3d(vec: tuple):
    length = math.sqrt(vec[0]**2 + vec[1]**2 + vec[2]**2)
    # assert length != 0, "La longueur du vecteur ne doit pas etre 0"
    if length == 0:
        return (float(0), float(0), float(0))
    return (vec[0] / length, vec[1] / length, vec[2] / length)

# Retoune le produit scalaire entre deux vecteurs sous forme de tuples
@njit(fastmath = True, cache = True)
def dot_2d(u: tuple, v: tuple):
    return u[0] * v[0] + u[1] * v[1]

# Retoune le produit scalaire entre deux vecteurs sous forme de tuples
@njit(fastmath = True, cache = True)
def dot_3d(u: tuple, v: tuple):
    return u[0] * v[0] + u[1] * v[1] + u[2] * v[2]

@njit(fastmath = True, cache = True)
def lerp(a: float, b: float, t: float):
    return (1 - t) * a + t * b
