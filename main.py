"""
Contains the tick, main, and level_editor functions.
"""

import json
import pygame
from vector import Vector
from controller import Controller, LEController
from level import Level, LELevel
from view import View, LEView


def tick(dt, max_angular_velocity, jump_sound, level, controller, view):
    """
    Step the simulation forward one timestep.

    Args:
        dt: A float, the length of the timestep.
        max_angular_velocity: An integer or float, the maximum angular velocity
        the player can have and and still use the controller to make themself
        faster in the direction they are spinning
        jump_sound: A string, the path to an audio file to be played
        when the player presses the jump button.
        level: A Level, the level to update.
        controller: A Controller, the controller to take player inputs from.
        view: A View, the view to display the level to.
    """
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

    # Play the jump sound if the player has just pressed the jump key.
    if controller.play_jump:
        view.play_sound_effect(jump_sound)

    # Update the level.
    level.update(dt)
    level.apply_collisions(
        controller.is_jumping, controller.is_bouncing
    )
    position_change = level.update_portals(dt)
    if position_change is not None:
        view.move_camera(position_change)
    if controller.restart:
        level.restart()

    # Update the camera position based on the player's position.
    view.update_lerp(dt)


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
    jump_sound = constants["jump_sound"]

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

        # Update the controller.
        controller.update(dt)

        # Tick the Level forward in time.
        tick(
            dt, max_angular_velocity, jump_sound, level, controller, view
        )

        # Draw the current state of the level to the window.
        view.refresh(dt)
        pygame.display.update()
        clock.tick(fps)


def level_editor():
    """
    Run the physics simulator, take player input, take level editor input,
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
    jump_sound = constants["jump_sound"]

    # Initialize the level, controller, view, and clock.
    with open(f"portal_configs/{portals}.json", "r", encoding="utf-8") as file:
        portals = json.load(file)
    level = LELevel(f"{starting_level}/", portals, constants)
    controller = LEController(constants)
    view = LEView(level, "sprites/", constants)
    clock = pygame.time.Clock()

    # Run the game until the window is closed.
    while True:
        # If the window is closed, quit the game.
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                print(f"final position = {level.player.position}")
                exit()

        # Update the controller.
        controller.update(dt)

        # If the game is paused, enter level editor mode.
        if controller.is_paused:
            camera_displacement = controller.camera_drag_displacement
            view.move_camera(camera_displacement)

        # Otherwise, tick the Level forward in time.
        else:
            tick(
                dt,
                max_angular_velocity,
                jump_sound,
                level,
                controller,
                view
            )

        # Draw the current state of the level to the window.
        view.refresh(dt)
        pygame.display.update()
        clock.tick(fps)

if __name__ == "__main__":
    level_editor()
