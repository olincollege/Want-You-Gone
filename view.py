"""
Contains the View class.
"""

from math import ceil, degrees
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
        self._camera = Vector.diff(level.player.position, self._window_center)
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
        self.draw_background(self._path + "night_sky_.png")
        for polygon in self._level.polygons:
            self.draw_polygon(polygon)
        self.draw_sprite(self._level.player, self._path + "wheatley.png")
        #self.draw_circle(self._level.player)
        pygame.display.flip()

    def draw_background(self, sprite_path):
        """
        Draws the background texture on the window in the shape of the border.

        Args:
            sprite_path: A string representing the file path
            of the background texture.
        """
        background = pygame.image.load(sprite_path).convert_alpha()
        background = pygame.transform.scale_by(background,1.3)
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
        sprite = pygame.transform.scale_by(sprite, 0.47)
        rotated_sprite = pygame.transform.rotate(sprite, degrees(shape.angle))
        position = Vector.sum(shape.position, self._camera) 
        position = position.get_tuple()
        sprite_rect = rotated_sprite.get_rect(center = position)
        self._window.blit(rotated_sprite, sprite_rect)

    def draw_circle(self, circle):
        """
        Draws a circle on the window based on the position and rotation
        of a circle and the position of the camera.

        Args:
            circle: A Circle representing the circle to display.
        """
        if self.check_cull(circle):
            return
        r = ceil(circle.radius)
        circle_surface = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
        # Draw at the center of the surface, not at world coords.
        pygame.draw.circle(circle_surface, circle.color, (r, r), circle.radius)
        # World -> screen: screen_pos = world_pos + camera.
        # Blit so the surface center lands on screen_pos.
        screen_pos = Vector.sum(circle.position, self._camera)
        blit_pos = Vector.sum(screen_pos, Vector(-r, -r))
        self._window.blit(circle_surface, blit_pos.get_tuple())

    def draw_polygon(self, polygon):
        """
        Draws a polygon on the window based on the position and rotation
        of a polygon and the position of the camera.

        Args:
            polygon: A Polygon representing the polygon to display.
        """
        if self.check_cull(polygon):
            return
        r = ceil(polygon.radius)
        polygon_surface = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
        # Rotated vertices are relative to the polygon center.
        # Offset them to the center of the surface so they draw correctly.
        local_verts = [
            (v.x + r, v.y + r) for v in polygon.rotated_vertices()
        ]
        pygame.draw.polygon(polygon_surface, polygon.color, local_verts)
        # World -> screen: screen_pos = world_pos + camera.
        screen_pos = Vector.sum(polygon.position, self._camera)
        blit_pos = Vector.sum(screen_pos, Vector(-r, -r))
        self._window.blit(polygon_surface, blit_pos.get_tuple())

    def update_lerp(self, dt):
        """
        Updates the camera's position to smoothly follow the player.

        Args:
            dt: A float representing the time since the last refresh.
        """
        self._camera.lerp(Vector.diff(self._level.player.position,
                    self._window_center), self._lerp_speed * dt)

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
        # World -> screen: screen_pos = world_pos + camera.
        screen_pos = Vector.sum(shape.position, self._camera)
        r = shape.radius
        shape_rect = pygame.Rect(
            screen_pos.x - r, screen_pos.y - r, r * 2, r * 2
        )
        return not screen_rect.colliderect(shape_rect)
