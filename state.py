import json

# Current logged-in user (set by login_flow)
current_user = None
import os
from settings import *

# --- Gameplay State ---
level = 1
score_p1 = 0
score_p2 = 0
win_status = False
winning_player = 0
game_state = "HOME"
game_mode = None

# --- 2.2 CAMERA ENGINE & PARTICLES ---
CAMERA_ZOOM = 1.0
CAMERA_SHAKE = 0
CAMERA_ANGLE = 0
BG_COLOR = (0, 0, 0)
particle_list = []  # Global list for all shattered fragments and engine trails

# --- 2.2 PLATFORMER PHYSICS ---
GRAVITY = 0.8
JUMP_POWER = -16

# --- Runtime Toggles ---
ADMIN_GOD_MODE = False
AUTO_PILOT_ACTIVE = False
TON_618_ACTIVE = False
TIME_FREEZE_END = 0
cheat_error_timer = 0
CHEAT_MENU_INDEX = 0

# --- MEGA HACK v7 STYLE ENGINE ---
CHEAT_MENU_VISIBLE = False
MH_ACTIVE_TAB = "Visual"

MEGAHACK_CATEGORIES = {
    "Player": ["Noclip", "God Mode", "Auto Pilot", "Toggle Platformer", "Infinite Ammo", "Shield Burst", "Full Heal"],
    "Bypass": ["Unlock All Ships", "Unlock All Helpers", "Infinite Credits", "Instant Win", "Toggle LAN Mode"],
    "Creator": ["Spawn Boss", "Spawn Drone", "Spawn Asteroid", "Clear Screen", "Level Up", "Level Down"],
    "Visual": ["Show Hitboxes", "Toggle HUD", "Cinematic Zoom", "Force Screen Shake", "Rotate Screen", "Chromatic Aberration", "Cyberpunk BG"],
    "Variables": ["Speedhack x0.5", "Speedhack x1.0", "Speedhack x2.0", "Speedhack x5.0", "Reverse Time"]
}

# The Global Hack State Registry
ACTIVE_HACKS = {hack: False for cat in MEGAHACK_CATEGORIES.values() for hack in cat}
ACTIVE_HACKS["Speedhack x1.0"] = True
GAME_SPEED = 1.0

# --- Catalogs & Profile System ---
SHIP_TYPES = {}
HELPER_TYPES = {}
active_mods = []

DEFAULT_PLAYER_DATA = {
    "credits": 0, 
    "coins": 0, 
    "owned_ships": ["default_jet"], 
    "selected_ship": "default_jet",
    "has_subscription": False, 
    "upgrades": {"blaster_level": 1, "max_health": 1},
    "unlocked_powers": ["power_autoshield"], 
    "has_downloaded_cheat_menu": False,
}

# --- Audio Settings ---
audio_settings = {
    "master_volume": 1.0,
    "sfx_volume": 0.8,
    "music_volume": 0.7,
    "sfx_muted": False,
    "music_muted": False,
}

def load_audio_config():
    global audio_settings
    try:
        if os.path.exists(AUDIO_CONFIG_FILE):
            with open(AUDIO_CONFIG_FILE, "r") as f:
                loaded = json.load(f)
                audio_settings.update(loaded)
    except Exception:
        pass

def save_audio_config():
    try:
        with open(AUDIO_CONFIG_FILE, "w") as f:
            json.dump(audio_settings, f, indent=4)
    except Exception:
        pass

all_player_data = {"P1": dict(DEFAULT_PLAYER_DATA), "P2": dict(DEFAULT_PLAYER_DATA)}

def load_mod_config():
    global active_mods
    try:
        if os.path.exists(MOD_CONFIG_FILE):
            with open(MOD_CONFIG_FILE, "r") as f:
                active_mods = json.load(f)
        else:
            active_mods = []
    except Exception: 
        active_mods = []

def save_mod_config():
    try:
        with open(MOD_CONFIG_FILE, "w") as f: 
            json.dump(active_mods, f)
    except Exception: 
        pass

def reload_mods():
    global SHIP_TYPES, HELPER_TYPES
    SHIP_TYPES.clear()
    HELPER_TYPES.clear()
    
    for k, v in BASE_SHIP_TYPES.items(): 
        SHIP_TYPES[k] = dict(v)
    for k, v in BASE_HELPER_TYPES.items(): 
        HELPER_TYPES[k] = dict(v)
        
    try:
        for filename in os.listdir(BASE_DIR):
            if filename.endswith(".json") and filename not in ["galactic_defender_progress.json", "mod_config.json", "custom_level.json"] and filename in active_mods:
                try:
                    with open(os.path.join(BASE_DIR, filename), "r") as f:
                        ext = json.load(f)
                        if "ships" in ext:
                            for k, d in ext["ships"].items():
                                d["color"] = tuple(d.get("color", (255, 255, 255)))
                                d["wing_color"] = tuple(d.get("wing_color", (150, 150, 150)))
                                d["from_datapack"] = True
                                SHIP_TYPES[k] = d
                        if "helpers" in ext:
                            for k, d in ext["helpers"].items():
                                d["from_datapack"] = True
                                HELPER_TYPES[k] = d
                except Exception: 
                    pass
    except Exception: 
        pass

def load_game_progress():
    global all_player_data
    try:
        if os.path.exists(PROGRESS_FILE):
            with open(PROGRESS_FILE, "r") as f:
                loaded_data = json.load(f)
                all_player_data["P1"] = {**dict(DEFAULT_PLAYER_DATA), **loaded_data.get("P1", {})}
                all_player_data["P2"] = {**dict(DEFAULT_PLAYER_DATA), **loaded_data.get("P2", {})}
        else: 
            save_game_progress()
    except Exception: 
        save_game_progress()

def save_game_progress():
    try:
        with open(PROGRESS_FILE, "w") as f: 
            json.dump(all_player_data, f, indent=4)
    except Exception: 
        pass