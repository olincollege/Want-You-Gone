"""
Contains the PortalEntrance and PortalExit classes.
"""

from math import sqrt
from vector import Vector

class PortalExit:
    """
    Stores the position of the exit end of a portal.

    Attributes
        _position: A Vector representing the position of the portal.
        _radius: A float representing the radius of the portal.
        color: A tuple representing the color to draw the portal as.
    """
    color = (0, 255, 255)

    def __init__(self, position, radius):
        """
        Initialize position and radius

        Args:
            position: A Vector representing the position of the portal.
            radius: A float representing the radius of the portal.
        """
        self._position = position
        self._radius = radius

    def depth(self, position, radius):
        """
        Calculate how deep a circle is in the portal.

        Args:
            position: A Vector representing the position
            of the center of the circle.
            radius: A float representing the radius of the circle.

        Returns:
            A float between 0 and 1 representing
            how deep the circle is in the portal.
        """
        difference = Vector.diff(position, self._position)
        distance = sqrt(difference.magnitude_squared())
        max_distance = self._radius + radius

        if distance >= max_distance:
            return 0
        else:
            return (max_distance - distance) / max_distance

    @property
    def radius(self):
        """Get radius"""
        return self._radius

    @property
    def position(self):
        """Get position"""
        return self._position


class PortalEntrance(PortalExit):
    """
    Stores the position of the entrance end of a portal
    and the position and level it transports the player to.

    Attributes
        _position: A Vector representing the position of the portal.
        _radius: A float representing the radius of the portal.
        _to_position: A Vector representing the position of the portal
        in the level that the portal transports the player to.
        _to_path: A string representing the path of the level that the portal
        transports the player to.
        color: A tuple representing the color to draw the portal as.
    """
    color = (255, 94, 0)

    def __init__(self, position, radius, to_position, to_path, max_force):
        super().__init__(position, radius)
        self._to_position = to_position
        self._to_path = to_path
        self._max_force = max_force

    def is_in(self, position, radius):
        """
        Return whether a circle with the given position and radius is
        fully inside the portal.

        Args:
            position: A Vector representing the position
            of the center of the circle.
            radius: A float representing the radius of the circle.

        Returns:
            A boolean representing whether a circle with the given
            position and radius is fully inside the portal.
        """
        return Vector.diff(position, self.position).magnitude_squared() <= (
            self._radius - radius) ** 2

    def force(self, position, radius):
        """
        Return the force that the portal should apply to a circle with the
        given position and radius
        and the magnitude of the glow the window should get.

        Args:
            position: A Vector representing the position
            of the center of the circle.
            radius: A float representing the radius of the circle.

        Returns:
            A Vector representing the force
            that the portal should apply to the circle.
            A float between 0 and 1 representing
            how colored the screen should be.
        """
        difference = Vector.diff(position, self._position)
        distance = sqrt(difference.magnitude_squared())
        max_distance = self._radius + radius

        if distance >= max_distance:
            return None, 0
        else:
            return difference.scale(
                (self._max_force * (max_distance - distance))
                / (max_distance * distance)
            ), (max_distance - distance) / max_distance

    @property
    def to_position(self):
        """Get to_position"""
        return self._to_position

    @property
    def to_path(self):
        """Get to_path"""
        return self._to_path
