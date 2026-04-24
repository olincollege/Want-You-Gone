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
    _gravity = Vector(0, 100)
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

        Args:
            dt: A float representing the amount of time to update for.
            is_jumping: A boolean representing whether or not the player is
            jumping in this update.
            is_bouncing: A boolean representing whether or not the player is
            bouncing in this update.
        """
        # Update the velocity of all shapes by adding gravity to them.
        self._player.force(self._gravity.scale(self._player.mass), dt)
        self._border.force(self._gravity.scale(self._border.mass), dt)
        for polygon in self._polygons:
            polygon.force(self._gravity.scale(polygon.mass), dt)

        # Update the positions and angles of all shapes by adding
        # their velocity and angular velocity to them.
        self._player.update_position(dt)
        self._border.update_position(dt)
        for polygon in self._polygons:
            polygon.update_position(dt)

        # ----------------------------------------------------------------------

        # Find the impulse vector for every collision with the player.
        collisions = []

        # Find the shortest distance between the player's center and
        # the closest point to it on each shape.
        for poly_index, polygon in enumerate(self._polygons + [self._border]):
            # If the player is too far from the polygon, skip it.
            if (polygon.radius + self.player.radius) ** 2 < Vector.diff(
                polygon.position, self._player.position).magnitude_squared():
                continue

            # Otherwise find the closest point on the polygon
            # to the player and the distance between them.
            shortest_distance = None
            closest_line = None
            closest_vertex = None
            vertices = polygon.world_vertices()
            for i, vertex in enumerate(vertices):
                # Find the distance between the player and the line segment
                # between vertices i - 1 and i and update
                # shortest_distance if it is shorter.
                distance = self._player.position.line_point_distance(
                    vertices[i - 1], vertex)
                if distance is not None and (shortest_distance is None or
                    abs(distance) < abs(shortest_distance)):
                    shortest_distance = distance
                    closest_line = i
                    closest_vertex = None

                # Find the distance between the player and the vertex
                # and update shortest_distance if it is shorter.
                distance = sqrt(Vector.diff(
                    self._player.position, vertex).magnitude_squared())
                if shortest_distance is None or abs(distance) < abs(
                    shortest_distance):
                    shortest_distance = distance
                    closest_vertex = i
                    closest_line = None

            # Determine the type of collision the player
            # is having with each polygon.

            # If the player is not colliding with the polygon, skip it.
            if (shortest_distance is None or
                shortest_distance > self._player.radius):
                continue
            print("")
            print(f"is_inverted: {polygon.is_inverted}")
            print(f"shortest_distance: {shortest_distance}")
            #print(f"closest_line: {polygon.vertices[closest_line - 1]} to {polygon.vertices[closest_line]}")
            print(f"poly_index: {poly_index}")

            # If the player is colliding with a vertex:
            if closest_vertex is not None:
                # If the player's center is outside the polygon,
                # add the impulse for the vertex.
                if Vector.det(
                    Vector.diff(vertices[closest_vertex - 1],
                                vertices[closest_vertex]),
                    Vector.diff(vertices[closest_vertex],
                                vertices[(closest_vertex + 1) % len(vertices)])
                ) < 0:
                    collisions.append(self.circle_corner_impulse(
                        self._player, polygon, closest_vertex,
                        is_jumping, is_bouncing))

                # If the player's center is inside the polygon,
                # add the impulses for the two edges connected to the vertex.
                else:
                    collisions.append(self.circle_edge_impulse(
                        self._player, polygon, closest_vertex,
                        is_jumping, is_bouncing))
                    collisions.append(self.circle_corner_impulse(
                        self._player, polygon, (closest_vertex + 1
                        ) % len(vertices), is_jumping, is_bouncing))

            hit_edge = False
            # If the player is colliding with an edge:
            if closest_line is not None:
                # If the player is colliding with the closest edge,
                # and the one next to it in the clockwise direction,
                # add the impulse for those edges.
                if (Vector.det(
                    Vector.diff(vertices[closest_line - 2],
                                vertices[closest_line - 1]),
                    Vector.diff(vertices[closest_line - 1],
                                vertices[closest_line])
                ) > 0 and Vector.det(
                    Vector.diff(self._player.position,
                                vertices[closest_line - 1]),
                    Vector.diff(vertices[closest_line - 2],
                                vertices[closest_line - 1])
                ) < self._player.radius ** 2):
                    collisions.append(self.circle_edge_impulse(
                        self._player, polygon, closest_line - 1,
                        is_jumping, is_bouncing))
                    collisions.append(self.circle_edge_impulse(
                        self._player, polygon, closest_line,
                        is_jumping, is_bouncing))
                    hit_edge = True

                # If the player is colliding with the closest edge,
                # and the one next to it in the counterclockwise direction,
                # add the impulse for those edges.
                if Vector.det(
                    Vector.diff(vertices[closest_line - 1],
                                vertices[closest_line]),
                    Vector.diff(vertices[closest_line],
                                vertices[(closest_line + 1) % len(vertices)])
                ) > 0 and Vector.det(
                    Vector.diff(self._player.position, vertices[closest_line]),
                    Vector.diff(vertices[closest_line],
                                vertices[(closest_line + 1) % len(vertices)])
                ) < self._player.radius ** 2:
                    collisions.append(self.circle_edge_impulse(
                        self._player, polygon, closest_line - 1,
                        is_jumping, is_bouncing))
                    if not hit_edge:
                        collisions.append(self.circle_edge_impulse(
                        self._player, polygon, closest_line,
                        is_jumping, is_bouncing))

                # If the player is colliding with the closest edge
                # but not either of the edges next to it,
                # add the impulse for the closest edge.
                elif not hit_edge:
                    collisions.append(self.circle_edge_impulse(
                        self._player, polygon, closest_line,
                        is_jumping, is_bouncing))

        # Average all the impulse vectors together
        # and apply the result to the player.
        print(f"collisions: {collisions}")
        impulse = Vector.sum_all(collisions).scale(self._player.mass
                / len(collisions)) if collisions else Vector(0, 0)
        relative_velocity = Vector.det(self._player.velocity, impulse) + (
            self._player.angular_velocity * self._player.radius) ** 2
        friction = impulse.scale(copysign(self._friction_coefficient,
                                          relative_velocity))
        friction = Vector(-friction.y, friction.x)
        self._player.impulse(impulse)
        self._player.impulse_at(friction,
                                impulse.normal().scale(-self._player.radius))

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

        return self.calculate_impulse(
            circle, polygon, normal, is_jumping, is_bouncing)

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

        return self.calculate_impulse(
            circle, polygon, normal, is_jumping, is_bouncing)

    def calculate_impulse(self, circle, polygon, normal,
                          is_jumping, is_bouncing):
        """
        Find the impulse vector for a collision between a circle and a polygon.
        Args:
            circle: A Circle representing the circle in the collision.
            polygon: A Polygon representing the polygon in the collision.
            normal: A Vector representing the normal vector for the collision.
            is_jumping: A boolean representing whether or not the player is
            jumping in the collision.
            is_bouncing: A boolean representing whether or not the player is
            bouncing in the collision.
            
        Returns:
            A Vector representing the impulse vector for the collision.
        """
        # Find the relative velocity of the circle and the edge.
        relative_velocity = Vector.diff(
            polygon.velocity, circle.velocity)

        # Find the impulse vector using the formula
        # impulse = (1 + e) * (relative_velocity dot normal) * normal + jump_up
        # where e is the coefficient of restitution
        # and jump_up is applied as an upward force when jumping.
        e = self._default_cor
        if circle.is_bouncy or polygon.is_bouncy:
            e = self._bouncy_cor
        if not is_bouncing:
            e = 0

        # Apply collision impulse along the normal
        collision_impulse = normal.scale(
            (-1 - e) * min(Vector.dot(normal, relative_velocity), 0))
        
        # Apply jump impulse upward (negative Y direction)
        jump_impulse = Vector(0, -self._jump_strength) if is_jumping else Vector(0, 0)
        
        return Vector(collision_impulse.x + jump_impulse.x, 
                     collision_impulse.y + jump_impulse.y)

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
