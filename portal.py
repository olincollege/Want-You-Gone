"""
Contains the PortalEntrance and PortalExit classes.
"""

from math import sqrt
from vector import Vector

class PortalExit:
    """
    Stores the visual characteristics of a portal.

    Attributes
        _position: A Vector representing the position of the portal.
        _radius: A float representing the radius of the portal.
        _color: A tuple representing the color to draw the portal as.
        _can_glow: A boolean representing if the portal can glow.
    """
    def __init__(self, position, radius, color):
        """
        Initialize all attributes.

        Args:
            position: A Vector representing the position of the portal.
            radius: A float representing the radius of the portal.
            color: A tuple representing the RGB values
            of the color to draw the portal as.
        """
        self._position = position
        self._radius = radius
        self._color = color
        self._can_glow = True

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
        min_distance = self._radius - radius

        if distance >= max_distance:
            return 0
        else:
            return min(
                1,
                (max_distance - distance + min_distance) / max_distance
            )

    def pause_glow(self):
        """Set can_glow to False"""
        self._can_glow = False

    def unpause_glow(self):
        """Set can_glow to True"""
        self._can_glow = True

    @property
    def can_glow(self):
        """Get can_glow"""
        return self._can_glow

    @property
    def radius(self):
        """Get radius"""
        return self._radius

    @property
    def position(self):
        """Get position"""
        return self._position

    @property
    def color(self):
        """Get color"""
        return self._color


class PortalEntrance(PortalExit):
    """
    Stores the visual and behavioral characteristics of a portal.

    Attributes
        _position: A Vector representing the position of the portal.
        _radius: A float representing the radius of the portal.
        _to_position: A Vector representing the position of the portal
        in the level that the portal transports the player to.
        _to_path: A string representing the path of the level that the portal
        transports the player to.
        _max_force: A float representing the magnitude of
        the maximum force the portal can exert on the player.
        _color: A tuple representing the color to draw the portal as.
        _can_glow: A boolean representing if the portal can glow.
    """
    def __init__(
            self, position, radius, to_position, to_path, max_force, color):
        """
        Initialize all attributes.

        Args:
            position: A Vector representing the position of the portal.
            radius: A float representing the radius of the portal.
            to_position: A Vector representing the position of the portal
            in the level that the portal transports the player to.
            to_path: A string representing the path of the level that the portal
            transports the player to.
            _max_force: A float representing the magnitude of
            the maximum force the portal can exert on the player.
            color: A tuple representing the RGB values
            of the color to draw the portal as.
        """
        super().__init__(position, radius, color)
        self._to_position = to_position
        self._to_path = to_path
        self._max_force = max_force
        self._is_active = False

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
        return self._is_active and Vector.diff(position, self.position
            ).magnitude_squared() <= (self._radius - radius) ** 2

    def force(self, position, radius):
        """
        Return the force that the portal should apply to a circle with the
        given position and radius.

        Args:
            position: A Vector representing the position
            of the center of the circle.
            radius: A float representing the radius of the circle.

        Returns:
            A Vector representing the force
            that the portal should apply to the circle.
        """
        if not self._is_active:
            return None

        difference = Vector.diff(position, self._position)
        distance = sqrt(difference.magnitude_squared())
        max_distance = self._radius + radius

        if distance >= max_distance:
            return None
        else:
            return difference.scale(
                (self._max_force * (max_distance - distance))
                / (max_distance * distance)
            )

    def activate(self):
        """
        Make the portal active.
        """
        self._is_active = True

    @property
    def to_portal(self):
        """
        Make a preview of what the other side of the portal should look like.

        Returns:
            copy: A PortalEntrance representing a copy of the portal but at the
            position of its other side.
        """
        copy = PortalEntrance(
            self._to_position,
            self._radius,
            self._position,
            self._to_path,
            self._max_force,
            self._color
        )
        if self._is_active:
            copy.activate()
        if not self._can_glow:
            copy.pause_glow()
        return copy

    @property
    def to_position(self):
        """Get to_position"""
        return self._to_position

    @property
    def to_path(self):
        """Get to_path"""
        return self._to_path

    @property
    def is_active(self):
        """Get is_active"""
        return self._is_active
