import pytest

from bataille_navalle.boat import Boat
from bataille_navalle.grid import Grid
from bataille_navalle.partie import Partie
from bataille_navalle.player import Player


def test_invalid_grid_size():
    with pytest.raises(ValueError):
        Grid(0)
    with pytest.raises(ValueError):
        Grid(27)


def test_same_boat_cannot_be_placed_twice():
    grid = Grid(5)
    boat = Boat(2)
    assert grid.place_boat(boat, 0, 0)
    assert not grid.place_boat(boat, 2, 2)
    assert len(grid.boats) == 1


def test_overlap_and_bounds():
    grid = Grid(5)
    assert grid.place_boat(Boat(3), 0, 0)
    assert not grid.place_boat(Boat(2), 0, 1)
    assert not grid.place_boat(Boat(3), 4, 4)


def test_no_duplicate_shots():
    a, b = Player("A"), Player("B")
    assert a.attack(b, 0, 0) == "À l'eau"
    assert a.attack(b, 0, 0) == "Déjà tiré"
    assert a.attack(b, -1, 0) == "Hors grille"


def test_ai_finishes_neighboring_ship():
    ai = Player("IA", True, 5)
    human = Player("H", grid_size=5)
    human.grid.place_boat(Boat(2), 2, 2)
    ai.shots = {
        (r, c) for r in range(5) for c in range(5) if (r, c) not in ((2, 2), (2, 3))
    }
    _, _, result = ai.computer_attack(human)
    assert result == "Touché"
    _, _, result = ai.computer_attack(human)
    assert result == "Coulé"


def test_sunk_does_not_erase_other_hits():
    ai = Player("IA", True, 5)
    ai.hits = [(0, 0), (3, 3)]
    ai._resolve_sunk(None, 0, 1)
    assert (3, 3) in ai.hits


def test_coordinate_input(monkeypatch):
    partie = Partie(Player("A", grid_size=5), Player("B", grid_size=5))
    answers = iter(["Z9", "C 3"])
    monkeypatch.setattr("builtins.input", lambda _: next(answers))
    assert partie.demander_coordonnees() == (2, 3)


def test_hidden_display(capsys):
    grid = Grid(3)
    grid.place_boat(Boat(2), 0, 0)
    grid.display(hide_boats=True, color=False)
    assert " B |" not in capsys.readouterr().out.splitlines()[2]
