import pygame
from camera import Camera
from math import hypot

class Enemy:
    def __init__(self,x,y,radius,health,speed,damage,attack_cooldown=1):
        self.x = x
        self.y = y
        self.radius = radius

        self.health = health
        self.speed = speed
        self.damage = damage
        self.attack_cooldown = attack_cooldown

        self.delta_time = attack_cooldown

    def move(self,dt,x,y):
        dx = x - self.x
        dy = y - self.y

        magnitude = hypot(dx,dy)

        normalized_x = dx / magnitude
        noramlized_y = dy / magnitude

        self.x += normalized_x * self.speed * dt
        self.y += noramlized_y * self.speed * dt

    def update(self,dt,x,y):
        self.delta_time += dt
        self.move(dt,x,y)

    def draw(self, screen : pygame.Surface, camera : Camera):
        screen_x, screen_y = camera.to_screen(self.x, self.y)

        pygame.draw.aacircle(screen, (0,255,0), (screen_x, screen_y), self.radius)
