import pytest
import math
from vector import Vector


def test_vector_initialization():
    """
    Tests the Vector class/object initialization
    """
    v = Vector(3, 4)
    assert v.x == 3.0
    assert v.y == 4.0

    v2 = Vector(-5, -1)
    assert v2.x == -5.0
    assert v2.y == -1

    v3 = Vector(999999, -999999)
    assert v3.x == 999999
    assert v3.y == -999999

    v4 = Vector(0, 0)
    assert v4.x == 0
    assert v4.y == 0


def test_vector_repr():
    """
    Tests the Vector class printing systems
    """
    v = Vector(1.5, -2.5)
    assert repr(v) == "(1.5, -2.5)"

    v2 = Vector(-5, 1)
    assert repr(v2) == "(-5, 1)"

    v3 = Vector(999999, -999999)
    assert repr(v3) == "(999999, -999999)"

    v4 = Vector(0, 0)
    assert repr(v4) == "(0, 0)"


def test_vector_get_tuple():
    """
    Test Vector retrieval in tuple format
    """
    v = Vector(7, 8)
    assert v.get_tuple() == (7.0, 8.0)

    v2 = Vector(-5, -13)
    assert v2.get_tuple() == (-5, -13)

    v3 = Vector(-999999, 999999)
    assert v3.get_tuple() == (-999999, 999999)

    v4 = Vector(0, 0)
    assert v4.get_tuple() == (0, 0)


def test_vector_add():
    """
    Test Vector addition
    """
    v1 = Vector(1, 2)
    v2 = Vector(3, 4)
    v1.add(v2)
    assert v1.get_tuple() == (4.0, 6.0)

    v3 = Vector(99999, -99999)
    v4 = Vector(-99999, 99999)
    v3.add(v4)
    assert v3.get_tuple() == (0, 0)

    v5 = Vector(0, 0)
    v6 = Vector(0, -1)
    v5.add(v6)
    assert v5.get_tuple() == (0, -1)


def test_vector_lerp():
    """
    Test Vector linear interpolation
    """
    v1 = Vector(0, 0)
    v2 = Vector(10, 10)
    v1.lerp(v2, 0.5)
    assert v1.get_tuple() == (5.0, 5.0)


def test_vector_rotate():
    """
    Test Vector rotation
    """
    v = Vector(1, 0)
    rotated = v.rotate(math.pi / 2)
    assert rotated.x == pytest.approx(0.0)
    assert rotated.y == pytest.approx(1.0)


def test_vector_scale():
    """
    Test Vector scaling
    """
    v = Vector(2, 3)
    scaled = v.scale(2.5)
    assert scaled.get_tuple() == (5.0, 7.5)

    v2 = Vector(10, 10)
    scaled2 = v2.scale(-2)
    assert scaled2.get_tuple() == (-20.0, -20.0)


def test_vector_normal():
    """
    Test Vector normal calculation
    """
    v = Vector(3, 4)
    norm = v.normal()
    assert norm.x == pytest.approx(0.6)
    assert norm.y == pytest.approx(0.8)


def test_vector_normal_zero_vector():
    """
    Test Vector nomral with zero-vectors
    """
    v = Vector(0, 0)
    norm = v.normal()
    assert norm.get_tuple() == (0.0, 0.0)


def test_vector_dot():
    """
    Test Vector dot products
    """
    v1 = Vector(1, 2)
    v2 = Vector(3, 4)
    assert Vector.dot(v1, v2) == 11.0


def test_vector_diff():
    """
    Test Vector difference calculation
    """
    tail = Vector(1, 1)
    head = Vector(4, 5)
    diff = Vector.diff(tail, head)
    assert diff.get_tuple() == (3.0, 4.0)


def test_vector_det():
    """
    Test Vector summation length(?)
    """
    v1 = Vector(1, 0)
    v2 = Vector(0, 1)
    assert Vector.det(v1, v2) == 1.0


def test_vector_sum():
    v1 = Vector(1, -1)
    v2 = Vector(-1, 2)
    result = Vector.sum(v1, v2)
    assert result.get_tuple() == (0.0, 1.0)
