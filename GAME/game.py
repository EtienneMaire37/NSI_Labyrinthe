import pygame
import math
import sys
# from GAME.defines import * # Ne fonctionne pas car ca duplique les variables
import GAME.defines
from GAME.renderer import normalize_vector2d
from GAME.rays import cast_ray
import GAME.map as mp

class Game:
    def __init__(self, _player_x: float, _player_y: float):
        pygame.init()

        pygame.event.set_allowed([pygame.QUIT, pygame.KEYDOWN, pygame.KEYUP, pygame.MOUSEMOTION])
        pygame.mouse.set_visible(False)
        pygame.event.set_grab(True)
        infoObject = pygame.display.Info()
        GAME.defines.SCREEN_WIDTH = infoObject.current_w
        GAME.defines.SCREEN_HEIGHT = infoObject.current_h
        if GAME.defines.FULL_RES:
            GAME.defines.RESOLUTION_X = GAME.defines.SCREEN_WIDTH
            GAME.defines.RESOLUTION_Y = GAME.defines.SCREEN_HEIGHT
        self.win = pygame.display.set_mode((GAME.defines.SCREEN_WIDTH, GAME.defines.SCREEN_HEIGHT))
        flags = pygame.FULLSCREEN | pygame.DOUBLEBUF
        pygame.display.set_mode((0, 0), flags)
        pygame.display.set_caption(GAME.defines.GAME_TITLE)
        self.clock = pygame.time.Clock()

        # Player variables
        self.player_x = _player_x
        self.player_y = _player_y
        self.player_z = 0
        self.player_angle = math.pi / 2
        self.mouse_mov = (0, 0)
        self.mouse_moved = False
        self.total_time = 0
        self.total_move_time = 0

        self.loading = True

        self.mouse_mov = (0, 0)
        self.last_mouse_reset = False

        self.in_menu = 0
        self.action_pressed = 0

    # Gère tous les évènement de la fenêtre chaque frame et arrête le programme si elle est fermée
    def handleEvents(self):
        self.mouse_moved = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)
            if event.type == pygame.MOUSEMOTION:
                self.mouse_mov = event.rel
                if not self.last_mouse_reset:
                    self.mouse_moved = True
                if math.sqrt((event.pos[0] - GAME.defines.SCREEN_WIDTH / 2)**2 + (event.pos[1] - GAME.defines.SCREEN_HEIGHT / 2)**2) > min(GAME.defines.SCREEN_WIDTH, GAME.defines.SCREEN_HEIGHT) / 2:
                    pygame.mouse.set_pos((GAME.defines.SCREEN_WIDTH / 2, GAME.defines.SCREEN_HEIGHT / 2))
                    self.mouse_moved = True
                    self.last_mouse_reset = True
                else:
                    self.last_mouse_reset = False

    # Gère les inputs liés au mouvement du personnage
    def handleMovement(self, delta_time: float, keys: list, _map: mp.Map):
        if self.loading:
            return 

        if keys[pygame.K_e]:
            self.action_pressed += 1
        else:
            self.action_pressed = 0

        if self.in_menu != 0 and self.action_pressed != 1:
            return

        if self.mouse_moved:
            self.player_angle += self.mouse_mov[0] * delta_time * GAME.defines.ROTATION_SPEED / 10

        if keys[pygame.K_z]:
            self.player_x += -1 * math.sin(self.player_angle) * GAME.defines.MOVE_SPEED * delta_time
            if _map._map[_map.size[0] * int(self.player_y) + int(self.player_x)] != 0:
                self.player_x -= -1 * math.sin(self.player_angle) * GAME.defines.MOVE_SPEED * delta_time
            self.player_y += math.cos(self.player_angle) * GAME.defines.MOVE_SPEED * delta_time
            if _map._map[_map.size[0] * int(self.player_y) + int(self.player_x)] != 0:
                self.player_y -= math.cos(self.player_angle) * GAME.defines.MOVE_SPEED * delta_time
        if keys[pygame.K_s]:
            self.player_x -= -1 * math.sin(self.player_angle) * GAME.defines.MOVE_SPEED * delta_time
            if _map._map[_map.size[0] * int(self.player_y) + int(self.player_x)] != 0:
                self.player_x += -1 * math.sin(self.player_angle) * GAME.defines.MOVE_SPEED * delta_time
            self.player_y -= math.cos(self.player_angle) * GAME.defines.MOVE_SPEED * delta_time
            if _map._map[_map.size[0] * int(self.player_y) + int(self.player_x)] != 0:
                self.player_y += math.cos(self.player_angle) * GAME.defines.MOVE_SPEED * delta_time
        if keys[pygame.K_d]:
            self.player_x += -1 * math.sin(self.player_angle + math.pi / 2) * GAME.defines.MOVE_SPEED * delta_time
            if _map._map[_map.size[0] * int(self.player_y) + int(self.player_x)] != 0:
                self.player_x -= -1 * math.sin(self.player_angle + math.pi / 2) * GAME.defines.MOVE_SPEED * delta_time
            self.player_y += math.cos(self.player_angle + math.pi / 2) * GAME.defines.MOVE_SPEED * delta_time
            if _map._map[_map.size[0] * int(self.player_y) + int(self.player_x)] != 0:
                self.player_y -= math.cos(self.player_angle + math.pi / 2) * GAME.defines.MOVE_SPEED * delta_time
        if keys[pygame.K_q]:
            self.player_x -= -1 * math.sin(self.player_angle + math.pi / 2) * GAME.defines.MOVE_SPEED * delta_time
            if _map._map[_map.size[0] * int(self.player_y) + int(self.player_x)] != 0:
                self.player_x += -1 * math.sin(self.player_angle + math.pi / 2) * GAME.defines.MOVE_SPEED * delta_time
            self.player_y -= math.cos(self.player_angle + math.pi / 2) * GAME.defines.MOVE_SPEED * delta_time
            if _map._map[_map.size[0] * int(self.player_y) + int(self.player_x)] != 0:
                self.player_y += math.cos(self.player_angle + math.pi / 2) * GAME.defines.MOVE_SPEED * delta_time

        if self.action_pressed == 1:
            if self.in_menu == 0:
                dX = -math.sin(self.player_angle) 
                dY = math.cos(self.player_angle) 
                if dX == 0:
                    dX = 0.001
                if dY == 0:
                    dY = 0.001
                wall_dist, hit, map_x, map_y, last_offset, step_x, step_y = cast_ray(dX, dY, self.player_x, self.player_y, self.player_angle, _map._map, _map.size)
                wall_dist += 0.01
                pos_x, pos_y = wall_dist * dX + self.player_x, wall_dist * dY + self.player_y
                menu = _map.interaction_data[math.floor(pos_x) + math.floor(pos_y) * _map.size[0]]
                if hit and menu != 0 and wall_dist < GAME.defines.MAX_PLAYER_INTERACTION_RANGE:
                    self.in_menu = menu
            else:
                self.in_menu = 0

    def _applyMovement(self, a, _a, _map):
        self.player_x += _a[0]
        if _map._map[_map.size[0] * int(self.player_y) + int(self.player_x)] == 0:
            a[0] += _a[0]
        self.player_x -= _a[0]
        self.player_y += _a[1]
        if _map._map[_map.size[0] * int(self.player_y) + int(self.player_x)] == 0:
            a[1] += _a[1]
        self.player_y -= _a[1]

    def update(self, _map: mp.Map):
        deltaTime = self.clock.tick(GAME.defines.MAX_FRAME_RATE) / 1000

        if not self.loading:
            self.total_time += deltaTime

            keys = pygame.key.get_pressed()
            self.handleMovement(deltaTime, keys, _map)
        pygame.display.set_caption(GAME.defines.GAME_TITLE + f"FPS: {int(1 / deltaTime)}")

    def display(self, buffer: list):
        surf = pygame.surfarray.make_surface(buffer * 255).convert()

        if GAME.defines.FULL_RES:
            self.win.blit(surf, (0, 0))
        else:
            surf = pygame.transform.scale(surf, self.win.get_size(), self.win)

        pygame.display.update()

        self.loading = False