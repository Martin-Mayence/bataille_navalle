import random
import re

from bataille_navalle.boat import Boat


class Partie:
    def __init__(self, player1, player2):
        if player1.grid.size != player2.grid.size:
            raise ValueError("Les grilles doivent avoir la même taille")
        self.players = [player1, player2]
        self.current = 0
        self.journal = []

    def demander_coordonnees(self):
        size = self.players[0].grid.size
        while True:
            value = (
                input(f"Coordonnée (ex. A0, A 0, {chr(64 + size)}{size - 1}) : ")
                .strip()
                .upper()
                .replace(" ", "")
            )
            if len(value) >= 2 and "A" <= value[0] <= chr(64 + size):
                try:
                    col = int(value[1:])
                except ValueError:
                    col = -1
                if 0 <= col < size:
                    return ord(value[0]) - 65, col
            print("Coordonnée invalide, recommence.")

    def _place_computer_boat(self, grid, boat):
        choices = [
            (r, c, horizontal)
            for horizontal in (True, False)
            for r in range(grid.size)
            for c in range(grid.size)
            if grid.can_place(boat, r, c, horizontal)
        ]
        if not choices:
            raise ValueError("Impossible de placer toute la flotte sur cette grille")
        return grid.place_boat(boat, *random.choice(choices))

    def setup(self):
        tailles = [5, 4, 3, 3, 2]
        for player in self.players:
            print(f"\n=== Placement : {player.name} ===")
            for taille in tailles:
                boat = Boat(taille)
                if player.is_computer:
                    self._place_computer_boat(player.grid, boat)
                    continue
                while True:
                    player.grid.display()
                    print(f"Bateau de taille {taille}")
                    row, col = self.demander_coordonnees()
                    orientation = input("Orientation (H/V) : ").strip().upper()
                    if orientation not in ("H", "V"):
                        print("Orientation invalide.")
                    elif player.grid.place_boat(boat, row, col, orientation == "H"):
                        break
                    else:
                        print("Placement impossible : hors grille ou chevauchement.")
            if player.is_computer:
                print("L'ordinateur a placé ses bateaux.")
            else:
                print("Ta flotte est prête !")

    @staticmethod
    def _visible_width(value):
        """Largeur affichée, sans les séquences de couleur ANSI."""
        return len(re.sub(r"\x1b\[[0-9;]*m", "", value))

    def _show_grids(self, player, opponent):
        left = player.grid.lines(color=True)
        right = opponent.grid.lines(hide_boats=True, color=True)
        left_width = max(map(self._visible_width, left))
        right_width = max(map(self._visible_width, right))
        gap = "    "
        journal_width = 34

        heading = (
            "TA FLOTTE".ljust(left_width)
            + gap
            + "GRILLE ADVERSE".ljust(right_width)
            + gap
            + "JOURNAL DU TOUR"
        )
        print("\n" + heading)
        print("-" * (left_width + right_width + len(gap) * 2 + journal_width))

        # Les derniers événements tiennent dans la hauteur des grilles.
        max_events = len(left) - 2
        recent = self.journal[-max_events:]
        notes = ["Derniers tirs :", ""] + recent
        height = max(len(left), len(right), len(notes))
        for i in range(height):
            a = left[i] if i < len(left) else ""
            b = right[i] if i < len(right) else ""
            note = notes[i] if i < len(notes) else ""
            print(
                a
                + " " * (left_width - self._visible_width(a))
                + gap
                + b
                + " " * (right_width - self._visible_width(b))
                + gap
                + note
            )

        print("B = Bateau   X = Touché   o = Raté   ~ = Eau")
        print("Tes bateaux restants :", sum(not b.is_sunk() for b in player.grid.boats))
        print(
            "Bateaux adverses restants :",
            sum(not b.is_sunk() for b in opponent.grid.boats),
        )

    def _record_shot(self, player, row, col, result):
        if result not in ("Déjà tiré", "Hors grille", "Aucun tir disponible"):
            name = "IA" if player.is_computer else "Toi"
            self.journal.append(f"{name} {chr(65 + row)}{col} : {result}")

    def play(self):
        self.setup()
        while True:
            player = self.players[self.current]
            opponent = self.players[1 - self.current]
            print(f"\n=== Tour de {player.name} ===")
            self._show_grids(self.players[0], self.players[1])

            if player.is_computer:
                row, col, result = player.computer_attack(opponent)
            else:
                row, col = self.demander_coordonnees()
                result = player.attack(opponent, row, col)
                if result in ("Déjà tiré", "Hors grille"):
                    print("Tir invalide :", result)
                    continue

            self._record_shot(player, row, col, result)
            self._show_grids(self.players[0], self.players[1])

            if opponent.grid.all_sunk():
                print(f"\nVictoire de {player.name} !")
                break
            self.current = 1 - self.current
