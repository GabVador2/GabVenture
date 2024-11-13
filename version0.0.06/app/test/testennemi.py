
import pygame
import random
import math

# Initialiser Pygame
pygame.init()

# Dimensions de la fenêtre de jeu
screen_width, screen_height = 800, 600
screen = pygame.display.set_mode((screen_width, screen_height))

# Couleurs prédéfinies pour les ennemis
COLORS = [(255, 0, 0), (0, 0, 255), (255, 255, 0), (0, 255, 255), (255, 0, 255)]
RED = (255, 0, 0)
GREEN = (0, 255, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Classe pour le joueur
class Player:
    def __init__(self):
        self.x = screen_width // 2
        self.y = screen_height // 2
        self.speed = 5
        self.size = 20  # Rayon du joueur
        self.cooldown = 500  # Cooldown entre les tirs (en millisecondes)
        self.last_shot = pygame.time.get_ticks()

    def move(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.x - self.size > 0:
            self.x -= self.speed
        if keys[pygame.K_RIGHT] and self.x + self.size < screen_width:
            self.x += self.speed
        if keys[pygame.K_UP] and self.y - self.size > 0:
            self.y -= self.speed
        if keys[pygame.K_DOWN] and self.y + self.size < screen_height:
            self.y += self.speed

    def draw(self):
        pygame.draw.circle(screen, GREEN, (self.x, self.y), self.size)

    def can_shoot(self):
        """Vérifie si le joueur peut tirer en fonction du cooldown"""
        current_time = pygame.time.get_ticks()
        if current_time - self.last_shot > self.cooldown:
            self.last_shot = current_time
            return True
        return False

# Classe pour un projectile
class Projectile:
    def __init__(self, x, y, direction):
        self.x = x
        self.y = y
        self.size = 5  # Taille du projectile
        self.color = BLACK
        self.speed = 10  # Vitesse du projectile
        self.direction = direction  # Direction du tir (tuple dx, dy)

    def move(self):
        # Mouvement du projectile dans la direction spécifiée
        self.x += self.direction[0] * self.speed
        self.y += self.direction[1] * self.speed

    def draw(self):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.size)

    def is_off_screen(self):
        # Vérifier si le projectile est hors de l'écran
        return self.x < 0 or self.x > screen_width or self.y < 0 or self.y > screen_height

# Classe pour l'ennemi
class Enemy:
    def __init__(self, x, y, color, health=100):
        self.x = x
        self.y = y
        self.color = color  # Couleur aléatoire
        self.health = health  # Santé initiale de l'ennemi
        self.max_health = health
        self.speed = 2
        self.size = 20  # Rayon de l'ennemi
        self.dx = 0
        self.dy = 0

    def follow(self, player):
        # Calcul de la direction de l'ennemi vers le joueur
        dx = player.x - self.x
        dy = player.y - self.y
        distance = math.hypot(dx, dy)
        if distance != 0:
            dx /= distance
            dy /= distance

        # Mouvement de l'ennemi vers le joueur
        self.dx = dx * self.speed
        self.dy = dy * self.speed

        self.x += self.dx
        self.y += self.dy

    def avoid(self, other_enemy):
        """Décaler l'ennemi pour éviter d'autres ennemis devant lui"""
        dx = other_enemy.x - self.x
        dy = other_enemy.y - self.y
        distance = math.hypot(dx, dy)

        # Si un autre ennemi est proche, ajouter une force de répulsion
        if distance < self.size * 2:
            # Ajouter une force de répulsion
            self.x -= dx * 0.05  # Ajuster la force de répulsion
            self.y -= dy * 0.05  # Ajuster la force de répulsion

    def draw(self):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.size)
        self.draw_health_bar()

    def draw_health_bar(self):
        """Dessine la barre de vie de l'ennemi au-dessus de lui"""
        bar_width = 40
        bar_height = 5
        health_ratio = self.health / self.max_health
        pygame.draw.rect(screen, RED, (self.x - bar_width / 2, self.y - self.size - 10, bar_width, bar_height))
        pygame.draw.rect(screen, GREEN, (self.x - bar_width / 2, self.y - self.size - 10, bar_width * health_ratio, bar_height))

# Fonction pour vérifier les collisions entre deux objets
def check_collision(obj1, obj2):
    distance = math.hypot(obj1.x - obj2.x, obj1.y - obj2.y)
    if distance < obj1.size + obj2.size:
        return True
    return False

# Fonction pour créer un ennemi à une position aléatoire mais loin du joueur
def create_enemy_away_from_player(player, min_distance=100):
    while True:
        # Générer des coordonnées aléatoires autour du joueur
        angle = random.uniform(0, 2 * math.pi)
        distance = random.randint(min_distance, min_distance + 200)  # Distance aléatoire autour du joueur
        x = int(player.x + math.cos(angle) * distance)
        y = int(player.y + math.sin(angle) * distance)
        
        # Vérifier que les coordonnées sont bien dans les limites de l'écran
        if 0 < x < screen_width and 0 < y < screen_height:
            color = random.choice(COLORS)
            return Enemy(x, y, color)

# Fonction pour calculer la direction du tir en fonction de la position du joueur et de la souris
def calculate_direction(player_x, player_y, mouse_x, mouse_y):
    dx = mouse_x - player_x
    dy = mouse_y - player_y
    distance = math.hypot(dx, dy)
    if distance != 0:
        dx /= distance
        dy /= distance
    return dx, dy

# Boucle principale du jeu
def game_loop():
    player = Player()

    # Liste des projectiles
    projectiles = []

    # Générer un nombre aléatoire d'ennemis (entre 5 et 10)
    num_enemies = random.randint(5, 10)
    enemies = [create_enemy_away_from_player(player) for _ in range(num_enemies)]

    # Timer pour l'apparition des ennemis
    enemy_spawn_interval = 7000  # Temps en millisecondes entre les apparitions
    last_enemy_spawn_time = pygame.time.get_ticks()

    clock = pygame.time.Clock()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Déplacer le joueur
        player.move()

        # Tirer un projectile si le bouton gauche de la souris est pressé
        mouse_pressed = pygame.mouse.get_pressed()
        if mouse_pressed[0] and player.can_shoot():
            # Obtenir la position de la souris
            mouse_x, mouse_y = pygame.mouse.get_pos()
            # Calculer la direction du projectile en fonction de la souris
            direction = calculate_direction(player.x, player.y, mouse_x, mouse_y)
            # Créer un projectile
            projectile = Projectile(player.x, player.y, direction)
            projectiles.append(projectile)

        # Remplir l'écran avec une couleur de fond
        screen.fill(WHITE)

        # Afficher le joueur
        player.draw()

        # Déplacer et afficher les projectiles
        for projectile in projectiles[:]:
            projectile.move()
            projectile.draw()

            # Vérifier si le projectile est hors écran
            if projectile.is_off_screen():
                projectiles.remove(projectile)

            # Vérifier les collisions avec les ennemis
            for enemy in enemies[:]:
                if check_collision(projectile, enemy):
                    enemy.health -= 20  # Réduire la santé de l'ennemi
                    if enemy.health <= 0:
                        enemies.remove(enemy)
                    projectiles.remove(projectile)
                    break  # Quitter la boucle après la collision

        # Vérifier si c'est le moment de faire apparaître un nouvel ennemi
        current_time = pygame.time.get_ticks()
        if current_time - last_enemy_spawn_time > enemy_spawn_interval:
            new_enemy = create_enemy_away_from_player(player)
            enemies.append(new_enemy)
            last_enemy_spawn_time = current_time

        # Déplacer et afficher les ennemis
        for enemy in enemies:
            enemy.follow(player)
            # Vérifier si l'ennemi doit éviter un autre ennemi
            for other_enemy in enemies:
                if enemy != other_enemy:
                    enemy.avoid(other_enemy)
            enemy.draw()

        # Mettre à jour l'affichage
        pygame.display.flip()

        # Contrôler le framerate
        clock.tick(60)

# Lancer le jeu
game_loop()
pygame.quit()
