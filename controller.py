"""
Contains the Controller class.
"""

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
        _ROLL_TORQUE: A float representing the angular acceleration
        applied per second when rolling.
        _ROLL_FORCE: A float representing the horizontal acceleration
        applied per second when rolling.
        _JUMP_BUFFER: A float representing the number of seconds after pressing
        the jump button a jump can activate.
        _keys: A dictionary representing the keys currently being pressed.
        _jump_timer: a float representing the number of seconds
        since the last jump.
        _released_jump: A boolean representing if the player has released the
        jump button since the last time they pressed it.
    """

    def __init__(self, constants):
        """
        Initialise all constants.

        Args:
            constants: A dictionary representing all the constants.
        """
        self._ROLL_TORQUE = constants["roll_torque"]
        self._ROLL_FORCE = constants["roll_force"]
        self._JUMP_BUFFER = constants["jump_buffer"]
        self._jump_timer = self._JUMP_BUFFER
        self._jump_released = True
        self.update(0)

    def update(self, dt):
        """
        Tick the jump timer forward by one frame and record the key inputs.

        Call this once per frame *before* reading any properties.

        Args:
            dt: A float representing the frame duration in seconds.
        """
        self._keys = pygame.key.get_pressed()
        self._jump_timer += dt
        jumping = self._keys[pygame.K_w] or self._keys[pygame.K_UP]
        if jumping:
            if self._jump_released:
                self._jump_timer = 0
            self._jump_released = False
        else:
            self._jump_released = True

    @property
    def restart(self):
        """
        True when the player wants to restart the level.

        Pressing R triggers this, which tells main.py to reload the level.

        Returns:
            A bool.
        """
        return self._keys[pygame.K_r]

    @property
    def is_jumping(self):
        """
        True when the jump timer is above zero.

        Pressing W or up arrow triggers a jump.

        Returns:
            A boolean.
        """
        return self._jump_timer < self._JUMP_BUFFER

    @property
    def is_bouncing(self):
        """
        True when the player wants the normal bounce to happen.

        Holding S / down arrow suppresses the bounce (returns False),
        which tells Level.calculate_impulse to use e = 0.

        Returns:
            A boolean.
        """
        return not (self._keys[pygame.K_s] or self._keys[pygame.K_DOWN])

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
        direction = 0
        if self._keys[pygame.K_a] or self._keys[pygame.K_LEFT]:
            direction += 1
        if self._keys[pygame.K_d] or self._keys[pygame.K_RIGHT]:
            direction -= 1
        return direction * self._ROLL_TORQUE, -direction * self._ROLL_FORCE
