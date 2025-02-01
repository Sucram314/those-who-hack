import pygame

FOLLOW_RATE = 0.2

class Camera:
    def __init__(self,x,y,WIDTH,HEIGHT):
        self.x = x
        self.y = y

        self.WIDTH = WIDTH
        self.HEIGHT = HEIGHT

    def follow(self, x, y):
        self.x += (x - self.x) * FOLLOW_RATE
        self.y += (y - self.y) * FOLLOW_RATE

    def to_screen(self,x,y):
        screen_x = x - self.x + self.WIDTH/2
        screen_y = self.y - y + self.HEIGHT/2
        return screen_x, screen_y 