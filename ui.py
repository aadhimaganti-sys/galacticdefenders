import pygame
import random
import os
import sys
import math
from settings import *
import state
import megahack
import sound_manager
import account
import admin_panel
import json

stars = [
    [
        random.randint(0, SCREEN_WIDTH),
        random.randint(0, SCREEN_HEIGHT),
        random.uniform(1, 4),
        random.choice([(255,255,255), (150,150,255), (255,255,200), (200,200,255)])
    ]
    for _ in range(150)
]

def draw_text(text, font, color, x, y, surface, align="center", drop_shadow=False):
    if drop_shadow:
        shadow_surf = font.render(str(text), True, (0, 0, 0))
        shadow_rect = shadow_surf.get_rect()
        if align == "center": shadow_rect.center = (x + 3, y + 3)
        elif align == "left": shadow_rect.midleft = (x + 3, y + 3)
        elif align == "right": shadow_rect.midright = (x + 3, y + 3)
        elif align == "topleft": shadow_rect.topleft = (x + 3, y + 3)
        elif align == "topright": shadow_rect.topright = (x + 3, y + 3)
        elif align == "midtop": shadow_rect.midtop = (x + 3, y + 3)
        surface.blit(shadow_surf, shadow_rect)

    text_surface = font.render(str(text), True, color)
    rect = text_surface.get_rect()
    if align == "center": rect.center = (x, y)
    elif align == "left": rect.midleft = (x, y)
    elif align == "right": rect.midright = (x, y)
    elif align == "topleft": rect.topleft = (x, y)
    elif align == "topright": rect.topright = (x, y)
    elif align == "midtop": rect.midtop = (x, y)
    surface.blit(text_surface, rect)
    return rect

def draw_stars(surface):
    for s in stars:
        s[1] += s[2] * state.GAME_SPEED
        if s[1] > SCREEN_HEIGHT:
            s[1] = 0
            s[0] = random.randint(0, SCREEN_WIDTH)
        
        c = s[3] if s[2] > 2.5 else (max(0, s[3][0]-100), max(0, s[3][1]-100), max(0, s[3][2]-100))
        pygame.draw.circle(surface, c, (int(s[0]), int(s[1])), int(s[2]))

def draw_scrollable_menu(screen, options, offset, mouse_pos, title, font_t, color_t, y_t, currency=None):
    screen.fill(BLACK)
    draw_stars(screen)
    draw_text(title, font_t, color_t, SCREEN_WIDTH // 2, y_t, screen, drop_shadow=True)
    if currency:
        draw_text(currency, FONT_MEDIUM, YELLOW, SCREEN_WIDTH - 250, y_t, screen, align="right", drop_shadow=True)
        
    for opt in options:
        r = opt["rect"].copy()
        r.centery = opt["original_y"] + offset
        
        if r.bottom > y_t + 50 and r.top < SCREEN_HEIGHT - 100:
            color = opt.get("override_color", BUTTON_COLOR)
            is_hover = r.collidepoint(mouse_pos)
            if is_hover and not opt.get("is_owned", False):
                color = BUTTON_HOVER_COLOR
                pygame.draw.rect(screen, (100, 150, 255), r.inflate(6, 6), border_radius=12)
            if opt.get("is_owned", False):
                color = BUTTON_DISABLED_COLOR
                
            pygame.draw.rect(screen, color, r, border_radius=10)
            pygame.draw.rect(screen, (200, 220, 255) if is_hover else (80, 100, 140), r, 2 if is_hover else 1, border_radius=10)
            if "desc" in opt:
                draw_text(opt["text"], FONT_MEDIUM, WHITE, r.centerx, r.centery - 10, screen, drop_shadow=True)
                draw_text(opt["desc"], FONT_SMALL, LIGHT_GRAY, r.centerx, r.centery + 15, screen, drop_shadow=True)
            else:
                draw_text(opt["text"], FONT_MEDIUM, WHITE, r.centerx, r.centery, screen, drop_shadow=True)

def show_home_screen(screen, clock):
    selected_p1 = state.SHIP_TYPES.get(state.all_player_data["P1"]["selected_ship"], BASE_SHIP_TYPES["default_jet"])["name"]
    credits_p1 = state.all_player_data["P1"]["credits"]
    
    current_user_display = state.current_user if state.current_user else "P1 (Guest)"
    is_adm = state.current_user and account.is_admin(state.current_user)
    is_p = state.current_user and account.is_primary_admin(state.current_user)
    admin_tag = " [PRIMARY ADMIN]" if is_p else (" [ADMIN]" if is_adm else "")
    
    col1_options = [
        {"text": "Single Player (Classic)", "action": "PLAYING_SINGLE_CLASSIC", "color": (30, 80, 140)},
        {"text": "Single Player (Boss Mode)", "action": "PLAYING_SINGLE_BOSS", "color": (140, 40, 60)},
        {"text": "Local Co-op (Classic)", "action": "PLAYING_MULTI_CLASSIC", "color": (40, 100, 120)},
        {"text": "Local Co-op (Boss Mode)", "action": "PLAYING_MULTI_BOSS", "color": (120, 40, 90)},
        {"text": "Engine Room", "action": "ENGINE_ROOM", "color": (150, 100, 20)},
        {"text": "??? STORY CAMPAIGN ???", "action": "PLAYING_SPINOFF", "color": (180, 0, 80)},
        {"text": "ENTER SECRET PROTOCOL", "action": "PASSWORD_SCREEN", "color": (100, 0, 0)},
    ]
    
    col2_options = [
        {"text": "👤 Account / Login", "action": "ACCOUNT_SCREEN", "color": (50, 70, 110)},
        {"text": "Host LAN Game", "action": "HOST_LAN_MENU", "color": (40, 90, 130)},
        {"text": "Join LAN Game", "action": "JOIN_LAN_MENU", "color": (40, 90, 130)},
        {"text": "Host GLOBAL Cloud", "action": "HOST_CLOUD", "color": (100, 0, 150)},
        {"text": "Join GLOBAL Cloud", "action": "JOIN_CLOUD", "color": (100, 0, 150)},
        {"text": "Galactic Web Browser", "action": "WEB_BROWSER", "color": (0, 100, 100)},
        {"text": "Store / Armory (P1)", "action": "STORE_P1", "color": (60, 110, 50)},
        {"text": "Select Ship (P1)", "action": "SELECT_SHIP_P1", "color": (70, 90, 120)},
        {"text": "⚙️ Game Settings", "action": "GAME_SETTINGS", "color": (30, 80, 140)},
        {"text": "Datapack Mod Loader", "action": "MOD_LOADER", "color": (110, 60, 120)},
        {"text": "GUI Level Architect", "action": "LEVEL_EDITOR", "color": (0, 120, 60)},
        {"text": "Quit Game", "action": "QUIT_PROGRAM", "color": (120, 30, 30)},
    ]

    button_w = 340
    button_h = 34
    pad_y = 6
    
    center_x = SCREEN_WIDTH // 2
    col1_x = center_x - button_w - 20
    col2_x = center_x + 20
    
    y_start = 165

    for i, opt in enumerate(col1_options):
        opt["rect"] = pygame.Rect(col1_x, y_start + i * (38 + 8), button_w, 38)

    for i, opt in enumerate(col2_options):
        opt["rect"] = pygame.Rect(col2_x, y_start + i * (button_h + pad_y), button_w, button_h)

    all_buttons = col1_options + col2_options

    while True:
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT: 
                return "QUIT_PROGRAM"
            if megahack.handle_event(event): 
                continue
            
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for opt in all_buttons:
                    if opt["rect"].collidepoint(mouse_pos):
                        sound_manager.play_sfx("ui_click")
                        return opt["action"]
            if event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_q, pygame.K_ESCAPE]: 
                    sound_manager.play_sfx("ui_click")
                    return "QUIT_PROGRAM"
                if event.key in [pygame.K_BACKQUOTE, pygame.K_F12] or getattr(event, 'unicode', '') in ['`', '~']:
                    if getattr(state, "DEV_CONSOLE_ALLOWED", True):
                        sound_manager.play_sfx("ui_click")
                        return "DEV_CONSOLE"
                    else:
                        sound_manager.play_sfx("game_over", 0.4)

        screen.fill(BLACK)
        draw_stars(screen)
        
        # Header & Title
        draw_text("GALACTIC DEFENDERS", FONT_XLARGE, CYAN, center_x, 50, screen, drop_shadow=True)
        
        # Pilot Status Badge
        badge_w = 640
        badge_rect = pygame.Rect(center_x - badge_w // 2, 92, badge_w, 36)
        pygame.draw.rect(screen, (20, 25, 40), badge_rect, border_radius=18)
        pygame.draw.rect(screen, (60, 90, 140), badge_rect, 2, border_radius=18)
        user_col = YELLOW if is_p else (CYAN if is_adm else WHITE)
        draw_text(f"USER: {current_user_display}{admin_tag}   |   CREDITS: {credits_p1} Cr   |   SHIP: {selected_p1}", FONT_SMALL, user_col, center_x, 110, screen)
        
        # Column Headers
        draw_text("─── MISSION SELECT ───", FONT_SMALL, (150, 180, 220), col1_x + button_w // 2, y_start - 20, screen, drop_shadow=True)
        draw_text("─── NETWORK & HANGAR ───", FONT_SMALL, (150, 180, 220), col2_x + button_w // 2, y_start - 20, screen, drop_shadow=True)
        
        # Draw Buttons
        for opt in all_buttons:
            is_hover = opt["rect"].collidepoint(mouse_pos)
            base_col = opt.get("color", BUTTON_COLOR)
            c = BUTTON_HOVER_COLOR if is_hover else base_col
            if is_hover:
                pygame.draw.rect(screen, (100, 150, 255), opt["rect"].inflate(6, 6), border_radius=10)
            pygame.draw.rect(screen, c, opt["rect"], border_radius=8)
            pygame.draw.rect(screen, (200, 220, 255) if is_hover else (60, 70, 90), opt["rect"], 2 if is_hover else 1, border_radius=8)
            draw_text(opt["text"], FONT_MEDIUM if opt in col1_options else FONT_SMALL, WHITE, opt["rect"].centerx, opt["rect"].centery, screen, drop_shadow=True)

        # Bottom shortcut info
        draw_text("Press TAB for MegaHack Menu  |  ~ / F12 Dev Console  |  ESC Quit", FONT_SMALL, (120, 130, 150), center_x, SCREEN_HEIGHT - 25, screen)

        megahack.draw(screen)
        pygame.display.flip()
        clock.tick(int(FPS * state.GAME_SPEED))

def show_store_screen(screen, clock, player_id_str):
    player_id_key = str(player_id_str).upper()
    if player_id_key not in state.all_player_data:
        player_id_key = "P1"
    player_data = state.all_player_data[player_id_key]
    player_data.setdefault("credits", 0)
    player_data.setdefault("owned_ships", ["default_jet"])
    player_data.setdefault("unlocked_powers", ["power_autoshield"])
    has_mod_loader = "power_modloader" in player_data["unlocked_powers"]
    btn_h, pad, start_y, fixed_title_y = 60, 20, 150, 70
    store_items = []

    for ship_key, ship_data in state.SHIP_TYPES.items():
        if ship_key == "default_jet" or ship_data.get("cost") in ["CHIP_RARE", "CHIP_EPIC"]: continue
        cost_val = ship_data.get("cost", 0)
        cost_display = "FREE (Mod Loader)" if (has_mod_loader and ship_data.get("from_datapack", False)) else f"Cost: {cost_val} Cr"
        ship_name = ship_data.get("name", ship_key.replace("_", " ").title())
        ship_desc = ship_data.get("desc", "Custom Starship")
        store_items.append({"key": ship_key, "text": f"{ship_name} - {cost_display}", "original_y": 0, "rect": None, "data": ship_data, "is_owned": ship_key in player_data["owned_ships"], "desc": ship_desc})

    for helper_key, helper_data in state.HELPER_TYPES.items():
        cost_val = helper_data.get("cost", 0)
        cost_display = "FREE (Mod Loader)" if (has_mod_loader and helper_data.get("from_datapack", False)) else f"Cost: {cost_val} Cr"
        helper_name = helper_data.get("name", helper_key.replace("_", " ").title())
        helper_desc = helper_data.get("desc", "Custom Helper Unit")
        store_items.append({"key": helper_key, "text": f"{helper_name} - {cost_display}", "original_y": 0, "rect": None, "data": helper_data, "is_helper": True, "is_owned": helper_key in player_data["unlocked_powers"], "desc": helper_desc})

    for i, item in enumerate(store_items):
        item["original_y"] = start_y + i * (btn_h + pad + 20)
        item["rect"] = pygame.Rect(SCREEN_WIDTH // 2 - 250, item["original_y"], 500, btn_h)

    back_btn = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 60, 200, 50)
    scroll_offset = 0

    while True:
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT: return "QUIT_PROGRAM"
            if megahack.handle_event(event): continue
                
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    for item in store_items:
                        item_rect = item["rect"].copy()
                        item_rect.centery = item["original_y"] + scroll_offset
                        if item_rect.collidepoint(mouse_pos) and not item.get("is_owned", False):
                            item_cost = 0 if (has_mod_loader and item["data"].get("from_datapack", False)) else item["data"].get("cost", 0)
                            if isinstance(item_cost, int) and player_data["credits"] >= item_cost:
                                player_data["credits"] -= item_cost
                                if item.get("is_helper", False): player_data["unlocked_powers"].append(item["key"])
                                else: player_data["owned_ships"].append(item["key"])
                                item["is_owned"] = True
                                state.save_game_progress()
                                sound_manager.play_sfx("powerup_collect", 0.9)
                            else:
                                sound_manager.play_sfx("game_over", 0.4)
                    if back_btn.collidepoint(mouse_pos): 
                        sound_manager.play_sfx("ui_click")
                        return "HOME"
                elif event.button == 4: scroll_offset = min(scroll_offset + 80, 0)
                elif event.button == 5:
                    if store_items:
                        max_scroll = -((store_items[-1]["original_y"] - start_y + btn_h + 20) - (SCREEN_HEIGHT - (fixed_title_y + 120)))
                        scroll_offset = max(scroll_offset - 80, max_scroll) if max_scroll < 0 else 0
                        
            if event.type == pygame.KEYDOWN and event.key in [pygame.K_ESCAPE, pygame.K_h]: 
                sound_manager.play_sfx("ui_click")
                return "HOME"

        draw_scrollable_menu(screen, store_items, scroll_offset, mouse_pos, f"{player_id_key}'s Armory", FONT_LARGE, YELLOW, fixed_title_y, currency=f"Credits: {player_data['credits']}")
        pygame.draw.rect(screen, BUTTON_HOVER_COLOR if back_btn.collidepoint(mouse_pos) else BUTTON_COLOR, back_btn, border_radius=10)
        draw_text("Back to Home", FONT_MEDIUM, WHITE, back_btn.centerx, back_btn.centery, screen)
        
        megahack.draw(screen)
        pygame.display.flip()
        clock.tick(int(FPS * state.GAME_SPEED))

def show_ship_selection_screen(screen, clock, player_id_str):
    player_id_key = str(player_id_str).upper()
    if player_id_key not in state.all_player_data:
        player_id_key = "P1"
    player_data = state.all_player_data[player_id_key]
    player_data.setdefault("credits", 0)
    player_data.setdefault("owned_ships", ["default_jet"])
    player_data.setdefault("selected_ship", "default_jet")
    start_y, fixed_title_y = 150, 70
    selectable_ships = []

    for ship_key in player_data["owned_ships"]:
        ship_data = state.SHIP_TYPES.get(ship_key)
        if not ship_data: continue
        name = ship_data.get("name", ship_key.replace("_", " ").title())
        desc = ship_data.get("desc", "Custom Starship")
        text = name + (" [SELECTED]" if ship_key == player_data.get("selected_ship") else "")
        selectable_ships.append({"key": ship_key, "text": text, "original_y": 0, "rect": None, "data": ship_data, "desc": desc})

    for i, item in enumerate(selectable_ships):
        item["original_y"] = start_y + i * 85
        item["rect"] = pygame.Rect(SCREEN_WIDTH // 2 - 175, item["original_y"], 350, 50)

    back_btn = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 60, 200, 50)
    scroll_offset = 0

    while True:
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT: return "QUIT_PROGRAM"
            if megahack.handle_event(event): continue
                
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    for ship_item in selectable_ships:
                        item_rect = ship_item["rect"].copy()
                        item_rect.centery = ship_item["original_y"] + scroll_offset
                        if item_rect.collidepoint(mouse_pos):
                            player_data["selected_ship"] = ship_item["key"]
                            state.save_game_progress()
                            sound_manager.play_sfx("ui_click")
                            return "HOME"
                    if back_btn.collidepoint(mouse_pos): 
                        sound_manager.play_sfx("ui_click")
                        return "HOME"
                elif event.button == 4: scroll_offset = min(scroll_offset + 85, 0)
                elif event.button == 5:
                    if selectable_ships:
                        max_scroll = -((selectable_ships[-1]["original_y"] - start_y + 70) - (SCREEN_HEIGHT - (fixed_title_y + 120)))
                        scroll_offset = max(scroll_offset - 85, max_scroll) if max_scroll < 0 else 0
                        
            if event.type == pygame.KEYDOWN and event.key in [pygame.K_ESCAPE, pygame.K_h]: 
                sound_manager.play_sfx("ui_click")
                return "HOME"

        draw_scrollable_menu(screen, selectable_ships, scroll_offset, mouse_pos, "SHIP COLLECTION", FONT_LARGE, YELLOW, fixed_title_y, currency=f"Credits: {player_data['credits']}")
        pygame.draw.rect(screen, BUTTON_HOVER_COLOR if back_btn.collidepoint(mouse_pos) else BUTTON_COLOR, back_btn, border_radius=10)
        draw_text("Back to Home", FONT_MEDIUM, WHITE, back_btn.centerx, back_btn.centery, screen)
        
        megahack.draw(screen)
        pygame.display.flip()
        clock.tick(int(FPS * state.GAME_SPEED))

def show_mod_loader_screen(screen, clock):
    start_y, fixed_title_y = 155, 60
    center_x = SCREEN_WIDTH // 2
    
    enable_all_btn = pygame.Rect(center_x - 300, 105, 140, 36)
    disable_all_btn = pygame.Rect(center_x - 150, 105, 140, 36)
    install_demo_btn = pygame.Rect(center_x + 5, 105, 175, 36)
    back_btn = pygame.Rect(center_x + 190, 105, 110, 36)
    
    scroll_offset = 0
    toast_msg = ""
    toast_color = WIN_GREEN
    toast_time = 0

    while True:
        mods_dir = os.path.join(BASE_DIR, "mods")
        os.makedirs(mods_dir, exist_ok=True)
        
        mod_files = sorted([f for f in os.listdir(mods_dir) if f.endswith(".json")])
        for f in sorted(os.listdir(BASE_DIR)):
            if f.endswith(".json") and f not in ["galactic_defender_progress.json", "mod_config.json", "custom_level.json", "audio_config.json", "users.json"] and f not in mod_files:
                mod_files.append(f)
        
        mod_items = []
        for i, f_name in enumerate(mod_files):
            is_active = f_name in state.active_mods
            display_name = f_name
            desc_text = "Datapack Mod"
            
            try:
                mod_path = os.path.join(mods_dir, f_name) if os.path.exists(os.path.join(mods_dir, f_name)) else os.path.join(BASE_DIR, f_name)
                with open(mod_path, "r") as f:
                    mod_data = json.load(f)
                display_name = mod_data.get("name", f_name)
                
                ships_cnt = len(mod_data.get("ships", {}))
                helpers_cnt = len(mod_data.get("helpers", {}))
                powerups_cnt = len(mod_data.get("powerups", {}))
                parts = []
                if ships_cnt > 0: parts.append(f"{ships_cnt} Ships")
                if helpers_cnt > 0: parts.append(f"{helpers_cnt} Helpers")
                if powerups_cnt > 0: parts.append(f"{powerups_cnt} Powerups")
                desc_text = "Contains: " + (", ".join(parts) if parts else "Custom Datapack Content")
            except Exception:
                pass
                
            mod_items.append({
                "key": f_name, 
                "text": f"{display_name} [{'ACTIVE' if is_active else 'DISABLED'}]", 
                "desc": desc_text,
                "is_active": is_active,
                "original_y": start_y + i * 80, 
                "rect": pygame.Rect(center_x - 300, start_y + i * 80, 600, 68), 
                "override_color": (0, 100, 60) if is_active else (60, 30, 40)
            })

        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT: 
                return "QUIT_PROGRAM"
            if megahack.handle_event(event): 
                continue
                
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    for item in mod_items:
                        item_rect = item["rect"].copy()
                        item_rect.centery = item["original_y"] + scroll_offset
                        if item_rect.collidepoint(mouse_pos):
                            if item["key"] in state.active_mods: 
                                state.active_mods.remove(item["key"])
                                toast_msg = f"🔌 UNLOADED MOD: '{item['key']}'"
                                toast_color = RED
                            else: 
                                state.active_mods.append(item["key"])
                                toast_msg = f"✅ LOADED MOD: '{item['key']}' — Unlocked in Hangar & Store!"
                                toast_color = WIN_GREEN
                            state.save_mod_config()
                            state.reload_mods()
                            state.save_game_progress()
                            sound_manager.play_sfx("hack_toggle")
                            toast_time = pygame.time.get_ticks()
                            
                    if enable_all_btn.collidepoint(mouse_pos):
                        state.active_mods = list(mod_files)
                        state.save_mod_config()
                        state.reload_mods()
                        state.save_game_progress()
                        sound_manager.play_sfx("hack_toggle")
                        toast_msg = "✅ ALL MODS LOADED IN GAME!"
                        toast_color = WIN_GREEN
                        toast_time = pygame.time.get_ticks()

                    elif disable_all_btn.collidepoint(mouse_pos):
                        state.active_mods = []
                        state.save_mod_config()
                        state.reload_mods()
                        state.save_game_progress()
                        sound_manager.play_sfx("hack_toggle")
                        toast_msg = "🔌 ALL MODS UNLOADED"
                        toast_color = YELLOW
                        toast_time = pygame.time.get_ticks()

                    elif install_demo_btn.collidepoint(mouse_pos):
                        demo_path = os.path.join(mods_dir, "cyber_strike.json")
                        demo_data = {
                            "name": "Cyber Strike Pack",
                            "ships": {
                                "cyber_strike_x": {
                                    "name": "Cyber Strike X",
                                    "desc": "Ultra-light experimental interceptor built for high-speed plasma assaults.",
                                    "max_health": 250,
                                    "speed": 18,
                                    "base_speed": 18,
                                    "shoot_delay": 55,
                                    "start_blasters": 4,
                                    "color": [0, 255, 200],
                                    "wing_color": [255, 0, 150],
                                    "cost": 0,
                                    "unlocked_by_default": True
                                }
                            },
                            "helpers": {
                                "plasma_drone": {
                                    "name": "Plasma Interceptor Drone",
                                    "desc": "Automated plasma defense orb.",
                                    "cost": 0,
                                    "shoot_delay": 120,
                                    "color": [0, 255, 200],
                                    "unlocked_by_default": True
                                }
                            }
                        }
                        try:
                            with open(demo_path, "w") as f:
                                json.dump(demo_data, f, indent=4)
                            if "cyber_strike.json" not in state.active_mods:
                                state.active_mods.append("cyber_strike.json")
                            state.save_mod_config()
                            state.reload_mods()
                            state.save_game_progress()
                            sound_manager.play_sfx("hack_toggle")
                            toast_msg = "✨ INSTALLED DEMO MOD! 'Cyber Strike X' unlocked in Hangar!"
                            toast_color = WIN_GREEN
                            toast_time = pygame.time.get_ticks()
                        except Exception as e:
                            toast_msg = f"Failed to install demo mod: {e}"
                            toast_color = RED
                            toast_time = pygame.time.get_ticks()

                    elif back_btn.collidepoint(mouse_pos): 
                        sound_manager.play_sfx("ui_click")
                        return "HOME"

                elif event.button == 4: 
                    scroll_offset = min(scroll_offset + 80, 0)
                elif event.button == 5:
                    if mod_items:
                        max_scroll = -((mod_items[-1]["original_y"] - start_y + 80) - (SCREEN_HEIGHT - (fixed_title_y + 120)))
                        scroll_offset = max(scroll_offset - 80, max_scroll) if max_scroll < 0 else 0
                        
            if event.type == pygame.KEYDOWN and event.key in [pygame.K_ESCAPE, pygame.K_h]: 
                sound_manager.play_sfx("ui_click")
                return "HOME"

        draw_scrollable_menu(screen, mod_items, scroll_offset, mouse_pos, "DATAPACK MOD LOADER", FONT_LARGE, MAGENTA, fixed_title_y)
        
        h_ena = enable_all_btn.collidepoint(mouse_pos)
        pygame.draw.rect(screen, (0, 140, 60) if h_ena else (0, 90, 40), enable_all_btn, border_radius=6)
        draw_text("⚡ Enable All", FONT_SMALL, WHITE, enable_all_btn.centerx, enable_all_btn.centery, screen)

        h_dis = disable_all_btn.collidepoint(mouse_pos)
        pygame.draw.rect(screen, (140, 40, 40) if h_dis else (90, 30, 30), disable_all_btn, border_radius=6)
        draw_text("🔌 Disable All", FONT_SMALL, WHITE, disable_all_btn.centerx, disable_all_btn.centery, screen)

        h_demo = install_demo_btn.collidepoint(mouse_pos)
        pygame.draw.rect(screen, (120, 40, 140) if h_demo else (80, 20, 100), install_demo_btn, border_radius=6)
        draw_text("✨ Install Demo Mod", FONT_SMALL, WHITE, install_demo_btn.centerx, install_demo_btn.centery, screen)

        h_back = back_btn.collidepoint(mouse_pos)
        pygame.draw.rect(screen, BUTTON_HOVER_COLOR if h_back else BUTTON_COLOR, back_btn, border_radius=6)
        draw_text("⬅ Home", FONT_SMALL, WHITE, back_btn.centerx, back_btn.centery, screen)

        if toast_msg and pygame.time.get_ticks() - toast_time < 3500:
            toast_bg = pygame.Rect(center_x - 300, SCREEN_HEIGHT - 55, 600, 36)
            pygame.draw.rect(screen, (20, 25, 40), toast_bg, border_radius=8)
            pygame.draw.rect(screen, toast_color, toast_bg, 2, border_radius=8)
            draw_text(toast_msg, FONT_SMALL, toast_color, center_x, toast_bg.centery, screen)

        megahack.draw(screen)
        pygame.display.flip()
        clock.tick(int(FPS * state.GAME_SPEED))

def show_password_screen(screen, clock):
    input_text, error_msg, error_time = "", "", 0
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: return "QUIT_PROGRAM"
            if megahack.handle_event(event): continue
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: 
                    sound_manager.play_sfx("ui_click")
                    return "HOME"
                elif event.key == pygame.K_RETURN:
                    if input_text.strip().upper() == "OMEGA": 
                        sound_manager.play_sfx("victory")
                        return "PLAYING_ULTIMATE_BOSS"
                    else: 
                        sound_manager.play_sfx("game_over", 0.4)
                        error_msg, error_time, input_text = "ACCESS DENIED.", pygame.time.get_ticks(), ""
                elif event.key == pygame.K_BACKSPACE: input_text = input_text[:-1]
                elif event.unicode.isprintable(): 
                    input_text += event.unicode
                    sound_manager.play_sfx("dialogue_beep", 0.4)
        
        screen.fill(BLACK)
        draw_stars(screen)
        draw_text("RESTRICTED PROTOCOL", FONT_LARGE, RED, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3, screen)
        input_rect = pygame.Rect(SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT // 2, 400, 50)
        pygame.draw.rect(screen, DARK_GRAY, input_rect, border_radius=10)
        
        text_surf = FONT_MEDIUM.render(input_text, True, YELLOW)
        screen.blit(text_surf, (input_rect.x + 10, input_rect.y + 10))
        
        if error_msg and pygame.time.get_ticks() - error_time < 2000:
            draw_text(error_msg, FONT_MEDIUM, RED, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 80, screen)
            
        megahack.draw(screen)
        pygame.display.flip()
        clock.tick(int(FPS * state.GAME_SPEED))

def show_account_screen(screen, clock):
    username_input = ""
    password_input = ""
    active_field = "username"  # "username" or "password"
    
    status_msg = ""
    status_color = WIN_GREEN
    status_time = 0

    while True:
        mouse_pos = pygame.mouse.get_pos()
        
        center_x = SCREEN_WIDTH // 2
        user_rect = pygame.Rect(center_x - 180, 230, 360, 42)
        pass_rect = pygame.Rect(center_x - 180, 310, 360, 42)
        
        login_btn = pygame.Rect(center_x - 180, 375, 175, 45)
        register_btn = pygame.Rect(center_x + 5, 375, 175, 45)
        logout_btn = pygame.Rect(center_x - 180, 430, 360, 40)
        back_btn = pygame.Rect(center_x - 180, 480, 360, 40)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "QUIT_PROGRAM"
            if megahack.handle_event(event):
                continue

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if user_rect.collidepoint(mouse_pos):
                    active_field = "username"
                    sound_manager.play_sfx("ui_click")
                elif pass_rect.collidepoint(mouse_pos):
                    active_field = "password"
                    sound_manager.play_sfx("ui_click")
                elif login_btn.collidepoint(mouse_pos):
                    sound_manager.play_sfx("ui_click")
                    u = username_input.strip()
                    p = password_input.strip()
                    if account.login(u, p):
                        state.current_user = u
                        u_data = account.load_user_data(u)
                        if u_data:
                            state.all_player_data["P1"].update(u_data)
                        status_msg = f"Successfully logged in as '{u}'!"
                        status_color = WIN_GREEN
                        status_time = pygame.time.get_ticks()
                    else:
                        status_msg = "Invalid username or password!"
                        status_color = RED
                        status_time = pygame.time.get_ticks()
                elif register_btn.collidepoint(mouse_pos):
                    sound_manager.play_sfx("ui_click")
                    u = username_input.strip()
                    p = password_input.strip()
                    if account.register(u, p):
                        state.current_user = u
                        is_adm = account.is_admin(u)
                        tag = " (Primary Admin)" if is_adm else ""
                        status_msg = f"Registered & logged in as '{u}'{tag}!"
                        status_color = WIN_GREEN
                        status_time = pygame.time.get_ticks()
                    else:
                        status_msg = "Registration failed (username taken or blank)."
                        status_color = RED
                        status_time = pygame.time.get_ticks()
                elif logout_btn.collidepoint(mouse_pos) and state.current_user:
                    sound_manager.play_sfx("ui_click")
                    state.current_user = None
                    account.set_active_session(None)
                    status_msg = "Logged out."
                    status_color = YELLOW
                    status_time = pygame.time.get_ticks()
                elif back_btn.collidepoint(mouse_pos):
                    sound_manager.play_sfx("ui_click")
                    return "HOME"

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "HOME"
                elif event.key == pygame.K_TAB:
                    active_field = "password" if active_field == "username" else "username"
                elif event.key == pygame.K_RETURN:
                    u = username_input.strip()
                    p = password_input.strip()
                    if account.login(u, p):
                        state.current_user = u
                        u_data = account.load_user_data(u)
                        if u_data:
                            state.all_player_data["P1"].update(u_data)
                        status_msg = f"Successfully logged in as '{u}'!"
                        status_color = WIN_GREEN
                        status_time = pygame.time.get_ticks()
                    else:
                        status_msg = "Invalid username or password!"
                        status_color = RED
                        status_time = pygame.time.get_ticks()
                elif event.key == pygame.K_BACKSPACE:
                    if active_field == "username":
                        username_input = username_input[:-1]
                    else:
                        password_input = password_input[:-1]
                elif event.unicode.isprintable():
                    if active_field == "username":
                        username_input += event.unicode
                    else:
                        password_input += event.unicode
                    sound_manager.play_sfx("dialogue_beep", 0.3)

        screen.fill(BLACK)
        draw_stars(screen)

        draw_text("ACCOUNT MANAGEMENT", FONT_LARGE, CYAN, center_x, 50, screen)
        
        badge_rect = pygame.Rect(center_x - 220, 105, 440, 40)
        pygame.draw.rect(screen, (20, 30, 50), badge_rect, border_radius=10)
        pygame.draw.rect(screen, (60, 90, 140), badge_rect, 2, border_radius=10)
        if state.current_user:
            is_adm = account.is_admin(state.current_user)
            is_p = account.is_primary_admin(state.current_user)
            role_str = "PRIMARY ADMIN" if is_p else ("ADMIN" if is_adm else "PLAYER")
            role_col = YELLOW if is_p else (CYAN if is_adm else WHITE)
            draw_text(f"Logged in as: {state.current_user} [{role_str}]", FONT_MEDIUM, role_col, center_x, 125, screen)
        else:
            draw_text("Not Logged In (Playing as Guest)", FONT_MEDIUM, LIGHT_GRAY, center_x, 125, screen)

        draw_text("Username:", FONT_SMALL, WHITE, user_rect.x, user_rect.y - 15, screen, align="left")
        draw_text("Password:", FONT_SMALL, WHITE, pass_rect.x, pass_rect.y - 15, screen, align="left")

        u_border = CYAN if active_field == "username" else (60, 70, 90)
        pygame.draw.rect(screen, DARK_GRAY, user_rect, border_radius=8)
        pygame.draw.rect(screen, u_border, user_rect, 2, border_radius=8)
        draw_text(username_input + ("|" if active_field == "username" and (pygame.time.get_ticks() // 500) % 2 == 0 else ""), FONT_MEDIUM, WHITE, user_rect.x + 10, user_rect.centery, screen, align="left")

        p_border = CYAN if active_field == "password" else (60, 70, 90)
        pygame.draw.rect(screen, DARK_GRAY, pass_rect, border_radius=8)
        pygame.draw.rect(screen, p_border, pass_rect, 2, border_radius=8)
        masked_pass = "*" * len(password_input)
        draw_text(masked_pass + ("|" if active_field == "password" and (pygame.time.get_ticks() // 500) % 2 == 0 else ""), FONT_MEDIUM, WHITE, pass_rect.x + 10, pass_rect.centery, screen, align="left")

        h_login = login_btn.collidepoint(mouse_pos)
        pygame.draw.rect(screen, BUTTON_HOVER_COLOR if h_login else BUTTON_COLOR, login_btn, border_radius=8)
        draw_text("Log In", FONT_MEDIUM, WHITE, login_btn.centerx, login_btn.centery, screen)

        h_reg = register_btn.collidepoint(mouse_pos)
        pygame.draw.rect(screen, (0, 120, 60) if h_reg else (0, 80, 40), register_btn, border_radius=8)
        draw_text("Register", FONT_MEDIUM, WHITE, register_btn.centerx, register_btn.centery, screen)

        if state.current_user:
            h_out = logout_btn.collidepoint(mouse_pos)
            pygame.draw.rect(screen, (140, 40, 40) if h_out else (100, 20, 20), logout_btn, border_radius=8)
            draw_text("Log Out Current Account", FONT_MEDIUM, WHITE, logout_btn.centerx, logout_btn.centery, screen)

        h_back = back_btn.collidepoint(mouse_pos)
        pygame.draw.rect(screen, BUTTON_HOVER_COLOR if h_back else (40, 50, 70), back_btn, border_radius=8)
        draw_text("Back to Home", FONT_MEDIUM, WHITE, back_btn.centerx, back_btn.centery, screen)

        if status_msg and pygame.time.get_ticks() - status_time < 3500:
            draw_text(status_msg, FONT_SMALL, status_color, center_x, SCREEN_HEIGHT - 60, screen)

        megahack.draw(screen)
        pygame.display.flip()
        clock.tick(int(FPS * state.GAME_SPEED))


def show_dev_console(screen, clock):
    """Developer Console Terminal.
    Accessible only if DEV_CONSOLE_ALLOWED is enabled and player presses the ` key.
    Pressing F4 opens Admin Control Panel (requires Admin account and Dev Console enabled).
    """
    if not getattr(state, "DEV_CONSOLE_ALLOWED", True):
        return "HOME"

    is_admin = bool(state.current_user and account.is_admin(state.current_user))
    font_mono = pygame.font.SysFont("monospace", 17)
    font_mono_bold = pygame.font.SysFont("monospace", 18, bold=True)

    center_x = SCREEN_WIDTH // 2
    win_w = 820
    win_h = 580
    win_rect = pygame.Rect(center_x - win_w // 2, 40, win_w, win_h)

    logs = [
        "[SYSTEM] Galactic Defenders Developer Terminal initialized.",
        f"[SYSTEM] Dev Console: ALLOWED | User: {state.current_user or 'Guest'} | Role: {'ADMIN' if is_admin else 'GUEST/USER'}",
        "[HOTKEY] Press [F4] to access Admin Control Panel (Admin privileges required).",
        "[INFO] Type 'help' for command list, or press [ESC] / [ ` ] to return to menu.",
        "--------------------------------------------------------------------------------",
    ]

    if not is_admin:
        logs.append("[NOTICE] Admin Control Panel is locked. Log in as an Admin to unlock [F4].")

    input_text = ""
    cursor_visible = True
    last_cursor_toggle = pygame.time.get_ticks()

    f4_btn = pygame.Rect(win_rect.left + 20, win_rect.bottom - 48, 260, 36)
    acc_btn = pygame.Rect(win_rect.left + 295, win_rect.bottom - 48, 200, 36)
    exit_btn = pygame.Rect(win_rect.right - 180, win_rect.bottom - 48, 160, 36)
    prompt_rect = pygame.Rect(win_rect.left + 20, win_rect.bottom - 95, win_rect.width - 40, 36)

    def try_open_admin():
        dev_allowed = getattr(state, "DEV_CONSOLE_ALLOWED", True)
        cur_is_admin = bool(state.current_user and account.is_admin(state.current_user))
        if dev_allowed and cur_is_admin:
            sound_manager.play_sfx("ui_click")
            return "ADMIN_PANEL"
        else:
            sound_manager.play_sfx("game_over", 0.6)
            if not dev_allowed:
                logs.append("[ACCESS DENIED] Developer Console is disabled in Settings.")
            elif not state.current_user:
                logs.append("[ACCESS DENIED] You are not logged in. Admin account required for Admin Panel.")
            else:
                logs.append(f"[ACCESS DENIED] Account '{state.current_user}' does not have Admin privileges.")
            return None

    while True:
        if not getattr(state, "DEV_CONSOLE_ALLOWED", True):
            return "HOME"

        now = pygame.time.get_ticks()
        if now - last_cursor_toggle > 500:
            cursor_visible = not cursor_visible
            last_cursor_toggle = now

        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "QUIT_PROGRAM"
            if megahack.handle_event(event):
                continue

            if event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_ESCAPE, pygame.K_BACKQUOTE] or getattr(event, 'unicode', '') in ['`', '~']:
                    sound_manager.play_sfx("ui_click")
                    return "HOME"
                elif event.key == pygame.K_F4:
                    res = try_open_admin()
                    if res:
                        return res
                elif event.key == pygame.K_RETURN:
                    cmd_line = input_text.strip()
                    if cmd_line:
                        logs.append(f"> {cmd_line}")
                        cmd_parts = cmd_line.split()
                        cmd = cmd_parts[0].lower()
                        args = cmd_parts[1:]

                        if cmd in ["f4", "admin", "admin_panel"]:
                            res = try_open_admin()
                            if res:
                                return res
                        elif cmd == "help":
                            logs.append("Available Commands:")
                            logs.append("  f4 / admin       - Open Admin Control Panel (requires Admin)")
                            logs.append("  status           - Show system, user, and dev status")
                            logs.append("  give_coins <n>   - Add <n> credits to Player 1")
                            logs.append("  godmode          - Toggle invincibility for testing")
                            logs.append("  speed <val>      - Set game speed multiplier (e.g. 1.0, 1.5)")
                            logs.append("  account          - Open Account / Login screen")
                            logs.append("  clear            - Clear terminal log output")
                            logs.append("  exit / quit      - Return to main menu")
                        elif cmd == "status":
                            logs.append(f"[STATUS] User: {state.current_user or 'Guest'} | Admin: {account.is_admin(state.current_user) if state.current_user else False}")
                            logs.append(f"[STATUS] Dev Console Allowed: {getattr(state, 'DEV_CONSOLE_ALLOWED', True)} | Speed: {state.GAME_SPEED}x | God Mode: {getattr(state, 'ADMIN_GOD_MODE', False)}")
                            logs.append(f"[STATUS] P1 Credits: {state.all_player_data.get('P1', {}).get('credits', 0):,} | Active Mods: {len(state.active_mods)}")
                        elif cmd == "clear":
                            logs.clear()
                            logs.append("[SYSTEM] Terminal cleared.")
                        elif cmd in ["exit", "quit", "q"]:
                            sound_manager.play_sfx("ui_click")
                            return "HOME"
                        elif cmd == "account":
                            sound_manager.play_sfx("ui_click")
                            return "ACCOUNT_SCREEN"
                        elif cmd == "godmode":
                            state.ADMIN_GOD_MODE = not getattr(state, "ADMIN_GOD_MODE", False)
                            logs.append(f"[SUCCESS] God Mode set to: {state.ADMIN_GOD_MODE}")
                            sound_manager.play_sfx("hack_toggle")
                        elif cmd in ["give_coins", "coins", "credits"]:
                            if args and args[0].lstrip("-").isdigit():
                                amt = int(args[0])
                                p1_data = state.all_player_data.setdefault("P1", {})
                                p1_data["credits"] = max(0, p1_data.get("credits", 0) + amt)
                                state.save_game_progress()
                                logs.append(f"[SUCCESS] Added {amt:,} credits to P1. New balance: {p1_data['credits']:,}")
                                sound_manager.play_sfx("powerup_collect")
                            else:
                                logs.append("[ERROR] Usage: give_coins <amount>")
                        elif cmd == "speed":
                            if args:
                                try:
                                    spd = float(args[0])
                                    state.GAME_SPEED = max(0.1, min(5.0, spd))
                                    logs.append(f"[SUCCESS] Game speed set to {state.GAME_SPEED}x")
                                except ValueError:
                                    logs.append("[ERROR] Invalid speed value. E.g. speed 1.5")
                            else:
                                logs.append("[ERROR] Usage: speed <multiplier>")
                        else:
                            logs.append(f"[ERROR] Unknown command: '{cmd}'. Type 'help' for commands.")
                    input_text = ""
                elif event.key == pygame.K_BACKSPACE:
                    input_text = input_text[:-1]
                else:
                    if event.unicode and event.unicode.isprintable() and event.unicode not in ['`', '~']:
                        input_text += event.unicode

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if f4_btn.collidepoint(mouse_pos):
                    res = try_open_admin()
                    if res:
                        return res
                elif acc_btn.collidepoint(mouse_pos):
                    sound_manager.play_sfx("ui_click")
                    return "ACCOUNT_SCREEN"
                elif exit_btn.collidepoint(mouse_pos):
                    sound_manager.play_sfx("ui_click")
                    return "HOME"

        screen.fill(BLACK)
        draw_stars(screen)

        # Draw Window Frame
        pygame.draw.rect(screen, (10, 16, 26), win_rect, border_radius=10)
        pygame.draw.rect(screen, (0, 180, 240), win_rect, 2, border_radius=10)

        # Title Bar
        title_bar = pygame.Rect(win_rect.left, win_rect.top, win_rect.width, 42)
        pygame.draw.rect(screen, (18, 30, 50), title_bar, border_top_left_radius=10, border_top_right_radius=10)
        pygame.draw.line(screen, (0, 180, 240), (win_rect.left, win_rect.top + 42), (win_rect.right, win_rect.top + 42), 2)
        
        draw_text("💻 DEVELOPER CONSOLE", FONT_MEDIUM, CYAN, win_rect.left + 20, title_bar.centery, screen, align="left")
        
        cur_adm = bool(state.current_user and account.is_admin(state.current_user))
        user_str = f"User: {state.current_user or 'Guest'} [{'ADMIN' if cur_adm else 'USER'}]"
        role_color = WIN_GREEN if cur_adm else YELLOW
        draw_text(user_str, FONT_SMALL, role_color, win_rect.right - 20, title_bar.centery, screen, align="right")

        # Terminal Output Box
        log_box = pygame.Rect(win_rect.left + 15, win_rect.top + 50, win_rect.width - 30, win_rect.height - 158)
        pygame.draw.rect(screen, (5, 8, 14), log_box, border_radius=6)
        pygame.draw.rect(screen, (30, 50, 75), log_box, 1, border_radius=6)

        # Draw visible logs (last 16 lines)
        visible_lines = logs[-16:]
        line_y = log_box.top + 10
        for l in visible_lines:
            c = (220, 225, 235)
            if l.startswith("[ACCESS DENIED]") or l.startswith("[ERROR]"):
                c = (255, 80, 80)
            elif l.startswith("[SUCCESS]"):
                c = (80, 255, 120)
            elif l.startswith("[HOTKEY]") or l.startswith("[NOTICE]"):
                c = (255, 220, 60)
            elif l.startswith("[SYSTEM]") or l.startswith("[DEV CONSOLE]") or l.startswith("[STATUS]"):
                c = (80, 210, 255)
            elif l.startswith(">"):
                c = (140, 255, 160)
            
            txt_surf = font_mono.render(l, True, c)
            screen.blit(txt_surf, (log_box.left + 12, line_y))
            line_y += 24

        # Prompt input box
        pygame.draw.rect(screen, (12, 20, 32), prompt_rect, border_radius=6)
        pygame.draw.rect(screen, CYAN if prompt_rect.collidepoint(mouse_pos) else (40, 70, 110), prompt_rect, 1, border_radius=6)
        
        display_input = "> " + input_text + ("_" if cursor_visible else " ")
        prompt_surf = font_mono_bold.render(display_input, True, (0, 255, 200))
        screen.blit(prompt_surf, (prompt_rect.left + 10, prompt_rect.centery - 9))

        # Bottom Buttons
        # F4 Button
        f4_hover = f4_btn.collidepoint(mouse_pos)
        f4_col = (140, 30, 30) if not cur_adm else ((0, 140, 80) if f4_hover else (0, 100, 60))
        if not cur_adm and f4_hover:
            f4_col = (180, 40, 40)
        pygame.draw.rect(screen, f4_col, f4_btn, border_radius=6)
        f4_text = "🔒 F4: Admin Panel (Locked)" if not cur_adm else "⚡ F4: Admin Control Panel"
        draw_text(f4_text, FONT_SMALL, WHITE, f4_btn.centerx, f4_btn.centery, screen)

        # Account / Login Button
        acc_hover = acc_btn.collidepoint(mouse_pos)
        pygame.draw.rect(screen, (60, 90, 130) if acc_hover else (40, 60, 90), acc_btn, border_radius=6)
        draw_text("👤 Account Login", FONT_SMALL, WHITE, acc_btn.centerx, acc_btn.centery, screen)

        # Exit Button
        exit_hover = exit_btn.collidepoint(mouse_pos)
        pygame.draw.rect(screen, (90, 40, 50) if exit_hover else (60, 30, 40), exit_btn, border_radius=6)
        draw_text("⬅ Exit (~ / ESC)", FONT_SMALL, WHITE, exit_btn.centerx, exit_btn.centery, screen)

        megahack.draw(screen)
        pygame.display.flip()
        clock.tick(int(FPS * state.GAME_SPEED))


def show_terminal_admin_panel(screen, clock):
    """In-Game Terminal Admin Control Panel.
    Renders directly on the Pygame canvas with interactive command prompt
    and quick buttons for all admin functions (1-9):
      1) List all registered users
      2) View user data
      3) Edit user credits
      4) Delete user
      5) List admin users
      6) Toggle admin rights
      7) Toggle God Mode
      8) Give +10,000 credits to P1
      9) Switch to GUI Admin Panel
      0) Exit Admin Panel
    """
    is_authorized = bool(getattr(state, "DEV_CONSOLE_ALLOWED", True) and state.current_user and account.is_admin(state.current_user))
    if not is_authorized:
        return show_admin_options(screen, clock)

    is_primary = account.is_primary_admin(state.current_user)
    role_str = "PRIMARY ADMIN" if is_primary else "ADMIN"

    font_mono = pygame.font.SysFont("monospace", 15)
    font_mono_bold = pygame.font.SysFont("monospace", 16, bold=True)

    win_rect = pygame.Rect(30, 25, 840, 650)
    log_box = pygame.Rect(45, 80, 520, 515)
    prompt_rect = pygame.Rect(45, 610, 520, 45)

    logs = [
        "╔══════════════════════════════════════════════════════════════════════╗",
        "║      GALACTIC DEFENDERS - IN-GAME TERMINAL ADMIN CONTROL PANEL       ║",
        f"║  Status: AUTHORIZED  |  User: {state.current_user:<15} [{role_str:<13}]  ║",
        "╚══════════════════════════════════════════════════════════════════════╝",
        " Select an option (Type number in prompt or click button):",
        "  [1] List all registered users",
        "  [2] View user account data",
        "  [3] Edit user credits / high score",
        "  [4] Delete user account",
        "  [5] List admin users",
        "  [6] Toggle admin privileges",
        "  [7] Toggle God Mode (Invincibility)",
        "  [8] Give +10,000 Credits to P1",
        "  [9] Switch to GUI Admin Panel",
        "  [0] Exit to Main Menu (ESC / `)",
        "────────────────────────────────────────────────────────────────────────",
    ]

    input_text = ""
    input_mode = "MAIN"
    pending_user = ""
    cursor_visible = True
    last_cursor_toggle = pygame.time.get_ticks()

    btn_x = 580
    btn_w = 275
    btn_h = 44
    btn_gap = 10
    by_start = 80

    cmd_buttons = [
        (1, "1. 👥 List All Users", (30, 60, 100)),
        (2, "2. 🔍 View User Data", (20, 80, 90)),
        (3, "3. 💰 Edit User Credits", (20, 90, 60)),
        (4, "4. 🗑️ Delete Account", (130, 30, 30)),
        (5, "5. ⭐ List Admin Accounts", (100, 75, 20)),
        (6, "6. 🛡️ Toggle Admin Rights", (110, 45, 90)),
        (7, "7. ⚡ Toggle God Mode", (0, 120, 70)),
        (8, "8. 💎 Give +10k Credits", (50, 80, 130)),
        (9, "9. 🖥️ GUI Admin Screen", (70, 40, 110)),
        (0, "0. ⬅ Exit Admin (ESC)", (60, 30, 40)),
    ]

    btn_rects = []
    for i, (num, label, col) in enumerate(cmd_buttons):
        r = pygame.Rect(btn_x, by_start + i * (btn_h + btn_gap), btn_w, btn_h)
        btn_rects.append((num, label, col, r))

    def execute_option(num):
        nonlocal input_mode, pending_user, input_text
        if num == 1:
            logs.append("[CMD 1] Registered Accounts:")
            users = account.list_all_usernames()
            if not users:
                logs.append("  (No users registered)")
            for u in users:
                adm = " (admin)" if account.is_admin(u) else ""
                prim = " [PRIMARY]" if account.is_primary_admin(u) else ""
                u_data = account.load_user_data(u)
                c_val = u_data.get("credits", 0)
                logs.append(f"  • {u:<14} {adm}{prim} | Credits: {c_val:,}")
            sound_manager.play_sfx("ui_click")

        elif num == 2:
            input_mode = "VIEW_USER"
            input_text = ""
            logs.append("────────────────────────────────────────")
            logs.append("Enter username to inspect data:")
            sound_manager.play_sfx("ui_click")

        elif num == 3:
            input_mode = "EDIT_NAME"
            input_text = ""
            logs.append("────────────────────────────────────────")
            logs.append("Enter username to modify credits:")
            sound_manager.play_sfx("ui_click")

        elif num == 4:
            input_mode = "DEL_USER"
            input_text = ""
            logs.append("────────────────────────────────────────")
            logs.append("Enter username to DELETE:")
            sound_manager.play_sfx("ui_click")

        elif num == 5:
            logs.append("[CMD 5] System Administrators:")
            admins = [u for u in account.list_all_usernames() if account.is_admin(u)]
            for u in admins:
                prim = " [PRIMARY]" if account.is_primary_admin(u) else ""
                logs.append(f"  ★ {u}{prim}")
            sound_manager.play_sfx("ui_click")

        elif num == 6:
            input_mode = "TOGGLE_ADMIN"
            input_text = ""
            logs.append("────────────────────────────────────────")
            logs.append("Enter username to toggle admin privileges:")
            sound_manager.play_sfx("ui_click")

        elif num == 7:
            state.ADMIN_GOD_MODE = not getattr(state, "ADMIN_GOD_MODE", False)
            logs.append(f"[TOGGLE] God Mode is now: {'ENABLED' if state.ADMIN_GOD_MODE else 'OFF'}")
            sound_manager.play_sfx("hack_toggle")

        elif num == 8:
            p1 = state.all_player_data.setdefault("P1", {})
            p1["credits"] = p1.get("credits", 0) + 10000
            state.save_game_progress()
            logs.append(f"[SUCCESS] Added +10,000 credits to P1! Total: {p1['credits']:,}")
            sound_manager.play_sfx("powerup_collect")

        elif num == 9:
            sound_manager.play_sfx("ui_click")
            res = show_admin_options(screen, clock)
            if res == "QUIT_PROGRAM":
                return "QUIT_PROGRAM"
            logs.append("[SYSTEM] Returned to In-Game Terminal Admin Panel.")

        elif num == 0:
            sound_manager.play_sfx("ui_click")
            return "HOME"
        return None

    while True:
        if not getattr(state, "DEV_CONSOLE_ALLOWED", True):
            return "HOME"

        now = pygame.time.get_ticks()
        if now - last_cursor_toggle > 500:
            cursor_visible = not cursor_visible
            last_cursor_toggle = now

        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "QUIT_PROGRAM"
            if megahack.handle_event(event):
                continue

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for num, label, col, r in btn_rects:
                    if r.collidepoint(mouse_pos):
                        action_res = execute_option(num)
                        if action_res:
                            return action_res
                        break

            if event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_ESCAPE, pygame.K_BACKQUOTE] and input_mode == "MAIN":
                    sound_manager.play_sfx("ui_click")
                    return "HOME"
                elif event.key == pygame.K_ESCAPE and input_mode != "MAIN":
                    input_mode = "MAIN"
                    input_text = ""
                    logs.append("[CANCELLED] Operation aborted.")
                    sound_manager.play_sfx("ui_click")
                elif event.key == pygame.K_RETURN:
                    typed = input_text.strip()
                    input_text = ""

                    if input_mode == "MAIN":
                        if typed in ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"]:
                            action_res = execute_option(int(typed))
                            if action_res:
                                return action_res
                        elif typed.lower() in ["help", "h"]:
                            logs.append("Select 1-9 or 0: 1=List, 2=View, 3=Edit, 4=Del, 5=Admins, 6=AdminToggle, 7=GodMode, 8=+10k, 9=GUI, 0=Exit")
                        elif typed.lower() in ["clear", "cls"]:
                            logs.clear()
                            logs.append("[SYSTEM] Terminal screen cleared.")
                        elif typed.lower() in ["exit", "quit", "q"]:
                            return "HOME"
                        elif typed:
                            logs.append(f"[ERROR] Invalid option '{typed}'. Choose 1-9, or 0 to exit.")
                            sound_manager.play_sfx("game_over", 0.4)

                    elif input_mode == "VIEW_USER":
                        logs.append(f"> {typed}")
                        data = account.load_user_data(typed)
                        if not data or typed not in account.list_all_usernames():
                            logs.append(f"[ERROR] User '{typed}' not found.")
                            sound_manager.play_sfx("game_over", 0.4)
                        else:
                            logs.append(f"[DATA] Account Details for '{typed}':")
                            logs.append(f"  Credits: {data.get('credits', 0):,} | High Score: {data.get('score', 0):,}")
                            logs.append(f"  Ships: {data.get('owned_ships', ['default_jet'])}")
                            logs.append(f"  Admin: {account.is_admin(typed)} | Primary Admin: {account.is_primary_admin(typed)}")
                            sound_manager.play_sfx("ui_click")
                        input_mode = "MAIN"

                    elif input_mode == "EDIT_NAME":
                        logs.append(f"> {typed}")
                        if typed not in account.list_all_usernames():
                            logs.append(f"[ERROR] User '{typed}' not found.")
                            sound_manager.play_sfx("game_over", 0.4)
                            input_mode = "MAIN"
                        else:
                            pending_user = typed
                            logs.append(f"Enter new credit amount for '{pending_user}':")
                            input_mode = "EDIT_VAL"

                    elif input_mode == "EDIT_VAL":
                        logs.append(f"> {typed}")
                        try:
                            new_val = int(typed)
                            u_data = account.load_user_data(pending_user)
                            u_data["credits"] = max(0, new_val)
                            account.save_user_data(pending_user, u_data)
                            if state.current_user == pending_user:
                                state.all_player_data["P1"]["credits"] = max(0, new_val)
                            logs.append(f"[SUCCESS] Credits for '{pending_user}' set to {new_val:,}.")
                            sound_manager.play_sfx("powerup_collect")
                        except ValueError:
                            logs.append("[ERROR] Invalid number entered.")
                            sound_manager.play_sfx("game_over", 0.4)
                        input_mode = "MAIN"

                    elif input_mode == "DEL_USER":
                        logs.append(f"> {typed}")
                        if account.is_primary_admin(typed):
                            logs.append("[ERROR] Cannot delete the Primary Admin account!")
                            sound_manager.play_sfx("game_over", 0.5)
                        elif typed not in account.list_all_usernames():
                            logs.append(f"[ERROR] User '{typed}' does not exist.")
                            sound_manager.play_sfx("game_over", 0.4)
                        else:
                            account.delete_user(typed)
                            logs.append(f"[SUCCESS] User account '{typed}' was deleted.")
                            sound_manager.play_sfx("explosion_medium")
                            if state.current_user == typed:
                                state.current_user = None
                        input_mode = "MAIN"

                    elif input_mode == "TOGGLE_ADMIN":
                        logs.append(f"> {typed}")
                        if account.is_primary_admin(typed):
                            logs.append("[ERROR] Cannot change admin status of Primary Admin.")
                            sound_manager.play_sfx("game_over", 0.5)
                        elif typed not in account.list_all_usernames():
                            logs.append(f"[ERROR] User '{typed}' does not exist.")
                            sound_manager.play_sfx("game_over", 0.4)
                        else:
                            cur_adm = account.is_admin(typed)
                            account.set_admin(typed, not cur_adm)
                            state_word = "granted" if not cur_adm else "revoked"
                            logs.append(f"[SUCCESS] Admin rights {state_word} for user '{typed}'.")
                            sound_manager.play_sfx("ui_click")
                        input_mode = "MAIN"

                elif event.key == pygame.K_BACKSPACE:
                    input_text = input_text[:-1]
                else:
                    if event.unicode and event.unicode.isprintable() and event.unicode not in ['`', '~']:
                        input_text += event.unicode

        screen.fill(BLACK)
        draw_stars(screen)

        pygame.draw.rect(screen, (8, 14, 22), win_rect, border_radius=10)
        pygame.draw.rect(screen, (0, 200, 160), win_rect, 2, border_radius=10)

        title_bar = pygame.Rect(win_rect.left, win_rect.top, win_rect.width, 42)
        pygame.draw.rect(screen, (12, 28, 38), title_bar, border_top_left_radius=10, border_top_right_radius=10)
        pygame.draw.line(screen, (0, 200, 160), (win_rect.left, win_rect.top + 42), (win_rect.right, win_rect.top + 42), 2)
        
        draw_text("⚙️ TERMINAL ADMIN CONTROL PANEL", FONT_MEDIUM, (0, 255, 180), win_rect.left + 20, title_bar.centery, screen, align="left")
        admin_info = f"Logged in: {state.current_user} [{role_str}]"
        draw_text(admin_info, FONT_SMALL, YELLOW, win_rect.right - 20, title_bar.centery, screen, align="right")

        pygame.draw.rect(screen, (4, 8, 12), log_box, border_radius=6)
        pygame.draw.rect(screen, (20, 50, 60), log_box, 1, border_radius=6)

        visible_lines = logs[-21:]
        line_y = log_box.top + 10
        for l in visible_lines:
            c = (200, 230, 220)
            if l.startswith("[ERROR]"):
                c = (255, 80, 80)
            elif l.startswith("[SUCCESS]"):
                c = (80, 255, 140)
            elif l.startswith("[CMD") or l.startswith("[TOGGLE]"):
                c = (0, 230, 255)
            elif l.startswith("╔") or l.startswith("║") or l.startswith("╚") or l.startswith("══"):
                c = (0, 255, 180)
            elif l.startswith(">"):
                c = (140, 255, 160)
            elif l.startswith("  ["):
                c = (255, 230, 100)
            
            txt_surf = font_mono.render(l, True, c)
            screen.blit(txt_surf, (log_box.left + 10, line_y))
            line_y += 23

        pygame.draw.rect(screen, (10, 20, 28), prompt_rect, border_radius=6)
        pygame.draw.rect(screen, (0, 255, 180) if prompt_rect.collidepoint(mouse_pos) else (30, 70, 80), prompt_rect, 1, border_radius=6)
        
        mode_tag = "Choose Option [0-9]: " if input_mode == "MAIN" else f"[{input_mode}]: "
        display_input = "> " + mode_tag + input_text + ("_" if cursor_visible else " ")
        prompt_surf = font_mono_bold.render(display_input, True, (0, 255, 200))
        screen.blit(prompt_surf, (prompt_rect.left + 10, prompt_rect.centery - 9))

        draw_text("── QUICK COMMANDS ──", FONT_SMALL, (0, 230, 255), btn_x + btn_w // 2, by_start - 18, screen)
        for num, label, base_col, r in btn_rects:
            hover = r.collidepoint(mouse_pos)
            col = BUTTON_HOVER_COLOR if hover else base_col
            pygame.draw.rect(screen, col, r, border_radius=6)
            pygame.draw.rect(screen, (0, 200, 160) if hover else (40, 70, 90), r, 1, border_radius=6)
            draw_text(label, FONT_SMALL, WHITE, r.centerx, r.centery, screen)

        megahack.draw(screen)
        pygame.display.flip()
        clock.tick(int(FPS * state.GAME_SPEED))


def show_admin_options(screen, clock):
    is_authorized = bool(getattr(state, "DEV_CONSOLE_ALLOWED", True) and state.current_user and account.is_admin(state.current_user))
    if not is_authorized:
        while True:
            mouse_pos = pygame.mouse.get_pos()
            center_x = SCREEN_WIDTH // 2
            acc_btn = pygame.Rect(center_x - 180, SCREEN_HEIGHT // 2 + 30, 360, 45)
            back_btn = pygame.Rect(center_x - 180, SCREEN_HEIGHT // 2 + 90, 360, 45)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "QUIT_PROGRAM"
                if megahack.handle_event(event):
                    continue
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if acc_btn.collidepoint(mouse_pos):
                        sound_manager.play_sfx("ui_click")
                        return "ACCOUNT_SCREEN"
                    elif back_btn.collidepoint(mouse_pos):
                        sound_manager.play_sfx("ui_click")
                        return "HOME"
                if event.type == pygame.KEYDOWN and event.key in [pygame.K_ESCAPE, pygame.K_BACKQUOTE]:
                    return "HOME"

            screen.fill(BLACK)
            draw_stars(screen)
            draw_text("ACCESS RESTRICTED", FONT_LARGE, RED, center_x, SCREEN_HEIGHT // 3 - 30, screen)
            if not getattr(state, "DEV_CONSOLE_ALLOWED", True):
                draw_text("Developer Console is currently DISABLED in Settings.", FONT_MEDIUM, YELLOW, center_x, SCREEN_HEIGHT // 3 + 25, screen)
                draw_text("Admin Panel can only be accessed via Dev Console when enabled.", FONT_SMALL, LIGHT_GRAY, center_x, SCREEN_HEIGHT // 3 + 60, screen)
            elif not state.current_user:
                draw_text("Admin privileges required to access Admin Controls.", FONT_MEDIUM, WHITE, center_x, SCREEN_HEIGHT // 3 + 25, screen)
                draw_text("Please log in with an account that has admin rights.", FONT_SMALL, LIGHT_GRAY, center_x, SCREEN_HEIGHT // 3 + 60, screen)
            else:
                draw_text(f"Account '{state.current_user}' does not have Admin privileges.", FONT_MEDIUM, WHITE, center_x, SCREEN_HEIGHT // 3 + 25, screen)
                draw_text("Admin Control Panel is restricted to administrators only.", FONT_SMALL, LIGHT_GRAY, center_x, SCREEN_HEIGHT // 3 + 60, screen)

            h_acc = acc_btn.collidepoint(mouse_pos)
            pygame.draw.rect(screen, BUTTON_HOVER_COLOR if h_acc else BUTTON_COLOR, acc_btn, border_radius=8)
            draw_text("👤 Go to Account Login", FONT_MEDIUM, WHITE, acc_btn.centerx, acc_btn.centery, screen)

            h_back = back_btn.collidepoint(mouse_pos)
            pygame.draw.rect(screen, (50, 60, 80) if h_back else DARK_GRAY, back_btn, border_radius=8)
            draw_text("⬅ Back to Main Menu", FONT_MEDIUM, WHITE, back_btn.centerx, back_btn.centery, screen)

            megahack.draw(screen)
            pygame.display.flip()
            clock.tick(int(FPS * state.GAME_SPEED))

    selected_user_idx = 0
    status_msg = ""
    status_color = WIN_GREEN
    status_time = 0

    while True:
        mouse_pos = pygame.mouse.get_pos()
        center_x = SCREEN_WIDTH // 2
        
        users_list = account.list_all_usernames()
        if selected_user_idx >= len(users_list):
            selected_user_idx = max(0, len(users_list) - 1)
        selected_user = users_list[selected_user_idx] if users_list else None

        rx = center_x - 90 + 20
        ry = 165 + 20

        if selected_user:
            toggle_admin_rect = pygame.Rect(rx, ry + 55, 210, 36)
            delete_user_rect = pygame.Rect(rx + 220, ry + 55, 210, 36)
            edit_credits_rect = pygame.Rect(rx, ry + 100, 430, 36)
        else:
            toggle_admin_rect = pygame.Rect(0, 0, 0, 0)
            delete_user_rect = pygame.Rect(0, 0, 0, 0)
            edit_credits_rect = pygame.Rect(0, 0, 0, 0)

        godmode_rect = pygame.Rect(rx, ry + 190, 430, 36)
        p1_credits_rect = pygame.Rect(rx, ry + 235, 430, 36)
        admin_settings_btn = pygame.Rect(rx, ry + 280, 430, 36)
        cli_admin_rect = pygame.Rect(rx, ry + 325, 430, 36)
        home_rect = pygame.Rect(center_x - 180, 560, 360, 42)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "QUIT_PROGRAM"
            if megahack.handle_event(event):
                continue

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "HOME"
                elif event.key == pygame.K_UP:
                    selected_user_idx = max(0, selected_user_idx - 1)
                elif event.key == pygame.K_DOWN:
                    selected_user_idx = min(len(users_list) - 1, selected_user_idx + 1)
                elif event.key == pygame.K_BACKQUOTE:
                    state.ADMIN_GOD_MODE = not state.ADMIN_GOD_MODE

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                user_list_top = 175
                for idx, u_name in enumerate(users_list):
                    u_rect = pygame.Rect(center_x - 380, user_list_top + idx * 36, 260, 32)
                    if u_rect.collidepoint(mouse_pos):
                        selected_user_idx = idx
                        sound_manager.play_sfx("ui_click")
                        break

                if selected_user and toggle_admin_rect.collidepoint(mouse_pos):
                    sound_manager.play_sfx("ui_click")
                    if account.is_primary_admin(selected_user):
                        status_msg = "Cannot change admin rights of Primary Admin!"
                        status_color = RED
                    else:
                        cur_status = account.is_admin(selected_user)
                        account.set_admin(selected_user, not cur_status)
                        status_msg = f"Admin status for '{selected_user}' set to {not cur_status}."
                        status_color = WIN_GREEN
                    status_time = pygame.time.get_ticks()

                elif selected_user and delete_user_rect.collidepoint(mouse_pos):
                    sound_manager.play_sfx("ui_click")
                    if account.is_primary_admin(selected_user):
                        status_msg = "Cannot delete the Primary Admin account!"
                        status_color = RED
                    else:
                        account.delete_user(selected_user)
                        status_msg = f"User '{selected_user}' deleted."
                        status_color = WIN_GREEN
                        selected_user_idx = max(0, selected_user_idx - 1)
                    status_time = pygame.time.get_ticks()

                elif selected_user and edit_credits_rect.collidepoint(mouse_pos):
                    sound_manager.play_sfx("ui_click")
                    u_data = account.load_user_data(selected_user)
                    u_data["credits"] = u_data.get("credits", 0) + 1000
                    account.save_user_data(selected_user, u_data)
                    if state.current_user == selected_user:
                        state.all_player_data["P1"]["credits"] = u_data["credits"]
                    status_msg = f"Added +1,000 credits to '{selected_user}'."
                    status_color = WIN_GREEN
                    status_time = pygame.time.get_ticks()

                elif godmode_rect.collidepoint(mouse_pos):
                    sound_manager.play_sfx("ui_click")
                    state.ADMIN_GOD_MODE = not state.ADMIN_GOD_MODE
                    status_msg = f"God Mode {'ENABLED' if state.ADMIN_GOD_MODE else 'OFF'}."
                    status_color = WIN_GREEN
                    status_time = pygame.time.get_ticks()

                elif p1_credits_rect.collidepoint(mouse_pos):
                    sound_manager.play_sfx("ui_click")
                    state.all_player_data["P1"]["credits"] += 10000
                    state.save_game_progress()
                    status_msg = "Added +10,000 credits to P1."
                    status_color = WIN_GREEN
                    status_time = pygame.time.get_ticks()

                elif admin_settings_btn.collidepoint(mouse_pos):
                    sound_manager.play_sfx("ui_click")
                    res = show_admin_settings_screen(screen, clock)
                    if res == "QUIT_PROGRAM":
                        return "QUIT_PROGRAM"
                    status_msg = "Returned from Privileged Admin Settings."
                    status_color = WIN_GREEN
                    status_time = pygame.time.get_ticks()

                elif cli_admin_rect.collidepoint(mouse_pos):
                    sound_manager.play_sfx("ui_click")
                    res = show_terminal_admin_panel(screen, clock)
                    if res == "QUIT_PROGRAM":
                        return "QUIT_PROGRAM"
                    elif res == "HOME":
                        return "HOME"
                    status_msg = "Returned from In-Game Terminal Admin Panel."
                    status_color = WIN_GREEN
                    status_time = pygame.time.get_ticks()

                elif home_rect.collidepoint(mouse_pos):
                    sound_manager.play_sfx("ui_click")
                    return "HOME"

        screen.fill(BLACK)
        draw_stars(screen)

        is_primary = account.is_primary_admin(state.current_user)
        role_label = "PRIMARY ADMIN" if is_primary else "ADMIN"
        draw_text("ADMIN CONTROL PANEL", FONT_LARGE, RED, center_x, 45, screen)
        draw_text(f"Logged in as: {state.current_user} [{role_label}]", FONT_SMALL, YELLOW, center_x, 85, screen)

        draw_text("── REGISTERED USERS ──", FONT_SMALL, CYAN, center_x - 250, 145, screen)
        list_bg = pygame.Rect(center_x - 390, 165, 280, 380)
        pygame.draw.rect(screen, (15, 20, 30), list_bg, border_radius=8)
        pygame.draw.rect(screen, (40, 60, 90), list_bg, 2, border_radius=8)

        user_list_top = 175
        for idx, u_name in enumerate(users_list):
            u_rect = pygame.Rect(center_x - 380, user_list_top + idx * 36, 260, 32)
            is_sel = (idx == selected_user_idx)
            is_u_admin = account.is_admin(u_name)
            is_u_primary = account.is_primary_admin(u_name)
            
            bg_col = (40, 80, 120) if is_sel else ((25, 35, 50) if u_rect.collidepoint(mouse_pos) else (20, 25, 35))
            pygame.draw.rect(screen, bg_col, u_rect, border_radius=6)
            if is_sel:
                pygame.draw.rect(screen, CYAN, u_rect, 2, border_radius=6)
                
            badge = "[P]" if is_u_primary else ("[A]" if is_u_admin else "[U]")
            b_color = YELLOW if is_u_primary else (CYAN if is_u_admin else LIGHT_GRAY)
            draw_text(f"{badge} {u_name}", FONT_SMALL, b_color, u_rect.x + 10, u_rect.centery, screen, align="left")

        draw_text("── USER & GAME CONTROLS ──", FONT_SMALL, CYAN, center_x + 130, 145, screen)
        right_bg = pygame.Rect(center_x - 90, 165, 470, 380)
        pygame.draw.rect(screen, (15, 20, 30), right_bg, border_radius=8)
        pygame.draw.rect(screen, (40, 60, 90), right_bg, 2, border_radius=8)

        if selected_user:
            is_sel_admin = account.is_admin(selected_user)
            is_sel_primary = account.is_primary_admin(selected_user)
            u_data = account.load_user_data(selected_user)
            cred = u_data.get("credits", 0)

            draw_text(f"Selected: {selected_user}", FONT_MEDIUM, WHITE, rx, ry, screen, align="left")
            role_text = "Primary Admin" if is_sel_primary else ("Admin" if is_sel_admin else "Regular User")
            draw_text(f"Role: {role_text}   |   Credits: {cred} Cr", FONT_SMALL, LIGHT_GRAY, rx, ry + 25, screen, align="left")

            btn_txt = "Revoke Admin" if is_sel_admin else "Grant Admin"
            h_t = toggle_admin_rect.collidepoint(mouse_pos)
            t_col = (140, 60, 0) if is_sel_admin else (0, 100, 140)
            pygame.draw.rect(screen, BUTTON_HOVER_COLOR if h_t else t_col, toggle_admin_rect, border_radius=6)
            draw_text(btn_txt, FONT_SMALL, WHITE, toggle_admin_rect.centerx, toggle_admin_rect.centery, screen)

            h_d = delete_user_rect.collidepoint(mouse_pos)
            pygame.draw.rect(screen, (180, 40, 40) if h_d else (120, 30, 30), delete_user_rect, border_radius=6)
            draw_text("Delete Account", FONT_SMALL, WHITE, delete_user_rect.centerx, delete_user_rect.centery, screen)

            h_c = edit_credits_rect.collidepoint(mouse_pos)
            pygame.draw.rect(screen, BUTTON_HOVER_COLOR if h_c else (30, 70, 110), edit_credits_rect, border_radius=6)
            draw_text(f"Add +1,000 Credits to '{selected_user}'", FONT_SMALL, WHITE, edit_credits_rect.centerx, edit_credits_rect.centery, screen)
        else:
            draw_text("No user selected", FONT_MEDIUM, LIGHT_GRAY, rx, ry, screen, align="left")

        pygame.draw.line(screen, (40, 60, 90), (rx, ry + 150), (rx + 430, ry + 150), 2)

        draw_text("GLOBAL CHEATS & TOOLS", FONT_SMALL, YELLOW, rx, ry + 165, screen, align="left")

        h_g = godmode_rect.collidepoint(mouse_pos)
        god_status = "ENABLED" if state.ADMIN_GOD_MODE else "OFF"
        god_col = (0, 140, 60) if state.ADMIN_GOD_MODE else (70, 70, 90)
        pygame.draw.rect(screen, BUTTON_HOVER_COLOR if h_g else god_col, godmode_rect, border_radius=6)
        draw_text(f"God Mode (In-Game ~): {god_status}", FONT_SMALL, WHITE, godmode_rect.centerx, godmode_rect.centery, screen)

        h_p1 = p1_credits_rect.collidepoint(mouse_pos)
        pygame.draw.rect(screen, BUTTON_HOVER_COLOR if h_p1 else (50, 80, 120), p1_credits_rect, border_radius=6)
        draw_text("Give +10,000 Credits to P1", FONT_SMALL, WHITE, p1_credits_rect.centerx, p1_credits_rect.centery, screen)

        h_as = admin_settings_btn.collidepoint(mouse_pos)
        pygame.draw.rect(screen, BUTTON_HOVER_COLOR if h_as else (30, 90, 150), admin_settings_btn, border_radius=6)
        draw_text("⚙️ Open Dedicated Admin Settings", FONT_SMALL, WHITE, admin_settings_btn.centerx, admin_settings_btn.centery, screen)

        h_cli = cli_admin_rect.collidepoint(mouse_pos)
        pygame.draw.rect(screen, (100, 40, 120) if h_cli else (70, 20, 90), cli_admin_rect, border_radius=6)
        draw_text("💻 Launch In-Game Terminal Admin Panel", FONT_SMALL, WHITE, cli_admin_rect.centerx, cli_admin_rect.centery, screen)

        h_home = home_rect.collidepoint(mouse_pos)
        pygame.draw.rect(screen, BUTTON_HOVER_COLOR if h_home else (40, 50, 70), home_rect, border_radius=8)
        draw_text("⬅ Return to Main Menu", FONT_MEDIUM, WHITE, home_rect.centerx, home_rect.centery, screen)

        if status_msg and pygame.time.get_ticks() - status_time < 3500:
            draw_text(status_msg, FONT_SMALL, status_color, center_x, SCREEN_HEIGHT - 20, screen)

        megahack.draw(screen)
        pygame.display.flip()
        clock.tick(int(FPS * state.GAME_SPEED))


def show_admin_settings_screen(screen, clock):
    """Dedicated Admin Settings Screen for Privileged Configurations."""
    is_authorized = bool(getattr(state, "DEV_CONSOLE_ALLOWED", True) and state.current_user and account.is_admin(state.current_user))
    if not is_authorized:
        return show_admin_options(screen, clock)

    status_msg = ""
    status_color = WIN_GREEN
    status_time = 0

    back_btn = pygame.Rect(SCREEN_WIDTH // 2 - 180, SCREEN_HEIGHT - 75, 360, 48)

    while True:
        mouse_pos = pygame.mouse.get_pos()
        center_x = SCREEN_WIDTH // 2
        y_cursor = 140

        dev_console_rect = pygame.Rect(center_x - 220, y_cursor, 440, 44)
        y_cursor += 60

        credits_rect = pygame.Rect(center_x - 220, y_cursor, 440, 44)
        y_cursor += 60

        speed_rect = pygame.Rect(center_x - 220, y_cursor, 440, 44)
        y_cursor += 60

        godmode_rect = pygame.Rect(center_x - 220, y_cursor, 440, 44)
        y_cursor += 60

        player_health_rect = pygame.Rect(center_x - 220, y_cursor, 440, 44)
        y_cursor += 75

        reset_progress_rect = pygame.Rect(center_x - 220, y_cursor, 210, 44)
        reset_users_rect = pygame.Rect(center_x + 10, y_cursor, 210, 44)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "QUIT_PROGRAM"
            if megahack.handle_event(event):
                continue

            if event.type == pygame.KEYDOWN and event.key in [pygame.K_ESCAPE, pygame.K_BACKQUOTE]:
                sound_manager.play_sfx("ui_click")
                return "ADMIN_PANEL"

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if dev_console_rect.collidepoint(mouse_pos):
                    sound_manager.play_sfx("hack_toggle")
                    state.DEV_CONSOLE_ALLOWED = not getattr(state, "DEV_CONSOLE_ALLOWED", True)
                    state.save_admin_config()
                    status_msg = f"Developer Console {'ENABLED' if state.DEV_CONSOLE_ALLOWED else 'DISABLED'}."
                    status_color = WIN_GREEN
                    status_time = pygame.time.get_ticks()

                elif credits_rect.collidepoint(mouse_pos):
                    sound_manager.play_sfx("ui_click")
                    opts = [0, 500, 1000, 5000, 10000]
                    cur = state.admin_settings.get("default_starting_credits", 0)
                    next_idx = (opts.index(cur) + 1) if cur in opts else 0
                    state.admin_settings["default_starting_credits"] = opts[next_idx]
                    state.save_admin_config()
                    status_msg = f"Default Starting Credits set to {opts[next_idx]:,} Cr."
                    status_color = WIN_GREEN
                    status_time = pygame.time.get_ticks()

                elif speed_rect.collidepoint(mouse_pos):
                    sound_manager.play_sfx("ui_click")
                    speeds = [0.5, 1.0, 1.5, 2.0]
                    cur = state.GAME_SPEED
                    next_idx = (speeds.index(cur) + 1) if cur in speeds else 1
                    state.GAME_SPEED = speeds[next_idx]
                    state.save_admin_config()
                    status_msg = f"Global Game Speed Multiplier set to {speeds[next_idx]}x."
                    status_color = WIN_GREEN
                    status_time = pygame.time.get_ticks()

                elif godmode_rect.collidepoint(mouse_pos):
                    sound_manager.play_sfx("hack_toggle")
                    state.ADMIN_GOD_MODE = not state.ADMIN_GOD_MODE
                    state.save_admin_config()
                    status_msg = f"Default Admin God Mode {'ENABLED' if state.ADMIN_GOD_MODE else 'OFF'}."
                    status_color = WIN_GREEN
                    status_time = pygame.time.get_ticks()

                elif player_health_rect.collidepoint(mouse_pos):
                    sound_manager.play_sfx("hack_toggle")
                    state.PLAYER_HEALTH_MODE = not state.PLAYER_HEALTH_MODE
                    state.save_admin_config()
                    status_msg = f"Player Health Mode {'ENABLED' if state.PLAYER_HEALTH_MODE else 'OFF'} (1-Hit Kill)."
                    status_color = WIN_GREEN
                    status_time = pygame.time.get_ticks()

                elif reset_progress_rect.collidepoint(mouse_pos):
                    sound_manager.play_sfx("game_over")
                    state.all_player_data = {"P1": dict(state.DEFAULT_PLAYER_DATA), "P2": dict(state.DEFAULT_PLAYER_DATA)}
                    state.save_game_progress()
                    status_msg = "🚨 Reset Game Progress to initial defaults!"
                    status_color = RED
                    status_time = pygame.time.get_ticks()

                elif reset_users_rect.collidepoint(mouse_pos):
                    sound_manager.play_sfx("game_over")
                    account.reset_all_users()
                    status_msg = "🚨 Reset User Accounts (Primary admin preserved)!"
                    status_color = RED
                    status_time = pygame.time.get_ticks()

                elif back_btn.collidepoint(mouse_pos):
                    sound_manager.play_sfx("ui_click")
                    return "ADMIN_PANEL"

        screen.fill(BLACK)
        draw_stars(screen)

        draw_text("⚙️ PRIVILEGED ADMIN SETTINGS", FONT_LARGE, RED, center_x, 45, screen)
        draw_text("Global system configurations, default rules, and emergency administration.", FONT_SMALL, LIGHT_GRAY, center_x, 88, screen)

        h1 = dev_console_rect.collidepoint(mouse_pos)
        dev_on = getattr(state, "DEV_CONSOLE_ALLOWED", True)
        pygame.draw.rect(screen, (0, 100, 140) if dev_on else (100, 30, 30), dev_console_rect, border_radius=8)
        if h1:
            pygame.draw.rect(screen, WHITE, dev_console_rect, 2, border_radius=8)
        draw_text(f"Developer Console Access: {'ENABLED' if dev_on else 'DISABLED'} (Click to Toggle)", FONT_SMALL, WHITE, dev_console_rect.centerx, dev_console_rect.centery, screen)

        h2 = credits_rect.collidepoint(mouse_pos)
        cur_c = state.admin_settings.get("default_starting_credits", 0)
        pygame.draw.rect(screen, (30, 80, 130), credits_rect, border_radius=8)
        if h2:
            pygame.draw.rect(screen, WHITE, credits_rect, 2, border_radius=8)
        draw_text(f"Default Starting Credits: {cur_c:,} Cr (Click to Cycle)", FONT_SMALL, WHITE, credits_rect.centerx, credits_rect.centery, screen)

        h3 = speed_rect.collidepoint(mouse_pos)
        cur_s = state.GAME_SPEED
        pygame.draw.rect(screen, (40, 90, 80), speed_rect, border_radius=8)
        if h3:
            pygame.draw.rect(screen, WHITE, speed_rect, 2, border_radius=8)
        draw_text(f"Global Game Speed Multiplier: {cur_s}x (Click to Cycle)", FONT_SMALL, WHITE, speed_rect.centerx, speed_rect.centery, screen)

        h4 = godmode_rect.collidepoint(mouse_pos)
        god_on = state.ADMIN_GOD_MODE
        pygame.draw.rect(screen, (0, 140, 60) if god_on else (70, 70, 90), godmode_rect, border_radius=8)
        if h4:
            pygame.draw.rect(screen, WHITE, godmode_rect, 2, border_radius=8)
        draw_text(f"Default Admin God Mode: {'ACTIVE' if god_on else 'OFF'} (Click to Toggle)", FONT_SMALL, WHITE, godmode_rect.centerx, godmode_rect.centery, screen)

        h_health = player_health_rect.collidepoint(mouse_pos)
        health_on = getattr(state, "PLAYER_HEALTH_MODE", False)
        pygame.draw.rect(screen, (0, 140, 60) if health_on else (70, 70, 90), player_health_rect, border_radius=8)
        if h_health:
            pygame.draw.rect(screen, WHITE, player_health_rect, 2, border_radius=8)
        draw_text(f"Player Health Mode: {'HP BAR' if health_on else '1-HIT KILL'} (Click to Toggle)", FONT_SMALL, WHITE, player_health_rect.centerx, player_health_rect.centery, screen)

        draw_text("── 🚨 EMERGENCY DATA RESET CONTROLS ──", FONT_SMALL, RED, center_x, reset_progress_rect.top - 18, screen)

        h_rp = reset_progress_rect.collidepoint(mouse_pos)
        pygame.draw.rect(screen, (160, 40, 40) if h_rp else (110, 20, 20), reset_progress_rect, border_radius=8)
        draw_text("Reset Progress JSON", FONT_SMALL, WHITE, reset_progress_rect.centerx, reset_progress_rect.centery, screen)

        h_ru = reset_users_rect.collidepoint(mouse_pos)
        pygame.draw.rect(screen, (160, 40, 40) if h_ru else (110, 20, 20), reset_users_rect, border_radius=8)
        draw_text("Reset Users JSON", FONT_SMALL, WHITE, reset_users_rect.centerx, reset_users_rect.centery, screen)

        h_back = back_btn.collidepoint(mouse_pos)
        pygame.draw.rect(screen, BUTTON_HOVER_COLOR if h_back else (40, 50, 70), back_btn, border_radius=8)
        draw_text("⬅ Return to Admin Control Panel", FONT_MEDIUM, WHITE, back_btn.centerx, back_btn.centery, screen)

        if status_msg and pygame.time.get_ticks() - status_time < 3500:
            draw_text(status_msg, FONT_SMALL, status_color, center_x, SCREEN_HEIGHT - 110, screen)

        megahack.draw(screen)
        pygame.display.flip()
        clock.tick(int(FPS * state.GAME_SPEED))


        megahack.draw(screen)
        pygame.display.flip()
        clock.tick(int(FPS * state.GAME_SPEED))

def show_web_browser_screen(screen, clock):
    current_url = "http://galactic.net/home"
    history = [current_url]
    history_idx = 0
    is_typing_url = False
    typed_url = ""
    
    # Mod Maker States
    mod_name_input = ""
    mod_desc_input = ""
    active_input = None
    
    import threading
    import requests
    import json
    
    API_URL = "https://api.restful-api.dev/objects/ff808181a09d98f701a0de960ca21ed3"
    cached_global_mods = []
    is_loading_mods = False
    
    def fetch_global_mods():
        nonlocal cached_global_mods, is_loading_mods
        if is_loading_mods: return
        is_loading_mods = True
        try:
            res = requests.get(API_URL, timeout=3).json()
            cached_global_mods = res.get("data", {}).get("mods", [])
        except: pass
        finally: is_loading_mods = False

    def publish_global_mod(new_mod):
        nonlocal cached_global_mods
        cached_global_mods.append(new_mod)
        try:
            requests.put(API_URL, json={"name": "mods", "data": {"mods": cached_global_mods}}, timeout=3)
        except: pass

    # Fetch initial mods on startup in a thread
    threading.Thread(target=fetch_global_mods, daemon=True).start()

    # Easter Egg States
    dvd_mode = False
    bx, by = SCREEN_WIDTH // 2 - 450, SCREEN_HEIGHT // 2 - 325
    bdx, bdy = 4, 3
    matrix_mode = False
    matrix_chars = []
    import random

    while True:
        mouse_pos = pygame.mouse.get_pos()
        
        if dvd_mode:
            bx += bdx
            by += bdy
            if bx <= 0 or bx + 900 >= SCREEN_WIDTH: bdx *= -1
            if by <= 0 or by + 650 >= SCREEN_HEIGHT: bdy *= -1
        else:
            bx, by = SCREEN_WIDTH // 2 - 450, SCREEN_HEIGHT // 2 - 325
            
        browser_w, browser_h = 900, 650
        
        home_rect = pygame.Rect(bx + 10, by + 5, 50, 30)
        back_rect = pygame.Rect(bx + 65, by + 5, 30, 30)
        fwd_rect = pygame.Rect(bx + 100, by + 5, 30, 30)
        url_bar_rect = pygame.Rect(bx + 140, by + 5, browser_w - 190, 30)
        close_rect = pygame.Rect(bx + browser_w - 40, by + 5, 30, 30)

        for event in pygame.event.get():
            if event.type == pygame.QUIT: return "QUIT_PROGRAM"
            if megahack.handle_event(event): continue
            
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                is_typing_url = False # defocus by default
                
                if close_rect.collidepoint(mouse_pos): return "HOME"
                if url_bar_rect.collidepoint(mouse_pos):
                    is_typing_url = True
                    typed_url = current_url
                    
                if home_rect.collidepoint(mouse_pos): 
                    current_url = "http://galactic.net/home"
                    history = history[:history_idx+1]
                    history.append(current_url)
                    history_idx += 1
                if back_rect.collidepoint(mouse_pos) and history_idx > 0:
                    history_idx -= 1
                    current_url = history[history_idx]
                if fwd_rect.collidepoint(mouse_pos) and history_idx < len(history) - 1:
                    history_idx += 1
                    current_url = history[history_idx]
                
                # Handling page links
                if current_url == "http://galactic.net/home":
                    if pygame.Rect(bx+250, by+190, 400, 50).collidepoint(mouse_pos): current_url = "http://darknet.galactic/megahack"
                    if pygame.Rect(bx+250, by+260, 400, 50).collidepoint(mouse_pos): current_url = "http://galactic.net/shipyard"
                    if pygame.Rect(bx+250, by+330, 400, 50).collidepoint(mouse_pos): current_url = "http://galactic.net/news"
                    if pygame.Rect(bx+250, by+400, 400, 50).collidepoint(mouse_pos): current_url = "http://galactic.net/mods"
                    if pygame.Rect(bx+250, by+470, 400, 50).collidepoint(mouse_pos): current_url = "http://galactic.net/updates"
                    if state.all_player_data["P1"].get("browser_v2") and pygame.Rect(bx+250, by+540, 400, 50).collidepoint(mouse_pos): current_url = "http://galactic.net/v2_vault"
                    
                    if current_url != "http://galactic.net/home":
                        history = history[:history_idx+1]
                        history.append(current_url)
                        history_idx += 1
                        
                elif current_url == "http://darknet.galactic/megahack":
                    if pygame.Rect(bx+300, by+350, 300, 60).collidepoint(mouse_pos): 
                        state.all_player_data["P1"]["has_downloaded_cheat_menu"] = True
                        state.save_game_progress()
                        
                elif current_url == "http://galactic.net/mods":
                    has_loader = "power_modloader" in state.all_player_data["P1"]["unlocked_powers"]
                    if not has_loader:
                        if pygame.Rect(bx+300, by+200, 300, 60).collidepoint(mouse_pos):
                            state.all_player_data["P1"]["unlocked_powers"].append("power_modloader")
                            state.save_game_progress()
                            sound_manager.play_sfx("ui_click")
                    else:
                        create_btn = pygame.Rect(bx + browser_w - 250, by + 100, 200, 40)
                        if create_btn.collidepoint(mouse_pos):
                            current_url = "http://galactic.net/mods/create"
                            history = history[:history_idx+1]
                            history.append(current_url)
                            history_idx += 1
                        else:
                            for i, m in enumerate(cached_global_mods[:5]):
                                if not isinstance(m, dict): continue
                                y = by + 180 + i * 70
                                dl_mod_btn = pygame.Rect(bx + 100 + browser_w - 380, y + 10, 150, 40)
                                if dl_mod_btn.collidepoint(mouse_pos):
                                    fname = m.get("fname")
                                    json_str = m.get("json_str")
                                    json_data = m.get("json_data")
                                    if fname and (json_str or json_data):
                                        if json_data and not json_str:
                                            mod_key = json_data.get("mod_key", fname.replace(".json", ""))
                                            # Remove mod_key so it doesn't pollute the object
                                            if "mod_key" in json_data: del json_data["mod_key"]
                                            json_str = json.dumps({"powerups": {mod_key: json_data}})
                                        mods_dir = os.path.join(BASE_DIR, "mods")
                                        os.makedirs(mods_dir, exist_ok=True)
                                        mod_path = os.path.join(mods_dir, fname)
                                        if not os.path.exists(mod_path):
                                            with open(mod_path, "w") as f: f.write(json_str)
                                            sound_manager.play_sfx("hack_toggle")
                                        
                elif current_url == "http://galactic.net/mods/create":
                    name_rect = pygame.Rect(bx + 200, by + 200, 400, 40)
                    desc_rect = pygame.Rect(bx + 200, by + 300, 400, 40)
                    publish_rect = pygame.Rect(bx + 300, by + 400, 300, 50)
                    
                    if name_rect.collidepoint(mouse_pos): active_input = "NAME"
                    elif desc_rect.collidepoint(mouse_pos): active_input = "DESC"
                    else: active_input = None
                    
                    if publish_rect.collidepoint(mouse_pos) and mod_name_input.strip() and mod_desc_input.strip():
                        import random
                        fname = mod_name_input.lower().replace(" ", "_")[:15] + f"_{random.randint(100,999)}.json"
                        
                        # Cloud Code Generation Parser (CG)
                        desc_lower = mod_desc_input.lower()
                        mod_key = fname.replace(".json", "")
                        jdata = {
                            "mod_key": mod_key,
                            "name": mod_name_input,
                            "desc": mod_desc_input,
                            "color": [random.randint(50, 255), random.randint(50, 255), random.randint(50, 255)]
                        }
                        
                        if "speed" in desc_lower or "fast" in desc_lower:
                            jdata["speed_multiplier"] = 1.5
                        if "damage" in desc_lower or "fire" in desc_lower or "blaster" in desc_lower:
                            jdata["fire_rate_multiplier"] = 1.5
                        if "health" in desc_lower or "heal" in desc_lower or "tank" in desc_lower:
                            jdata["heal_amount"] = 50
                            
                        # If no keywords matched at all, pick a random one
                        if "speed_multiplier" not in jdata and "fire_rate_multiplier" not in jdata and "heal_amount" not in jdata:
                            effect = random.choice(["speed_multiplier", "fire_rate_multiplier", "heal_amount"])
                            val = 1.5 if effect != "heal_amount" else 50
                            jdata[effect] = val
                            
                        threading.Thread(target=publish_global_mod, args=({"name": mod_name_input, "fname": fname, "desc": mod_desc_input, "json_data": jdata},), daemon=True).start()
                        
                        mod_name_input = ""
                        mod_desc_input = ""
                        current_url = "http://galactic.net/mods"
                        history = history[:history_idx+1]
                        history.append(current_url)
                        history_idx += 1
                        sound_manager.play_sfx("victory")

                elif current_url == "http://galactic.net/shipyard":
                    if pygame.Rect(bx+250, by+300, 400, 80).collidepoint(mouse_pos) and state.all_player_data["P1"]["credits"] >= 8000:
                        if "shadow_wraith" not in state.all_player_data["P1"]["owned_ships"]:
                            state.all_player_data["P1"]["credits"] -= 8000
                            state.all_player_data["P1"]["owned_ships"].append("shadow_wraith")
                            state.save_game_progress()
                            sound_manager.play_sfx("powerup_collect")

                elif current_url == "http://galactic.net/updates":
                    dl_v2_btn = pygame.Rect(bx+250, by+300, 400, 80)
                    if dl_v2_btn.collidepoint(mouse_pos) and not state.all_player_data["P1"].get("browser_v2"):
                        state.all_player_data["P1"]["browser_v2"] = True
                        state.save_game_progress()
                        sound_manager.play_sfx("level_up")

                elif current_url == "http://galactic.net/v2_vault":
                    dl_ship_btn = pygame.Rect(bx+250, by+200, 400, 80)
                    if dl_ship_btn.collidepoint(mouse_pos) and "v2_phantom" not in state.all_player_data["P1"]["owned_ships"]:
                        state.all_player_data["P1"]["owned_ships"].append("v2_phantom")
                        state.save_game_progress()
                        sound_manager.play_sfx("powerup_collect")
                        
                    dl_pwr_btn = pygame.Rect(bx+250, by+320, 400, 80)
                    if dl_pwr_btn.collidepoint(mouse_pos) and "power_magnet" not in state.all_player_data["P1"]["unlocked_powers"]:
                        state.all_player_data["P1"]["unlocked_powers"].append("power_magnet")
                        state.save_game_progress()
                        sound_manager.play_sfx("powerup_collect")
            
            if event.type == pygame.KEYDOWN:
                if is_typing_url:
                    if event.key == pygame.K_RETURN:
                        is_typing_url = False
                        if typed_url != current_url:
                            if not typed_url.startswith("http://"): typed_url = "http://" + typed_url
                            
                            # Easter Eggs Checks
                            if typed_url == "http://galactic.net/bounce":
                                dvd_mode = not dvd_mode
                                typed_url = history[history_idx] # cancel navigation
                            elif typed_url == "http://galactic.net/matrix":
                                matrix_mode = True
                                # Init matrix lines
                                matrix_chars = [{"x": random.randint(0, SCREEN_WIDTH), "y": random.randint(-600, 0), "speed": random.randint(5, 15)} for _ in range(100)]
                                typed_url = history[history_idx] # cancel navigation
                            elif typed_url == "http://galactic.net/askew":
                                typed_url = history[history_idx]
                                bx += 30
                                by += 40
                            else:
                                matrix_mode = False
                                current_url = typed_url
                                history = history[:history_idx+1]
                                history.append(current_url)
                                history_idx += 1
                    elif event.key == pygame.K_ESCAPE:
                        is_typing_url = False
                    elif event.key == pygame.K_BACKSPACE:
                        typed_url = typed_url[:-1]
                    elif event.unicode.isprintable():
                        typed_url += event.unicode
                elif active_input == "NAME":
                    if event.key == pygame.K_BACKSPACE: mod_name_input = mod_name_input[:-1]
                    elif event.unicode.isprintable() and len(mod_name_input) < 30: mod_name_input += event.unicode
                elif active_input == "DESC":
                    if event.key == pygame.K_BACKSPACE: mod_desc_input = mod_desc_input[:-1]
                    elif event.unicode.isprintable() and len(mod_desc_input) < 50: mod_desc_input += event.unicode
                else:
                    if event.key == pygame.K_ESCAPE: return "HOME"

        screen.fill((20, 40, 60))
        
        # Browser Frame
        pygame.draw.rect(screen, (200, 200, 200), (bx, by, browser_w, browser_h), border_radius=8)
        pygame.draw.rect(screen, (150, 150, 150), (bx, by, browser_w, 40), border_radius=8)
        pygame.draw.rect(screen, (10, 15, 20), (bx, by + 40, browser_w, browser_h - 40), border_bottom_left_radius=8, border_bottom_right_radius=8)
        
        # Navigation Buttons
        pygame.draw.rect(screen, DARK_GRAY, home_rect, border_radius=4)
        draw_text("HOME", FONT_SMALL, WHITE, home_rect.centerx, home_rect.centery, screen)
        
        back_col = DARK_GRAY if history_idx > 0 else (100, 100, 100)
        pygame.draw.rect(screen, back_col, back_rect, border_radius=4)
        draw_text("<", FONT_SMALL, WHITE, back_rect.centerx, back_rect.centery, screen)
        
        fwd_col = DARK_GRAY if history_idx < len(history) - 1 else (100, 100, 100)
        pygame.draw.rect(screen, fwd_col, fwd_rect, border_radius=4)
        draw_text(">", FONT_SMALL, WHITE, fwd_rect.centerx, fwd_rect.centery, screen)
        
        # Address Bar
        url_color = (255, 255, 200) if is_typing_url else WHITE
        pygame.draw.rect(screen, url_color, url_bar_rect, border_radius=4)
        display_url = typed_url + ("|" if (pygame.time.get_ticks()//500)%2==0 and is_typing_url else "") if is_typing_url else current_url
        draw_text(display_url, FONT_SMALL, BLACK, url_bar_rect.left + 10, url_bar_rect.centery, screen, align="left")
        
        pygame.draw.rect(screen, RED, close_rect, border_radius=4)
        draw_text("X", FONT_SMALL, WHITE, close_rect.centerx, close_rect.centery, screen)
        
        # Page Content
        if current_url == "http://galactic.net/home":
            title = "GALACTIC WEB PORTAL v2.0" if state.all_player_data["P1"].get("browser_v2") else "GALACTIC WEB PORTAL"
            draw_text(title, FONT_LARGE, CYAN, bx + browser_w//2, by + 120, screen, drop_shadow=True)
            link1, link2, link3, link4 = pygame.Rect(bx+250, by+190, 400, 50), pygame.Rect(bx+250, by+260, 400, 50), pygame.Rect(bx+250, by+330, 400, 50), pygame.Rect(bx+250, by+400, 400, 50)
            link5 = pygame.Rect(bx+250, by+470, 400, 50)
            
            links = [(link1, "▶ Darknet: MegaHack v7", MAGENTA), (link2, "▶ Black Market Shipyard", ORANGE), (link3, "▶ Galactic News Network", YELLOW), (link4, "▶ Modding Community Hub", (100, 255, 100)), (link5, "▶ System Updates", LIGHT_GRAY)]
            
            if state.all_player_data["P1"].get("browser_v2"):
                link6 = pygame.Rect(bx+250, by+540, 400, 50)
                links.append((link6, "▶ The Quantum Vault (v2.0 Exclusive)", CYAN))
                
            for r, t, col in links:
                pygame.draw.rect(screen, (50, 50, 80), r, border_radius=8)
                pygame.draw.rect(screen, (100, 150, 255) if r.collidepoint(mouse_pos) else (80, 80, 120), r, 2, border_radius=8)
                draw_text(t, FONT_MEDIUM, col, r.centerx, r.centery, screen)
                
        elif current_url == "http://darknet.galactic/megahack":
            draw_text("◆ MEGAHACK RUNTIME INJECTOR ◆", FONT_LARGE, MAGENTA, bx + browser_w//2, by + 150, screen)
            dl_btn = pygame.Rect(bx+300, by+350, 300, 60)
            pygame.draw.rect(screen, BUTTON_DISABLED_COLOR, dl_btn, border_radius=10)
            pygame.draw.rect(screen, (100, 100, 120), dl_btn, 2, border_radius=10)
            draw_text("UNLOCKED BY DEFAULT - Press TAB", FONT_MEDIUM, WIN_GREEN, dl_btn.centerx, dl_btn.centery, screen)
                
        elif current_url == "http://galactic.net/shipyard":
            draw_text("BLACK MARKET SHIPYARD", FONT_LARGE, ORANGE, bx + browser_w//2, by + 150, screen)
            buy_btn = pygame.Rect(bx+250, by+300, 400, 80)
            pygame.draw.rect(screen, BUTTON_COLOR, buy_btn, border_radius=10)
            pygame.draw.rect(screen, (120, 140, 180), buy_btn, 2, border_radius=10)
            msg = "OWNED" if "shadow_wraith" in state.all_player_data["P1"]["owned_ships"] else "BUY 'SHADOW WRAITH' - 8000 Cr"
            draw_text(msg, FONT_MEDIUM, WHITE, buy_btn.centerx, buy_btn.centery, screen)
            
        elif current_url == "http://galactic.net/news":
            draw_text("GALACTIC NEWS NETWORK", FONT_LARGE, YELLOW, bx + browser_w//2, by + 120, screen)
            draw_text("Breaking: Unprecedented anomaly detected in Sector 5.", FONT_SMALL, LIGHT_GRAY, bx + 50, by + 200, screen, align="left")
            draw_text("Rumors of an 'Omega Overlord' returning have caused panic.", FONT_SMALL, LIGHT_GRAY, bx + 50, by + 250, screen, align="left")
            draw_text("Prices of illegal 'Shadow Wraith' ships surge in black market.", FONT_SMALL, LIGHT_GRAY, bx + 50, by + 300, screen, align="left")
            draw_text("Galactic Federation suspends all bounty payouts indefinitely.", FONT_SMALL, LIGHT_GRAY, bx + 50, by + 350, screen, align="left")

        elif current_url == "http://galactic.net/mods":
            draw_text("COMMUNITY MODS HUB", FONT_LARGE, (100, 255, 100), bx + browser_w//2, by + 100, screen)
            has_loader = "power_modloader" in state.all_player_data["P1"]["unlocked_powers"]
            
            if not has_loader:
                dl_loader_btn = pygame.Rect(bx+300, by+200, 300, 60)
                pygame.draw.rect(screen, BUTTON_COLOR, dl_loader_btn, border_radius=10)
                draw_text("DOWNLOAD MOD LOADER", FONT_MEDIUM, WHITE, dl_loader_btn.centerx, dl_loader_btn.centery, screen)
            else:
                draw_text("Mod Loader Installed! Browse hundreds of mods.", FONT_SMALL, WHITE, bx + browser_w//2, by + 140, screen)
                create_btn = pygame.Rect(bx + browser_w - 250, by + 100, 200, 40)
                pygame.draw.rect(screen, (50, 150, 250), create_btn, border_radius=5)
                draw_text("CREATE NEW MOD", FONT_SMALL, WHITE, create_btn.centerx, create_btn.centery, screen)
                
                if is_loading_mods:
                    draw_text("Syncing with Global Cloud...", FONT_MEDIUM, YELLOW, bx + browser_w//2, by + 300, screen)
                else:
                    for i, m in enumerate(cached_global_mods[:5]):
                        if not isinstance(m, dict): continue
                        y = by + 180 + i * 70
                        x = bx + 100
                        pygame.draw.rect(screen, (40, 40, 60), (x, y, browser_w - 200, 60), border_radius=8)
                        draw_text(m.get("name", "Unknown Mod"), FONT_MEDIUM, YELLOW, x + 20, y + 30, screen, align="left")
                        draw_text(m.get("desc", "No description provided."), FONT_SMALL, LIGHT_GRAY, x + 250, y + 30, screen, align="left")
                        dl_mod_btn = pygame.Rect(x + browser_w - 380, y + 10, 150, 40)
                        fname = m.get("fname", f"unknown_mod_{i}.json")
                        is_installed = os.path.exists(os.path.join(BASE_DIR, "mods", fname))
                        
                        pygame.draw.rect(screen, (50, 150, 50) if is_installed else BUTTON_COLOR, dl_mod_btn, border_radius=5)
                        draw_text("ADDED" if is_installed else "ADD MOD", FONT_SMALL, WHITE, dl_mod_btn.centerx, dl_mod_btn.centery, screen)

        elif current_url == "http://galactic.net/mods/create":
            draw_text("MOD CREATOR WORKSHOP", FONT_LARGE, (100, 255, 100), bx + browser_w//2, by + 100, screen)
            draw_text("Create a new mod and publish it to the community!", FONT_SMALL, LIGHT_GRAY, bx + browser_w//2, by + 140, screen)
            
            name_rect = pygame.Rect(bx + 200, by + 200, 400, 40)
            pygame.draw.rect(screen, (255, 255, 200) if active_input == "NAME" else WHITE, name_rect, border_radius=5)
            draw_text("Mod Name:", FONT_MEDIUM, WHITE, bx + 100, by + 220, screen)
            draw_text(mod_name_input + ("|" if (pygame.time.get_ticks()//500)%2==0 and active_input == "NAME" else ""), FONT_MEDIUM, BLACK, name_rect.left + 10, name_rect.centery, screen, align="left")
            
            desc_rect = pygame.Rect(bx + 200, by + 300, 400, 40)
            pygame.draw.rect(screen, (255, 255, 200) if active_input == "DESC" else WHITE, desc_rect, border_radius=5)
            draw_text("Description:", FONT_MEDIUM, WHITE, bx + 100, by + 320, screen)
            draw_text(mod_desc_input + ("|" if (pygame.time.get_ticks()//500)%2==0 and active_input == "DESC" else ""), FONT_MEDIUM, BLACK, desc_rect.left + 10, desc_rect.centery, screen, align="left")
            
            publish_rect = pygame.Rect(bx + 300, by + 400, 300, 50)
            can_publish = bool(mod_name_input.strip() and mod_desc_input.strip())
            pygame.draw.rect(screen, (50, 150, 250) if can_publish else (100, 100, 100), publish_rect, border_radius=10)
            draw_text("PUBLISH TO CLOUD", FONT_MEDIUM, WHITE, publish_rect.centerx, publish_rect.centery, screen)

        elif current_url == "http://galactic.net/updates":
            draw_text("SYSTEM UPDATES & FIRMWARE", FONT_LARGE, LIGHT_GRAY, bx + browser_w//2, by + 120, screen)
            if state.all_player_data["P1"].get("browser_v2"):
                draw_text("System is up to date! (v2.0 Installed)", FONT_MEDIUM, WIN_GREEN, bx + browser_w//2, by + 200, screen)
            else:
                draw_text("New Update Available: Galactic Browser v2.0", FONT_MEDIUM, YELLOW, bx + browser_w//2, by + 200, screen)
                dl_v2_btn = pygame.Rect(bx+250, by+300, 400, 80)
                is_hover = dl_v2_btn.collidepoint(mouse_pos)
                pygame.draw.rect(screen, BUTTON_HOVER_COLOR if is_hover else BUTTON_COLOR, dl_v2_btn, border_radius=10)
                pygame.draw.rect(screen, CYAN if is_hover else (120, 140, 180), dl_v2_btn, 2, border_radius=10)
                draw_text("INSTALL v2.0 UPGRADE - FREE", FONT_MEDIUM, WHITE, dl_v2_btn.centerx, dl_v2_btn.centery, screen)

        elif current_url == "http://galactic.net/v2_vault":
            draw_text("THE QUANTUM VAULT (v2.0 Exclusive)", FONT_LARGE, CYAN, bx + browser_w//2, by + 100, screen)
            
            # V2 Phantom Ship
            dl_ship_btn = pygame.Rect(bx+250, by+200, 400, 80)
            owned_ship = "v2_phantom" in state.all_player_data["P1"]["owned_ships"]
            is_hover_ship = dl_ship_btn.collidepoint(mouse_pos)
            pygame.draw.rect(screen, BUTTON_DISABLED_COLOR if owned_ship else (BUTTON_HOVER_COLOR if is_hover_ship else BUTTON_COLOR), dl_ship_btn, border_radius=10)
            pygame.draw.rect(screen, (100, 100, 120) if owned_ship else (CYAN if is_hover_ship else (120, 140, 180)), dl_ship_btn, 2, border_radius=10)
            msg_ship = "DOWNLOADED" if owned_ship else "DOWNLOAD 'V2 PHANTOM' SHIP"
            draw_text(msg_ship, FONT_MEDIUM, WHITE, dl_ship_btn.centerx, dl_ship_btn.centery, screen)
            
            # Magnetic Field Generator Powerup
            dl_pwr_btn = pygame.Rect(bx+250, by+320, 400, 80)
            owned_pwr = "power_magnet" in state.all_player_data["P1"]["unlocked_powers"]
            is_hover_pwr = dl_pwr_btn.collidepoint(mouse_pos)
            pygame.draw.rect(screen, BUTTON_DISABLED_COLOR if owned_pwr else (BUTTON_HOVER_COLOR if is_hover_pwr else BUTTON_COLOR), dl_pwr_btn, border_radius=10)
            pygame.draw.rect(screen, (100, 100, 120) if owned_pwr else (CYAN if is_hover_pwr else (120, 140, 180)), dl_pwr_btn, 2, border_radius=10)
            msg_pwr = "DOWNLOADED" if owned_pwr else "DOWNLOAD 'MAGNETIC CORE' HACK"
            draw_text(msg_pwr, FONT_MEDIUM, WHITE, dl_pwr_btn.centerx, dl_pwr_btn.centery, screen)

        elif matrix_mode:
            # Overwrite the page area with black
            pygame.draw.rect(screen, (0, 0, 0), (bx, by + 40, browser_w, browser_h - 40), border_bottom_left_radius=8, border_bottom_right_radius=8)
            font_mat = pygame.font.Font(None, 24)
            for m in matrix_chars:
                m["y"] += m["speed"]
                if m["y"] > browser_h:
                    m["y"] = random.randint(-100, 0)
                    m["x"] = random.randint(0, browser_w)
                
                # Draw the character
                if m["y"] > 40:
                    char_surf = font_mat.render(chr(random.randint(33, 126)), True, (0, 255, 0))
                    screen.blit(char_surf, (bx + m["x"], by + m["y"]))
            
            draw_text("WAKE UP, CAPTAIN...", FONT_LARGE, (200, 255, 200), bx + browser_w//2, by + browser_h//2, screen)

        else:
            draw_text("404: PAGE NOT FOUND", FONT_LARGE, RED, bx + browser_w//2, by + 300, screen)
            draw_text(f"The requested URL ({current_url}) was not found on this server.", FONT_SMALL, LIGHT_GRAY, bx + browser_w//2, by + 350, screen)

        megahack.draw(screen)
        pygame.display.flip()
        clock.tick(int(FPS * state.GAME_SPEED))

def show_audio_settings_screen(screen, clock):
    return show_settings_screen(screen, clock)

def show_settings_screen(screen, clock):
    """Full Game and Audio Settings Control Center."""
    back_btn = pygame.Rect(SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT - 70, 300, 50)
    
    # Volume control buttons
    vol_types = ["master_volume", "sfx_volume", "music_volume"]
    labels = ["Master Volume", "Sound Effects (SFX)", "Music Volume"]
    
    test_sfx = [
        ("Laser", "laser"),
        ("Heavy Blast", "heavy_laser"),
        ("Enemy Laser", "enemy_laser"),
        ("Explosion", "explosion_medium"),
        ("Boss Boom", "explosion_boss"),
        ("Powerup", "powerup_collect"),
        ("Shield Hit", "shield_hit"),
        ("Level Up", "level_up"),
        ("Alarm", "alarm_boss"),
        ("Warp Speed", "warp_speed"),
        ("Virus Laser", "virus_laser"),
        ("Coin Drop", "coin_pickup")
    ]
    
    test_music = [
        ("Menu Synth", "menu_theme"),
        ("Battle Beat", "battle_theme"),
        ("Boss Cyber", "boss_theme"),
        ("Story Void", "story_theme"),
        ("Victory!", "victory_theme")
    ]

    while True:
        mouse_pos = pygame.mouse.get_pos()
        
        # Build UI rects
        center_x = SCREEN_WIDTH // 2
        y_cursor = 130
        
        vol_rects = {}
        for idx, vkey in enumerate(vol_types):
            minus_rect = pygame.Rect(center_x - 190, y_cursor, 40, 34)
            bar_rect = pygame.Rect(center_x - 140, y_cursor, 280, 34)
            plus_rect = pygame.Rect(center_x + 150, y_cursor, 40, 34)
            vol_rects[vkey] = (minus_rect, bar_rect, plus_rect)
            y_cursor += 48
            
        # Mute & Feature toggle rects (3 buttons: SFX, Music, Copilot)
        btn_w = 180
        gap = 15
        total_w = 3 * btn_w + 2 * gap
        start_x = center_x - (total_w // 2)
        sfx_mute_rect = pygame.Rect(start_x, y_cursor + 6, btn_w, 36)
        music_mute_rect = pygame.Rect(start_x + (btn_w + gap), y_cursor + 6, btn_w, 36)
        copilot_toggle_rect = pygame.Rect(start_x + 2 * (btn_w + gap), y_cursor + 6, btn_w, 36)
        y_cursor += 50
        
        # Sound Pack Selector Rect
        sound_pack_rect = pygame.Rect(center_x - 200, y_cursor + 4, 400, 38)
        y_cursor += 58
        
        # SFX test rects
        sfx_btn_rects = []
        for i, (label, sound_id) in enumerate(test_sfx):
            col = i % 4
            row = i // 4
            r = pygame.Rect(center_x - 260 + (col * 135), y_cursor + (row * 38), 125, 32)
            sfx_btn_rects.append((r, label, sound_id))
            
        y_cursor += 130
        
        # Music test rects
        music_btn_rects = []
        for i, (label, track_id) in enumerate(test_music):
            r = pygame.Rect(center_x - 325 + (i * 132), y_cursor, 125, 32)
            music_btn_rects.append((r, label, track_id))

        for event in pygame.event.get():
            if event.type == pygame.QUIT: 
                return "QUIT_PROGRAM"
            if megahack.handle_event(event): 
                continue
            
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # Check volume minus/plus
                for vkey, (minus_r, _, plus_r) in vol_rects.items():
                    if minus_r.collidepoint(mouse_pos):
                        state.audio_settings[vkey] = max(0.0, round(state.audio_settings.get(vkey, 1.0) - 0.1, 1))
                        sound_manager.update_audio_volumes()
                        state.save_audio_config()
                        sound_manager.play_sfx("ui_click")
                    elif plus_r.collidepoint(mouse_pos):
                        state.audio_settings[vkey] = min(1.0, round(state.audio_settings.get(vkey, 1.0) + 0.1, 1))
                        sound_manager.update_audio_volumes()
                        state.save_audio_config()
                        sound_manager.play_sfx("ui_click")
                        
                # Check mute toggles
                if sfx_mute_rect.collidepoint(mouse_pos):
                    state.audio_settings["sfx_muted"] = not state.audio_settings.get("sfx_muted", False)
                    sound_manager.update_audio_volumes()
                    state.save_audio_config()
                    sound_manager.play_sfx("hack_toggle")
                    
                if music_mute_rect.collidepoint(mouse_pos):
                    state.audio_settings["music_muted"] = not state.audio_settings.get("music_muted", False)
                    sound_manager.update_audio_volumes()
                    state.save_audio_config()
                    sound_manager.play_sfx("hack_toggle")
                    
                if copilot_toggle_rect.collidepoint(mouse_pos):
                    state.audio_settings["enable_copilot"] = not state.audio_settings.get("enable_copilot", False)
                    state.save_audio_config()
                    sound_manager.play_sfx("hack_toggle")
                    
                if sound_pack_rect.collidepoint(mouse_pos):
                    cur_p = state.audio_settings.get("sound_pack", "classic")
                    new_p = "cyber" if cur_p == "classic" else "classic"
                    sound_manager.set_sound_pack(new_p)
                    
                # Check SFX test buttons
                for r, label, sound_id in sfx_btn_rects:
                    if r.collidepoint(mouse_pos):
                        sound_manager.play_sfx(sound_id, 1.0)
                        
                # Check Music test buttons
                for r, label, track_id in music_btn_rects:
                    if r.collidepoint(mouse_pos):
                        sound_manager.play_music(track_id, loop=True)
                        sound_manager.play_sfx("ui_click")
                        
                if back_btn.collidepoint(mouse_pos):
                    sound_manager.play_sfx("ui_click")
                    sound_manager.play_music("menu_theme")
                    return "HOME"
                    
            if event.type == pygame.KEYDOWN and event.key in [pygame.K_ESCAPE, pygame.K_h]:
                sound_manager.play_sfx("ui_click")
                sound_manager.play_music("menu_theme")
                return "HOME"

        screen.fill(BLACK)
        draw_stars(screen)
        
        # Header
        draw_text("⚙️ GAME SETTINGS", FONT_LARGE, CYAN, center_x, 50, screen)
        draw_text("Customize audio volume levels, sound packs, copilot assistant, and sound effects.", FONT_SMALL, LIGHT_GRAY, center_x, 88, screen)
        
        # Draw Volume Sliders
        for idx, vkey in enumerate(vol_types):
            minus_r, bar_r, plus_r = vol_rects[vkey]
            cur_val = state.audio_settings.get(vkey, 1.0)
            
            draw_text(labels[idx], FONT_MEDIUM, WHITE, minus_r.left - 20, minus_r.centery, screen, align="right")
            
            pygame.draw.rect(screen, BUTTON_HOVER_COLOR if minus_r.collidepoint(mouse_pos) else BUTTON_COLOR, minus_r, border_radius=6)
            draw_text("-", FONT_MEDIUM, WHITE, minus_r.centerx, minus_r.centery, screen)
            
            pygame.draw.rect(screen, DARK_GRAY, bar_r, border_radius=6)
            fill_w = int(bar_r.width * cur_val)
            if fill_w > 0:
                bar_color = CYAN if "master" in vkey else (YELLOW if "sfx" in vkey else MAGENTA)
                pygame.draw.rect(screen, bar_color, (bar_r.x, bar_r.y, fill_w, bar_r.height), border_radius=6)
            draw_text(f"{int(cur_val * 100)}%", FONT_SMALL, WHITE, bar_r.centerx, bar_r.centery, screen)
            
            pygame.draw.rect(screen, BUTTON_HOVER_COLOR if plus_r.collidepoint(mouse_pos) else BUTTON_COLOR, plus_r, border_radius=6)
            draw_text("+", FONT_MEDIUM, WHITE, plus_r.centerx, plus_r.centery, screen)
            
        # Draw Mute Toggles
        sfx_muted = state.audio_settings.get("sfx_muted", False)
        sfx_color = MOD_OFF_COLOR if sfx_muted else MOD_ON_COLOR
        pygame.draw.rect(screen, sfx_color, sfx_mute_rect, border_radius=8)
        draw_text(f"SFX: {'MUTED' if sfx_muted else 'ENABLED'}", FONT_SMALL, WHITE, sfx_mute_rect.centerx, sfx_mute_rect.centery, screen)
        
        mus_muted = state.audio_settings.get("music_muted", False)
        mus_color = MOD_OFF_COLOR if mus_muted else MOD_ON_COLOR
        pygame.draw.rect(screen, mus_color, music_mute_rect, border_radius=8)
        draw_text(f"Music: {'MUTED' if mus_muted else 'ENABLED'}", FONT_SMALL, WHITE, music_mute_rect.centerx, music_mute_rect.centery, screen)
        
        copilot_enabled = state.audio_settings.get("enable_copilot", False)
        copilot_color = MOD_ON_COLOR if copilot_enabled else MOD_OFF_COLOR
        pygame.draw.rect(screen, copilot_color, copilot_toggle_rect, border_radius=8)
        draw_text(f"Copilot: {'ON' if copilot_enabled else 'OFF'}", FONT_SMALL, WHITE, copilot_toggle_rect.centerx, copilot_toggle_rect.centery, screen)

        
        # Draw Sound Pack Selector Button
        cur_pack = state.audio_settings.get("sound_pack", "classic").title()
        pack_btn_color = (0, 130, 200) if cur_pack.lower() == "cyber" else (180, 100, 20)
        if sound_pack_rect.collidepoint(mouse_pos):
            pack_btn_color = (0, 170, 255) if cur_pack.lower() == "cyber" else (220, 130, 30)
        pygame.draw.rect(screen, pack_btn_color, sound_pack_rect, border_radius=8)
        pygame.draw.rect(screen, (200, 230, 255) if sound_pack_rect.collidepoint(mouse_pos) else (80, 100, 140), sound_pack_rect, 2, border_radius=8)
        draw_text(f"🔊 SOUND SET: [{cur_pack.upper()} ACTIVE]  (Click to Switch)", FONT_SMALL, WHITE, sound_pack_rect.centerx, sound_pack_rect.centery, screen)
        
        # Draw SFX Test Section
        draw_text("─── Test Sound Effects ───", FONT_SMALL, YELLOW, center_x, sfx_btn_rects[0][0].top - 16, screen)
        for r, label, _ in sfx_btn_rects:
            c = BUTTON_HOVER_COLOR if r.collidepoint(mouse_pos) else (50, 60, 90)
            pygame.draw.rect(screen, c, r, border_radius=6)
            draw_text(label, FONT_SMALL, WHITE, r.centerx, r.centery, screen)
            
        # Draw Music Test Section
        draw_text("─── Switch Music Soundtrack ───", FONT_SMALL, MAGENTA, center_x, music_btn_rects[0][0].top - 16, screen)
        for r, label, track_id in music_btn_rects:
            is_active = (sound_manager.SoundManager.get_instance().current_music_track == track_id)
            c = (140, 40, 100) if is_active else (BUTTON_HOVER_COLOR if r.collidepoint(mouse_pos) else (60, 40, 70))
            pygame.draw.rect(screen, c, r, border_radius=6)
            draw_text(label, FONT_SMALL, YELLOW if is_active else WHITE, r.centerx, r.centery, screen)

        # Back Button
        pygame.draw.rect(screen, BUTTON_HOVER_COLOR if back_btn.collidepoint(mouse_pos) else BUTTON_COLOR, back_btn, border_radius=10)
        draw_text("Save & Return to Home", FONT_MEDIUM, WHITE, back_btn.centerx, back_btn.centery, screen)
        
        megahack.draw(screen)
        pygame.display.flip()
        clock.tick(int(FPS * state.GAME_SPEED))

def show_instructions_screen(screen, clock, mode):
    center_x = SCREEN_WIDTH // 2
    center_y = SCREEN_HEIGHT // 2
    
    card_w = 640
    card_h = 380
    card_rect = pygame.Rect(center_x - card_w // 2, center_y - card_h // 2, card_w, card_h)
    
    start_btn = pygame.Rect(center_x - 140, card_rect.bottom - 70, 280, 45)

    while True:
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT: 
                return "QUIT_PROGRAM"
            if megahack.handle_event(event): 
                continue
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if start_btn.collidepoint(mouse_pos):
                    sound_manager.play_sfx("ui_click")
                    return
            if event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_SPACE, pygame.K_RETURN, pygame.K_ESCAPE]:
                    sound_manager.play_sfx("ui_click")
                    return

        screen.fill(BLACK)
        draw_stars(screen)
        
        # Briefing Card
        pygame.draw.rect(screen, (20, 25, 35), card_rect, border_radius=12)
        pygame.draw.rect(screen, CYAN, card_rect, 2, border_radius=12)
        
        draw_text("MISSION BRIEFING", FONT_LARGE, YELLOW, center_x, card_rect.top + 40, screen)
        draw_text(f"Mode: {mode.replace('PLAYING_', '').replace('_', ' ')}", FONT_SMALL, (160, 190, 220), center_x, card_rect.top + 75, screen)
        
        # Player 1 controls
        p1_box = pygame.Rect(center_x - 280, card_rect.top + 105, 560, 50)
        pygame.draw.rect(screen, (30, 40, 60), p1_box, border_radius=8)
        draw_text("PILOT 1:", FONT_MEDIUM, CYAN, p1_box.left + 70, p1_box.centery, screen)
        draw_text("[W][A][S][D] Move   |   [SPACE] Shoot", FONT_MEDIUM, WHITE, p1_box.left + 330, p1_box.centery, screen)
        
        # Player 2 controls (if multiplayer)
        if "MULTI" in mode or "LAN" in mode or "CLOUD" in mode:
            p2_box = pygame.Rect(center_x - 280, card_rect.top + 165, 560, 50)
            pygame.draw.rect(screen, (40, 30, 50), p2_box, border_radius=8)
            draw_text("PILOT 2:", FONT_MEDIUM, MAGENTA, p2_box.left + 70, p2_box.centery, screen)
            draw_text("[ARROWS] Move   |   [ENTER] Shoot", FONT_MEDIUM, WHITE, p2_box.left + 330, p2_box.centery, screen)
        else:
            tip_box = pygame.Rect(center_x - 280, card_rect.top + 165, 560, 50)
            pygame.draw.rect(screen, (30, 35, 45), tip_box, border_radius=8)
            draw_text("Collect glowing power-ups for Shields and Triple Blasters!", FONT_SMALL, (180, 210, 240), tip_box.centerx, tip_box.centery, screen)

        # Launch Button
        is_hover = start_btn.collidepoint(mouse_pos)
        pygame.draw.rect(screen, BUTTON_HOVER_COLOR if is_hover else WIN_GREEN, start_btn, border_radius=8)
        draw_text("LAUNCH MISSION", FONT_MEDIUM, BLACK if not is_hover else WHITE, start_btn.centerx, start_btn.centery, screen)

        draw_text("Press SPACE or Click Launch to Begin", FONT_SMALL, LIGHT_GRAY, center_x, card_rect.bottom + 25, screen)

        megahack.draw(screen)
        pygame.display.flip()
        clock.tick(int(FPS * state.GAME_SPEED))

def show_game_over_screen(screen, clock, did_win_game, winner_id=0):
    center_x = SCREEN_WIDTH // 2
    center_y = SCREEN_HEIGHT // 2
    
    card_w = 600
    card_h = 380
    card_rect = pygame.Rect(center_x - card_w // 2, center_y - card_h // 2, card_w, card_h)
    
    home_btn = pygame.Rect(center_x - 220, card_rect.bottom - 65, 200, 45)
    quit_btn = pygame.Rect(center_x + 20, card_rect.bottom - 65, 200, 45)

    while True:
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT: 
                return "QUIT_PROGRAM"
            if megahack.handle_event(event): 
                continue
                
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if home_btn.collidepoint(mouse_pos):
                    sound_manager.play_sfx("ui_click")
                    return "HOME"
                elif quit_btn.collidepoint(mouse_pos):
                    sound_manager.play_sfx("ui_click")
                    return "QUIT_PROGRAM"
                    
            if event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_h, pygame.K_SPACE, pygame.K_RETURN, pygame.K_ESCAPE]: 
                    sound_manager.play_sfx("ui_click")
                    return "HOME"
                elif event.key == pygame.K_q: 
                    return "QUIT_PROGRAM"

        screen.fill(BLACK)
        draw_stars(screen)
        
        # Summary Card
        card_border_color = WIN_GREEN if did_win_game else LOSE_RED
        pygame.draw.rect(screen, (20, 22, 32), card_rect, border_radius=12)
        pygame.draw.rect(screen, card_border_color, card_rect, 2, border_radius=12)
        
        # Title
        title_text = "VICTORY ACHIEVED!" if did_win_game else "MISSION FAILED"
        draw_text(title_text, FONT_XLARGE, card_border_color, center_x, card_rect.top + 45, screen)
        
        # Stats
        stats_y = card_rect.top + 105
        stat_box1 = pygame.Rect(center_x - 240, stats_y, 480, 40)
        pygame.draw.rect(screen, (30, 35, 50), stat_box1, border_radius=6)
        draw_text(f"P1 Final Score: {state.score_p1}", FONT_MEDIUM, YELLOW, stat_box1.centerx, stat_box1.centery, screen)
        
        if state.score_p2 > 0:
            stat_box2 = pygame.Rect(center_x - 240, stats_y + 48, 480, 40)
            pygame.draw.rect(screen, (30, 35, 50), stat_box2, border_radius=6)
            draw_text(f"P2 Final Score: {state.score_p2}", FONT_MEDIUM, MAGENTA, stat_box2.centerx, stat_box2.centery, screen)
            
        sector_box = pygame.Rect(center_x - 240, stats_y + (96 if state.score_p2 > 0 else 48), 480, 40)
        pygame.draw.rect(screen, (30, 35, 50), sector_box, border_radius=6)
        draw_text(f"Sector Reached: {state.level}", FONT_MEDIUM, CYAN, sector_box.centerx, sector_box.centery, screen)
        
        # Action Buttons
        pygame.draw.rect(screen, BUTTON_HOVER_COLOR if home_btn.collidepoint(mouse_pos) else BUTTON_COLOR, home_btn, border_radius=8)
        draw_text("Return to Home (H)", FONT_MEDIUM, WHITE, home_btn.centerx, home_btn.centery, screen)
        
        pygame.draw.rect(screen, (150, 40, 40) if quit_btn.collidepoint(mouse_pos) else (110, 30, 30), quit_btn, border_radius=8)
        draw_text("Quit Game (Q)", FONT_MEDIUM, WHITE, quit_btn.centerx, quit_btn.centery, screen)
        
        megahack.draw(screen)
        pygame.display.flip()
        clock.tick(int(FPS * state.GAME_SPEED))

def show_engine_room(screen, clock):
    panels = [
        {"rect": pygame.Rect(SCREEN_WIDTH//2 - 200, 250, 150, 150), "status": "BROKEN"},
        {"rect": pygame.Rect(SCREEN_WIDTH//2 + 50, 250, 150, 150), "status": "BROKEN"},
        {"rect": pygame.Rect(SCREEN_WIDTH//2 - 200, 450, 150, 150), "status": "BROKEN"},
        {"rect": pygame.Rect(SCREEN_WIDTH//2 + 50, 450, 150, 150), "status": "BROKEN"}
    ]
    
    particles = []
    alarm_timer = 0
    break_timer = 0
    
    sound_manager.play_sfx("alarm_boss")

    while True:
        mouse_pos = pygame.mouse.get_pos()
        dt = clock.tick(int(FPS * state.GAME_SPEED))
        
        all_fixed = all(p["status"] == "FIXED" for p in panels)
        if all_fixed:
            sound_manager.play_sfx("level_up")
            return "CONTROL_ROOM"
        
        break_timer += dt
        if break_timer > 2500:
            break_timer = 0
            fixed_panels = [p for p in panels if p["status"] == "FIXED"]
            if fixed_panels and random.random() > 0.4:
                p = random.choice(fixed_panels)
                p["status"] = "BROKEN"
                sound_manager.play_sfx("shield_hit")
                for _ in range(20):
                    particles.append([p["rect"].centerx, p["rect"].centery, random.uniform(-5, 5), random.uniform(-5, 5), random.randint(20, 40)])
        
        alarm_timer += dt
        if alarm_timer > 2000:
            alarm_timer = 0
            sound_manager.play_sfx("alarm_boss", volume_scale=0.5)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "QUIT_PROGRAM"
            if megahack.handle_event(event): continue
            if event.type == pygame.MOUSEBUTTONDOWN:
                for p in panels:
                    if p["rect"].collidepoint(event.pos) and p["status"] == "BROKEN":
                        p["status"] = "FIXED"
                        sound_manager.play_sfx("powerup_collect")
                        for _ in range(15):
                            particles.append([event.pos[0], event.pos[1], random.uniform(-3, 3), random.uniform(-3, 3), random.randint(10, 30)])
        
        screen.fill((20, 0, 0))
        draw_stars(screen)
        
        if pygame.time.get_ticks() % 1000 < 500:
            draw_text("WARNING: ENGINE FAILURE", FONT_LARGE, RED, SCREEN_WIDTH // 2, 80, screen)
        draw_text("Click broken (red) panels to repair them before they break again!", FONT_MEDIUM, WHITE, SCREEN_WIDTH // 2, 140, screen)
        
        for i, p in enumerate(panels):
            color = RED if p["status"] == "BROKEN" else WIN_GREEN
            hover_color = (255, 100, 100) if p["status"] == "BROKEN" else (100, 255, 100)
            draw_color = hover_color if p["rect"].collidepoint(mouse_pos) else color
            
            pygame.draw.rect(screen, draw_color, p["rect"], border_radius=15)
            pygame.draw.rect(screen, WHITE, p["rect"], 3, border_radius=15)
            draw_text(f"PANEL {i+1}", FONT_MEDIUM, BLACK, p["rect"].centerx, p["rect"].centery - 20, screen)
            draw_text(p["status"], FONT_MEDIUM, BLACK, p["rect"].centerx, p["rect"].centery + 20, screen)
            
            if p["status"] == "BROKEN" and random.random() < 0.1:
                particles.append([p["rect"].centerx + random.randint(-50, 50), p["rect"].centery + random.randint(-50, 50), random.uniform(-4, 4), random.uniform(-4, 4), random.randint(15, 30)])

        for part in particles[:]:
            part[0] += part[2]
            part[1] += part[3]
            part[4] -= 1
            if part[4] <= 0:
                particles.remove(part)
            else:
                pygame.draw.circle(screen, (255, 165, 0), (int(part[0]), int(part[1])), max(1, part[4]//5))

        megahack.draw(screen)
        pygame.display.flip()

def show_control_room(screen, clock):
    sound_manager.play_music("menu_theme")
    warp_speed = 10
    
    while True:
        mouse_pos = pygame.mouse.get_pos()
        dt = clock.tick(int(FPS * state.GAME_SPEED))
        
        start_btn = pygame.Rect(SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT // 2 + 50, 400, 60)
        back_btn = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 130, 200, 40)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "QUIT_PROGRAM"
            if megahack.handle_event(event): continue
            if event.type == pygame.MOUSEBUTTONDOWN:
                if start_btn.collidepoint(event.pos):
                    sound_manager.play_sfx("ui_click")
                    return "PLAYING_SINGLE_CLASSIC"
                if back_btn.collidepoint(event.pos):
                    sound_manager.play_sfx("ui_click")
                    return "HOME"
        
        screen.fill((10, 15, 25))
        
        for s in stars:
            s[1] += s[2] * warp_speed
            if s[1] > SCREEN_HEIGHT:
                s[1] = 0
                s[0] = random.randint(0, SCREEN_WIDTH)
            pygame.draw.circle(screen, WHITE, (int(s[0]), int(s[1])), int(s[2]))
        
        pygame.draw.rect(screen, (30, 40, 60), (0, 0, SCREEN_WIDTH, 120))
        pygame.draw.rect(screen, (30, 40, 60), (0, SCREEN_HEIGHT - 120, SCREEN_WIDTH, 120))
        
        draw_text("SYSTEMS ONLINE. YOU HAVE THE CONN.", FONT_LARGE, CYAN, SCREEN_WIDTH // 2, 60, screen)
        draw_text("Control Room initialized. Awaiting commands...", FONT_MEDIUM, LIGHT_GRAY, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50, screen)
        
        pygame.draw.rect(screen, WIN_GREEN if start_btn.collidepoint(mouse_pos) else (40, 150, 60), start_btn, border_radius=10)
        pygame.draw.rect(screen, WHITE, start_btn, 2, border_radius=10)
        draw_text("INITIATE LAUNCH (SINGLE PLAYER)", FONT_MEDIUM, WHITE, start_btn.centerx, start_btn.centery, screen)
        
        pygame.draw.rect(screen, BUTTON_HOVER_COLOR if back_btn.collidepoint(mouse_pos) else BUTTON_COLOR, back_btn, border_radius=8)
        draw_text("Return to Main Menu", FONT_SMALL, WHITE, back_btn.centerx, back_btn.centery, screen)
        
        megahack.draw(screen)
        pygame.display.flip()