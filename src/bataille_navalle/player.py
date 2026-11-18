import random

from bataille_navalle.grid import Grid


class Player:
    def __init__(self, name, is_computer=False, grid_size=10):
        self.name = name
        self.is_computer = is_computer
        self.grid = Grid(grid_size)
        self.shots = set()
        # Touches non résolues, classées par bateau probable.
        self.hits = []
        self.targets = []
        self.misses = set()
        self.sunk_positions = set()

    def attack(self, opponent, row, col):
        if not (0 <= row < opponent.grid.size and 0 <= col < opponent.grid.size):
            return "Hors grille"
        if (row, col) in self.shots:
            return "Déjà tiré"
        result = opponent.grid.shoot(row, col)
        self.shots.add((row, col))
        return result

    def _neighbors(self, position, size):
        r, c = position
        return [
            (r + dr, c + dc)
            for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1))
            if 0 <= r + dr < size and 0 <= c + dc < size
        ]

    def _candidate_targets(self, size):
        # Chaque touche non résolue reste une piste, même si un autre bateau coule.
        candidates = []
        for hit in self.hits:
            for neighbor in self._neighbors(hit, size):
                if neighbor not in self.shots and neighbor not in candidates:
                    candidates.append(neighbor)

        # Favoriser une ligne déjà touchée, sans présumer que des bateaux voisins
        # appartiennent au même navire.
        def score(pos):
            r, c = pos
            return sum(1 for hr, hc in self.hits if abs(hr - r) + abs(hc - c) == 1)

        random.shuffle(candidates)
        candidates.sort(key=score, reverse=True)
        return candidates

    def update_targets(self, size):
        self.targets = self._candidate_targets(size)

    def _resolve_sunk(self, opponent, row, col):
        hit_set = set(self.hits) | {(row, col)}
        candidates = []
        for dr, dc in ((0, 1), (1, 0)):
            segment = [(row, col)]
            for sign in (-1, 1):
                r, c = row + sign * dr, col + sign * dc
                while (r, c) in hit_set:
                    segment.append((r, c))
                    r += sign * dr
                    c += sign * dc
            candidates.append(segment)
        self.sunk_positions.add((row, col))
        self.hits = [p for p in self.hits if p != (row, col)]

    def computer_attack(self, opponent):
        size = opponent.grid.size
        self.update_targets(size)
        if self.targets:
            row, col = self.targets[0]
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
        elif result == "Coulé":
            self._resolve_sunk(opponent, row, col)
        elif result == "À l'eau":
            self.misses.add((row, col))
        self.update_targets(size)
        return row, col, result
