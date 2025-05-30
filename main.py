import pygame, math, random
import data.e.scripts as e

#from data.e.scripts.entities.stuff import AnimatedItem, Item
from data.e.scripts.env.tiles import *
from data.scripts.entities import Player, Slime
from data.scripts.blasters import BLaserManager, Blaster
from data.e.scripts.tools.utils import outline
from data.e.scripts.gfx.lighting import Lighting

class App(e.Pygmy):
    def __init__(self):
        super().__init__(config={
            'caption': 'Platformerre'
        })
        #self.world.tile_map.load('data/maps/0.json')
        #self.world.tile_map.load_leaves('data/config/leaf.json')
        self.world.tile_map.load('data/maps/0.json')
        self.entities = []
        self.lighting = Lighting(self)
        player_pos = [10, 10]
        for spawner in self.world.tile_map.extract([('spawners', 0), ('spawners', 1)]):
            if spawner.variant == 0:
                player_pos = list(spawner.pos)
            elif spawner.variant == 1:
                self.entities.append(Slime(list(spawner.pos), (11, 7), (-2, -2), self))
        self.player = Player(player_pos, (6, 7), (-1, -1), self, vj=-3.56, vx=1.0, friction=0.61, air_friction=0.66)
        self.world.window.add_shader('stuff', 'stuff.frag', 'default.vert')  # add shaders with mgl stuff
        self.world.window.set_camera_target(self.player)
        self.world.window.window.opacity = 1.0
        self.player_health = 0
        self.high_color_top = pygame.Color(99, 159, 91)
        self.low_color_top = pygame.Color(156, 102, 89)
        self.high_color_bottom = pygame.Color(55, 110, 73)
        self.low_color_bottom = pygame.Color(136, 67, 79)
        self.health_flash = [(254, 254, 215), 0]
        #self.items = [AnimatedItem(self.assets['game']['collectables/coin'], self, (xo * 4, 10), (0, -6), self.assets['game']['particle/particle'][0], mass=0.25, bounce=0.9, speed=0.5) for xo in range(100)]#Item(self, (30, 10), (0, -6), self.assets['game']['particle/particle'][0], mass=0.25, bounce=0.9)
        #self.slimes = [Slime((x * 40, -70), (11, 7), (-2, -2), self) for x in range(20)]#[Slime((500, -20), (11, 7), (-2, -2), self), Slime((100, -20), (11, 7), (-2, -2), self), Slime((110, -20), (11, 7), (-2, -2), self), Slime((50, -20), (11, 7), (-2, -2), self)]
        self.blaser_manager = BLaserManager(self)
        self.blaster = Blaster(self, self.assets['game']['blaster'], [10, 10], [0, 0], 'red')
        self.light = self.lighting.add_light(self.player.pos, [256, 256], color=(254, 254, 215))#(219, 188, 150))
        self.light_surf = self.lighting.update_lighting([0, 0])
        self.fire_flies = [[[random.random() * self.world.window.screen.get_width(), random.random() * self.world.window.screen.get_height()], random.random() * math.pi * 2, random.random() * 10 + 10, random.random() * 4 * random.choice([-1, 1]), self.lighting.add_light([0, 0], [5, 5], (221, 172, 70)), random.random()] for _ in range(20)]

    def secsec(self):
        self.health_flash[1] = min(self.health_flash[1] + 1 * self.dt, 10)
        if self.player.health > self.player.max_health * 0.15:
            outline(self.assets['game']['health_bar'], (8, 6), self.world.window.ui_surf, pygame.Color(22, 19, 35).lerp(self.health_flash[0], 1 - self.health_flash[1] * 0.1))
        else:
            outline(self.assets['game']['health_bar'], (8, 6), self.world.window.ui_surf, pygame.Color(22, 19, 35).lerp((254, 254, 215), (math.sin(self.time * 0.1) + 1) * 0.5).lerp((194, 89, 64), (math.sin(self.time * 0.037) + 1) * 0.5))
        target_health = self.player.health if self.player.ad >= 120 else 0
        self.player_health += (target_health - self.player_health) * 0.2 * self.dt
        surf = pygame.Surface((32, 8))
        pygame.draw.rect(surf, self.low_color_top.lerp(self.high_color_top, max(0, min(1, self.player_health / self.player.max_health))), (3, 2, 27 * max(0, min(1, self.player_health / self.player.max_health)), 2))
        pygame.draw.rect(surf, self.low_color_bottom.lerp(self.high_color_bottom, max(0, min(1, self.player_health / self.player.max_health))), (3, 4, 27 * max(0, min(1, self.player_health / self.player.max_health)), 2))
        surf.set_colorkey((0, 255, 0))
        surf.blit(self.assets['game']['health_bar'], (0, 0))
        self.world.window.ui_surf.blit(surf, (8, 6))

    def update(self, screen, scroll):
        if self.player.update():
            self.player.die()
        #self.item.box.draw(screen, scroll)
        self.player.draw(screen, scroll)
        self.light.update(self.player.pos)
        for fly in self.fire_flies:
            fly[0][0] += math.cos(fly[1]) * fly[2] * self.dt * 0.05
            fly[0][1] += math.sin(fly[1]) * fly[2] * self.dt * 0.05
            fly[1] += fly[3] * self.dt * 0.005
            if random.random() * 4 < self.dt:
                fly[3] = random.random() * 2 * random.choice([-1, 1])
                fly[2] = random.random() * 5 + 5
            loc = (((fly[0][0] - scroll[0]) % screen.get_width()) + scroll[0], ((fly[0][1] - scroll[1]) % screen.get_height()) + scroll[1])
            self.lighting.add_light(loc, [math.sin(self.time * 0.01 + fly[5] * 1000) * 2 + 5, math.sin(self.time * 0.01 + fly[5] * 1000) * 2 + 5], (221, 172, 70))

        #self.item.update(screen, scroll)
        #self.world.tile_map.leaves(screen, scroll)
        #self.world.tile_map.physics_map.draw(screen, scroll)
        if pygame.K_p in self.toggles:
            print(self.player.pos)
            print(f'''sparks: {len(self.world.gfx_manager.sparks)}
                smoke: {len(self.world.gfx_manager.smoke)}
                impact: {len(self.world.gfx_manager.impact)}
                shockwaves: {len(self.world.gfx_manager.shockwaves)}
                kick_up: {len(self.world.gfx_manager.kick_up)}
                shadows: {len(self.world.gfx_manager.shadows)}
                glow_dust: {len(self.world.gfx_manager.glow_dust)}
                slime: {len(self.world.gfx_manager.slime)}
                glow: {len(self.world.gfx_manager.glow)}
                particles: {len([particle for particle in self.world.gfx_manager.particles if particle.particle_type == 'particle'])}
                splat: {len(self.world.gfx_manager.splat)}
                trails: {len(self.world.gfx_manager.trails)}
                timed_coins: {len(self.world.gfx_manager.timed_coins)}
                glow_circle: {len(self.world.gfx_manager.glow_circle)}
                ''')
            #self.player.damage(5)
            self.blaster.fire(angle=random.random() - 0.5)
            #for layer in self.world.tile_map.layers:
            #   layer.stamp(self.assets['game']['large_decor'][0], (20, 80))
           # self.item.box.vel.y = -5
            #self.item.box.vel.x = 5
        #self.world.tile_map.physics_map.draw(screen, scroll)
        #for layer in self.world.tile_map.layers:
        #    layer.draw_tile_chunks(screen, scroll)
        self.blaser_manager.update(screen, scroll)
        self.blaster.draw(screen, scroll)
        self.light_surf = self.lighting.update_lighting(scroll)

    def run(self):
        while self.running:
            self.sec()

if __name__ == '__main__':
    app = App()
    app.run()