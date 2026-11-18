import random

from bataille_navalle.boat import Boat


class Partie:
    def __init__(self, player1, player2):
        self.players = [player1, player2]
        self.current = 0

    def setup(self):
        tailles = [5, 4, 3, 3, 2]

        for player in self.players:
            print(f"\n=== Placement : {player.name} ===")

            for taille in tailles:
                placed = False

                while not placed:
                    boat = Boat(taille)

                    if player.is_computer:
                        row = random.randrange(player.grid.size)
                        col = random.randrange(player.grid.size)
                        horizontal = random.choice([True, False])

                        placed = player.grid.place_boat(boat, row, col, horizontal)

                    else:
                        player.grid.display()
                        print(f"\nBateau de taille {taille}")

                        try:
                            row, col = self.demander_coordonnees()
                            orientation = input("Orientation (H/V) : ").strip().upper()

                            if orientation not in ("H", "V"):
                                print("Orientation invalide")
                                continue

                            placed = player.grid.place_boat(
                                boat, row, col, orientation == "H"
                            )

                            if not placed:
                                print("Placement impossible !")

                        except ValueError:
                            print("Coordonnées invalides")

            if player.is_computer:
                print("L'ordinateur a placé ses bateaux.")
            else:
                print("\nTes bateaux sont placés !")
                player.grid.display()

    def play(self):
        self.setup()

        while True:
            player = self.players[self.current]
            opponent = self.players[1 - self.current]

            print(f"\n=== Tour de {player.name} ===")

            if player.is_computer:
                row, col, result = player.computer_attack(opponent)

                print(f"L'ordinateur tire en ({row}, {col})")
                print(f"Résultat : {result}")

            else:
                print("\nTa grille :")
                player.grid.display()

                print("\nGrille adverse :")
                opponent.grid.display(hide_boats=True)

                try:
                    row, col = self.demander_coordonnees()
                except ValueError:
                    print("Coordonnées invalides")
                    continue

                result = player.attack(opponent, row, col)
                print(f"\nRésultat : {result}")

                if result in ("Déjà tiré", "Hors grille"):
                    continue

            if opponent.grid.all_sunk():
                print(f"\nVictoire de {player.name} !")
                break

            self.current = 1 - self.current

    def demander_coordonnees(self):
        while True:
            ligne = input("Ligne (A-J) : ").strip().upper()
            colonne = input("Colonne (0-9) : ").strip()

            if len(ligne) != 1 or not ("A" <= ligne <= "J"):
                print("Ligne invalide ! Utilise A à J.")
                continue

            try:
                col = int(colonne)
            except ValueError:
                print("Colonne invalide ! Utilise un nombre.")
                continue

            if not 0 <= col <= 9:
                print("Colonne hors de la grille !")
                continue

            row = ord(ligne) - ord("A")
            return row, col
