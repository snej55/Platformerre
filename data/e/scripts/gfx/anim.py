import pygame, math

class Animation:
    def __init__(self, entity, anim, speed, loop=False, tim=[1], indep=None):
        self.anim = list(anim)
        self.speed = speed
        self.loop = loop
        self.entity = entity
        self.tim = list(tim)
        self.frame = 0
        self.indep = indep
        self.finished = False
    
    def update(self, dt):
        if self.indep:
            return math.floor(getattr(self.entity, self.indep[0]) / self.indep[1] * len(self.anim))%len(self.anim)
        if self.loop:
            self.frame += self.speed * dt / self.tim[math.floor(self.frame) % len(self.tim)]
            return self.frame
        else:
            self.frame = min(len(self.anim) - 0.5, self.frame + self.speed * dt / self.tim[math.floor(self.frame) % len(self.tim)])
            if self.frame >= len(self.anim) - 0.5:
                self.finished = True
            return self.frame