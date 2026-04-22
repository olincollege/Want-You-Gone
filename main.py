"""
Contains the Main class.
"""
import pygame
from sys import exit
from level import Level
from view import View


def main():
    """
    Run the physics simulator, take player input,
    and display the state of the game to a window.
    """
    fps = 60
    dt = 1 / fps
    level = Level("example_level/")
    view = View(level, "sprites/")
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
        #pygame.display.update()

if __name__ == "__main__":
    main()
