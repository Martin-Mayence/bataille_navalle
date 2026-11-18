class Boat:
    def __init__(self, size):
        if size <= 0:
            raise ValueError("La taille du bateau doit être supérieure à zéro")
        self.size = size
        self.positions = []
        self.hits = set()

    def place(self, positions):
        if len(positions) != self.size:
            raise ValueError("Taille incorrecte")
        self.positions = positions

    def shoot(self, position):
        if position not in self.positions:
            return "À l'eau"

        if position in self.hits:
            return "Déjà tiré"

        self.hits.add(position)

        if self.is_sunk():
            return "Coulé"

        return "Touché"

    def is_sunk(self):
        return len(self.hits) == self.size
