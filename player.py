import pygame
from camera import Camera

class Player:
    def __init__(self, x, y, acceleration=40, friction=0.9):
        self.x = x
        self.y = y

        self.xvel = 0
        self.yvel = 0

        self.acceleration = acceleration
        self.friction = friction

    def move(self, dt, xinput, yinput):
        self.xvel += xinput * self.acceleration
        self.xvel *= self.friction

        self.yvel += yinput * self.acceleration
        self.yvel *= self.friction

        self.x += self.xvel * dt
        self.y += self.yvel * dt
    
    def update(self, dt, xinput, yinput):
        self.move(dt, xinput, yinput)

    def draw(self, screen : pygame.Surface, camera : Camera):
        screen_x, screen_y = camera.to_screen(self.x, self.y)

        pygame.draw.rect(screen, (255,255,255), (screen_x - 25, screen_y - 25, 50, 50))