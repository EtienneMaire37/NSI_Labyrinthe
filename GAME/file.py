class File:
    def __init__(self):
        self.contenu = []

    def est_vide(self):
        return self.contenu == []

    def enfiler(self,x):
        self.contenu.append(x)

    def defiler(self):
        if not self.est_vide():
            return self.contenu.pop(0)
        else:
            print("File vide !")

    def taille(self):
        return len(self.contenu)

    def sommet(self):
        if not self.est_vide():
            return self.contenu[0]
        else:
            print("File vide !")
