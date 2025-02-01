from bullet import Bullet

class Weapon:
    def __init__(self, reload, bullet : Bullet):
        self.reload = reload
        self.bullet = bullet

    def shoot(self,x,y,angle):
        return self.bullet.instantiate(x,y,angle)
    