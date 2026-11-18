from bataille_navalle.partie import Partie
from bataille_navalle.player import Player


def choisir_difficulte():
    while True:
        print("\n=== DIFFICULTÉ DE L'IA ===")
        print("1. Facile")
        print("2. Normal")
        print("3. Difficile")
        print("0. Retour au menu")

        choix = input("\nChoix : ").strip()

        difficultes = {"1": "facile", "2": "normal", "3": "difficile"}

        if choix == "0":
            return None

        if choix in difficultes:
            return difficultes[choix]

        print("Choix invalide.")


def afficher_regles():
    print("\n" + "=" * 45)
    print("RÈGLES DE LA BATAILLE NAVALE")
    print("=" * 45)

    print("""
Chaque joueur possède 5 bateaux :
- 1 bateau de 5 cases
- 1 bateau de 4 cases
- 2 bateaux de 3 cases
- 1 bateau de 2 cases

Les bateaux sont placés horizontalement
ou verticalement.

Les joueurs tirent chacun leur tour.

Résultats possibles :
- À l'eau : aucun bateau touché
- Touché : un bateau a été atteint
- Coulé : toutes ses cases sont touchées

Le premier joueur qui coule tous
les bateaux adverses gagne.

Pendant le placement :
- H : horizontal
- V : vertical
- ANNULER : retirer le dernier bateau

Les coordonnées utilisent une lettre
et un nombre, par exemple C5.
""")

    input("Appuie sur Entrée pour revenir...")


def main():
    while True:
        print("\n" + "=" * 45)
        print("         BATAILLE NAVALE")
        print("=" * 45)

        print("1. Nouvelle partie")
        print("2. Règles du jeu")
        print("0. Quitter")

        choix = input("\nTon choix : ").strip()

        if choix == "1":
            difficulte = choisir_difficulte()

            if difficulte is None:
                continue

            humain = Player("Joueur 1", is_computer=False)

            ordinateur = Player("Ordinateur", is_computer=True, difficulty=difficulte)

            partie = Partie(humain, ordinateur)

            partie.play()

            input("\nAppuie sur Entrée pour revenir au menu...")

        elif choix == "2":
            afficher_regles()

        elif choix == "0":
            print("\nMerci d'avoir joué !")
            break

        else:
            print("Choix invalide.")


if __name__ == "__main__":
    main()
