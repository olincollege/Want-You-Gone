"""
Contains the Main class.
"""
from math import copysign
import pygame
from controller import Controller
from vector import Vector
from level import Level
from view import View


def main():
    """
    Run the physics simulator, take player input,
    and display the state of the game to a window.
    """
    fps = 60
    dt = 1 / fps
    max_angular_velocity = 10
    level = Level("level_1/")
    controller = Controller()
    view = View(level, "sprites/")
    clock = pygame.time.Clock()
    while True:
        # If the window is closed, quit the game.
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

        # Update the level with the current state of the controller.
        roll_torque = controller.roll_torque
        if copysign(1, roll_torque) != copysign(1, level.player.angular_velocity
            ) or abs(level.player.angular_velocity) < max_angular_velocity:
            level.player.angular_accelerate(roll_torque, dt)
        level.player.accelerate(Vector(-1, 0).scale(roll_torque), dt)
        controller.update(dt)
        level.update(dt)
        level.apply_collisions(controller.is_jumping,
                               controller.is_bouncing, dt)
        if controller.restart:
            level.restart()

        # Draw the current state of the level to the window.
        view.refresh(dt)
        pygame.display.update()
        clock.tick(fps)

if __name__ == "__main__":
    main()
