class Camera:
    def __init__(self,screen_width,screen_height,x=0,y=0,follow_rate=0.2):
        self.x = x
        self.y = y

        self.screen_width = screen_width
        self.screen_height = screen_height

        self.follow_rate = follow_rate

    def reset(self):
        self.x = 0
        self.y = 0

    def follow(self, x, y):
        self.x += (x - self.x) * self.follow_rate
        self.y += (y - self.y) * self.follow_rate

    def to_screen(self,x,y):
        screen_x = x - self.x + self.screen_width/2
        screen_y = self.y - y + self.screen_height/2
        return screen_x, screen_y 