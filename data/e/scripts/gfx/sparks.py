import pygame, math

class Spark:
    def __init__(self, loc, angle, speed, color, scale=1, spinny=False, decay=0.1):
        self.loc = list(loc)
        self.angle = angle
        self.speed = speed
        self.scale = scale
        self.color = color
        self.alive = True
        self.decay = 0.1
        self.spinny = spinny

    def point_towards(self, angle, rate, dt):
        rotate_direction = ((angle - self.angle + math.pi * 3) % (math.pi * 2)) - math.pi
        try:
            rotate_sign = abs(rotate_direction) / rotate_direction
        except ZeroDivisionError:
            rotate_sign = 1
        if abs(rotate_direction) < rate:
            self.angle = angle
        else:
            self.angle += rate * rotate_sign * dt

    def calculate_movement(self, dt):
        return [math.cos(self.angle) * self.speed, math.sin(self.angle) * self.speed]

    # gravity and friction
    def velocity_adjust(self, friction, force, terminal_velocity, dt):
        movement = self.calculate_movement(dt)
        movement[1] = min(terminal_velocity, movement[1] + force * dt)
        movement[0] += (movement[0] * friction - movement[0]) * dt
        self.angle = math.atan2(movement[1], movement[0])

    def update(self, dt):
        movement = self.calculate_movement(dt)
        self.loc[0] += movement[0] * dt
        self.loc[1] += movement[1] * dt

        #self.point_towards(math.pi / 2, 0.02, dt)
        #self.velocity_adjust(0.975, 0, 1, dt)

        self.speed -= self.decay * dt

        return self.speed <= 0

    def draw(self, surf, scroll):
        if not self.spinny:
            points = [
                [self.loc[0] - scroll[0] + math.cos(self.angle) * self.speed * self.scale * 3, self.loc[1] - scroll[1] + math.sin(self.angle) * self.speed * self.scale * 3],
                [self.loc[0] - scroll[0] + math.cos(self.angle + math.pi / 2) * self.speed * self.scale * 0.5, self.loc[1] - scroll[1] + math.sin(self.angle + math.pi / 2) * self.speed * self.scale * 0.5],
                [self.loc[0] - scroll[0] - math.cos(self.angle) * self.speed * self.scale * 1, self.loc[1] - scroll[1] - math.sin(self.angle) * self.speed * self.scale * 1],
                [self.loc[0] - scroll[0] + math.cos(self.angle - math.pi / 2) * self.speed * self.scale * 0.5, self.loc[1] - scroll[1] - math.sin(self.angle + math.pi / 2) * self.speed * self.scale * 0.5],
                ]
        else:
            points = [
                (self.loc[0] + math.cos(self.angle + math.sin(self.speed * 20) * math.pi * 0.5) * self.speed * 3 - scroll.x, self.loc[1] + math.sin(self.angle + math.sin(self.speed * 20) * math.pi * 0.5) * self.speed * 3 - scroll.y),
                (self.loc[0] + math.cos(self.angle + math.pi * 0.125) * self.speed * 2 - scroll.x, self.loc[1] + math.sin(self.angle + math.pi * 0.125) * self.speed * 2 - scroll.y),
                (self.loc[0] + math.cos(self.angle + math.pi * 0.5) * self.speed * 0.5 - scroll.x, self.loc[1] + math.sin(self.angle + math.pi * 0.5) * self.speed * 0.5 - scroll.y),
                (self.loc[0] + math.cos(self.angle + math.pi) * self.speed * 3 - scroll.x, self.loc[1] + math.sin(self.angle + math.pi) * self.speed * 3 - scroll.y),
                (self.loc[0] + math.cos(self.angle - math.pi * 0.5) * self.speed * 0.5 - scroll.x, self.loc[1] + math.sin(self.angle - math.pi * 0.5) * self.speed * 0.5 - scroll.y),
                (self.loc[0] + math.cos(self.angle - math.pi * 0.125) * self.speed * 2 - scroll.x, self.loc[1] + math.sin(self.angle - math.pi * 0.125) * self.speed * 2 - scroll.y)
            ]
        pygame.draw.polygon(surf, self.color, points)

