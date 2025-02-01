from bullet import Bullet

class Weapon:
    def __init__(self, reload, bullet : Bullet):
        self.reload = reload
        self.bullet = bullet

        self.delta_time = 0

    def update(self,dt):
        self.delta_time += dt

    def shoot(self,x,y,angle):
        if self.delta_time >= self.reload:
            self.delta_time = 0
            return self.bullet.instantiate(x,y,angle)
    