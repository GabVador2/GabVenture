import pygame
import os
import sys
from game import Game

# Ouvrir un fichier de log pour les erreurs

# Gérer les chemins de manière correcte
script_dir = os.path.dirname(os.path.abspath(__file__))

os.chdir(script_dir)

if __name__ == '__main__':
    try:
        pygame.init()
        pygame.mixer.init()
        myGame = Game()
        myGame.run()
    except Exception as e:
        print(f"Erreur lors du lancement du jeu: {e}")