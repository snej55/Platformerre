import time, pygame

class Tick:
    def __init__(self, app, fps=0):
        self.app = app
        self.dt = 1
        self.last_time = time.time() - 1 / 60
        self.clock = pygame.time.Clock()
        self.fps = fps
        self.slomo = 1
    
    def update(self):
        self.dt = time.time() - self.last_time
        self.dt *= 60 * self.slomo
        self.slomo += (1 - self.slomo) / 12.5 * (self.dt / self.slomo)
        self.last_time = time.time()
        self.clock.tick(self.fps)