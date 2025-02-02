import pygame
import pygame.surfarray
import numpy as np
import pickle as pk
from math import hypot, pi, sin, cos

from model import Data, Aimer
from player import Player
from camera import Camera
from bullet import Bullet
from weapon import Weapon
from enemy import Enemy
from cycle import Cycle
from particle import Particle

def sigmoid(n):
    return 1/(1+np.exp(-n))

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
        self.upgrade = Button(self.load_to_scale("textures\\upgrade.png", 600, 600), 0, 0)

        self.input_layer_label = Asset(self.font[24].render("Input Layer",0,(255,255,255)), -375, -360 + 50)
        self.hidden_layer1_label = Asset(self.font[24].render("Hidden Layer 1",0,(255,255,255)), -125, -340 + 50)
        self.hidden_layer2_label = Asset(self.font[24].render("Hidden Layer 2",0,(255,255,255)), 125, -230 + 50)
        self.output_layer_label = Asset(self.font[24].render("Output Layer",0,(255,255,255)), 375, -190 + 50)

        self.weights1_label = Asset(self.font[16].render("Weights 1",0,(255,255,255)), -250, 350 + 50)
        self.weights2_label = Asset(self.font[16].render("Weights 2",0,(255,255,255)), 0, 285 + 50)
        self.weights3_label = Asset(self.font[16].render("Weights 3",0,(255,255,255)), 250, 210 + 50)

        self.bias1_label = Asset(self.font[16].render("Bias 1",0,(255,255,255)), -125, 340 + 50)
        self.bias2_label = Asset(self.font[16].render("Bias 2",0,(255,255,255)), 125, 230 + 50)
        self.bias3_label = Asset(self.font[16].render("Bias 3",0,(255,255,255)), 375, 190 + 50)

        self.data_generator_label = Asset(self.font[36].render("Data Generator",0,(255,255,255)), 0, -360)
        self.visualizer_label = Asset(self.font[36].render("Visualizer",0,(255,255,255)), 0, -360)
        self.trainer_label = Asset(self.font[36].render("Trainer",0,(255,255,255)), 0, -360)

    def load_to_scale(self, relative_path, w, h):
        return pygame.transform.scale(pygame.image.load(f"{self.directory}\\{relative_path}"),(w,h))

NORMAL_ZOMBIE = Enemy(0,0,30,100,150,10,10,(0,200,0))
FAST_ZOMBIE = Enemy(0,0,20,100,200,10,15,(0,255,0))
BIG_ZOMBIE = Enemy(0,0,40,200,100,20,15,(0,255,0))

class Engine:
    def __init__(self,screen,fps,directory):
        self.directory = directory
        self.scene = "menu"
        self.tab = "training"
        self.UI = UI(directory)

        self.screen : pygame.Surface = screen
        self.width, self.height = screen.get_size()

        self.clock = pygame.time.Clock()
        self.fps = fps

        self.player = Player()
        self.coins = 0
        self.tokens = 0
        self.angle = 0

        self.camera = Camera(self.width,self.height)

        self.enemies : list[Enemy] = []
        self.bullets : list[Bullet] = []
        self.particles : list[Particle] = []

        #weapons
        self.weapon_type = 0
        self.weapons = [Weapon(0.5,Bullet(0,0,0,500,10,10,100,10)),
                        Weapon(1,Bullet(0,0,0,2000,5,50,0,0))]
        
        self.current_cooldown = 0

        #waves
        self.cycles : list[Cycle] = [
            #Cycle([Enemy(0,0,30,float("inf"),0,0)]*5,repeats=float("inf")),
            Cycle([NORMAL_ZOMBIE]*3),
            Cycle([FAST_ZOMBIE]*5),
            Cycle([BIG_ZOMBIE]*3),
            Cycle([NORMAL_ZOMBIE, FAST_ZOMBIE, BIG_ZOMBIE]*2),
        ]

        self.cyclenum = 0
        self.currepeat = 0

        #input layer
        self.input_size = 800
        self.input_resolution = 20
        self.input_layer : np.ndarray = np.zeros((self.input_resolution ** 2, 1))
        self.input_surface : pygame.Surface = pygame.surface.Surface((self.input_size,self.input_size))
        self.downscaled = pygame.surface.Surface((self.input_resolution,self.input_resolution))

        self.prediction_cooldown = 0
        self.prediction_interval = 0.5

        #models
        #self.selector : Selector = Selector(Data(), self.input_resolution)
        self.aimer : Aimer = Aimer(Data(), self.input_resolution)

    def save(self):
        with open(f"{self.directory}\\data\\playerdata.pk","wb") as f:
            pk.dump((self.coins,self.tokens), f)

        # with open(f"{self.directory}\\data\\selector.pk","wb") as f:
        #     pk.dump(self.selector, f)

        with open(f"{self.directory}\\data\\aimer.pk","wb") as f:
            pk.dump(self.aimer, f)

    def load(self):
        try:
            with open(f"{self.directory}\\data\\playerdata.pk","rb") as f:
                self.coins, self.tokens = pk.load(f)

            # with open(f"{self.directory}\\data\\selector.pk","rb") as f:
            #     self.selector = pk.load(f)

            with open(f"{self.directory}\\data\\aimer.pk","rb") as f:
                self.aimer = pk.load(f)
        except:
            pass

    def reset(self):
        self.player.reset()
        self.angle = 0

        self.camera.reset()

        self.enemies : list[Enemy] = []
        self.bullets : list[Bullet] = []
        self.particles : list[Particle] = []

        self.weapon_type = 0
        self.current_cooldown = 0

        self.cyclenum = 0
        self.currepeat = 0

        self.prediction_cooldown = 0

    def game_over(self):
        pass

    def update_input(self):
        self.input_surface.fill((0,0,0))

        for enemy in self.enemies:
            enemy.input(self.player.x, self.player.y, self.input_size, self.input_surface)

        self.downscaled = pygame.transform.smoothscale(self.input_surface, (self.input_resolution, self.input_resolution))
        self.input_layer = np.reshape(pygame.surfarray.array2d(self.downscaled),(self.input_resolution**2,1)) / 0xffffff

    def add_example(self, x, y):
        # one_hot = np.zeros((len(self.weapons),1))
        # one_hot[self.weapon_type,0] = 1
        # self.selector.data.add_example(self.input_layer, one_hot, self.weapon_type)

        magnitude = hypot(x, y)
        x /= magnitude
        y /= magnitude

        one_hot = np.zeros((16,1))

        maxdot = float("-inf")
        best = 0
        for i in range(16):
            angle = 2 * pi * i / 16
            ax = cos(angle)
            ay = sin(angle)

            dot = x * ax + y * ay
            if dot > maxdot:
                maxdot = dot
                best = i

        one_hot[best,0] = 1

        self.aimer.data.add_example(self.input_layer, one_hot, best)

    def auto_add_example(self):
        x = 1
        y = 0
        minsqrdist = float("inf")

        for enemy in self.enemies:
            sqrdist = enemy.x ** 2 + enemy.y ** 2

            if sqrdist < minsqrdist:
                minsqrdist = sqrdist
                x = enemy.x
                y = enemy.y

        self.add_example(x,y)

    def train(self):
        #self.selector.train()
        self.aimer.train()
    
    def run_prediction(self):
        self.update_input()

        #self.weapon_type = self.selector.predict(self.input_layer)[0]
        prediction = self.aimer.predict(self.input_layer)[0]

        self.angle = 2 * pi * prediction / 16

    def update(self):
        dt = self.clock.tick(self.fps) / 1000
        pygame.event.pump()

        keys = pygame.key.get_pressed()
        curkeys = pygame.key.get_just_pressed()

        if curkeys[pygame.K_ESCAPE]:
            if self.scene == "menu":
                return True
            
            self.scene = "menu"
            self.reset()

        xinput = (keys[pygame.K_d] or keys[pygame.K_RIGHT]) - (keys[pygame.K_a] or keys[pygame.K_LEFT])
        yinput = (keys[pygame.K_w] or keys[pygame.K_UP]) - (keys[pygame.K_s] or keys[pygame.K_DOWN])

        mx, my = pygame.mouse.get_pos()
        left, middle, right, _, _ = pygame.mouse.get_just_pressed()

        self.screen.fill((0,0,0))

        if self.scene == "menu":
            if self.UI.play_button.update(self.width, self.height, mx, my, left, middle, right):
                self.scene = "game"
                self.UI.play_button.upscale = 1
            
            if self.UI.shopping_cart.update(self.width, self.height, mx, my, left, middle, right):
                self.scene = "shop"
                self.tab = "training"
                self.UI.shopping_cart.upscale = 1

        elif self.scene == "game":
            self.player.update(dt,xinput,yinput)
            self.camera.follow(self.player.x, self.player.y)

            stuff = self.cycles[self.cyclenum].update(dt, self.player.x, self.player.y)

            if stuff is not None:
                self.currepeat += 1
                self.enemies.extend(stuff)

                if self.currepeat == self.cycles[self.cyclenum].repeats:
                    self.cyclenum += 1
                    if self.cyclenum == len(self.cycles):
                        self.cyclenum -= 1

                    self.currepeat = 0

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

            for enemy in self.enemies:
                if enemy.health <= 0:
                    self.coins += enemy.value

            self.enemies = [enemy for enemy in self.enemies if enemy.health > 0]
            self.bullets = [bullet for bullet in self.bullets if not bullet.despawn]
            self.particles = [particle for particle in self.particles if particle.update(dt)]

            if self.player.health <= 0:
                self.game_over()

            self.prediction_cooldown -= dt

            if self.prediction_cooldown <= 0:
                self.prediction_cooldown = self.prediction_interval
                self.run_prediction()

            #self.screen.blit(self.input_surface,((self.width - self.input_size)/2, (self.height - self.input_size)/2))
        
        elif self.scene == "shop":
            if self.tab == "epoch":
                if curkeys[pygame.K_TAB]:
                    self.tab = "training"

                if self.UI.upgrade.update(self.width, self.height, mx, my, left, middle, right):
                    self.tokens += self.coins
                    self.coins = 0
                
            elif self.tab == "training":
                if curkeys[pygame.K_TAB]:
                    self.tab = "visual"

                if keys[pygame.K_EQUALS] or left:
                    #self.add_example(mx, my)
                    self.auto_add_example()

                    self.enemies = [*self.cycles[self.cyclenum].spawn(self.player.x, self.player.y, 100, 800)]
                    self.update_input()

                    self.currepeat += 1

                    if self.currepeat == self.cycles[self.cyclenum].repeats:
                        self.cyclenum += 1
                        if self.cyclenum == len(self.cycles):
                            self.cyclenum = 0

                        self.currepeat = 0

                if 1 or right:
                    self.train()

            elif self.tab == "visual":
                if curkeys[pygame.K_TAB]:
                    self.tab = "epoch"
        
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
            if self.tokens > 0:
                self.train()
                self.tokens -= 1

            if self.tab == "epoch":
                self.UI.upgrade.draw(self.screen, self.width, self.height)

                self.UI.trainer_label.draw(self.screen, self.width, self.height)

            elif self.tab == "training":
                for enemy in self.enemies:
                    enemy.draw(self.screen, self.camera)

                self.screen.blit(pygame.transform.scale(self.downscaled, (self.input_size, self.input_size)), (self.width/2 - self.input_size/2, self.height/2 - self.input_size/2))
                self.screen.fill((0,255,0),(self.width/2 - self.input_size/2, self.height/2 - self.input_size/2, self.input_size, self.input_size),special_flags=pygame.BLEND_MULT)
                pygame.draw.rect(self.screen,(255,0,0),(self.width/2 - self.input_size/2, self.height/2 - self.input_size/2, self.input_size, self.input_size), 5)

                self.player.draw(self.screen, self.camera)

                self.UI.data_generator_label.draw(self.screen, self.width, self.height)

                examples_text = self.UI.font[32].render(f"# of Examples: {self.aimer.data.output.shape[1]}",0,(255,255,255))
                w, h = examples_text.get_size()
                self.screen.blit(examples_text, (10, self.height-h-10))

            elif self.tab == "visual":

                #code by henry tian
                b1, b2, b3 = self.aimer.biases
                W1, W2, W3 = self.aimer.weights
                w = self.width
                h = self.height
                const = -50

                rad = 7
                dist = 5
                distbetweencols = 250

                numvis = 16
                distbetweenX = 50

                for i in range(b1.shape[0]):
                    x = w/2-0.5*distbetweencols
                    y = (h-((2*rad+dist)*b1.shape[0]-dist))/2+i*(rad*2+dist) - const
                    for j in range(numvis):
                        x2 = w/2-1.5*distbetweencols
                        y2 = (h-((2*rad+dist)*numvis*2-2*dist+distbetweenX))/2+j*(rad*2+dist) - const
                        pygame.draw.aaline(self.screen, (255-255*sigmoid(W1[i,j]),0,255*sigmoid(W1[i,j])), (x,y), (x2,y2))
                    for j in range(numvis,2*numvis):
                        x2 = w/2-1.5*distbetweencols
                        y2 = (h-((2*rad+dist)*numvis*2-2*dist+distbetweenX))/2+j*(rad*2+dist)+distbetweenX - const
                        pygame.draw.aaline(self.screen, (255-255*sigmoid(W1[i,j]),0,255*sigmoid(W1[i,j])), (x,y), (x2,y2))
                for i in range(b2.shape[0]):
                    x = w/2+0.5*distbetweencols
                    y = (h-((2*rad+dist)*b2.shape[0]-dist))/2+i*(rad*2+dist) - const
                    for j in range(len(W2[i])):
                        x2 = w/2-0.5*distbetweencols
                        y2 = (h-((2*rad+dist)*b1.shape[0]-dist))/2+j*(rad*2+dist) - const
                        pygame.draw.aaline(self.screen, (255-255*sigmoid(W2[i,j]),0,255*sigmoid(W2[i,j])), (x,y), (x2,y2))
                for i in range(b3.shape[0]):
                    x = w/2+1.5*distbetweencols
                    y = (h-((2*rad+dist)*b3.shape[0]-dist))/2+i*(rad*2+dist) - const
                    for j in range(len(W3[i])):
                        x2 = w/2+0.5*distbetweencols
                        y2 = (h-((2*rad+dist)*b2.shape[0]-dist))/2+j*(rad*2+dist) - const
                        pygame.draw.aaline(self.screen, (255-255*sigmoid(W2[i,j]),0,255*sigmoid(W2[i,j])), (x,y), (x2,y2))

                for i in range(numvis):
                    x = w/2-1.5*distbetweencols
                    y = (h-((2*rad+dist)*numvis*2-2*dist+distbetweenX))/2+i*(rad*2+dist) - const
                    pygame.draw.aacircle(self.screen, (255,255,255), (x,y), rad)

                bruh = (h-((2*rad+dist)*numvis*2-2*dist+distbetweenX))/2+(numvis-1)*(rad*2+dist) - const
                bruh2 = (h-((2*rad+dist)*numvis*2-2*dist+distbetweenX))/2+numvis*(rad*2+dist)+distbetweenX - const

                for i in range(3):
                    x = w/2-1.5*distbetweencols
                    y = (bruh + bruh2) / 2 + (i - 1) * (rad + dist)
                    pygame.draw.aacircle(self.screen, (255,255,255), (x,y), 2)

                for i in range(numvis,numvis*2):
                    x = w/2-1.5*distbetweencols
                    y = (h-((2*rad+dist)*numvis*2-2*dist+distbetweenX))/2+i*(rad*2+dist)+distbetweenX - const
                    pygame.draw.aacircle(self.screen, (255,255,255), (x,y), rad)
                    
                for i in range(b1.shape[0]):
                    x = w/2-0.5*distbetweencols
                    y = (h-((2*rad+dist)*b1.shape[0]-dist))/2+i*(rad*2+dist) - const
                    pygame.draw.aacircle(self.screen, (255-255*sigmoid(b1[i,0]),0,255*sigmoid(b1[i,0])), (x, y), rad)
                for i in range(b2.shape[0]):
                    x = w/2+0.5*distbetweencols
                    y = (h-((2*rad+dist)*b2.shape[0]-dist))/2+i*(rad*2+dist) - const
                    pygame.draw.aacircle(self.screen, (255-255*sigmoid(b2[i,0]),0,255*sigmoid(b2[i,0])), (x, y), rad)
                for i in range(b3.shape[0]):
                    x = w/2+1.5*distbetweencols
                    y = (h-((2*rad+dist)*b3.shape[0]-dist))/2+i*(rad*2+dist) - const
                    pygame.draw.aacircle(self.screen, (255-255*sigmoid(b3[i,0]),0,255*sigmoid(b3[i,0])), (x, y), rad)

                self.UI.input_layer_label.draw(self.screen, self.width, self.height)
                self.UI.hidden_layer1_label.draw(self.screen, self.width, self.height)
                self.UI.hidden_layer2_label.draw(self.screen, self.width, self.height)
                self.UI.output_layer_label.draw(self.screen, self.width, self.height)

                self.UI.weights1_label.draw(self.screen, self.width, self.height)
                self.UI.weights2_label.draw(self.screen, self.width, self.height)
                self.UI.weights3_label.draw(self.screen, self.width, self.height)

                self.UI.bias1_label.draw(self.screen, self.width, self.height)
                self.UI.bias2_label.draw(self.screen, self.width, self.height)
                self.UI.bias3_label.draw(self.screen, self.width, self.height)

                self.UI.visualizer_label.draw(self.screen, self.width, self.height)

        if self.scene != "menu":
            coin_text = self.UI.font[32].render(f"Coins: {self.coins}",0,(255,255,255))
            w, h = coin_text.get_size()
            self.screen.blit(coin_text, (self.width-w - 10, 10))

            accuracy_text = self.UI.font[32].render(f"Accuracy: {self.aimer.accuracy:.2%}",0,(255,255,255))
            w, h = accuracy_text.get_size()
            self.screen.blit(accuracy_text, (self.width-w - 10, self.height-h-10))

            iteration_text = self.UI.font[32].render(f"Epoch: {self.aimer.iteration}",0,(255,255,255))
            w2, h2 = iteration_text.get_size()
            self.screen.blit(iteration_text, (self.width-w2 - 10, self.height-h-h2-10))