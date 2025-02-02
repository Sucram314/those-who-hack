import random
from math import sin,cos,pi,sqrt
from enemy import Enemy

class Cycle:
    def __init__(self, enemies : list[Enemy], repeats=3, interval=10):
        self.enemies = enemies
        self.repeats = repeats
        self.interval = interval

        self.delta_time = interval

    def spawn(self, x, y, min_spawn_distance=900, max_spawn_distance=1100):
        for enemy in self.enemies:
            angle = random.uniform(0, 2*pi)
            dist = sqrt(random.uniform(0,1)) * (max_spawn_distance - min_spawn_distance) + min_spawn_distance

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