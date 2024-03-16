from ..tools.utils import key, load_key
from ..bip import *

class PathFinder:
    def __init__(self, app):
        self.app = app
        self.graph = {}
        self.physics_map = self.app.world.tile_map.physics_map
        self.tile_map = dict(self.app.world.tile_map.physics_map.tile_map)
        self.gen_map()
        self.connect_points()
    
    def gen_path(self):
        pass # vector node based pathfinding stuff here...
    
    def connect_points(self, jump_height=2, jump_distance=2):
        points = list(self.graph)
        for i, loc in enumerate(points):
            point = self.graph[loc][0]
            close_right = -1
            close_left_drop = -1
            close_right_drop = -1
            no_bi_join = []
            pos = list(loc)
            mode = self.cell_type(pos, above=True)
            for j, nloc in enumerate(self.graph):
                if nloc != loc:
                    spos = list(nloc)
                    if mode[1] == 0 and abs(spos[1] - pos[1]) < TILE_SIZE * 0.25 and spos[0] > pos[0]:
                        if (close_right < 0 or spos[0] < points[i][0]) and close_right != i:
                            if not (close_right == i):
                                close_right = j
                    if mode[0] == -1:
                        if abs(spos[0] - (pos[0] - TILE_SIZE)) < TILE_SIZE * 0.25 and spos[1] > pos[1]:
                            if (close_left_drop < 0 or spos[0] < points[i][0]) and close_left_drop != i:
                                close_left_drop = j
                        if spos[1] >= pos[1] - (TILE_SIZE * jump_height) and spos[1] <= pos[1] and spos[0] > pos[0] - (TILE_SIZE * (jump_distance + 2)) and spos[0] < pos[0] and self.cell_type(spos, True)[1] == -1:
                            if not points[j] in self.graph[loc][0]:
                                self.graph[loc][0].append(points[j])
                    if mode[1] == -1:
                        if abs(spos[0] - (pos[0] + TILE_SIZE)) < TILE_SIZE * 0.25 and spos[1] > pos[1]:
                            if (close_right_drop < 0 or spos[0] < points[i][0]) and close_right_drop != i:
                                close_right_drop = j
                        if spos[1] >= pos[1] - (TILE_SIZE * jump_height) and spos[1] <= pos[1] and spos[0] < pos[0] + (TILE_SIZE * (jump_distance + 2)) and spos[0] > pos[0] and self.cell_type(spos, True)[0] == -1:
                            if not points[j] in self.graph[loc][0]:
                                self.graph[loc][0].append(points[j])

            if close_right > 0:
                if not points[close_right] in self.graph[loc][0]:
                    self.graph[loc][0].append(points[close_right])
            if close_left_drop > 0:
                if not points[close_left_drop] in self.graph[loc][0]:
                    if points[close_left_drop][1] <= pos[1] + TILE_SIZE * jump_height:
                        self.graph[loc][0].append(points[close_left_drop])
                    else:
                        self.graph[loc][1].append(points[close_left_drop])
            if close_right_drop > 0:
                if not points[close_right_drop] in self.graph[loc][0]:
                    if points[close_right_drop][1] <= pos[1] + TILE_SIZE * jump_height:
                        self.graph[loc][0].append(points[close_right_drop])
                    else:
                        self.graph[loc][1].append(points[close_right_drop])
    
    def cell_type(self, pos, above=False):
        pos = list(pos)
        if above:
            pos[1] += TILE_SIZE
        if self.physics_map.block_check([pos[0], pos[1] - TILE_SIZE]):
            return None
        results = [0, 0]
        if self.physics_map.block_check([pos[0] - TILE_SIZE, pos[1] - TILE_SIZE]):
            results[0] = 1
        elif not self.physics_map.block_check([pos[0] - TILE_SIZE, pos[1]]):
            results[0] = -1
        if self.physics_map.block_check([pos[0] + TILE_SIZE, pos[1] - TILE_SIZE]):
            results[1] = 1
        elif not self.physics_map.block_check([pos[0] + TILE_SIZE, pos[1]]):
            results[1] = -1
        return list(results)
    
    def create_point(self, pos):
        above = [pos[0], pos[1] - TILE_SIZE]
        cell_pos = [above[0] + TILE_SIZE * 0.5, above[1] + TILE_SIZE * 0.5]
        if not (tuple(cell_pos) in self.graph):
            self.graph[tuple(cell_pos)] = [[], []]
    
    def gen_map(self):
        for loc in self.tile_map:
            pos = list(self.tile_map[loc].pos)
            mode = self.cell_type(pos)
            if mode:
                if mode != [0, 0]:
                    self.create_point(pos)
                    if mode[0] == -1:
                        cell = [pos[0] - TILE_SIZE, pos[1]]
                        i = TILE_SIZE * 0.25
                        while i < TILE_SIZE * 20:
                            collidepoint = [cell[0], cell[1] + i]
                            i += TILE_SIZE * 0.25
                            if self.physics_map.block_check(collidepoint):
                                i = TILE_SIZE * 20 + 1
                        self.create_point(collidepoint)
                    elif mode[1] == -1:
                        cell = [pos[0] + TILE_SIZE, pos[1]]
                        i = TILE_SIZE * 0.25
                        while i < TILE_SIZE * 20:
                            collidepoint = [cell[0], cell[1] + i]
                            i += TILE_SIZE * 0.25
                            if self.physics_map.block_check(collidepoint):
                                i = TILE_SIZE * 20 + 1
                        self.create_point(collidepoint)
    
    def draw(self, surf, scroll):
        for loc in self.graph:
            pos = tuple(loc)
            pygame.draw.circle(surf, (255, 255, 255), (pos[0] - scroll[0], pos[1] - scroll[1]), 1)
            points = [(pos[0] - scroll[0], pos[1] - scroll[1]), *[(p[0] - scroll[0], p[1] - scroll[1]) for p in self.graph[loc][0]]]
            for i, p in enumerate(points):
                pygame.draw.line(surf, (255, 0, 0), p, (pos[0] - scroll[0], pos[1] - scroll[1]), 1)
            points = [(pos[0] - scroll[0], pos[1] - scroll[1]), *[(p[0] - scroll[0], p[1] - scroll[1]) for p in self.graph[loc][1]]]
            for i, p in enumerate(points):
                pygame.draw.line(surf, (255, 200, 0), p, (pos[0] - scroll[0], pos[1] - scroll[1]), 1)