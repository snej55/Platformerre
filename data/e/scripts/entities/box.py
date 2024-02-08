import pygame, random

class Box:
    '''
    To be used to track a hitbox
    Mass is fictional value for changing gravity

    Attach a spring or something to this.
    Rendering is ugly.
    '''
    def __init__(self, app, pos, dimensions, mass=1, friction=0.9, bounce=0.5):
        self.app = app
        self.dimensions = pygame.Vector2(dimensions)
        self.pos = pygame.Vector2(pos)
        self.vel = pygame.Vector2(0, 0)
        self.mass = mass
        self.falling = 99
        self.gravity = 0.5 * mass
        self.bounce = bounce * mass
        self.friction = friction
        self.collisions = {'left': False, 'right': False, 'up': False, 'down': False}
    
    def rect(self):
        return pygame.Rect(self.pos, self.dimensions)

    def update(self):
        if self.vel.y > 6:  # terminal velocity
            self.vel.y = 6
        frame_vel = pygame.Vector2(self.vel.x, self.vel.y)

        self.pos.x += frame_vel.x * self.app.dt
        self.falling += 1 * self.app.dt
        for direction in self.collisions:
            if self.collisions[direction]:
                self.collisions[direction] += 1 * self.app.dt
            if self.collisions[direction] > 2:
                self.collisions[direction] = 0
        entity_rect = self.rect()
        for rect in self.app.world.tile_map.physics_map.physics_rects_around(self.pos):
            if rect.colliderect(entity_rect):
                self.pos.x -= frame_vel.x * self.app.dt
                self.vel.x *= -self.bounce
                #self.vel.y *= self.friction
                break
        self.pos.y += frame_vel.y * self.app.dt
        entity_rect = self.rect()
        self.vel.y += self.gravity * self.app.dt
        for rect in self.app.world.tile_map.physics_map.physics_rects_around(self.pos):
            if rect.colliderect(entity_rect):
                self.pos.y -= frame_vel.y * self.app.dt
                self.vel.y *= -self.bounce
                self.vel.x *= self.friction
                break
        return pygame.Vector2(self.rect().center)

    def draw(self, screen, scroll):
        pygame.draw.rect(screen, (255, 0, 0), (self.rect().x - scroll[0], self.rect().y - scroll[1], self.rect().width, self.rect().height))
        screen.set_at((self.rect().centerx - scroll[0], self.rect().centery - scroll[1]), (255, 255, 255))