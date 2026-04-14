"""
Contains the Shape class and its subclasses Circle and Polygon.
"""

class Shape():
    """
    Stores the physical state of 2D shape in space.

    Attributes:
        _position: A vector representing the position of the center of mass of the shape.
        _radius: A float representing the distance between the center of mass and the furthest part of the shape from the center of mass.
        _velocity: A vector representing the velocity of the shape.
        _angle: A Float representing the angular displacement of the shape.
        _angular_velocity: A Float representing the angular velocity of the shape.
        _can_move: A boolean representing if the shape can move or not.
        _is_inverted: A boolean representing if the mass of the shape is outside of it.
        _elasticity: A float between 0 and 1 representing the coefficient of elasticity of the shape.
        _friction (float)
        _moment (float)
        _mass (float)

    """