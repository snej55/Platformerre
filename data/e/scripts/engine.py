import pygame, sys, time
import gc

from .man.window import Win

window = Win()

from .assets import *
from .env.tiles import TileMap
from .man.world import World

class Pygmy:
    def __init__(self, mode='game', config={}):
        self.render_scale = pygame.Vector2(RENDER_SCALE, RENDER_SCALE)
        self.config = config
        self.clock = pygame.time.Clock()
        self.dt = 1
        self.title = 'pge window'
        if 'caption' in self.config:
            self.title = self.config['caption']
        self.mode = mode
        self.last_time = time.time() - 1 / 60
        self.tile_size = TILE_SIZE
        self.chunk_size = pygame.Vector2(CHUNK_SIZE)
        self.auto_tile_types = AUTO_TILE_TYPES
        self.physics_tile_types = PHYSICS_TILE_TYPES
        self.entity_quad_size = ENTITY_QUAD_SIZE
        self.danger = DANGER
        self.scrolling = 0
        self.render_scroll = [0, 0]
        self.screen_shake = 0
        self.clicking = False
        self.right_clicking = False
        self.mouse_pos = []
        self.assets = {'game': GAME_ASSETS, 'edit': EDIT_ASSETS}
        self.palettes = PALETTES
        self.running = True
        self.keys = {key: False for key in KEYS}
        self.tile_map = TileMap(self)
        self.toggles = {}
        self.fps = 0
        self.shaders = {'frag': None, 'vert': None}
        for prgram in self.shaders:
            if prgram in self.config:
                self.shaders[prgram] = self.config[prgram]
        self.shaders = {'frag': self.shaders['frag'], 'vert': self.shaders['vert']}
        self.world = World(self)
        window.start(self)
        self.world.init_window(window)
        self.world.gfx_manager.add_particle_system('cinders', 'physics', trail=True, bounce=0.4, fade=2)
        self.time = 0
    
    def __contains__(self, pos):
        return self.world.window.camera.scroll[0] <= pos[0] <= self.world.window.camera.scroll[0] + self.world.window.screen.get_width() and self.world.window.camera.scroll[1] <= pos[1] <= self.world.window.camera.scroll[1] + self.world.window.screen.get_height()
    
    def load_level(self, path):
        return self.tile_map.load(path)
    
    def secsec(self):
        '''
        Overwrite this to do *stuff*

        This *stuff* will happen at the end of rendering, before shaders and stuff.
        '''
        pass
    
    def close(self):
        self.running = False
        pygame.display.quit()
        pygame.quit()
        sys.exit()
    
    def u_rect(self):
        return pygame.Rect(self.scroll[0] - 64, self.scroll[1] - 64, self.world.window.screen.get_width() + 128, self.world.window.screen.get_height() + 128)
    
    def update(self, *args, **kwargs):
        pass
    
    def sec(self, shade_uniforms={}):
        self.time += 1 * self.dt
        self.mouse_pos = list(n / self.render_scale[i] for i, n in enumerate(pygame.mouse.get_pos()))
        self.toggles = set([])
        self.scrolling = 0
        pygame.event.set_allowed([pygame.QUIT, pygame.KEYDOWN, pygame.KEYUP, pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP])
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
        if not shade_uniforms:
            screen_tex = self.world.window.mgl.surf_to_texture(self.world.window.screen)
            shade_uniforms = {'stuff': {'slomo': self.world.tick.slomo, 'tex': screen_tex, 'alpha_surf': self.world.window.alpha_surf, 'lighting': self.light_surf, 'ui_surf': self.world.window.ui_surf}}
        self.world.update(shade_uniforms=shade_uniforms)
        self.scroll = self.world.window.render_scroll
        self.dt = self.world.tick.dt
