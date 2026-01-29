from .tools.utils import *
from .bip import TILE_SIZE

GAME_ASSETS = {'large_decor': load_tile_imgs('decor/large_decor.png', 50),
               'gras': load_spritesheet('grass', 'grass'),
               'sword': load_img('entities/sword.png'),
               'slash': load_spritesheet('vfx', 'slash'),
               'noise': load_img('vfx/noise.png'),
               'particle/particle': load_spritesheet('particles', 'particle'),
               'particle/explode': load_spritesheet('particles', 'explode'),
               'particle/leaf': load_spritesheet('particles', 'leaf'),
               'collectables/coin': load_spritesheet('collectables', 'coin'),
               'health_bar': load_img('misc/health_bar.png'),
               'enemy_health_bar': load_img('misc/enemy_health_bar.png'),
               'spawners': load_imgs('spawners'),
               'blaster': load_img('blasters/blaster.png'),
               'lasers': {
                   'red': load_img('blasters/laser_red.png'),
                   'blue': load_img('blasters/laser.png')
               }}
EDIT_ASSETS = {'large_decor': load_tile_imgs('decor/large_decor.png', 50),
               'spawners': load_imgs('spawners')}
GAME_ASSETS = load_tile_assets('tiles', GAME_ASSETS, TILE_SIZE)
EDIT_ASSETS = load_tile_assets('tiles', EDIT_ASSETS, TILE_SIZE)
load_entity_assets('entities/player', GAME_ASSETS, 'player')
load_entity_assets('entities/slime_green', GAME_ASSETS, 'slime_green')
PALETTES = load_palettes(GAME_ASSETS)