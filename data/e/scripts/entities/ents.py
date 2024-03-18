import pygame, math, random

from ..gfx.particles import Particle
from ..gfx.sparks import Spark
from ..gfx.anim import Animation
from ..bip import ENTITY_QUAD_SIZE, TILE_SIZE, SOOT

class EntityManager:
    def __init__(self, app):
        self.app = app
        self.ents_frame = {}
        self.entities_updated = 0
        self.entity_rects = []
    
    def get_quad(self, pos):
        loc = str(int(pos[0] / TILE_SIZE / ENTITY_QUAD_SIZE[0])) + ';' + str(int(pos[1] / TILE_SIZE / ENTITY_QUAD_SIZE[1]))
        if not loc in self.ents_frame:
            self.ents_frame[loc] = []
        return self.ents_frame[loc]
    
    def update(self, surf, scroll):
        self.entities_updated = 0
        self.entity_rects = []
        for y in range(math.ceil(surf.get_height() / (ENTITY_QUAD_SIZE[1] * TILE_SIZE)) + 2):
            for x in range(math.ceil(surf.get_width() / (ENTITY_QUAD_SIZE[0] * TILE_SIZE)) + 2):
                target_x = x - 2 + math.ceil(int(scroll[0]) / (ENTITY_QUAD_SIZE[0] * TILE_SIZE))
                target_y = y - 2 + math.ceil(int(scroll[1]) / (ENTITY_QUAD_SIZE[1] * TILE_SIZE))
                target_quad = f'{target_x};{target_y}'
                if target_quad in self.ents_frame:
                    for i, entity in sorted(enumerate(self.ents_frame[target_quad]), reverse=True):
                        kill = entity.update()
                        entity.draw(surf, scroll)
                        self.entities_updated += 1
                        self.entity_rects.append(entity.rect())
                        if kill:
                            entity.die()
                            self.ents_frame[target_quad].pop(i)
                            del entity
                        elif not self.get_quad(entity.pos) is entity.quad:
                            self.get_quad(entity.pos).append(entity)
                            self.ents_frame[target_quad].pop(i)
        self.entity_rects.append(self.app.player.rect())

class HealthBar:
    '''
    health_dim: actual size of section of health bar which shows health
    dim: size to be transformed to

    Used to show health of enemies
    '''
    def __init__(self, app, img, entity, health_dim: tuple, dim: tuple, offset: tuple, high_top_color=pygame.Color(99, 159, 91), high_bottom_color=pygame.Color(55, 110, 73), low_color_bottom=pygame.Color(136, 67, 79),
                 low_color_top=pygame.Color(156, 102, 89)):
        self.entity = entity
        self.app = app
        self.health_dim = tuple(health_dim)
        self.dim = tuple(dim)
        self.offset = tuple(offset)
        self.actual_size = img.get_size()
        self.img = img
        self.img.set_colorkey((0, 0 ,0))
        self.high_color_top = high_top_color
        self.high_color_bottom = high_bottom_color
        self.low_color_top = low_color_top
        self.low_color_bottom = low_color_bottom
        self.entity_health = self.entity.max_health
    
    def draw(self, screen, loc):
        self.entity_health += (self.entity.health - self.entity_health) * 0.2 * self.app.dt
        self.entity_health = max(0, self.entity_health)
        surf = pygame.Surface(self.actual_size)
        pygame.draw.rect(surf, self.low_color_top.lerp(self.high_color_top, self.entity_health / self.entity.max_health), (self.offset[0],
                                                                                                                            self.offset[1],
                                                                                                                            self.health_dim[0] * self.entity_health / self.entity.max_health,
                                                                                                                            self.health_dim[1] * 0.5))
        pygame.draw.rect(surf, self.low_color_bottom.lerp(self.high_color_bottom, self.entity_health / self.entity.max_health), (self.offset[0],
                                                                                                                                  self.offset[1] + self.health_dim[1] * 0.5,
                                                                                                                                  self.health_dim[0] * self.entity_health / self.entity.max_health,
                                                                                                                                  self.health_dim[1] * 0.5))
        surf.blit(self.img, (0, 0))
        surf.set_colorkey((0, 0, 0))
        screen.blit(pygame.transform.scale(surf, self.dim), loc)

#  Entity parent class
class Entity:
    def __init__(self, pos, dimensions, anim_offset, app, e_type, fiend=True, enemy=None, mask_collide_offset=None, hurt_recovery=1, hurt_flash=5, health=10, glow=False):
        self.pos = pygame.Vector2(pos)
        self.dimensions = pygame.Vector2(dimensions)
        self.anim_offset = pygame.Vector2(anim_offset)
        self.fiend = fiend
        self.enemy = enemy
        self.app = app
        self.mode = e_type
        self.state = 'idle'
        self.frames = {'idle': 0, 'run': 0}
        self.movement = pygame.Vector2(0, 0)
        self.collisions = {'left': False, 'right': False, 'up': False, 'down': False}
        self.flipped = False
        self.hurt_recovery = hurt_recovery
        self.hurt_flash = hurt_flash
        self.orig_anim_offset = pygame.Vector2(anim_offset)
        self.hit = False
        self.gravity = 0.3
        self.wall_jump = 0
        self.outside = pygame.Vector2(0, 0)
        self.health = health
        self.max_health = health
        self.platmode_collided = False
        self.ad = 99999999
        self.ad_limit = 0
        self.falling = 99
        self.controls = {'up': False}
        self.hurt = 99
        self.name = type(self).__name__
        if self.mode != 'player':
            self.quad = self.app.world.entity_manager.get_quad(self.pos)
            self.quad.append(self)
        self.name = type(self).__name__.lower()
        self.glow = False
        if glow:
            self.glow = True
            self.light = self.app.lighting.add_light(glow[0], glow[1], glow[2])

    def collide_mask(self, mask, pos):
        offset = (pos[0] - self.pos.x, pos[1] - self.pos.y)
        return self.hurt_mask.overlap(mask, offset)
    
    def distance_to(self, entity):
        return self.pos.distance_to(entity.pos)
    
    def __getitem__(self, item):
        return self.__dict__[item]
    
    def die(self):
        pass
    
    def get_colliding_ents(self, rect=None):
        entity_rect = rect if rect else self.rect()
        entities = []
        for y in range(3):
            for x in range(3):
                loc = str(int(self.pos[0] / TILE_SIZE / ENTITY_QUAD_SIZE[0]) + x - 1) + ';' + str(int(self.pos[1] / TILE_SIZE / ENTITY_QUAD_SIZE[1]) + y - 1)
                if loc in self.app.entity_manager.ents_frame:
                    for entity in self.app.entity_manager.ents_frame[loc]:
                        if entity.rect().colliderect(entity_rect):
                            entities.append(entity)
        return entities
    
    def get_neighbours(self):
        for y in range(3):
            for x in range(3):
                loc = str(int(self.pos[0] / TILE_SIZE / ENTITY_QUAD_SIZE[0]) + x - 1) + ';' + str(int(self.pos[1] / TILE_SIZE / ENTITY_QUAD_SIZE[1]) + y - 1)
                if loc in self.app.entity_manager.ents_frame:
                    for entity in self.app.entity_manager.ents_frame[loc]:
                        yield entity

    def copy(self):
        entity = Entity(self.pos, self.dimensions, self.anim_offset, self.app, self.mode, self.fiend, self.enemy)
        entity.__dict__ = dict(self.__dict__)
        entity.quad = self.app.entity_manager.get_quad(self.pos)
        return entity

    def chk(self, attr, val=None):
        if not hasattr(self, attr):
            setattr(self, attr, val)
        return getattr(self, attr)
    
    def palette(self):
        state = self.state if self.state != 'hurt' else 'idle'
        return self.app.palettes[self.name + '/' + state][math.floor(self.frames[self.state] % len(self.animation()))][0]

    def sec(self):
        self.chk('collisions', {'left': False, 'right': False, 'up': False, 'down': False})
        self.chk('state', 'idle')
        self.chk('mode')
        self.chk('pos')
        self.frames['hurt'] = 0
        self.hurt_mask = pygame.mask.from_surface(self.img().copy())
        hurt_surf = pygame.Surface(self.hurt_mask.get_size())
        hurt_surf.blit(self.hurt_mask.to_surface(), (0, 0))
        hurt_surf = pygame.transform.scale(hurt_surf, (hurt_surf.get_width() + 2, hurt_surf.get_height() + 2))
        hurt_surf.set_colorkey((0, 0, 0))
        self.app.assets['game'][self.name + '/' + 'hurt'] = [hurt_surf]
    
    def rect(self):
        return pygame.Rect(self.pos.x, self.pos.y, self.dimensions.x, self.dimensions.y)

    def handle_animations(self):
        self.hurt += self.hurt_recovery * self.app.dt
        self.anim_offset = pygame.Vector2(self.orig_anim_offset)
        if self.hurt < self.hurt_flash:
            self.state = 'hurt'
            self.anim_offset = pygame.Vector2(self.orig_anim_offset[0] - 1, self.orig_anim_offset[1] - 1)
            self.frames['hurt'] = 0
            return self.hurt
        return None
    
    def update(self):
        if self.movement.y > 6:  # terminal velocity
            self.movement.y = 6
        frame_movement = pygame.Vector2(self.movement.x + self.outside.x + self.wall_jump, self.movement.y + self.outside.y)

        self.pos.x += frame_movement.x * self.app.dt
        self.falling += 1 * self.app.dt
        for direction in self.collisions:
            if self.collisions[direction]:
                self.collisions[direction] += 1 * self.app.dt
            if self.collisions[direction] > 2:
                self.collisions[direction] = 0
        entity_rect = self.rect()
        for rect in self.app.world.tile_map.physics_map.physics_rects_around(self.pos):
            if rect.colliderect(entity_rect):
                if frame_movement.x * self.app.dt > 0:
                    self.collisions['right'] = 1
                    entity_rect.right = rect.left
                if frame_movement.x * self.app.dt < 0:
                    self.collisions['left'] = 1
                    entity_rect.left = rect.right
                self.pos.x = entity_rect.x
        self.pos.y += frame_movement.y * self.app.dt
        entity_rect = self.rect()
        for rect in self.app.world.tile_map.physics_map.physics_rects_around(self.pos):
            if rect.colliderect(entity_rect):
                if frame_movement.y * self.app.dt > 0:
                    self.collisions['down'] = 1
                    entity_rect.bottom = rect.top
                    if self.falling > 6:
                        for _ in range(int(min(self.falling * 0.1, 30))):
                            self.app.world.gfx_manager.add_kickup((self.rect().centerx, self.rect().bottom - 1), [random.uniform(-1, 1), random.uniform(-2, -0.2)], (77, 40, 49), random.randint(100, 220))
                            #angle = random.random() * math.pi * 2
                            #speed = random.random() * 0.5
                            #self.app.world.gfx_manager.smoke.append([list(self.rect().center), [math.cos(angle) * speed, math.sin(angle) * speed], 1, random.randint(200, 255), 0, random.randint(0, 360), (200, 200, 255)])
                    self.falling = 0
                if frame_movement.y * self.app.dt < 0:
                    self.collisions['up'] = 1
                    entity_rect.top = rect.bottom
                self.movement.y = 0
                self.outside.y = 0
                self.pos.y = entity_rect.y

        self.movement.y += self.gravity * self.app.dt
        if self.glow:
            self.light.update(self.pos)
        return self.health < 0 or self.app.world.tile_map.physics_map.danger_at(self.rect())

    def damage(self, intt=1):
        self.health -= intt
        self.hurt = 0

    def animation(self, mode=None):
        return self.app.assets['game'][self.name + '/' + (mode if mode else self.state)]

    def img(self) -> pygame.Surface:
        return pygame.transform.flip(self.animation()[math.floor(self.frames[self.state] % len(self.animation()))], self.flipped, False)

    def draw(self, surf, scroll=(0, 0)):
        self.handle_animations()
        surf.blit(self.img(), (self.pos.x - int(scroll.x) + self.anim_offset.x, self.pos.y - int(scroll.y) + self.anim_offset.y))

inAir = lambda entity: entity.falling > entity.fall_buff
xMotion = lambda entity: abs(entity.movement[0]) > 0.025
grounded = lambda entity: entity.grounded < entity.ground_buff

class PlayerBase(Entity):
    def __init__(self, pos, dimensions, anim_offset, app, air_friction=0.56, friction=0.54, vx=1.8, vj=-3, jump_buff=10, double_jump=1, gravity_apr=[0.2,0.4,0.1,1,0], out_dim=0.1,
             grounded_tim=2, jump_tim=1, fall_buff=6, ground_buff=24, jump_animbuff=70, mass=0.8):
        super().__init__(pos, dimensions, anim_offset, app, 'player', False, 'all')
        self.controls = {'up': False, 'down': False, 'left': False, 'right': False, 'climb': False}
        self.frames = {'idle': 0, 'jump': 0, 'run': 0, 'land': 0, 'wall_slide': 0, 'climb': 0}
        self.anim = {'idle': Animation(self, self.animation(mode='idle'), 0.2, True),
                     'jump': Animation(self, self.animation(mode='jump'), 0.4, False, indep=['falling', jump_animbuff]),
                     'run': Animation(self, self.animation(mode='run'), 0.26, True),
                     'land': Animation(self, self.animation(mode='land'), 0.0125, False, indep=['grounded', ground_buff]),
                     'wall_slide': Animation(self, self.animation(mode='wall_slide'), 1, True),
                     'climb': Animation(self, self.animation(mode='climb'), 0.26, True)}
        self.jumping = 99
        self.spawn_pos = pygame.Vector2(pos)
        self.mass = mass
        self.ground_buff = ground_buff
        self.double_jump = 1
        self.grounded = 0
        self.friction = friction
        self.air_friction = air_friction
        self.max_health = 10
        self.vx = vx
        self.jump_buff = jump_buff
        self.jumps = 0
        self.double_jump = double_jump
        self.ad = 122
        self.vj = vj
        self.gravity_apr = list(gravity_apr)
        self.out_dim = out_dim
        self.wall_slide = False
        self.grounded_tim = grounded_tim
        self.jump_tim = jump_tim
        self.dashing = 0
        self.fall_buff = fall_buff
        self.jumped = 99
        self.health = self.max_health
        self.ad_limit = 120
        self.sec()
    
    def die(self):
        self.app.world.tick.slomo = 0.0000001
        self.app.world.window.camera.add_screen_shake(8)
        #angle = math.atan2(-self.app.player.pos.y + self.pos.y, self.app.player.pos.x - self.pos.x)
        #dis = math.sqrt((self.app.player.pos.y - self.pos.y) ** 2 + (self.app.player.pos.x - self.pos.x) ** 2) ** 3 * 0.1
        #self.app.player.outside = -pygame.Vector2(math.sin(angle) / dis * 50, math.cos(angle) / dis * 50)
        self.state = 'idle'
        palette = self.palette()
        for _ in range(random.randint(25, 50)):
            angle = random.random() * math.pi * 2
            speed = random.random() + 1
            self.app.world.gfx_manager.smoke.append([list(self.rect().center), [math.cos(angle) * speed, math.sin(angle) * speed], 1, random.randint(200, 255), 0, random.randint(0, 360), (200, 200, 255)])
        for _ in range(random.randint(20, 40)):
            angle = random.random() * math.pi * 2
            speed = random.random() * 5
            self.app.world.gfx_manager.particles.append(Particle(self.app, 'particle', self.rect().center, [math.cos(angle + math.pi) * speed * 0.5, math.sin(angle + math.pi) * speed * 0.5], random.randint(0, 7)))
            self.app.world.gfx_manager.particle_systems['cinders'].append([list((self.rect().centerx, self.rect().bottom)), [math.cos(angle) * speed, math.sin(angle) * speed], random.randint(2, 20), random.choice(palette)])
            angle = random.random() * math.pi * 2
            speed = random.random() * 3 + 3
            self.app.world.gfx_manager.particles.append(Particle(self.app, 'particle', self.rect().center, [math.cos(angle + math.pi) * speed * 0.5, math.sin(angle + math.pi) * speed * 0.5], random.randint(0, 7)))
            self.app.world.gfx_manager.sparks.append(Spark(self.rect().center, angle, random.random() + 2, (255, 255, 255), scale=0.5, decay=0.02))
        for i in range(random.randint(35, 50)):
            angle = random.random() * math.pi * 2
            vel = random.random() * 5 + 2
            self.app.world.gfx_manager.add_kickup(self.rect().center, (math.cos(angle) * vel * 0.25, math.sin(angle) * vel * 2), random.choice(palette), random.randint(100, 200), friction=0.95, flags=pygame.BLEND_RGBA_ADD, bounce=0.5)
            if i % 3 == 0: self.app.world.gfx_manager.add_glow_dust(self.rect().center, (math.cos(angle) * vel * 0.2, math.sin(angle) * vel * 1.5), random.choice(palette), random.randint(100, 200), friction=0.95, bounce=0.5, flags=pygame.BLEND_RGBA_ADD)
        self.app.world.gfx_manager.radial(self.rect().center)
        for _ in range(20):
            angle = random.random() * math.pi * 2
            vel = random.random() * 2 + 2
            self.app.world.gfx_manager.slime.append([list(self.rect().center), [math.cos(angle) * vel, math.sin(angle) * vel], SOOT])
        for _ in range(100):
            angle = random.random() * math.pi * 2
            vel = random.random() * 5 + 5
            self.app.world.gfx_manager.splat.append([list(self.rect().center), [math.cos(angle) * vel, math.sin(angle) * vel], random.choice(palette), 3])
        for _ in range(random.randint(10, 15)):
            angle = random.random() * math.pi * 2
            vel = random.random() + 1
            size = random.random() * 2 + 3
            self.app.world.gfx_manager.glow_circle.append([list(self.pos), [vel * math.cos(angle), vel * math.sin(angle) - 2], size, size, random.choice(palette), random.random()])
        self.app.world.gfx_manager.shockwaves.append([list(self.rect().center), 0.01, (230, 215, 204), 1.2, 25])
        self.app.world.gfx_manager.trail(40, 2, [self.rect().centerx, self.rect().bottom])
        self.pos = pygame.Vector2(self.spawn_pos)
        self.health = self.max_health
        self.dashing = 0
        self.ad = 0
        self.falling = 99
        self.jumping = 99
        self.grounded = 0
    
    def damage(self, intt=1):
        palette = self.palette()
        self.app.world.tick.slomo = 0.00000000001
        for _ in range(40):
            angle = random.random() * math.pi * 2
            vel = random.random() * 2 + 3
            self.app.world.gfx_manager.splat.append([list(self.rect().center), [math.cos(angle) * vel, math.sin(angle) * vel], random.choice(palette), 3])
        for _ in range(4):
            angle = random.random() * math.pi * 0.25 - math.pi * 0.125
            self.app.world.gfx_manager.sparks.append(Spark([self.rect().centerx, self.rect().bottom], angle, random.random() * 2 + 2, (254, 254, 215), decay=1))
        for _ in range(4):
            angle = math.pi + random.random() * math.pi * 0.25 - math.pi * 0.125
            self.app.world.gfx_manager.sparks.append(Spark([self.rect().centerx, self.rect().bottom], angle, random.random() * 2 + 2, (254, 254, 215), decay=1))
        self.hurt = 0
        self.app.health_flash[1] = 0
        self.app.health_flash[0] = (254, 254, 215)
        return super().damage(intt)

    def update(self):
        self.ad += 1 * self.app.dt
        if self.ad >= 120:
            self.health = min(self.max_health, self.health + 0.00025 * self.app.dt)
            self.grounded += self.grounded_tim * self.app.dt
            self.jumping += self.jump_tim * self.app.dt
            if self.hurt > 3:
                self.controls = {'up': self.controls['up'], 'down': self.app.keys[pygame.K_DOWN] or self.app.keys[pygame.K_s], 'left': self.app.keys[pygame.K_LEFT] or self.app.keys[pygame.K_a], 'right': self.app.keys[pygame.K_RIGHT] or self.app.keys[pygame.K_d], 'climb': self.app.keys[pygame.K_UP] or self.app.keys[pygame.K_w]}
                if (pygame.K_z in self.app.toggles or pygame.K_k in self.app.toggles) and abs(self.dashing) < 40:
                    self.app.world.window.camera.add_screen_shake(3.5)
                    if self.flipped:
                        self.dashing = -60
                    else:
                        self.dashing = 60
            self.dashing = min(0, self.dashing + 1 * self.app.dt) if self.dashing < 0 else max(0, self.dashing - 1 * self.app.dt)
            if 50 < abs(self.dashing) < 60:
                self.movement[0] += self.dashing * 0.05
                if int(self.app.time * 2) % 2 == 0:
                    c1 = pygame.Color((81, 177, 202))
                    c2 = pygame.Color((255, 255, 255))
                    self.app.world.gfx_manager.glow.append([[self.rect().centerx, self.rect().centery], [0, 0], 1, c1.lerp(c2, random.random())])
                if abs(int(self.dashing)) in {51, 59}:
                    for _ in range(int(10 * self.app.dt)):
                        angle = random.random() * math.pi * 2 
                        speed = random.random() * 0.25
                        pvel = [math.cos(angle) * speed, math.sin(angle) * speed]
                        c1 = pygame.Color((81, 177, 202))
                        c2 = pygame.Color((255, 255, 255))

                        self.app.world.gfx_manager.glow.append([[self.rect().centerx, self.rect().centery], pvel, random.random() + 2, c1.lerp(c2, random.random())])
            if not self.wall_slide:
                self.controls['climb'] = False
            if self.controls['down']:
                if self.movement[1] < 0:
                    self.movement[1] *= 0.5
            if self.controls['left']:
                self.movement[0] -= self.vx * (5 - abs(self.wall_jump)) * 0.2
                self.flipped = True
            if self.controls['right']:
                self.movement[0] += self.vx * (5 - abs(self.wall_jump)) * 0.2
                self.flipped = False
            if pygame.K_w in self.app.toggles or pygame.K_UP in self.app.toggles:
                self.jumping = 0
            self.wall_slide = False
            if self.collisions['left'] or self.collisions['right']:
                if self.falling > self.fall_buff:
                    if self.collisions['right']:
                        self.flipped = False
                    else:
                        self.flipped = True
                    self.wall_slide = True
                    self.falling = self.fall_buff
                    self.movement[1] = min(self.movement[1], 1.0)
                    if random.random() / self.app.dt < 0.2:
                        pass
            #      if self.controls['up']:
            #         if self.flipped:
                #            self.wall_jump = 5
                #           self.movement[1] = -2
                #          self.jumping = self.jump_buff
                #     else:
                    #        self.wall_jump = -5
                    #       self.movement[1] = -2
                    #      self.jumping = self.jump_buff
                    if pygame.K_LEFT in self.app.toggles and not self.flipped:
                        self.wall_jump = -2.5
                        self.movement[1] = -2.8
                        self.jumping = self.jump_buff
                    if pygame.K_RIGHT in self.app.toggles and self.flipped:
                        self.wall_jump = 2.5
                        self.movement[1] = -2.8
                        self.jumping = self.jump_buff
            if self.falling < self.fall_buff:
                self.wall_jump = 0
            if self.controls['climb']:
                self.movement[1] = -1
            self.controls['up'] = self.jumping < self.jump_buff
            if self.controls['up']:
                if self.falling < self.fall_buff:
                    self.movement[1] = self.vj
                    self.falling = self.fall_buff + 1
                    self.jumping = self.jump_buff
            if not (self.falling > self.fall_buff and (self.controls['left'] or self.controls['right'])):
                self.movement[0] *= self.friction
            else:
                self.movement[0] *= self.air_friction
            if self.falling < self.fall_buff:
                self.jumps = 0
            if not self.jumps:
                if self.falling >= self.fall_buff:
                    self.jumps = 1
            if self.movement[1] ** 2 < self.gravity_apr[3]:
                self.gravity = self.gravity_apr[0] * self.mass
            else:
                self.gravity = self.gravity_apr[1] * self.mass
            if self.movement[1] > self.gravity_apr[4]:
                self.gravity += self.gravity_apr[2]
            self.wall_jump = min(self.wall_jump + 0.35 * self.app.dt, 0) if self.wall_jump < 0 else max(self.wall_jump - 0.35 * self.app.dt, 0)
            self.outside[0] = min(self.outside[0] + self.out_dim * self.app.dt, 0) if self.outside[0] < 0 else max(self.outside[0] - self.out_dim * self.app.dt, 0)
            self.outside[1] = min(self.outside[1] + self.out_dim * self.app.dt, 0) if self.outside[1] < 0 else max(self.outside[1] - self.out_dim * self.app.dt, 0)
            return super().update()
        else:
            return 0

    def handle_animations(self):
        if self.controls['climb']:
            self.state = 'climb'
            self.grounded = 0
            self.frames['climb'] = self.anim['climb'].update(self.app.dt)
        elif self.wall_slide:
            self.state = 'wall_slide'
            self.grounded = 0
            self.frames['wall_slide'] = self.anim['wall_slide'].update(self.app.dt)
        elif self.falling >= self.fall_buff:
            self.state = 'jump'
            self.grounded = 0
            self.frames['idle'] = -1
            self.frames['jump'] = self.anim['jump'].update(self.app.dt)
        elif round(self.movement[0]):
            self.state = 'run'
            self.frames['run'] = self.anim['run'].update(self.app.dt)
            self.frames['idle'] = -1
        elif self.grounded < self.ground_buff:
            self.state = 'land'
            self.frames['land'] = self.anim['land'].update(self.app.dt)
            self.frames['idle'] = -1
        else:
            self.state = 'idle'
            self.frames['idle'] = self.anim['idle'].update(self.app.dt)
            self.frames['run'] = 7
        return super().handle_animations()
