class Water:
    def __init__(self):
        self.touched = False

    def shoot(self):
        if self.touched:
            return "Déjà tiré"

        self.touched = True
        return "À l'eau"
