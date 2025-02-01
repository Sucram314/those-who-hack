import pygame

from player import Player
from camera import Camera
from bullet import Bullet
from weapon import Weapon
from enemy import Enemy
from cycle import Cycle
from particle import Particle

class Engine:
    def __init__(self,screen,fps):
        self.screen = screen
        self.width, self.height = screen.get_size()

        self.clock = pygame.time.Clock()
        self.fps = fps

        self.player = Player(0,0)
        self.camera = Camera(0,0,self.width,self.height)

        self.enemies : list[Enemy] = []
        self.bullets : list[Bullet] = []
        self.particles : list[Particle] = []

        self.weapon_type = 0
        self.weapons = [Weapon(0.5,Bullet(0,0,0,500,10,10,100,10)),
                        Weapon(1,Bullet(0,0,0,2000,5,50,0,0))]
        
        self.current_cooldown = 0

        self.cycles : list[Cycle] = [Cycle([Enemy(0,0,30,100,100,10)]*3),Cycle([Enemy(0,0,30,100,200,10)]*5,repeats=999)]
        self.cyclenum = 0

        self.input_resolution = 30
        self.input = [[0]*self.input_resolution for _ in range(self.input_resolution)]

    def game_over(self):
        pass

    def update(self):
        dt = self.clock.tick(self.fps) / 1000
        pygame.event.pump()

        keys = pygame.key.get_pressed()

        if keys[pygame.K_ESCAPE]:
            return True
        
        if keys[pygame.K_1]: self.weapon_type = 0
        if keys[pygame.K_2]: self.weapon_type = 1

        xinput = (keys[pygame.K_d] or keys[pygame.K_RIGHT]) - (keys[pygame.K_a] or keys[pygame.K_LEFT])
        yinput = (keys[pygame.K_w] or keys[pygame.K_UP]) - (keys[pygame.K_s] or keys[pygame.K_DOWN])

        self.screen.fill((0,0,0))

        #use ai to update weapon_type and shoot direction here
        
        self.player.update(dt,xinput,yinput)
        self.camera.follow(self.player.x, self.player.y)

        self.enemies.extend(self.cycles[self.cyclenum].update(dt, self.player.x, self.player.y))

        if self.cycles[self.cyclenum].repeats < 0:
            self.cyclenum += 1

        self.current_cooldown -= dt

        if keys[pygame.K_SPACE] and self.current_cooldown <= 0:
            cur_weapon = self.weapons[self.weapon_type]
            self.current_cooldown = cur_weapon.reload
            self.bullets.append(cur_weapon.shoot(self.player.x, self.player.y, 0))
            
        for enemy in self.enemies:
            enemy.update(dt, self.player.x, self.player.y)

            dx = self.player.x - enemy.x
            dy = self.player.y - enemy.y

            sqrdist = dx ** 2 + dy ** 2
            
            if sqrdist <= (enemy.radius + self.player.radius) ** 2:
                if enemy.delta_time >= enemy.attack_cooldown:
                    self.player.health -= enemy.damage
                    enemy.delta_time = 0

                magnitude = sqrdist ** 0.5
                normalized_x = dx / magnitude
                normalized_y = dy / magnitude

                depenetration =  magnitude - enemy.radius - self.player.radius

                enemy.x += normalized_x * depenetration
                enemy.y += normalized_y * depenetration

        for i in range(len(self.enemies)):
            enemy1 = self.enemies[i]

            for j in range(i):
                enemy2 = self.enemies[j]

                dx = enemy1.x - enemy2.x
                dy = enemy1.y - enemy2.y
                
                sqrdist = dx ** 2 + dy ** 2

                if sqrdist <= (enemy1.radius + enemy2.radius) ** 2:
                    magnitude = sqrdist ** 0.5
                    normalized_x = dx / magnitude
                    normalized_y = dy / magnitude

                    depenetration =  magnitude - enemy1.radius - enemy2.radius
                    ratio = enemy2.radius ** 2 / (enemy1.radius ** 2 + enemy2.radius ** 2)

                    enemy1.x -= normalized_x * depenetration * ratio
                    enemy1.y -= normalized_y * depenetration * ratio

                    enemy2.x += normalized_x * depenetration * (1 - ratio)
                    enemy2.y += normalized_y * depenetration * (1 - ratio)

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

        return False

    def draw(self):
        for particle in self.particles:
            particle.draw(self.screen, self.camera)

        for enemy in self.enemies:
            enemy.draw(self.screen, self.camera)

        for bullet in self.bullets: 
            bullet.draw(self.screen, self.camera)

        self.player.draw(self.screen, self.camera)
