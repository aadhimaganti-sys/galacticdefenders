import json
import os
from settings import BASE_DIR
import state

GUILDS_FILE = os.path.join(BASE_DIR, "guilds.json")
CHATS_FILE = os.path.join(BASE_DIR, "guild_chats.json")
guilds_cache = []

# Mapping of perk names to their actual effect values
AUTO_PERKS_MAP = {
    "Credit Bonus I": {"type": "credits", "value": 0.10},
    "Hull Reinforcement I": {"type": "health", "value": 1},
    "Blaster Overcharge I": {"type": "damage", "value": 0.10},
    "Guild Banner": {"type": "none", "value": 0}
}

def init_guilds():
    global guilds_cache
    guilds_cache = []
    if os.path.exists(GUILDS_FILE):
        try:
            with open(GUILDS_FILE, "r") as f:
                guilds_cache = json.load(f)
        except Exception:
            guilds_cache = []

    if not guilds_cache:
        guilds_cache = [
            {
                "name": "Solar Vanguard",
                "tag": "SOLAR",
                "description": "Elite frontier pilots dedicated to guarding inner colonies.",
                "leader": "Commander Vex",
                "level": 3,
                "xp": 12000,
                "bank_credits": 15000,
                "members": [
                    {"username": "Commander Vex", "rank": "Leader", "contributions": 5000},
                    {"username": "Lyra", "rank": "Officer", "contributions": 3500},
                    {"username": "Kael", "rank": "Member", "contributions": 1200}
                ],
                "perks": ["Credit Bonus I", "Hull Reinforcement I"]
            },
            {
                "name": "Nebula Syndicate",
                "tag": "VOID",
                "description": "Interstellar corsairs and smugglers navigating uncharted hyperspace lanes.",
                "leader": "Shadow Corsair",
                "level": 2,
                "xp": 6500,
                "bank_credits": 8200,
                "members": [
                    {"username": "Shadow Corsair", "rank": "Leader", "contributions": 4000},
                    {"username": "Nyx", "rank": "Officer", "contributions": 2100}
                ],
                "perks": ["Blaster Overcharge I"]
            }
        ]
        save_guilds()

def save_guilds():
    try:
        with open(GUILDS_FILE, "w") as f:
            json.dump(guilds_cache, f, indent=4)
        return True
    except Exception:
        return False

def get_all_guilds():
    return guilds_cache

def get_player_guild(username):
    if not username:
        return None
    for g in guilds_cache:
        for m in g.get("members", []):
            if m.get("username") == username:
                return g
    return None

def create_guild(name, tag, desc, leader_username):
    if not name or not tag or not leader_username:
        return False
    if get_player_guild(leader_username) is not None:
        return False

    for g in guilds_cache:
        if g.get("name") == name or g.get("tag") == tag:
            return False

    new_guild = {
        "name": name,
        "tag": tag,
        "description": desc,
        "leader": leader_username,
        "level": 1,
        "xp": 0,
        "bank_credits": 0,
        "members": [{"username": leader_username, "rank": "Leader", "contributions": 0}],
        "perks": ["Guild Banner"]
    }
    guilds_cache.append(new_guild)
    save_guilds()
    return True

def join_guild(guild_name, username):
    if not username:
        return False
    if get_player_guild(username) is not None:
        return False

    for g in guilds_cache:
        if g.get("name") == guild_name:
            g.setdefault("members", []).append({"username": username, "rank": "Member", "contributions": 0})
            save_guilds()
            return True
    return False

def leave_guild(username):
    if not username:
        return False
    for i, g in enumerate(list(guilds_cache)):
        members = g.get("members", [])
        for m in list(members):
            if m.get("username") == username:
                members.remove(m)
                if g.get("leader") == username:
                    if members:
                        g["leader"] = members[0]["username"]
                        members[0]["rank"] = "Leader"
                    else:
                        guilds_cache.remove(g)
                save_guilds()
                return True
    return False

def deposit_credits(username, amount):
    if amount <= 0 or not username:
        return False
    g = get_player_guild(username)
    if not g:
        return False

    user_data = state.all_player_data.get(state.current_user if state.current_user else "Guest", {})
    if user_data.get("credits", 0) < amount:
        return False

    user_data["credits"] -= amount
    g["bank_credits"] = g.get("bank_credits", 0) + amount
    g["xp"] = g.get("xp", 0) + amount
    if g["xp"] >= g.get("level", 1) * 5000:
        g["level"] = g.get("level", 1) + 1

    for m in g.get("members", []):
        if m.get("username") == username:
            m["contributions"] = m.get("contributions", 0) + amount
            break

    state.save_game_progress()
    save_guilds()
    return True

def upgrade_guild_perk(guild_name, perk_name, cost):
    for g in guilds_cache:
        if g.get("name") == guild_name:
            if g.get("bank_credits", 0) < cost:
                return False
            perks = g.setdefault("perks", [])
            if perk_name in perks:
                return False
            g["bank_credits"] -= cost
            perks.append(perk_name)
            save_guilds()
            return True
    return False

def send_guild_message(guild_tag, username, message):
    if not guild_tag or not username or not message:
        return False
    
    data = {}
    if os.path.exists(CHATS_FILE):
        try:
            with open(CHATS_FILE, "r") as f:
                data = json.load(f)
        except Exception:
            data = {}
    
    guild_chat = data.setdefault(guild_tag, [])
    guild_chat.append({
        "username": username,
        "message": message,
        "timestamp": os.path.getmtime(CHATS_FILE) if os.path.exists(CHATS_FILE) else 0
    })
    data[guild_tag] = guild_chat[-50:]
    
    try:
        with open(CHATS_FILE, "w") as f:
            json.dump(data, f, indent=4)
        return True
    except Exception:
        return False

def get_guild_messages(guild_tag):
    if not guild_tag:
        return []
    if not os.path.exists(CHATS_FILE):
        return []
    try:
        with open(CHATS_FILE, "r") as f:
            data = json.load(f)
            return data.get(guild_tag, [])
    except Exception:
        return []

def get_active_perks(username):
    g = get_player_guild(username)
    if not g:
        return {}
    
    active_bonuses = {}
    for perk in g.get("perks", []):
        bonus = AUTO_PERKS_MAP.get(perk)
        if bonus and bonus["type"] != "none":
            active_bonuses[bonus["type"]] = bonus["value"]
            
    return active_bonuses
