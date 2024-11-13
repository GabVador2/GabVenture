import pygame
class Audio():
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        self.BVNS = pygame.mixer.Sound("audio/Bienvenuev2.mp3")
        self.MBS = pygame.mixer.Sound("audio/mMainBackSounds.mp3")
        self.sons_en_cours = {"BVNS": False, "MBS": False}
    def jouer_son(self, son, nom):
        if self.est_joue(f"{nom}") == False:
            try: son.play(); self.sons_en_cours[nom] = True
            except Exception as e: print(f"la musique {nom} ne s'est pas lancer: {e}")
    def est_joue(self, nom): return self.sons_en_cours[nom]
    def mettre_a_jour_etat(self):
        for nom, en_cours in self.sons_en_cours.items():
            if en_cours and not pygame.mixer.get_busy(): self.sons_en_cours[nom] = False   