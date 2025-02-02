import pygame
from camera import Camera
from math import sin,cos

class Bullet:
    def __init__(self, x, y, angle, speed, radius, damage, area_radius, area_damage, lifetime=1e999, despawn_distance=2000):
        self.x = x
        self.y = y
        self.angle = angle

        self.speed = speed
        self.radius = radius
        self.damage = damage
        self.area_radius = area_radius
        self.area_damage = area_damage
        
        self.lifetime = lifetime
        self.despawn_distance = despawn_distance
        self.despawn = False

    def instantiate(self, x, y, angle):
        return Bullet(x, y, angle, self.speed, self.radius, self.damage, self.area_radius, self.area_damage, self.lifetime, self.despawn_distance)

    def move(self,dt):
        self.x += self.speed * cos(self.angle) * dt
        self.y += self.speed * sin(self.angle) * dt

    def update(self,dt,x,y):
        self.move(dt)

        dx = x - self.x
        dy = y - self.y

        sqrdist = dx**2 + dy**2

        if sqrdist > self.despawn_distance**2:
            self.despawn = True

        self.lifetime -= dt
        if self.lifetime <= 0:
            self.despawn = True

    def draw(self, screen : pygame.Surface, camera : Camera):
        screen_x, screen_y = camera.to_screen(self.x, self.y)

        pygame.draw.aacircle(screen, (255,0,0), (screen_x, screen_y), self.radius)