import pygame, math
import data.e.scripts as e

#from data.e.scripts.entities.stuff import AnimatedItem, Item
from data.e.scripts.env.tiles import *
from data.scripts.entities import Player, Slime
from data.e.scripts.tools.utils import outline

class App(e.Pygmy):
    def __init__(self):
        super().__init__(config={
            'caption': 'Platformerre'
        })
        #self.world.tile_map.load('data/maps/0.json')
        #self.world.tile_map.load_leaves('data/config/leaf.json')
        self.world.window.add_shader('stuff', 'default.frag', 'default.vert')  # add shaders with mgl stuff
        self.world.tile_map.load('data/maps/0.json')
        self.player = Player((20, 10), (6, 7), (-1, -1), self, vj=-4)
        self.world.window.set_camera_target(self.player)
        self.world.window.window.opacity = 1.0
        self.player_health = 0
        self.high_color_top = pygame.Color(99, 159, 91)
        self.low_color_top = pygame.Color(156, 102, 89)
        self.high_color_bottom = pygame.Color(55, 110, 73)
        self.low_color_bottom = pygame.Color(136, 67, 79)
        self.health_flash = [(254, 254, 215), 0]
        #self.items = [AnimatedItem(self.assets['game']['collectables/coin'], self, (xo * 4, 10), (0, -6), self.assets['game']['particle/particle'][0], mass=0.25, bounce=0.9, speed=0.5) for xo in range(100)]#Item(self, (30, 10), (0, -6), self.assets['game']['particle/particle'][0], mass=0.25, bounce=0.9)
        self.slimes = [Slime((x * 40, -70), (11, 7), (-2, -2), self) for x in range(20)]#[Slime((500, -20), (11, 7), (-2, -2), self), Slime((100, -20), (11, 7), (-2, -2), self), Slime((110, -20), (11, 7), (-2, -2), self), Slime((50, -20), (11, 7), (-2, -2), self)]
    
    def secsec(self):
        self.health_flash[1] = min(self.health_flash[1] + 1 * self.dt, 10)
        if self.player.health > self.player.max_health * 0.15:
            outline(self.assets['game']['health_bar'], (8, 6), self.world.window.screen, pygame.Color(22, 19, 35).lerp(self.health_flash[0], 1 - self.health_flash[1] * 0.1))
        else:
            outline(self.assets['game']['health_bar'], (8, 6), self.world.window.screen, pygame.Color(22, 19, 35).lerp((254, 254, 215), (math.sin(self.time * 0.1) + 1) * 0.5).lerp((194, 89, 64), (math.sin(self.time * 0.037) + 1) * 0.5))
        target_health = self.player.health if self.player.ad >= 120 else 0
        self.player_health += (target_health - self.player_health) * 0.2 * self.dt
        surf = pygame.Surface((32, 8))
        pygame.draw.rect(surf, self.low_color_top.lerp(self.high_color_top, self.player_health / self.player.max_health), (3, 2, 27 * self.player_health / self.player.max_health, 2))
        pygame.draw.rect(surf, self.low_color_bottom.lerp(self.high_color_bottom, self.player_health / self.player.max_health), (3, 4, 27 * self.player_health / self.player.max_health, 2))
        surf.set_colorkey((0, 255, 0))
        surf.blit(self.assets['game']['health_bar'], (0, 0))
        self.world.window.screen.blit(surf, (8, 6))

    def update(self, screen, scroll):
        if self.player.update():
            self.player.die()
        #self.item.box.draw(screen, scroll)
        self.player.draw(screen, scroll)
        #self.item.update(screen, scroll)
        #self.world.tile_map.leaves(screen, scroll)
        #self.world.tile_map.physics_map.draw(screen, scroll)
        if pygame.K_p in self.toggles:
            print(self.player.pos)
            #for layer in self.world.tile_map.layers:
             #   layer.stamp(self.assets['game']['large_decor'][0], (20, 80))
           # self.item.box.vel.y = -5
            #self.item.box.vel.x = 5

    def run(self):
        while self.running:
            self.sec()

if __name__ == '__main__':
    app = App()
    app.run()