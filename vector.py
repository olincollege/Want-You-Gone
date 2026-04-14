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
        self.x = x
        self.y = y

    def __repr__(self):
        """
        Represent the vector as a string with the row vector format: (x, y)

        Returns:
            A string representing the vector in row vector format
        """
        return f"({self.x}, {self.y})"
    
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
        Increments a vector by another vector.

        Args:
            increment: A vector representing the amounts to increase self._x and self._y by.
        """
        self._x += increment.x
        self._y += increment.y

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