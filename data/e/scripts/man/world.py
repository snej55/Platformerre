import pygame

from .fps import Tick
from ..env.tiles import TileMap
from ..entities.ents import EntityManager # hey
from ..gfx.management import GFXManager
from ..entities.stuff import ItemManager

class World:
    def __init__(self, app):
        self.app = app
        self.tile_map = TileMap(app)
        self.tick = Tick(app, fps=self.app.fps)
        self.gfx_manager = GFXManager(app)
        self.entity_manager = EntityManager(app)
        self.item_manager = ItemManager(app)
    
    def init_window(self, win):
        self.window = win
    
    def update(self, shade_uniforms={}):
        screen, scroll = tuple(self.window.sec())
        self.tile_map.draw_decor(screen, scroll)
        self.entity_manager.update(screen, scroll)
        self.item_manager.update(screen, scroll)
        self.tile_map.update_grass([self.app.player])
        self.tile_map.draw_tiles(screen, scroll)
        self.app.update(screen, scroll)
        self.gfx_manager.update(screen, scroll)
        self.app.secsec()
        self.window.filt()
        pygame.display.set_caption(f'{self.app.title} at {self.tick.clock.get_fps() :.1f} FPS')
        self.window.shade(shade_uniforms)
        self.window.inflate()
        self.tick.update()