import pygame, math, random

from data.e.scripts.entities.stuff import AnimatedItem
from data.e.scripts.entities.ents import Entity, PlayerBase
from data.e.scripts.gfx.particles import Particle
from data.e.scripts.gfx.sparks import Spark
from data.scripts.sword import Sword
from data.e.scripts.gfx.anim import Animation
from data.e.scripts.bip import SOOT
from data.e.scripts.tools.maf import direction_to
from data.e.scripts.entities.ents import HealthBar

class Player(PlayerBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sword = Sword(self.app, self.pos, self, offset=(-1, -6))
        self.sec()
    
    def update(self, *args):
        stuff = super().update(*args)
        if self.ad >= 120:
            self.outside += (self.outside * 0.96 - self.outside) * self.app.dt
            if pygame.K_x in self.app.toggles and self.sword.attacked > 10:
                self.sword.attack()
            self.sword.update()
        return stuff
    
    def draw(self, surf, scroll=(0, 0)):
        if self.ad >= 120:
            if abs(self.dashing) < 50:
                if self.sword.target_dir == -math.pi * 0.25:
                    self.sword.draw(surf, scroll)
                    return super().draw(surf, scroll)
                super().draw(surf, scroll)
                self.sword.draw(surf, scroll)

class Slime(Entity):
    def __init__(self, pos, dimensions, anim_offset, app, color='green', slime=(99, 159, 91)):
        super().__init__(pos, dimensions, anim_offset, app, e_type='slime')
        self.name += f'_{color}'
        self.slime = slime
        self.grounded = 0
        self.splat = True
        self.running = 0
        self.frames = {'idle': 0, 'run': 0, 'jump': 0}
        self.anim = {'idle': Animation(self, self.animation(mode='idle'), 0.25, True), 
                     'run': Animation(self, self.animation(mode='run'), 0.3, True),
                     'jump': Animation(self, self.animation(mode='jump'), 0.3, True)}
        self.attacking = False # niet aanvallen
        self.attack_tim = 0
        self.grounded = 0
        self.strength = 1
        self.health_bar = HealthBar(self.app, self.app.assets['game']['enemy_health_bar'], self, (13, 2), (16, 4), (2, 1))
        self.sec()

    def die(self):
        self.app.world.tick.slomo = 0.00001
        self.app.world.window.camera.add_screen_shake(6)
        #angle = math.atan2(-self.app.player.pos.y + self.pos.y, self.app.player.pos.x - self.pos.x)
        #dis = math.sqrt((self.app.player.pos.y - self.pos.y) ** 2 + (self.app.player.pos.x - self.pos.x) ** 2) ** 3 * 0.1
        #self.app.player.outside = -pygame.Vector2(math.sin(angle) / dis * 50, math.cos(angle) / dis * 50)
        self.state = 'idle'
        palette = self.palette()
        for _ in range(random.randint(15, 20)):
            angle = random.random() * math.pi * 2
            speed = random.random() + 1
            self.app.world.gfx_manager.smoke.append([list(self.rect().center), [math.cos(angle) * speed, math.sin(angle) * speed], 1, random.randint(200, 255), 0, random.randint(0, 360), (200, 200, 255)])
        for _ in range(random.randint(5, 10)):
            angle = random.random() * math.pi * 2
            speed = random.random() * 10
            self.app.world.gfx_manager.particles.append(Particle(self.app, 'particle', self.rect().center, [math.cos(angle + math.pi) * speed * 0.5, math.sin(angle + math.pi) * speed * 0.5], random.randint(0, 7)))
            self.app.world.gfx_manager.particle_systems['cinders'].append([list((self.rect().centerx, self.rect().bottom)), [math.cos(angle) * speed, math.sin(angle) * speed], random.randint(2, 20), random.choice(palette)])
            angle = random.random() * math.pi * 2
            speed = random.random() + 1
            self.app.world.gfx_manager.particles.append(Particle(self.app, 'particle', self.rect().center, [math.cos(angle + math.pi) * speed * 0.5, math.sin(angle + math.pi) * speed * 0.5], random.randint(0, 7)))
            self.app.world.gfx_manager.sparks.append(Spark(self.rect().center, angle, random.random() + 2, (255, 255, 255), scale=0.5, decay=0.02))
        for _ in range(15):
            angle = random.random() * math.pi * 2
            vel = random.random() * 5 + 5
            self.app.world.gfx_manager.splat.append([list(self.rect().center), [math.cos(angle) * vel, math.sin(angle) * vel], pygame.Color(self.slime).lerp((22, 19, 35), random.random() * 0.5), 2])
        for i in range(random.randint(35, 50)):
            angle = random.random() * math.pi * 2
            vel = random.random() * 5 + 2
            self.app.world.gfx_manager.add_kickup(self.rect().center, (math.cos(angle) * vel * 0.25, math.sin(angle) * vel * 2), random.choice(palette), random.randint(100, 200), friction=0.95, flags=pygame.BLEND_RGBA_ADD, bounce=0.5)
            if i % 3 == 0: self.app.world.gfx_manager.add_glow_dust(self.rect().center, (math.cos(angle) * vel * 0.2, math.sin(angle) * vel * 1.5), random.choice(palette), random.randint(100, 200), friction=0.95, bounce=0.5, flags=pygame.BLEND_RGBA_ADD)
        self.app.world.gfx_manager.radial(self.rect().center)
        for _ in range(5):
            angle = random.random() * math.pi * 2
            vel = random.random() + 1
            self.app.world.gfx_manager.slime.append([list(self.rect().center), [math.cos(angle) * vel, math.sin(angle) * vel], SOOT])
        self.app.world.gfx_manager.shockwaves.append([list(self.rect().center), 0.01, (230, 215, 204), 1.2, 25])
        if self.falling < 3:
            self.app.world.gfx_manager.trail(35, 1, [self.rect().centerx, self.rect().bottom])
        else:
            self.app.world.gfx_manager.trail(20, 2, [self.rect().centerx, self.rect().bottom])
        for _ in range(random.randint(2, 5)):
            self.app.world.gfx_manager.timed_coins.append([0, random.randint(1, 3) * 60, self.rect().center])
        for _ in range(random.randint(15, 30)):
            self.app.world.gfx_manager.timed_coins.append([0, random.randint(100, 1000) * 60, self.rect().center])
    
    def damage(self, intt, direction=math.pi * 0.5):
        self.app.world.window.camera.add_screen_shake(3.5)
        self.hit = True
        self.app.world.tick.slomo = 0.5
        state = self.state
        self.state = 'idle'
        palette = self.palette()
        self.state = state
        attack_dir = direction
        for _ in range(4):
            angle = attack_dir + random.random() * math.pi * 0.25 - math.pi * 0.125
            self.app.world.gfx_manager.sparks.append(Spark([self.app.player.rect().centerx, self.app.player.rect().bottom], angle, random.random() + 1, (254, 254, 215), decay=1))
        for _ in range(random.randint(4, 5)):
            angle = random.random() * math.pi * 2
            speed = random.random()
            self.app.world.gfx_manager.smoke.append([list(self.rect().center), [math.cos(angle) * speed, math.sin(angle) * speed], 0.5, random.randint(200, 255), 0, random.randint(0, 360), (200, 200, 255)])
        for _ in range(random.randint(10, 20)):
            angle = random.random() * math.pi * 2
            vel = random.random() * 2 + 2
            self.app.world.gfx_manager.add_kickup(self.rect().center, [math.cos(angle) * vel, math.sin(angle) * vel], random.choice(palette), random.randint(100, 200), friction=0.95, bounce=0.5)
            #self.app.world.gfx_manager.add_kickup(self.rect().center, [math.cos(angle) * vel, math.sin(angle) * vel], random.choice(palette), random.randint(100, 200))
        for _ in range(random.randint(20, 40)):
            angle = random.random() * math.pi * 2
            vel = random.random() * 2 + 2
            self.app.world.gfx_manager.splat.append([list(self.rect().center), [math.cos(angle) * vel, math.sin(angle) * vel], pygame.Color(self.slime).lerp((22, 19, 35), random.random() * 0.5), 2])
        for _ in range(random.randint(20, 30)):
            angle = random.random() * math.pi * 2
            speed = random.random() * 10
            self.app.world.gfx_manager.particle_systems['cinders'].append([list((self.rect().centerx, self.rect().bottom)), [math.cos(angle) * speed, math.sin(angle) * speed], random.randint(2, 20), random.choice(palette)])
        return super().damage(intt)
    
    def update(self, *args):
        if self.falling > 3:
            self.grounded = 0
        else:
            self.grounded += 1
        self.outside += (self.outside * 0.96 - self.outside) * self.app.dt
        if not self.attacking:
            if not self.running:
                if random.random() / self.app.dt < 0.01:
                    self.running = -0.1 if self.flipped else 0.1
                    for _ in range(random.randint(2, 3)):
                        angle = random.random() * math.pi * 0.5 + math.pi * 1.5 if self.flipped else random.random() * math.pi * 0.5 + math.pi
                        speed = random.random() * 2
                        self.app.world.gfx_manager.particle_systems['cinders'].append([list((self.rect().centerx, self.rect().bottom)), [math.cos(angle) * speed, math.sin(angle) * speed], random.randint(2, 20), self.slime])
            elif self.running:
                self.movement[0] += self.running
                if random.random() / self.app.dt < 0.9:
                    self.app.world.gfx_manager.slime.append([[self.rect().centerx - self.movement[0], self.rect().bottom], [(random.random() - 0.5) * 0.125, random.random() * 0.5], self.slime])
                offset = self.rect().width * -3 if self.flipped else self.rect().width * 3
                if random.random() / self.app.dt < 0.01:
                    self.running = 0
                    for _ in range(random.randint(2, 3)):
                        angle = random.random() * math.pi * 0.5 + math.pi * 1.5 if not self.flipped else random.random() * math.pi * 0.5 + math.pi
                        speed = random.random()
                        self.app.world.gfx_manager.particle_systems['cinders'].append([list((self.rect().centerx, self.rect().bottom)), [math.cos(angle) * speed, math.sin(angle) * speed], random.randint(2, 20), self.slime])
                elif not self.app.world.tile_map.physics_map.solid_check((self.rect().centerx + offset, self.rect().bottom + 2)) or self.app.world.tile_map.physics_map.solid_check((self.rect().centerx + offset, self.rect().centery)):
                    self.flipped = not self.flipped
                    self.running = 0
                    for _ in range(random.randint(2, 3)):
                        angle = random.random() * math.pi * 0.5 + math.pi * 1.5 if self.flipped else random.random() * math.pi * 0.5 + math.pi
                        speed = random.random()
                        self.app.world.gfx_manager.particle_systems['cinders'].append([list((self.rect().centerx, self.rect().bottom)), [math.cos(angle) * speed, math.sin(angle) * speed], random.randint(2, 20), self.slime])
            self.movement[0] *= 0.96
            self.grounded += 1 * self.app.dt
            if 200 < self.grounded < 201:
                for i in range(self.rect().width):
                    self.app.world.gfx_manager.slime.append([[self.rect().left + i, self.rect().bottom], [0, random.random() * 0.5], self.slime])
            if math.sqrt((self.app.player.rect().centery - self.rect().centery) ** 2 + (self.app.player.rect().centerx - self.rect().centerx) ** 2) < 40 and self.attack_tim > 100 and self.falling < 4:
                self.attacking = True
                self.attack_tim = 0
                self.app.world.window.camera.screen_shake = max(2, self.app.world.window.camera.screen_shake)
                self.movement[1] = -4
            self.attack_tim += 1 * self.app.dt
        else:
            self.attack_tim += 1 * self.app.dt
            if self.attack_tim > 90:
                self.attack_tim = 0
                self.attacking = False
            if random.random() / self.app.dt < 0.9 and self.falling < 5:
                angle = random.random() * math.pi * 0.5 + math.pi * 1.5 if not self.flipped else random.random() * math.pi * 0.5 + math.pi
                speed = random.random()
                self.app.world.gfx_manager.particle_systems['cinders'].append([list((self.rect().centerx, self.rect().bottom)), [math.cos(angle) * speed, math.sin(angle) * speed], random.randint(2, 20), self.slime])
                self.app.world.gfx_manager.slime.append([[self.rect().centerx - self.movement[0] + (random.random() - 0.5) * self.rect().width, self.rect().bottom], [0, random.random() * 0.5], self.slime])
            self.flipped = not self.app.player.rect().centerx > self.rect().centerx
            if 2 < self.grounded < 4:
                self.app.world.window.camera.add_screen_shake(3.5)
                if self.collide_mask(self.app.player.hurt_mask, self.app.player.pos):
                    palette = [(55, 110, 73), self.slime]
                    self.app.world.tick.slomo = 0.1
                    for _ in range(random.randint(20, 40)):
                        angle = random.random() * math.pi * 2
                        vel = random.random() * 2 + 2
                        self.app.world.gfx_manager.add_kickup(self.rect().center, [math.cos(angle) * vel, math.sin(angle) * vel], random.choice(palette), random.randint(100, 200))
                        # def add_kickup(self, pos, vel, color, alpha, bounce=0.7, gravity=0.1, friction=0.999, decay=1, flags=0):
                    self.app.player.damage(self.strength)
            if self.falling > 3:
                self.movement[0] = (self.app.player.rect().centerx - self.rect().centerx) * 0.1
            else:
                self.movement[0] *= 0.96
        if not self.hit:
            if self.collide_mask(self.app.player.hurt_mask, self.app.player.pos) and abs(self.app.player.dashing) > 50:
                self.damage(1, direction=direction_to(self.rect().center, self.app.player.rect().center))
                self.attack_tim = 90
            if self.collide_mask(self.app.player.sword.attack_mask, self.app.player.sword.attack_offset) or (self.app.player.sword.slash and self.collide_mask(self.app.player.hurt_mask, self.app.player.pos)):
                self.damage(2, direction=direction_to(self.rect().center, self.app.player.rect().center))
                self.attack_tim = 90
                dx = (self.app.player.pos.x - self.pos.x)
                force = (16 - min(abs(dx), 16)) / 16
                if dx == 0:
                    dx = 0.00000001
                self.outside.x += -dx / abs(dx) * force * 3
                dy = (self.app.player.pos.y - self.pos.y)
                force = (16 - min(abs(dy), 16)) / 12
                if dy == 0:
                    dy = 0.00001
                self.outside.y += -dy / abs(dy) * force * 5
        elif not self.app.player.sword.slash and self.hurt > self.hurt_flash:
            self.hit = False
        return super().update(*args)

    def handle_animations(self):
        if self.attacking:
            self.state = 'jump'
            self.frames['jump'] = self.anim['jump'].update(self.app.dt)
        elif not self.running:
            self.state = 'idle'
            self.frames['idle'] = self.anim['idle'].update(self.app.dt)
        else:
            self.state = 'run'
            self.frames['run'] = self.anim['run'].update(self.app.dt)
        return super().handle_animations()

    def draw(self, surf, scroll):
        if self.health < self.max_health:
            self.health_bar.draw(surf, (self.rect().centerx - 8 - scroll[0], self.rect().top - 4 - scroll[1]))
        return super().draw(surf, scroll)
    
