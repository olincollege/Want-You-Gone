"""
Contains the Controller and LEController classes.
"""

import pygame

from vector import Vector


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
        _play_jump: A boolean representing if the jump button has been pressed
        in the most recent timestep.
    """

    def __init__(self, constants):
        """
        Initialise all constants and readable attributes.

        Args:
            constants: A dictionary representing all the constants.
        """
        self._ROLL_TORQUE = constants["roll_torque"]
        self._ROLL_FORCE = constants["roll_force"]
        self._JUMP_BUFFER = constants["jump_buffer"]
        self._jump_timer = self._JUMP_BUFFER
        self._jump_released = True
        self._play_jump = False
        self.update(0)

    def update(self, dt):
        """
        Tick the jump timer forward by one frame and record the key inputs.

        Call this once per frame *before* reading any properties.

        Args:
            dt: A float representing the frame duration in seconds.
        """
        # Update the keys currently being pressed.
        self._keys = pygame.key.get_pressed()

        # Update the jump tracker.
        self._jump_timer += dt
        jumping = self._keys[pygame.K_w] or self._keys[pygame.K_UP]
        if jumping:
            if self._jump_released:
                self._jump_timer = 0
                self._jump_released = False
                self._play_jump = True
                return
        else:
            self._jump_released = True
        self._play_jump = False

    @property
    def restart(self):
        """
        True when the player wants to restart the level.

        Pressing R triggers this, which tells main.py to reload the level.

        Returns:
            A boolean.
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
            direction -= 1
        if self._keys[pygame.K_d] or self._keys[pygame.K_RIGHT]:
            direction += 1
        return direction * self._ROLL_TORQUE, direction * self._ROLL_FORCE

    @property
    def play_jump(self):
        """
        True when the player has jumped in the most recent timestep
        and the jump sound should be played.

        Returns:
            A boolean.
        """
        return self._play_jump


class LEController(Controller):
    """
    Same as Controller but with extra level editor input options.

    Attributes:
        _pause_released: A boolean representing if the pause key
        was released on the last frame.
        _is_paused: A boolean representing
        if gameplay is currently paused.
        All other attributes are inherited from Controller.
        _camera_drag_position: A Vector representing the position of the mouse
        in the previous frame when dragging the camera.
        _camera_drag_displacement: A Vector representing the amount
        to move the camera in the current frame based on mouse dragging.
    """
    def __init__(self, constants):
        """
        Initialise all constants and readable attributes.

        Args:
            constants: A dictionary representing all the constants.
        """
        super().__init__(constants)
        self._pause_released = True
        self._is_paused = False
        self._camera_drag_position = None
        self._camera_drag_displacement = Vector(0, 0)

    def update(self, dt):
        """
        Tick the jump timer forward by one frame and record the key inputs.

        Call this once per frame *before* reading any properties.

        Args:
            dt: A float representing the frame duration in seconds.
        """
        # Update the keys currently being pressed and the jump tracker.
        super().update(dt)

        # Update the pause tracker.
        pausing = self._keys[pygame.K_SPACE]
        if pausing:
            if self._pause_released:
                self._is_paused = not self._is_paused
            self._pause_released = False
        else:
            self._pause_released = True

        # Update the camera drag tracker.
        mouse_buttons = pygame.mouse.get_pressed()
        if mouse_buttons[2]:  # Right mouse button is pressed
            mouse_position = pygame.mouse.get_pos()
            mouse_position = Vector(mouse_position[0], mouse_position[1])
            if self._camera_drag_position is not None:
                self._camera_drag_displacement = Vector.diff(
                    self._camera_drag_position, mouse_position
                )
            self._camera_drag_position = mouse_position
        else:
            self._camera_drag_position = None
            self._camera_drag_displacement = Vector(0, 0)

    @property
    def is_paused(self):
        """Get is paused"""
        return self._is_paused

    @property
    def camera_drag_displacement(self):
        """Get camera drag displacement"""
        return self._camera_drag_displacement
