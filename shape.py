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
        _angle: A float representing the angular displacement of the shape (radians).
        _angular_velocity: A float representing the angular velocity (radians/s).
        _can_move: A boolean representing if the shape can move.
        _is_inverted: A boolean representing if the mass of the shape is outside it.
        _elasticity: A float in [0, 1] representing the coefficient of restitution.
        _friction: A float in [0, 1] representing the coefficient of friction.
        _moment: A float representing the moment of inertia.
        _mass: A float representing the mass.
        _radius: A float representing the bounding radius (used for broad-phase collision).
    """

    def __init__(
        self,
        position,
        velocity,
        angle,
        angular_velocity,
        can_move,
        is_inverted,
        elasticity,
        friction,
        moment,
        mass,
        radius,
    ):
        """
        Initializes all Shape attributes.

        Args:
            position: A Vector representing the position of the center of mass.
            velocity: A Vector representing the velocity of the shape.
            angle: A float representing the angular displacement (radians).
            angular_velocity: A float representing the angular velocity (radians/s).
            can_move: A boolean representing if the shape can move.
            is_inverted: A boolean representing if the mass is outside the shape.
            elasticity: A float in [0, 1] for the coefficient of restitution.
            friction: A float in [0, 1] for the coefficient of friction.
            moment: A float representing the moment of inertia.
            mass: A float representing the mass.
            radius: A float representing the bounding radius.
        """
        self._position = position
        self._velocity = velocity
        self._angle = angle
        self._angular_velocity = angular_velocity
        self._can_move = can_move
        self._is_inverted = is_inverted
        self._elasticity = elasticity
        self._friction = friction
        self._moment = moment
        self._mass = mass
        self._radius = radius

    # We do not need all of these, but for now just leave them as is.
    # We can remove what we do not need later.

    @property
    def position(self):
        return self._position

    @property
    def velocity(self):
        return self._velocity

    @property
    def angle(self):
        return self._angle

    @property
    def angular_velocity(self):
        return self._angular_velocity

    @property
    def can_move(self):
        return self._can_move

    @property
    def is_inverted(self):
        return self._is_inverted

    @property
    def elasticity(self):
        return self._elasticity

    @property
    def friction(self):
        return self._friction

    @property
    def moment(self):
        return self._moment

    @property
    def mass(self):
        return self._mass

    @property
    def radius(self):
        return self._radius

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
        rotational = 0.5 * self._moment * self._angular_velocity ** 2
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
        velocity=None,
        angle=0,
        angular_velocity=0,
        can_move=False,
        is_inverted=False,
        elasticity=0.5,
        friction=0.5,
    ):
        """
        Initialize a Circle. Mass and moment are derived from radius.

        Args:
            radius: A float representing the radius of the circle.
            position: A Vector representing the position of the center of mass.
            velocity: A Vector representing the velocity (default zero).
            angle: A float representing angular displacement in radians (default 0).
            angular_velocity: A float representing angular velocity in radians/s (default 0).
            can_move: A boolean representing if the shape can move (default False).
            is_inverted: A boolean representing if the mass is outside the shape (default False).
            elasticity: A float in [0, 1] for the coefficient of restitution (default 0.5).
            friction: A float in [0, 1] for the coefficient of friction (default 0.5).
        """
        if velocity is None:
            velocity = Vector(0, 0)

        # Derive mass and moment of inertia from radius (uniform density disc)
        mass = pi * radius * radius
        moment = mass * radius * radius / 2

        self._radius = radius
        super().__init__(
            position,
            velocity,
            angle,
            angular_velocity,
            can_move,
            is_inverted,
            elasticity,
            friction,
            moment,
            mass,
            radius,
        )

    def impulse(self, impulse):
        """
        Apply an instantaneous linear impulse. For a circle the angular
        contribution requires a contact point, so plain impulse is purely linear.
        Use impulse_at for off-center contact.

        Args:
            impulse: A Vector representing the impulse to apply.
        """
        super().impulse(impulse)

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
        # Δω = r × J / I  (2D cross product: rx*Jy - ry*Jx)
        self._angular_velocity += (
            contact_point.x * impulse.y - contact_point.y * impulse.x
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
        velocity=None,
        angle=0,
        angular_velocity=0,
        can_move=False,
        is_inverted=False,
        elasticity=0.5,
        friction=0.5,
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
            velocity: A Vector representing the velocity (default zero).
            angle: A float representing angular displacement in radians (default 0).
            angular_velocity: A float representing angular velocity in radians/s (default 0).
            can_move: A boolean representing if the shape can move (default False).
            is_inverted: A boolean representing if the mass is outside the shape (default False).
            elasticity: A float in [0, 1] for the coefficient of restitution (default 0.5).
            friction: A float in [0, 1] for the coefficient of friction (default 0.5).
        """
        if velocity is None:
            velocity = Vector(0, 0)

        n = len(vertices)

        # Signed area contributions from each edge (shoelace formula pieces)
        # Formula is far too big to shove here so deal with it.
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
                Vector.dot(p1, p1)
                + Vector.dot(p1, p2)
                + Vector.dot(p2, p2)
            )
            moment_num += cross * dot_sum
            moment_den += cross
        moment = (mass / 6) * (moment_num / moment_den) if moment_den != 0 else 0

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
            elasticity,
            friction,
            moment,
            mass,
            bounding_radius,
        )

    @property
    def local_vertices(self):
        """
        Vertex positions relative to the center of mass at angle = 0.
        """
        return self._local_vertices

    def world_vertices(self):
        """
        Compute the current world-space vertex positions by rotating local
        vertices by _angle and then translating by _position.

        Returns:
            A list of Vectors representing the current world-space vertices.
        """
        return [
            Vector(
                self._position.x + v.rotate(self._angle).x,
                self._position.y + v.rotate(self._angle).y,
            )
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
                contact_point.x * impulse.y - contact_point.y * impulse.x
            ) / self._moment