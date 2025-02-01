from bullet import Bullet

class Weapon:
    def __init__(self, reload, speed, radius, damage, area_radius, area_damage):
        self.reload = reload

        self.speed = speed
        self.radius = radius
        self.damage = damage
        self.area_radius = area_radius
        self.area_damage = area_damage

        self.delta_time = 0

    def update(self,dt):
        self.delta_time += dt

    def shoot(self,x,y):
        if self.delta_time >= self.reload:
            self.delta_time = 0
            return Bullet(x, y, 0, self.speed, self.radius, self.damage, self.area_radius, self.area_damage)

    