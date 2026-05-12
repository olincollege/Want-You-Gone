"""
Contains the Vector class.
"""

from math import sin, cos, sqrt


class Vector:
    """
    Store a vector as an x-y coordinate pair.

    Attributes:
        _x: A float representing the x component of the vector.
        _y: A float representing the y component of the vector.
    """

    def __init__(self, x, y):
        """
        Initialize x and y.

        Args:
            x: A number representing the x component of the vector.
            y: A number representing the y component of the vector.
        """
        self._x = float(x)
        self._y = float(y)

    def __repr__(self):
        """
        Represent the vector as a string with the row vector format: (x, y)

        Returns:
            A string representing the vector in row vector format
        """

        def _fmt(v):
            return int(v) if v == int(v) else v

        return f"({_fmt(self._x)}, {_fmt(self._y)})"

    def get_tuple(self):
        """
        Represent the vector as a tuple with the format: (x, y)

        Returns:
            A tuple holding the values of _x and _y in that order
        """
        return (self._x, self._y + 0.5)

    @property
    def x(self):
        """
        Get self._x.

        Returns:
            self._x: A float representing the x component of the vector.
        """
        return self._x

    @property
    def y(self):
        """
        Get self._y.

        Returns:
            self._y: A float representing the y component of the vector.
        """
        return self._y

    def add(self, increment):
        """
        Increments the vector by another vector.

        Args:
            increment: A vector representing the amounts to increase
            self._x and self._y by.
        """
        self._x += increment.x
        self._y += increment.y

    def lerp(self, to, increment):
        """
        Moves the vector a fraction of the way towards another vector.

        Args:
            to: A Vector representing the point self is moving towards.
            increment: A float between 0 and 1 representing the fraction
            of the way self is incremented by
        """
        self.add(Vector(to.x - self._x, to.y - self._y).scale(increment))

    def rotate(self, angle):
        """
        Find the vector made by rotating self a number of radians
        counter clockwise about the origin.

        Args:
            angle: A float representing the angle by which to rotate the vector.

        Returns:
            A Vector representing self rotated angle radians about the origin.
        """
        return Vector(
            self._x * cos(angle) - self._y * sin(angle),
            self._x * sin(angle) + self._y * cos(angle),
        )

    def scale(self, scalar):
        """
        Multiply self by a scalar.

        Args:
            scalar: A float representing the amount to scale self by.

        Returns:
            A Vector made by scaling self by scalar.
        """
        return Vector(self._x * scalar, self._y * scalar)

    def normal(self):
        """
        Find the normal vector that points in the direction of self.

        Returns:
            A Vector with length 1 that points in the direction of self.
        """
        # Calculate the magnitude of self and divide self by it
        magnitude = sqrt(self.magnitude_squared())

        # If self has no direction return the vector with no direction
        if magnitude == 0:
            return Vector(0, 0)

        return self.scale(1 / magnitude)

    def line_point_distance(self, line1, line2):
        """
        Find the signed distance between a point and a line segment.

        Args:
            self: A Vector representing the point.
            line1: A Vector representing the right end of the line
            when observed facing in the positive direction.
            line2: A Vector representing the left end of the line
            when observed facing in the positive direction.

        Returns:
            A float representing the signed distance between self and the line
            segment between line1 and line2. The distance is positive when
            the point is on the right side of the line when observed from
            the perspective of line1, facing line2.
            None: If the point on the line segment
            that self is closest to is line1 or line2.
        """
        tangent = Vector.diff(line1, line2).normal()

        # If the point is behind line1 return None.
        if Vector.dot(tangent, Vector.diff(line1, self)) < 0:
            return None

        # If the point is past line2 return None.
        if Vector.dot(tangent, Vector.diff(line2, self)) > 0:
            return None

        # Otherwise return the determinant of the matrix
        # [self - line1 | tangent]
        return Vector.det(Vector.diff(self, line1), tangent)

    def magnitude_squared(self):
        """
        Find the magnitude of self squared.

        Returns:
            A float representing the magnitude of self squared.
        """
        magnitude_squared = self._x * self._x + self._y * self._y
        if abs(magnitude_squared) < 0.1:
            return 0
        return magnitude_squared

    @classmethod
    def dot(cls, vec1, vec2):
        """
        Calculate the dot product between two vectors.

        Args:
            vec1: A vector to be put on the left side of the dot product.
            vec2: A vector to be put on the right side of the dot product.

        Returns:
            A float representing the dot product between vec1 and vec2.
        """
        return vec1.x * vec2.x + vec1.y * vec2.y

    @classmethod
    def diff(cls, tail, head):
        """
        Find the vector, centered at the origin, that goes from tail to head.

        Args:
            tail: A vector representing the starting point of a vector.
            head: A vector representing the ending point of a vector.

        Returns:
            A vector representing the x and y difference from head to tail.
        """
        return Vector(head.x - tail.x, head.y - tail.y)

    @classmethod
    def det(cls, vec1, vec2):
        """
        Find the determinant of the matrix made by combining two vectors.

        Args:
            vec1: A Vector representing the left column of the matrix.
            vec2: A Vector representing the right column of the matrix.

        Returns:
            The determinant of the matrix [vec1 | vec2]
        """
        return vec1.x * vec2.y - vec2.x * vec1.y

    @classmethod
    def sum(cls, vec1, vec2):
        """
        Find the sum of two vectors.

        Args:
            vec1: A Vector to be summed with vec2.
            vec2: A Vector to be summed with vec1.

        Returns:
            A Vector representing vec1 + vec2
        """
        return Vector(vec1.x + vec2.x, vec1.y + vec2.y)

    @classmethod
    def sum_all(cls, vectors):
        """
        Find the sum of a list of vectors.

        Args:
            vectors: A list of Vectors to be summed together.

        Returns:
            A Vector representing the sum of all the vectors in vectors.
        """
        if not vectors:
            return Vector(0, 0)
        x_sum = sum(vector.x for vector in vectors)
        y_sum = sum(vector.y for vector in vectors)
        return Vector(x_sum, y_sum)
