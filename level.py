"""
Contains the Level class.
"""

from math import sqrt
import json
from shape import Circle, Polygon
from vector import Vector


class Level:
    """
    Store the physical state of a set of 2D shapes.

    Attributes:
        _gravity: A Vector representing the gravity on the level.
        self._path: A string representing the path to the folder
        with all the starting data for the level.
        self._player: A Circle representing the player character.
        self._border: A Polygon representing the outmost border
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
    _gravity = Vector(0, 0.2)

    def __init__(self, path):
        """
        Initialize all attributes from the files in a folder.

        Args:
            path: A string representing the path of the folder.
        """
        self._path = path
        self.restart()

    def restart(self):
        """
        Set all attributes to their default values.
        """
        # Read the file for player.
        with open(self._path + "player.json", "r", encoding="utf-8") as file:
            player_attributes = json.load(file)

        # Initialize player.
        self._player = Circle(
            player_attributes["radius"],
            self.make_vector(player_attributes["position"]),
            self.make_vector(player_attributes["velocity"]),
            player_attributes["angle"],
            player_attributes["angular_velocity"],
            True,
            False,
            player_attributes["is_bouncy"],
            tuple(player_attributes["color"]),
        )

        # ----------------------------------------------------------------------

        # Read the file for border.
        with open(self._path + "border.json", "r", encoding="utf-8") as file:
            border_attributes = json.load(file)

        # Initialize border.
        self._border = Polygon(
            self.make_vector(border_attributes["vertices"]),
            self.make_vector(border_attributes["position"]),
            self.make_vector(border_attributes["velocity"]),
            border_attributes["angle"],
            border_attributes["angular_velocity"],
            False,
            True,
            border_attributes["is_bouncy"],
            tuple(border_attributes["color"]),
        )

        # ----------------------------------------------------------------------

        # Read the file for polygons.
        with open(self._path + "polygons.json", "r", encoding="utf-8") as file:
            polygons_attributes = json.load(file)

        # Initialize polygons.
        self._polygons = [
            Polygon(
                self.make_vector(polygon_attributes["vertices"]),
                self.make_vector(polygon_attributes["position"]),
                self.make_vector(polygon_attributes["velocity"]),
                polygon_attributes["angle"],
                polygon_attributes["angular_velocity"],
                False,
                False,
                polygon_attributes["is_bouncy"],
                tuple(polygon_attributes["color"]),
            )
            for polygon_attributes in polygons_attributes
        ]

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
        if isinstance(json_input[0], int) or isinstance(json_input[0], float):
            if len(json_input) != 2:
                raise ValueError("A base list is not of length two!")
            return Vector(float(json_input[0]), float(json_input[1]))

        # Otherwise go a level deeper into the list
        return [cls.make_vector(i) for i in json_input]

    def update(self, dt):
        """
        Update the position velocity, angular velocity,
        and angle of all shapes on the level.

        Args:
            dt: A float representing the amount of time to update for.
        """
        # Update the velocity of all shapes by adding gravity to them.
        self._player.force(self._gravity, dt)
        self._border.force(self._gravity, dt)
        for polygon in self._polygons:
            polygon.force(self._gravity, dt)

        # Update the positions and angles of all shapes by adding
        # their velocity and angular velocity to them.
        self._player.update_position(dt)
        self._border.update_position(dt)
        for polygon in self._polygons:
            polygon.update_position(dt)

        # Find the shortest distance between the player's center and
        # the closest point to it on each shape.
        for polygon in self._polygons:
            # If the player is too far from the polygon, skip it.
            if (polygon.radius + self.player.radius) ** 2 < Vector.diff(
                polygon.position, self._player.position).magnitude_squared():
                continue

            # Otherwise find the closest point on the polygon
            # to the player and the distance between them.
            shortest_distance = None
            closest_line = None
            closest_vertex = None
            for i, vertex in enumerate(polygon.vertices):
                # Find the distance between the player and the line segment
                # between vertices i - 1 and i and update
                # shortest_distance if it is shorter.
                distance = self._player.position.line_point_distance(
                    polygon.vertices[i - 1], vertex)
                if distance is not None and (shortest_distance is None or
                    abs(distance) < abs(shortest_distance)):
                    shortest_distance = distance
                    closest_line = i

                # Find the distance between the player and the vertex
                # and update shortest_distance if it is shorter.
                distance = sqrt(Vector.diff(
                    self._player.position, vertex).magnitude_squared())
                if shortest_distance is None or distance < abs(
                    shortest_distance):
                    shortest_distance = distance
                    closest_vertex = i

            # Find the collision normal for the line or vertex
            # that is closest to the player.
            

    @property
    def player(self):
        """Get player"""
        return self._player

    @property
    def border(self):
        """Get border"""
        return self._border

    @property
    def polygons(self):
        """Get border"""
        return self._polygons
