import pygame
import sys

from player import Player
from camera import Camera
from bullet import Bullet
from weapon import Weapon
from enemy import Enemy
from particle import Particle

class Engine:
    def __init__(self,screen,fps):
        self.screen = screen
        self.width, self.height = screen.get_size()

        self.clock = pygame.time.Clock()
        self.fps = fps

        self.player = Player(0,0)
        self.camera = Camera(0,0,self.width,self.height)

        self.enemies : list[Enemy] = [Enemy(500,500,30,100,100,10),Enemy(500,600,30,100,100,10)]
        self.bullets : list[Bullet] = []
        self.particles : list[Particle] = []

        self.weapon_type = 0
        self.weapons = [Weapon(0.5,500,10,10,100,10)]

    def game_over(self):
        pass

    def update(self):
        dt = self.clock.tick(self.fps) / 1000
        pygame.event.pump()

        keys = pygame.key.get_pressed()

        if keys[pygame.K_ESCAPE]:
            pygame.quit()
            sys.exit()

        xinput = (keys[pygame.K_d] or keys[pygame.K_RIGHT]) - (keys[pygame.K_a] or keys[pygame.K_LEFT])
        yinput = (keys[pygame.K_w] or keys[pygame.K_UP]) - (keys[pygame.K_s] or keys[pygame.K_DOWN])

        self.screen.fill((0,0,0))

        #use ai to update weapon_type and shoot direction here
        
        self.player.update(dt,xinput,yinput)
        self.camera.follow(self.player.x, self.player.y)

        for weapon in self.weapons:
            weapon.update(dt)

        if keys[pygame.K_SPACE]:
            res = self.weapons[self.weapon_type].shoot(self.player.x, self.player.y)
            
            if res is not None:
                self.bullets.append(res)

        for enemy in self.enemies:
            enemy.update(dt, self.player.x, self.player.y)

            dx = self.player.x - enemy.x
            dy = self.player.y - enemy.y

            sqrdist = dx ** 2 + dy ** 2
            
            if sqrdist <= (enemy.radius + self.player.radius) ** 2:
                if enemy.delta_time >= enemy.attack_cooldown:
                    self.player.health -= enemy.damage
                    enemy.delta_time = 0

        area_damages : list[Bullet] = []
        
        for bullet in self.bullets:
            bullet.update(dt,self.player.x,self.player.y)
            
            for enemy in self.enemies:
                dx = enemy.x - bullet.x
                dy = enemy.y - bullet.y

                sqrdist = dx ** 2 + dy ** 2

                if sqrdist <= (bullet.radius + enemy.radius) ** 2:
                    enemy.health -= bullet.damage
                    bullet.despawn = True

                    if bullet.area_damage > 0:
                        area_damages.append(bullet)
                        self.particles.append(Particle(bullet.x, bullet.y, 0, 0, 0, 0, bullet.area_radius, 1))

                    break

        for bullet in area_damages:
            for enemy in self.enemies:
                dx = enemy.x - bullet.x
                dy = enemy.y - bullet.y

                sqrdist = dx ** 2 + dy ** 2

                if sqrdist <= (bullet.area_radius + enemy.radius) ** 2:
                    enemy.health -= bullet.area_damage

        self.enemies = [enemy for enemy in self.enemies if enemy.health > 0]
        self.bullets = [bullet for bullet in self.bullets if not bullet.despawn]
        self.particles = [particle for particle in self.particles if particle.update(dt)]

        if self.player.health <= 0:
            self.game_over()

    def draw(self):
        for particle in self.particles:
            particle.draw(self.screen, self.camera)

        for enemy in self.enemies:
            enemy.draw(self.screen, self.camera)

        for bullet in self.bullets: 
            bullet.draw(self.screen, self.camera)

        self.player.draw(self.screen, self.camera)

        pygame.display.flip()


if __name__ == "__main__":
    SCREEN = pygame.display.set_mode(flags=pygame.FULLSCREEN)
    FPS = 60

    engine = Engine(SCREEN, FPS)

    while True:
        engine.update()
        engine.draw()


