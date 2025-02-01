import pygame
import sys

from player import Player
from camera import Camera
from bullet import Bullet
from weapon import Weapon

class Engine:
    def __init__(self,screen,fps):
        self.screen = screen
        self.width, self.height = screen.get_size()

        self.clock = pygame.time.Clock()
        self.fps = fps

        self.player = Player(0,0)
        self.camera = Camera(0,0,self.width,self.height)

        self.enemies = []
        self.bullets : list[Bullet] = []

        self.weapon_type = 0
        self.weapons = [Weapon(0.5,500,10,10,0,0)]

    def update(self):
        dt = self.clock.tick(self.fps) / 1000
        pygame.event.pump()

        keys = pygame.key.get_pressed()

        if keys[pygame.K_ESCAPE]:
            pygame.quit()
            sys.exit()

        xinput = (keys[pygame.K_d] or keys[pygame.K_RIGHT]) - (keys[pygame.K_a] or keys[pygame.K_LEFT])
        yinput = (keys[pygame.K_w] or keys[pygame.K_UP]) - (keys[pygame.K_s] or keys[pygame.K_DOWN])
        
        self.player.update(dt,xinput,yinput)
        self.camera.follow(self.player.x, self.player.y)

        self.bullets = [bullet for bullet in self.bullets if bullet.update(dt,self.player.x,self.player.y)]

        for weapon in self.weapons:
            weapon.update(dt)

        if keys[pygame.K_SPACE]:
            res = self.weapons[self.weapon_type].shoot(self.player.x, self.player.y)
            if res is not None:
                self.bullets.append(res)


        self.screen.fill((0,0,0))

        self.player.draw(self.screen, self.camera)

        for bullet in self.bullets: 
            bullet.draw(self.screen, self.camera)

        pygame.display.flip()

if __name__ == "__main__":
    SCREEN = pygame.display.set_mode(flags=pygame.FULLSCREEN)
    FPS = 60

    engine = Engine(SCREEN, FPS)

    while 1:
        engine.update()


