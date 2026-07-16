"""
Contains the WorldText class.
"""

import pygame


class WorldText:
    """
    A single piece of static text anchored to a position in the world,
    e.g. a sign or label placed alongside polygons on a level.

    Unlike TextDisplay, this has no fade lifecycle - it is always drawn
    while on screen, the same way a Polygon is.

    Attributes:
        _position: A Vector representing the world position of the text.
        _surface: A Surface with the pre-rendered text.
        _radius: A float used for view-frustum culling, based on the
        rendered surface size.
    """

    def __init__(self, text, position, size, color, font_path=None):
        self._position = position
        font = pygame.font.Font(font_path, size)
        self._surface = font.render(text, True, tuple(color))
        self._radius = max(self._surface.get_width(),
                            self._surface.get_height()) / 2

    @property
    def position(self):
        """Get position"""
        return self._position

    @property
    def radius(self):
        """Get radius"""
        return self._radius

    @property
    def surface(self):
        """Get the pre-rendered surface"""
        return self._surface