import pygame
from camera import Camera
from math import sin,cos

class Bullet:
    def __init__(self, x, y, angle, speed, radius, damage, area_radius, area_damage, despawn_distance=2000):
        self.x = x
        self.y = y
        self.angle = angle

        self.speed = speed
        self.radius = radius
        self.damage = damage
        self.area_radius = area_radius
        self.area_damage = area_damage
        
        self.despawn_distance = despawn_distance

    def move(self,dt):
        self.x += self.speed * cos(self.angle) * dt
        self.y += self.speed * sin(self.angle) * dt

    def update(self,dt,x,y):
        self.move(dt)

        sqrdist = (self.x - x)**2 + (self.y - y)**2
        return sqrdist <= self.despawn_distance**2

    def draw(self, screen : pygame.Surface, camera : Camera):
        screen_x, screen_y = camera.to_screen(self.x, self.y)
        pygame.draw.rect(screen, (255,0,0), (screen_x - 10, screen_y - 10, 20, 20))