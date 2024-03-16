import pygame

class Lighting:
    def __init__(self, app):
        self.app = app
        self.light = pygame.image.load('data/e/scripts/gfx/light.png').convert()
        self.light_surf = pygame.Surface(self.app.world.window.screen.get_size())
        self.lights = []
    
    def add_light(self, pos, dimensions):
        light = Light(pos, self.app, self, dimensions)
        self.lights.append(light)
        return light
    
    def update_lighting(self, scroll):
        self.light_surf.fill((255, 255, 255))
        for light in self.lights:
            self.light_surf.blit(light.light_surf, (light.pos.x - scroll[0], light.pos.y - scroll[1]), special_flags=pygame.BLEND_RGBA_SUB)
        self.lights = []
        return self.light_surf

class Light:
    def __init__(self, pos, app, lighting, dimensions):
        self.app = app
        self.lighting = lighting
        self.light_surf = pygame.transform.scale(lighting.light, dimensions).convert()
        self.dimensions = pygame.Vector2(dimensions)
        self.pos = pygame.Vector2(pos)
    
    def update(self, pos=None):
        if pos: self.pos = pygame.Vector2(pos) - (self.dimensions * 0.5)
        self.lighting.lights.append(self)
