import random

import pytest

from bataille_navalle.boat import Boat
from bataille_navalle.grid import Grid
from bataille_navalle.partie import Partie
from bataille_navalle.player import Player


def make_players(size=10, difficulty="normal"):
    human = Player("Humain", grid_size=size)
    ai = Player(
        "IA",
        is_computer=True,
        grid_size=size,
        difficulty=difficulty,
    )
    return human, ai


def test_sunk_positions_only_after_sinking():
    grid = Grid(5)
    assert grid.place_boat(Boat(2), 1, 1)

    assert grid.shoot(1, 1) == "Touché"
    assert grid.sunk_positions_at(1, 1) is None

    assert grid.shoot(1, 2) == "Coulé"
    assert grid.sunk_positions_at(1, 2) == {(1, 1), (1, 2)}


def test_adjacent_boats_keep_other_hits():
    human, ai = make_players(5)

    # Deux bateaux adjacents
    assert human.grid.place_boat(Boat(2), 0, 0)
    assert human.grid.place_boat(Boat(2), 1, 0)

    assert ai.attack(human, 0, 0) == "Touché"
    assert ai.attack(human, 1, 0) == "Touché"
    assert ai.attack(human, 0, 1) == "Coulé"

    # Le bateau de la deuxième ligne
    # est encore partiellement touché.
    assert (1, 0) in ai.pending_hits

    # Les touches du bateau coulé
    # ne sont plus dans les cibles actives.
    assert (0, 0) not in ai.pending_hits
    assert (0, 1) not in ai.pending_hits

    assert ai.attack(human, 1, 1) == "Coulé"
    assert not ai.pending_hits
    assert ai.sunk_count == 2


def test_old_resolve_sunk_signature():
    ai = Player("IA", True, 5)

    ai.hits = [(0, 0), (3, 3)]
    ai._resolve_sunk(None, 0, 1)

    assert (3, 3) in ai.hits


@pytest.mark.parametrize("difficulty", ["facile", "normal", "difficile"])
def test_ai_never_repeats_shot(difficulty):
    human, ai = make_players(5, difficulty)

    assert human.grid.place_boat(Boat(2), 0, 0)

    seen = set()

    for _ in range(25):
        row, col, result = ai.computer_attack(human)

        assert (row, col) not in seen
        assert result not in ("Déjà tiré", "Hors grille")

        seen.add((row, col))

    assert len(seen) == 25

    assert ai.computer_attack(human) == (None, None, "Aucun tir disponible")


def test_statistics_accuracy():
    human, ai = make_players(5)

    human.grid.place_boat(Boat(2), 0, 0)

    assert ai.attack(human, 0, 0) == "Touché"
    assert ai.attack(human, 4, 4) == "À l'eau"

    assert ai.total_shots == 2
    assert ai.successful_shots == 1
    assert ai.accuracy() == 50.0

    assert ai.attack(human, 0, 0) == "Déjà tiré"
    assert ai.total_shots == 2


def test_sunk_removes_remaining_size():
    human, ai = make_players(10)

    human.grid.place_boat(Boat(2), 0, 0)

    ai.attack(human, 0, 0)
    ai.attack(human, 0, 1)

    assert ai.remaining_sizes.count(2) == 0
    assert ai.sunk_count == 1


def test_invalid_placement():
    grid = Grid(5)

    assert grid.place_boat(Boat(3), 0, 0)

    assert not grid.place_boat(Boat(2), 0, 1)

    assert not grid.place_boat(Boat(3), 4, 4)


def test_journal_right_of_grids(capsys):
    human, ai = make_players(5)
    partie = Partie(human, ai)

    partie._record_shot(human, 2, 3, "Touché")

    partie._show_grids(human, ai)

    output = capsys.readouterr().out

    assert "TA FLOTTE" in output
    assert "GRILLE ADVERSE" in output
    assert "JOURNAL DES TIRS" in output
    assert "C3" in output

    heading = next(line for line in output.splitlines() if "JOURNAL DES TIRS" in line)

    assert (
        heading.index("TA FLOTTE")
        < heading.index("GRILLE ADVERSE")
        < heading.index("JOURNAL DES TIRS")
    )


def test_journal_keeps_last_events(capsys):
    human, ai = make_players(5)
    partie = Partie(human, ai)

    for index in range(20):
        partie.journal.append(f"Événement {index}")

    partie._show_grids(human, ai)

    output = capsys.readouterr().out

    assert "Événement 19" in output
    assert "Événement 0" not in output


@pytest.mark.parametrize("difficulty", ["facile", "normal", "difficile"])
def test_ai_can_finish_complete_game(difficulty):
    random.seed(1234)

    human, ai = make_players(10, difficulty)

    fleet = [
        (5, 0, 0),
        (4, 2, 0),
        (3, 4, 0),
        (3, 6, 0),
        (2, 8, 0),
    ]

    for length, row, col in fleet:
        assert human.grid.place_boat(Boat(length), row, col)

    for _ in range(100):
        if human.grid.all_sunk():
            break

        row, col, result = ai.computer_attack(human)

        assert row is not None
        assert col is not None
        assert result not in (
            "Déjà tiré",
            "Hors grille",
            "Aucun tir disponible",
        )

    assert human.grid.all_sunk()
    assert ai.sunk_count == 5
    assert ai.total_shots <= 100


def test_random_fleet_placement():
    human, ai = make_players()
    partie = Partie(human, ai)

    assert partie._place_random_fleet(ai)

    assert len(ai.grid.boats) == 5

    positions = [pos for boat in ai.grid.boats for pos in boat.positions]

    assert len(positions) == 17
    assert len(set(positions)) == 17
