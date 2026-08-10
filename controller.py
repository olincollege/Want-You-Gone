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
        _mouse_buttons: A tuple representing the state of each mouse button.
        _camera_drag_position: A Vector representing the position of the mouse
        in the previous frame when dragging the camera.
        _camera_drag_displacement: A Vector representing the amount
        to move the camera in the current frame based on mouse dragging.
        _dynamic_toggle_released: A boolean representing
        if the dynamic toggle key was released on the last frame.
        _toggle_dynamic: A boolean representing if the editor wants to toggle
        the 'dynamic' state of an object in the level editor.
        _edit_clicking_released: A boolean representing
        if the edit click button was released in the last frame.
        _edit_click: A boolean representing if the editor wants to
        make an edit click.
        _delete_clicking_released: A boolean representing
        if the delete button was released in the last frame.
        _delete_click: A boolean representing if the editor wants to
        make a deletion.
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
        self._dynamic_toggle_released = True
        self._toggle_dynamic = False
        self._edit_click_released = True
        self._edit_click = False
        self._delete_click_released = True
        self._delete_click = False

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

        # Update the dynamic toggle tracker.
        dynamic_toggling = self._keys[pygame.K_d]
        self._toggle_dynamic = False
        if dynamic_toggling:
            if self._dynamic_toggle_released:
                self._toggle_dynamic = True
            self._dynamic_toggle_released = False
        else:
            self._dynamic_toggle_released = True

        # Update the camera drag tracker.
        self._mouse_buttons = pygame.mouse.get_pressed()
        mouse_position = pygame.mouse.get_pos()
        self._mouse_position = Vector(mouse_position[0], mouse_position[1])
        if self._mouse_buttons[2]:  # Right mouse button is pressed
            if self._camera_drag_position is not None:
                self._camera_drag_displacement = Vector.diff(
                    self._camera_drag_position, self._mouse_position
                )
            self._camera_drag_position = self._mouse_position
        else:
            self._camera_drag_position = None
            self._camera_drag_displacement = Vector(0, 0)

        # Update the edit click tracker.
        edit_clicking = self._mouse_buttons[0]  # Left mouse button is pressed
        self._edit_click = False
        if edit_clicking:
            if self._edit_click_released:
                self._edit_click = True
            self._edit_click_released = False
        else:
            self._edit_click_released = True

        # Update the delete click tracker.
        deleting = self._keys[pygame.K_BACKSPACE] or self._keys[pygame.K_DELETE]
        self._delete_click = False
        if deleting:
            if self._delete_click_released:
                self._delete_click = True
            self._delete_click_released = False
        else:
            self._delete_click_released = True

    @property
    def editor_position(self):
        """
        Get the position of the mouse in the level editor.

        Returns:
            A Vector representing the position of the mouse in the level editor.
            None if the left mouse button is not pressed.
        """
        if not self._mouse_buttons[0]:  # Left mouse button is pressed
            return None
        return self._mouse_position

    @property
    def new_polygon(self):
        """
        True when the player wants to create a new polygon in the level editor.
        This is triggered by pressing P.
        """
        return self._keys[pygame.K_p]

    @property
    def new_circle(self):
        """
        True when the player wants to create a new circle in the level editor.
        This is triggered by pressing C.
        """
        return self._keys[pygame.K_c]

    @property
    def delete(self):
        """
        True when the player wants to delete something in the level editor.
        This is triggered by pressing the backspace or delete key.
        """
        return self._delete_click

    @property
    def toggle_dynamic(self):
        """
        True when the player wants to toggle the dynamic state of an object
        in the level editor. This is triggered by pressing D.
        """
        return self._toggle_dynamic

    @property
    def finish_editing(self):
        """
        True when the player wants to finish editing the editing shape.
        This is triggered by the enter key.
        """
        return self._keys[pygame.K_RETURN]

    @property
    def is_paused(self):
        """Get is paused"""
        return self._is_paused

    @property
    def camera_drag_displacement(self):
        """Get camera drag displacement"""
        return self._camera_drag_displacement

    @property
    def edit_click(self):
        """Get edit click"""
        return self._edit_click
