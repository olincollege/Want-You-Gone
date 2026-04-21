"""
Contains the view class
"""

from vector import Vector
import pygame

class View:
    """
    Displays the state of a level to a graphical window.

    Attributes:
        _level: A Level representing the level to display.
        _camera: A Vector representing the position of the camera.
        _path: A string representing the path of the folder with every sprite.
        _lerp_speed: A float representing the speed at which the camera
        follows the player.
        _window: A surface that will have the level drawn on it.
    """

    def __init__(self, level, path):
        """
        Initialize level, camera, path, lerp_speed, and window.

        Args:
            level: A Level to display.
            path: A string representing the path of the folder
            with every sprite.
        """
        self._level = level
        self._camera = level.player.position
        self._path = path
        self._lerp_speed = 0.9
        self._window = pygame.display.set_mode((1200, 900))

    def display_objects(self):
        """
        Gets coordinates from and object and determines whether or not to display them.
        """
        surface = pygame.image.load(self._path).convert()

    def draw_shapes(self):
        """
        Gets coordinates and image of a shape to display and displays that shape.
        """
        pass

    def update_lerp(self):
        pass

    def check_cull(self):
        pass
