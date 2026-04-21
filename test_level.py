import pytest
import json
from unittest.mock import patch, mock_open
from level import Level
from vector import Vector
from shape import Circle, Polygon

# Mock JSON data to simulate the file reads
MOCK_PLAYER_JSON = (
    '{"radius": 10.0, "position": [0, 0], "velocity": [0, 0], "angle": 0,'
    ' "angular_velocity": 0, "is_bouncy": false, "color": [255, 0, 0]}'
)
MOCK_BORDER_JSON = (
    '{"vertices": [[-100, -100], [100, -100], [100, 100], [-100, 100]],'
    ' "position": [0, 0], "velocity": [0, 0], "angle": 0, "angular_velocity":'
    ' 0, "is_bouncy": false, "color": [0, 255, 0]}'
)
MOCK_POLYGONS_JSON = (
    '[{"vertices": [[-10, -10], [10, -10], [0, 10]], "position": [50, 50],'
    ' "velocity": [0, 0], "angle": 0, "angular_velocity": 0, "is_bouncy": true,'
    ' "color": [0, 0, 255]}]'
)


def mock_open_side_effect(file_path, *args, **kwargs):
    """Routes the mocked file opening to the correct dummy data."""
    if "player.json" in file_path:
        return mock_open(read_data=MOCK_PLAYER_JSON)()
    elif "border.json" in file_path:
        return mock_open(read_data=MOCK_BORDER_JSON)()
    elif "polygons.json" in file_path:
        return mock_open(read_data=MOCK_POLYGONS_JSON)()
    return mock_open(read_data="{}")()


@patch("builtins.open", side_effect=mock_open_side_effect)
def test_level_initialization(mock_file):
    level = Level("dummy_path/")

    assert isinstance(level.player, Circle)
    assert isinstance(level.border, Polygon)
    assert isinstance(level.polygons, list)
    assert len(level.polygons) == 1
    assert isinstance(level.polygons[0], Polygon)


def test_make_vector_base_case():
    result = Level.make_vector([3, 4])
    assert isinstance(result, Vector)
    assert result.get_tuple() == (3.0, 4.0)


def test_make_vector_nested_case():
    result = Level.make_vector([[1, 2], [3, 4]])
    assert isinstance(result, list)
    assert len(result) == 2
    assert result[0].get_tuple() == (1.0, 2.0)
    assert result[1].get_tuple() == (3.0, 4.0)


def test_make_vector_invalid_length():
    with pytest.raises(ValueError, match="A base list is not of length two!"):
        Level.make_vector([1, 2, 3])


def test_make_vector_invalid_nested_length():
    with pytest.raises(ValueError):
        Level.make_vector([[1, 2], [3, 4, 5]])
