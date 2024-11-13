import pygame
import json
pygame.display.set_mode()
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, w, h, t, playerspeed):
        super().__init__()
        self.sprite_sheet = pygame.image.load("textures\player.png").convert_alpha()
        self.sprite_sheet.set_colorkey((255, 255, 255))
        self.image = self.get_image(0, 0)
        self.rect = self.image.get_rect()
        self.playerspeed = playerspeed
        self.MAP_WIDTH = w
        self.MAP_HEIGHT = h
        self.PLAYER_SIZE = t
        self.image = pygame.Surface((self.PLAYER_SIZE, self.PLAYER_SIZE))
        self.image.fill((255, 0, 0))
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.load_key_configuration()
        self.keys = {
            'left': self.key_q,
            'right': self.key_d,
            'up': self.key_z,
            'down': self.key_s
        }
        self.images = {
            "up": self.get_image(0, 384),
            "down": self.get_image(0, 0),
            "right": self.get_image(0, 256),
            "left": self.get_image(0, 128)
        }
        self.image = self.images["up"]
    def save_key_configuration(self):
        key_config = {
            "key_ESCAPE": self.key_ESCAPE,
            "key_z": self.key_z,
            "key_q": self.key_q,
            "key_d": self.key_d,
            "key_s": self.key_s,
            "key_Inventory": self.key_Inventory
        }
        with open('save\general\key_config.json', 'w') as f:
            json.dump(key_config, f)
    def load_key_configuration(self):
        try:
            with open('save\general\key_config.json', 'r') as f:
                print("les key ont bien été chargé, Super!")
                key_config = json.load(f)
                self.key_ESCAPE = key_config.get("key_ESCAPE")
                self.key_z = key_config.get("key_z")
                self.key_q = key_config.get("key_q")
                self.key_d = key_config.get("key_d")
                self.key_s = key_config.get("key_s")
                self.key_Inventory = key_config.get("key_Inventory")
        except FileNotFoundError:
            self.key_ESCAPE = pygame.K_ESCAPE
            self.key_z = pygame.K_z
            self.key_q = pygame.K_q
            self.key_d = pygame.K_d
            self.key_s = pygame.K_s
            self.key_Inventory = pygame.K_e
            self.save_key_configuration()
            print("les Key vienne d'étre mis en place")
    def update(self, collision_rects):
        orikey = pygame.key.get_pressed()
        with open('save\general\key_config.json', 'r') as f:
            dx, dy = 0, 0
            key_config = json.load(f)
            if orikey[pygame.K_LEFT] or orikey[key_config.get("key_q", pygame.K_q)]: dx = -self.playerspeed; self.image = self.images["left"]
            if orikey[pygame.K_RIGHT] or orikey[key_config.get("key_d", pygame.K_d)]: dx = self.playerspeed; self.image = self.images["right"]
            if orikey[pygame.K_UP] or orikey[key_config.get("key_z", pygame.K_z)]: dy = -self.playerspeed; self.image = self.images["up"]
            if orikey[pygame.K_DOWN] or orikey[key_config.get("key_s", pygame.K_s)]: dy = self.playerspeed; self.image = self.images["down"]

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
                if self.image == self.images["up"]:
                    print("graou")
                    if dy > 0:
                        self.rect.bottom = rect.top
                    if dy < 0:
                        self.rect.top = rect.bottom
    def get_image(self, x, y):
        image = pygame.Surface([128, 128])
        image.set_colorkey((0, 0, 0))
        image.blit(self.sprite_sheet, (0, 0), (x, y, 128, 128))
        return image
    def get(self):
        self.image = self.images["down"]
        return self.image

class Camera:
    def __init__(self, width, height): self.camera = pygame.Rect(0, 0, width, height); self.widthm = width; self.heightm = height; screen_info = pygame.display.Info(); self.WIDTH, self.HEIGHT = screen_info.current_w, screen_info.current_h
    def apply(self, entity):
        if isinstance(entity, pygame.Rect): return entity.move(self.camera.topleft)
        else: return entity.rect.move(self.camera.topleft)

    def update(self, target):
        x = -target.rect.centerx + int(self.WIDTH / 2); x = min(0, x); x = max(-(self.widthm - self.WIDTH), x)
        y = -target.rect.centery + int(self.HEIGHT / 2); y = min(0, y); y = max(-(self.heightm - self.HEIGHT), y)
        self.camera = pygame.Rect(x, y, self.widthm, self.heightm)
    def get_offset(self):
        return self.camera.topleft