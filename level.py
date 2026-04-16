"""
Contains the Level class.
"""

from shape import Circle, Polygon

class Level():
    """
    Store the physical state of a set of 2D shapes.

    Attributes:
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
        # Read the file for player.
        with open(path + "player.txt", "r", encoding="utf-8") as f:
            player_text = f.read()

        # Extract the attributes of player.
        player_position = self.read_vector(
            self.read_variable(player_text, "position"))
        player_velocity = self.read_vector(
            self.read_variable(player_text, "velocity"))
        player_angle = float(self.read_variable(player_text, "angle"))
        player_angular_velocity = float(
            self.read_variable(player_text, "angular_velocity"))
        player_can_move = True
        player_is_inverted = False
        player_is_bouncy = self.read_boolean(
            self.read_variable(player_text, "is_bouncy"))
        player_radius = abs(float(self.read_variable(player_text, "radius")))

        # Initialize player.
        self._player = Circle(player_position,
                              player_velocity,
                              player_angle,
                              player_angular_velocity,
                              player_can_move,
                              player_is_inverted,
                              player_is_bouncy,
                              player_radius)

        # ----------------------------------------------------------------------

        # Read the file for boarder.
        with open(path + "boarder.txt", "r", encoding="utf-8") as f:
            boarder_text = f.read()

        # Extract the attributes of boarder.
        player_position = self.read_vector(
            self.read_variable(boarder_text, "position"))
        player_velocity = self.read_vector(
            self.read_variable(boarder_text, "velocity"))
        player_angle = float(self.read_variable(boarder_text, "angle"))
        player_angular_velocity = float(self.read_variable(
            boarder_text, "angular_velocity"))
        player_can_move = False
        player_is_inverted = True
        player_is_bouncy = self.read_boolean(self.read_variable(
            boarder_text, "is_bouncy"))
        player_vertices = [self.read_vector(vertex)
                           for vertex in self.read_list(
                           self.read_variable(boarder_text, "vertices"))]

        # Initialize boarder.
        self._boarder = Polygon(player_vertices,
                         player_position,
                         player_velocity,
                         player_angle,
                         player_angular_velocity,
                         player_can_move,
                         player_is_inverted,
                         player_is_bouncy)

    @classmethod
    def read_variable(cls, text, name):
        """
        Find the value of a variable as defined in a string.

        Args:
            text: A string representing a set of variable names and
                  the values associated with them.
            name: The name of the variable to find the value of.
        
        Returns:
            A string representing the value of the variable.

        Raises:
            ValueError: If variable is not defined in text.
        """

    @classmethod
    def read_list(cls, text):
        """
        Find the elements in a list described by a string.

        Args:
            test: A string representing a list of values.
        
        Returns:
            A list representing the values described in text.
        """

    @classmethod
    def read_vector(cls, text):
        """
        Find the Vector described by a string.

        Args:
            text: A string representing a vector.
        
        Returns:
            The Vector described by text.
        
        Raises:
            ValueError: If the vector doesn't have two indices
            or if any of its indices can't be cast as floats.
        """

    @classmethod
    def read_boolean(cls, text):
        """
        Find the boolean described by a string.

        Args:
            text: A string representing a boolean.
        
        Returns:
            The boolean described by text.

        Raises:
            ValueError: If text is neither "True" nor "False".
        """
        if text == "True":
            return True
        if text == "False":
            return False
        raise ValueError("value is neither \"True\" nor \"False\"")
