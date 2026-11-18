import pytest

from bataille_navalle import player
from bataille_navalle.grid import Grid


def test_name():
    p = player.Player("Alice")
    assert p.name == "Alice"

    with pytest.raises(TypeError):
        p = player.Player()


def test_grid():
    p = player.Player("Alice")
    assert isinstance(p.grid, Grid)


def test_shots():
    p = player.Player("Alice")
    assert p.shots == set()
