import pygame
import json
import os
from perlin_noise import PerlinNoise

# Initialiser Pygame et le mode vidéo
pygame.init()
SCREEN_WIDTH, SCREEN_HEIGHT = 1920, 1000  # Taille de la fenêtre
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Procedural Map")

# Paramètres de la carte
MAP_WIDTH = 300  # Nombre de tuiles en largeur
MAP_HEIGHT = 300  # Nombre de tuiles en hauteur
TILE_SIZE = 16  # Taille de chaque tuile en pixels

# Charger les images de tuiles
tile_images = {
    "water": pygame.image.load('textures/water.jpg').convert_alpha(),
    "grass": pygame.image.load('textures/grass.jpg').convert_alpha(),
    "mountain": pygame.image.load('textures/mountain.jpg').convert_alpha(),
    "sand": pygame.image.load('textures/sand.jpg').convert_alpha()
}
# Définir les tuiles avec collision
collision_tiles = ["water"]

# Définir le type de tuile en fonction de la valeur de bruit
def get_tile_type(value):
    if value < -0.3:
        return "water"
    elif value < 0:
        return "sand"
    elif value < 0.3:
        return "grass"
    elif value < 0.7:
        return "mountain"
    else:
        return "grass"

# Générer la carte procédurale
def generate_procedural_map(width, height, tile_size):
    map_data = []
    noise = PerlinNoise(octaves=32)
    for y in range(height):
        for x in range(width):
            value = noise([x / width, y / height])
            tile_type = get_tile_type(value)
            map_data.append({"x": x, "y": y, "type": tile_type})
    return map_data

# Sauvegarder la carte en JSON
def save_map_to_json(map_data, filename):
    with open(filename, 'w') as json_file:
        json.dump(map_data, json_file, indent=4)
    print(f"Map data saved to '{filename}'")

# Charger la carte depuis JSON
def load_map_from_json(filename):
    with open(filename, 'r') as json_file:
        return json.load(json_file)

# Vérifier si le fichier de carte existe
map_filename = 'procedural_map.json'
if not os.path.exists(map_filename):
    map_data = generate_procedural_map(MAP_WIDTH, MAP_HEIGHT, TILE_SIZE)
    save_map_to_json(map_data, map_filename)
else:
    map_data = load_map_from_json(map_filename)

# Créer une surface de carte
map_surface = pygame.Surface((MAP_WIDTH * TILE_SIZE, MAP_HEIGHT * TILE_SIZE))

# Dessiner les tuiles sur la surface
collision_rects = []
for tile in map_data:
    x, y = tile["x"], tile["y"]
    tile_type = tile["type"]
    tile_image = tile_images[tile_type]
    map_surface.blit(tile_image, (x * TILE_SIZE, y * TILE_SIZE))
    if tile_type in collision_tiles:
        collision_rects.append(pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE))

class Camera:
    def __init__(self, width, height):
        self.camera = pygame.Rect(0, 0, width, height)
        self.width = width
        self.height = height

    def apply(self, entity):
        if isinstance(entity, pygame.Rect):
            return entity.move(self.camera.topleft)
        else:
            return entity.rect.move(self.camera.topleft)

    def update(self, target):
        x = -target.rect.centerx + int(SCREEN_WIDTH / 2)
        y = -target.rect.centery + int(SCREEN_HEIGHT / 2)
        x = min(0, x)  # Left edge
        y = min(0, y)  # Top edge
        x = max(-(self.width - SCREEN_WIDTH), x)  # Right edge
        y = max(-(self.height - SCREEN_HEIGHT), y)  # Bottom edge
        self.camera = pygame.Rect(x, y, self.width, self.height)

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((TILE_SIZE, TILE_SIZE))
        self.image.fill((255, 0, 0))
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

    def update(self, keys, collision_rects):
        dx, dy = 0, 0
        if keys[pygame.K_LEFT]:
            dx = -2.5
        if keys[pygame.K_RIGHT]:
            dx = 2.5
        if keys[pygame.K_UP]:
            dy = -2.5
        if keys[pygame.K_DOWN]:
            dy = 2.5

        # Mise à jour de la position avec gestion des collisions
        self.rect.x += dx
        for rect in collision_rects:
            if self.rect.colliderect(rect):
                if dx > 0:
                    self.rect.right = rect.left
                if dx < 0:
                    self.rect.left = rect.right

        self.rect.y += dy
        for rect in collision_rects:
            if self.rect.colliderect(rect):
                if dy > 0:
                    self.rect.bottom = rect.top
                if dy < 0:
                    self.rect.top = rect.bottom

player = Player(MAP_WIDTH * TILE_SIZE // 2, MAP_HEIGHT * TILE_SIZE // 2)
camera = Camera(MAP_WIDTH * TILE_SIZE, MAP_HEIGHT * TILE_SIZE)

# Créer un groupe de sprites et ajouter le joueur
all_sprites = pygame.sprite.Group()
all_sprites.add(player)

# Boucle principale du jeu
running = True
clock = pygame.time.Clock()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    player.update(keys, collision_rects)
    camera.update(player)

    screen.fill((0, 0, 0))
    screen.blit(map_surface, camera.apply(pygame.Rect(0, 0, MAP_WIDTH * TILE_SIZE, MAP_HEIGHT * TILE_SIZE)).topleft)

    for entity in all_sprites:
        screen.blit(entity.image, camera.apply(entity))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()