class Camera:
    def __init__(self,x,y,screen_width,screen_height,follow_rate=0.2):
        self.x = x
        self.y = y

        self.screen_width = screen_width
        self.screen_height = screen_height

        self.follow_rate = follow_rate

    def follow(self, x, y):
        self.x += (x - self.x) * self.follow_rate
        self.y += (y - self.y) * self.follow_rate

    def to_screen(self,x,y):
        screen_x = x - self.x + self.screen_width/2
        screen_y = self.y - y + self.screen_height/2
        return screen_x, screen_y 