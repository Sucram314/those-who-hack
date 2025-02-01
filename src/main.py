import pygame
from game import Engine

SCREEN = pygame.display.set_mode(flags=pygame.FULLSCREEN)
FPS = 60

engine = Engine(SCREEN, FPS)

while True:
    if engine.update():
        pygame.quit()
        break
    
    engine.draw()

    pygame.display.update()

