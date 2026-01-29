import math, pygame, random

class PhysicsParticles:
    def __init__(self, game, trail=False, friction=0.999, bounce=0.7, explode=False, gravity=0.24, fade=False):
        self.trail = trail
        self.friction = friction
        self.bounce = -bounce
        self.particles = []
        self.gravity = gravity
        self.fade = fade
        self.explode = explode
        self.game = game
    
    def __getitem__(self, index: int):
        return self.particles[index]

    def append(self, item):
        self.particles.append(item)
    
    def update(self, surf, scroll=(0, 0)):
        for particle in self.particles.copy():
            if type(particle[3]) == tuple:
                particle[3] = list(particle[3])
            speed = (abs(particle[1][0]) + abs(particle[1][1]))
            particle[1][0] *= 0.999
            particle[0][0] += particle[1][0] * self.game.dt
            if self.game.world.tile_map.physics_map.solid_check(particle[0]):
                particle[0][0] -= particle[1][0] * self.game.dt
                particle[1][0] *= self.bounce
                particle[1][1] *= self.friction
            particle[1][1] += self.gravity * self.game.dt
            particle[1][1] *= 0.999
            particle[0][1] += particle[1][1] * self.game.dt
            if self.game.world.tile_map.physics_map.solid_check(particle[0]):
                particle[0][1] -= particle[1][1] * self.game.dt
                particle[1][1] *= self.bounce
                particle[1][0] *= self.friction
            if self.trail:
                angle = math.atan2(particle[1][1], particle[1][0])
                pygame.draw.polygon(surf, particle[3], [
                    (particle[0][0] - scroll[0], particle[0][1] - scroll[1]),
                    (particle[0][0] - math.cos(angle + math.pi * 0.5) - scroll[0], particle[0][1] - math.sin(angle + math.pi * 0.5) - scroll[1]),
                    (particle[0][0] - scroll[0] - particle[1][0] * 3, particle[0][1] - scroll[1] - particle[1][1] * 3),
                    (particle[0][0] - math.cos(angle + math.pi * -0.5) - scroll[0], particle[0][1] - math.sin(angle + math.pi * -0.5) - scroll[1]),
                ])
            else:
                pygame.draw.circle(surf, particle[3], (particle[0][0] - scroll[0], particle[0][1] - scroll[1]), particle[2] / 2)
            if self.fade:
                particle[3][1] = max(particle[3][1] - self.fade * self.game.dt, 0)
                particle[3][2] = max(particle[3][2] - self.fade * self.game.dt, 0)
                particle[3][0] = max(particle[3][0] - self.fade * self.game.dt, 0)
                if particle[3][2] == 0 and particle[3][1] == 0 and particle[3][0] == 0:
                    particle[2] = -1
            else:
                particle[2] -= (particle[2] / 20 + 0.0000001) * self.game.dt
            if self.explode:
                if random.random() / self.game.dt / min(1, particle[2]) < 0.01:
                    angle = random.random() * math.pi * 2
                    speed = random.random()
                    self.game.world.gfx_manager.smoke.append([list((particle[0][0], particle[0][1])), [math.cos(angle) * speed, math.sin(angle) * speed], 0.5, random.randint(200, 255), 0, random.randint(0, 360), (200, 200, 255)])
                if speed > 5:
                    self.game.world.gfx_manager.particles.append(Particle(self.game, 'particle', (particle[0][0], particle[0][1]), [0, 0], random.randint(2, 3)))
        
            if particle[2] < 0:
                self.particles.remove(particle)

class KickUp:
    def __init__(self, game, friction=0.9, bounce=0.8, gravity=0.24, decay=0.005):
        self.friction=friction
        self.bounce=bounce
        self.gravity=gravity
        self.decay = decay
        self.particles = []
        self.game = game
    
    def append(self, item):
        self.particles.append(item)
    
    @staticmethod
    def rect_surf(width, alpha, color):
        surf = pygame.Surface((width, width))
        try:
            surf.fill(color)
        except ValueError:
            print(color)
        surf.convert()
        surf.set_colorkey((0, 0, 0))
        surf.set_alpha(alpha)
        return surf
    
    def spawn(self, pos, vel, color, alpha, bounce=0.8, friction=0.9, decay=1, gravity=0.08):
        self.particles.append([list(pos), list(vel), alpha, tuple(color), bounce, friction, decay, gravity])
    
    def update(self, screen, scroll):
        for particle in self.particles.copy():
            if particle[0] in self.game:
                if abs(particle[1][0]) > 0.0005 or abs(particle[1][1]) > 0.0005:
                    particle[0][0] += particle[1][0] * self.game.dt
                    if self.game.world.tile_map.physics_map.solid_check(particle[0]):
                        particle[0][0] -= particle[1][0] * self.game.dt
                        particle[1][0] *= -particle[4]
                        particle[1][1] *= particle[5]
                    particle[1][1] += particle[7]
                    particle[0][1] += particle[1][1] * self.game.dt
                    if self.game.world.tile_map.physics_map.solid_check(particle[0]):
                        particle[0][1] -= particle[1][1] * self.game.dt
                        particle[1][1] *= -particle[4]
                        particle[1][0] *= particle[5]
                particle[2] -= particle[6] * self.game.dt
                screen.blit(self.rect_surf(1, particle[2], particle[3]), (particle[0][0] - 0.5 - scroll[0], particle[0][1] - 0.5 - scroll[1]))
                if particle[2] < 0:
                    self.particles.remove(particle)
            else:
                particle[2] -= particle[6] * self.game.dt * 4

class Particle:
    def __init__(self, game, particle_type, pos, vel=[0, 0], frame=0, solid=False, friction=(1, 1)):
        self.game = game
        self.particle_type = particle_type
        self.pos = list(pos)
        self.vel = list(vel)
        self.animation = self.game.assets['game']['particle/' + self.particle_type].copy()
        self.alpha = 255
        if self.particle_type == 'leaf':
            self.alpha = 10
        self.frame = frame % len(self.animation)
        self.done = False
        self.speed = 0.1
        self.solid = solid
        self.friction = pygame.Vector2(friction)
        self.timer = 0
    
    def img(self):
        self.frame += max(0.025, self.speed) * self.game.dt
        if self.frame >= len(self.animation):
            self.done = True
            return self.animation[-1]
        return self.animation[math.floor(self.frame)]
    
    def update(self):
        kill = False
        if self.done:
            if self.particle_type == 'particle':
                self.alpha -= 200 * self.game.dt
            self.alpha -= 2 * self.game.dt
            kill = self.particle_type == 'explode' or self.particle_type == 'star'
            if self.alpha < 15:
                kill = True
                self.alpha = 0
        else:
            self.alpha = min(255, self.alpha + 4 * self.game.dt)
        self.pos[0] += self.vel[0] * self.game.dt
        self.vel[0] += (self.vel[0] * self.friction.x - self.vel[0]) * self.game.dt
        if self.solid:
            check = self.game.world.tile_map.physics_map.solid_check(self.pos)
            if check: 
                self.pos[0] -= self.vel[0] * self.game.dt
                self.vel[0] = 0
        self.pos[1] += self.vel[1] * self.game.dt
        self.vel[1] += (self.vel[1] * self.friction.y - self.vel[1]) * self.game.dt
        if self.solid:
            check = self.game.world.tile_map.physics_map.solid_check(self.pos)
            if check:
                self.done = True
                self.vel[1] = 0
                self.vel[0] = 0
                self.speed = 0
        self.timer += 1 * self.game.dt
        if self.timer > 600:
            kill = True
            print(f'''
        solid: {self.solid}
        particle_type: {self.particle_type}
        done: {self.done}
        alpha: {self.alpha}
        frame: {self.frame}
        anim: {len(self.animation)}
        speed: {self.speed}
    ''')
        return kill
    
    def draw(self, surf, scroll):
        img = self.img()
        if self.pos in self.game:
            img.set_alpha(self.alpha)
            surf.blit(img, (self.pos[0] - scroll[0] - img.get_width() // 2, self.pos[1] - scroll[1] - img.get_height() // 2))

class Shadow:
    def __init__(self, surf, pos, app, target=None, start_alpha=200, decay=2):
        self.pos = list(pos)
        self.decay = decay
        self.surf = surf.copy()
        self.alpha = start_alpha
        self.target = target
        self.app = app
        if self.target:
            self.offset = (self.target.pos[0] - self.pos[0], self.target.pos[1] - self.pos[1])
    
    def draw(self, surf, scroll):
        self.alpha -= self.decay * self.app.dt
        self.surf.set_alpha(self.alpha)
        if self.target:
            self.pos[0] = self.target.pos[0] - self.offset[0]
            self.pos[1] = self.target.pos[1] - self.offset[1]
        surf.blit(self.surf, (self.pos[0] - scroll[0], self.pos[1] - scroll[1]))