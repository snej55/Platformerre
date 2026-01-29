import pygame, math

from data.e.scripts.bip import BLASER_CHUNK_SIZE, TILE_SIZE

class BLaserManager:
    def __init__(self, app):
        self.chunks = {}
        self.chunk_size = BLASER_CHUNK_SIZE

    def get_chunk(self, pos):
        loc = str(math.floor(pos[0] / self.chunk_size[0] / TILE_SIZE)) + ';' + str(math.floor(pos[1] / self.chunk_size[1] / TILE_SIZE))
        if not (loc in self.chunks):
            self.chunks[loc] = []
        return self.chunks[loc]

    def load_chunks(self, items):
        '''
        items: list[Object]
        object most have attr pos
        '''
        for item in items:
            loc = str(math.floor(item.pos[0] / TILE_SIZE / self.chunk_size[0])) + ';' + str(math.floor(item.pos[1] / TILE_SIZE / self.chunk_size[1]))
            if not (loc in self.chunks):
                self.chunks[loc] = []
            self.chunks[loc].append(item)
        return self.chunks

    def update(self, surf, scroll):
        for y in range(math.ceil(surf.get_height() / (self.chunk_size[1] * TILE_SIZE)) + 2):
            for x in range(math.ceil(surf.get_width() / (self.chunk_size[0] * TILE_SIZE)) + 2):
                target_x = x - 2 + math.ceil(int(scroll[0]) / (self.chunk_size[0] * TILE_SIZE))
                target_y = y - 2 + math.ceil(int(scroll[1]) / (self.chunk_size[1] * TILE_SIZE))
                target_quad = f'{target_x};{target_y}'
                if target_quad in self.chunks:
                    for i, item in sorted(enumerate(self.chunks[target_quad]), reverse=True):
                        kill = item.update()
                        item.draw(surf, scroll)
                        if kill:
                            item.die()
                            self.chunks[target_quad].pop(i)
                            del item
                        elif not self.get_chunk(item.pos) is self.chunks[target_quad]:
                            self.get_chunk(item.pos).append(self.chunks[target_quad].pop(i))


class BLaser:
    def __init__(self, app, angle, speed, color, pos):
        self.app = app
        self.color = color
        self.angle = angle
        self.speed = speed
        self.pos = pygame.Vector2(pos)
        self.vel = [math.cos(angle) * speed, math.sin(-angle) * speed]
        if self.color in self.app.assets['game']['lasers']:
            self.img = self.app.assets['game']['lasers'][self.color]
        else: self.img = self.app.assets['game']['lasers'][self.app.assets['game']['lasers'].keys()[0]]
        self.app.blaser_manager.load_chunks([self])
    
    def die(self):
        pass
    
    def update(self):
        kill = 0
        self.pos[0] += self.vel[0] * self.app.dt
        self.pos[1] += self.vel[1] * self.app.dt
        collide_pos = [self.pos[0] + math.cos(self.angle) * self.img.get_width() * 0.5, self.pos[1] + math.sin(self.angle) * self.img.get_width() * 0.5]
        if self.app.world.tile_map.physics_map.solid_check(collide_pos):
            kill = 1
        return kill

    def draw(self, surf, scroll):
        img_copy = pygame.transform.rotate(self.img, math.degrees(self.angle))
        surf.blit(img_copy, (self.pos[0] + int(self.img.get_width() / 2) - int(img_copy.get_width() / 2) - scroll[0], self.pos[1] + int(self.img.get_height() / 2) - int(img_copy.get_height() / 2) - scroll[1]))

class Blaster:
    def __init__(self, app, img, pos, target, color):
        self.pos = pygame.Vector2(pos)
        self.target = target
        self.color = color
        self.app = app
        self.img = img
        self.flipped = False
    
    def fire(self, angle=0, speed=5):
        return BLaser(self.app, angle, speed, self.color, self.pos)
    
    def draw(self, surf, scroll, offset=(0, 0)):
        surf.blit(pygame.transform.flip(self.img, self.flipped, False), (self.pos[0] - scroll[0] + offset[0], self.pos[1] - scroll[1] + offset[1]))