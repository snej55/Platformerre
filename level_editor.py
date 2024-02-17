'''WARNING: This is some *stinky* code. Use at own risk...'''

import pygame, math, time, sys

from data.e.scripts.bip import *
from data.e.scripts.assets import *
from data.e.scripts.tools.ui.box import Box
from data.e.scripts.env.tiles import TileMap, Layer, Tile, PhysicsTile
from data.e.scripts.tools.ui.texto import TextBox, Font

PHYSICS_MODES = ['block', 'danger']

class Editor():
    def __init__(self, config={}):
        self.config = config
        self.mode = 'edit'
        self.render_scale = pygame.Vector2(RENDER_SCALE, RENDER_SCALE)
        self.display = pygame.display.set_mode(WIN_DIMENSIONS)
        self.screen = pygame.Surface((self.display.get_width() / self.render_scale.x, self.display.get_height() / self.render_scale.y))
        self.clock = pygame.time.Clock()
        self.dt = 1
        self.title = 'pge window'
        if 'caption' in self.config:
            self.title = self.config['caption']
        self.last_time = time.time() - 1 / 60
        self.tile_size = TILE_SIZE
        self.chunk_size = pygame.Vector2(CHUNK_SIZE)
        self.auto_tile_types = AUTO_TILE_TYPES
        self.physics_tile_types = PHYSICS_TILE_TYPES
        self.entity_quad_size = ENTITY_QUAD_SIZE
        self.danger = DANGER
        self.scrolling = 0
        self.running = True
        self.render_scroll = [0, 0]
        self.screen_shake = 0
        self.clicking = False
        self.right_clicking = False
        self.mouse_pos = []
        self.assets = {'game': GAME_ASSETS, 'edit': EDIT_ASSETS}
        self.tile_variant = 0
        self.tile_group = 0
        self.tile_list = list(self.assets['edit'])
        self.on_grid = True
        self.render_scale = [2.0, 2.0]
        self.layer_scale = 1.0
        self.layer = 0
        self.alpha = 255
        self.fps = 60
        self.solid = True
        self.title = 'Fancy new level editor'
        self.tile_map = TileMap(self)
        self.tile_map.load('data/maps/0.json', mode='edit')
        self.panel = Box(self, (0, 0, self.screen.get_width() * 0.333, self.screen.get_height()), (100, 100, 100), alpha=150, stroke=(255, 255, 255))
        self.filt = pygame.Surface(self.screen.get_size())
        self.filt.fill((50, 50, 50))
        self.filt.set_alpha(100)
        self.lry_panel_scroll = 0
        self.lyrs = 0
        self.auto_tiling = False
        self.time = 0
        self.palettes = PALETTES
        self.running = True
        self.keys = {key: False for key in KEYS}
        self.toggles = {}
        self.fps = 0
        self.scroll = pygame.Vector2(0, 0)
        self.panel_scroll = -10
        self.panel_tile_dim = [0, 0]
        self.physics_mode = 0
        self.tile_select_surf = pygame.Surface(tuple(self.panel_tile_dim))
        self.tile_select_surf.fill((255, 100, 0))
        self.tile_select_surf.set_alpha(127)
        self.tile_group_box = TextBox('data/images/fonts/small_font.png', pygame.Rect(0, 0, 100, 10), self.tile_list[self.tile_group])
        self.text = Font('data/images/fonts/small_font.png')
        self.tile_select_pos = (0, 0)
        self.tile_select_map = {}
        #print([self.tile_map.physics_map.tile_map[loc].pos for loc in self.tile_map.physics_map.tile_map])
    
    def __contains__(self, pos):
        return self.scroll[0] <= pos[0] <= self.scroll[0] + self.world.window.screen.get_width() and self.scroll[1] <= pos[1] <= self.scroll[1] + self.world.window.screen.get_height()
    
    def load_level(self, path):
        return self.tile_map.load(path)
    
    def close(self):
        self.running = False
        print('closing')
        pygame.quit()
        sys.exit()
    
    def draw_grid(self, scroll, size, color):
        tile_size = [self.tile_size * size[0], self.tile_size * size[1]]
        length = math.ceil(self.screen.get_width() / tile_size[0]) + 2
        height = math.ceil(self.screen.get_height() / tile_size[1]) + 2
        for x in range(length):
            pygame.draw.line(self.screen, color, ((x - 1) * tile_size[0] - (scroll[0] % tile_size[0]), 0), ((x - 1) * tile_size[0] - (scroll[0] % tile_size[0]), self.screen.get_height()))
        for y in range(height):
            pygame.draw.line(self.screen, color, (0, (y - 1) * tile_size[1] - (scroll[1] % tile_size[1])), (self.screen.get_width(), (y - 1) * tile_size[1] - (scroll[1] % tile_size[1])))
        
    def handle_panel(self, mouse_pos):
        if self.keys[pygame.K_RCTRL] and self.keys[pygame.K_RIGHT]:
            self.panel.rect.width += 1
        if self.keys[pygame.K_RCTRL] and self.keys[pygame.K_LEFT]:
            self.panel.rect.width = max(self.panel_tile_dim[0], self.panel.rect.width - 1)
        if self.keys[pygame.K_RCTRL] and self.keys[pygame.K_w]:
            self.panel.alpha = min(self.panel.alpha + 1, 255)
        if pygame.K_p in self.toggles:
            self.physics_mode = (self.physics_mode + 1) % len(PHYSICS_MODES)
        if self.keys[pygame.K_RCTRL] and self.keys[pygame.K_s]:
            self.panel.alpha = max(self.panel.alpha - 1, 0)
        if self.panel.width:
            if self.keys[pygame.K_RCTRL] and self.keys[pygame.K_r]:
                self.panel.stroke[0] = min(self.panel.stroke[0] + 1, 255)
            if self.keys[pygame.K_RCTRL] and self.keys[pygame.K_f]:
                self.panel.stroke[0] = max(self.panel.stroke[0] - 1, 0)
            if self.keys[pygame.K_RCTRL] and self.keys[pygame.K_t]:
                self.panel.stroke[1] = min(self.panel.stroke[1] + 1, 255)
            if self.keys[pygame.K_RCTRL] and self.keys[pygame.K_g]:
                self.panel.stroke[1] = max(self.panel.stroke[1] - 1, 0)
            if self.keys[pygame.K_RCTRL] and self.keys[pygame.K_y]:
                self.panel.stroke[2] = min(self.panel.stroke[2] + 1, 255)
            if self.keys[pygame.K_RCTRL] and self.keys[pygame.K_h]:
                self.panel.stroke[2] = max(self.panel.stroke[2] - 1, 0)
        else:
            if self.keys[pygame.K_RCTRL] and self.keys[pygame.K_r]:
                self.panel.fill[0] = min(self.panel.fill[0] + 1, 255)
            if self.keys[pygame.K_RCTRL] and self.keys[pygame.K_f]:
                self.panel.fill[0] = max(self.panel.fill[0] - 1, 0)
            if self.keys[pygame.K_RCTRL] and self.keys[pygame.K_t]:
                self.panel.fill[1] = min(self.panel.fill[1] + 1, 255)
            if self.keys[pygame.K_RCTRL] and self.keys[pygame.K_g]:
                self.panel.fill[1] = max(self.panel.fill[1] - 1, 0)
            if self.keys[pygame.K_RCTRL] and self.keys[pygame.K_y]:
                self.panel.fill[2] = min(self.panel.fill[2] + 1, 255)
            if self.keys[pygame.K_RCTRL] and self.keys[pygame.K_h]:
                self.panel.fill[2] = max(self.panel.fill[2] - 1, 0)
        if self.keys[pygame.K_RCTRL] and (pygame.K_d in self.toggles):
            self.panel.width = not self.panel.width
        self.panel.draw(self.screen)
        for tile in self.assets['edit'][self.tile_list[self.tile_group]]:
            self.panel_tile_dim[0] = max(self.panel_tile_dim[0], tile.get_height())
            self.panel_tile_dim[1] = max(self.panel_tile_dim[1], tile.get_height())
        self.panel.rect.width = max(self.panel_tile_dim[0], self.panel.rect.width)
        self.tile_select_surf = pygame.Surface(tuple(self.panel_tile_dim))
        self.tile_select_surf.fill((255, 100, 0))
        self.tile_select_surf.set_alpha(127)
        height = 0
        lat = 0
        self.tile_select_map = {}
        for i, tile in enumerate(self.assets['edit'][self.tile_list[self.tile_group]]):
            self.screen.blit(tile, (lat, height - self.panel_scroll))
            self.tile_select_map[(math.floor(lat / self.panel_tile_dim[0]), math.floor(height / self.panel_tile_dim[1]))] = i
            lat += self.panel_tile_dim[0]
            if lat + self.panel_tile_dim[0] > self.panel.rect.width:
                lat = 0
                height += self.panel_tile_dim[1]
        if self.panel.rect.collidepoint(mouse_pos[0], mouse_pos[1]):
            mp = (mouse_pos[0], mouse_pos[1] + self.panel_scroll)
            if self.clicking:
                if (math.floor(mp[0] / self.panel_tile_dim[0]), math.floor(mp[1] / self.panel_tile_dim[1])) in self.tile_select_map:
                    self.tile_select_pos = (math.floor(mp[0] / self.panel_tile_dim[0]), math.floor(mp[1] / self.panel_tile_dim[1]))
                    self.tile_variant = self.tile_select_map[self.tile_select_pos]
            if self.scrolling:
                self.panel_scroll = max(-10, min(self.panel_scroll + self.scrolling * 10, height + self.panel_tile_dim[1]))
        
        if self.keys[pygame.K_LCTRL] and pygame.K_g in self.toggles:
            self.tile_group = (self.tile_group + 1) % len(self.tile_list)
            self.tile_variant = 0
            self.tile_select_pos = (0, 0)
            self.panel_tile_dim = [0, 0]
            self.tile_group_box = TextBox('data/images/fonts/small_font.png', pygame.Rect(0, 0, 100, 10), self.tile_list[self.tile_group])
        self.tile_group_box.render(self.screen, 1)
    
    def handle_lry_panel(self, mouse_pos):
        panel_surf = pygame.Surface((int(self.screen.get_width() * 0.1), int(self.screen.get_height() * 0.5)))
        panel_surf.fill((90, 90, 90))
        panel_surf.set_alpha(150)
        #pygame.draw.rect(self.screen, (90, 90, 90), (self.screen.get_width() * 0.9, 20, self.screen.get_width() * 0.1, self.screen.get_height() * 0.5))
        for i, layer in enumerate(self.tile_map.layers):
            color = (255, 255, 255)
            if layer.index == self.layer: color = (255, 0, 0)
            pygame.draw.rect(panel_surf, color, (self.screen.get_width() * 0.01, self.screen.get_width() * 0.01 + i * self.screen.get_width() * 0.08 - self.lry_panel_scroll, self.screen.get_width() * 0.08, self.screen.get_width() * 0.08),
            width=1)
            self.text.render(panel_surf, str(layer.index), (self.screen.get_width() * 0.01 + 2, self.screen.get_width() * 0.01 + i * self.screen.get_width() * 0.08 - self.lry_panel_scroll + 2))
        panel_rect = pygame.Rect(self.screen.get_width() * 0.9, 20, self.screen.get_width() * 0.1, self.screen.get_height() * 0.5)
        if panel_rect.collidepoint(mouse_pos[0], mouse_pos[1]): 
            if self.scrolling: self.lry_panel_scroll = max(0, self.lry_panel_scroll + self.scrolling * 10)
        if self.keys[pygame.K_LCTRL] and pygame.K_UP in self.toggles:
            self.tile_map.layers[self.layer].index, self.tile_map.layers[self.layer - 1].index = self.tile_map.layers[self.layer - 1].index, self.tile_map.layers[self.layer].index
            self.layer -= 1
        elif self.keys[pygame.K_LCTRL] and pygame.K_DOWN in self.toggles:
            self.tile_map.layers[self.layer].index, self.tile_map.layers[min(len(self.tile_map.layers) - 1, self.layer + 1)].index = self.tile_map.layers[min(len(self.tile_map.layers) - 1, self.layer + 1)].index, self.tile_map.layers[self.layer].index
            self.layer += 1
        self.screen.blit(panel_surf, (self.screen.get_width() * 0.9, 20))
    
    def update(self):
        self.screen.fill((0, 0, 0))
        if not self.keys[pygame.K_RCTRL]: self.scroll[0] += (self.keys[pygame.K_d] - self.keys[pygame.K_a]) * 2; self.scroll[1] += (self.keys[pygame.K_s] - self.keys[pygame.K_w]) * 2
        if pygame.K_t in self.toggles:
            self.tile_map.layers[self.layer].auto_tile()
        if self.keys[pygame.K_LCTRL] and pygame.K_i in self.toggles:
            self.auto_tiling = not self.auto_tiling
        if pygame.K_l in self.toggles:
            self.lyrs = (self.lyrs + 1) % 3
            print(self.lyrs)
        if pygame.K_g in self.toggles and not (self.keys[pygame.K_LCTRL] and pygame.K_g in self.toggles):
            self.on_grid = not self.on_grid
        if self.keys[pygame.K_LSHIFT]:
            self.scroll[1] += self.scrolling * 50
        elif self.keys[pygame.K_RSHIFT]:
            self.scroll[0] += self.scrolling * 50
        if self.keys[pygame.K_LCTRL] and pygame.K_w in self.toggles:
            self.tile_map.layers.pop(self.layer)
            self.layer = len(self.tile_map.layers) - 1
        if pygame.K_q in self.toggles:
            if self.keys[pygame.K_LSHIFT]:
                self.layer = (self.layer + 1) % len(self.tile_map.layers)
            else:
                self.layer = (self.layer - 1) % len(self.tile_map.layers)
            print(self.layer)
        if self.keys[pygame.K_LCTRL] and self.keys[pygame.K_s]:
            self.tile_map.save('data/maps/0.json')
        if pygame.K_n in self.toggles and self.keys[pygame.K_LCTRL]:
            self.tile_map.layers.append(Layer(self.tile_map, {'tile_map': {}, 'decor': [], 'solid': False, 'render_scale': 1.0}, self, mode='edit', index=len(self.tile_map.layers)))
            print(len(self.tile_map.layers))
        render_scroll = (int(self.scroll[0]), int(self.scroll[1]))
        if self.lyrs == 0:
            layers = self.tile_map.layers.copy()
            for i, layer in enumerate(layers):
                if i != self.layer:
                    layer.draw(self.screen, self.scroll)
            self.screen.blit(self.filt, (0, 0))
            layers[self.layer].draw(self.screen, self.scroll)
        elif self.lyrs == 1:
            self.tile_map.draw_decor(self.screen, self.scroll)
            self.tile_map.draw_tiles(self.screen, self.scroll)
            self.tile_map.physics_map.draw(self.screen, render_scroll)
        else:
            self.tile_map.layers.sort(key=lambda x: x.index)
            for i, layer in enumerate(self.tile_map.layers):
                layer.index = i
            self.tile_map.draw_decor(self.screen, self.scroll)
            self.tile_map.draw_tiles(self.screen, self.scroll)
        self.draw_grid(render_scroll, [1, 1], (50, 50, 50))
        self.draw_grid(render_scroll, CHUNK_SIZE, (100, 50, 0))
        self.draw_grid(render_scroll, WATER_CHUNK_SIZE, (0, 0, 100))
        self.draw_grid(render_scroll, ENTITY_QUAD_SIZE, (100, 0, 0))
        pygame.draw.line(self.screen, (255, 255, 255), (-render_scroll[0], -render_scroll[1]), (self.screen.get_width(), -render_scroll[1]))
        pygame.draw.line(self.screen, (255, 255, 255), (-render_scroll[0], -render_scroll[1]), (-render_scroll[0], self.screen.get_height()))
        current_tile_img = self.assets['edit'][self.tile_list[self.tile_group]][self.tile_variant].copy()
        current_tile_img.set_alpha(200)
        mouse_pos = pygame.mouse.get_pos()
        mouse_pos = (mouse_pos[0] / RENDER_SCALE, mouse_pos[1] / RENDER_SCALE)
        tile_pos = (math.floor((mouse_pos[0] + self.scroll[0]) // self.tile_size), math.floor((mouse_pos[1] + self.scroll[1]) // self.tile_size))
        if self.on_grid:
            self.screen.blit(current_tile_img, (tile_pos[0] * self.tile_size - self.scroll[0], tile_pos[1] * self.tile_size - self.scroll[1]))
        else:
            self.screen.blit(current_tile_img, mouse_pos)
        self.handle_panel(mouse_pos)
        self.handle_lry_panel(mouse_pos)
        self.screen.blit(self.tile_select_surf, (self.tile_select_pos[0] * self.panel_tile_dim[0], self.tile_select_pos[1] * self.panel_tile_dim[1] - self.panel_scroll))
        if not self.panel.rect.collidepoint(mouse_pos[0], mouse_pos[1]):
            if self.clicking:
                if self.lyrs == 0:
                    if self.on_grid:
                        loc = str(tile_pos[0]) + ';' + str(tile_pos[1])
                        self.tile_map.layers[self.layer].tile_map[loc] = Tile(tile_pos, (self.tile_size, self.tile_size), (0, 0), self.tile_list[self.tile_group], self.tile_variant, 
                        current_tile_img.copy(), loc, True, self.layer_scale)
                        if self.tile_list[self.tile_group] in AUTO_TILE_TYPES and self.auto_tiling:
                            self.tile_map.layers[self.layer].auto_tile()
                    else:
                        loc = str(math.floor(tile_pos[0] / CHUNK_SIZE[0])) + ';' + str(math.floor(tile_pos[1] / CHUNK_SIZE[1]))
                        if not loc in self.tile_map.layers[self.layer].decor_chunker.chunk_data:
                            self.tile_map.layers[self.layer].decor_chunker.chunk_data[loc] = []
                        self.tile_map.layers[self.layer].decor_chunker.chunk_data[loc].append(Tile((mouse_pos[0] + self.scroll.x, mouse_pos[1] + self.scroll.y), current_tile_img.get_size(),
                        (0, 0), self.tile_list[self.tile_group], self.tile_variant, current_tile_img.copy(), None, False, self.layer_scale))
                else:
                    loc = str(tile_pos[0]) + ';' + str(tile_pos[1])
                    self.tile_map.physics_map.tile_map[loc] = PhysicsTile(tile_pos, [TILE_SIZE, TILE_SIZE], [0, 0], loc, mode=PHYSICS_MODES[self.physics_mode])
            elif self.right_clicking:
                if self.lyrs == 0:
                    loc = str(tile_pos[0]) + ';' + str(tile_pos[1])
                    if loc in self.tile_map.layers[self.layer].tile_map:
                        del self.tile_map.layers[self.layer].tile_map[loc]
                        if self.tile_list[self.tile_group] in AUTO_TILE_TYPES and self.auto_tiling:
                            self.tile_map.layers[self.layer].auto_tile()
                    mouse_pos = (mouse_pos[0] + self.scroll[0], mouse_pos[1] + self.scroll[1])
                    for coord in self.tile_map.layers[self.layer].decor_chunker.chunk_data:
                        for tile in self.tile_map.layers[self.layer].decor_chunker.chunk_data[coord].copy():
                            if tile.rect.collidepoint(mouse_pos):
                                self.tile_map.layers[self.layer].decor_chunker.chunk_data[coord].remove(tile)
                else:
                    loc = str(tile_pos[0]) + ';' + str(tile_pos[1])
                    if loc in self.tile_map.physics_map.tile_map:
                        del self.tile_map.physics_map.tile_map[loc]
        self.text.render(self.screen, f'FPS: {self.clock.get_fps() :.1f}', (280, 5))
        pygame.transform.scale_by(self.screen, self.render_scale, self.display)
        pygame.display.set_caption(f'{self.title} at {self.clock.get_fps() :.0f} FPS')
        pygame.display.flip()
        self.clock.tick(60)
    
    def run(self):
        while self.running:
            self.time += 1 * self.dt
            self.mouse_pos = list(n / self.render_scale[i] for i, n in enumerate(pygame.mouse.get_pos()))
            self.toggles = set([])
            self.scrolling = 0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.close()
                if event.type == pygame.KEYDOWN:
                    self.keys[event.key] = True
                    self.toggles.add(event.key)
                if event.type == pygame.KEYUP:
                    self.keys[event.key] = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.clicking = True
                    if event.button == 3:
                        self.right_clicking = True
                    if event.button == 4:
                        self.scrolling = -1
                    if event.button == 5:
                        self.scrolling = 1
                if event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        self.clicking = False
                    if event.button == 3:
                        self.right_clicking = False
            if self.keys[pygame.K_ESCAPE]:
                self.close()
            self.update()

if __name__ == '__main__':
    Editor().run()
