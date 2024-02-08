import pygame, sys, time, json
from data.e.scripts.assets import GAME_ASSETS

class App:
    def __init__(self):
        self.display = pygame.display.set_mode((500, 500))
        self.screen = pygame.Surface((250, 250))
        self.dt = 1
        self.last_time = time.time() - 1 / 60
        self.clock = pygame.time.Clock()
        self.running = True
        self.config = {}
        for mode in GAME_ASSETS:
            if 'decor' in str(mode).lower():
                self.config[mode] = {}
                for variant, img in enumerate(GAME_ASSETS[mode]):
                    self.config[mode][variant] = [img, None, (0, 0)]
        self.scrolling = 0
        self.left = 0
        self.right = 0
        self.mouse_down = False
        self.mouse_pos = [0, 0]
        self.click_pos = [0, 0]
        self.select_rect = pygame.Rect(min(self.mouse_pos[0], self.click_pos[0]), min(self.mouse_pos[1], self.click_pos[1]), abs(self.mouse_pos[0] - self.click_pos[0]), abs(self.mouse_pos[1] - self.click_pos[1]))
        self.back_space = False
        self.enter = False
    
    def close(self):
        self.running = False
        pygame.quit()
        sys.exit()
    
    def save(self, path='data/config/leaf.json'):
        with open(path, 'w') as f:
            dump = {}
            for mode in self.config:
                dump[mode] = {}
                for variant in self.config[mode]:
                    dump[mode][variant] = [self.config[mode][variant][1], self.config[mode][variant][2]]
            json.dump(dump, f)
            f.close()
    
    def update(self):
        self.mouse_pos = pygame.mouse.get_pos()
        self.mouse_pos = [coord * 0.5 for coord in self.mouse_pos]
        i = 0
        for mode in self.config:
            for variant in self.config[mode]:
                img = self.config[mode][variant][0]
                rect = pygame.Rect(self.scrolling + i, 0, img.get_width(), img.get_height())
                if rect.collidepoint(self.mouse_pos[0], self.mouse_pos[1]):
                    pygame.draw.rect(self.screen, (100, 100, 100), rect)
                    if self.mouse_down:
                        self.select_rect = pygame.Rect(min(self.mouse_pos[0], self.click_pos[0]), min(self.mouse_pos[1], self.click_pos[1]), abs(self.mouse_pos[0] - self.click_pos[0]), abs(self.mouse_pos[1] - self.click_pos[1]))
                        pygame.draw.rect(self.screen, (255, 0, 0), self.select_rect, 1)
                        if self.enter:
                            self.config[mode][variant][1] = (self.select_rect.x - (self.scrolling + i), self.select_rect.y, self.select_rect.width, self.select_rect.height)
                            self.config[mode][variant][2] = (self.scrolling + i, self.select_rect.y)
                            self.mouse_down = False
                    if self.config[mode][variant][1]:
                        pygame.draw.rect(self.screen, (255, 255, 0), self.config[mode][variant][1], 1)
                    if self.back_space:
                        self.config[mode][variant][1] = None
                        self.config[mode][variant][2] = (0, 0)
                self.screen.blit(img, (self.scrolling + i, 0))
                i += img.get_width() + 2
    
    def run(self):
        while self.running:
            self.dt = time.time() - self.last_time
            self.dt *= 60
            self.last_time = time.time()
            self.screen.fill((0, 0, 0))
            self.scrolling -= (self.right - self.left) * self.dt
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.close()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.close()
                    if event.key == pygame.K_a:
                        self.left = 1
                    if event.key == pygame.K_d:
                        self.right = 1
                    if event.key == pygame.K_BACKSPACE:
                        self.back_space = True
                    if event.key == pygame.K_RETURN:
                        self.enter = True
                    if event.key == pygame.K_o:
                        self.save()
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_a:
                        self.left = 0
                    if event.key == pygame.K_d:
                        self.right = 0
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.mouse_down = True
                        self.mouse_pos = pygame.mouse.get_pos()
                        self.mouse_pos = [coord * 0.5 for coord in self.mouse_pos]
                        self.click_pos = self.mouse_pos
                if event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        self.mouse_down = False
            self.update()
            self.back_space = False
            self.enter = False
            pygame.transform.scale_by(self.screen, 2.0, self.display)
            pygame.display.set_caption(f'FPS: {self.clock.get_fps() :.1f}')
            pygame.display.flip()
            self.clock.tick(60)

if __name__ == '__main__':
    App().run()
