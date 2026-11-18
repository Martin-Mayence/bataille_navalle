from bataille_navalle.partie import Partie
from bataille_navalle.player import Player


def main():
    humain = Player("Joueur 1")
    ordinateur = Player("Ordinateur", is_computer=True)

    partie = Partie(humain, ordinateur)
    partie.play()


if __name__ == "__main__":
    main()
