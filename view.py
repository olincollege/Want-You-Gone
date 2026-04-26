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
        _background_texture: A surface representing the background texture to draw.
        _player_sprite: A surface representing the sprite to draw for the player.
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
        self._lerp_speed = 0.97
        self._window = pygame.display.set_mode((1200, 900))
        pygame.display.set_caption('Want You Gone')
        self._background_texture = pygame.image.load(
            self._path + "night_sky.png").convert_alpha()
        self._player_sprite = pygame.image.load(
            self._path + "wheatley.png").convert_alpha()
        self.refresh(0)

    def refresh(self, dt):
        """
        Refresh the display to show the current state of the level.

        Args:
            dt: A float representing the time since the last refresh.
        """
        self.update_lerp(dt)
        self._window.fill(self._level.border.color)
        self.draw_background()
        for polygon in self._level.polygons:
            self.draw_polygon(polygon)
        self.draw_player(self._level.player)
        #self.draw_circle(self._level.player)
        pygame.display.flip()

    def draw_background(self):
        """
        Draws the background texture on the window in the shape of the border.

        Args:
            texture_path: A string representing the file path
            of the background texture.
        """
        texture = pygame.transform.scale_by(self._background_texture, 1.25)
        texture_rect = texture.get_rect()
        texture_rect.center = self._window_center.get_tuple()
        mask = pygame.Surface((texture_rect.width, texture_rect.height))
        mask.fill(self._level.border.color)
        vertices = [Vector.sum(vertex, self._camera).get_tuple() for vertex in self._level.border.world_vertices()]
        pygame.draw.polygon(mask, (0, 0, 0), vertices)
        mask_rect = mask.get_rect()
        mask_rect.center = self._window_center.get_tuple()

        tmp_image = texture.copy() # make a copy of the texture to keep it unchanged for future usage
        mask.set_colorkey((0, 0, 0)) # we want the black colored parts of the mask to be transparent
        tmp_image.blit(mask, (0, 0)) # blit the mask to the texture. the black parts are transparent so we see the pixels of the texture there

        tmp_rect = tmp_image.get_rect()
        tmp_rect.center = self._window_center.get_tuple()
        tmp_image.set_colorkey(self._level.border.color)
        self._window.blit(texture, texture_rect)
        self._window.blit(mask, mask_rect)
        self._window.blit(tmp_image, tmp_rect)

    def draw_player(self, shape):
        """
        Draws a sprite on the window based on the position and rotation
        of a shape and the position of the camera.

        Args:
            shape: A Circle or Polygon representing the shape to display.
            path: A string representing the file path of the sprite to display.
        """
        # Get image and rotate it.
        sprite = pygame.transform.scale_by(self._player_sprite, 0.47)
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
