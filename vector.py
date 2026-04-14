"""
Contains the Vector class.
"""

class Vector():
    """
    Store a vector as an x-y coordinate pair.

    Attributes:
        x: A float representing the x component of the vector.
        y: A float representing the y component of the vector.
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

    def add(self, increment):
        """

        """