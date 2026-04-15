"""
Contains the Vector class.
"""

class Vector():
    """
    Store a vector as an x-y coordinate pair.

    Attributes:
        _x: A float representing the x component of the vector.
        _y: A float representing the y component of the vector.
    """

    def __init__(self, x, y):
        """
        Initialize x and y.
        """
        self._x = x
        self._y = y

    def __repr__(self):
        """
        Represent the vector as a string with the row vector format: (x, y)

        Returns:
            A string representing the vector in row vector format
        """
        return f"({self.x}, {self.y})"
    
    def get_tuple(self):
        """
        Represent the vector as a tuple with the format: (x, y)

        Returns:
            A tuple holding the values of _x and _y in that order
        """
        return (self._x, self._y)
    
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
            increment: A vector representing the amounts to increase self._x and self._y by.
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
        self._x += increment * (to.x - self._x)
        self._y += increment * (to.y - self._y)

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