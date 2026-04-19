"""
Contains the view class
"""

class View():
    """
    Gets info from other classes and displays based on that.

    Attributes:
    _x: A float representing the x coordinate of the player
    _y: A float representing the y coordinate of the player
    _imagepath: 
    self.lerp_speed: A float representing the speed of the camera.

    """

    def __init__(self, x, y, imagepath):
        """
        Initialize x, y coordinates and the image path to retrieve image.

        Args:
        x: A float representing the x coordinate of the object to display. 
        y: A float representing the y coordinate of the object to display.
        """
        self._x = float(x)
        self._y = float(y)
        self._imagepath = str(imagepath)

    def display_window(self):
        """
        Sets the display dimensions and chooses where to display.
        """
        pygame.display.set_mode((800, 600))

    def display_objects(self):
        """
        Gets coordinates from and object and determines whether or not to display them.
        """
        surface = pygame.image.load(self._imagepath).convert()

    def draw_shapes(self):
        """
        Gets coordinates and image of a shape to display and displays that shape.
        """
        pass

    def update_lerp(self):
        pass

    def check_cull(self):
        pass


