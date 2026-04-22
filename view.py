import pygame
pygame.init()

class View():
    """
    Displays the state of a level to a graphical window.

    Attributes:
        _level: A Level representing the level to display.
        _camera: A Vector representing the position of the camera.
        _path: A string representing the path of the folder with every sprite.
        _lerp_speed: A float representing the speed at which the camera
        follows the player.
        _window: A surface that will have the level drawn on it.
    """

    def __init__(self, level, path):
        """
        Initialize level, camera, path, lerp_speed, and window.

        Args:
            level: A Level to display.
            path: A string representing the path of the folder
            with every sprite.
        """
        self._level = level
        self._camera = level.player.position()
        self._path = path
        self._lerp_speed = 0.9
        self._window = pygame.display.set_mode((1200, 900))

    def update_window(self, _window):
        """
        Creates window to be run for each frame. 
        """
        screen = self._window
        pygame.display.set_caption('Want You Gone')

    def draw_sprite(self, angle, path):
        """
        Gets coordinates and rotation to display sprite.
        """
        #get image and rotate it
        character_original = pygame.image.load(path).convert_alpha()
        character_surface = pygame.transform.rotate(character_original, angle)
        position = self._camera.get_tuple
        character_rect = character_surface.get_rect(center = position)
        #draws image. Remember that a screen (display surface) is needed 
        screen.blit(character_rect, position)

    def draw_circle(self, x, y):
        """
        Gets coordinates of a circle to display and displays it.
        """
        circle_surface = pygame.Surface(400,400)
        circle_surface.set_alpha(0)
        pygame.draw.circle(circle_surface,Circle.color, Circle.position,Circle.radius)

    def draw_polygon(self):
        """
        Gets coordinates and image of a shape to display and displays that shape.
        """
        polygon_surface = pygame.Surface(400,400)
        polygon_surface.set_alpha(0)
        pygame.draw.polygon(polygon_surface, Polygon.color, Polygon.vertices,)

    def update_lerp(self, x, y):
        pass

    def check_cull(self, x, y):
        """
        Gets coordinates from and object and determines whether or not to display them.
        """
        screen_rect = pygame.Rect(0, 0, 1200, 900)
        return screen_rect.collidepoint(x,y)


