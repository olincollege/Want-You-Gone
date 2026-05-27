"""
Contains the Shape class and its subclasses Circle and Polygon.
"""

from math import pi, sqrt
from vector import Vector


class Shape:
    """
    Stores the physical state of a 2D shape in space.

    Attributes:
        _position: A Vector representing the position of the center of mass.
        _velocity: A Vector representing the velocity of the shape.
        _angle: A float representing the angular displacement
                of the shape (radians).
        _angular_velocity: A float representing the angular velocity (rad/s).
        _IS_BOUNCY: A boolean representing if the shape is
                    bouncier than usual.
        _MOMENT: A float representing the moment of inertia.
        _MASS: A float representing the mass.
        _RADIUS: A float representing the bounding radius
                 (used for broad-phase collision).
        _COLOR: A tuple representing the RGB values of the shape's color.
    """

    def __init__(
        self,
        position,
        velocity,
        angle,
        angular_velocity,
        is_bouncy,
        moment,
        mass,
        radius,
        color,
    ):
        """
        Initializes all Shape attributes.

        Args:
            position: A Vector representing the position of the center of mass.
            velocity: A Vector representing the velocity of the shape.
            angle: A float representing the angular displacement (radians).
            angular_velocity: A float representing the angular velocity (rad/s).
            is_bouncy: A boolean representing if the shape is
                       bouncier than usual.
            moment: A float representing the moment of inertia.
            mass: A float representing the mass.
            radius: A float representing the bounding radius.
            color: A tuple representing the RGB values of the shape's color.
        """
        self._position = position
        self._velocity = velocity
        self._angle = angle
        self._angular_velocity = angular_velocity
        self._IS_BOUNCY = is_bouncy
        self._MOMENT = moment
        self._MASS = mass
        self._RADIUS = radius
        self._COLOR = color

    # We do not need all of these, but for now just leave them as is.
    # We can remove what we do not need later.

    @property
    def position(self):
        """Get position"""
        return self._position

    @property
    def velocity(self):
        """Get velocity"""
        return self._velocity

    @property
    def angle(self):
        """Get angle"""
        return self._angle

    @property
    def angular_velocity(self):
        """Get angular_velocity"""
        return self._angular_velocity

    @property
    def moment(self):
        """Get moment"""
        return self._MOMENT

    @property
    def mass(self):
        """Get mass"""
        return self._MASS

    @property
    def radius(self):
        """Get radius"""
        return self._RADIUS

    @property
    def color(self):
        """Get color"""
        return self._COLOR

    @property
    def is_bouncy(self):
        """Get is_bouncy"""
        return self._IS_BOUNCY

    def set_position(self, position):
        """
        ONLY FOR USE IN PORTAL TELEPORTATION!

        Args:
            position: A Vector representing the
            new position of the center of mass.
        """
        self._position = position

    def get_energy(self):
        """
        Calculate the total kinetic energy (translational + rotational).

        Returns:
            A float representing KE = ½mv² + ½Iω².
        """
        v_sq = Vector.dot(self._velocity, self._velocity)
        translational = 0.5 * self._MASS * v_sq
        rotational = 0.5 * self._MOMENT * self._angular_velocity**2
        return translational + rotational

    def get_momentum(self):
        """
        Calculate the linear momentum vector.

        Returns:
            A Vector representing p = mv.
        """
        return self._velocity.scale(self._MASS)

    def velocity_at(self, point):
        """
        Calculate the velocity at a point in world space, which is the
        center of mass velocity plus the tangential velocity from rotation.

        Args:
            point: A Vector representing the point in world space.

        Returns:
            A Vector representing the velocity at the given point.
        """
        r = Vector.diff(self._position, point)
        tangential = Vector(r.y, -r.x).scale(self._angular_velocity)
        return Vector.sum(self._velocity, tangential)

    def inv_effective_mass(self, contact_point, direction):
        """
        Effective mass is infinite for static shapes,
        so inverse effective mass is zero.

        Returns:
            Zero.
        """
        return 0

    def nudge(self, nudge):
        """
        Non-dynamic shapes cannot be nudged.
        """

    def impulse(self, impulse):
        """
        Non-dynamic shapes cannot be impulsed.
        """

    def impulse_at(self, impulse, contact_point):
        """
        Non-dynamic shapes cannot be impulsed.
        """


class DynamicShape(Shape):
    """
    Stores and updates the physical state of a 2D shape in space.
    """
    def update_position(self, dt):
        """
        Integrate velocity and angular velocity forward by dt seconds.

        Args:
            dt: A float representing the timestep in seconds.
        """
        self._position.add(self._velocity.scale(dt))
        self._angle += self._angular_velocity * dt

    def accelerate(self, acceleration, dt):
        """
        Apply a continuous acceleration for one timestep.

        Args:
            acceleration: A Vector representing the acceleration to apply.
            dt: A float representing the timestep in seconds.
        """
        self._velocity.add(acceleration.scale(dt))

    def angular_accelerate(self, angular_acceleration, dt):
        """
        Apply a continuous angular acceleration for one timestep.

        Args:
            angular_acceleration: A float representing
            the angular acceleration to apply.
            dt: A float representing the timestep in seconds.
        """
        self._angular_velocity += angular_acceleration * dt

    def impulse(self, impulse):
        """
        Apply an instantaneous linear impulse (Δv = J / m).

        Args:
            impulse: A Vector representing the impulse to apply.
        """
        self._velocity.add(impulse.scale(1 / self._MASS))

    def nudge(self, nudge):
        """
        Apply an instantaneous nudge, which is a very small position change
        used to prevent shapes from getting stuck together.

        Args:
            nudge: A Vector representing the nudge to apply.
        """
        self._position.add(nudge)

    def impulse_at(self, impulse, contact_point):
        """
        Apply an impulse at a contact point, producing both linear and
        angular velocity changes.

        Args:
            impulse: A Vector representing the impulse.
            contact_point: A Vector representing
            the contact point in world space.
        """
        contact_vector = Vector.diff(self._position, contact_point)
        self._velocity.add(impulse.scale(1 / self._MASS))
        # Delta w = r × J / I  (2D cross product: rx*Jy - ry*Jx)
        self._angular_velocity += (
            Vector.det(impulse, contact_vector)
        ) / self._MOMENT

    def inv_effective_mass(self, contact_point, direction):
        """
        Calculate the inverse effective mass at a point, which is 
        one divided by the linear mass plus the contribution from angular mass.

        Args:
            contact_point: A Vector representing the point in world space.
            direction: A Vector with a magnitude of 1
            representing the direction of the impulse.

        Returns:
            A float representing the inverse effective mass
            at the contact point.
        """
        contact_vector = Vector.diff(self._position, contact_point)
        inverse_translational = 1 / self._MASS
        inverse_rotational = (
            Vector.det(contact_vector, direction) ** 2 / self._MOMENT
        )
        return inverse_translational + abs(inverse_rotational)


class Circle(Shape):
    """
    Stores the physical state of a circle in 2D space.

    Attributes:
        _RADIUS: A float representing the radius of the circle.
        All other attributes are inherited from Shape.
    """

    def __init__(
        self,
        radius,
        position,
        velocity,
        angle,
        angular_velocity,
        is_bouncy,
        color,
    ):
        """
        Initialize a Circle. Mass and moment are derived from radius.

        Args:
            radius: A float representing the radius of the circle.
            position: A Vector representing the position of the center of mass.
            velocity: A Vector representing the velocity.
            angle: A float representing angular displacement in radians.
            angular_velocity: A float representing angular velocity in rad/s.
            is_bouncy: A boolean representing if the shape is
                       bouncier than usual.
            color: A tuple representing the RGB values of the shape's color.
        """
        # Derive mass and moment of inertia from radius (uniform density disc)
        mass = pi * radius * radius
        moment = mass * radius * radius / 2

        super().__init__(
            position,
            velocity,
            angle,
            angular_velocity,
            is_bouncy,
            moment,
            mass,
            radius,
            color,
        )


class Polygon(Shape):
    """
    Stores the physical state of a convex polygon in 2D space.
    Vertices are stored relative to the center of mass so that rotation
    is simply a matter of rotating each vertex by _angle.

    Attributes:
        _LOCAL_VERTICES: A list of Vectors representing vertex positions
                         relative to the center of mass at angle = 0.
        _world_vertices: A list of Vectors representing vertex positions.
        All other attributes are inherited from Shape.
    """

    def __init__(
        self,
        vertices,
        position,
        velocity,
        angle,
        angular_velocity,
        is_inverted,
        is_bouncy,
        color,
    ):
        """
        Initialize a Polygon from a list of world-space vertices.
        Mass, moment, and center of mass are derived from the vertex list.
        Vertices are re-centered around the center of mass.

        Args:
            vertices: A list of Vectors representing the polygon's vertices
                      in world space (counter-clockwise winding assumed).
            position: A Vector representing where the polygon's center of mass
                      sits in the world. The vertices are offset so that
                      (0, 0) in local space is the center of mass.
            velocity: A Vector representing the velocity.
            angle: A float representing angular displacement in radians.
            angular_velocity: A float representing angular velocity in rad/s.
            is_inverted: A boolean representing if
                         the mass is outside the shape.
            is_bouncy: A boolean representing if the shape
                       is bouncier than usual.
            color: A tuple representing the RGB values of the shape's color.
        """
        n = len(vertices)

        # Signed area contributions from each edge (shoelace formula pieces)
        # Formula is far too big to shove here so deal with it.
        segment_areas = [
            Vector.det(vertices[i - 1], vertices[i]) for i in range(n)
        ]
        signed_area = sum(segment_areas)
        # For a normal polygon we want CCW winding (signed_area > 0).
        # For an inverted polygon we want CW winding (signed_area < 0).
        # Reverse and recompute when the winding is wrong.
        if (signed_area < 0) == is_inverted:
            vertices.reverse()
            segment_areas = [
                Vector.det(vertices[i - 1], vertices[i]) for i in range(n)
            ]
            signed_area = sum(segment_areas)
        mass = abs(signed_area) / 2

        # Center of mass via the standard polygon centroid formula
        x_com = sum(
            (vertices[i - 1].x + vertices[i].x) * segment_areas[i]
            for i in range(n)
        ) / (6 * mass if signed_area > 0 else -6 * mass)
        y_com = sum(
            (vertices[i - 1].y + vertices[i].y) * segment_areas[i]
            for i in range(n)
        ) / (6 * mass if signed_area > 0 else -6 * mass)
        center_of_mass = Vector(x_com, y_com)

        # Re-center vertices so local (0, 0) is the center of mass
        local_vertices = [Vector.diff(center_of_mass, v) for v in vertices]
        position = Vector.sum(position, center_of_mass)

        # Moment of inertia for a polygon about its centroid
        moment_num = 0.0
        moment_den = 0.0
        for i in range(n):
            p1 = local_vertices[i - 1]
            p2 = local_vertices[i]
            cross = abs(Vector.det(p1, p2))
            dot_sum = (
                Vector.dot(p1, p1) + Vector.dot(p1, p2) + Vector.dot(p2, p2)
            )
            moment_num += cross * dot_sum
            moment_den += cross
        moment = (
            (mass / 6) * (moment_num / moment_den) if moment_den != 0 else 0
        )

        # Bounding radius: furthest vertex from the center of mass
        bounding_radius = max(
            sqrt(v.x * v.x + v.y * v.y) for v in local_vertices
        )

        self._LOCAL_VERTICES = local_vertices
        self._rotated_vertices = [
            v.rotate(angle) for v in self._LOCAL_VERTICES]
        self._world_vertices = [
            Vector.sum(position, v.rotate(angle))
            for v in self._LOCAL_VERTICES
            ]
        super().__init__(
            position,
            velocity,
            angle,
            angular_velocity,
            is_bouncy,
            moment,
            mass,
            bounding_radius,
            color,
        )

    @property
    def local_vertices(self):
        """
        Vertex positions relative to the center of mass at angle = 0.
        """
        return self._LOCAL_VERTICES

    @property
    def world_vertices(self):
        """
        Compute the current world-space vertex positions by rotating local
        vertices by _angle and then translating by _position.

        Returns:
            A list of Vectors representing the current world-space vertices.
        """
        return self._world_vertices

    @property
    def rotated_vertices(self):
        """
        Find the vertex positions relative to the center of mass at angle.

        Returns:
            A list of Vectors representing the local vertices
            rotated by self._angle.
        """
        return self._rotated_vertices


class DynamicCircle(Circle, DynamicShape):
    """
    Store and update the physical state of a circle in 2D space.

    Attributes:
        All attributes are inherited from Circle and DynamicShape.
    """

class DynamicPolygon(Polygon, DynamicShape):
    """
    Store and update the physical state of a polygon in 2D space.

    Attributes:
        All attributes are inherited from Polygon and DynamicShape.
    """
    def update_rotated_vertices(self):
        """
        Update rotated vertices to match the current state of the polygon.
        """
        self._rotated_vertices = [
            v.rotate(self._angle) for v in self._LOCAL_VERTICES]

    def update_world_vertices(self):
        """
        Update world vertices to match the current state of the polygon.
        """
        self._world_vertices = [
            Vector.sum(self._position, v)
            for v in self._rotated_vertices]

    def update_position(self, dt):
        """
        Integrate velocity, angular velocity forward by dt seconds
        and update rotated and world vertices.

        Args:
            dt: A float representing the timestep in seconds.
        """
        super().update_position(dt)
        self.update_rotated_vertices()
        self.update_world_vertices()

    def nudge(self, nudge):
        """
        Apply an instantaneous nudge, which is a very small position change
        used to prevent shapes from getting stuck together
        and update world vertices.

        Args:
            nudge: A Vector representing the nudge to apply.
        """
        super().nudge(nudge)
        self.update_world_vertices()
