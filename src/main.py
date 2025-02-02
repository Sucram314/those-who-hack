import pygame
import os
from game import Engine

pygame.init()

SCREEN = pygame.display.set_mode(flags=pygame.FULLSCREEN)
FPS = 60
DIRECTORY = os.getcwd() + "\\src"

engine = Engine(SCREEN, FPS, DIRECTORY)
engine.load()

while True:
    if engine.update():
        engine.save() 
        pygame.quit()
        break
    
    engine.draw()

    pygame.display.update()

