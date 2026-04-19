import pytest
import math
from vector import Vector
from shape import Shape, Circle, Polygon

@pytest.fixture
def basic_shape():
    return Shape(
        position=Vector(0, 0),
        velocity=Vector(10, 0),
        angle=0.0,
        angular_velocity=1.0,
        can_move=True,
        is_inverted=False,
        is_bouncy=False,
        moment=10.0,
        mass=5.0,
        radius=2.0,
        color=(255, 255, 255)
    )

def test_shape_update_position(basic_shape):
    basic_shape.update_position(0.5)
    assert basic_shape.position.get_tuple() == (5.0, 0.0)
    assert basic_shape.angle == pytest.approx(0.5)

def test_shape_cannot_move(basic_shape):
    basic_shape._can_move = False
    basic_shape.update_position(1.0)
    basic_shape.force(Vector(100, 100), 1.0)
    basic_shape.torque(100, 1.0)
    basic_shape.impulse(Vector(50, 50))
    
    # Assert nothing changed
    assert basic_shape.position.get_tuple() == (0.0, 0.0)
    assert basic_shape.velocity.get_tuple() == (10.0, 0.0)
    assert basic_shape.angular_velocity == 1.0

def test_shape_force_and_torque(basic_shape):
    basic_shape.force(Vector(10, 0), 1.0) # F=ma -> a = 10/5 = 2. v becomes 12
    assert basic_shape.velocity.get_tuple() == (12.0, 0.0)
    
    basic_shape.torque(20, 1.0) # t=Ia -> a = 20/10 = 2. w becomes 3
    assert basic_shape.angular_velocity == 3.0

def test_shape_energy_and_momentum(basic_shape):
    # KE = 0.5 * m * v^2 + 0.5 * I * w^2
    # KE = 0.5 * 5 * 100 + 0.5 * 10 * 1 = 250 + 5 = 255
    assert basic_shape.get_energy() == 255.0
    
    momentum = basic_shape.get_momentum()
    assert momentum.get_tuple() == (50.0, 0.0)

def test_circle_initialization():
    circle = Circle(
        radius=2.0,
        position=Vector(0, 0),
        velocity=Vector(0, 0),
        angle=0.0,
        angular_velocity=0.0,
        can_move=True,
        is_inverted=False,
        is_bouncy=False,
        color=(255, 0, 0)
    )
    expected_mass = math.pi * 4.0
    expected_moment = expected_mass * 4.0 / 2.0
    
    assert circle.mass == pytest.approx(expected_mass)
    assert circle.moment == pytest.approx(expected_moment)

def test_circle_impulse_at():
    circle = Circle(2.0, Vector(0, 0), Vector(0, 0), 0.0, 0.0, True, False, False, (255,0,0))
    impulse = Vector(0, 10)
    contact = Vector(2, 0)
    
    circle.impulse_at(impulse, contact)
    
    # Check linear velocity (J/m)
    assert circle.velocity.y == pytest.approx(10 / circle.mass)
    # Check angular velocity (r x J / I)
    expected_w = (2 * 10 - 0 * 0) / circle.moment
    assert circle.angular_velocity == pytest.approx(expected_w)

def test_polygon_initialization():
    # A 2x2 square centered at origin in world space initially
    vertices = [Vector(-1, -1), Vector(1, -1), Vector(1, 1), Vector(-1, 1)]
    poly = Polygon(
        vertices=vertices,
        position=Vector(5, 5),
        velocity=Vector(0, 0),
        angle=0.0,
        angular_velocity=0.0,
        can_move=True,
        is_inverted=False,
        is_bouncy=False,
        color=(0, 255, 0)
    )
    
    # Mass of 2x2 square should be 4
    assert poly.mass == pytest.approx(4.0)
    # Bounding radius should be sqrt(1^2 + 1^2) = sqrt(2)
    assert poly.radius == pytest.approx(math.sqrt(2))
    # Test local vertices centered correctly
    assert poly.local_vertices[0].get_tuple() == (-1.0, -1.0)

def test_polygon_world_vertices():
    vertices = [Vector(-1, -1), Vector(1, -1), Vector(1, 1), Vector(-1, 1)]
    poly = Polygon(vertices, Vector(10, 10), Vector(0, 0), 0.0, 0.0, True, False, False, (0, 0, 0))
    
    world_verts = poly.world_vertices()
    assert world_verts[0].get_tuple() == (9.0, 9.0)
    assert world_verts[2].get_tuple() == (11.0, 11.0)

def test_polygon_impulse():
    vertices = [Vector(-1, -1), Vector(1, -1), Vector(1, 1), Vector(-1, 1)]
    poly = Polygon(vertices, Vector(0, 0), Vector(0, 0), 0.0, 0.0, True, False, False, (0, 0, 0))
    
    # Pure linear impulse
    poly.impulse(Vector(8, 0))
    assert poly.velocity.get_tuple() == (2.0, 0.0) # mass is 4
    assert poly.angular_velocity == 0.0
    
    # Impulse with contact point (torque)
    poly.impulse(Vector(0, 4), Vector(1, 0))
    assert poly.angular_velocity > 0.0 # Should impart positive spin
