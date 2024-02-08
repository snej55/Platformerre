import pygame, math

from data.e.scripts.gfx.anim import Animation
from data.e.scripts.gfx.particles import Shadow

# changes in sword

class Slash:
    def __init__(self, app, pos, flip=False, target=None, vflip=False):
        self.app = app
        self.anim = [pygame.transform.flip(img, flip, vflip) for img in list(app.assets['game']['slash'])]
        self.animation = Animation(self, self.app.assets['game']['slash'], 2)
        self.pos = list(pos)
        self.vflip = vflip
        self.flip = flip
        self.img = None
        self.target = target
        if self.target:
            self.offset = (self.target.pos[0] - self.pos[0], self.target.pos[1] - self.pos[1])
    
    def draw(self, surf, scroll):
        if self.target:
            self.pos[0] = self.target.pos[0] - self.offset[0]
            self.pos[1] = self.target.pos[1] - self.offset[1]
        self.img = self.anim[math.floor(self.animation.update(self.app.dt)) % len(self.anim)]
        surf.blit(self.img, (self.pos[0] - scroll[0], self.pos[1] - scroll[1]))

class Sword:
    def __init__(self, app, pos, target=None, offset=(0, 0)):
        self.pos = pygame.Vector2(pos)
        self.app = app
        self.target = target
        self.angle = 0
        self.offset = offset
        self.img = app.assets['game']['sword'].copy()
        self.attacking = False
        self.angle_offset = 90
        self.swing_dir = 0
        self.shadow_release = 0
        self.swing_vel = 0
        self.slash = None
        self.arm_length = 1.5
        self.attacked = 10
        self.target_turn = 180
        self.flipped = False
        self.target_dir = 1 * math.pi
        self.damp = 0.5
        self.attack_surf = pygame.Surface((32, 32))
        self.attack_mask = pygame.mask.from_surface(self.attack_surf)
        self.attack_offset = (0, 0)
    
    def attack(self):
        #self.app.world.window.camera.screen_shake = max(self.app.world.window.camera.screen_shake, 1)
        if self.target_dir == -math.pi * 0.25:
            self.target_dir = math.pi * 0.75
        else:
            self.target_dir = -math.pi * 0.25
        if self.target_turn == 90:
            self.target_turn = 200
        else:
            self.target_turn = 90
        self.attacking = True
        self.attacked = 0
        self.damp = 0.6
        if not self.flipped:
            self.slash = Slash(self.app, (self.target.rect().centerx - 5, self.target.pos[1] - 5), target=self.target, vflip=bool(self.target_dir == -math.pi * 0.25))
        else:
            self.slash = Slash(self.app, (self.target.rect().centerx - 10, self.target.pos[1] - 5), flip=True, target=self.target, vflip=bool(self.target_dir == -math.pi * 0.25))

    def update(self):
        self.attacked += 1 * self.app.dt
        self.shadow_release += 1 * self.app.dt
        if self.target:
            self.pos = list(self.target.rect().center)
        if not self.attacking:
            self.target_dir = -math.pi * 0.25
            self.target_turn = 90
        else:
            if self.angle + self.angle_offset > self.target_dir:
                self.damp = 0.5
            if self.attacked > 40:
                self.attacking = False
                self.attacked = 4
                self.damp = 0.4
        if self.attacking:
            if self.shadow_release > 2 and self.slash:
                if self.slash.animation.frame < 13:
                    self.shadow_release = 0
                    img_copy = pygame.transform.rotate(self.img, math.degrees(self.angle) - 90 + self.angle_offset)
                    self.flipped = False
                    offset = list(self.offset)
                    if self.target.flipped:
                        img_copy = pygame.transform.flip(img_copy, True, False)
                        self.flipped = True
                        offset[0] -= 3
                        offset[1] += 0
                    self.app.world.gfx_manager.shadows.append(Shadow(img_copy, (self.pos[0] + int(self.img.get_width() / 2) - int(img_copy.get_width() / 2) + offset[0], self.pos[1] + int(self.img.get_height() / 2) - int(img_copy.get_height() / 2)+ offset[1]),
                    self.app, self, decay=20, start_alpha=100))
        force = (-self.target_dir - self.angle) * 0.3
        self.swing_vel += force * self.app.dt
        self.angle += self.swing_vel * self.app.dt
        if self.flipped:
            self.pos[0] += -math.cos(-self.angle) * self.arm_length
            self.pos[1] += math.sin(-self.angle) * self.arm_length
        else:
            self.pos[0] += math.cos(-self.angle) * self.arm_length
            self.pos[1] += math.sin(-self.angle) * self.arm_length
        self.angle_offset = 90 + (self.target_turn - 90) * self.angle / self.target_dir
        self.swing_vel += (self.swing_vel * self.damp - self.swing_vel) * self.app.dt
    
    def draw(self, surf, scroll):
        img_copy = pygame.transform.rotate(self.img, math.degrees(self.angle) - 90 + self.angle_offset)
        self.flipped = False
        offset = list(self.offset)
        if self.target.flipped:
            img_copy = pygame.transform.flip(img_copy, True, False)
            self.flipped = True
            offset[0] -= 3
            offset[1] += 0
        surf.blit(img_copy, (self.pos[0] + int(self.img.get_width() / 2) - int(img_copy.get_width() / 2) - scroll[0] + offset[0], self.pos[1] + int(self.img.get_height() / 2) - int(img_copy.get_height() / 2) - scroll[1] + offset[1]))
        if self.slash:
            self.slash.draw(surf, scroll)
            if self.slash.animation.finished:
                self.slash = None
        self.attack_surf.fill((0, 0, 0, 0))
        if self.attacking and self.slash:
            self.attack_surf.blit(img_copy, (16 + int(self.img.get_width() / 2) - int(img_copy.get_width() / 2) + offset[0], 16 + int(self.img.get_height() / 2) - int(img_copy.get_height() / 2) + offset[1]))
            self.attack_surf.blit(self.slash.img, (16 - self.slash.offset[0], 16 - self.slash.offset[1]))
        self.attack_mask = pygame.mask.from_surface(self.attack_surf)
        self.attack_surf = self.attack_mask.to_surface()
        self.attack_offset = (self.target.pos.x - 16, self.target.pos.y - 16)
        return self.attack_mask, self.attack_offset