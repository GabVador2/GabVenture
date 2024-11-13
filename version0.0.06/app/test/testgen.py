import pygame
import random

# Initialisation de Pygame
pygame.init()

# Dimensions de la fenêtre
largeur_fenetre = 800
hauteur_fenetre = 800
taille_tuile = 40  # Taille de chaque tuile en pixels

# Définition des biomes et de leurs caractéristiques
biomes = {
    "forêt": {"couleur": (0, 128, 0), "éléments": ["arbres", "fleurs"]},
    "désert": {"couleur": (255, 255, 0), "éléments": ["sables", "cactus"]},
    "montagnes": {"couleur": (128, 128, 128), "éléments": ["rochers", "neige"]},
}

# Fonction pour générer une carte aléatoire
def generer_carte(taille_x, taille_y):
    carte = []
    for y in range(taille_y):
        ligne = []
        for x in range(taille_x):
            biome = random.choice(list(biomes.keys()))
            ligne.append(biome)
        carte.append(ligne)
    return carte

# Fonction pour dessiner la carte
def dessiner_carte(carte):
    for y, ligne in enumerate(carte):
        for x, biome in enumerate(ligne):
            couleur = biomes[biome]["couleur"]
            pygame.draw.rect(fenetre, couleur, (x * taille_tuile, y * taille_tuile, taille_tuile, taille_tuile))

# Création de la fenêtre
fenetre = pygame.display.set_mode((largeur_fenetre, hauteur_fenetre))
pygame.display.set_caption("Générateur de Carte")

# Génération de la carte
taille_x = largeur_fenetre // taille_tuile
taille_y = hauteur_fenetre // taille_tuile
carte = generer_carte(taille_x, taille_y)

# Boucle principale
en_cours = True
while en_cours:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            en_cours = False

    # Dessiner la carte
    fenetre.fill((0, 0, 0))  # Remplir l'arrière-plan en noir
    dessiner_carte(carte)
    pygame.display.flip()  # Mettre à jour l'affichage

# Quitter Pygame
pygame.quit()