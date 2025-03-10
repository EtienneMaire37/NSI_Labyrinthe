import pygame
import math
import sys
from GAME.defines import *
from GAME.renderer import normalize_vector2d
from GAME.rays import ray_entities_intersection
import GAME.map as mp

class Game:
    def __init__(self, _player_x: float, _player_y: float):
        pygame.init()

        pygame.event.set_allowed([pygame.QUIT, pygame.KEYDOWN, pygame.KEYUP, pygame.MOUSEMOTION])
        pygame.mouse.set_visible(False)
        pygame.event.set_grab(True)
        infoObject = pygame.display.Info()
        SCREEN_WIDTH = infoObject.current_w
        SCREEN_HEIGHT = infoObject.current_h
        self.win = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        flags = pygame.FULLSCREEN | pygame.DOUBLEBUF
        pygame.display.set_caption("")
        self.clock = pygame.time.Clock()

        # Player variables
        self.player_x = _player_x
        self.player_y = _player_y
        self.player_z = 0
        self.player_angle = 0
        self.mouse_mov = (0, 0)
        self.mouse_moved = False
        self.total_time = 0
        self.total_move_time = 0

        self.loading = True
        self.loadingTimer = 0

        self.mouse_mov = (0, 0)
        self.mouse_moved = False

    # Gère tous les évènement de la fenêtre chaque frame et arrête le programme si elle est fermée
    def handleEvents(self):
        self.mouse_moved = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)
            if event.type == pygame.MOUSEMOTION:
                self.mouse_mov = event.rel
                self.mouse_moved = True
                if math.sqrt((event.pos[0] - SCREEN_WIDTH / 2)**2 + (event.pos[1] - SCREEN_HEIGHT / 2)**2) > min(SCREEN_WIDTH, SCREEN_HEIGHT) / 2:
                    pygame.mouse.set_pos((SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2))


    # Gère les inputs liés au mouvement du personnage
    def handleMovement(self, delta_time: float, keys: list, _map: mp.Map):
        if self.loadingTimer < LOAD_TIME:
            return

        if self.mouse_moved:
            self.player_angle += self.mouse_mov[0] * delta_time * ROTATION_SPEED / 10

        # Handle ZSDQ movement
        if keys[pygame.K_LEFT]:
            self.player_angle -= ROTATION_SPEED * delta_time
        if keys[pygame.K_RIGHT]:
            self.player_angle += ROTATION_SPEED * delta_time

        if keys[pygame.K_z]:
            self.player_x += -1 * math.sin(self.player_angle) * MOVE_SPEED * delta_time
            if _map._map[_map.size[0] * int(self.player_y) + int(self.player_x)] != ' ':
                self.player_x -= -1 * math.sin(self.player_angle) * MOVE_SPEED * delta_time
            self.player_y += math.cos(self.player_angle) * MOVE_SPEED * delta_time
            if _map._map[_map.size[0] * int(self.player_y) + int(self.player_x)] != ' ':
                self.player_y -= math.cos(self.player_angle) * MOVE_SPEED * delta_time
        if keys[pygame.K_s]:
            self.player_x -= -1 * math.sin(self.player_angle) * MOVE_SPEED * delta_time
            if _map._map[_map.size[0] * int(self.player_y) + int(self.player_x)] != ' ':
                self.player_x += -1 * math.sin(self.player_angle) * MOVE_SPEED * delta_time
            self.player_y -= math.cos(self.player_angle) * MOVE_SPEED * delta_time
            if _map._map[_map.size[0] * int(self.player_y) + int(self.player_x)] != ' ':
                self.player_y += math.cos(self.player_angle) * MOVE_SPEED * delta_time
        if keys[pygame.K_d]:
            self.player_x += -1 * math.sin(self.player_angle + math.pi / 2) * MOVE_SPEED * delta_time
            if _map._map[_map.size[0] * int(self.player_y) + int(self.player_x)] != ' ':
                self.player_x -= -1 * math.sin(self.player_angle + math.pi / 2) * MOVE_SPEED * delta_time
            self.player_y += math.cos(self.player_angle + math.pi / 2) * MOVE_SPEED * delta_time
            if _map._map[_map.size[0] * int(self.player_y) + int(self.player_x)] != ' ':
                self.player_y -= math.cos(self.player_angle + math.pi / 2) * MOVE_SPEED * delta_time
        if keys[pygame.K_q]:
            self.player_x -= -1 * math.sin(self.player_angle + math.pi / 2) * MOVE_SPEED * delta_time
            if _map._map[_map.size[0] * int(self.player_y) + int(self.player_x)] != ' ':
                self.player_x += -1 * math.sin(self.player_angle + math.pi / 2) * MOVE_SPEED * delta_time
            self.player_y -= math.cos(self.player_angle + math.pi / 2) * MOVE_SPEED * delta_time
            if _map._map[_map.size[0] * int(self.player_y) + int(self.player_x)] != ' ':
                self.player_y += math.cos(self.player_angle + math.pi / 2) * MOVE_SPEED * delta_time


    def _applyMovement(self, a, _a, _map):
        self.player_x += _a[0]
        if _map._map[_map.size[0] * int(self.player_y) + int(self.player_x)] == ' ':
            a[0] += _a[0]
        self.player_x -= _a[0]
        self.player_y += _a[1]
        if _map._map[_map.size[0] * int(self.player_y) + int(self.player_x)] == ' ':
            a[1] += _a[1]
        self.player_y -= _a[1]

    def update(self, _map: mp.Map):
        deltaTime = self.clock.tick(MAX_FRAME_RATE) / 1000

        if not self.loading:
            self.total_time += deltaTime
            self.loadingTimer += deltaTime

            keys = pygame.key.get_pressed()
            self.handleMovement(deltaTime, keys, _map)
        pygame.display.set_caption(f"Errorbytes | FPS: {int(1 / deltaTime)}")

    def display(self, buffer: list):
        surf = pygame.surfarray.make_surface(buffer * 255).convert()

        if FULL_RES:
            self.win.blit(surf, (0, 0))
        else:
            surf = pygame.transform.scale(surf, self.win.get_size(), self.win)

        pygame.display.update()

        self.loading = False