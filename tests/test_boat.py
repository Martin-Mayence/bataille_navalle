import pytest

from bataille_navalle.boat import Boat


def test_boat_size():
    boat = Boat(3)
    assert boat.size == 3

    with pytest.raises(TypeError):
        boat = Boat()

    with pytest.raises(ValueError):
        boat = Boat(0)

    with pytest.raises(ValueError):
        boat = Boat(-1)


def test_boat_sunk():
    boat = Boat(2)
    assert not boat.is_sunk()

    boat.place([(0, 0), (0, 1)])
    boat.shoot((0, 0))
    assert not boat.is_sunk()

    boat.shoot((0, 1))
    assert boat.is_sunk()


def test_shooting():
    boat = Boat(2)
    boat.place([(0, 0), (0, 1)])

    assert boat.shoot((0, 0)) == "Touché"
    assert boat.shoot((0, 1)) == "Coulé"
    assert boat.shoot((0, 2)) == "À l'eau"
    assert boat.shoot((0, 0)) == "Déjà tiré"
