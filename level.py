"""
Contains the Level class.
"""

import json
from shape import Circle, Polygon
from vector import Vector

class Level():
    """
    Store the physical state of a set of 2D shapes.

    Attributes:
        self._path: A string representing the path to the folder
        with all the starting data for the level.
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
        self._path = path
        self.refresh()

    def refresh(self):
        """
        Set all attributes to their default values.
        """
        # Read the file for player.
        with open(self._path + "player.json", "r", encoding="utf-8") as file:
            player_attributes = json.load(file)

        # Initialize player.
        self._player = Circle(
            self.make_vector(player_attributes["position"]),
            self.make_vector(player_attributes["velocity"]),
            player_attributes["angle"],
            player_attributes["angular_velocity"],
            True,
            False,
            player_attributes["is_bouncy"],
            player_attributes["radius"],
            tuple(player_attributes["color"]))

        # ----------------------------------------------------------------------

        # Read the file for boarder.
        with open(self._path + "boarder.json", "r", encoding="utf-8") as file:
            boarder_attributes = json.load(file)

        # Initialize boarder.
        self._boarder = Polygon(
            self.make_vector(boarder_attributes["vertices"]),
            self.make_vector(boarder_attributes["position"]),
            self.make_vector(boarder_attributes["velocity"]),
            boarder_attributes["angle"],
            boarder_attributes["angular_velocity"],
            False,
            True,
            boarder_attributes["is_bouncy"],
            tuple(boarder_attributes["color"]))

        # ----------------------------------------------------------------------

        # Read the file for polygons.
        with open(self._path + "polygons.json", "r", encoding="utf-8") as file:
            polygons_attributes = json.load(file)

        # Initialize polygons.
        self._polygons = [Polygon(
            self.make_vector(polygon_attributes["vertices"]),
            self.make_vector(polygon_attributes["position"]),
            self.make_vector(polygon_attributes["velocity"]),
            polygon_attributes["angle"],
            polygon_attributes["angular_velocity"],
            False,
            False,
            polygon_attributes["is_bouncy"],
            tuple(polygon_attributes["color"]))
            for polygon_attributes in polygons_attributes]

    @classmethod
    def make_vector(cls, json_input):
        """
        Convert lists of numbers to Vectors,
        lists of lists of numbers to lists of Vectors,
        and so on.

        Args:
            json_input: A list of numbers (floats or integers),
            a list of lists of numbers, or a nested list of a higher degree.

        Returns:
            The same nested list structure as json_input but with Vectors
            replacing the lowest lists in the hierarchy.
        
        Raises:
            ValueError: If a base list is not of length two.
        """
        # If json_input is a list of numbers return it as a Vector.
        if json_input[0].isinstance(int) or json_input[0].isinstance(float):
            if len(json_input) != 2:
                raise ValueError("A base list is not of length two!")
            return Vector(float(json_input[0]), float(json_input[1]))

        # Otherwise go a level deeper into the list
        return [cls.make_vector(i) for i in json_input]
