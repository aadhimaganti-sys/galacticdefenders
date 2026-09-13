import pygame
import os
import sys

pygame.init()

# --- Display & Timing ---
info = pygame.display.Info()
SCREEN_WIDTH = info.current_w
SCREEN_HEIGHT = info.current_h
FPS = 60

# --- Colors ---
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
JET_BLUE = (0, 150, 255)
JET_WING_COLOR = (0, 100, 200)
JET_BLASTER_COLOR = (200, 200, 200)

PLAYER_COLORS = [
    (0, 150, 255),  # P1: Blue
    (255, 100, 0),  # P2: Orange
    (50, 255, 50),  # P3: Green
    (255, 50, 255), # P4: Magenta
    (255, 255, 0),  # P5+: Yellow
]

BULLET_YELLOW = (255, 255, 0)
WIN_GREEN = (0, 255, 0)
LOSE_RED = (255, 0, 0)
ORANGE = (255, 165, 0)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
DARK_GRAY = (50, 50, 50)
LIGHT_GRAY = (150, 150, 150)

BUTTON_COLOR = (0, 50, 100)
BUTTON_HOVER_COLOR = (0, 80, 150)
BUTTON_DISABLED_COLOR = (70, 70, 70)
SHIELD_COLOR = (100, 200, 255, 150)
BOSS_COLOR = (200, 50, 50)
MOD_ON_COLOR = (0, 180, 50)
MOD_OFF_COLOR = (180, 50, 50)
COCKPIT_GLASS = (150, 220, 255)

# --- Fonts ---
FONT_XLARGE = pygame.font.SysFont("Arial", 80, bold=True)
FONT_LARGE = pygame.font.SysFont("Arial", 50, bold=True)
FONT_MEDIUM = pygame.font.SysFont("Arial", 30)
FONT_SMALL = pygame.font.SysFont("Arial", 20)

# --- Paths ---
if getattr(sys, "frozen", False):
    BASE_DIR = os.path.expanduser("~/Documents/GalacticDefender")
    if not os.path.exists(BASE_DIR):
        os.makedirs(BASE_DIR)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

PROGRESS_FILE = os.path.join(BASE_DIR, "galactic_defender_progress.json")
MOD_CONFIG_FILE = os.path.join(BASE_DIR, "mod_config.json")

# --- Base Catalogs ---
BASE_SHIP_TYPES = {
    "default_jet": {
        "name": "Default Jet",
        "cost": 0,
        "speed": 7,
        "color": JET_BLUE,
        "wing_color": JET_WING_COLOR,
        "desc": "The reliable starting jet.",
        "start_blasters": 1,
    },
    "speeder_x1": {
        "name": "Speeder X1",
        "cost": 200,
        "speed": 10,
        "color": (200, 0, 0),
        "wing_color": (150, 0, 0),
        "desc": "A much faster, agile fighter.",
        "start_blasters": 1,
    },
    "tank_mk1": {
        "name": "Tank Mk1",
        "cost": 350,
        "speed": 5,
        "color": (0, 100, 0),
        "wing_color": (0, 70, 0),
        "desc": "Slower, but starts with 2 blasters.",
        "start_blasters": 2,
    },
    "scout_mk2": {
        "name": "Scout MK2",
        "cost": 150,
        "speed": 8,
        "color": (100, 100, 255),
        "wing_color": (70, 70, 200),
        "desc": "Balanced speed and maneuverability.",
        "start_blasters": 1,
    },
    "assault_mk3": {
        "name": "Assault MK3",
        "cost": 500,
        "speed": 6,
        "color": (150, 50, 0),
        "wing_color": (100, 30, 0),
        "desc": "Heavy firepower, 3 starting blasters.",
        "start_blasters": 3,
    },
    "boss_hunter": {
        "name": "Boss Hunter",
        "cost": "CHIP_RARE",
        "speed": 9,
        "color": (255, 0, 255),
        "wing_color": (200, 0, 200),
        "desc": "Designed to shred boss armor.",
        "start_blasters": 4,
    },
    "shadow_wraith": {
        "name": "Shadow Wraith",
        "cost": 8000,
        "speed": 12,
        "color": (20, 20, 20),
        "wing_color": (50, 0, 100),
        "desc": "Black market stealth ship. Insanely fast.",
        "start_blasters": 3,
    },
}

BASE_HELPER_TYPES = {
    "power_modloader": {
        "name": "Datapack Mod Loader License",
        "cost": 2000,
        "desc": "Unlocks Mod Loader & makes ALL Datapack items FREE in Armory!",
    },
    "power_autopilot": {
        "name": "Auto-Pilot Mod",
        "cost": 1000,
        "desc": "Unlocks auto-pilot toggle.",
    },
    "power_godmode": {
        "name": "God Mode Protocol",
        "cost": 5000,
        "desc": "Unlocks invincibility.",
    },
    "power_autoshield": {
        "name": "Auto-Shield Deployer",
        "cost": 0,
        "desc": "Automatically deploys shields (UNLOCKED DEFAULT).",
    },
    "power_autotriple": {
        "name": "Auto-Triple Booster",
        "cost": 2500,
        "desc": "Max fire rate.",
    },
    "power_magnet": {
        "name": "Magnetic Field Generator",
        "cost": 3000,
        "desc": "Alters gravity fields to pull powerups toward your ship.",
    },
    "secret_spinoff_key": {
        "name": "Story Campaign Access",
        "cost": 500,
        "desc": "Unlocks the cinematic Story Mode.",
    },
}