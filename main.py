"""
Contains the Main class.
"""
import pygame
from controller import Controller
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
    controller = Controller()
    view = View(level, "sprites/")
    while True:
        # If the window is closed, quit the game.
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

        # Update the level with the current state of the controller.
        level.player.torque(controller.roll_torque, dt)
        controller.update(dt)
        level.update(dt, controller.is_jumping, controller.is_bouncing)

        # Draw the current state of the level to the window.
        view.refresh(dt)
        pygame.display.update()

if __name__ == "__main__":
    main()
