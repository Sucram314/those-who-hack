import asyncio
import pygame
from game import Engine

SCREEN = pygame.display.set_mode(flags=pygame.FULLSCREEN)
FPS = 60

engine = Engine(SCREEN, FPS)

async def main():
    while True:
        if engine.update():
            return
        
        engine.draw()

        pygame.display.update()
        await asyncio.sleep(0)

asyncio.run(main())
