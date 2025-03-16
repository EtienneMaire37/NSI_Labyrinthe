import pygame
import math
import sys
# from GAME.defines import * # Ne fonctionne pas car ca duplique les variables
import GAME.defines
from GAME.renderer import normalize_vector2d, Renderer
from GAME.rays import cast_ray
import GAME.map as mp
from GAME.entity import Entity
from GAME.pathfinding import a_star
from GAME.math import lerp
from GAME.item import Item
import random

class Game:
    def __init__(self, _player_x: float, _player_y: float):
        pygame.init()
        pygame.mixer.init(channels = 8) # Jusqu'à 8 sons en meme temps

        pygame.event.set_allowed([pygame.QUIT, pygame.KEYDOWN, pygame.KEYUP, pygame.MOUSEMOTION])
        # pygame.mouse.set_visible(False)
        # pygame.event.set_grab(True)
        # pygame.mouse.set_visible(True)
        # pygame.event.set_grab(False)
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
        self.cam_anim_time = 0

        self.loading = True

        self.mouse_mov = (0, 0)
        self.last_mouse_reset = False

        self.in_menu = 1
        self.action_counter = 0
        self.inventory_counter = 0
        self.click_button = 0
        self.mouse_clicked = False
        self.mouse_released = False

        self.inventory = [None] * GAME.defines.INVENTORY_SIZE

        self.entities = []

        self.jumpscare_sound = [pygame.mixer.Sound(file = f"RESOURCES/sounds/jumpscare{i}.mp3") for i in range(4, 6)]
        # self.step_sound = [pygame.mixer.Sound(file = f"RESOURCES/sounds/step{i}.{["wav", "mp3"][i > 0]}") for i in range(1, 5)]
        self.step_sound = []
        for i in range(4):
            ext = [".wav", ".mp3"]
            self.step_sound.append(pygame.mixer.Sound(file = "RESOURCES/sounds/step" + str(i + 1) + ext[i > 0]))
            self.step_sound[i].set_volume(.2)
        self.walking_timer = 0

        if self.in_menu == 0:
            pygame.mouse.set_visible(False)
            pygame.event.set_grab(True)
        else:
            pygame.mouse.set_visible(True)
            pygame.event.set_grab(False)

    # Gère tous les évènement de la fenêtre chaque frame et arrête le programme si elle est fermée
    def handleEvents(self):
        self.mouse_moved = self.mouse_clicked = self.mouse_released = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)
            if event.type == pygame.MOUSEMOTION:
                if self.in_menu == 0:
                    self.mouse_mov = event.rel
                    if not self.last_mouse_reset:
                        self.mouse_moved = True
                    if math.sqrt((event.pos[0] - GAME.defines.SCREEN_WIDTH / 2)**2 + (event.pos[1] - GAME.defines.SCREEN_HEIGHT / 2)**2) > min(GAME.defines.SCREEN_WIDTH, GAME.defines.SCREEN_HEIGHT) / 2:
                        pygame.mouse.set_pos((GAME.defines.SCREEN_WIDTH / 2, GAME.defines.SCREEN_HEIGHT / 2))
                        self.mouse_moved = True
                        self.last_mouse_reset = True
                    else:
                        self.last_mouse_reset = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.mouse_clicked = True
            if event.type == pygame.MOUSEBUTTONUP:
                self.mouse_released = True

    # Gère les inputs liés au mouvement du personnage
    def handleMovement(self, delta_time: float, keys: list, _map: mp.Map):
        if self.loading:
            return 

        if keys[pygame.K_e]:
            self.action_counter += 1
        else:
            self.action_counter = 0

        if keys[pygame.K_i]:
            self.inventory_counter += 1
        else:
            self.inventory_counter = 0

        if self.action_counter == 1:
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
                    pygame.mouse.set_visible(True)
                    pygame.event.set_grab(False)

                    pygame.mouse.set_pos((GAME.defines.SCREEN_WIDTH / 2, GAME.defines.SCREEN_HEIGHT / 2))
                    self.last_mouse_reset = True
            elif self.in_menu != 1 and self.in_menu != 3 and self.in_menu != 4:
                self.in_menu = 0
                pygame.mouse.set_visible(False)
                pygame.event.set_grab(True)

        if self.inventory_counter == 1:
            if self.in_menu == 0:
                self.in_menu = 5
                pygame.mouse.set_visible(True)
                pygame.event.set_grab(False)
            elif self.in_menu == 5:
                self.in_menu = 0
                pygame.mouse.set_visible(False)
                pygame.event.set_grab(True)

        # if self.in_menu != 0 and self.action_counter != 1:
        if self.in_menu != 0:
            return

        if self.mouse_moved:
            self.player_angle += self.mouse_mov[0] * delta_time * GAME.defines.ROTATION_SPEED / 10

        if keys[pygame.K_LSHIFT]:
            # GAME.defines.MOVE_SPEED = 2.5
            GAME.defines.MOVE_SPEED = lerp(GAME.defines.MOVE_SPEED, 3, 2 * delta_time)
        else:
            GAME.defines.MOVE_SPEED = lerp(GAME.defines.MOVE_SPEED, 2, 2 * delta_time)

        # print(GAME.defines.MOVE_SPEED)

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

    def update(self, renderer, _map: mp.Map):
        deltaTime = self.clock.tick(GAME.defines.MAX_FRAME_RATE) / 1000
        # print(deltaTime)

        if (not self.loading) and deltaTime < .1:
            self.total_time += deltaTime
            self.cam_anim_time += deltaTime * (1 + (GAME.defines.MOVE_SPEED - 2) * 5)

            keys = pygame.key.get_pressed()
            self.handleMovement(deltaTime, keys, _map)

            if self.in_menu != 1 and self.in_menu != 3 and self.in_menu != 4: # Si on n'est pas dans le menu principal ou dans l'écran de game over ou dans les controles
                if keys[pygame.K_q] or keys[pygame.K_d] or keys[pygame.K_z] or keys[pygame.K_s]:
                    self.walking_timer += deltaTime
                threshold = .45 - (GAME.defines.MOVE_SPEED - 2) * .1
                if self.walking_timer > threshold:
                    self.walking_timer = 0
                    self.step_sound[random.randint(0, 3)].play()
                    
                # for entity in self.entities:
                i = 0
                while i < len(self.entities):
                # for i in range(len(self.entities)):
                    # self.update_entity_ai(entity, _map, deltaTime)
                    # entity = self.entities[i]
                    distance_to_entity = math.sqrt((self.player_x - self.entities[i].position[0])**2 + (self.player_y - self.entities[i].position[1])**2)
                    if self.entities[i].hostile:
                        if distance_to_entity < 0.7075: # ~= sqrt(2) / 2
                            self.in_menu = 3    # Game over
                            pygame.mouse.set_visible(True)
                            pygame.event.set_grab(False)
                            self.jumpscare_sound[random.randint(0, 1)].play()

                        self.follow_path(self.entities[i], deltaTime, _map)
                        self.entities[i].walk_sound_timer += deltaTime
                        if self.entities[i].ai_state == "patrol":
                            threshold = GAME.defines.ENTITY_WALK_SOUND_SPEED
                        else:
                            threshold = GAME.defines.ENTITY_RUN_SOUND_SPEED
                        if self.entities[i].walk_sound_timer > threshold:
                            self.entities[i].walk_sound_timer = 0
                            # print("ws")
                            rvol = 1 / (.7 * distance_to_entity)**2 # math.log10(10 / (distance_to_entity * .3)**2)
                            vol = min(1, max(0, rvol))
                            self.entities[i].walk_sound.set_volume(vol)
                            # print(max(0, -2 * math.log10(.3 * distance_to_entity / math.sqrt(10))))
                            if vol > .03:
                                self.entities[i].walk_sound.play()
                        # self.entities[i] = entity
                    else:
                        if distance_to_entity < 0.4:
                            j = 0
                            while self.inventory[j] != None and j < GAME.defines.INVENTORY_SIZE:
                                if self.inventory[j] == None:
                                    self.inventory[j] = self.entities[i].item
                                j += 1
                            self.delete_entity(renderer, i)
                            i -= 1
                    i += 1

        pygame.display.set_caption(GAME.defines.GAME_TITLE + f" | FPS: {int(1 / deltaTime)}")

    def display(self, buffer: list):
        surf = pygame.surfarray.make_surface(buffer * 255).convert()

        if GAME.defines.FULL_RES:
            self.win.blit(surf, (0, 0))
        else:
            surf = pygame.transform.scale(surf, self.win.get_size(), self.win)

        pygame.display.update()

        self.loading = False

    # Faire suivre le chemin (vers le joueur ou aléatoire) à une entité
    def follow_path(self, entity, delta_time, _map):
        if not entity.path:
            return

        target_x = entity.path[0][0] + 0.5
        target_y = entity.path[0][1] + 0.5
        
        dx = target_x - entity.position[0]
        dy = target_y - entity.position[1]
        distance = math.hypot(dx, dy)
        
        if distance < 0.1:
            entity.path.pop(0)
            if not entity.path:
                return
            return self.follow_path(entity, delta_time, _map)
        
        if distance > 0:
            move_dir = (dx / distance, dy / distance)
        else:
            return
        
        if entity.ai_state == "patrol":
            speed = entity.speed
        else:
            speed = entity.run_speed
        new_x = entity.position[0] + move_dir[0] * speed * delta_time
        new_y = entity.position[1] + move_dir[1] * speed * delta_time
        
        grid_x = int(new_x)
        grid_y = int(new_y)
        if _map._map[grid_y * _map.size[0] + grid_x] == 0:
            entity.position = (new_x, new_y, entity.position[2])
        else:
            if _map._map[grid_y * _map.size[0] + int(entity.position[0])] == 0:
                new_y = entity.position[1] + move_dir[1] * entity.speed * delta_time
                if _map._map[int(new_y) * _map.size[0] + int(entity.position[0])] == 0:
                    entity.position = (entity.position[0], new_y, entity.position[2])
            elif _map._map[int(entity.position[1]) * _map.size[0] + grid_x] == 0:
                new_x = entity.position[0] + move_dir[0] * entity.speed * delta_time
                if _map._map[int(entity.position[1]) * _map.size[0] + int(new_x)] == 0:
                    entity.position = (new_x, entity.position[1], entity.position[2])

    def generate_entity_pos(self, map, distance_to_player):
        pos_x = pos_y = 0
        while map._map[int(pos_x) + map.size[0] * int(pos_y)] != 0 or math.sqrt((pos_x - self.player_x)**2 + (pos_y - self.player_y)**2) < distance_to_player or (pos_x == 0 and pos_y == 0):
            pos_x = random.randint(0, map.size[0] - 1)
            pos_y = random.randint(0, map.size[1] - 1)
        return pos_x, pos_y

    # Génère les entités dans le labyrinthe
    def generate_entities(self, renderer, map):
        for i in range(16):
            pos_x, pos_y = self.generate_entity_pos(map, 20)
            # print(pos_x - self.player_x, pos_y - self.player_y)
            monster = Entity(pos_x, pos_y, self.player_z, 1, 1, f"RESOURCES/monsters/no-bg{random.randint(0, 2)}.png", (255, 255, 255), "RESOURCES/sounds/monster-walk.mp3", True)
            renderer.add_entity(monster)
            monster.detection_radius = 7.
            monster.hearing_radius = 4.
            # monster.speed = 3
            # monster.run_speed = 4.7
            # monster.speed = 2.5
            # monster.run_speed = 4 # 3.8
            monster.speed = 2.5
            monster.run_speed = 3
            self.entities.append(monster)

        for i in range(16):
            pos_x, pos_y = self.generate_entity_pos(map, 10)
            items = ["RESOURCES/items/sac.png"]
            item = Entity(pos_x + .5, pos_y + .5, self.player_z - .5, .3, .7, items[random.randint(0, 0)], (0, 0, 0), "", False)
            renderer.add_entity(item)
            self.entities.append(item)

    def delete_entity(self, renderer, index):
        self.entities.pop(index)
        renderer.delete_entity(index)

    # Lance le jeu
    def run(self):
        infoObject = pygame.display.Info()
        infoObject = pygame.display.Info()
        SCREEN_WIDTH = infoObject.current_w
        SCREEN_HEIGHT = infoObject.current_h
        RESOLUTION_X = GAME.defines.RESOLUTION_X
        RESOLUTION_Y = GAME.defines.RESOLUTION_Y
        if GAME.defines.FULL_RES:
            RESOLUTION_X = SCREEN_WIDTH
            RESOLUTION_Y = SCREEN_HEIGHT

        map1 = mp.Map()
        map1.load_from_list(GAME.defines.MAP1, GAME.defines.MAP1_INTERACT, GAME.defines.MAP1_SIZE_X, GAME.defines.MAP1_SIZE_Y,
                            ["RESOURCES/pack/TILE_2C.PNG", "RESOURCES/pack/082.png", "RESOURCES/pack/TECH_1C.PNG", "RESOURCES/pack/TECH_1E.PNG", "RESOURCES/pack/TECH_2F.PNG", "RESOURCES/pack/CONSOLE_1B.PNG", "RESOURCES/pack/TECH_3B.PNG", "RESOURCES/pack/SUPPORT_4A.PNG"], 0, 1)

        renderer = Renderer(RESOLUTION_X, RESOLUTION_Y)
        # for i in range(4096):   # Une entité pour 32x32 blocks | bcp trop pour les performances
        self.generate_entities(renderer, map1)
        # renderer.clean_entities()

        while True:
            self.handleEvents()
            self.update(renderer, map1)
            m_x, m_y =  pygame.mouse.get_pos()
            menu = renderer.update(self.inventory, GAME.defines.MOVE_SPEED, self.click_button, int(m_x * RESOLUTION_X / SCREEN_WIDTH), int(m_y * RESOLUTION_Y / SCREEN_HEIGHT), self.cam_anim_time, self.in_menu, map1, self.player_x, self.player_y, self.player_z, self.player_angle)
            self.display(renderer.buffer)

            if self.mouse_clicked:
                self.click_button = menu
                # print(self.click_button, int(m_x * RESOLUTION_X / SCREEN_WIDTH), int(m_y * RESOLUTION_Y / SCREEN_HEIGHT))
            if self.mouse_released:
                if self.click_button == menu:
                    match self.click_button:
                        case 1:     # Bouton jouer
                            self.in_menu = 0 
                            pygame.mouse.set_visible(False)
                            pygame.event.set_grab(True)
                        case 2:     # Regénérer le labyrinthe
                            # map1._map, map1.interaction_data = GAME.maze.maze_to_map(GAME.defines.MAP1_SIZE_X, GAME.defines.MAP1_SIZE_Y)
                            # renderer.clean_entities()
                            # self.entities = []
                            # self.generate_entities(renderer, map1)
                            GAME.defines.MAP1, GAME.defines.MAP1_INTERACT = GAME.maze.maze_to_map(GAME.defines.MAP1_SIZE_X, GAME.defines.MAP1_SIZE_Y)
                            map1 = mp.Map()
                            map1.load_from_list(GAME.defines.MAP1, GAME.defines.MAP1_INTERACT, GAME.defines.MAP1_SIZE_X, GAME.defines.MAP1_SIZE_Y,
                                                ["RESOURCES/pack/TILE_2C.PNG", "RESOURCES/pack/082.png", "RESOURCES/pack/TECH_1C.PNG", "RESOURCES/pack/TECH_1E.PNG", "RESOURCES/pack/TECH_2F.PNG", "RESOURCES/pack/CONSOLE_1B.PNG", "RESOURCES/pack/TECH_3B.PNG", "RESOURCES/pack/SUPPORT_4A.PNG"], 0, 1)
                            renderer.clean_entities()
                            self.entities = []
                            self.generate_entities(renderer, map1)
                        case 3:     # Rejouer
                            GAME.defines.MAP1, GAME.defines.MAP1_INTERACT = GAME.maze.maze_to_map(GAME.defines.MAP1_SIZE_X, GAME.defines.MAP1_SIZE_Y)
                            map1 = mp.Map()
                            map1.load_from_list(GAME.defines.MAP1, GAME.defines.MAP1_INTERACT, GAME.defines.MAP1_SIZE_X, GAME.defines.MAP1_SIZE_Y,
                                                ["RESOURCES/pack/TILE_2C.PNG", "RESOURCES/pack/082.png", "RESOURCES/pack/TECH_1C.PNG", "RESOURCES/pack/TECH_1E.PNG", "RESOURCES/pack/TECH_2F.PNG", "RESOURCES/pack/CONSOLE_1B.PNG", "RESOURCES/pack/TECH_3B.PNG", "RESOURCES/pack/SUPPORT_4A.PNG"], 0, 1)
                            renderer.clean_entities()
                            self.entities = []
                            self.player_x, self.player_y = (GAME.defines.MAP1_SIZE_X / 2, GAME.defines.MAP1_SIZE_Y / 2 + 1)
                            self.generate_entities(renderer, map1)
                            self.in_menu = 1
                            self.player_angle = math.pi / 2
                            GAME.defines.MOVE_SPEED = 2
                        case 4:     # Montre les controles
                            self.in_menu = 4
                        case 5:     # Retour (controles)
                            self.in_menu = 1
                        case _:
                            pass
                self.click_button = 0
            for i in range(min(len(renderer.entities), len(self.entities))):
                renderer.entities[i]['position'] = self.entities[i].position
                if self.entities[i].hostile:
                    # renderer.entities[i] = self.entities[i]
                    self.entities[i].position = (self.entities[i].position[0] + .5, self.entities[i].position[1] + .5, self.entities[i].position[2])
                    # print(renderer.entities[i]['position'])

                    entity = self.entities[i]
                    distance = math.sqrt((entity.position[0] - self.player_x)**2 + (entity.position[1] - self.player_y)**2)
                    has_los = False
                    if distance < entity.detection_radius:
                        dx = self.player_x - entity.position[0]
                        dy = self.player_y - entity.position[1]
                        if dx == 0:
                            dx = 0.01
                        if dy == 0:
                            dy = 0.01
                        dist, hit, _, _, _, _, _ = cast_ray(dx, dy, entity.position[0], entity.position[1], 0, map1._map, map1.size)
                        has_los = dist >= distance - 1
                    pos_x, pos_y = (int(entity.position[0] - .5), int(entity.position[1] - .5))
                    if entity.ai_state == "chase":
                        if has_los or distance < entity.hearing_radius:
                            if len(entity.path) != 0:
                                next_tile = entity.path[0]
                                entity.path = [next_tile] + a_star((next_tile[0], next_tile[1]), (int(self.player_x), int(self.player_y)), map1._map, map1.size)
                            else:
                                entity.path = a_star((pos_x, pos_y), (int(self.player_x), int(self.player_y)), map1._map, map1.size)
                        else:
                            if len(entity.path) <= 1:
                                entity.ai_state = "patrol"
                    else:
                        if has_los or distance < entity.hearing_radius:
                            entity.ai_state = "chase"
                        else:
                            if len(entity.path) == 0:
                                next_tile = (int(entity.position[0] - .5), int(entity.position[1] - .5))
                                new_next_tile = (next_tile[0] + random.randint(-1, 1), next_tile[1] + random.randint(-1, 1))
                                while map1._map[int(new_next_tile[0]) + int(new_next_tile[1]) * map1.size[0]] != 0:
                                    new_next_tile = (next_tile[0] + random.randint(-1, 1), next_tile[1] + random.randint(-1, 1))
                                entity.path = [next_tile] + [new_next_tile]

                    self.entities[i].position = (self.entities[i].position[0] - .5, self.entities[i].position[1] - .5, self.entities[i].position[2])