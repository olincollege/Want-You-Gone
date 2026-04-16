"""
Contains the Level class.
"""

class Level():
    """
    Store the physical state of a set of 2D shapes.

    Attributes:
        self._player: A Circle representing the player character.
        self._boarder: A Polygon representing the outmost border
        of the space objects can move inside.
        self._circles: A list of Circles representing the
        stationary circles on the level.
        self._polygons: A list of Polygons representing the
        stationary polygons on the level.
        self._moving_circles: A list of Circles representing the
        moving circles on the level.
        self._moving_polygons: A list of Polygons representing the
        moving polygons on the level.
    """

    def __init__(self, path):
        """
        Initialize all attributes from the files in a folder.

        Args:
            path: A string representing the path of the folder.
        """
        