"""
Contains the Shape class and its subclasses Circle and Polygon.
"""

from math import pi
from vector import Vector


class Shape:
    """
    Stores the physical state of 2D shape in space.

    Attributes:
        _position: A vector representing the position of the center of mass of the shape.
        _velocity: A vector representing the velocity of the shape.
        _angle: A Float representing the angular displacement of the shape.
        _angular_velocity: A Float representing the angular velocity of the shape.
        _can_move: A boolean representing if the shape can move or not.
        _moment: A float representing the moment of inertia of the circle.
        _mass: A float representing the mass of the circle.
    """

    def __init__(
        self,
        position,
        velocity,
        angle,
        angular_velocity,
        can_move,
        is_inverted,
        moment,
        mass,
    ):
        """
        Initializes position, velocity, angle, angular_velocity, can_move, and is_inverted.

        Args:
            position: A vector representing the position of the center of mass of the shape.
            velocity: A vector representing the velocity of the shape.
            angle: A Float representing the angular displacement of the shape.
            angular_velocity: A Float representing the angular velocity of the shape.
            can_move: A boolean representing if the shape can move or not.
            is_inverted: A boolean representing if the mass of the shape is outside of it.
            moment: A float representing the moment of inertia of the circle.
            mass: A float representing the mass of the circle.
        """
        self._position = position
        self._velocity = velocity
        self._angle = angle
        self._angular_velocity = angular_velocity
        self._can_move = can_move
        self._is_inverted = is_inverted
        self._moment = moment
        self._mass = mass


class Circle(Shape):
    """
    Stores the physical state of a circle in 2D space.

    Attributes:
        _radius: A float representing the radius of the circle.
        _moment: A float representing the moment of inertia of the circle.
        _mass: A float representing the mass of the circle.
        _position: A vector representing the position of the center of mass of the shape.
        _velocity: A vector representing the velocity of the shape.
        _angle: A Float representing the angular displacement of the shape.
        _angular_velocity: A Float representing the angular velocity of the shape.
        _can_move: A boolean representing if the shape can move or not.
    """

    def __init__(
        self,
        radius,
        position,
        velocity=Vector(0, 0),
        angle=0,
        angular_velocity=0,
        can_move=False,
        is_inverted=False,
    ):
        """
        Initialize radius, position, velocity, angle, angular_velocity,
        can_move, and is_inverted. Calculate mass and moment.

        Args:
            radius: A float representing the radius of the circle.
            position: A vector representing the position of the
            center of mass of the shape.
            velocity: A vector representing the velocity of the shape.
            angle: A Float representing the angular displacement of the shape.
            angular_velocity: A Float representing the
            angular velocity of the shape.
            can_move: A boolean representing if the shape can move or not.
            is_inverted: A boolean representing if the
            mass of the shape is outside of it.
        """
        # Calculate mass and moment
        mass = pi * radius * radius
        moment = mass * radius * radius / 2

        # Initialize everything
        self._radius = radius
        super.__init__(
            position,
            velocity,
            angle,
            angular_velocity,
            can_move,
            is_inverted,
            moment,
            mass,
        )


class Polygon(Shape):
    """
    Stores the physical state of a polygon in 2D space.

    Attributes:
        _vertices: A list of vectors representing the vertices of the polygon.
        _radius: A float representing the distance between the center of
        mass and the furthest part of the polygon from the center of mass.
        _is_inverted: A boolean representing if the mass of the
        polygon is outside of it.
        _moment: A float representing the moment of inertia of the polygon.
        _mass: A float representing the mass of the polygon.
        _position: A vector representing the position of the
        center of mass of the shape.
        _velocity: A vector representing the velocity of the shape.
        _angle: A Float representing the angular displacement of the shape.
        _angular_velocity: A Float representing the
        angular velocity of the shape.
        _can_move: A boolean representing if the shape can move or not.
    """

    def __init__(
        self,
        vertices,
        position,
        velocity=Vector(0, 0),
        angle=0,
        angular_velocity=0,
        can_move=False,
        is_inverted=False,
    ):
        """
        Initialize vertices, position, velocity, angle, angular_velocity, can_move, and is_inverted.
        Calculate radius, mass, and moment.
        Offset position and vertices so the vertex (0, 0) is the center of mass of the polygon.

        Args:
            vertices: A list of vectors representing the vertices of the polygon
            radius: A float representing the distance between the center of mass and the furthest part of the polygon from the center of mass.
            position: A Vector representing the position of the center of mass of the shape.
            velocity: A vector representing the velocity of the shape.
            angle: A float representing the angular displacement of the shape.
            angular_velocity: A float representing the angular velocity of the shape.
            can_move: A boolean representing if the shape can move or not.
            is_inverted: A boolean representing if the mass of the shape is outside of it.
        """
        # Calculate mass and moment
        segment_areas = [Vector.det(vertices[i-1], vertices[i]) for i in range(len(vertices))]
        mass = abs(sum(segment_areas)) / 2
        x_com = sum(
            [
                (vertices[i - 1].x + vertices[i].x) * segment_areas[i]
                for i in range(len(vertices))
            ]
        ) / (6 * mass)
        y_com = sum(
            [
                (vertices[i - 1].y + vertices[i].y) * segment_areas[i]
                for i in range(len(vertices))
            ]
        ) / (6 * mass)
        center_of_mass = Vector(x_com, y_com)
        vertices = [Vector.diff(center_of_mass, vertex) for vertex in vertices]

        # Calculate the needed offset to center vertices around the center of mass.
