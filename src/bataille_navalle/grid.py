from bataille_navalle import water


class Grid:
    def __init__(self, size=10):
        self.size = size
        self.cells = [[water.Water() for _ in range(size)] for _ in range(size)]
        self.boats = []

    def place_boat(self, boat, row, col, horizontal=True):
        positions = []

        for i in range(boat.size):
            r = row if horizontal else row + i
            c = col + i if horizontal else col

            if not (0 <= r < self.size and 0 <= c < self.size):
                return False

            for other in self.boats:
                if (r, c) in other.positions:
                    return False

            positions.append((r, c))

        boat.place(positions)
        self.boats.append(boat)
        return True

    def shoot(self, row, col):
        if not (0 <= row < self.size and 0 <= col < self.size):
            return "Hors grille"

        position = (row, col)

        for boat in self.boats:
            if position in boat.positions:
                return boat.shoot(position)

        return self.cells[row][col].shoot()

    def all_sunk(self):
        return bool(self.boats) and all(boat.is_sunk() for boat in self.boats)

    def display(self, hide_boats=False):
        # Couleurs du terminal
        RESET = "\033[0m"
        GREEN = "\033[92m"
        RED = "\033[91m"
        YELLOW = "\033[93m"
        CYAN = "\033[96m"

        # En-tête
        print()
        print("     " + "   ".join(str(i) for i in range(self.size)))

        print("   +" + "---+" * self.size)

        for r in range(self.size):
            # Lettres A, B, C...
            letter = chr(65 + r)
            line = f" {letter} |"

            for c in range(self.size):
                position = (r, c)

                symbol = f"{CYAN}~{RESET}"

                # Tir raté
                if self.cells[r][c].touched:
                    symbol = f"{YELLOW}o{RESET}"

                # Vérifier les bateaux
                for boat in self.boats:
                    if position in boat.positions:
                        if position in boat.hits:
                            symbol = f"{RED}X{RESET}"
                        elif not hide_boats:
                            symbol = f"{GREEN}B{RESET}"

                line += f" {symbol} |"

            print(line)
            print("   +" + "---+" * self.size)

        print()
        print(
            f"{GREEN}B{RESET} = Bateau   "
            f"{RED}X{RESET} = Touché   "
            f"{YELLOW}o{RESET} = Raté   "
            f"{CYAN}~{RESET} = Eau"
        )
        print()
