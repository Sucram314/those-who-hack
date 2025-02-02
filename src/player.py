import pygame
from camera import Camera

class Player:
    def __init__(self, x=0, y=0, health=100, radius=30, acceleration=40, friction=0.9):
        self.x = x
        self.y = y
        self.full_health = health
        self.health = health
        self.radius = radius

        self.xvel = 0
        self.yvel = 0

        self.acceleration = acceleration
        self.friction = friction

    def reset(self):
        self.x = 0
        self.y = 0
        self.health = self.full_health
        
        self.xvel = 0
        self.yvel = 0

    def move(self, dt, xinput, yinput):
        self.xvel += xinput * self.acceleration
        self.xvel *= self.friction

        self.yvel += yinput * self.acceleration
        self.yvel *= self.friction

        self.x += self.xvel * dt
        self.y += self.yvel * dt
    
    def update(self, dt, xinput, yinput):
        self.move(dt, xinput, yinput)

    def draw(self, screen : pygame.Surface, camera : Camera, is_game_over=False):
        screen_x, screen_y = camera.to_screen(self.x, self.y)

        pygame.draw.aacircle(screen, (127,127,127) if is_game_over else (255,255,255), (screen_x,screen_y), self.radius)