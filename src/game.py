import pygame
import pygame.surfarray
import numpy as np

from model import Selector, Aimer
from player import Player
from camera import Camera
from bullet import Bullet
from weapon import Weapon
from enemy import Enemy
from cycle import Cycle
from particle import Particle

class Asset:
    def __init__(self, texture : pygame.Surface, x, y):
        self.texture = texture.convert()
        self.x = x
        self.y = y
        self.w, self.h = self.texture.get_size()

    def draw(self, screen : pygame.Surface, screen_width, screen_height):
        screen.blit(self.texture,(self.x + (screen_width - self.w) / 2, self.y + (screen_height - self.h) / 2)) 

class Button(Asset):
    def __init__(self, texture, x, y):
        super().__init__(texture, x, y)
        self.upscale = 1

    def update(self, screen_width, screen_height, mx, my, left, middle, right):
        target = 1

        if self.x + (screen_width - self.w) / 2 <= mx <= self.x + (screen_width + self.w) / 2 and self.y + (screen_height - self.h) / 2 <= my <= self.y + (screen_height + self.h) / 2:
            target = 1.2

            if left:
                return True

        self.upscale += (target - self.upscale) * 0.2

        return False

    def draw(self, screen : pygame.Surface, screen_width, screen_height):
        scaled = pygame.transform.smoothscale_by(self.texture,self.upscale)
        w,h = scaled.get_size()
        screen.blit(scaled,(self.x + (screen_width - w) / 2, self.y + (screen_height - h) / 2)) 

class UI:
    def __init__(self, directory):
        self.directory = directory

        self.font = [pygame.font.Font(f"{self.directory}\\pixelmix\\pixelmix.ttf",i) for i in range(128)]

        self.title = Asset(self.font[100].render("neuroAImers",0,(255,255,255)), 0, -200)
        self.shopping_cart = Button(self.load_to_scale("textures\\shopping_cart.png", 300, 300), 200, 100)
        self.play_button =  Button(self.load_to_scale("textures\\play.png", 300, 300), -200, 100)

    def load_to_scale(self, relative_path, w, h):
        return pygame.transform.scale(pygame.image.load(f"{self.directory}\\{relative_path}"),(w,h))

class Engine:
    def __init__(self,screen,fps,directory):
        self.scene = "menu"
        self.UI = UI(directory)

        self.screen : pygame.Surface = screen
        self.width, self.height = screen.get_size()

        self.clock = pygame.time.Clock()
        self.fps = fps

        self.player = Player(0,0)
        self.angle = 0

        self.camera = Camera(0,0,self.width,self.height)

        self.enemies : list[Enemy] = []
        self.bullets : list[Bullet] = []
        self.particles : list[Particle] = []

        #weapons
        self.weapon_type = 0
        self.weapons = [Weapon(0.5,Bullet(0,0,0,500,10,10,100,10)),
                        Weapon(1,Bullet(0,0,0,2000,5,50,0,0))]
        
        self.current_cooldown = 0

        #waves
        self.cycles : list[Cycle] = [Cycle([Enemy(0,0,30,100,100,10)]*3),Cycle([Enemy(0,0,30,100,200,10)]*5,repeats=999)]
        self.cyclenum = 0

        #input layer
        self.input_size = 600
        self.input_resolution = 20
        self.input_layer : np.ndarray = np.zeros(self.input_resolution ** 2)
        self.input_surface : pygame.Surface = pygame.surface.Surface((self.input_size,self.input_size))

        self.prediction_cooldown = 0
        self.prediction_interval = 0.5

        #models
        self.selector : Selector = Selector(self.input_resolution)
        self.aimer : Aimer = Aimer(self.input_resolution)

    def game_over(self):
        pass

    def update_input(self):
        self.input_surface.fill((0,0,0))

        for enemy in self.enemies:
            enemy.input(self.player.x, self.player.y, self.input_size, self.input_surface)

        downscaled = pygame.transform.smoothscale(self.input_surface, (self.input_resolution, self.input_resolution))
        self.input_layer = np.reshape(pygame.surfarray.array2d(downscaled),(self.input_resolution**2,1)) / 0xffffff

    def run_prediction(self):
        self.update_input()

        self.weapon_type = np.argmax(self.selector.predict(self.input_layer))

        prediction_x, prediction_y = self.aimer.predict(self.input_layer)[0]
        self.angle = np.arctan2(prediction_x, prediction_y)

    def update(self):
        dt = self.clock.tick(self.fps) / 1000
        pygame.event.pump()

        keys = pygame.key.get_pressed()
        curkeys = pygame.key.get_just_pressed()

        if curkeys[pygame.K_ESCAPE]:
            if self.scene == "menu":
                return True
            
            self.scene = "menu"

        xinput = (keys[pygame.K_d] or keys[pygame.K_RIGHT]) - (keys[pygame.K_a] or keys[pygame.K_LEFT])
        yinput = (keys[pygame.K_w] or keys[pygame.K_UP]) - (keys[pygame.K_s] or keys[pygame.K_DOWN])

        mx, my = pygame.mouse.get_pos()
        left, middle, right, _, _ = pygame.mouse.get_just_pressed()

        self.screen.fill((0,0,0))

        if self.scene == "menu":
            if self.UI.play_button.update(self.width, self.height, mx, my, left, middle, right):
                self.scene = "game"
            
            if self.UI.shopping_cart.update(self.width, self.height, mx, my, left, middle, right):
                self.scene = "shop"

        elif self.scene == "game":
            self.player.update(dt,xinput,yinput)
            self.camera.follow(self.player.x, self.player.y)

            self.enemies.extend(self.cycles[self.cyclenum].update(dt, self.player.x, self.player.y))

            if self.cycles[self.cyclenum].repeats < 0:
                self.cyclenum += 1

            self.current_cooldown -= dt

            if keys[pygame.K_SPACE] and self.current_cooldown <= 0:
                cur_weapon = self.weapons[self.weapon_type]
                self.current_cooldown = cur_weapon.reload
                self.bullets.append(cur_weapon.shoot(self.player.x, self.player.y, self.angle))
                
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


            self.prediction_cooldown -= dt

            if self.prediction_cooldown <= 0:
                self.prediction_cooldown = self.prediction_interval
                self.run_prediction()
        
        elif self.scene == "shop":
            pass
        
        return False

    def draw(self):
        if self.scene == "menu":
            self.UI.title.draw(self.screen,self.width,self.height)
            self.UI.play_button.draw(self.screen,self.width,self.height)
            self.UI.shopping_cart.draw(self.screen,self.width,self.height)

        elif self.scene == "game":
            for particle in self.particles:
                particle.draw(self.screen, self.camera)

            for enemy in self.enemies:
                enemy.draw(self.screen, self.camera)

            for bullet in self.bullets: 
                bullet.draw(self.screen, self.camera)

            self.player.draw(self.screen, self.camera)

        elif self.scene == "shop":
            pass
