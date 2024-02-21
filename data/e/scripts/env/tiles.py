import pygame, json, math, random

from ..gfx.particles import Particle
from .chunks import TileChunker, Rects
from .grass import GrassManager
from ..bip import *
from .leaf_loader import LeafSpawnLoader

class Tile:
    def __init__(self, pos, dimensions, rect_offset, mode: str, variant: int, img: pygame.Surface, key=None, grid=False, render_scale=1.0):
        self.pos = pygame.Vector2(pos) / render_scale
        if grid:
            self.pos *= TILE_SIZE
        self.grid = grid
        self.dimensions = pygame.Vector2(dimensions) / render_scale
        self.rect = pygame.Rect(self.pos.x + rect_offset[0] / render_scale, self.pos.y + rect_offset[1] / render_scale, self.dimensions.x, self.dimensions.y)
        self.mode = mode
        self.variant = variant
        self.img = img
        self.key = key
    
    def copy(self):
        tile = Tile(self.pos, self.dimensions, (0, 0), self.mode, self.variant, self.img)
        tile.__dict__ = dict(self.__dict__)
        return tile

    def draw(self, surf, scroll): # alpha
        surf.blit(self.img, (self.pos.x - scroll.x, self.pos.y - scroll.y))

class TileMap:
    def __init__(self, app):
        self.app = app
        self.layers = []
        self.physics_map = PhysicsTileMap(app, {})
        self.leaf_spawners = None
        self.grass_map = {}
    
    def load_leaves(self, path):
        loader = LeafSpawnLoader(self.app, path)
        self.leaf_spawners = Rects(loader.rects, [10, 10])
    
    def save(self, path):
        with open(path, 'w') as f:
            json.dump({'layers': [layer.save() for layer in self.layers], 'physics': self.physics_map.save(self.physics_map.tile_map)}, f)
            f.close()
    
    def load(self, path, mode='game'):
        f = open(path, 'r')
        map_data = json.load(f)
        f.close()
        self.grass_map = {}
        for i, layer in enumerate(map_data['layers']):
            self.layers.append(Layer(self, layer, self.app, mode=mode, index=i))
        self.physics_map = PhysicsTileMap(self.app, map_data['physics'])
        if mode == 'game':
            self.grass_manager = GrassManager(self.app, self.app.assets['game']['gras'])
            self.grass_manager.load(self.grass_map, 8, 2)
    
    def extract(self, id_pairs, keep=False):
        matches = []
        for layer in self.layers:
            matches.extend(layer.extract(id_pairs, keep))
        return matches
    
    def draw_decor(self, surf, scroll):
        for layer in self.layers:
            layer.draw_decor(surf, scroll)
    
    def draw_tiles(self, surf, scroll):
        if hasattr(self, 'grass_manager'):
            self.grass_manager.draw(surf, (scroll[0] + 8, scroll[1] - 3))
        for layer in self.layers:
            layer.draw_tiles(surf, scroll)

    def leaves(self, surf, scroll):
        if self.leaf_spawners:
            for rect, fix in self.leaf_spawners.updateables(surf, scroll):
                if random.random() * 20000 / 0.5 / self.app.dt < rect.width * rect.height:
                    if rect.colliderect(self.app.u_rect()):
                        pos = (rect.x + random.random() * rect.width, rect.y + random.random() * rect.height)
                        if not self.physics_map.solid_check(pos) and fix:
                            self.app.world.gfx_manager.particles.append(Particle(self.app, 'leaf', pos, (-0.1, 0.3), frame=random.randint(0, 16), solid=True))
                        else:
                            self.app.world.gfx_manager.particles.append(Particle(self.app, 'leaf', pos, (-0.1, 0.3), frame=random.randint(0, 16), solid=False))
    
    def update_grass(self, rects):
        if hasattr(self, 'grass_manager'):
            self.grass_manager.update(rects)

class Layer:
    def __init__(self, tile_map, layer, app, mode, index=0):
        self.app = app
        self.mode = mode
        self.mapper = tile_map
        self.index = index
        self.tile_map, self.decor, self.render_scale = self.load(layer, mode=mode)
        if mode == 'game':
            for grass_tile in self.extract([('keys', 0)], False):
                if grass_tile.grid:
                    self.mapper.grass_map[grass_tile.key] = None
        self.tile_size = TILE_SIZE / self.render_scale
        for loc in self.tile_map.copy():
            tile = self.tile_map[loc]
            if 'decor' in tile.mode:
                self.decor.append(tile.copy())
                del self.tile_map[loc]
        self.decor_chunker = TileChunker(self.decor, self.app.chunk_size, TILE_SIZE)
        self.tile_chunks = self.load_tile_chunks()
    
    def load_tile_chunks(self):
        tile_chunks = {}
        for loc in self.tile_map:
            tile = self.tile_map[loc]
            aloc = str(math.floor(tile.pos.x / self.tile_size / TILE_CHUNK_SIZE[0])) + ';' + str(math.floor(tile.pos.y / self.tile_size / TILE_CHUNK_SIZE[1]))
            if not (aloc in tile_chunks):
                tile_chunks[aloc] = pygame.Surface((self.tile_size * TILE_CHUNK_SIZE[0], self.tile_size * TILE_CHUNK_SIZE[1]))
            tile_chunks[aloc].blit(tile.img, (tile.pos[0]%(self.tile_size * TILE_CHUNK_SIZE[0]), tile.pos[1]%(self.tile_size * TILE_CHUNK_SIZE[1])))
        return tile_chunks
    
    def save(self):
        tile_map = {}
        for loc in self.tile_map:
            tile_map[loc] = {'pos': list(self.tile_map[loc].pos / TILE_SIZE), 'dimensions': list(self.tile_map[loc].dimensions), 'rect_offset': [self.tile_map[loc].rect.x - self.tile_map[loc].pos.x, self.tile_map[loc].rect.y - self.tile_map[loc].pos.y],
                            'mode': self.tile_map[loc].mode, 'variant': self.tile_map[loc].variant}
        decor = []
        for coord in self.decor_chunker.chunk_data:
            for i, tile in enumerate(self.decor_chunker.chunk_data[coord]):
                decor.append({'pos': list(tile.pos), 'dimensions': list(tile.dimensions), 'rect_offset': [tile.rect.x - tile.pos.x, tile.rect.y - tile.pos.y], 'mode': tile.mode, 'variant': tile.variant})
        return {'tile_map': dict(tile_map), 'decor': list(decor), 'render_scale': self.render_scale}
    
    def load(self, layer, mode='game'):
        tile_map = {}
        for loc in layer['tile_map']:
            tile = layer['tile_map'][loc].copy()
            tile_map[loc] = Tile(tile['pos'], tile['dimensions'], tile['rect_offset'], tile['mode'], tile['variant'], pygame.transform.scale_by(self.app.assets[mode][tile['mode']][tile['variant']],
             layer['render_scale']), loc, grid=True, render_scale=layer['render_scale'])
        decor = []
        for i, tile in enumerate(layer['decor']):
            decor.append(Tile(tile['pos'], tile['dimensions'], tile['rect_offset'], tile['mode'], tile['variant'], pygame.transform.scale_by(self.app.assets[mode][tile['mode']][tile['variant']],
             layer['render_scale']), None, render_scale=layer['render_scale']))
        return tile_map, decor, layer['render_scale']
    
    def auto_tile(self):
        for loc in self.tile_map:
            tile = self.tile_map[loc]
            aloc = ''
            for shift in [(-1, 0), (0, -1), (1, 0), (0, 1)]:
                check_loc = str(math.floor(tile.pos[0] / TILE_SIZE) + shift[0]) + ';' + str(math.floor(tile.pos[1] / TILE_SIZE) + shift[1])
                if check_loc in self.tile_map:
                    if self.tile_map[check_loc].mode == tile.mode:
                        aloc += '1'
                    else:
                        aloc += '0'
                else:
                    aloc += '0'
            if tile.mode in AUTO_TILE_TYPES:
                tile.variant = AUTO_TILE_MAP[aloc] - 1
                tile.img = pygame.transform.scale_by(self.app.assets[self.mode][tile.mode][tile.variant], self.render_scale)
    
    def extract(self, id_pairs, keep=False):
        matches = []
        for tile in self.decor.copy():
            if (tile.mode, tile.variant) in id_pairs:
                matches.append(tile.copy())
                if not keep:
                    self.decor.remove(tile)
        for loc in self.tile_map.copy():
            tile = self.tile_map[loc]
            if (tile.mode, tile.variant) in id_pairs:
                matches.append(tile.copy())
                if not keep:
                    del self.tile_map[loc]
        
        return matches
            
    '''def solid_check(self, pos):
        tile_loc = str(math.floor(pos[0] // TILE_SIZE)) + ';' + str(math.floor(pos[1] // TILE_SIZE))
        if (tile_loc in self.tile_map) and self.solid:
            if self.tile_map[tile_loc].mode in PHYSICS_TILE_TYPES:
                return self.tile_map[tile_loc]
    
    def tile_type_at(self, pos):
        tile_loc = str(math.floor(pos.x // self.tile_size)) + ';' + str(math.floor(pos.x // self.tile_size))
        if tile_loc in self.tile_map:
            return self.tile_map[tile_loc].mode
    
    def tiles_around(self, pos):
        tiles = []
        tile_loc = (math.floor(pos.x // self.tile_size), math.floor(pos.y // self.tile_size))
        for offset in NEIGHBOUR_OFFSETS:
            check_loc = str(tile_loc[0] + offset[0]) + ';' + str(tile_loc[1] + offset[1])
            if check_loc in self.tile_map:
                tiles.append(self.tile_map[check_loc])
        return tiles
    
    def physics_rects_around(self, pos):
        if self.solid:
            rects = []
            for tile in self.tiles_around(pos):
                if tile.mode in PHYSICS_TILE_TYPES:
                    rects.append(tile.rect)
            return rects
        return []'''

    def stamp(self, img, pos):
        for y in range(math.ceil(img.get_height() / self.tile_size)):
            for x in range(math.ceil(img.get_width() / self.tile_size)):
                loc = (pos[0] + x * self.tile_size, pos[1] + y * self.tile_size)
                tile_loc = str(math.floor(loc[0] / self.tile_size)) + ';' + str(math.floor(loc[1] / self.tile_size))
                if tile_loc in self.tile_map:
                    tile = self.tile_map[tile_loc]
                    img_mask = pygame.mask.from_surface(tile.img)
                    tile.img.blit(img, (pos[0] - loc[0], pos[1] - loc[1]))
                    tile.img.blit(img_mask.to_surface(setcolor=(0, 0, 0, 0), unsetcolor=(0, 255, 0)), (0, 0))
                    tile.img.set_colorkey((0, 255, 0))

    
    def draw_tiles(self, surf, scroll):
        for x in range(math.floor(scroll.x / self.tile_size), math.floor((scroll.x + surf.get_width()) // self.tile_size + 1)):
            for y in range(math.floor(scroll.y // self.tile_size), math.floor((scroll.y + surf.get_height()) // self.tile_size + 1)):
                loc = str(x) + ';' + str(y)
                if loc in self.tile_map:
                    tile = self.tile_map[loc]
                    tile.draw(surf, pygame.Vector2(math.floor(scroll.x), math.floor(scroll.y)))
    
    def draw_decor(self, surf, scroll):
        self.decor_chunker.draw(surf, scroll)
        
    def draw(self, surf, scroll):
        self.decor_chunker.draw(surf, scroll)
        for x in range(math.floor(scroll.x / self.tile_size), math.floor((scroll.x + surf.get_width()) // self.tile_size + 1)):
            for y in range(math.floor(scroll.y // self.tile_size), math.floor((scroll.y + surf.get_height()) // self.tile_size + 1)):
                loc = str(x) + ';' + str(y)
                if loc in self.tile_map:
                    tile = self.tile_map[loc]
                    tile.draw(surf, pygame.Vector2(math.floor(scroll.x), math.floor(scroll.y)))
    
    def draw_tile_chunks(self, surf, scroll):
        for x in range(math.floor(scroll.x / self.tile_size / TILE_CHUNK_SIZE[0]), math.floor((scroll.x + surf.get_width()) // (self.tile_size * TILE_CHUNK_SIZE[0]) + 1)):
            for y in range(math.floor(scroll.y // (self.tile_size * TILE_CHUNK_SIZE[1])), math.floor((scroll.y + surf.get_height()) // (self.tile_size * TILE_CHUNK_SIZE[1]) + 1)):
                loc = str(x) + ';' + str(y)
                if loc in self.tile_chunks:
                    surf.blit(self.tile_chunks[loc], (x * self.tile_size * TILE_CHUNK_SIZE[0] - math.floor(scroll.x), y * self.tile_size * TILE_CHUNK_SIZE[1] - math.floor(scroll.y)))

PHYSICS_COLOURS = {'block': (255, 255, 255), 'danger': (255, 0, 0)}

class PhysicsTile:
    def __init__(self, pos, dimensions, rect_offset, key, mode='block'):
        self.pos = pygame.Vector2(pos) * TILE_SIZE
        self.key = key
        self.rect_offset = list(rect_offset)
        self.dimensions = list(dimensions)
        self.mode = mode
        self.custom = bool(self.mode == 'custom')
        self.rect = pygame.Rect(self.pos.x + rect_offset[0], self.pos.y + rect_offset[1], dimensions[0], dimensions[1])

class PhysicsTileMap:
    def __init__(self, app, tile_map):
        self.app = app
        self.tile_map = self.load(tile_map)
    
    @staticmethod
    def load(tile_data):
        tile_map = {}
        for loc in tile_data:
            try:
                tile_map[loc] = PhysicsTile(tile_data[loc]['pos'], tile_data[loc]['dimensions'], tile_data[loc]['rect_offset'], loc, mode=tile_data[loc]['mode'])
            except KeyError:
                tile_map[loc] = PhysicsTile(tile_data[loc]['pos'], tile_data[loc]['dimensions'], tile_data[loc]['rect_offset'], loc)
        return tile_map
    
    @staticmethod
    def save(tile_data):
        tile_map = {}
        for loc in tile_data:
            tile_map[loc] = {'pos': list(tile_data[loc].pos / TILE_SIZE), 'rect_offset': tile_data[loc].rect_offset.copy(), 'dimensions': list(tile_data[loc].dimensions), 'mode': tile_data[loc].mode}
        return tile_map
    
    def solid_check(self, pos):
        tile_loc = str(math.floor(pos[0] // TILE_SIZE)) + ';' + str(math.floor(pos[1] // TILE_SIZE))
        if (tile_loc in self.tile_map):
            if not self.tile_map[tile_loc].custom:
                return True
            if self.tile_map[tile_loc].rect.collidepoint(pos[0], pos[1]):
                return self.tile_map[tile_loc]
    
    def block_check(self, pos):
        tile_loc = str(math.floor(pos[0] // TILE_SIZE)) + ';' + str(math.floor(pos[1] // TILE_SIZE))
        if tile_loc in self.tile_map:
            return self.tile_map[tile_loc].mode == 'block'
    
    def particle_solid(self, pos):
        return f'{str(math.floor(pos[0] / TILE_SIZE))};{str(math.floor(pos[1] / TILE_SIZE))}' in self.tile_map
    
    def tile_type_at(self, pos):
        tile_loc = str(math.floor(pos[0] / TILE_SIZE)) + ';' + str(math.floor(pos[1] / TILE_SIZE))
        if tile_loc in self.tile_map:
            return self.tile_map[tile_loc].mode
    
    def danger_at(self, rect):
        for tile in self.tiles_around(rect.center):
            if (tile.mode in self.app.danger) and rect.colliderect(tile.rect):
                return 1
    
    def tiles_around(self, pos):
        tiles = []
        tile_loc = (math.floor(pos[0] // TILE_SIZE), math.floor(pos[1] // TILE_SIZE))
        for offset in NEIGHBOUR_OFFSETS:
            check_loc = str(tile_loc[0] + offset[0]) + ';' + str(tile_loc[1] + offset[1])
            if check_loc in self.tile_map:
                tiles.append(self.tile_map[check_loc])
        return tiles
    
    def physics_rects_around(self, pos):
        for tile in self.tiles_around(pos):
            if not (tile.mode in self.app.danger):
                yield tile.rect
    
    def draw(self, surf, scroll):
        for loc in self.tile_map:
            tile = self.tile_map[loc]
            pygame.draw.rect(surf, PHYSICS_COLOURS[tile.mode], (tile.rect.x - scroll[0], tile.rect.y - scroll[1], tile.rect.width, tile.rect.height))
