"""
Contains the Controller class.
"""

import json

import pygame


class Controller:
    """
    Translates player input into game actions and manages input state.

    The controller handles:
      - Left/right rolling (A/D or arrow keys) applied as torque each frame.
      - Jumping (W or up arrow) applied as an upward impulse on collision.
      - Bounce suppression (S or down arrow) sets restitution to zero on
        touchdown so the player doesn't bounce.

    Attributes:
        _roll_torque: A float representing the angular acceleration
        applied per second when rolling.
        _roll_force: A float representing the horizontal acceleration
        applied per second when rolling.       
    """

    def __init__(self, constants_path):
        """
        Initialise all constants.

        Args:
            constants_path: A string representing the path to the json file
            with all constants.
        """
        with open(constants_path, "r", encoding="utf-8") as file:
            constants = json.load(file)

        self.ROLL_TORQUE = constants["roll_torque"]
        self.ROLL_FORCE = constants["roll_force"]

    def update(self, dt_seconds):
        """
        Tick the controller forward by one frame.

        Call this once per frame *before* reading is_jumping / is_rolling.

        Args:
            dt_seconds: A float representing the frame duration in seconds.
        """

    @property
    def restart(self):
        """
        True when the player wants to restart the level.

        Pressing R triggers this, which tells main.py to reload the level.

        Returns:
            A bool.
        """
        keys = pygame.key.get_pressed()
        return keys[pygame.K_r]

    @property
    def is_jumping(self):
        """
        True when the player is pressing the jump key right now.

        Pressing W or up arrow triggers a jump.

        Returns:
            A boolean.
        """
        keys = pygame.key.get_pressed()
        return keys[pygame.K_w] or keys[pygame.K_UP]

    @property
    def is_bouncing(self):
        """
        True when the player wants the normal bounce to happen.

        Holding S / down arrow suppresses the bounce (returns False),
        which tells Level.calculate_impulse to use e = 0.

        Returns:
            A boolean.
        """
        keys = pygame.key.get_pressed()
        return not (keys[pygame.K_s] or keys[pygame.K_DOWN])

    @property
    def roll(self):
        """
        The net torque and force to apply to the player this frame for rolling.

        Left (A / left arrow) gives negative torque (clockwise in standard
        pygame coordinates where y increases downward).
        Right (D / right arrow) gives positive torque.

        Returns:
            A float and a Vector. Zero when no roll key is held.
        """
        keys = pygame.key.get_pressed()
        direction = 0
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            direction += 1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            direction -= 1
        return direction * self.ROLL_TORQUE, -direction * self.ROLL_FORCE
