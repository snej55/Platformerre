import pygame

from pygame._sdl2 import Window

from data.e.scripts.bip import WIN_DIMENSIONS, RENDER_SCALE
from .mgl.mgl import MGL
from .camera import Camera

class Win:
    def start(self, app):
        self.app = app#
        self.camera = Camera(app, self)
        self.scroll = self.camera.scroll
        if 'icon' in self.app.assets['game']:
            pygame.display.set_icon(self.app.assets['game']['icon'])
        elif 'icon' in self.app.assets['edit']:
            pygame.display.set_icon(self.app.assets['edit']['icon'])
    
    def __init__(self, dur=1.0, color=(255, 255, 255), flags=pygame.DOUBLEBUF | pygame.OPENGL, start_dur=1.0):
        self.display = pygame.display.set_mode(WIN_DIMENSIONS, flags=flags)
        self.render_scroll = [0, 0]
        self.render_scale = pygame.Vector2(RENDER_SCALE, RENDER_SCALE)
        self.screen = pygame.Surface((self.display.get_width() / self.render_scale.x, self.display.get_height() / self.render_scale.y))
        self.ui_surf = self.screen.copy()
        self.alpha_surf = self.screen.copy()
        self.filter = self.screen.copy()
        self.vaos = {}
        self.mgl = MGL()
        self.add_shader('default', 'default.frag', 'default.vert')
        self.window = Window.from_display_module()
        self.window.opacity = 0
        dis = 0
        while dis ** 2 < self.display.get_height():
            self.display.fill((0, 0, 0))
            self.window.opacity = (dis ** 2) / self.display.get_height()
            dis += 0.1 * dur
            for i in range(4):
                pygame.draw.rect(self.display, color, (self.display.get_width() * 0.25 * i, 0, self.display.get_width() * 0.125, dis ** 2))
            for i in range(4):
                pygame.draw.rect(self.display, color, (self.display.get_width() * 0.25 * i + self.display.get_width() * 0.125, self.display.get_height() - dis ** 2, self.display.get_width() * 0.125, self.display.get_height()))
            screen_tex = self.mgl.surf_to_texture(self.display)
            self.shade({'default': {'tex': screen_tex, 'alpha_surf': self.alpha_surf, 'ui_surf': self.ui_surf}})
            pygame.display.flip()
        self.start_dur = start_dur

    def add_shader(self, name, frag_path, vert_path=None, buffer=None, vao_args=['2f 2f', 'vert', 'texcoord']):
        self.vaos[name] = self.mgl.render_object(frag_path, vert_path, vao_args, buffer)
        if name != 'default' and 'default' in self.vaos:
            del self.vaos['default']
            return 1
        return 0
    
    def set_camera_target(self, target):
        self.camera.target = target
    
    def sec(self):
        self.screen.fill((0, 0, 0))
        self.ui_surf.fill((0, 0, 0))
        self.alpha_surf.fill((0, 0, 0))
        self.render_scroll = self.camera.update()
        return self.screen, self.render_scroll

    def filt(self):
        if self.app.time * self.start_dur < 60:
            self.filter.fill((int(255 * (60 - self.app.time * self.start_dur) / 60), int(255 * (60 - self.app.time * self.start_dur) / 60), int(255 * (60 - self.app.time * self.start_dur) / 60)))
            self.screen.blit(self.filter, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
            self.ui_surf.blit(self.filter, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
            self.alpha_surf.blit(self.filter, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
    
    def draw(self, objects):
        for obj in objects:
            render_obj = getattr(self.app.world, obj)
            render_obj.draw(self.screen, self.render_scroll)
    
    def shade(self, uniforms, dest=None):
        for vao in self.vaos:
            rdest = None
            if dest:
                if vao in dest:
                    rdest = dest[vao]
            self.vaos[vao].render(rdest, uniforms[vao])
    
    def inflate(self):
        pygame.transform.scale_by(self.screen, self.render_scale, self.display)
        pygame.display.flip()