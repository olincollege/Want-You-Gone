"""
Contains the Level class.
"""

from math import sqrt, copysign
import json
from portal import PortalExit, PortalEntrance
from shape import Polygon, DynamicCircle#, DynamicPolygon
from vector import Vector


class Level:
    """
    Store the physical state of a set of 2D shapes.

    Attributes:
        _GRAVITY: A Vector representing the gravity on the level.
        _JUMP_STRENGTH: A float representing the strength of the jump.
        _DEFAULT_COR: A float representing the
        default coefficient of restitution.
        _BOUNCY_COR: A float representing the coefficient
        of restitution for bouncy objects.
        _FRICTION_COEFFICIENT: A float representing the friction coefficient.
        self._path: A string representing the path to the folder
        with all the starting data for the level.
        self._portals: A list of dictionaries representing
        the attributes of all portals.
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

    def __init__(self, shapes_path, portals, constants):
        """
        Initialize all attributes from the files in a folder. 

        Args:
            shapes_path: A string representing the path of the folder
            containing the attributes of all shapes on the level.
            portals: A list of dictionaries representing
            the attributes of all portals.
            constants: A dictionary representing all the constants.
        """
        # Set all constants and the path for the level.
        self._GRAVITY = self.make_vector(constants["gravity"])
        self._JUMP_STRENGTH = constants["jump_strength"]
        self._DEFAULT_COR = constants["default_cor"]
        self._BOUNCY_COR = constants["bouncy_cor"]
        self._FRICTION_COEFFICIENT = constants["friction_coefficient"]
        self._path = shapes_path
        self._portals = portals

        # Initialize all shapes on the level.
        self.restart()

    def restart(self):
        """
        Set all player,shape and portal attributes to their default values.
        """
        # Read the file for player.
        with open(self._path + "player.json", "r", encoding="utf-8") as file:
            player_attributes = json.load(file)

        # Initialize player.
        self._player = DynamicCircle(
            player_attributes["radius"],
            self.make_vector(player_attributes["position"]),
            self.make_vector(player_attributes["velocity"]),
            player_attributes["angle"],
            player_attributes["angular_velocity"],
            player_attributes["is_bouncy"],
            tuple(player_attributes["color"]),
        )

        self.reset()

    def reset(self):
        """
        Set all shape and portal attributes to their default values.
        """
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
                polygon_attributes["is_bouncy"],
                tuple(polygon_attributes["color"]),
            )
            for polygon_attributes in polygons_attributes
        ]

        # ----------------------------------------------------------------------

        # Initialize portals.
        self._portal_entrances = []
        self._portal_exits = []

        for portal in self._portals:
            if portal["from_path"] == self._path:
                position = self.make_vector(portal["from_position"])
                radius = portal["radius"]
                to_position = self.make_vector(portal["to_position"])
                to_path = portal["to_path"]
                max_force = portal["max_force"]
                self._portal_entrances.append(
                    PortalEntrance(
                        position, radius, to_position, to_path, max_force))

            if portal["to_path"] == self._path:
                position = self.make_vector(portal["to_position"])
                radius = portal["radius"]
                self._portal_exits.append(PortalExit(position, radius))

    def update_portals(self, dt):
        """
        Check if the player is in any portal entrance and if so, move the player
        to the corresponding portal exit.

        Returns:
            A Vector representing the change in the player's position.
            None if the player is not in any portal entrance.
        """
        # Apply portal forces to the player
        # if they are touching a portal entrance.
        for entrance in self._portal_entrances:
            force = entrance.force(self._player.position, self._player.radius)
            if force is not None:
                self._player.accelerate(force, dt)

        # If the player is in the portal entrance, move them to
        # the corresponding portal exit and return the change in their position.
        for entrance in self._portal_entrances:
            if entrance.is_in(self._player.position, self._player.radius):
                # Record the player's position relative to the portal entrance,
                # and their velocity, angle, and angular velocity.
                relative_position = Vector.diff(
                    entrance.position, self._player.position)

                # Change which level the player is on.
                self._path = entrance.to_path
                self.reset()

                # Move the player to the corresponding position
                # relative to the portal exit.
                self._player.set_position(Vector.sum(
                    entrance.to_position, relative_position))

                # Return the change in the player's position.
                return Vector.diff(entrance.to_position, entrance.position)

        # If the player is not in any portal entrance, return None.
        return None

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

    def update(self, dt):
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
        self._player.accelerate(self._GRAVITY, dt)

        # Update the positions and angles of all shapes by adding
        # their velocity and angular velocity to them.
        self._player.update_position(dt)

    def apply_collisions(self, is_jumping, is_bouncing, dt):
        """
        Calculate and apply the impulses for all collisions between the player
        and the polygons on the level.

        Args:
            is_jumping: A boolean representing whether or not the player is
            jumping in this update.
            is_bouncing: A boolean representing whether or not the player is
            bouncing in this update.
            dt: A float representing the amount of time
            to apply the impulses for.
        """
        for polygon in self._polygons + [self._border]:
            self.circle_polygon_collision(
                self._player, polygon, dt, is_jumping, is_bouncing)

    def circle_polygon_collision(
        self, circle, polygon, dt, is_jumping=False, is_bouncing=False
    ):
        """
        Detect and apply a collision between a circle and a polygon.

        Args:
            circle: A Circle representing the circle in the collision.
            polygon: A Polygon representing the polygon in the collision.
            is_jumping: A boolean representing whether or not the player is
            jumping in the collision.
            is_bouncing: A boolean representing whether or not the player is
            bouncing in the collision.
            dt: A float representing the timestep.
        """

        # Find the shortest distance between the circle's center and
        # the closest point to it on the polygon.

        # If the circle is too far from the polygon, skip it.
        if (polygon.radius + circle.radius) ** 2 < Vector.diff(
            polygon.position, circle.position
        ).magnitude_squared():
            return

        # Otherwise find the closest point on the polygon
        # to the circle and the distance between them.
        shortest_distance = None
        closest_edge = None
        closest_vertex = None
        vertices = polygon.world_vertices
        for i, vertex in enumerate(vertices):
            # Find the distance between the circle and the edge
            # between vertices i - 1 and i and update
            # shortest_distance if it is shorter.
            distance = circle.position.edge_point_distance(
                vertices[i - 1], vertex
            )
            if distance is not None and (
                shortest_distance is None
                or abs(distance) < abs(shortest_distance)
            ):
                shortest_distance = distance
                closest_edge = i
                closest_vertex = None

            # Find the distance between the circle and the vertex
            # and update shortest_distance if it is shorter.
            distance = sqrt(
                Vector.diff(
                    circle.position, vertex
                ).magnitude_squared()
            )
            if shortest_distance is None or abs(distance) < abs(
                shortest_distance
            ):
                shortest_distance = distance
                closest_vertex = i
                closest_edge = None

        # Determine the type of collision the circle
        # is having with each polygon.

        # If the circle is not colliding with the polygon, skip it.
        # Otherwise, resolve any collisions.
        if (
            shortest_distance is None
            or (shortest_distance > circle.radius and not is_jumping)
            or (shortest_distance > circle.radius + 1 and is_jumping)
        ):
            return

        # If the circle is colliding with a vertex:
        if closest_vertex is not None:
            # Determine whether the circle's center is inside the polygon
            # by checking if the angle from the closest vertex
            # to the circle's center is convex or reflex.
            is_inside = (
                Vector.det(
                    Vector.diff(
                        vertices[closest_vertex - 1],
                        vertices[closest_vertex],
                    ),
                    Vector.diff(
                        vertices[closest_vertex],
                        vertices[(closest_vertex + 1) % len(vertices)],
                    ),
                ) > 0)

            # If the circle is outside of the polygon
            # it is colliding with the vertex.
            # Otherwise, it is colliding with the edges connected to the vertex.
            if not is_inside:
                self.circle_corner_impulse(
                    circle,
                    polygon,
                    closest_vertex,
                    is_jumping,
                    is_bouncing,
                    dt
                )
            else:
                self.circle_edge_impulse(
                    circle,
                    polygon,
                    closest_vertex,
                    is_jumping,
                    is_bouncing,
                    dt
                )
                self.circle_edge_impulse(
                    circle,
                    polygon,
                    (closest_vertex + 1) % len(vertices),
                    is_jumping,
                    is_bouncing,
                    dt
                )

        hit_edge = False
        # If the circle is colliding with an edge:
        if closest_edge is not None:
            # If the circle is colliding with the closest edge,
            # and the one next to it in the clockwise direction,
            # add the impulse for those edges.
            if (
                Vector.det(
                    Vector.diff(
                        vertices[closest_edge - 2],
                        vertices[closest_edge - 1],
                    ),
                    Vector.diff(
                        vertices[closest_edge - 1], vertices[closest_edge]
                    ),
                )
                > 0
                and Vector.det(
                    Vector.diff(
                        circle.position, vertices[closest_edge - 1]
                    ),
                    Vector.diff(
                        vertices[closest_edge - 2],
                        vertices[closest_edge - 1],
                    ),
                )
                < circle.radius**2
            ):
                self.circle_edge_impulse(
                    circle,
                    polygon,
                    closest_edge - 1,
                    is_jumping,
                    is_bouncing,
                    dt
                )
                self.circle_edge_impulse(
                    circle,
                    polygon,
                    closest_edge,
                    is_jumping,
                    is_bouncing,
                    dt
                )
                hit_edge = True

            # If the circle is colliding with the closest edge,
            # and the one next to it in the counterclockwise direction,
            # add the impulse for those edges.
            if (
                Vector.det(
                    Vector.diff(
                        vertices[closest_edge - 1], vertices[closest_edge]
                    ),
                    Vector.diff(
                        vertices[closest_edge],
                        vertices[(closest_edge + 1) % len(vertices)],
                    ),
                )
                > 0
                and Vector.det(
                    Vector.diff(
                        circle.position, vertices[closest_edge]
                    ),
                    Vector.diff(
                        vertices[closest_edge],
                        vertices[(closest_edge + 1) % len(vertices)],
                    ),
                )
                < circle.radius**2
            ):
                self.circle_edge_impulse(
                    circle,
                    polygon,
                    closest_edge - 1,
                    is_jumping,
                    is_bouncing,
                    dt
                )
                if not hit_edge:
                    self.circle_edge_impulse(
                        circle,
                        polygon,
                        closest_edge,
                        is_jumping,
                        is_bouncing,
                        dt
                    )

            # If the circle is colliding with the closest edge
            # but not either of the edges next to it,
            # add the impulse for the closest edge.
            elif not hit_edge:
                self.circle_edge_impulse(
                    circle,
                    polygon,
                    closest_edge,
                    is_jumping,
                    is_bouncing,
                    dt
                )

    def apply_collision(
        self,
        shape1,
        shape2,
        normal,
        collision_point,
        is_jumping,
        is_bouncing,
        dt
    ):
        """
        Apply a collision impulse and friction to two shapes.

        Args:
            shape1: A Shape representing the first shape in the collision.
            shape2: A Shape representing the second shape in the collision.
            normal: A Vector representing the normal vector for the collision,
            in the direction from shape2 to shape1.
            collision_point: A Vector representing
            the contact point of collision in world space.
            dt: A float representing the length of the timestep.
        """
        # Find the relative velocity of shape1 with respect to shape2.
        relative_velocity = Vector.diff(
            shape2.velocity_at(collision_point),
            shape1.velocity_at(collision_point)
        )

        # Find the impulse vector using the formula
        # impulse = (1 + e) * (relative_velocity dot normal) * normal + jump_up
        # where e is the coefficient of restitution
        # and jump_up is applied as an upward force when jumping.
        e = self._DEFAULT_COR
        if shape1.is_bouncy or shape2.is_bouncy:
            e = self._BOUNCY_COR
        if not is_bouncing:
            e = 0

        # Apply collision impulse along the normal
        collision_scalar = max(
            (1 + e) * (5 - Vector.dot(normal, relative_velocity)), 0
        )
        if collision_scalar != 0:
            collision_scalar += self._JUMP_STRENGTH if is_jumping else 0

        impulse = normal.scale(collision_scalar)

        shape1.nudge(impulse.scale(dt))
        shape2.nudge(impulse.scale(-dt))
        effective_mass_normal = 1 / (
            shape1.inv_effective_mass(collision_point, normal) +
            shape2.inv_effective_mass(collision_point, normal)
        )
        impulse = impulse.scale(effective_mass_normal)

        # Calculate the friction for the collision.
        tangent = Vector(normal.y, -normal.x)
        effective_mass_tangent = 1 / (
            shape1.inv_effective_mass(collision_point, tangent) +
            shape2.inv_effective_mass(collision_point, tangent)
        )
        friction_magnitude = abs(
            Vector.dot(relative_velocity, tangent) * effective_mass_tangent
        )
        friction_magnitude = max(friction_magnitude, 0)
        max_friction = self._FRICTION_COEFFICIENT * sqrt(
            impulse.magnitude_squared()
        )
        friction_magnitude = min(friction_magnitude, max_friction)
        friction_impulse = tangent.scale(
            -copysign(
                friction_magnitude,
                Vector.dot(relative_velocity, tangent),
            )
        )

        # Apply the impulse and friction to the circle and polygon.
        shape1.impulse_at(impulse, collision_point)
        shape2.impulse_at(impulse.scale(-1), collision_point)
        shape1.impulse_at(friction_impulse, collision_point)
        shape2.impulse_at(friction_impulse.scale(-1), collision_point)

    def circle_corner_impulse(
        self, circle, polygon, vertex, is_jumping, is_bouncing, dt
    ):
        """
        Apply the impulse for a collision between a circle and a corner.

        Args:
            circle: A Circle representing the circle in the collision.
            polygon: A Polygon representing the polygon in the collision.
            vertex: A integer representing the index of the corner in the
            collision.
            is_jumping: A boolean representing whether or not the player is
            jumping in the collision.
            is_bouncing: A boolean representing whether or not the player is
            bouncing in the collision.
            dt: A float representing the length of the timestep.
        """
        # Find the normal vector for the collision.
        normal = Vector.diff(polygon.world_vertices[vertex], circle.position)
        normal = normal.normal()

        # Calculate and apply the impulse
        self.apply_collision(
            circle,
            polygon,
            normal,
            polygon.world_vertices[vertex],
            is_jumping,
            is_bouncing,
            dt
        )

    def circle_edge_impulse(
        self, circle, polygon, edge, is_jumping, is_bouncing, dt
    ):
        """
        Apply the impulse for a collision between a circle and an edge.

        Args:
            circle: A Circle representing the circle in the collision.
            polygon: A Polygon representing the polygon in the collision.
            edge: A integer representing the index of the edge in the
            collision. The edge is between vertices edge - 1 and edge.
            is_jumping: A boolean representing whether or not the player is
            jumping in the collision.
            is_bouncing: A boolean representing whether or not the player is
            bouncing in the collision.
            dt: A float representing the length of the timestep.
        """
        # Find the normal vector for the collision.
        tangent = Vector.diff(
            polygon.world_vertices[edge], polygon.world_vertices[edge - 1]
        ).normal()
        normal = Vector(tangent.y, -tangent.x)
        contact_point = Vector.sum(
            normal.scale(-circle.radius), circle.position
        )

        # Calculate and apply the impulse
        self.apply_collision(
            circle,
            polygon,
            normal,
            contact_point,
            is_jumping,
            is_bouncing,
            dt
        )

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

    @property
    def portal_entrances(self):
        """Get portal entrances"""
        return self._portal_entrances

    @property
    def portal_exits(self):
        """Get portal exits"""
        return self._portal_exits
