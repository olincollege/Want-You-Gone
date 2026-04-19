import pytest
import math
from vector import Vector

def test_vector_initialization():
    v = Vector(3, 4)
    assert v.x == 3.0
    assert v.y == 4.0

def test_vector_repr():
    v = Vector(1.5, -2.5)
    assert repr(v) == "(1.5, -2.5)"

def test_vector_get_tuple():
    v = Vector(7, 8)
    assert v.get_tuple() == (7.0, 8.0)

def test_vector_add():
    v1 = Vector(1, 2)
    v2 = Vector(3, 4)
    v1.add(v2)
    assert v1.get_tuple() == (4.0, 6.0)

def test_vector_lerp():
    v1 = Vector(0, 0)
    v2 = Vector(10, 10)
    v1.lerp(v2, 0.5)
    assert v1.get_tuple() == (5.0, 5.0)

def test_vector_rotate():
    v = Vector(1, 0)
    rotated = v.rotate(math.pi / 2)
    assert rotated.x == pytest.approx(0.0)
    assert rotated.y == pytest.approx(1.0)

def test_vector_scale():
    v = Vector(2, 3)
    scaled = v.scale(2.5)
    assert scaled.get_tuple() == (5.0, 7.5)

def test_vector_normal():
    v = Vector(3, 4)
    norm = v.normal()
    assert norm.x == pytest.approx(0.6)
    assert norm.y == pytest.approx(0.8)

def test_vector_normal_zero_vector():
    v = Vector(0, 0)
    norm = v.normal()
    assert norm.get_tuple() == (0.0, 0.0)

def test_vector_dot():
    v1 = Vector(1, 2)
    v2 = Vector(3, 4)
    assert Vector.dot(v1, v2) == 11.0

def test_vector_diff():
    tail = Vector(1, 1)
    head = Vector(4, 5)
    diff = Vector.diff(tail, head)
    assert diff.get_tuple() == (3.0, 4.0)

def test_vector_det():
    v1 = Vector(1, 0)
    v2 = Vector(0, 1)
    assert Vector.det(v1, v2) == 1.0

def test_vector_sum():
    v1 = Vector(1, -1)
    v2 = Vector(-1, 2)
    result = Vector.sum(v1, v2)
    assert result.get_tuple() == (0.0, 1.0)
