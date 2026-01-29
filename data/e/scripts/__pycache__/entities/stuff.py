import pygame, math, random

from ..env.chunks import MovingQuads
from .box import Box

class Item:
    def __init__(self, app, pos, vel, img, bounce=0.5, friction=0.5, mass=1):
        self.app = app
        self.pos = pygame.Vector2(pos)
        self.img = img
        self.bounce = bounce
        self.friction = friction
        self.mass = mass
        self.box = Box(app, pos, img.get_size(), mass, friction, bounce)
        self.box.vel = pygame.Vector2(vel)
        self.dampening = 0.6
        self.tension = 0.2
        self.vel = pygame.Vector2(0, 0)
        self.settled = 0
        self.app.world.item_manager.add_item(self)
    
    def rect(self):
        return self.box.rect()

    def anchor(self):
        return self.box.update()

    def update(self, screen, scroll):
        anchor = self.anchor()
        if ((self.pos.x - self.app.player.pos.x) ** 2 + (self.pos.y - self.app.player.pos.y) ** 2) < 400:
            anchor = pygame.Vector2(self.app.player.rect().center)
            self.box.vel += ((self.pos - pygame.Vector2(self.box.rect().center)) - self.box.vel) * 0.5
        if self.app.player.rect().collidepoint(self.pos) and self.app.player.dashing < 50:
            for _ in range(random.randint(4, 6)):
                angle = random.random() * math.pi * 2
                vel = random.random() + 1
                size = random.random() * 2 + 3
                self.app.world.gfx_manager.glow_circle.append([list(self.pos), [vel * math.cos(angle), vel * math.sin(angle) - 2], size, size, pygame.Color((221, 172, 70)).lerp((219, 188, 150), random.random())])
            return 1
        if self.app.world.tile_map.physics_map.danger_at(self.rect()):
            for _ in range(random.randint(4, 6)):
                angle = random.random() * math.pi * 2
                vel = random.random() + 1
                size = random.random() * 2 + 3
                self.app.world.gfx_manager.glow_circle.append([list(self.pos), [vel * math.cos(angle) * 0.6, vel * math.sin(angle) - 3], size, size, pygame.Color((221, 172, 70)).lerp((219, 188, 150), random.random())])
            return 1
        force = pygame.Vector2(anchor.x - self.pos.x, anchor.y - self.pos.y) * self.tension
        self.vel += force * self.app.dt
        self.pos += self.vel * self.app.dt
        self.vel += (self.vel * self.dampening - self.vel) * self.app.dt
        loc = pygame.Vector2(self.pos.x - self.img.get_width() * 0.5, self.pos.y - self.img.get_height() * 0.5)
        yo = 0
        if abs(self.box.vel.x) < 1 and abs(self.box.vel.y) < 1:
            self.settled += 1 * self.app.dt
            if self.settled > 100:
                yo = math.sin((self.settled - 100) * 0.1) * 3
        else:
            self.settled = 0
        screen.blit(self.img, (loc[0] - scroll[0], loc[1] - scroll[1] + yo))

class AnimatedItem(Item):
    def __init__(self, animation:list, app, pos, vel, img, bounce=0.5, friction=0.5, mass=1, speed=0.2):
        super().__init__(app, pos, vel, img, bounce, friction, mass)
        self.animation = animation
        self.frame = 0
        self.speed = speed
    
    def update(self, *args, **kwargs):
        self.frame += self.speed * self.app.dt
        self.img = self.animation[math.floor(self.frame)%len(self.animation)]
        return super().update(*args, **kwargs)

class ItemManager:
    def __init__(self, app, items=[]):
        self.app = app
        self.items = items
        self.quads = MovingQuads(items, [20, 20])
    
    def add_item(self, item):
        self.items.append(item)
        self.quads.add_item(item)
    
    def update(self, screen, scroll):
        self.quads.update(screen, scroll, screen, scroll)