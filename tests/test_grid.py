from bataille_navalle.boat import Boat
from bataille_navalle.grid import Grid


def test_cells():
    grid = Grid(size=5)
    assert len(grid.cells) == 5
    assert len(grid.cells[0]) == 5

    for row in grid.cells:
        for cell in row:
            assert not cell.touched


def test_size():
    grid = Grid(size=7)
    assert grid.size == 7

    grid_default = Grid()
    assert grid_default.size == 10


def test_place_boat():
    grid = Grid(size=5)
    boat = Boat(size=3)

    # Place a boat horizontally
    assert grid.place_boat(boat, row=1, col=1, horizontal=True)
    assert boat.positions == [(1, 1), (1, 2), (1, 3)]

    # Try to place another boat overlapping the first one
    another_boat = Boat(size=2)
    assert not grid.place_boat(another_boat, row=1, col=2, horizontal=True)

    # Place a boat vertically
    vertical_boat = Boat(size=2)
    assert grid.place_boat(vertical_boat, row=0, col=0, horizontal=False)
    assert vertical_boat.positions == [(0, 0), (1, 0)]


def test_shooting():
    grid = Grid(size=5)
    boat = Boat(size=2)
    grid.place_boat(boat, row=1, col=1, horizontal=True)

    # Shoot at the boat
    assert grid.shoot(1, 1) == "Touché"
    assert grid.shoot(1, 2) == "Coulé"

    # Shoot at water
    assert grid.shoot(0, 0) == "À l'eau"

    # Shoot at the same position again
    assert grid.shoot(1, 1) == "Déjà tiré"


def test_all_sunk():
    grid = Grid(size=5)
    boat1 = Boat(size=2)
    boat2 = Boat(size=3)

    grid.place_boat(boat1, row=0, col=0, horizontal=True)
    grid.place_boat(boat2, row=2, col=2, horizontal=False)

    # Initially, not all boats are sunk
    assert not grid.all_sunk()

    # Sink the first boat
    grid.shoot(0, 0)
    grid.shoot(0, 1)
    assert not grid.all_sunk()

    # Sink the second boat
    grid.shoot(2, 2)
    grid.shoot(3, 2)
    grid.shoot(4, 2)
    assert grid.all_sunk()


def test_display(capsys):
    grid = Grid(size=3)
    boat = Boat(size=2)
    grid.place_boat(boat, row=0, col=0, horizontal=True)

    # Shoot at the boat and water
    grid.shoot(0, 0)  # Hit
    grid.shoot(1, 1)  # Miss

    # Display the grid without hiding boats
    grid.display(hide_boats=False)
    captured = capsys.readouterr()
    assert "X" in captured.out  # Hit symbol
    assert "o" in captured.out  # Miss symbol
    assert "~" in captured.out  # Water symbol

    # Display the grid with hiding boats
    grid.display(hide_boats=True)
    captured_hidden = capsys.readouterr()
    assert "X" in captured_hidden.out  # Hit symbol
    assert "o" in captured_hidden.out  # Miss symbol
    assert "~" in captured_hidden.out  # Water symbol
