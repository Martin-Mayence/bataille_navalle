import random
import re

from bataille_navalle.boat import Boat
from bataille_navalle.grid import Grid


class Partie:
    RESET = "\033[0m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    CYAN = "\033[96m"
    BOLD = "\033[1m"

    FLEET = (5, 4, 3, 3, 2)

    def __init__(self, player1, player2):
        if player1.grid.size != player2.grid.size:
            raise ValueError("Les grilles doivent avoir la même taille")

        self.players = [player1, player2]
        self.current = 0
        self.journal = []
        self.turn_number = 1

    def demander_coordonnees(self, allow_undo=False):
        size = self.players[0].grid.size

        while True:
            value = (
                input(
                    "Coordonnée (ex. A0, C5)"
                    + (" ou ANNULER" if allow_undo else "")
                    + " : "
                )
                .strip()
                .upper()
                .replace(" ", "")
            )

            if allow_undo and value in ("ANNULER", "U"):
                return None

            match = re.fullmatch(r"([A-Z])(\d+)", value)

            if match:
                row = ord(match.group(1)) - 65
                col = int(match.group(2))

                if 0 <= row < size and 0 <= col < size:
                    return row, col

            print(f"{self.RED}Coordonnée invalide.{self.RESET}")

    def _place_computer_boat(self, grid, boat):
        choices = [
            (r, c, horizontal)
            for horizontal in (True, False)
            for r in range(grid.size)
            for c in range(grid.size)
            if grid.can_place(boat, r, c, horizontal)
        ]

        if not choices:
            return False

        return grid.place_boat(boat, *random.choice(choices))

    def _place_random_fleet(self, player):
        size = player.grid.size

        # Plusieurs tentatives complètes pour éviter
        # un blocage dû à un mauvais placement initial.
        for _ in range(500):
            player.grid = Grid(size)
            success = True

            for taille in self.FLEET:
                boat = Boat(taille)

                if not self._place_computer_boat(player.grid, boat):
                    success = False
                    break

            if success:
                return True

        player.grid = Grid(size)
        return False

    def _manual_placement(self, player):
        player.grid = Grid(player.grid.size)
        index = 0

        while index < len(self.FLEET):
            taille = self.FLEET[index]

            print("\n" + "=" * 35)
            print("PLACEMENT DE TA FLOTTE")
            print("=" * 35)

            player.grid.display(color=True)

            print(f"\nBateau {index + 1}/{len(self.FLEET)}")
            print(f"Taille : {taille}")

            remaining = self.FLEET[index:]
            print("Bateaux à placer :", remaining)

            print("\nANNULER : retirer le dernier bateau")

            coords = self.demander_coordonnees(allow_undo=True)

            if coords is None:
                if index == 0:
                    print("Aucun bateau à annuler.")
                    continue

                player.grid.boats.pop()
                index -= 1

                print(f"{self.YELLOW}Dernier placement annulé.{self.RESET}")
                continue

            row, col = coords

            orientation = input("Orientation (H/V) : ").strip().upper()

            if orientation not in ("H", "V"):
                print("Orientation invalide.")
                continue

            boat = Boat(taille)

            placed = player.grid.place_boat(boat, row, col, orientation == "H")

            if placed:
                index += 1
                print(f"{self.GREEN}Bateau placé !{self.RESET}")
            else:
                print(
                    f"{self.RED}"
                    "Placement impossible : "
                    "hors grille ou chevauchement."
                    f"{self.RESET}"
                )

        print("\nTa flotte est prête !")
        player.grid.display(color=True)

    def setup(self):
        human = self.players[0]
        computer = self.players[1]

        while True:
            print("\n=== PLACEMENT DES BATEAUX ===")
            print("1. Placement manuel")
            print("2. Placement automatique")

            choice = input("Choix : ").strip()

            if choice == "1":
                self._manual_placement(human)
                break

            elif choice == "2":
                if self._place_random_fleet(human):
                    print("\nPlacement automatique terminé.")
                    human.grid.display(color=True)
                    break
                print("Placement impossible.")

            else:
                print("Choix invalide.")

        if not self._place_random_fleet(computer):
            raise ValueError("Impossible de placer la flotte adverse.")

        print("\nL'ordinateur a placé ses bateaux.")
        input("\nAppuie sur Entrée pour commencer...")

    @staticmethod
    def _visible_width(value):
        return len(re.sub(r"\x1b\[[0-9;]*m", "", value))

    def _color_result(self, result):
        if "Coulé" in result:
            return f"{self.RED}{self.BOLD}{result}{self.RESET}"

        if "Touché" in result:
            return f"{self.RED}{result}{self.RESET}"

        if "À l'eau" in result:
            return f"{self.CYAN}{result}{self.RESET}"

        return result

    def _show_grids(self, player, opponent):
        left = player.grid.lines(color=True)
        right = opponent.grid.lines(hide_boats=True, color=True)

        left_width = max(map(self._visible_width, left))
        right_width = max(map(self._visible_width, right))

        gap = "    "
        journal_width = 40

        heading = (
            "TA FLOTTE".ljust(left_width)
            + gap
            + "GRILLE ADVERSE".ljust(right_width)
            + gap
            + "JOURNAL DU TOUR"
        )

        print("\n" + heading)

        print("-" * (left_width + right_width + len(gap) * 2 + journal_width))

        height = max(len(left), len(right))

        # On garde une ligne pour le titre
        # et une ligne vide.
        max_events = max(0, height - 2)

        recent = self.journal[-max_events:] if max_events else []

        notes = [""] * height
        notes[0] = "Derniers événements :"

        # Aligner les événements en bas
        start = height - len(recent)

        for i, event in enumerate(recent):
            notes[start + i] = event

        for i in range(height):
            a = left[i] if i < len(left) else ""
            b = right[i] if i < len(right) else ""
            note = notes[i]

            print(
                a
                + " " * (left_width - self._visible_width(a))
                + gap
                + b
                + " " * (right_width - self._visible_width(b))
                + gap
                + note
            )

        print(
            f"\n{self.GREEN}B = Bateau{self.RESET}"
            f"   {self.RED}X = Touché{self.RESET}"
            f"   {self.YELLOW}o = Raté{self.RESET}"
            f"   {self.CYAN}~ = Eau{self.RESET}"
        )

        human_remaining = sum(not boat.is_sunk() for boat in player.grid.boats)

        enemy_remaining = sum(not boat.is_sunk() for boat in opponent.grid.boats)

        print(
            f"\nTes bateaux : {human_remaining}"
            f"   |   Bateaux adverses : {enemy_remaining}"
        )

        print(f"Tour : {self.turn_number}")

    def _record_shot(self, player, row, col, result):
        if result in ("Déjà tiré", "Hors grille", "Aucun tir disponible"):
            return

        name = "IA" if player.is_computer else "Toi"

        position = f"{chr(65 + row)}{col}"

        message = (
            f"T{self.turn_number:02} "
            f"{name:<3} {position:<4} : "
            f"{self._color_result(result)}"
        )

        self.journal.append(message)

    def _show_statistics(self, winner):
        print("\n" + "=" * 50)
        print(f"{self.GREEN}{self.BOLD}        FIN DE LA PARTIE{self.RESET}")
        print("=" * 50)

        if winner.is_computer:
            print(f"{self.RED}L'ordinateur a gagné !{self.RESET}")
        else:
            print(f"{self.GREEN}Félicitations, tu as gagné !{self.RESET}")

        print("\nSTATISTIQUES")
        print("-" * 50)

        print(f"{'Statistique':<22}{'Toi':>12}{'IA':>12}")

        print("-" * 50)

        human, computer = self.players

        rows = [
            ("Tirs effectués", human.total_shots, computer.total_shots),
            ("Tirs réussis", human.successful_shots, computer.successful_shots),
            ("Bateaux coulés", human.sunk_count, computer.sunk_count),
            ("Précision", f"{human.accuracy():.1f}%", f"{computer.accuracy():.1f}%"),
        ]

        for label, h_value, c_value in rows:
            print(f"{label:<22}{h_value!s:>12}{c_value!s:>12}")

        print("-" * 50)
        print(f"Nombre de tours : {self.turn_number}")
        print("=" * 50)

    def play(self):
        self.setup()

        human, computer = self.players

        while True:
            player = self.players[self.current]
            opponent = self.players[1 - self.current]

            self._show_grids(human, computer)

            if player.is_computer:
                print("\nL'ordinateur réfléchit...")

                row, col, result = player.computer_attack(opponent)

                if result == "Aucun tir disponible":
                    print(result)
                    break

                print(f"IA : {chr(65 + row)}{col} -> {result}")

            else:
                print("\nÀ toi de jouer !")

                row, col = self.demander_coordonnees()

                result = player.attack(opponent, row, col)

                if result in ("Déjà tiré", "Hors grille"):
                    print(f"{self.YELLOW}Tir invalide : {result}{self.RESET}")
                    continue

                print(f"\nRésultat : {self._color_result(result)}")

            self._record_shot(player, row, col, result)

            # Actualiser immédiatement les grilles
            self._show_grids(human, computer)

            if opponent.grid.all_sunk():
                self._show_statistics(player)
                return

            if player.is_computer:
                self.turn_number += 1

            self.current = 1 - self.current
