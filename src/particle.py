import pygame
from camera import Camera

class Particle:
    def __init__(self,x,y,xvel,yvel,xacc,yacc,radius,lifetime):
        self.x = x
        self.y = y
        self.xvel = xvel
        self.yvel = yvel
        self.xacc = xacc
        self.yacc = yacc
        self.radius = radius
        self.lifetime = lifetime
        self.initial_lifetime = lifetime

    def move(self,dt):
        self.xvel += self.xacc
        self.yvel += self.yacc

        self.x += self.xvel * dt
        self.y += self.yvel * dt

    def update(self,dt):
        self.lifetime -= dt

        self.move(dt)

        return self.lifetime > 0
    
    def draw(self, screen : pygame.Surface, camera : Camera):
        screen_x, screen_y = camera.to_screen(self.x, self.y)

        pygame.draw.circle(screen, (255*self.lifetime//self.initial_lifetime,127*self.lifetime//self.initial_lifetime,0), (screen_x, screen_y), self.radius)