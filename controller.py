"""
Contains the Controller class.
"""

import pygame


class Controller:
    """
    Translates player input into game actions and manages input state.

    The controller handles:
      - Left/right rolling (A/D or arrow keys) applied as torque each frame.
      - Jumping (W or up arrow) applied as an impulse on collision in the collision
        direction.
      - Bounce suppression (S or down arrow) sets restitution to zero on
        touchdown so the player doesn't bounce.
      - Jump buffering: afaik, because a bounce resolves in a single frame, pressing
        W up to JUMP_BUFFER_MS milliseconds *before* a collision still counts
        as a jump input for that collision.

    Attributes:
        _jump_buffer_ms: An int representing how long (ms) a jump keypress
                         is buffered before a collision.
        _jump_buffer_timer: A float tracking remaining buffer time (ms).
        _roll_torque: A float representing the torque applied per second
                      when rolling.
    """

    JUMP_BUFFER_MS = 200
    ROLL_TORQUE = 3.0  # tweak to taste

    def __init__(self):
        """Initialise all input-state bookkeeping."""
        self._jump_buffer_timer = 0.0  # counts down in ms

    def update(self, dt_seconds):
        """
        Tick the controller forward by one frame.

        Call this once per frame *before* reading is_jumping / is_rolling.

        Args:
            dt_seconds: A float representing the frame duration in seconds.
        """
        dt_ms = dt_seconds * 1000.0

        # Drain the jump buffer.
        if self._jump_buffer_timer > 0:
            self._jump_buffer_timer = max(0.0, self._jump_buffer_timer - dt_ms)

        # Check for a fresh jump keypress this frame and (re-)fill the buffer.
        keys = pygame.key.get_pressed()
        jump_held = keys[pygame.K_w] or keys[pygame.K_UP]
        if jump_held:
            self._jump_buffer_timer = self.JUMP_BUFFER_MS

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
        True when a jump input is buffered (key held or pressed recently).

        This stays True for up to JUMP_BUFFER_MS after the key was pressed,
        so the player can press W slightly before a collision and still get
        the jump bonus on that bounce.

        Returns:
            A bool.
        """
        return self._jump_buffer_timer > 0

    @property
    def is_bouncing(self):
        """
        True when the player wants the normal bounce to happen.

        Holding S / down arrow suppresses the bounce (returns False),
        which tells Level.calculate_impulse to use e = 0.

        Returns:
            A bool.
        """
        keys = pygame.key.get_pressed()
        return not (keys[pygame.K_s] or keys[pygame.K_DOWN])

    @property
    def roll_torque(self):
        """
        The net torque to apply to the player this frame for rolling.

        Left (A / left arrow) gives negative torque (clockwise in standard
        pygame coordinates where y increases downward).
        Right (D / right arrow) gives positive torque.

        Returns:
            A float. Zero when no roll key is held.
        """
        keys = pygame.key.get_pressed()
        direction = 0
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            direction -= 1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            direction += 1
        return direction * self.ROLL_TORQUE

    def consume_jump_buffer(self):
        """
        Clear the jump buffer after it has been used for a collision.

        Call this inside Level.update() immediately after a collision is
        resolved so that a single keypress doesn't apply the jump bonus
        to multiple simultaneous collision contacts.
        """
        self._jump_buffer_timer = 0.0