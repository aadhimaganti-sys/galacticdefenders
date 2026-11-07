import json
import copy
import os

# Current logged-in user (set by login_flow)
current_user = None
from settings import *

# --- Gameplay State ---
level = 1

win_status = False
winning_player = 0
game_state = "HOME"
game_mode = None

# --- 2.2 CAMERA ENGINE & PARTICLES ---
CAMERA_ZOOM = 1.0
CAMERA_SHAKE = 0
CAMERA_ANGLE = 0
BG_COLOR = (0, 0, 0)
particle_list: list = []  # Global list for all shattered fragments and engine trails

# --- PILOT & CREW DATA ---
CHARACTERS = {
    "Rook": {"role": "Copilot", "color": (100, 200, 255), "desc": "Ace pilot with lightning reflexes.", "price": 0},
    "Vax": {"role": "Tactical", "color": (255, 100, 100), "desc": "Weapons specialist and combat veteran.", "price": 0},
    "Sparky": {"role": "Engineer", "color": (255, 200, 50), "desc": "Ship mechanic who keeps the core stable.", "price": 0},
    "Kael": {"role": "Commander", "color": (150, 100, 255), "desc": "Strategic mastermind.", "price": 0},
    "Nova": {"role": "Navigator", "color": (0, 255, 150), "desc": "Can chart a course through a black hole.", "price": 500},
    "Jax": {"role": "Gunner", "color": (255, 50, 50), "desc": "Never misses a shot. Likes big explosions.", "price": 800},
    "Lyra": {"role": "Medic", "color": (255, 150, 200), "desc": "Keeps the crew alive when things go wrong.", "price": 600},
    "Bex": {"role": "Scavenger", "color": (200, 150, 50), "desc": "Finds spare parts where there are none.", "price": 400},
    "Zane": {"role": "Shield Operator", "color": (50, 150, 255), "desc": "Master of deflector arrays and barriers.", "price": 1000},
}
current_crew = ["Rook", "Vax", "Sparky"]

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
SHIP_TYPES: dict = {}
HELPER_TYPES: dict = {}
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
    "pilot_level": 1,
    "pilot_xp": 0,
    "stat_points": 0,
}

def new_player_data():
    """Return an independent copy of the default player profile."""
    return copy.deepcopy(DEFAULT_PLAYER_DATA)

def get_player_data(username=None):
    """Return a player's data, creating it with defaults when missing."""
    user = username if username else (current_user if current_user else "Guest")
    if user not in all_player_data:
        all_player_data[user] = new_player_data()
    else:
        for key, value in DEFAULT_PLAYER_DATA.items():
            all_player_data[user].setdefault(key, copy.deepcopy(value))
    return all_player_data[user]

# --- General & Audio Settings (Player Preferences) ---
audio_settings = {
    "master_volume": 1.0,
    "sfx_volume": 0.8,
    "music_volume": 0.7,
    "sfx_muted": False,
    "music_muted": False,
    "enable_copilot": False,
    "sound_pack": "classic",
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
    global audio_settings
    try:
        with open(AUDIO_CONFIG_FILE, "w") as f:
            json.dump(audio_settings, f, indent=4)
    except Exception:
        pass

# --- Privileged Admin Settings ---
admin_settings = {
    "dev_console_allowed": True,
    "default_starting_credits": 0,
    "global_game_speed": 1.0,
    "force_god_mode": False,
    "ship_view_mode": False,
}

DEV_CONSOLE_ALLOWED = True
PLAYER_HEALTH_MODE = False
SHIP_VIEW_MODE = False

def load_admin_config():
    global admin_settings, DEV_CONSOLE_ALLOWED, GAME_SPEED, ADMIN_GOD_MODE, PLAYER_HEALTH_MODE, SHIP_VIEW_MODE
    try:
        if os.path.exists(ADMIN_CONFIG_FILE):
            with open(ADMIN_CONFIG_FILE, "r") as f:
                loaded = json.load(f)
                admin_settings.update(loaded)
                DEV_CONSOLE_ALLOWED = admin_settings.get("dev_console_allowed", True)
                GAME_SPEED = admin_settings.get("global_game_speed", 1.0)
                ADMIN_GOD_MODE = admin_settings.get("force_god_mode", False)
                PLAYER_HEALTH_MODE = admin_settings.get("player_health_mode", False)
                SHIP_VIEW_MODE = admin_settings.get("ship_view_mode", False)
    except Exception:
        pass

def save_admin_config():
    global admin_settings, DEV_CONSOLE_ALLOWED, GAME_SPEED, ADMIN_GOD_MODE, PLAYER_HEALTH_MODE, SHIP_VIEW_MODE
    try:
        admin_settings["dev_console_allowed"] = DEV_CONSOLE_ALLOWED
        admin_settings["global_game_speed"] = GAME_SPEED
        admin_settings["force_god_mode"] = ADMIN_GOD_MODE
        admin_settings["player_health_mode"] = PLAYER_HEALTH_MODE
        admin_settings["ship_view_mode"] = SHIP_VIEW_MODE
        with open(ADMIN_CONFIG_FILE, "w") as f:
            json.dump(admin_settings, f, indent=4)
    except Exception:
        pass


all_player_data = {}

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

POWERUP_TYPES: dict = {}

def reload_mods():
    global SHIP_TYPES, HELPER_TYPES, POWERUP_TYPES
    SHIP_TYPES.clear()
    HELPER_TYPES.clear()
    POWERUP_TYPES.clear()
    
    for k, v in BASE_SHIP_TYPES.items(): 
        SHIP_TYPES[k] = dict(v)
    for k, v in BASE_HELPER_TYPES.items(): 
        HELPER_TYPES[k] = dict(v)
        
    mods_dir = os.path.join(BASE_DIR, "mods")
    if not os.path.exists(mods_dir):
        return
        
    try:
        for filename in os.listdir(mods_dir):
            if filename.endswith(".json") and (filename in active_mods):
                try:
                    with open(os.path.join(mods_dir, filename), "r") as f:
                        ext = json.load(f)
                        if "ships" in ext:
                            for k, d in ext["ships"].items():
                                d["name"] = d.get("name", k.replace("_", " ").title())
                                d["desc"] = d.get("desc", "Custom Datapack Starship")
                                d["cost"] = d.get("cost", 0)
                                d["speed"] = d.get("speed", d.get("base_speed", 7))
                                d["color"] = tuple(d.get("color", (255, 255, 255)))
                                d["wing_color"] = tuple(d.get("wing_color", (150, 150, 150)))
                                d["from_datapack"] = True
                                SHIP_TYPES[k] = d
                                if d.get("unlocked_by_default", False) or d.get("cost", 0) == 0:
                                    user = current_user if current_user else "Guest"
                                    player_data = get_player_data(user)
                                    if k not in player_data.get("owned_ships", []):
                                        player_data.setdefault("owned_ships", ["default_jet"]).append(k)
                        if "helpers" in ext:
                            for k, d in ext["helpers"].items():
                                d["name"] = d.get("name", k.replace("_", " ").title())
                                d["desc"] = d.get("desc", "Custom Datapack Helper Unit")
                                d["cost"] = d.get("cost", 0)
                                d["from_datapack"] = True
                                HELPER_TYPES[k] = d
                                if d.get("unlocked_by_default", False) or d.get("cost", 0) == 0:
                                    user = current_user if current_user else "Guest"
                                    player_data = get_player_data(user)
                                    if k not in player_data.get("unlocked_powers", []):
                                        player_data.setdefault("unlocked_powers", ["power_autoshield"]).append(k)
                        if "powerups" in ext:
                            for k, d in ext["powerups"].items():
                                d["name"] = d.get("name", k.replace("_", " ").title())
                                d["desc"] = d.get("desc", "Custom Datapack Powerup")
                                d["color"] = tuple(d.get("color", (0, 255, 255)))
                                POWERUP_TYPES[k] = d
                except Exception as e: 
                    print(f"Error loading mod {filename}: {e}")
    except Exception: 
        pass
def load_game_progress():
    global all_player_data, current_user
    try:
        import account
        active_session = account.get_active_session()
        if active_session:
            current_user = active_session

        user = current_user if current_user else "Guest"
        all_player_data[user] = new_player_data()

        if current_user:
            u_data = account.load_user_data(current_user)
            if u_data:
                all_player_data[user].update(u_data)

        # Guest data is used for local co-op and when nobody is logged in,
        # so make sure it always exists.
        if "Guest" not in all_player_data:
            all_player_data["Guest"] = new_player_data()
    except Exception:
        pass
def save_game_progress():
    try:
        user = current_user if current_user else "Guest"
        if current_user:
            import account
            account.save_user_data(current_user, all_player_data.get(user, DEFAULT_PLAYER_DATA))
    except Exception: 
        pass