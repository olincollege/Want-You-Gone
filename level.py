"""
Contains the Level and LELevel classes.
"""

from math import ceil, floor, sqrt, copysign
import json
from collections import namedtuple

from portal import PortalEntrance
from shape import Circle, DynamicShape, Polygon, DynamicCircle, DynamicPolygon
from text_display import TextDisplay
from world_text import WorldText
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
        self._dynamic_circles: A list of DynamicCircles representing the
        dynamic circles on the level.
        self._dynamic_polygons: A list of DynamicPolygons representing the
        dynamic polygons on the level.
        self._portal_depth: A float representing how deep
        the player is in the closest portal to them
        self._current_portal: A portal representing the closest portal
        to the player, None if they aren't inside a portal.
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
        self._DEFAULT_FRICTION = constants["default_friction"]
        self._SLIPPERY_FRICTION = constants["slippery_friction"]
        self._path = shapes_path
        self._portals = portals
        self._caption = TextDisplay(constants)
        self._ENTRANCE_COLOR = tuple(constants["entrance_color"])
        self._EXIT_COLOR = tuple(constants["exit_color"])
        self._MAX_PORTAL_FORCE = constants["max_portal_force"]

        # Initialize all shapes and portals on the level.
        self._signs = None
        self._border = None
        self._circles = None
        self._polygons = None
        self._dynamic_circles = None
        self._dynamic_polygons = None
        self._portal_entrances = None
        self.restart()

        # Initialize an empty list of debug points to draw on the level.
        self._debug_points = []

        # Initialize portal travel related variables.
        self._portal_depth = 0
        self._current_portal = None

    def restart(self):
        """
        Set all player, shape and portal attributes to their default values
        and pause the glow of all portals.
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
            player_attributes["is_slippery"],
            tuple(player_attributes["color"]),
            "player"
        )

        # Set all shape and portal attributes to their default values.
        self.reset()

        # Temporarily disable all portal glow.
        for portal in self._portal_entrances:
            portal.pause_glow()

    def reset(self):
        """
        Set all shape and portal attributes to their default values.
        """
        # Read the file for the caption.
        with open(self._path + "caption.json", "r", encoding="utf-8") as file:
            caption_attributes = json.load(file)

        fixed = caption_attributes.get("fixed_to_screen", True)

        # Display the caption for the level.
        self._caption.show(caption_attributes["title"],
                           caption_attributes["subtitle"],
                           fixed)

        # ---------------------------------------------------------------------

        with open(self._path + "signs.json", "r", encoding="utf-8") as file:
            signs_attributes = json.load(file)

        self._signs = [
            WorldText(
                sign["text"],
                self.make_vector(sign["position"]),
                sign["size"],
                sign["color"],
            )
            for sign in signs_attributes
        ]

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
            True,
            border_attributes["is_bouncy"],
            border_attributes["is_slippery"],
            tuple(border_attributes["color"]),
            "border"
        )

        # ----------------------------------------------------------------------

        # Read the file for circles.
        with open(self._path + "circles.json", "r",
                  encoding="utf-8") as file:
            circles_attributes = json.load(file)

        # Initialize circles.
        self._circles = [
            Circle(
                circle_attributes["radius"],
                self.make_vector(circle_attributes["position"]),
                self.make_vector(circle_attributes["velocity"]),
                circle_attributes["angle"],
                circle_attributes["angular_velocity"],
                circle_attributes["is_bouncy"],
                circle_attributes["is_slippery"],
                tuple(circle_attributes["color"]),
                circle_attributes["comment"]
            )
            for circle_attributes in circles_attributes
        ]

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
                polygon_attributes["is_slippery"],
                tuple(polygon_attributes["color"]),
                polygon_attributes["comment"]
            )
            for polygon_attributes in polygons_attributes
        ]

        # ----------------------------------------------------------------------

        # Read the file for dynamic circles.
        with open(self._path + "dynamic_circles.json", "r",
                  encoding="utf-8") as file:
            dynamic_circles_attributes = json.load(file)

        # Initialize dynamic circles.
        self._dynamic_circles = [
            DynamicCircle(
                circle_attributes["radius"],
                self.make_vector(circle_attributes["position"]),
                self.make_vector(circle_attributes["velocity"]),
                circle_attributes["angle"],
                circle_attributes["angular_velocity"],
                circle_attributes["is_bouncy"],
                circle_attributes["is_slippery"],
                tuple(circle_attributes["color"]),
                circle_attributes["comment"]
            )
            for circle_attributes in dynamic_circles_attributes
        ]

        # ----------------------------------------------------------------------

        # Read the file for dynamic polygons.
        with open(self._path + "dynamic_polygons.json", "r",
                  encoding="utf-8") as file:
            dynamic_polygons_attributes = json.load(file)

        # Initialize dynamic polygons.
        self._dynamic_polygons = [
            DynamicPolygon(
                self.make_vector(polygon_attributes["vertices"]),
                self.make_vector(polygon_attributes["position"]),
                self.make_vector(polygon_attributes["velocity"]),
                polygon_attributes["angle"],
                polygon_attributes["angular_velocity"],
                False,
                polygon_attributes["is_bouncy"],
                polygon_attributes["is_slippery"],
                tuple(polygon_attributes["color"]),
                polygon_attributes["comment"]
            )
            for polygon_attributes in dynamic_polygons_attributes
        ]

        # ----------------------------------------------------------------------

        # Initialize portals.
        self._portal_entrances = []

        for portal in self._portals:
            if portal["from_path"] == self._path:
                position = self.make_vector(portal["from_position"])
                radius = portal["radius"]
                to_position = self.make_vector(portal["to_position"])
                to_path = portal["to_path"]
                self._portal_entrances.append(
                    PortalEntrance(
                        position,
                        radius,
                        to_position,
                        to_path,
                        self._MAX_PORTAL_FORCE,
                        self._ENTRANCE_COLOR
                    )
                )

            if portal["to_path"] == self._path:
                position = self.make_vector(portal["to_position"])
                radius = portal["radius"]
                from_position = self.make_vector(portal["from_position"])
                from_path = portal["from_path"]
                self._portal_entrances.append(
                    PortalEntrance(
                        position,
                        radius,
                        from_position,
                        from_path,
                        self._MAX_PORTAL_FORCE,
                        self._EXIT_COLOR
                    )
                )

    def update_portals(self, dt):
        """
        Update the portal travel attributes,
        check if the player is in any portal entrance and if so, move the player
        to the corresponding portal exit.

        Returns:
            A Vector representing by how much the player was teleported.
            None if the the player wasn't teleported.
        """
        depth = 0
        the_portal = None
        for portal in self._portal_entrances:
            # If the portal is too far from the player, skip it,
            # activate it and enable its glow.
            if (portal.radius + self._player.radius) ** 2 < Vector.diff(
                portal.position, self._player.position
            ).magnitude_squared():
                portal.activate()
                portal.unpause_glow()
                continue

            # Apply portal forces to the player
            # if they are touching a portal
            # and calculate the depth of the player in the portal.
            force = portal.force(
                self._player.position, self._player.radius)
            calc_depth = portal.depth(
                self._player.position, self._player.radius)
            if force is not None:
                self._player.accelerate(force, dt)
                self._player.slow(calc_depth * 5, dt)
            if calc_depth > depth:
                depth = calc_depth # recorded depth = calculated depth
                the_portal = portal

            # If the player is in the portal, move them to
            # the corresponding portal exit
            # and return the change in their position.
            if portal.is_in(self._player.position, self._player.radius):
                # Record the player's position relative to the portal,
                # and their velocity, angle, and angular velocity.
                relative_position = Vector.diff(
                    portal.position, self._player.position)

                # Change which level the player is on.
                self.set_path(portal.to_path)
                self.reset()

                # Move the player to the corresponding position
                # relative to the portal exit.
                self._player.set_position(Vector.sum(
                    portal.to_position, relative_position))

                # Set the portal travel attributes.
                self._portal_depth = depth
                self._current_portal = portal.to_portal

                # Return the player's displacement due to the portal travel.
                return Vector.diff(portal.to_position, portal.position)

        # Set the portal travel attributes
        # even if the player is not fully in the closest portal.
        self._portal_depth = depth
        self._current_portal = the_portal

        # The player didn't teleport so return None.
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
        # Empty the list of debug points to draw on the level.
        #self._debug_points = []

        # Update text
        self._caption.update(dt)

        # Update the velocity of all shapes by adding gravity to them.
        self._player.accelerate(self._GRAVITY, dt)
        for circle in self._dynamic_circles:
            circle.accelerate(self._GRAVITY, dt)
        for polygon in self._dynamic_polygons:
            polygon.accelerate(self._GRAVITY, dt)

        # Update the positions and angles of all shapes by adding
        # their velocity and angular velocity to them.
        self._player.update_position(dt)
        for circle in self._dynamic_circles:
            circle.update_position(dt)
        for polygon in self._dynamic_polygons:
            polygon.update_position(dt)

    def apply_collisions(self, is_jumping, is_bouncing):
        """
        Calculate and apply the impulses for all
        collisions between all shapes on the level.

        Args:
            is_jumping: A boolean representing whether or not the player is
            jumping in this update.
            is_bouncing: A boolean representing whether or not the player is
            bouncing in this update.
        """
        # Dynamic circles on player and stationary circles & polygons.
        for circle in self._dynamic_circles:
            self.circle_circle_collision(
                self._player, circle, is_jumping, is_bouncing)
            for polygon in self._polygons + [self._border]:
                self.circle_polygon_collision(circle, polygon)
            for other_circle in self._circles:
                self.circle_circle_collision(circle, other_circle)

        # Dynamic polygons on stationary circles & polygons.
        for polygon in self._dynamic_polygons:
            for other_polygon in self._polygons + [self._border]:
                self.polygon_polygon_collision(polygon, other_polygon)
            for circle in self._circles:
                self.circle_polygon_collision(circle, polygon)

        # Dynamic polygons on player and dynamic circles.
        for polygon in self._dynamic_polygons:
            self.circle_polygon_collision(
                self._player, polygon, is_jumping, is_bouncing)
            for circle in self._dynamic_circles:
                self.circle_polygon_collision(circle, polygon)

        # Player on stationary circles & polygons.
        for polygon in self._polygons + [self._border]:
            self.circle_polygon_collision(
                self._player, polygon, is_jumping, is_bouncing)
        for circle in self._circles:
            self.circle_circle_collision(
                self._player, circle, is_jumping, is_bouncing)

        # Dynamic circles on each other.
        for i, circle in enumerate(self._dynamic_circles):
            for other_circle in self._dynamic_circles[i:]:
                self.circle_circle_collision(circle, other_circle)

        # Dynamic polygons on each other.
        for i, polygon in enumerate(self._dynamic_polygons):
            for other_polygon in self._dynamic_polygons[i:]:
                self.polygon_polygon_collision(polygon, other_polygon)

    def circle_polygon_collision(
        self, circle, polygon, is_jumping=False, is_bouncing=False
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
        """

        # Find the shortest distance between the circle's center and
        # the closest point to it on the polygon.

        # If the circle is too far from the polygon, skip it.
        if (polygon.radius + circle.radius) ** 2 < Vector.diff(
            polygon.position, circle.position
        ).magnitude_squared():
            return

        # Otherwise, find the closest point on the polygon
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
                    is_bouncing
                )
            else:
                self.circle_edge_impulse(
                    circle,
                    polygon,
                    closest_vertex,
                    shortest_distance,
                    is_jumping,
                    is_bouncing
                )
                self.circle_edge_impulse(
                    circle,
                    polygon,
                    (closest_vertex + 1) % len(vertices),
                    shortest_distance,
                    is_jumping,
                    is_bouncing
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
                    shortest_distance,
                    is_jumping,
                    is_bouncing
                )
                self.circle_edge_impulse(
                    circle,
                    polygon,
                    closest_edge,
                    shortest_distance,
                    is_jumping,
                    is_bouncing
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
                    shortest_distance,
                    is_jumping,
                    is_bouncing
                )
                if not hit_edge:
                    self.circle_edge_impulse(
                        circle,
                        polygon,
                        closest_edge,
                    shortest_distance,
                        is_jumping,
                        is_bouncing
                    )
                    hit_edge = True

            # If the circle is colliding with the closest edge
            # but not either of the edges next to it,
            # add the impulse for the closest edge.
            elif not hit_edge:
                self.circle_edge_impulse(
                    circle,
                    polygon,
                    closest_edge,
                    shortest_distance,
                    is_jumping,
                    is_bouncing
                )

    def circle_circle_collision(
        self, circle1, circle2, is_jumping=False, is_bouncing=False
    ):
        """
        Detect and apply a collision between two circles.

        Args:
            circle1: A Circle representing the first circle in the collision.
            circle2: A Circle representing the second circle in the collision.
            is_jumping: A boolean representing whether or not the player is
            jumping in the collision.
            is_bouncing: A boolean representing whether or not the player is
            bouncing in the collision.
        """
        # If the circles are not colliding, skip them.
        if (Vector.diff(circle1.position, circle2.position).magnitude_squared()
            > (circle1.radius + circle2.radius) ** 2):
            return

        # Otherwise, resolve the collision.
        difference = Vector.diff(circle2.position, circle1.position)
        normal = difference.normal()
        contact_point = Vector.sum(
            normal.scale(-circle1.radius), circle1.position
        )

        # Calculate displacement.
        displacement = Vector.diff(
            difference, normal.scale(circle1.radius + circle2.radius))

        # Apply the collision impulse and friction to the circles.
        self.apply_collision(
            circle1,
            circle2,
            normal,
            contact_point,
            is_jumping,
            is_bouncing,
            displacement
        )

    def polygon_polygon_collision(self, polygon1, polygon2):
        """
        Detect and apply all collisions between two polygons.

        Args:
            polygon1: A Polygon representing the first polygon in the collision.
            polygon1_prev: The previous position of polygon1.
            polygon2: A Polygon, the second polygon in the collision.
        """
        # position: A Vector, the location of the intersection in world space.
        # order1: A float, how far along
        # the boundary of polygon1 the intersection is
        # before the decimal point, which edge
        # and after, where on that edge.
        # order2: A float: same as order1 but for polygon2
        # direction: A float, its sign changes depending on if
        # the edge on one polygon is entering or exiting the other.
        Intersection = namedtuple("Intersection", [
            "position", "order1", "order2", "direction"])

        def calculate_intersection(polygon1, polygon2, edge1, edge2):
            """
            Calculate information about the intersection between two edges
            if those edges intersect.

            Args:
                polygon1: A Polygon, the first polygon in the collision.
                polygon2: A Polygon, the second polygon in the collision.
                edge1: A Vector representing one of the edges of polygon1
                from vertices(edge1 - 1) to vertices(edge1).
                edge2: A Vector representing one of the edges of polygon2.
            
            Returns:
                An Intersection namedtuple with the position, order1, order2,
                and direction of the intersection if the edges intersect.
                None if the edges do not intersect.
            """
            # Find the world space positions of each edge's vertices.
            p1 = polygon1.world_vertices[edge1 - 1]
            p2 = polygon1.world_vertices[edge1]
            q1 = polygon2.world_vertices[edge2 - 1]
            q2 = polygon2.world_vertices[edge2]

            # Check if the edges cross.
            p_diff = Vector.diff(p1, p2)
            q_diff = Vector.diff(q1, q2)
            p_det_1 = Vector.det(p_diff, Vector.diff(p1, q1))
            p_det_2 = Vector.det(p_diff, Vector.diff(p1, q2))
            q_det_1 = Vector.det(q_diff, Vector.diff(q1, p1))
            q_det_2 = Vector.det(q_diff, Vector.diff(q1, p2))

            # The line segments cross if
            # p1 and p2 are on opposite sides of the line through q1 and q2
            # and q1 and q2 are on opposite sides of the line through p1 and p2.
            cross = ((p_det_1 <= 0) ^ (p_det_2 < 0)
                ) and ((q_det_1 <= 0) ^ (q_det_2 < 0))

            # If the edges do not cross, return None.
            if not cross:
                return None

            # Otherwise, calculate the:
            # intersection point,
            t_numerator = Vector.det(Vector.diff(q1, q2), Vector.diff(q1, p1))
            t_denominator = Vector.det(Vector.diff(p1, p2), Vector.diff(q1, q2))
            t = t_numerator / t_denominator if t_denominator != 0 else 0
            intersection_point = Vector.sum(p1, Vector.diff(p1, p2).scale(t))

            # Order values,
            order1 = (
                (edge1 + Vector.diff(p1, intersection_point).magnitude_squared()
                / Vector.diff(p1, p2).magnitude_squared() - 1
                ) % len(polygon1.local_vertices)
            )
            order2 = (
                (edge2 + Vector.diff(q1, intersection_point).magnitude_squared()
                / Vector.diff(q1, q2).magnitude_squared() - 1
                ) % len(polygon2.local_vertices)
            )

            # and direction of the intersection.
            direction = Vector.det(p_diff, q_diff)
            if direction == 0:
                return None

            return Intersection(intersection_point, order1, order2, direction)


        # If the polygons are not colliding, skip them.
        if (Vector.diff(polygon1.position, polygon2.position
            ).magnitude_squared() > (polygon1.radius + polygon2.radius) ** 2):
            return

        # Loop through each combination of edges collecting every intersection.
        intersections = []
        vertices1 = polygon1.world_vertices
        vertices2 = polygon2.world_vertices
        for edge1 in range(len(vertices1)):
            for edge2 in range(len(vertices2)):
                # Try to add an intersection to the list of intersections
                # based on the two edges.
                # If the edges do not intersect, nothing is added.
                intersection = calculate_intersection(
                    polygon1, polygon2, edge1, edge2
                )
                if intersection is not None:
                    intersections.append(intersection)

        # If there are somehow an odd number of intersections,
        # skip the collision.
        if len(intersections) % 2 != 0:
            return

        # Sort the intersections by their order values for each polygon.
        sorted1 = sorted(intersections, key=lambda i: i.order1)
        sorted2 = sorted(intersections, key=lambda i: i.order2)

        # Loop through each sorted list and find adjacent pairs of intersections
        # that start with an entering edge and end with an exiting edge.
        collisions1 = []
        collisions2 = []
        for i, intersection1 in enumerate(sorted1):
            if (intersection1.direction > 0 and
                sorted1[(i + 1) % len(sorted1)].direction < 0):
                collisions1.append((intersection1,
                                    sorted1[(i + 1) % len(sorted1)]))
        for i, intersection2 in enumerate(sorted2):
            if (intersection2.direction < 0 and
                sorted2[(i + 1) % len(sorted2)].direction > 0):
                collisions2.append((intersection2,
                                    sorted2[(i + 1) % len(sorted2)]))

        # Execute all collisions that appear in both lists of collisions
        # and remove them from the lists.
        for collision1 in collisions1[:]:
            for collision2 in collisions2[:]:
                if (collision1[0].position == collision2[1].position and
                    collision1[1].position == collision2[0].position):
                    # Calculate how deep the polygons are in each other.
                    depth1 = 0
                    depth2 = 0
                    n = len(vertices1)
                    start = ceil(collision1[0].order1)
                    end = floor(collision1[1].order1)
                    for i in range((end - start + 1) % n):
                        vertex = (start + i) % n
                        depth = polygon1.world_vertices[vertex
                            ].edge_point_distance(collision1[0].position,
                                collision1[1].position, False
                            )
                        if depth is not None and depth > depth1:
                            depth1 = depth
                    n = len(vertices2)
                    start = ceil(collision2[0].order2)
                    end = floor(collision2[1].order2)
                    for i in range((end - start + 1) % n):
                        vertex = (start + i) % n
                        depth = polygon2.world_vertices[vertex
                        ].edge_point_distance(collision2[0].position,
                            collision2[1].position, False
                        )
                        if depth is not None and depth > depth2:
                            depth2 = depth
                    total_depth = depth1 + depth2

                    # Apply the impulses for the collision
                    # at both intersection points.
                    self.dual_point_impulse(
                        polygon1,
                        polygon2,
                        collision1[0].position,
                        collision1[1].position,
                        total_depth
                    )
                    collisions1.remove(collision1)
                    collisions2.remove(collision2)

        # Of the remaining collisions, execute the one
        # with the shallowest penetration.
        shallowest_collision = None
        shallowest_depth = None
        for collision1 in collisions1:
            # Calculate the depth of polygon1's deepest vertex in polygon2.
            depth1 = None
            n = len(vertices1)
            start = ceil(collision1[0].order1)
            end = floor(collision1[1].order1)
            for i in range((end - start + 1) % n):
                vertex = (start + i) % n
                depth = polygon1.world_vertices[vertex
                    ].edge_point_distance(collision1[0].position,
                        collision1[1].position, False
                    )
                if depth1 is None or (depth is not None and depth > depth1):
                    depth1 = depth

            # If the depth is shallower than the previous shallowest depth
            # record the collision and depth.
            if shallowest_depth is None or (
                depth1 is not None and depth1 < shallowest_depth):
                shallowest_collision = collision1
                shallowest_depth = depth1

        for collision2 in collisions2:
            # Calculate the depth of polygon2's deepest vertex in polygon2.
            depth2 = None
            n = len(vertices2)
            start = ceil(collision2[0].order2)
            end = floor(collision2[1].order2)
            for i in range((end - start + 1) % n):
                vertex = (start + i) % n
                depth = polygon2.world_vertices[vertex
                    ].edge_point_distance(collision2[0].position,
                        collision2[1].position, False
                    )
                if depth2 is None or (depth is not None and depth > depth2):
                    depth2 = depth

            # If the depth is shallower than the previous shallowest depth
            # record the collision and depth.
            if shallowest_depth is None or (
                depth2 is not None and depth2 < shallowest_depth):
                shallowest_collision = collision2
                shallowest_depth = depth2

        if shallowest_depth is not None:
            # Apply the impulses for the collision
            # at both intersection points.
            self.dual_point_impulse(
                polygon1,
                polygon2,
                shallowest_collision[0].position,
                shallowest_collision[1].position,
                shallowest_depth
            )

    def apply_collision(
        self,
        shape1,
        shape2,
        normal,
        collision_point,
        is_jumping,
        is_bouncing,
        displacement
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

        inv_effective_mass1 = shape1.inv_effective_mass(collision_point, normal)
        inv_effective_mass2 = shape2.inv_effective_mass(collision_point, normal)
        total_inv_effective_mass = inv_effective_mass1 + inv_effective_mass2
        effective_mass_normal = (1 / total_inv_effective_mass
            ) if total_inv_effective_mass != 0 else 0
        impulse = impulse.scale(effective_mass_normal)

        # Nudge the shapes apart to prevent them
        # from phasing through each other.
        if issubclass(type(shape1), DynamicShape):
            if issubclass(type(shape2), DynamicShape):
                scale1 = 0.5
                scale2 = 0.5
            else:
                scale1 = 1
                scale2 = 0
        else:
            scale1 = 0
            scale2 = 1
        shape1.nudge(displacement.scale(scale1))
        shape2.nudge(displacement.scale(-scale2))

        # Calculate the friction for the collision.
        tangent = Vector(normal.y, -normal.x)
        effective_mass_tangent = 1 / (
            shape1.inv_effective_mass(collision_point, tangent) +
            shape2.inv_effective_mass(collision_point, tangent)
        )
        friction_magnitude = abs(
            Vector.dot(relative_velocity, tangent) * effective_mass_tangent
        )
        friction_coefficient = self._DEFAULT_FRICTION
        if shape1.is_slippery or shape2.is_slippery:
            friction_coefficient = self._SLIPPERY_FRICTION
        max_friction = friction_coefficient * sqrt(
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
        return

    def dual_point_impulse(
            self, polygon1, polygon2, point1, point2, depth):
        """
        Apply the impulses for a collision between two polygons at two points.

        Args:
            polygon1: A Polygon representing the first polygon in the collision.
            polygon2: A Polygon, the second polygon in the collision.
            point1: A Vector representing the position of one of the contact
            points of collision in world space.
            point2: A Vector representing the position of the other contact
            point of collision in world space.
            depth: A float representing the displacement to nudge the
            polygons apart to prevent them from phasing through each other.
        """
        # Find the normal vector for the collision.
        tangent = Vector.diff(point2, point1).normal()
        normal = Vector(-tangent.y, tangent.x)

        # Calculate displacement.
        displacement = normal.scale(depth * 0.5)

        # Calculate and apply the impulses
        self.apply_collision(
            polygon1,
            polygon2,
            normal,
            point1,
            False,
            False,
            displacement
        )

        self.apply_collision(
            polygon1,
            polygon2,
            normal,
            point2,
            False,
            False,
            displacement
        )

    def circle_corner_impulse(
        self, circle, polygon, vertex, is_jumping, is_bouncing
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
        """
        # Find the normal vector for the collision.
        difference = Vector.diff(
            polygon.world_vertices[vertex], circle.position)
        normal = difference.normal()

        # Calculate displacement.
        displacement = Vector.diff(difference, normal.scale(circle.radius))

        # Calculate and apply the impulse
        self.apply_collision(
            circle,
            polygon,
            normal,
            polygon.world_vertices[vertex],
            is_jumping,
            is_bouncing,
            displacement
        )

    def circle_edge_impulse(
        self, circle, polygon, edge, distance, is_jumping, is_bouncing
    ):
        """
        Apply the impulse for a collision between a circle and an edge.

        Args:
            circle: A Circle representing the circle in the collision.
            polygon: A Polygon representing the polygon in the collision.
            edge: A integer representing the index of the edge in the
            collision. The edge is between vertices edge - 1 and edge.
            distance: A float representing the distance between the circle's
            center and the closest point on the edge to the circle's center.
            is_jumping: A boolean representing whether or not the player is
            jumping in the collision.
            is_bouncing: A boolean representing whether or not the player is
            bouncing in the collision.
        """
        # Find the normal vector for the collision.
        tangent = Vector.diff(
            polygon.world_vertices[edge], polygon.world_vertices[edge - 1]
        ).normal()
        normal = Vector(tangent.y, -tangent.x)
        contact_point = Vector.sum(
            normal.scale(-circle.radius), circle.position
        )

        # Calculate displacement.
        displacement = normal.scale(-distance + circle.radius)

        # Calculate and apply the impulse
        self.apply_collision(
            circle,
            polygon,
            normal,
            contact_point,
            is_jumping,
            is_bouncing,
            displacement
        )

    def vertex_edge_impulse(
        self, polygon1, polygon2, vertex, edge, distance
    ):
        """
        Apply the impulse for a collision between a vertex and an edge.

        Args:
            polygon1: A Polygon representing the first polygon in the collision.
            polygon2: A Polygon, the second polygon in the collision.
            vertex: A Vector representing the position of the vertex in the
            collision on polygon1 in world space.
            edge: A integer representing the index of the edge in the
            collision on polygon2, between vertices edge - 1 and edge.
            distance: A float representing the distance between the vertex and
            the closest point on the edge to the vertex.
        """
        # Find the normal vector for the collision.
        tangent = Vector.diff(
            polygon2.world_vertices[edge - 1],
            polygon2.world_vertices[edge]
        ).normal()
        normal = Vector(-tangent.y, tangent.x)

        # Calculate displacement.
        displacement = normal.scale(-distance)

        # Calculate and apply the impulse
        self.apply_collision(
            polygon1,
            polygon2,
            normal,
            vertex,
            False,
            False,
            displacement
        )

    def move_shape(self, movement, dt):
        """
        ONLY FOR TESTING PURPOSES. NOT FOR ACTUAL GAMEPLAY.
        Move a certain shape on the level,
        which one it is will be rewritten depending on the testing being done.
        """
        self._dynamic_polygons[0].nudge(movement.scale(dt))

    def set_path(self, new_path):
        """
        Change self._path to be a different level directory.

        Args:
            new_path: A string representing
            the path of the new level directory.
        """
        self._path = new_path

    @property
    def player(self):
        """Get player"""
        return self._player

    @property
    def border(self):
        """Get border"""
        return self._border

    @property
    def circles(self):
        """Get circles"""
        return self._circles

    @property
    def polygons(self):
        """Get polygons"""
        return self._polygons

    @property
    def portal_entrances(self):
        """Get portal entrances"""
        return self._portal_entrances

    @property
    def dynamic_circles(self):
        """Get dynamic circles"""
        return self._dynamic_circles

    @property
    def dynamic_polygons(self):
        """Get dynamic polygons"""
        return self._dynamic_polygons

    @property
    def caption(self):
        """Get caption"""
        return self._caption

    @property
    def signs(self):
        """Get signs"""
        return self._signs

    @property
    def debug_points(self):
        """Get debug points"""
        return self._debug_points

    @property
    def portal_depth(self):
        """Get portal depth"""
        return self._portal_depth

    @property
    def current_portal(self):
        """Get current portal"""
        return self._current_portal

class LELevel(Level):
    """
    Same as Level but for use in a level editor.

    Attributes:
        _editing_polygon: A list of Vectors representing
        the polygon currently being edited, or None.
        _editing_circle: A length 2 list containing
        a Vector representing the position of the circle
        currently being edited and a float representing its radius,
        or None.
        _editing_shape_is_dynamic: A boolean representing
        whether the shape currently being edited is dynamic or not.
        _DYNAMIC_COLOR: A tuple of 3 integers
        representing the RGB color of dynamic shapes.
        _STATIONARY_COLOR: A tuple of 3 integers
        representing the RGB color of stationary shapes.
        All other attributes are inherited from Level.
    """
    # Set the colors for dynamic and stationary shapes.
    _DYNAMIC_COLOR = (200, 20, 20)
    _STATIONARY_COLOR = (111, 135, 209)

    def __init__(self, shapes_path, portals, constants):
        """
        Initialize a LELevel.

        Args:
            constants: A Constants object containing the game's constants.
        """
        super().__init__(shapes_path, portals, constants)
        self._editing_polygon = None
        self._editing_circle = None
        self._editing_shape_is_dynamic = True

    def set_path(self, new_path):
        """
        Same as in Level but finish editing first.
        """
        self.finish_editing()
        super().set_path(new_path)

    def toggle_dynamic(self):
        """
        Toggle whether the shape currently being edited is dynamic or not.
        """
        self._editing_shape_is_dynamic = not self._editing_shape_is_dynamic

    def reformat_json(self, path):
        """
        Reformat a .json file, making all arrays except the one containing
        every object fit in their own lines.

        Args:
            path: The path to the .json file to reformat.
        """
        # Load the data from the .json file.
        with open(path, 'r', encoding='utf-8') as f:
            data = f.read()

        # Pass through the data and reformat it.
        can_edit = False
        i = 0
        while i < len(data):
            # If i is between a pair of brackets it can be edited,
            # otherwise it cannot and if i is an open bracket,
            # remove the newline after it.
            if data[i] == "{":
                can_edit = True
                data = data[:i + 1] + data[i + 2:]
            elif data[i] == "}":
                can_edit = False

            # If i is a comma or open bracket, followed by a newline,
            # and can_edit is True,
            # delete the newline and all subsequent spaces.
            if (
                (data[i] == "," or data[i] == "[") and
                i + 1 < len(data) and
                data[i + 1] == "\n" and
                can_edit
            ):
                indents = 0
                for j in range(i + 2, len(data)):
                    if data[j] == " ":
                        indents += 1
                    else:
                        break
                data = data[:i + 1] + data[i + 2 + indents:]

                # If i is a comma, add a space after it.
                if data[i] == ",":
                    data = data[:i + 1] + " " + data[i + 1:]

            # If i is a closing bracket, following eight spaces
            # and a newline, and can_edit is True,
            # remove the newline and spaces.
            if (
                data[i] == "]" and
                i - 9 >= 0 and
                data[i - 9:i] == "\n        " and
                can_edit
            ):
                data = data[:i - 9] + data[i:]
                i -= 9

            # If i is a closing bracket, following 12 spaces
            # and a newline, and can_edit is True,
            # remove the newline and spaces.
            if (
                data[i] == "]" and
                i - 13 >= 0 and
                data[i - 13:i] == "\n            " and
                can_edit
            ):
                data = data[:i - 13] + data[i:]
                i -= 13

            # If i is a quotation mark that is following
            # something other than a colon, then a space,
            # replace the space with a newline and two tabs.
            if (
                data[i] == "\"" and
                i - 1 >= 0 and
                data[i - 2] != ":" and
                data[i - 1] == " "
            ):
                data = data[:i - 1] + "\n\t\t" + data[i:]

            # Increment i to move to the next character.
            i += 1

        with open(path, 'w', encoding='utf-8') as f:
            f.write(data)

    def finish_editing(self):
        """
        Finish editing the current shape and add it to the level
        and corresponding .json file.
        """

        def make_dynamic_polygon(vertices):
            """
            Make a dynamic polygon from a list of vertices.

            Args:
                vertices: A list of Vectors representing the vertices of the
                polygon in world space.
            
            Returns:
                A DynamicPolygon representing
                the polygon with the given vertices.
            """
            polygon = DynamicPolygon(
                vertices,
                Vector(0, 0),
                Vector(0, 0),
                0,
                0,
                False,
                False,
                True,
                self._DYNAMIC_COLOR,
                "Unnamed Dynamic Polygon"
            )
            return polygon


        def make_polygon(vertices):
            """
            Make a polygon from a list of vertices.

            Args:
                vertices: A list of Vectors representing the vertices of the
                polygon in world space.
            
            Returns:
                A Polygon representing
                the polygon with the given vertices.
            """
            polygon = Polygon(
                vertices,
                Vector(0, 0),
                Vector(0, 0),
                0,
                0,
                False,
                False,
                False,
                self._STATIONARY_COLOR,
                "Unnamed Polygon"
            )
            return polygon


        def make_dynamic_circle(circle):
            """
            Make a dynamic circle from a position and radius.

            Args:
                circle: A tuple of a Vector representing
                the position of the circle in world space
                and a float representing the radius of the circle.
            
            Returns:
                A DynamicCircle representing
                the circle with the given position and radius.
            """
            circle = DynamicCircle(
                circle[1],
                circle[0],
                Vector(0, 0),
                0,
                0,
                False,
                True,
                self._DYNAMIC_COLOR,
                "Unnamed Dynamic Circle"
            )
            return circle


        def make_circle(circle):
            """
            Make a circle from a position and radius.

            Args:
                circle: A tuple of a Vector representing
                the position of the circle in world space
                and a float representing the radius of the circle.
            
            Returns:
                A Circle representing
                the circle with the given position and radius.
            """
            circle = Circle(
                circle[1],
                circle[0],
                Vector(0, 0),
                0,
                0,
                False,
                False,
                self._STATIONARY_COLOR,
                "Unnamed Circle"
            )
            return circle


        def append_json(path, shape):
            """
            Append a shape to the .json file at the given path.

            Args:
                path: The path to the .json file.
                shape: The shape to append.
            """
            # Make a dictionary representing the shape.
            if issubclass(type(shape), Polygon):
                position = shape.position
                vertices = [[v.x + position.x, v.y + position.y]
                    for v in shape.local_vertices]
                shape_dict = {
                    "comment": shape.__repr__(),
                    "vertices": vertices,
                    "position": [0, 0],
                    "velocity": [shape.velocity.x, shape.velocity.y],
                    "angle": shape.angle,
                    "angular_velocity": shape.angular_velocity,
                    "is_bouncy": shape.is_bouncy,
                    "is_slippery": shape.is_slippery,
                    "color": list(shape.color)
                }
            elif issubclass(type(shape), Circle):
                shape_dict = {
                    "comment": shape.__repr__(),
                    "radius": shape.radius,
                    "position": [shape.position.x, shape.position.y],
                    "velocity": [shape.velocity.x, shape.velocity.y],
                    "angle": shape.angle,
                    "angular_velocity": shape.angular_velocity,
                    "is_bouncy": shape.is_bouncy,
                    "is_slippery": shape.is_slippery,
                    "color": list(shape.color)
                }
            else:
                return

            # Load the existing shapes from the .json file.
            path = self._path + path
            try:
                with open(path, "r", encoding="utf-8") as f:
                    shapes = json.load(f)
            except FileNotFoundError:
                shapes = []

            # Append the new shape to the list of shapes.
            shapes.append(shape_dict)

            # Write the updated list of shapes to the .json file.
            with open(path, "w", encoding="utf-8") as f:
                json.dump(shapes, f, indent=4)

            # Reformat the .json file to be more human-readable.
            self.reformat_json(path)

        # If a polygon is being edited, finish editing it.
        if self._editing_polygon is not None and len(
            self._editing_polygon) >= 3:
            if self._editing_shape_is_dynamic:
                polygon = make_dynamic_polygon(self._editing_polygon)
                self._dynamic_polygons.append(polygon)
                append_json("dynamic_polygons.json", polygon)
            else:
                polygon = make_polygon(self._editing_polygon)
                self._polygons.append(polygon)
                append_json("polygons.json", polygon)
            self._editing_polygon = None

        # If a circle is being edited, finish editing it.
        if self._editing_circle is not None:
            if self._editing_shape_is_dynamic:
                circle = make_dynamic_circle(self._editing_circle)
                self._dynamic_circles.append(circle)
                append_json("dynamic_circles.json", circle)
            else:
                circle = make_circle(self._editing_circle)
                self._circles.append(circle)
                append_json("circles.json", circle)
            self._editing_circle = None

    def new_editing_polygon(self, vertex):
        """
        Start editing a new polygon.

        Args:
            vertex: a Vector representing the first vertex of the polygon.
        """
        self.finish_editing()
        self._editing_polygon = [vertex]

    def new_editing_circle(self, position, radius):
        """
        Start editing a new circle.

        Args:
            position: A Vector representing the position of the circle
            in world space.
            radius: A float representing the radius of the circle.
        """
        self.finish_editing()
        self._editing_circle = [position, radius]

    def add_editing_vertex(self, vertex, index=None):
        """
        Add a vertex to the polygon currently being edited.

        Args:
            vertex: A Vector representing the position of the vertex
            in world space.
            index: An integer representing the index at which to insert
            the vertex, or None to append it to the end of the list.
        """
        if self._editing_polygon is not None:
            if index is None:
                self._editing_polygon.append(vertex)
            else:
                self._editing_polygon.insert(index, vertex)

    def remove_editing_vertex(self, index):
        """
        Remove a vertex from the polygon currently being edited.

        Args:
            index: An integer representing the index of the vertex to remove.
        """
        if self._editing_polygon is not None:
            if 0 <= index < len(self._editing_polygon):
                self._editing_polygon.pop(index)

    def move_editing_vertex(self, index, new_position):
        """
        Move a vertex of the polygon currently being edited.

        Args:
            index: An integer representing the index of the vertex to move.
            new_position: A Vector representing the new position of the vertex
            in world space.
        """
        if self._editing_polygon is not None:
            if 0 <= index < len(self._editing_polygon):
                self._editing_polygon[index] = new_position

    def set_editing_circle_position(self, new_position):
        """
        Set the position of the circle currently being edited.

        Args:
            new_position: A Vector representing the new position of the circle
            in world space.
        """
        if self._editing_circle is not None:
            self._editing_circle[0] = new_position

    def set_editing_circle_radius(self, new_radius):
        """
        Set the radius of the circle currently being edited.

        Args:
            new_radius: A float representing the new radius of the circle.
        """
        if self._editing_circle is not None:
            self._editing_circle[1] = new_radius

    def delete_editing_shape(self):
        """
        Delete the shape currently being edited.
        """
        self._editing_polygon = None
        self._editing_circle = None

    def pop_json(self, path, index):
        """
        Remove a shape from the .json file at the given path.

        Args:
            path: A string representing the path to the .json file.
            index: An integer representing the index of the shape to remove.
        """
        # Load the existing shapes from the .json file.
        path = self._path + path
        try:
            with open(path, "r", encoding="utf-8") as f:
                shapes = json.load(f)
        except FileNotFoundError:
            shapes = []

        # Remove the shape at the given index from the list of shapes.
        if 0 <= index < len(shapes):
            shapes.pop(index)

        # Write the updated list of shapes to the .json file.
        with open(path, "w", encoding="utf-8") as f:
            json.dump(shapes, f, indent=4)

        # Reformat the .json file to be more human-readable.
        self.reformat_json(path)

    def edit_existing_polygon(self, polygon):
        """
        Start editing an existing polygon.

        Args:
            polygon: An integer representing the index of the polygon
            in self._polygons to edit.
        
        Raises:
            IndexError: If the polygon index is out of range.
        """
        self.finish_editing()
        if not 0 <= polygon < len(self._polygons):
            raise IndexError("Polygon index out of range.")
        self._editing_polygon = self._polygons[polygon].world_vertices.copy()
        self._editing_shape_is_dynamic = False
        self._polygons.pop(polygon)
        self.pop_json("polygons.json", polygon)

    def edit_existing_dynamic_polygon(self, polygon):
        """
        Start editing an existing dynamic polygon.

        Args:
            polygon: An integer representing the index of the polygon
            in self._dynamic_polygons to edit.
        
        Raises:
            IndexError: If the polygon index is out of range.
        """
        self.finish_editing()
        if not 0 <= polygon < len(self._dynamic_polygons):
            raise IndexError("Polygon index out of range.")
        self._editing_polygon = self._dynamic_polygons[polygon
            ].world_vertices.copy()
        self._editing_shape_is_dynamic = True
        self._dynamic_polygons.pop(polygon)
        self.pop_json("dynamic_polygons.json", polygon)

    def edit_existing_circle(self, circle):
        """
        Start editing an existing circle.

        Args:
            circle: An integer representing the index of the circle
            in self._circles to edit.
        
        Raises:
            IndexError: If the circle index is out of range.
        """
        self.finish_editing()
        if not 0 <= circle < len(self._circles):
            raise IndexError("Circle index out of range.")
        self._editing_circle = [
            self._circles[circle].position,
            self._circles[circle].radius
        ]
        self._editing_shape_is_dynamic = False
        self._circles.pop(circle)
        self.pop_json("circles.json", circle)

    def edit_existing_dynamic_circle(self, circle):
        """
        Start editing an existing dynamic circle.

        Args:
            circle: An integer representing the index of the circle
            in self._dynamic_circles to edit.
        
        Raises:
            IndexError: If the circle index is out of range.
        """
        self.finish_editing()
        if not 0 <= circle < len(self._dynamic_circles):
            raise IndexError("Circle index out of range.")
        self._editing_circle = [
            self._dynamic_circles[circle].position,
            self._dynamic_circles[circle].radius
        ]
        self._editing_shape_is_dynamic = True
        self._dynamic_circles.pop(circle)
        self.pop_json("dynamic_circles.json", circle)

    @property
    def editing_color(self):
        """
        Get the RGB color of the shape currently being edited
        based on whether it is dynamic or stationary.
        """
        if self._editing_shape_is_dynamic:
            return self._DYNAMIC_COLOR
        else:
            return self._STATIONARY_COLOR

    @property
    def editing_polygon(self):
        """Get the polygon currently being edited"""
        return self._editing_polygon

    @property
    def editing_circle(self):
        """Get the circle currently being edited"""
        return self._editing_circle

    @property
    def editing_shape_is_dynamic(self):
        """Get whether the shape currently being edited is dynamic or not"""
        return self._editing_shape_is_dynamic
