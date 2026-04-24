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
        _can_move: A boolean representing if the shape can move.
        _is_inverted: A boolean representing if the mass
                      of the shape is outside it.
        _is_bouncy: A boolean representing if the shape is
                    bouncier than usual.
        _moment: A float representing the moment of inertia.
        _mass: A float representing the mass.
        _radius: A float representing the bounding radius
                 (used for broad-phase collision).
        _color: A tuple representing the RGB values of the shape's color.
    """

    def __init__(
        self,
        position,
        velocity,
        angle,
        angular_velocity,
        can_move,
        is_inverted,
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
            can_move: A boolean representing if the shape can move.
            is_inverted: A boolean representing if the mass is
                         outside the shape.
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
        self._can_move = can_move
        self._is_inverted = is_inverted
        self._is_bouncy = is_bouncy
        self._moment = moment
        self._mass = mass
        self._radius = radius
        self._color = color

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
    def can_move(self):
        """Get can_move"""
        return self._can_move

    @property
    def is_inverted(self):
        """Get is_inverted"""
        return self._is_inverted

    @property
    def moment(self):
        """Get moment"""
        return self._moment

    @property
    def mass(self):
        """Get mass"""
        return self._mass

    @property
    def radius(self):
        """Get radius"""
        return self._radius

    @property
    def color(self):
        """Get color"""
        return self._color
    
    @property
    def is_bouncy(self):
        """Get is_bouncy"""
        return self._is_bouncy

    def update_position(self, dt):
        """
        Integrate velocity and angular velocity forward by dt seconds.

        Args:
            dt: A float representing the timestep in seconds.
        """
        if not self._can_move:
            return
        self._position.add(self._velocity.scale(dt))
        self._angle += self._angular_velocity * dt

    def force(self, force, dt):
        """
        Apply a continuous force for one timestep (F = ma → Δv = F/m * dt).

        Args:
            force: A Vector representing the force to apply.
            dt: A float representing the timestep in seconds.
        """
        if not self._can_move:
            return
        self._velocity.add(force.scale(dt / self._mass))

    def torque(self, torque, dt):
        """
        Apply a continuous torque for one timestep (τ = Iα → Δω = τ/I * dt).

        Args:
            torque: A float representing the torque to apply (positive = CCW).
            dt: A float representing the timestep in seconds.
        """
        if not self._can_move:
            return
        self._angular_velocity += torque * dt / self._moment

    def impulse(self, impulse):
        """
        Apply an instantaneous linear impulse (Δv = J / m).

        Args:
            impulse: A Vector representing the impulse to apply.
        """
        if not self._can_move:
            return
        self._velocity.add(impulse.scale(1 / self._mass))

    def get_energy(self):
        """
        Calculate the total kinetic energy (translational + rotational).

        Returns:
            A float representing KE = ½mv² + ½Iω².
        """
        v_sq = Vector.dot(self._velocity, self._velocity)
        translational = 0.5 * self._mass * v_sq
        rotational = 0.5 * self._moment * self._angular_velocity**2
        return translational + rotational

    def get_momentum(self):
        """
        Calculate the linear momentum vector.

        Returns:
            A Vector representing p = mv.
        """
        return self._velocity.scale(self._mass)


class Circle(Shape):
    """
    Stores the physical state of a circle in 2D space.

    Attributes:
        _radius: A float representing the radius of the circle.
        All other attributes are inherited from Shape.
    """

    def __init__(
        self,
        radius,
        position,
        velocity,
        angle,
        angular_velocity,
        can_move,
        is_inverted,
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
            can_move: A boolean representing if the shape can move.
            is_inverted: A boolean representing if the mass
                         is outside the shape.
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
            can_move,
            is_inverted,
            is_bouncy,
            moment,
            mass,
            radius,
            color,
        )

    def impulse_at(self, impulse, contact_point):
        """
        Apply an impulse at a contact point, producing both linear and
        angular velocity changes.

        Args:
            impulse: A Vector representing the impulse.
            contact_point: A Vector representing the contact point
                           relative to the center of mass.
        """
        if not self._can_move:
            return
        self._velocity.add(impulse.scale(1 / self._mass))
        # Delta w = r × J / I  (2D cross product: rx*Jy - ry*Jx)
        self._angular_velocity += (
            Vector.det(contact_point, impulse)
        ) / self._moment


class Polygon(Shape):
    """
    Stores the physical state of a convex polygon in 2D space.
    Vertices are stored relative to the center of mass so that rotation
    is simply a matter of rotating each vertex by _angle.

    Attributes:
        _local_vertices: A list of Vectors representing vertex positions
                         relative to the center of mass at angle = 0.
        All other attributes are inherited from Shape. I think.
    """

    def __init__(
        self,
        vertices,
        position,
        velocity,
        angle,
        angular_velocity,
        can_move,
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
            can_move: A boolean representing if the shape can move.
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

        self._local_vertices = local_vertices
        super().__init__(
            position,
            velocity,
            angle,
            angular_velocity,
            can_move,
            is_inverted,
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
        return self._local_vertices

    def rotated_vertices(self):
        """
        Find the vertex positions relative to the center of mass at angle.

        Returns:
            A list of Vectors representing the local vertices
            rotated by self._angle.
        """
        return [v.rotate(self._angle) for v in self._local_vertices]

    def world_vertices(self):
        """
        Compute the current world-space vertex positions by rotating local
        vertices by _angle and then translating by _position.

        Returns:
            A list of Vectors representing the current world-space vertices.
        """
        return [
            Vector.sum(self._position, v.rotate(self._angle))
            for v in self._local_vertices
        ]

    def impulse(self, impulse, contact_point=None):
        """
        Apply an instantaneous impulse, with optional off-center torque.

        Args:
            impulse: A Vector representing the impulse to apply.
            contact_point: A Vector representing the contact point relative
                           to the center of mass (None for pure linear).
        """
        if not self._can_move:
            return
        self._velocity.add(impulse.scale(1 / self._mass))
        if contact_point is not None:
            # Delta w = r × J / I
            self._angular_velocity += (
                Vector.det(contact_point, impulse)
            ) / self._moment
