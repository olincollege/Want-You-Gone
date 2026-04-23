"""
Contains the View class.
"""

from math import ceil
import pygame
from vector import Vector
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
        self._window_center = Vector(600, 450)
        self._level = level
        self._camera = Vector.diff(self._window_center, level.player.position)
        self._path = path
        self._lerp_speed = 0.9
        self._window = pygame.display.set_mode((1200, 900))
        pygame.display.set_caption('Want You Gone')
        self.refresh(0)

    def refresh(self, dt):
        """
        Refresh the display to show the current state of the level.

        Args:
            dt: A float representing the time since the last refresh.
        """
        self.update_lerp(dt)
        self._window.fill(self._level.border.color)
        # self.draw_background(self._path + "background.png")
        for polygon in self._level.polygons:
            self.draw_polygon(polygon)
        # self.draw_sprite(self._level.player, self._path + "player.png")
        self.draw_circle(self._level.player)
        pygame.display.flip()

    def draw_background(self, sprite_path):
        """
        Draws the background texture on the window in the shape of the border.

        Args:
            sprite_path: A string representing the file path
            of the background texture.
        """
        background = pygame.image.load(sprite_path).convert_alpha()
        self._window.blit(background, (0,0))

    def draw_sprite(self, shape, sprite_path):
        """
        Draws a sprite on the window based on the position and rotation
        of a shape and the position of the camera.

        Args:
            shape: A Circle or Polygon representing the shape to display.
            path: A string representing the file path of the sprite to display.
        """
        # Get image and rotate it.
        sprite = pygame.image.load(sprite_path).convert_alpha()
        rotated_sprite = pygame.transform.rotate(sprite, shape.angle)
        position = Vector.diff(self._camera, shape.position).add(
            Vector(shape.radius, shape.radius)).get_tuple()
        sprite_rect = rotated_sprite.get_rect(center = position)

        # Draw image on the window.
        self._window.blit(sprite_rect, position)

    def draw_circle(self, circle):
        """
        Draws a circle on the window based on the position and rotation
        of a circle and the position of the camera.

        Args:
            circle: A Circle representing the circle to display.
        """
        if self.check_cull(circle):
            return
        circle_surface = pygame.Surface((
            ceil(circle.radius * 2), ceil(circle.radius * 2)), pygame.SRCALPHA)
        pygame.draw.circle(circle_surface, circle.color,
                           circle.position.get_tuple(), circle.radius)
        position = Vector.sum(Vector.diff(self._camera, circle.position),
                              Vector(-circle.radius, -circle.radius))
        circle_rect = circle_surface.get_rect(center = position.get_tuple())
        self._window.blit(circle_surface, circle_rect)
        print(f"{circle_rect = }")

    def draw_polygon(self, polygon):
        """
        Draws a polygon on the window based on the position and rotation
        of a polygon and the position of the camera.

        Args:
            polygon: A Polygon representing the polygon to display.
        """
        if self.check_cull(polygon):
            return
        polygon_surface = pygame.Surface(
            (ceil(polygon.radius * 2), ceil(polygon.radius * 2)), pygame.SRCALPHA)
        pygame.draw.polygon(polygon_surface, polygon.color,
        [vertex.get_tuple() for vertex in polygon.rotated_vertices()])
        position = Vector.sum(Vector.diff(self._camera, polygon.position),
                              Vector(-polygon.radius, -polygon.radius))
        polygon_rect = polygon_surface.get_rect(center = position.get_tuple())
        self._window.blit(polygon_surface, polygon_rect)

    def update_lerp(self, dt):
        """
        Updates the camera's position to smoothly follow the player.

        Args:
            dt: A float representing the time since the last refresh.
        """
        self._camera.lerp(Vector.diff(self._window_center,
                    self._level.player.position), self._lerp_speed * dt)

    def check_cull(self, shape):
        """
        Determines whether or not to display a shape.

        Args:
            shape: A Circle or Polygon representing the shape to check.
        
        Returns:
            A boolean representing whether or not to
            cull (not display) the shape.
        """
        screen_rect = self._window.get_rect()
        shape_rect = pygame.Rect(Vector.sum(shape.position,
        Vector(shape.radius, shape.radius)).get_tuple(),
        (shape.radius * 2, shape.radius * 2))
        return not screen_rect.colliderect(shape_rect)
