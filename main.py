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
    # --------------------------------------------------------------------------
    fps = 40
    mode = "normal"
    portals = "close"
    starting_level = "example_level"
    # --------------------------------------------------------------------------
    dt = 1 / fps
    with open(f"constants/{mode}_mode.json", "r", encoding="utf-8") as file:
        constants = json.load(file)
    max_angular_velocity = constants["max_angular_velocity"]

    # Initialize the level, controller, view, and clock.
    with open(f"portal_configs/{portals}.json", "r", encoding="utf-8") as file:
        portals = json.load(file)
    level = Level(f"{starting_level}/", portals, constants)
    controller = Controller(constants)
    view = View(level, "sprites/", constants)
    clock = pygame.time.Clock()

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
        #if roll_force > 0:
            #level.move_shape(Vector(100, 0), dt)
        #elif roll_force < 0:
            #level.move_shape(Vector(-100, 0), dt)

        # Update the controller and level.
        play_jump = controller.update(dt)
        if play_jump:
            view.play_sound_effect(constants["jump_sound"])
        level.update(dt)
        level.apply_collisions(
            controller.is_jumping, controller.is_bouncing
        )
        position_change, depth, portal = level.update_portals(dt)
        if position_change is not None:
            view.move_camera(position_change)
        if controller.restart:
            level.restart()

        # Draw the current state of the level to the window.
        view.refresh(dt, depth, portal)
        pygame.display.update()
        clock.tick(fps)


if __name__ == "__main__":
    main()
