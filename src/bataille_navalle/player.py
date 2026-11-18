import random

from bataille_navalle.grid import Grid


class Player:
    def __init__(self, name, is_computer=False):
        self.name = name
        self.is_computer = is_computer
        self.grid = Grid()
        self.shots = set()

        # Mémoire de l'IA
        self.targets = []
        self.hits = []

    def attack(self, opponent, row, col):
        position = (row, col)

        if position in self.shots:
            return "Déjà tiré"

        result = opponent.grid.shoot(row, col)

        if result != "Hors grille":
            self.shots.add(position)

        return result

    def add_target(self, row, col, size):
        # Vérifier que la case existe
        if not (0 <= row < size and 0 <= col < size):
            return

        position = (row, col)

        # Ne pas ajouter une case déjà tirée
        if position in self.shots:
            return

        if position not in self.targets:
            self.targets.append(position)

    def update_targets(self, size):
        # Reconstruire les cibles à partir
        # des cases touchées du bateau actuel
        self.targets = []

        if not self.hits:
            return

        if len(self.hits) == 1:
            row, col = self.hits[0]

            directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

            random.shuffle(directions)

            for dr, dc in directions:
                self.add_target(row + dr, col + dc, size)

        else:
            rows = [r for r, c in self.hits]
            cols = [c for r, c in self.hits]

            if len(set(rows)) == 1:
                # Bateau horizontal
                row = rows[0]

                self.add_target(row, min(cols) - 1, size)
                self.add_target(row, max(cols) + 1, size)

            elif len(set(cols)) == 1:
                # Bateau vertical
                col = cols[0]

                self.add_target(min(rows) - 1, col, size)
                self.add_target(max(rows) + 1, col, size)

    def computer_attack(self, opponent):
        size = opponent.grid.size

        # Choisir une cible prioritaire
        if self.targets:
            row, col = self.targets.pop(0)

        else:
            available = [
                (r, c)
                for r in range(size)
                for c in range(size)
                if (r, c) not in self.shots
            ]

            if not available:
                return None, None, "Aucun tir disponible"

            row, col = random.choice(available)

        result = self.attack(opponent, row, col)

        if result == "Touché":
            self.hits.append((row, col))
            self.update_targets(size)

        elif result == "Coulé":
            # Le bateau est détruit
            self.hits = []
            self.targets = []

        return row, col, result
