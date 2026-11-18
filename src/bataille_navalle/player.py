import random

from bataille_navalle.grid import Grid


class Player:
    def __init__(
        self,
        name,
        is_computer=False,
        grid_size=10,
        difficulty="normal",
    ):
        if difficulty not in ("facile", "normal", "difficile"):
            raise ValueError("Difficulté inconnue")

        self.name = name
        self.is_computer = is_computer
        self.difficulty = difficulty
        self.grid = Grid(grid_size)

        self.shots = set()
        self.hits = []
        self.targets = []
        self.misses = set()
        self.sunk_positions = set()
        self.pending_hits = set()

        self.total_shots = 0
        self.successful_shots = 0
        self.sunk_count = 0

        # Tailles des bateaux restant à couler.
        self.remaining_sizes = [5, 4, 3, 3, 2]

    def attack(self, opponent, row, col):
        size = opponent.grid.size

        if not (0 <= row < size and 0 <= col < size):
            return "Hors grille"

        position = (row, col)

        if position in self.shots:
            return "Déjà tiré"

        result = opponent.grid.shoot(row, col)

        if result in ("Hors grille", "Déjà tiré"):
            return result

        self.shots.add(position)
        self.total_shots += 1

        if result == "À l'eau":
            self.misses.add(position)

        elif result == "Touché":
            self.successful_shots += 1
            self.pending_hits.add(position)

        elif result == "Coulé":
            self.successful_shots += 1
            self.sunk_count += 1

            # Seul le bateau coulé est révélé.
            positions = opponent.grid.sunk_positions_at(row, col)

            if positions is not None:
                self._resolve_sunk(positions, row, col)
                length = len(positions)

                if length in self.remaining_sizes:
                    self.remaining_sizes.remove(length)

        self.hits = sorted(self.pending_hits)
        self.update_targets(size)

        return result

    def accuracy(self):
        if not self.total_shots:
            return 0.0

        return 100 * self.successful_shots / self.total_shots

    def _neighbors(self, position, size):
        row, col = position

        for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            nr = row + dr
            nc = col + dc

            if 0 <= nr < size and 0 <= nc < size:
                yield nr, nc

    def _resolve_sunk(self, boat, row, col):
        """Retire uniquement les touches du bateau coulé.

        boat peut être un objet Boat, un ensemble
        de positions ou None (ancien test).
        """
        position = (row, col)

        if boat is not None:
            if hasattr(boat, "positions"):
                positions = set(boat.positions)
            else:
                positions = set(boat)

        else:
            # Compatibilité avec les anciens tests.
            # Sans preuve, on conserve les autres
            # touches plutôt que de les supprimer.
            positions = {position}

        self.pending_hits.update(self.hits)
        self.pending_hits.difference_update(positions)
        self.sunk_positions.update(positions)

        self.hits = sorted(self.pending_hits)
        self.update_targets(self.grid.size)

    def _target_scores(self, size):
        """Attribue un score aux cases voisines."""
        scores = {}

        for hit in self.pending_hits:
            for position in self._neighbors(hit, size):
                if position in self.shots:
                    continue

                scores[position] = scores.get(position, 0) + 1

        # Favoriser les prolongements d'alignements.
        for row, col in self.pending_hits:
            for dr, dc in ((0, 1), (1, 0)):
                for sign in (-1, 1):
                    nr = row + dr * sign
                    nc = col + dc * sign

                    if (nr, nc) not in self.pending_hits:
                        continue

                    end_r = nr
                    end_c = nc

                    while (end_r, end_c) in self.pending_hits:
                        end_r += dr * sign
                        end_c += dc * sign

                    target = (end_r, end_c)

                    if (
                        0 <= end_r < size
                        and 0 <= end_c < size
                        and target not in self.shots
                    ):
                        scores[target] = scores.get(target, 0) + 5

        return scores

    def update_targets(self, size):
        scores = self._target_scores(size)

        self.targets = sorted(
            scores,
            key=lambda pos: (-scores[pos], pos[0], pos[1]),
        )

    def _hard_search(self, available, size):
        """Recherche stratégique sans information cachée."""
        # Les bateaux de longueur 2 ou plus
        # peuvent être recherchés en damier.
        if self.remaining_sizes and min(self.remaining_sizes) >= 2:
            candidates = [pos for pos in available if sum(pos) % 2 == 0]
        else:
            candidates = []

        candidates = candidates or available

        # Score basé sur les possibilités de placement.
        scores = {}

        for row, col in candidates:
            score = 0

            for length in self.remaining_sizes:
                for dr, dc in ((0, 1), (1, 0)):
                    for offset in range(length):
                        start_r = row - offset * dr
                        start_c = col - offset * dc

                        positions = [
                            (start_r + i * dr, start_c + i * dc) for i in range(length)
                        ]

                        if all(
                            0 <= r < size and 0 <= c < size and (r, c) not in self.shots
                            for r, c in positions
                        ):
                            score += 1

            scores[(row, col)] = score

        best = max(scores.values())

        choices = [pos for pos, score in scores.items() if score == best]

        return random.choice(choices)

    def computer_attack(self, opponent):
        size = opponent.grid.size

        available = [
            (r, c) for r in range(size) for c in range(size) if (r, c) not in self.shots
        ]

        if not available:
            return None, None, "Aucun tir disponible"

        self.update_targets(size)

        if self.difficulty == "facile":
            row, col = random.choice(available)

        elif self.targets:
            if self.difficulty == "normal":
                row, col = random.choice(self.targets[:4])
            else:
                scores = self._target_scores(size)
                best = max(scores.values())

                choices = [pos for pos in self.targets if scores[pos] == best]

                row, col = random.choice(choices)

        elif self.difficulty == "difficile":
            row, col = self._hard_search(available, size)

        else:
            row, col = random.choice(available)

        result = self.attack(opponent, row, col)

        return row, col, result
