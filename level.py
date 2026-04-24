"""
Contains the Level class.
"""

from math import sqrt, copysign
import json
from shape import Circle, Polygon
from vector import Vector


class Level:
    """
    Store the physical state of a set of 2D shapes.

    Attributes:
        _gravity: A Vector representing the gravity on the level.
        self._path: A string representing the path to the folder
        with all the starting data for the level.
        self._player: A Circle representing the player character.
        self._border: A Polygon representing the outmost border
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
    _gravity = Vector(0, 30)
    _jump_strength = 5
    _default_cor = 0.2
    _bouncy_cor = 0.8
    _friction_coefficient = 0.5

    def __init__(self, path):
        """
        Initialize all attributes from the files in a folder.

        Args:
            path: A string representing the path of the folder.
        """
        self._path = path
        self.restart()

    def restart(self):
        """
        Set all attributes to their default values.
        """
        # Read the file for player.
        with open(self._path + "player.json", "r", encoding="utf-8") as file:
            player_attributes = json.load(file)

        # Initialize player.
        self._player = Circle(
            player_attributes["radius"],
            self.make_vector(player_attributes["position"]),
            self.make_vector(player_attributes["velocity"]),
            player_attributes["angle"],
            player_attributes["angular_velocity"],
            True,
            False,
            player_attributes["is_bouncy"],
            tuple(player_attributes["color"]),
        )

        # ----------------------------------------------------------------------

        # DO NOT REMOVE THE COMMENT ATTRIBUTES FROM THE JSON
        # THEY ARE FOR HUMAN READABILITY. NOT USED IN CODE

        # Read the file for border.
        with open(self._path + "border.json", "r", encoding="utf-8") as file:
            border_attributes = json.load(file)

        # Initialize border.
        self._border = Polygon(
            self.make_vector(border_attributes["vertices"]),
            self.make_vector(border_attributes["position"]),
            self.make_vector(border_attributes["velocity"]),
            border_attributes["angle"],
            border_attributes["angular_velocity"],
            False,
            True,
            border_attributes["is_bouncy"],
            tuple(border_attributes["color"]),
        )

        # ----------------------------------------------------------------------

        # Read the file for polygons.
        with open(self._path + "polygons.json", "r", encoding="utf-8") as file:
            polygons_attributes = json.load(file)

        # Initialize polygons.
        self._polygons = [
            Polygon(
                self.make_vector(polygon_attributes["vertices"]),
                self.make_vector(polygon_attributes["position"]),
                self.make_vector(polygon_attributes["velocity"]),
                polygon_attributes["angle"],
                polygon_attributes["angular_velocity"],
                False,
                False,
                polygon_attributes["is_bouncy"],
                tuple(polygon_attributes["color"]),
            )
            for polygon_attributes in polygons_attributes
        ]

    @classmethod
    def make_vector(cls, json_input):
        """
        Convert lists of numbers to Vectors,
        lists of lists of numbers to lists of Vectors,
        and so on.

        Args:
            json_input: A list of numbers (floats or integers),
            a list of lists of numbers, or a nested list of a higher degree.

        Returns:
            The same nested list structure as json_input but with Vectors
            replacing the lowest lists in the hierarchy.

        Raises:
            ValueError: If a base list is not of length two.
        """
        # If json_input is a list of numbers return it as a Vector.
        if isinstance(json_input[0], int) or isinstance(json_input[0], float):
            if len(json_input) != 2:
                raise ValueError("A base list is not of length two!")
            return Vector(float(json_input[0]), float(json_input[1]))

        # Otherwise go a level deeper into the list
        return [cls.make_vector(i) for i in json_input]

    def update(self, dt, is_jumping, is_bouncing):
        """
        Update the position velocity, angular velocity,
        and angle of all shapes on the level.
        """
        # Apply forces
        self._player.force(self._gravity.scale(self._player.mass), dt)
        self._border.force(self._gravity.scale(self._border.mass), dt)
        for polygon in self._polygons:
            polygon.force(self._gravity.scale(polygon.mass), dt)

        # Update positions
        self._player.update_position(dt)
        self._border.update_position(dt)
        for polygon in self._polygons:
            polygon.update_position(dt)

        # THEN do collision detection and response
        for polygon in self._polygons + [self._border]:
            if (polygon.radius + self._player.radius) ** 2 < Vector.diff(
                polygon.position, self._player.position).magnitude_squared():
                continue

            shortest_distance = None
            closest_line = None
            closest_vertex = None
            vertices = polygon.world_vertices()

            for i, vertex in enumerate(vertices):
                distance = self._player.position.line_point_distance(vertices[i - 1], vertex)
                if distance is not None and 0 < distance < self._player.radius:
                    if shortest_distance is None or distance < shortest_distance:
                        shortest_distance = distance
                        closest_line = i
                        closest_vertex = None

                dist_to_vert = sqrt(Vector.diff(vertex, self._player.position).magnitude_squared())
                if dist_to_vert < self._player.radius:
                    if shortest_distance is None or dist_to_vert < shortest_distance:
                        shortest_distance = dist_to_vert
                        closest_vertex = i
                        closest_line = None

            if shortest_distance is not None:
                if closest_vertex is not None:
                    contact_point = vertices[closest_vertex]
                else:
                    a, b = vertices[closest_line - 1], vertices[closest_line]
                    ab = Vector.diff(a, b)
                    ap = Vector.diff(a, self._player.position)
                    t = max(0, min(1, Vector.dot(ap, ab) / ab.magnitude_squared()))
                    contact_point = Vector.sum(a, ab.scale(t))

                collision_normal = Vector.diff(contact_point, self._player.position).normal()
                
                # Push out
                overlap = (self._player.radius - shortest_distance) + 0.05
                self._player.position.add(collision_normal.scale(overlap))
                
                # ONLY cancel velocity going INTO the surface
                v_dot_n = Vector.dot(self._player.velocity, collision_normal)
                if v_dot_n < 0:  # Moving into surface
                    # Remove just the component going into the surface
                    self._player._velocity.add(collision_normal.scale(-v_dot_n))
                
                # Apply bounce if bouncing
                if is_bouncing:
                    bounce = collision_normal.scale(self._jump_strength)
                    self._player.impulse(bounce)
                
                break

    def circle_corner_impulse(self, circle, polygon, vertex,
                              is_jumping, is_bouncing):
        """
        Find the impulse vector for a collision between a circle and a corner.

        Args:
            circle: A Circle representing the circle in the collision.
            polygon: A Polygon representing the polygon in the collision.
            vertex: A integer representing the index of the corner in the
            collision.
            is_jumping: A boolean representing whether or not the player is
            jumping in the collision.
            is_bouncing: A boolean representing whether or not the player is
            bouncing in the collision.

        Returns:
            A Vector representing the impulse vector for the collision.
        """
        # Find the normal vector for the collision.
        normal = Vector.diff(polygon.world_vertices()[vertex], circle.position)
        normal = normal.normal()

        # Find the relative velocity of the circle and the vertex.
        relative_velocity = Vector.diff(circle.velocity, polygon.velocity)

        return self.calculate_impulse(
            circle, polygon, normal, relative_velocity, is_jumping, is_bouncing)

    def circle_edge_impulse(self, circle, polygon, line,
                            is_jumping, is_bouncing):
        """
        Find the impulse vector for a collision between a circle and an edge.

        Args:
            circle: A Circle representing the circle in the collision.
            polygon: A Polygon representing the polygon in the collision.
            line: A integer representing the index of the edge in the
            collision. The edge is between vertices line - 1 and line.
            is_jumping: A boolean representing whether or not the player is
            jumping in the collision.
            is_bouncing: A boolean representing whether or not the player is
            bouncing in the collision.

        Returns:
            A Vector representing the impulse vector for the collision.
        """
        # Find the normal vector for the collision.
        tangent = Vector.diff(polygon.world_vertices()[line],
            polygon.world_vertices()[line - 1]).normal()
        normal = Vector(-tangent.y, tangent.x)

        # Find the relative velocity of the circle and the edge.
        relative_velocity = Vector.diff(circle.velocity, polygon.velocity)

        return self.calculate_impulse(
            circle, polygon, normal, relative_velocity, is_jumping, is_bouncing)

    def calculate_impulse(self, circle, polygon, normal, relative_velocity,
                      is_jumping, is_bouncing):
        """
        Find the impulse vector for a collision between a circle and a polygon.
        """
        dot_product = Vector.dot(normal, relative_velocity)
        
        print(f"  calculate_impulse: normal={normal}, rel_vel={relative_velocity}, dot={dot_product}")
        
        if dot_product >= 0:
            print(f"    -> Rejecting (separating)")
            return Vector(0, 0)

        e = self._default_cor
        if circle.is_bouncy or polygon.is_bouncy:
            e = self._bouncy_cor
        if not is_bouncing:
            e = 0
        
        jump = self._jump_strength if is_jumping else 0

        impulse_magnitude = (-(1 + e) * dot_product + jump)
        result = normal.scale(impulse_magnitude)
        
        print(f"    -> impulse_magnitude={impulse_magnitude}, result={result}")
        
        return result

    def circle_corner_impulse(self, circle, polygon, vertex,
                          is_jumping, is_bouncing):
        """Find the impulse vector for a collision between a circle and a corner."""
        normal = Vector.diff(polygon.world_vertices()[vertex], circle.position)
        normal = normal.normal()

        # Relative velocity: circle moving relative to polygon
        relative_velocity = Vector.diff(polygon.velocity, circle.velocity)

        return self.calculate_impulse(
            circle, polygon, normal, relative_velocity, is_jumping, is_bouncing)

    def circle_edge_impulse(self, circle, polygon, line,
                            is_jumping, is_bouncing):
        """Find the impulse vector for a collision between a circle and an edge."""
        tangent = Vector.diff(polygon.world_vertices()[line],
            polygon.world_vertices()[line - 1]).normal()
        normal = Vector(-tangent.y, tangent.x)

        # Relative velocity: circle moving relative to polygon
        relative_velocity = Vector.diff(polygon.velocity, circle.velocity)

        return self.calculate_impulse(
            circle, polygon, normal, relative_velocity, is_jumping, is_bouncing)
    
    def get_closest_point_on_edge(self, p, a, b):
        """
        Finds the point on segment AB closest to point P.
        """
        ab = Vector.diff(b, a)
        ap = Vector.diff(p, a)
        # Project point p onto the line segment ab
        t = Vector.dot(ap, ab) / ab.magnitude_squared()
        t = max(0, min(1, t))  # Clamp to the segment
        return Vector.sum(a, ab.scale(t))

    @property
    def player(self):
        """Get player"""
        return self._player

    @property
    def border(self):
        """Get border"""
        return self._border

    @property
    def polygons(self):
        """Get border"""
        return self._polygons
