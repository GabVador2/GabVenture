import pygame
import sys
import os
import json
import time
import stat
import random
import shutil
import threading
from pygame.locals import *
from audio import Audio
from player import Player, Camera
try:
    from perlin_noise import PerlinNoise
except:
    print(f"Perlin-noise n'est pas installer\nFaite pip install perlin-noise dans l'invite de commande")
pygame.mixer.init()
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRIS = (160, 160, 160)
BLUE = (0, 0, 255)
SILVER = (192, 192, 192)
GOLD = (255, 215, 0)
ORANGE = (255, 128, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
all_sprites = pygame.sprite.Group()

class Game(Player):
    def __init__(self):
        self.CHUNK_SIZE = 16
        self.nowsave = f""
        self.addsave = False
        self.collision_rects2 = []
        self.selectslotHotB = (0, "none")
        self.audio_instance = Audio()
        self.audio_instance.jouer_son(self.audio_instance.BVNS, "BVNS")
        self.save = {}
        self.clock = pygame.time.Clock()
        self.frame_count = 0
        self.fps = 0
        self.loadsavegenerals()
        self.playerspeed = 2.2
        self.MAP_WIDTH = 200  # Nombre de tuiles en largeur
        self.MAP_HEIGHT = 200  # Nombre de tuiles en hauteur
        self.TILE_SIZE = 64 # Taille de chaque tuile en pixels
        self.PLAYER_SIZE = 128
        super().__init__(self.MAP_WIDTH * self.TILE_SIZE // 2, self.MAP_HEIGHT * self.TILE_SIZE // 2, self.MAP_WIDTH, self.MAP_HEIGHT, self.PLAYER_SIZE, self.playerspeed)
        self.settingsofpause = False
        screen_info = pygame.display.Info()
        self.WIDTH, self.HEIGHT = screen_info.current_w, screen_info.current_h
        self.player = Player(self.MAP_WIDTH * self.TILE_SIZE // 2, self.MAP_HEIGHT * self.TILE_SIZE // 2, self.MAP_WIDTH, self.MAP_HEIGHT, self.PLAYER_SIZE, self.playerspeed)
        self.Audio = Audio()
        self.camera = Camera(self.MAP_WIDTH * self.TILE_SIZE, self.MAP_HEIGHT * self.TILE_SIZE)
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT), pygame.RESIZABLE)
        self.Inventory_open = False
        self.all_sprites = pygame.sprite.Group()
        # Affichage de la fenêtre
        pygame.display.set_caption("Gabventure")
        # Générer le joeur

        self.background = pygame.image.load("textures\mbackground.jpg").convert()  # Charger l'image de fond
        self.background = pygame.transform.scale(self.background, self.screen.get_size())
        self.wood_image = pygame.image.load("textures\WOOD.jpg").convert()
        self.wood_image.set_colorkey((255, 255, 255))
        self.ROCK_image = pygame.image.load("textures\ROCK.jpg").convert()
        self.ROCK_image.set_colorkey((255, 255, 255))
        self.wood_pickaxe_image = pygame.image.load("textures\wood_pickaxe.jpg").convert()
        self.wood_pickaxe_image.set_colorkey((255, 255, 255))
        self.raw_iron_image = pygame.image.load("textures\RAW_IRON.jpg").convert()
        self.raw_iron_image.set_colorkey((255, 255, 255))
        self.raw_gold_image = pygame.image.load("textures\RAW_GOLD.jpg").convert()
        self.raw_gold_image.set_colorkey((255, 255, 255))
        self.ITEMS = {
            "WHITE": (255, 255, 255),
            "BLACK": (0, 0, 0),
            "GRIS": (160, 160, 160),
            "BLUE": (0, 0, 255),
            "SILVER": (192, 192, 192),
            "GOLD": (255, 215, 0),
            "GREEN": (0, 255, 0),
            "RED": (255, 0, 0),
            "WOOD": self.wood_image,
            "ROCK": self.ROCK_image,
            "WOOD_PICKAXE": self.wood_pickaxe_image,
            "RAW_IRON": self.raw_iron_image,
            "RAW_GOLD": self.raw_gold_image,
        }
        self.Inventory = {}
        self.HotB = {}
        self.saveb_t = {}
        self.saveb_r = {}
        self.settingsback = pygame.image.load("textures\settingsback.jpg").convert()  # Charger l'image de fond
        self.settingsback = pygame.transform.scale(self.settingsback, self.screen.get_size())
        width, height = self.settingsback.get_size()
        for x in range(width):
            for y in range(height):
                r, g, b, a = self.settingsback.get_at((x, y))
                if r > 200 and g > 200 and b > 200:
                    self.settingsback.set_at((x, y), (255, 255, 255, 0))
        self.Inventory_hand = False
        self.selected_item = None
        self.selected_item_index = None
        self.selected_item_pos = None
        self.quantity_item = 0
        self.quantitytoremove_item = 0
        self.changefonttextKEsc = False
        self.changefonttextKz = False
        self.changefonttextKq = False
        self.changefonttextKd = False
        self.changefonttextKs = False
        self.changefonttextKInv = False
        self.quantitytoremove_itemwait = False
        self.last_click_time = 0
        pygame.display.set_caption("IDK Game")

        # Charger les images de tuiles
        self.tile_images = {
            "water": pygame.image.load("textures\water.jpg").convert_alpha(),
            "grass": pygame.image.load("textures\grass.jpg").convert_alpha(),
            "mountain": pygame.image.load("textures\mountain.jpg").convert(),
            "sand": pygame.image.load("textures\sand.jpg").convert(),
            "mineraliron": pygame.image.load("textures\mineraliron.jpg").convert(),
            "mineralgold": pygame.image.load("textures\mineralgold.jpg").convert(),
            "ressourcewood": pygame.image.load("textures\\ressourcewood.jpg").convert()
        }
        self.mineral_to_inventory = {
            'mineraliron': "RAW_IRON",
            'mineralgold': "RAW_GOLD",
            'ressourcewood': "WOOD"
            }
        # Définir les tuiles avec collision
        self.collision_tiles = ["water"]
        self.change_key = ["ESCAPE", "z", "q", "d", "s", "Inventory"]
        self.key_ = ["ESCAPE", "z", "q", "d", "s", "Inventory"]
        # Créer une surface pour la carte
        self.map_surface = pygame.Surface((self.MAP_WIDTH * self.TILE_SIZE, self.MAP_HEIGHT * self.TILE_SIZE))
        self.collision_rects = []
        self.map_data = []
        self.map_filename = os.path.join(os.path.dirname(__file__), '')
        self.buttonmine = 0
    def savegenerals(self, savefordelete):
        try:
            with open('save\general\savegenerals.json', 'r') as f:
                savegeneral = json.load(f)
                savegeneral = {
                    "totalsave": self.totalsave,
                    "language": self.language,
                }
                try:
                    if savefordelete == "":
                        for sa in range(1, self.totalsave +1):
                            if sa == self.totalsave:
                                savegeneral[f"save{sa}"] = f"{self.savename}"
                                print(f" Fart Ok noms {self.savename} assigner save {sa}")
                            else:
                                with open('save\general\savegenerals.json', 'r') as a:
                                    verifsavegeneral = json.load(a)
                                    proute = verifsavegeneral.get(f"save{sa}", "No save found")
                                    savegeneral[f"save{sa}"] = proute
                                    print(f"Ok noms {proute} assigner save {sa}")
                    else:
                        try:
                            with open('save\general\savegenerals.json', 'r') as e:
                                savegeneral = json.load(e)
                                savegeneral[f"totalsave"] -= 1
                                del savegeneral[f"save{savefordelete}"]
                                print(f"delete {savefordelete}")
                            with open('save\general\savegenerals.json', 'w') as f:
                                    json.dump(savegeneral, f)
                            try:
                                for sa in range(int(savefordelete), self.totalsave + 1):
                                    with open('save\general\savegenerals.json', 'r') as a:
                                        verifsavegeneral = json.load(a)
                                        proute = verifsavegeneral.get(f"save{sa + 1}", "No save found")
                                        try:
                                            savegeneral[f"save{sa}"] = proute
                                            del savegeneral[f"save{sa + 1}"]
                                            os.rename(f"save\{sa + 1}", f"save\{sa}")
                                            os.rename(f"save\{sa}\map{sa + 1}.json", f"save\{sa}\map{sa}.json")
                                        except Exception as e:
                                            print(f"Proute le chargement des noms de save na pas fonctionner: {e}")    
                                        print(f"Ok noms {proute} assigner save {sa}")  
                            except Exception as e:
                                print(f"Caca le chargement des noms de save na pas fonctionner: {e}")                                 
                        except Exception as e:
                            print(f"2222222le chargement des noms de save na pas fonctionner: {e}")

                except Exception as e:
                    print(f"le chargement des noms de save na pas fonctionner: {e}")
            with open('save\general\savegenerals.json', 'w') as f:
                json.dump(savegeneral, f)
        except:
            savegeneral = {
                "totalsave": self.totalsave,
                "language": self.language,
            }
            with open('save\general\savegenerals.json', 'w') as f:
                json.dump((savegeneral), f, indent=4)        
    def loadsavegenerals(self):
        try:
            with open('save\general\savegenerals.json', 'r') as f:
                print("les key ont bien été chargé, Super!")
                savegeneral = json.load(f)
                self.totalsave = savegeneral.get("totalsave")
                self.language = savegeneral.get("language")
                for sa in range(0, self.totalsave):
                    self.save[sa] = savegeneral.get(f"save{sa}")
        except FileNotFoundError:
            self.totalsave = 0
            self.language = "English"
            for sa in range(0, self.totalsave):
                self.save[sa] = f"save{sa}"
            self.savegenerals("")
    def get_tile_type(self, value):
        if value < -0.3: return "water"
        elif value < 0: return "sand"
        elif value < 0.3: return "grass"
        elif value < 0.7: return "mountain"
        else: return "grass"
    def select_english(self):
        global language
        self.language = "English"

    # Sélectionner la langue française
    def select_french(self):
        global language
        self.language = "Français"
    # Générer la carte procédurale
    def generate_procedural_map(self, width, height):
        map_data = []
        noise = PerlinNoise(octaves=7)
        try:
            for y in range(height):
                for x in range(width):
                    value = noise([x / width, y / height])
                    tile_type = self.get_tile_type(value)
                    if random.randint(1, 20) == 1 and self.get_tile_type(value) == "grass":
                        if random.randint(1, 10) == 1:
                            tile_type = "mineraliron"
                        elif random.randint(1, 15) == 1:
                            tile_type = "mineralgold"
                        else: tile_type = "ressourcewood"
                    map_data.append({"x": x, "y": y, "type": tile_type})


        except: print("erreur lor de la génération de la map")
        return map_data

    # Sauvegarder la carte en JSON
    def save_map_to_json(self, map_data, filename):
        try:
            os.makedirs(os.path.dirname(filename), exist_ok=True) 
            with open(filename, 'w') as json_file:
                json.dump(map_data, json_file)
                print(f"Map data saved to '{filename}'")
        except Exception as e: print(f"Nous avons pas pu sauvegarder la map '{filename}': {e}")
        self.tileinmapdata()

    # Charger la carte depuis JSON
    def load_map_from_json(self, filename):
        with open(filename, 'r') as json_file:
            return json.load(json_file)

    # Vérifier si le fichier de carte existe et charger ou générer
    def verifmap(self, map_filename):
        if not os.path.exists(map_filename):
            self.collision_rects = []
            self.map_data = []
            print(f"la map {map_filename} n'existe pas")
            map_data = self.generate_procedural_map(self.MAP_WIDTH, self.MAP_HEIGHT)
            self.save_map_to_json(map_data, map_filename)
            self.map_data = self.load_map_from_json(map_filename) 
        else:
            self.collision_rects = []
            self.map_data = []
            self.map_data = self.load_map_from_json(map_filename)
            print("la map existe")
        self.map_surface = pygame.Surface((self.MAP_WIDTH * self.TILE_SIZE, self.MAP_HEIGHT * self.TILE_SIZE))

    # Créer une surface de carte et dessiner les tuiles
    def tileinmapdata(self):
        for tile in self.map_data:
            x, y = tile["x"], tile["y"]
            tile_type = tile["type"]
            tile_image = self.tile_images[tile_type]
            self.map_surface.blit(tile_image, (x * self.TILE_SIZE, y * self.TILE_SIZE))
            if tile_type in self.collision_tiles: self.collision_rects.append(pygame.Rect(x * self.TILE_SIZE, y * self.TILE_SIZE, self.TILE_SIZE, self.TILE_SIZE))
            rect = pygame.Rect(x * self.TILE_SIZE, y * self.TILE_SIZE, self.TILE_SIZE, self.TILE_SIZE)
            self.collision_rects2.append(rect)
    def menu_principal(self):
        menu_running = True
        self.audio_instance.jouer_son(self.audio_instance.MBS, "MBS")
        self.audio_instance.mettre_a_jour_etat()
        while menu_running:
            self.screen.fill(WHITE)
            self.screen.blit(self.background, (0, 0))
            # Affichage du menu
            font = pygame.font.Font(None, 74)
            titre = font.render("Gabventure", True, BLACK)
            self.screen.blit(titre, (self.WIDTH // 2 - titre.get_width() // 2, self.HEIGHT // 4))

            made_font = pygame.font.Font(None, 30)
            font = pygame.font.Font(None, 56)
            jouer_texte = font.render("Play", True, GREEN) if (self.language == "English") else(font.render("Jouer", True, GREEN))
            settings_texte = font.render("Settings", True, BLACK) if (self.language == "English") else(font.render("Paramètres", True, BLACK))
            quitter_texte = font.render("Leave", True, RED) if (self.language == "English") else(font.render("Quitter", True, RED))
            madeby_texte = made_font.render("Made by Gabriel Goepp", True, BLACK) if (self.language == "English") else(made_font.render("Créer par Gabriel Goepp", True, BLACK))

            # Positions des textes
            jouer_rect = jouer_texte.get_rect(center=(self.WIDTH // 2, self.HEIGHT // 2))
            settings_rect = settings_texte.get_rect(center=(self.WIDTH // 2, self.HEIGHT // 2 + 75))
            quitter_rect = quitter_texte.get_rect(center=(self.WIDTH // 2, self.HEIGHT // 2 + 150))

            # Dessiner les rectangles
            pygame.draw.rect(self.screen, BLACK, jouer_rect.inflate(20, 10), 4)  # rectangle autour de "Jouer"
            pygame.draw.rect(self.screen, BLACK, settings_rect.inflate(20, 10), 4)
            pygame.draw.rect(self.screen, BLACK, quitter_rect.inflate(20, 10), 4)  # rectangle autour de "Quitter"

            # Blit les textes
            self.screen.blit(madeby_texte, (self.WIDTH - 250, 10))
            pygame.draw.rect(self.screen, GRIS, jouer_rect.inflate(12, 2), 40); self.screen.blit(jouer_texte, jouer_rect)
            pygame.draw.rect(self.screen, GRIS, settings_rect.inflate(12, 2), 40); self.screen.blit(settings_texte, settings_rect)
            pygame.draw.rect(self.screen, GRIS, quitter_rect.inflate(12, 2), 40); self.screen.blit(quitter_texte, quitter_rect)


            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_x, mouse_y = event.pos
                    if jouer_rect.collidepoint(mouse_x, mouse_y):
                        menu_running = False  # Quitter le menu et commencer le jeu
                        self.save_menu()
                    if settings_rect.collidepoint(mouse_x, mouse_y):
                        menu_running = False  # Quitter le menu et aller dans les settings
                        self.settings_menu()
                    if quitter_rect.collidepoint(mouse_x, mouse_y):
                        pygame.quit()
                        sys.exit()
            pygame.display.flip()

    def save_menu(self):
        running = True
        self.loadsavegenerals()
        while running:
            self.screen.fill(WHITE)
            self.screen.blit(self.background, (0, 0))
            save_font = pygame.font.Font(None, 100)
            font = pygame.font.Font(None, 74)
            titre = font.render("Save Menu", True, BLACK) if (self.language == "English") else(font.render("Menu des sauvegardes", True, BLACK))
            self.screen.blit(titre, (self.WIDTH // 2 - titre.get_width() // 2, 50))
            with open('save\general\savegenerals.json', 'r') as a:
                verifsavegeneral = json.load(a)
            if self.addsave == True:
                savenametext_texte = save_font.render(f"{self.savename}", True, BLACK)
                savenametext_rect = savenametext_texte.get_rect(center=(self.WIDTH // 2, self.HEIGHT //2))
                pygame.draw.rect(self.screen, BLACK, savenametext_rect.inflate(20, 10), 4)
                pygame.draw.rect(self.screen, GRIS, savenametext_rect.inflate(18, 2), 45)
                self.screen.blit(savenametext_texte, savenametext_rect)    
            else:
                for i in range(1, self.totalsave + 1):
                    proute = verifsavegeneral.get(f"save{i}", "No save found")
                    self.saveb_t[i] = save_font.render(f"Save - {proute}", True, BLACK) if (self.language == "English") else(save_font.render(f"Sauvegarde - {proute}", True, BLACK))
                    self.saveb_r[i] = self.saveb_t[i].get_rect(center=(self.WIDTH // 2, 150 + 100 * i - 100))
                    pygame.draw.rect(self.screen, BLACK, self.saveb_r[i].inflate(150, 10), 4)
                    pygame.draw.rect(self.screen, GRIS, self.saveb_r[i].inflate(142, 2), 45)
                    self.screen.blit(self.saveb_t[i], self.saveb_r[i])
            
            addsave_texte = font.render("+", True, RED) if (self.language == "English") else(font.render("+", True, RED))
            addsave_rect = addsave_texte.get_rect(center=(self.WIDTH // 2 + titre.get_width() // 2 + 30, 70))
            pygame.draw.rect(self.screen, BLACK, addsave_rect.inflate(20, 10), 4)
            self.screen.blit(addsave_texte, addsave_rect)
            
            proute2 = verifsavegeneral.get(f"save{self.nowsave}", "No save found")
            playsave_texte = font.render(f"Play - {proute2}", True, RED) if (self.language == "English") else(font.render(f"Jouer - {proute2}", True, RED))
            playsave_rect = playsave_texte.get_rect(center=(self.WIDTH // 1.2, self.HEIGHT - 150))
            pygame.draw.rect(self.screen, GRIS, playsave_rect.inflate(18, 2), 45)
            pygame.draw.rect(self.screen, BLACK, playsave_rect.inflate(20, 10), 4)
            self.screen.blit(playsave_texte, playsave_rect)

            deletesave_texte = font.render(f"Delete - {proute2}", True, RED) if (self.language == "English") else(font.render(f"Supprimer - {proute2}", True, RED))
            deletesave_rect = deletesave_texte.get_rect(center=(self.WIDTH // 5.2, self.HEIGHT - 150))
            pygame.draw.rect(self.screen, GRIS, deletesave_rect.inflate(18, 2), 45)
            pygame.draw.rect(self.screen, BLACK, deletesave_rect.inflate(20, 10), 4)
            self.screen.blit(deletesave_texte, deletesave_rect)


            retour_texte = font.render("<- Back", True, RED) if (self.language == "English") else(font.render("<- Retour", True, RED))
            retour_rect = retour_texte.get_rect(center=(self.WIDTH // 2, self.HEIGHT - 150))
            pygame.draw.rect(self.screen, BLACK, retour_rect.inflate(20, 10), 4)
            self.screen.blit(retour_texte, retour_rect)   
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_x, mouse_y = event.pos
                    if retour_rect.collidepoint(mouse_x, mouse_y):
                        running = False
                        self.menu_principal()
                    if playsave_rect.collidepoint(mouse_x, mouse_y) and self.nowsave != "":
                        running = False
                        self.verifmap(f'save/{self.nowsave}/map{self.nowsave}.json')
                        self.demarrer_jeu()
                    if deletesave_rect.collidepoint(mouse_x, mouse_y) and self.nowsave != "":
                        try:
                            os.chmod(f"save/{self.nowsave}", 0o777)
                            shutil.rmtree(f"save/{self.nowsave}")
                            try:
                                self.totalsave -= 1
                                self.savegenerals(f"{self.nowsave}")
                            except Exception as e:
                                print(f"Errrrrrrrrreur !! {e}")
                        except:
                            print("Error: Nous avons pas pu supprimer les fichiers")
                            try:
                                self.totalsave -= 1
                                self.savegenerals(f"{self.nowsave}")
                            except Exception as e:
                                print(f"Errrrrrrrrreur !! {e}")
                    for ii in range(1, self.totalsave +1):
                        if self.saveb_r[ii].collidepoint(mouse_x, mouse_y):
                            self.nowsave = f"{ii}"
                    if addsave_rect.collidepoint(mouse_x, mouse_y):
                        self.savename = ""
                        self.addsave = True
                if event.type == pygame.KEYDOWN:
                    if self.addsave == True:
                        if event.key == K_RETURN: print(self.savename); self.addsave = False; self.totalsave += 1; self.savegenerals("")
                        elif event.key == K_BACKSPACE: self.savename = self.savename[:-1]
                        elif len(self.savename) <= 15: self.savename += event.unicode
            pygame.display.flip()
    def demarrer_jeu(self):
        clock = pygame.time.Clock()
        # Clock
        shift_pressed = False
        running = True
        all_sprites.add(self.player)
        self.tileinmapdata()
        self.load_InventoryItemSlot()
        tileverif1, tileverif2 = 0, 0
        while running:
            fpsfont = pygame.font.Font(None, 36)
            if not self.Inventory_open:
                self.player.update(self.collision_rects); self.camera.update(self.player)
            self.screen.fill((0, 0, 0))
            self.screen.blit(self.map_surface, self.camera.apply(pygame.Rect(0, 0, self.map_surface.get_width(), self.map_surface.get_height())).topleft)
            for entity in all_sprites: self.screen.blit(entity.image, self.camera.apply(entity))
            self.load_HotBItemSlot(); self.HotBInventory()
            if self.Inventory_open: 
                self.load_InventoryItemSlot(); self.Inventorys(); self.print_inventory(), self.invplayer()
                if self.selected_item and self.selected_item_index is not None: self.InventoryItemHand(self.selected_item)
            mouse_buttons = pygame.mouse.get_pressed()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.save_map_to_json(self.map_data, f"save/{self.nowsave}/map{self.nowsave}.json")
                    pygame.quit()
                if self.Inventory_open:
                    if mouse_buttons[0]: self.CheckInvCol("Sleft") if(shift_pressed) else(self.CheckInvCol("left"))
                    elif mouse_buttons[2]: self.CheckInvCol("SRight") if(shift_pressed) else(self.CheckInvCol("Right"))
                if event.type == pygame.KEYDOWN:
                    if event.key == self.key_ESCAPE: running, self.Inventory_open = False, False; self.menu_pause()
                    if event.key == pygame.K_LSHIFT or event.key == pygame.K_RSHIFT: shift_pressed = True
                    if event.key == self.key_Inventory: self.Inventory_open = not self.Inventory_open
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_LSHIFT or event.key == pygame.K_RSHIFT: shift_pressed = False
                if event.type == MOUSEWHEEL:
                    if event.y == 1:
                        if self.selectslotHotB[0] == 7: self.selectslotHotB = (0,) + self.selectslotHotB[1:]
                        else: self.selectslotHotB = (self.selectslotHotB[0] + 1,) + self.selectslotHotB[1:]
                    if event.y == -1:
                        if self.selectslotHotB[0] == 0: self.selectslotHotB = (7,) + self.selectslotHotB[1:]
                        else: self.selectslotHotB = (self.selectslotHotB[0] - 1,) + self.selectslotHotB[1:]             
            if pygame.mouse.get_pressed()[0]:
                if not self.Inventory_open:
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    camera_x, camera_y = self.camera.get_offset()
                    world_mouse_x = (mouse_x + abs(camera_x)) // self.TILE_SIZE
                    world_mouse_y = (mouse_y + abs(camera_y)) // self.TILE_SIZE
                    for tile in self.map_data:
                        if tile['x'] == world_mouse_x and tile['y'] == world_mouse_y:
                            if tileverif1 == tile["x"] and tileverif2 == tile["y"]:
                                if tile["type"] in {"mineraliron", "mineralgold", "ressourcewood"}:
                                    if abs((mouse_x + abs(camera_x) - (self.player.rect.x + 64)) // self.TILE_SIZE) <= 1 and abs((mouse_y + abs(camera_y) - (self.player.rect.y + 64)) // self.TILE_SIZE) <= 1:
                                        if tile["type"] == "mineraliron" and self.selectslotHotB[1] == "WOOD_PICKAXE" or tile["type"] =="mineralgold" and self.selectslotHotB[1] == "WOOD_PICKAXE" or tile["type"] == "ressourcewood":
                                            self.buttonmine += 1
                                            pygame.draw.rect(self.screen, GRIS, (self.WIDTH / 3.5,self.HEIGHT - 200, 800, 40))
                                            pygame.draw.rect(self.screen, ORANGE, (self.WIDTH / 3.5, self.HEIGHT - 200, 6.6666 * self.buttonmine, 40))
                                            pygame.draw.rect(self.screen, BLACK, (self.WIDTH / 3.5, self.HEIGHT - 200, 800, 40), 2)
                                            if self.buttonmine == 120:
                                                self.addInventory_Data(self.mineral_to_inventory[tile["type"]], "IDK", 1, "Inventory")
                                                tile['type'] = "grass"
                                                self.map_data[self.map_data.index(tile)] = {"x": tile['x'], "y": tile['y'], "type": "grass"}
                                                self.buttonmine = 0
                                                self.tileinmapdata()
                                                break
                                        else: self.buttonmine = 0
                                    else:self.buttonmine = 0
                            else:
                                tileverif1, tileverif2 = tile["x"], tile["y"]
                                self.buttonmine = 0
            else:
                tileverif1, tileverif2 = 0, 0
                self.buttonmine = 0


            # Afficher les FPS à l'écran
            fps_text = fpsfont.render(f"FPS: {self.clock.get_fps():.2f}", True, (255, 255, 255))
            self.clock.tick(60)
            self.screen.blit(fps_text, (10, 10))
            pygame.display.flip()
        pygame.quit()
    def menu_pause(self):
        self.screen.blit(self.map_surface, self.camera.apply(pygame.Rect(0, 0, self.MAP_WIDTH * self.TILE_SIZE, self.MAP_HEIGHT * self.TILE_SIZE)).topleft)
        clock = pygame.time.Clock()
        running = True
        while running:
            font = pygame.font.Font(None, 54)
            jouer_texte = font.render("Continue", True, GREEN) if (self.language == "English") else(font.render("Continuer", True, GREEN))
            jouer_rect = jouer_texte.get_rect(center=(self.WIDTH // 2, self.HEIGHT // 2))
            pygame.draw.rect(self.screen, GRIS, jouer_rect.inflate(20, 10), 40)
            pygame.draw.rect(self.screen, BLACK, jouer_rect.inflate(20, 10), 4)
            self.screen.blit(jouer_texte, jouer_rect)
            retour_texte = font.render("Back in the main menu", True, RED) if (self.language == "English") else(font.render("Retour au menu principale", True, RED))
            retour_rect = retour_texte.get_rect(center=(self.WIDTH // 2, self.HEIGHT // 2 + 150))
            pygame.draw.rect(self.screen, GRIS, retour_rect.inflate(20, 10), 40)
            pygame.draw.rect(self.screen, BLACK, retour_rect.inflate(20, 10), 4)
            self.screen.blit(retour_texte, retour_rect)
            settings_texte = font.render("Settings", True, BLACK) if (self.language == "English") else(font.render("Paramètres", True, BLACK))
            settings_rect = settings_texte.get_rect(center=(self.WIDTH // 2, self.HEIGHT // 2 + 75))
            pygame.draw.rect(self.screen, GRIS, settings_rect.inflate(20, 10), 40)
            pygame.draw.rect(self.screen, BLACK, settings_rect.inflate(20, 10), 4)
            self.screen.blit(settings_texte, settings_rect)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_x, mouse_y = event.pos
                    if jouer_rect.collidepoint(mouse_x, mouse_y):
                        running = False  # Quitter le menu et commencer le jeu
                        self.demarrer_jeu()
                    if retour_rect.collidepoint(mouse_x, mouse_y):
                        running = False  # Quitter le menu et commencer le jeu
                        self.settingsofpause = False
                        self.save_map_to_json(self.map_data, f"save/{self.nowsave}/map{self.nowsave}.json")
                        self.menu_principal()
                    if settings_rect.collidepoint(mouse_x, mouse_y):
                        self.settingsofpause = True
                        running = False  # Quitter le menu et commencer le jeu
                        self.settings_menu()
            clock.tick(60)
            pygame.display.flip(); pygame.display.update()
        pygame.quit()

    def settings_menu(self):
        running = True
        while running:
            self.screen.fill(WHITE)
            self.screen.blit(self.settingsback, (0, 0))
            font = pygame.font.Font(None, 56)
            Key_font = pygame.font.Font(None, 38)
            retour_texte = font.render("<- Back", True, RED) if (self.language == "english") else(font.render("<- Retour", True, RED))
            retour_rect = retour_texte.get_rect(center=(self.WIDTH // 2, self.HEIGHT - 100))
            pygame.draw.rect(self.screen, BLACK, retour_rect.inflate(20, 10), 4)
            self.screen.blit(retour_texte, retour_rect)
            self.varsettings_ = ["Touche Retour", "Avancer", "Aller a Gauche", "Aller a Droite", "Reculer", "Touche Inventaire", "Language"]
            self.varsettings_e = ["Back Key", "Move Forward", "Move Left", "Move Right", "Move Backwards", "Inventory key", "Language"]
            self.varsettings_t = ["ToucheRetour", "ToucheAvancer", "ToucheGauche", "ToucheDroite", "ToucheReculer", "ToucheInventaire", "ToucheLanguage"]
            self.varsettings_r = ["ToucheRetour", "ToucheAvancer", "ToucheGauche", "ToucheDroite", "ToucheReculer", "ToucheInventaire", "ToucheLanguage"]
            for r in range(7):
                key = getattr(self, f"key_{self.key_[r]}") if (r != 6) else ()
                self.varsettings_t[r] = Key_font.render((f"{self.varsettings_[r]}: {pygame.key.name(key)}" if (self.language == "Français") else(f"{self.varsettings_e[r]}: {pygame.key.name(key)}")) if (self.varsettings_[r] != "Language") else (f"Language: " f"{self.language}"), True, BLACK)
                self.varsettings_r[r] = self.varsettings_t[r].get_rect(center=(300, 100 + 50 * r))
                pygame.draw.rect(self.screen, BLACK, self.varsettings_r[r].inflate(20, 10), 4)
                self.screen.blit(self.varsettings_t[r], self.varsettings_r[r]) 
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_x, mouse_y = event.pos
                    if retour_rect.collidepoint(mouse_x, mouse_y):
                        running = False
                        if self.settingsofpause == True: self.menu_pause(); self.settingsofpause = False
                        else: self.menu_principal()
                    else:
                        for rr in range(7):
                            if rr == 6 and self.varsettings_r[rr].collidepoint(mouse_x, mouse_y):
                                self.language = "Français" if(self.language == "English") else("English")
                                self.savegenerals("")
                if event.type == pygame.KEYDOWN:
                    for rr in range(7):
                        mouse_pos = pygame.mouse.get_pos()
                        keyv = f"{self.key_[rr]}" if (rr !=6) else()
                        if keyv in self.change_key and self.varsettings_r[rr].collidepoint(mouse_pos):
                            setattr(self, f"key_{keyv}", event.key)  # Change dynamiquement la touche
                            Player.save_key_configuration(self)  # Sauvegarder la nouvelle configuration
            pygame.display.flip()
    def changefonttextV(self, a, b, c, d, e, f):
        if self.changefonttextKESCAPE == True: pygame.draw.rect(self.screen, GRIS, a.inflate(12, 3), 80)
        if self.changefonttextKz == True: pygame.draw.rect(self.screen, GRIS, b.inflate(12, 3), 80)
        if self.changefonttextKq == True: pygame.draw.rect(self.screen, GRIS, c.inflate(12, 3), 80)
        if self.changefonttextKd == True: pygame.draw.rect(self.screen, GRIS, d.inflate(12, 3), 80)
        if self.changefonttextKs == True: pygame.draw.rect(self.screen, GRIS, e.inflate(12, 3), 80)
        if self.changefonttextKInventory == True: pygame.draw.rect(self.screen, GRIS, f.inflate(12, 3), 80)

    def load_InventoryItemSlot(self):
        try:
            with open(f"save\{self.nowsave}/Inventory.json", "r") as f:
                Inventory = json.load(f)
                for key in Inventory: self.Inventory[key] = {'item': Inventory[key].get('item', 'unknown'), 'quantity': Inventory[key].get('quantity', 0), "R": Inventory[key].get('R', 0), "C": Inventory[key].get('C', 0)}
        except (FileNotFoundError, json.JSONDecodeError):
            inventory = {}
            for c in range(8): 
                for r in range(6): key = f"CR{c}{r}"; inventory[key] = {"C": c, "R": r, "item": "none", "quantity": 0}
            try:
                with open(f"save\{self.nowsave}/Inventory.json", 'w') as file: json.dump(inventory, file, indent=4); print(f"Fichier d'inventaire créé avec succès")
            except IOError as e: print(f"Erreur lors de la création du fichier d'inventaire : {e}")

    def load_HotBItemSlot(self):
        try:
            with open(f"save\{self.nowsave}/HotB.json", "r") as f:
                HotB = json.load(f)
                for hkey in HotB: self.HotB[hkey] = {'item': HotB[hkey].get('item', 'unknown'), 'quantity': HotB[hkey].get('quantity', 0), "HR": HotB[hkey].get('HR', 0), "HC": HotB[hkey].get('HC', 0)}
        except (FileNotFoundError, json.JSONDecodeError):
            HotB = {}
            for hc in range(8):
                for hr in range(1): hkey = f"CR{hc}{hr}"; HotB[hkey] = {"HC": hc, "HR": hr, "item": "none", "quantity": 0}
            try: 
                with open(f"save\{self.nowsave}/HotB.json", 'w') as file: json.dump(HotB, file, indent=4)
            except IOError as e: print(f"Erreur lors de la création du fichier d'HotB : {e}")
    def print_inventory(self):
        start_x = self.WIDTH / 8; start_y = 100; font = pygame.font.Font(None, 38)
        for index, details in self.Inventory.items():
            item_name, quantity = details['item'], font.render(f"{details['quantity']}", True, self.ITEMS["BLACK"]); item = self.ITEMS.get(item_name, (128, 128, 128))
            if isinstance(item, tuple): pygame.draw.rect(self.screen, item, (start_x + details['C'] * 100 + 10, start_y + details['R'] * 100 + 10, 80, 80))
            else: self.screen.blit(item, (start_x + details['C'] * 100 + 10, start_y + details['R'] * 100 + 10))
            if details['quantity'] > 0: self.screen.blit(quantity, (start_x + details['C'] * 100 + 10 + 64, start_y + details['R'] * 100 + 10)) if (details['quantity'] < 10) else (self.screen.blit(quantity, (start_x + details['C'] * 100 + 10 + 58, start_y + details['R'] * 100 + 10))) if (details['quantity'] >= 10 and details['quantity'] < 100) else(self.screen.blit(quantity, (start_x + details['C'] * 100 + 10 + 44, start_y + details['R'] * 100 + 10)))
    
    def addInventory_Data(self, item, index, quantity, Invorhotb):
        with open(f"save/{self.nowsave}/Inventory.json", 'r') if(Invorhotb == "Inventory") else(open(f"save/{self.nowsave}/HotB.json", "r")) as file: data = json.load(file)
        if index == "IDK":
            for items in data:
                if data[f"{items}"]["item"] == item:
                    data[f"{items}"]["quantity"] += 1
                    break
            else:
                for items in data:
                    if data[f"{items}"]["item"] == "none":
                        data[f"{items}"]["item"] = item
                        data[f"{items}"]["quantity"] += 1
                        break
                else:
                    self.addInventory_Data(item, "IDK", 1, "HotB")                
        else:
            data[f"{index}"]["item"] = item; data[f"{index}"]["quantity"] += quantity
        with open(f"save/{self.nowsave}/Inventory.json", 'w') if(Invorhotb == "Inventory") else(open(f"save/{self.nowsave}/HotB.json", "w")) as file: json.dump(data, file, indent=4)
    
    def removeInventory_Data(self, index, Invorhotb):
        with open(f"save/{self.nowsave}/Inventory.json", 'r') if(Invorhotb == "Inventory") else(open(f"save/{self.nowsave}/HotB.json", "r")) as file: data = json.load(file)
        if data[f"{index}"]["quantity"] == 0: pass
        elif data[f"{index}"]["quantity"] == self.quantitytoremove_item: data[f"{index}"]["item"] = "none"; data[f"{index}"]["quantity"] -= self.quantitytoremove_item
        else: 
            data[f"{index}"]["quantity"] -= self.quantitytoremove_item
            if not self.Inventory_hand: self.Inventory_hand = not self.Inventory_hand
        with open(f"save/{self.nowsave}/Inventory.json", 'w') if(Invorhotb == "Inventory") else(open(f"save/{self.nowsave}/HotB.json", "w")) as file: json.dump(data, file, indent=4); self.quantitytoremove_itemwait = False
    
    def run(self): self.menu_principal()
    
    def Inventorys(self):
        start_x, start_y = self.WIDTH / 8, 100
        font = pygame.font.Font(None, 38)
        inventaire_titre = font.render("Inventory", True, BLACK) if (self.language == "English") else(font.render("Inventaire", True, BLACK))
        self.screen.blit(inventaire_titre, (start_x, start_y - 30))
        x = 100
        width, height, num_columns, num_rows = 100, 100, 8, 6
        pygame.draw.rect(self.screen, GRIS, (start_x, start_y, num_columns * 100, num_rows * 100))
        for col in range(num_columns):
            for row in range(num_rows):
                x, y = start_x + col * (width), start_y + row * (height)
                pygame.draw.rect(self.screen, BLACK, (x, y, width, height), 4)
    def HotBInventory(self):
        x = 100
        hstart_x, hstart_y = self.WIDTH / 3.5, self.HEIGHT - 100
        width, height, num_columns, num_rows = 100, 100, 8, 1
        htfont = pygame.font.Font(None, 36)
        pygame.draw.rect(self.screen, BLACK, (self.WIDTH / 3.5,hstart_y - 50, 350, 40))
        pygame.draw.rect(self.screen, RED, (self.WIDTH / 3.5,hstart_y - 50, 350, 40))
        pygame.draw.rect(self.screen, BLACK, (self.WIDTH / 3.5,hstart_y - 50, 350, 40), 2)
        pygame.draw.rect(self.screen, GRIS, (hstart_x, hstart_y, 800, 100))
        for index, hdetails in self.HotB.items():
            x, y = hstart_x + hdetails["HC"] * (width), hstart_y + 0 * (height)
            pygame.draw.rect(self.screen, ORANGE, (hstart_x + 4 + self.selectslotHotB[0] * 100,hstart_y +4, width - 8 , height  - 8), 4)
            self.selectslotHotB = self.selectslotHotB[:1] + (hdetails['item'] if(hdetails["HC"] == self.selectslotHotB[0]) else(self.selectslotHotB[1]),) + self.selectslotHotB[2:]
            pygame.draw.rect(self.screen, BLACK, (x, y, width, height), 4)
            color_name = hdetails['item']
            hquantity = htfont.render(f"{hdetails['quantity']}", True, BLACK)
            Hitem = self.ITEMS.get(color_name, (128, 128, 128))
            if isinstance(Hitem, tuple): pygame.draw.rect(self.screen, Hitem, (hstart_x + hdetails["HC"] * 100 + 10, hstart_y + hdetails['HR'] * 100 + 10, 80, 80))
            else: self.screen.blit(Hitem, (hstart_x + hdetails['HC'] * 100 + 10, hstart_y + hdetails['HR'] * 100 + 10))
            if hdetails['quantity'] > 0: self.screen.blit(hquantity, (hstart_x + hdetails['HC'] * 100 + 10 + 64,hstart_y + 10)) if (hdetails['quantity'] < 10) else (self.screen.blit(hquantity, (hstart_x + hdetails['HC'] * 100 + 5 + 58,hstart_y + 10))) if (hdetails['quantity'] >= 10 and hdetails['quantity'] < 100) else(self.screen.blit(hquantity, (hstart_x + hdetails['HC'] * 100 + 5 + 44,hstart_y + 10)))
    def CheckInvCol(self, rightorleft):
        current_time = time.time()
        if current_time - self.last_click_time < 0.1:
            return
        self.last_click_time = current_time
        hstart_x, hstart_y = self.WIDTH / 3.5, self.HEIGHT - 100
        start_x, start_y = self.WIDTH / 8, 100
        for slot, details in self.Inventory.items():
            item, x, y = details["item"], start_x + details['C'] * 100 + 10, start_y + details['R'] * 100 + 10; index_rect = pygame.Rect(x, y, 80, 80)
            self.doublecheck(index_rect, slot, item, "Inventory", rightorleft, details)
        for slot2, details2 in self.HotB.items():
            item, x, y = details2["item"], hstart_x + details2['HC'] * 100 + 10, hstart_y + details2['HR'] * 100 + 10; index_rect = pygame.Rect(x, y, 80, 80)
            self.doublecheck(index_rect, slot2, item, "hotb", rightorleft, details2)
    def doublecheck(self, index_rect, slot, item, type, rightorleft, details):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        if index_rect.collidepoint(mouse_x, mouse_y):
            item = details["item"]
            if rightorleft == "Right" or rightorleft == "SRight":
                if item == "none" or item == self.selected_item:
                    if self.selected_item:
                        quantity_to_add = 1 if rightorleft == "Right" else self.quantity_item
                        self.addInventory_Data(self.selected_item, slot, quantity_to_add, type)
                        self.quantity_item -= quantity_to_add
                        if self.quantity_item == 0: self.selected_item = None
            elif rightorleft == "left" or rightorleft == "Sleft":
                if item != "none" and (self.selected_item is None or self.selected_item == item):
                    if not self.quantitytoremove_itemwait:
                        self.selected_item_index, self.selected_item, self.quantitytoremove_itemwait, self.quantitytoremove_item = slot, item, True, 1 if rightorleft == "left" else details["quantity"]
                        self.quantity_item += 1 if rightorleft == "left" else details["quantity"]; self.removeInventory_Data(slot, type)

    def InventoryItemHand(self, details):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        itemhand = self.ITEMS.get(details, (128, 128, 128))
        hand_rect = (mouse_x, mouse_y, 80, 80)
        if isinstance(itemhand, tuple): pygame.draw.rect(self.screen, itemhand, hand_rect)
        else: self.screen.blit(itemhand, (mouse_x, mouse_y))
        font = pygame.font.Font(None, 36)
        quantity = font.render(f"{self.quantity_item}", True, self.ITEMS["BLACK"])
        if self.quantity_item > 0: self.screen.blit(quantity, (mouse_x + 68, mouse_y)) if (self.quantity_item < 10) else (self.screen.blit(quantity, (mouse_x + 58, mouse_y))) if (self.quantity_item < 100) else(self.screen.blit(quantity, (mouse_x + 48, mouse_y)))

    def invplayer(self):
        start_x, start_y = self.WIDTH / 8 + 800, 100
        pygame.draw.rect(self.screen, GRIS, (start_x, start_y, 400, 600))
