import pygame, math

class Impact:
    def __init__(self, pos, speed, angle, color, length=1):
        self.pos = list(pos)
        self.speed = speed
        self.color = tuple(color)
        self.angle = angle
        self.length = length
    
    def update(self, dt):
        self.pos[0] += math.cos(self.angle) * self.speed * dt
        self.pos[1] += math.sin(self.angle) * self.speed * dt
        self.speed -= 0.1 * dt
        return self.speed < 0
    
    def draw(self, surf, scroll=(0, 0)):
        pygame.draw.line(surf, self.color, (self.pos[0] - scroll[0], self.pos[1] - scroll[1]), (self.pos[0] - scroll[0] + math.cos(self.angle) * self.speed * self.length, self.pos[1] - scroll[1] + math.sin(self.angle) * self.speed * self.length))