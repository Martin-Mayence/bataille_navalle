from bataille_navalle.water import Water


class Grid:
    def __init__(self, size=10):
        if not isinstance(size, int) or isinstance(size, bool) or not 1 <= size <= 26:
            raise ValueError("La taille de grille doit être comprise entre 1 et 26")
        self.size = size
        self.cells = [[Water() for _ in range(size)] for _ in range(size)]
        self.boats = []

    def can_place(self, boat, row, col, horizontal=True):
        if boat in self.boats or boat.positions or boat.hits:
            return False
        positions = [
            (row + (0 if horizontal else i), col + (i if horizontal else 0))
            for i in range(boat.size)
        ]
        occupied = {p for other in self.boats for p in other.positions}
        return all(
            0 <= r < self.size and 0 <= c < self.size and (r, c) not in occupied
            for r, c in positions
        )

    def place_boat(self, boat, row, col, horizontal=True):
        if not self.can_place(boat, row, col, horizontal):
            return False
        positions = [
            (row + (0 if horizontal else i), col + (i if horizontal else 0))
            for i in range(boat.size)
        ]
        boat.place(positions)
        self.boats.append(boat)
        return True

    def shoot(self, row, col):
        if not (0 <= row < self.size and 0 <= col < self.size):
            return "Hors grille"
        for boat in self.boats:
            if (row, col) in boat.positions:
                return boat.shoot((row, col))
        return self.cells[row][col].shoot()

    def all_sunk(self):
        return bool(self.boats) and all(boat.is_sunk() for boat in self.boats)

    def symbol_at(self, row, col, hide_boats=False):
        position = (row, col)
        for boat in self.boats:
            if position in boat.positions:
                if position in boat.hits:
                    return "X"
                return "~" if hide_boats else "B"
        return "o" if self.cells[row][col].touched else "~"

    def lines(self, hide_boats=False, color=False):
        colors = {"X": "\033[91m", "B": "\033[92m", "o": "\033[93m", "~": "\033[96m"}
        reset = "\033[0m"
        lines = ["    " + " ".join(f"{c:2}" for c in range(self.size))]
        lines.append("   +" + "---" * self.size + "+")
        for r in range(self.size):
            cells = []
            for c in range(self.size):
                symbol = self.symbol_at(r, c, hide_boats)
                if color:
                    symbol = colors[symbol] + symbol + reset
                cells.append(f" {symbol} ")
            lines.append(f" {chr(65 + r)} |" + "".join(cells) + "|")
        lines.append("   +" + "---" * self.size + "+")
        return lines

    def display(self, hide_boats=False, color=True):
        print("\n".join(self.lines(hide_boats, color)))
        print("B = Bateau   X = Touché   o = Raté   ~ = Eau")
