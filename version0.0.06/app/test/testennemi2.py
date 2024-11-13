import pygame
import random
import math

# Initialiser Pygame
pygame.init()

# Dimensions de la fenêtre
screen_width, screen_height = 800, 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Jeu de Tir avec Ennemis")

# Couleurs
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)

# Limite du nombre d'ennemis sur la carte
MAX_ENEMIES = 10  # Nombre maximal d'ennemis en même temps
FOLLOW_RANGE = 200  # Champ d'action des ennemis
AVOIDANCE_DISTANCE = 30  # Distance d'évitement entre ennemis

# Classe pour le joueur
class Player:
    def __init__(self):
        self.x = screen_width // 2
        self.y = screen_height // 2
        self.speed = 5
        self.size = 20
        self.health = 100
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
        current_time = pygame.time.get_ticks()
        return current_time - self.last_shot > self.cooldown

# Classe pour un projectile
class Projectile:
    def __init__(self, x, y, direction, speed=10, color=BLACK):
        self.x = x
        self.y = y
        self.size = 5
        self.color = color
        self.speed = speed
        self.direction = direction

    def move(self):
        self.x += self.direction[0] * self.speed
        self.y += self.direction[1] * self.speed

    def draw(self):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.size)

    def is_off_screen(self):
        return self.x < 0 or self.x > screen_width or self.y < 0 or self.y > screen_height

# Classe de base pour les ennemis
class Enemy:
    def __init__(self, x, y, color, health=100):
        self.x = x
        self.y = y
        self.color = color
        self.health = health
        self.max_health = health
        self.size = 20
        self.speed = 2

    def draw(self):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.size)
        self.draw_health_bar()

    def draw_health_bar(self):
        bar_width = 40
        bar_height = 5
        health_ratio = self.health / self.max_health
        pygame.draw.rect(screen, RED, (self.x - bar_width / 2, self.y - self.size - 10, bar_width, bar_height))
        pygame.draw.rect(screen, GREEN, (self.x - bar_width / 2, self.y - self.size - 10, bar_width * health_ratio, bar_height))

# Classe pour le combattant
class Fighter(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y, RED)
        self.attack_range = 30

    def follow(self, player, enemies):
        dx = player.x - self.x
        dy = player.y - self.y
        distance = math.hypot(dx, dy)

        if distance <= FOLLOW_RANGE:  # Suivre uniquement si dans le champ d'action
            if distance > self.attack_range:
                if distance != 0:
                    dx /= distance
                    dy /= distance

                # Éviter le chevauchement avec d'autres ennemis
                for enemy in enemies:
                    if enemy != self and check_collision(self, enemy):
                        # Détourner l'ennemi
                        self.avoid_enemy(enemy)

                # Avancer vers le joueur
                self.x += dx * self.speed
                self.y += dy * self.speed

    def avoid_enemy(self, enemy):
        # Calculer la direction pour éviter l'ennemi
        dx = self.x - enemy.x
        dy = self.y - enemy.y
        distance = math.hypot(dx, dy)

        if distance < AVOIDANCE_DISTANCE:  # Si l'ennemi est trop proche
            # Réculez légèrement
            self.x += dx / distance * self.speed
            self.y += dy / distance * self.speed

            # Déplacez-vous latéralement pour éviter l'ennemi
            if abs(dx) > abs(dy):
                self.x += AVOIDANCE_DISTANCE * (1 if dx > 0 else -1)  # Déplacement sur le côté
            else:
                self.y += AVOIDANCE_DISTANCE * (1 if dy > 0 else -1)  # Déplacement sur le côté

# Classe pour l'archer
class Archer(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y, BLUE)
        self.shoot_cooldown = 1000  # Cooldown entre les tirs
        self.last_shot = pygame.time.get_ticks()
        self.projectiles = []

    def follow(self, player, enemies):
        dx = player.x - self.x
        dy = player.y - self.y
        distance = math.hypot(dx, dy)

        if distance > 150:  # Garder une certaine distance
            if distance != 0:
                dx /= distance
                dy /= distance

            # Éviter les collisions avec d'autres ennemis
            for enemy in enemies:
                if enemy != self and check_collision(self, enemy):
                    self.avoid_enemy(enemy)

            # Avancer vers le joueur
            self.x += dx * self.speed
            self.y += dy * self.speed
        else:
            # Tirez si possible
            if self.can_shoot():
                direction = (dx / distance, dy / distance)
                projectile = Projectile(self.x, self.y, direction, speed=5, color=RED)
                self.projectiles.append(projectile)

    def avoid_enemy(self, enemy):
        # Logique de décalage
        dx = self.x - enemy.x
        dy = self.y - enemy.y
        distance = math.hypot(dx, dy)

        if distance < AVOIDANCE_DISTANCE:  # Si l'ennemi est trop proche
            # Réculez légèrement
            self.x += dx / distance * self.speed
            self.y += dy / distance * self.speed

            # Déplacez-vous latéralement pour éviter l'ennemi
            if abs(dx) > abs(dy):
                self.x += AVOIDANCE_DISTANCE * (1 if dx > 0 else -1)  # Déplacement sur le côté
            else:
                self.y += AVOIDANCE_DISTANCE * (1 if dy > 0 else -1)  # Déplacement sur le côté

    def can_shoot(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_shot > self.shoot_cooldown:
            self.last_shot = current_time
            return True
        return False

    def draw(self):
        super().draw()
        for projectile in self.projectiles[:]:
            projectile.move()
            projectile.draw()

# Fonction pour vérifier les collisions
def check_collision(obj1, obj2):
    distance = math.hypot(obj1.x - obj2.x, obj1.y - obj2.y)
    return distance < obj1.size + obj2.size
def calculate_direction(start_x, start_y, target_x, target_y):
    dx = target_x - start_x
    dy = target_y - start_y
    distance = math.hypot(dx, dy)
    if distance == 0:
        return (0, 0)  # No movement if the distance is zero
    return (dx / distance, dy / distance)
# Créer un ennemi loin du joueur
def create_enemy_away_from_player(player, enemy_type):
    while True:
        angle = random.uniform(0, 2 * math.pi)
        distance = random.randint(150, 300)
        x = int(player.x + math.cos(angle) * distance)
        y = int(player.y + math.sin(angle) * distance)

        if 0 < x < screen_width and 0 < y < screen_height:
            if enemy_type == "fighter":
                return Fighter(x, y)
            elif enemy_type == "archer":
                return Archer(x, y)

# Boucle principale du jeu
def game_loop():
    clock = pygame.time.Clock()
    player = Player()
    enemies = []
    projectiles = []

    # Apparition des ennemis
    for _ in range(MAX_ENEMIES):
        enemy_type = random.choice(["fighter", "archer"])
        enemy = create_enemy_away_from_player(player, enemy_type)
        enemies.append(enemy)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if player.can_shoot():
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    direction = calculate_direction(player.x, player.y, mouse_x, mouse_y)
                    projectile = Projectile(player.x, player.y, direction, speed=10, color=BLACK)
                    projectiles.append(projectile)

        player.move()

        # Gérer le comportement des ennemis
        for enemy in enemies:
            if isinstance(enemy, Fighter):
                enemy.follow(player, enemies)
            elif isinstance(enemy, Archer):
                enemy.follow(player, enemies)

            # Gérer les projectiles de l'archer
            if isinstance(enemy, Archer):
                for projectile in enemy.projectiles[:]:
                    projectile.move()
                    if check_collision(projectile, player):
                        player.health -= 10  # Perte de vie du joueur
                        enemy.projectiles.remove(projectile)
                    if projectile.is_off_screen():
                        enemy.projectiles.remove(projectile)

        # Vérification des collisions entre le joueur et les ennemis
        for enemy in enemies:
            if check_collision(player, enemy):
                player.health -= 1  # Perte de vie du joueur

        # Mise à jour des projectiles du joueur
        for projectile in projectiles[:]:
            projectile.move()

            # Vérification des collisions avec les ennemis
            for enemy in enemies[:]:
                if check_collision(projectile, enemy):
                    enemy.health -= 10
                    if enemy.health <= 0:
                        enemies.remove(enemy)
                    projectiles.remove(projectile)
                    break

            if projectile.is_off_screen():
                projectiles.remove(projectile)

        # Affichage
        screen.fill(WHITE)
        player.draw()
        for enemy in enemies:
            enemy.draw()
        for projectile in projectiles:
            projectile.draw()

        # Afficher la vie du joueur
        health_text = f"Vie: {player.health}"
        font = pygame.font.Font(None, 36)
        text_surface = font.render(health_text, True, BLACK)
        screen.blit(text_surface, (10, 10))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

# Démarrer le jeu
game_loop()
