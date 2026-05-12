"""
Contains the Main class.
"""

import json
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
    # Set all constants.
    fps = 60
    dt = 1 / fps
    constants_path = "constants/normal_mode.json"
    with open(constants_path, "r", encoding="utf-8") as file:
        constants = json.load(file)
    max_angular_velocity = constants["max_angular_velocity"]
    max_translational_velocity = constants["max_translational_velocity"]

    # Initialize the level, controller, view, and clock.
    level = Level("level_1/", constants_path)
    controller = Controller(constants_path)
    view = View(level, "sprites/")
    clock = pygame.time.Clock()

    # Run the game until the window is closed.
    while True:
        # If the window is closed, quit the game.
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                print(level.player.position)
                exit()

        # Apply the effects of the roll control from the player.
        roll_torque, roll_force = controller.roll
        if (
            roll_torque * level.player.angular_velocity < 0
            or abs(level.player.angular_velocity) < max_angular_velocity
        ):
            level.player.angular_accelerate(roll_torque, dt)
        if (
            roll_force * level.player.velocity.x < 0
            or abs(level.player.velocity.x) < max_translational_velocity
        ):
            level.player.accelerate(Vector(roll_force, 0), dt)

        # Update the controller and level.
        controller.update(dt)
        level.update(dt)
        level.apply_collisions(
            controller.is_jumping, controller.is_bouncing, dt
        )
        if controller.restart:
            level.restart()

        # Draw the current state of the level to the window.
        view.refresh(dt)
        pygame.display.update()
        clock.tick(fps)


if __name__ == "__main__":
    main()
