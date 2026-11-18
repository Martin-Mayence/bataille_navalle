import random

from bataille_navalle.grid import Grid


class Player:
    def __init__(self, name, is_computer=False, grid_size=10, difficulty="normal"):
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

        self.total_shots = 0
        self.successful_shots = 0
        self.sunk_count = 0

        # Mémoire des touches non résolues
        self.pending_hits = set()

    def attack(self, opponent, row, col):
        size = opponent.grid.size

        if not (0 <= row < size and 0 <= col < size):
            return "Hors grille"

        if (row, col) in self.shots:
            return "Déjà tiré"

        result = opponent.grid.shoot(row, col)

        self.shots.add((row, col))
        self.total_shots += 1

        if result in ("Touché", "Coulé"):
            self.successful_shots += 1

        if result == "Coulé":
            self.sunk_count += 1

        if result == "À l'eau":
            self.misses.add((row, col))

        return result

    def accuracy(self):
        if self.total_shots == 0:
            return 0.0

        return self.successful_shots / self.total_shots * 100

    def _neighbors(self, position, size):
        row, col = position

        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

        return [
            (row + dr, col + dc)
            for dr, dc in directions
            if 0 <= row + dr < size and 0 <= col + dc < size
        ]

    def _target_scores(self, size):
        scores = {}

        for row, col in self.pending_hits:
            for target in self._neighbors((row, col), size):
                if target in self.shots:
                    continue

                scores[target] = scores.get(target, 0) + 1

        # Bonus pour les alignements de touches
        for row, col in self.pending_hits:
            for dr, dc in ((0, 1), (1, 0)):
                for sign in (-1, 1):
                    nr = row + dr * sign
                    nc = col + dc * sign

                    if (nr, nc) not in self.pending_hits:
                        continue

                    end_r = nr + dr * sign
                    end_c = nc + dc * sign

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
        self.targets = sorted(scores, key=lambda p: scores[p], reverse=True)

    def _resolve_sunk(self, boat, row, col):
        position = (row, col)

        # Compatibilité avec les anciennes touches
        self.pending_hits.update(self.hits)

        if boat is not None:
            # Si le bateau est connu, retirer uniquement
            # les positions de ce bateau.
            sunk_positions = set(boat.positions)
        else:
            # Sinon, déterminer le segment probable
            # à partir des touches connues.
            hit_set = self.pending_hits | {position}
            segments = []

            for dr, dc in ((0, 1), (1, 0)):
                segment = {position}

                for sign in (-1, 1):
                    nr = row + dr * sign
                    nc = col + dc * sign

                    while (nr, nc) in hit_set:
                        segment.add((nr, nc))
                        nr += dr * sign
                        nc += dc * sign

                segments.append(segment)

            sunk_positions = max(segments, key=len)

        self.sunk_positions.update(sunk_positions)
        self.pending_hits.difference_update(sunk_positions)

        # Synchroniser les anciennes et nouvelles données
        self.hits = sorted(self.pending_hits)

        self.update_targets(self.grid.size)

    def _random_search(self, available):
        return random.choice(available)

    def _hard_search(self, available):
        # Recherche en damier
        checkerboard = [pos for pos in available if (pos[0] + pos[1]) % 2 == 0]

        candidates = checkerboard or available

        # Favoriser les cases centrales
        size = self.grid.size
        center = (size - 1) / 2

        scores = {
            pos: (-abs(pos[0] - center) - abs(pos[1] - center)) for pos in candidates
        }

        best = max(scores.values())

        choices = [pos for pos in candidates if scores[pos] == best]

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
            row, col = self._random_search(available)

        elif self.targets:
            if self.difficulty == "normal":
                # Choix parmi les cibles voisines
                row, col = random.choice(self.targets[:4])
            else:
                # Priorité à la cible la mieux notée
                row, col = self.targets[0]

        elif self.difficulty == "difficile":
            row, col = self._hard_search(available)

        else:
            row, col = self._random_search(available)

        result = self.attack(opponent, row, col)
        position = (row, col)

        if result == "Touché":
            self.pending_hits.add(position)

        elif result == "Coulé":
            self._resolve_sunk(None, row, col)

        self.hits = sorted(self.pending_hits)
        self.update_targets(size)

        return row, col, result
