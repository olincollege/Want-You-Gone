"""
Contains the Main class.
"""

import json
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
    fps = 40
    dt = 1 / fps
    with open("constants/normal_mode.json", "r", encoding="utf-8") as file:
        constants = json.load(file)
    max_angular_velocity = constants["max_angular_velocity"]

    # Initialize the level, controller, view, and clock.
    with open("portal_configs/test.json", "r", encoding="utf-8") as file:
        portals = json.load(file)
    level = Level("level_1/", portals, constants)
    controller = Controller(constants)
    view = View(level, "sprites/", constants)
    clock = pygame.time.Clock()

    # Chapter Start Text
    view.text_display.show("Chapter 1", "The Part Where I'm Sorry")
 
    # Run the game until the window is closed.
    while True:
        # If the window is closed, quit the game.
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                print(f"final position = {level.player.position}")
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
            or abs(level.player.velocity.x) <
            max_angular_velocity * level.player.radius
        ):
            level.player.accelerate(Vector(roll_force, 0), dt)
        if roll_force > 0:
            level.move_shape(Vector(100, 0), dt)
        elif roll_force < 0:
            level.move_shape(Vector(-100, 0), dt)

        # Update the controller and level.
        controller.update(dt)
        level.update(dt)
        level.apply_collisions(
            controller.is_jumping, controller.is_bouncing
        )
        position_change = level.update_portals(dt)
        if position_change is not None:
            view.move_camera(position_change)
        if controller.restart:
            level.restart()

        # Draw the current state of the level to the window.
        view.refresh(dt)
        pygame.display.update()
        clock.tick(fps)


if __name__ == "__main__":
    main()
