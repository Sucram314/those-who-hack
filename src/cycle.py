import random
from math import sin,cos,pi
from enemy import Enemy

class Cycle:
    def __init__(self, enemies : list[Enemy], repeats=3, interval=10, min_spawn_distance=900, max_spawn_distance=1100):
        self.enemies = enemies
        self.repeats = repeats
        self.interval = interval

        self.min_spawn_distance = min_spawn_distance
        self.max_spawn_distance = max_spawn_distance

        self.delta_time = interval

    def spawn(self, x, y):
        for enemy in self.enemies:
            angle = random.uniform(0, 2*pi)
            dist = random.uniform(self.min_spawn_distance,self.max_spawn_distance)

            ex = x + dist * cos(angle)
            ey = y + dist * sin(angle)

            yield enemy.instantiate(ex,ey)

        self.repeats -= 1

    def update(self,dt,x,y):
        self.delta_time += dt

        if self.delta_time >= self.interval:
            self.delta_time -= self.interval
            return self.spawn(x,y)
        
        return []