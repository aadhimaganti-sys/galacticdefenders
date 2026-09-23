import pygame
import random
import os
import sys
from settings import *
import state
import megahack
import sound_manager

stars = [[random.randint(0, SCREEN_WIDTH), random.randint(0, SCREEN_HEIGHT), random.uniform(1, 4)] for _ in range(100)]

def draw_text(text, font, color, x, y, surface, align="center"):
    text_surface = font.render(str(text), True, color)
    rect = text_surface.get_rect()
    if align == "center":
        rect.center = (x, y)
    elif align == "left":
        rect.midleft = (x, y)
    elif align == "right":
        rect.midright = (x, y)
    elif align == "topleft":
        rect.topleft = (x, y)
    elif align == "topright":
        rect.topright = (x, y)
    elif align == "midtop":
        rect.midtop = (x, y)
    surface.blit(text_surface, rect)
    return rect

def draw_stars(surface):
    for s in stars:
        s[1] += s[2] * state.GAME_SPEED
        if s[1] > SCREEN_HEIGHT:
            s[1] = 0
            s[0] = random.randint(0, SCREEN_WIDTH)
        pygame.draw.circle(surface, WHITE if s[2] > 2.5 else LIGHT_GRAY, (int(s[0]), int(s[1])), int(s[2]))

def draw_scrollable_menu(screen, options, offset, mouse_pos, title, font_t, color_t, y_t, currency=None):
    screen.fill(BLACK)
    draw_stars(screen)
    draw_text(title, font_t, color_t, SCREEN_WIDTH // 2, y_t, screen)
    if currency:
        draw_text(currency, FONT_MEDIUM, YELLOW, SCREEN_WIDTH - 250, y_t, screen, align="right")
        
    for opt in options:
        r = opt["rect"].copy()
        r.centery = opt["original_y"] + offset
        
        if r.bottom > y_t + 50 and r.top < SCREEN_HEIGHT - 100:
            color = opt.get("override_color", BUTTON_COLOR)
            if r.collidepoint(mouse_pos) and not opt.get("is_owned", False):
                color = BUTTON_HOVER_COLOR
            if opt.get("is_owned", False):
                color = BUTTON_DISABLED_COLOR
                
            pygame.draw.rect(screen, color, r, border_radius=10)
            pygame.draw.rect(screen, (80, 100, 140), r, 2, border_radius=10)
            draw_text(opt["text"], FONT_MEDIUM, WHITE, r.centerx, r.centery, screen)
            if "desc" in opt:
                draw_text(opt["desc"], FONT_SMALL, LIGHT_GRAY, r.centerx, r.centery + 20, screen)

def show_home_screen(screen, clock):
    selected_p1 = state.SHIP_TYPES.get(state.all_player_data["P1"]["selected_ship"], BASE_SHIP_TYPES["default_jet"])["name"]
    credits_p1 = state.all_player_data["P1"]["credits"]
    
    col1_options = [
        {"text": "Single Player (Classic)", "action": "PLAYING_SINGLE_CLASSIC", "color": (30, 80, 140)},
        {"text": "Single Player (Boss Mode)", "action": "PLAYING_SINGLE_BOSS", "color": (140, 40, 60)},
        {"text": "Local Co-op (Classic)", "action": "PLAYING_MULTI_CLASSIC", "color": (40, 100, 120)},
        {"text": "Local Co-op (Boss Mode)", "action": "PLAYING_MULTI_BOSS", "color": (120, 40, 90)},
        {"text": "??? STORY CAMPAIGN ???", "action": "PLAYING_SPINOFF", "color": (180, 0, 80)},
        {"text": "ENTER SECRET PROTOCOL", "action": "PASSWORD_SCREEN", "color": (100, 0, 0)},
    ]
    
    col2_options = [
        {"text": "Host LAN Game", "action": "HOST_LAN_MENU", "color": (40, 90, 130)},
        {"text": "Join LAN Game", "action": "JOIN_LAN_MENU", "color": (40, 90, 130)},
        {"text": "Host GLOBAL Cloud", "action": "HOST_CLOUD", "color": (100, 0, 150)},
        {"text": "Join GLOBAL Cloud", "action": "JOIN_CLOUD", "color": (100, 0, 150)},
        {"text": "Galactic Web Browser", "action": "WEB_BROWSER", "color": (0, 100, 100)},
        {"text": "Store / Armory (P1)", "action": "STORE_P1", "color": (60, 110, 50)},
        {"text": "Select Ship (P1)", "action": "SELECT_SHIP_P1", "color": (70, 90, 120)},
        {"text": "🔊 Audio & Music Settings", "action": "AUDIO_SETTINGS", "color": (30, 80, 140)},
        {"text": "Datapack Mod Loader", "action": "MOD_LOADER", "color": (110, 60, 120)},
        {"text": "GUI Level Architect", "action": "LEVEL_EDITOR", "color": (0, 120, 60)},
        {"text": "Quit Game", "action": "QUIT_PROGRAM", "color": (120, 30, 30)},
    ]

    button_w = 340
    button_h = 38
    pad_y = 8
    
    center_x = SCREEN_WIDTH // 2
    col1_x = center_x - button_w - 20
    col2_x = center_x + 20
    
    y_start = 175

    for i, opt in enumerate(col1_options):
        opt["rect"] = pygame.Rect(col1_x, y_start + i * (button_h + pad_y), button_w, button_h)

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
                if event.key in [pygame.K_BACKQUOTE, pygame.K_F12]: 
                    sound_manager.play_sfx("ui_click")
                    return "ADMIN_PANEL"

        screen.fill(BLACK)
        draw_stars(screen)
        
        # Header & Title
        draw_text("GALACTIC DEFENDERS", FONT_XLARGE, CYAN, center_x, 50, screen)
        
        # Pilot Status Badge
        badge_w = 560
        badge_rect = pygame.Rect(center_x - badge_w // 2, 92, badge_w, 36)
        pygame.draw.rect(screen, (20, 25, 40), badge_rect, border_radius=18)
        pygame.draw.rect(screen, (60, 90, 140), badge_rect, 2, border_radius=18)
        draw_text(f"PILOT: P1   |   CREDITS: {credits_p1} Cr   |   SHIP: {selected_p1}", FONT_MEDIUM, YELLOW, center_x, 110, screen)
        
        # Column Headers
        draw_text("─── MISSION SELECT ───", FONT_SMALL, (150, 180, 220), col1_x + button_w // 2, y_start - 20, screen)
        draw_text("─── NETWORK & HANGAR ───", FONT_SMALL, (150, 180, 220), col2_x + button_w // 2, y_start - 20, screen)
        
        # Draw Buttons
        for opt in all_buttons:
            is_hover = opt["rect"].collidepoint(mouse_pos)
            base_col = opt.get("color", BUTTON_COLOR)
            c = BUTTON_HOVER_COLOR if is_hover else base_col
            pygame.draw.rect(screen, c, opt["rect"], border_radius=8)
            pygame.draw.rect(screen, (200, 220, 255) if is_hover else (60, 70, 90), opt["rect"], 2 if is_hover else 1, border_radius=8)
            draw_text(opt["text"], FONT_MEDIUM, WHITE, opt["rect"].centerx, opt["rect"].centery, screen)

        # Bottom shortcut info
        draw_text("Press TAB for MegaHack Menu  |  F12 Developer Console  |  ESC Quit", FONT_SMALL, (120, 130, 150), center_x, SCREEN_HEIGHT - 25, screen)

        megahack.draw(screen)
        pygame.display.flip()
        clock.tick(int(FPS * state.GAME_SPEED))

def show_store_screen(screen, clock, player_id_str):
    player_data = state.all_player_data[player_id_str]
    has_mod_loader = "power_modloader" in player_data["unlocked_powers"]
    btn_h, pad, start_y, fixed_title_y = 60, 20, 150, 70
    store_items = []

    for ship_key, ship_data in state.SHIP_TYPES.items():
        if ship_key == "default_jet" or ship_data["cost"] in ["CHIP_RARE", "CHIP_EPIC"]: continue
        cost_display = "FREE (Mod Loader)" if (has_mod_loader and ship_data.get("from_datapack", False)) else f"Cost: {ship_data['cost']} Cr"
        store_items.append({"key": ship_key, "text": f"{ship_data['name']} - {cost_display}", "original_y": 0, "rect": None, "data": ship_data, "is_owned": ship_key in player_data["owned_ships"], "desc": ship_data["desc"]})

    for helper_key, helper_data in state.HELPER_TYPES.items():
        cost_display = "FREE (Mod Loader)" if (has_mod_loader and helper_data.get("from_datapack", False)) else f"Cost: {helper_data['cost']} Cr"
        store_items.append({"key": helper_key, "text": f"{helper_data['name']} - {cost_display}", "original_y": 0, "rect": None, "data": helper_data, "is_helper": True, "is_owned": helper_key in player_data["unlocked_powers"], "desc": helper_data["desc"]})

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
                            item_cost = 0 if (has_mod_loader and item["data"].get("from_datapack", False)) else item["data"]["cost"]
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

        draw_scrollable_menu(screen, store_items, scroll_offset, mouse_pos, f"{player_id_str}'s Armory", FONT_LARGE, YELLOW, fixed_title_y, currency=f"Credits: {player_data['credits']}")
        pygame.draw.rect(screen, BUTTON_HOVER_COLOR if back_btn.collidepoint(mouse_pos) else BUTTON_COLOR, back_btn, border_radius=10)
        draw_text("Back to Home", FONT_MEDIUM, WHITE, back_btn.centerx, back_btn.centery, screen)
        
        megahack.draw(screen)
        pygame.display.flip()
        clock.tick(int(FPS * state.GAME_SPEED))

def show_ship_selection_screen(screen, clock, player_id_str):
    player_data = state.all_player_data[player_id_str]
    start_y, fixed_title_y = 150, 70
    selectable_ships = []

    for ship_key in player_data["owned_ships"]:
        ship_data = state.SHIP_TYPES.get(ship_key)
        if not ship_data: continue
        text = ship_data["name"] + (" [SELECTED]" if ship_key == player_data["selected_ship"] else "")
        selectable_ships.append({"key": ship_key, "text": text, "original_y": 0, "rect": None, "data": ship_data, "desc": ship_data["desc"]})

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
    start_y, fixed_title_y = 150, 70
    back_btn = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 60, 200, 50)
    scroll_offset = 0

    while True:
        mod_files = [f for f in os.listdir(BASE_DIR) if f.endswith(".json") and f not in ["galactic_defender_progress.json", "mod_config.json", "custom_level.json"]]
        mod_items = []
        for i, f_name in enumerate(mod_files):
            is_active = f_name in state.active_mods
            mod_items.append({"key": f_name, "text": f"{f_name} - [{'ON' if is_active else 'OFF'}]", "original_y": start_y + i * 80, "rect": pygame.Rect(SCREEN_WIDTH // 2 - 250, start_y + i * 80, 500, 60), "override_color": MOD_ON_COLOR if is_active else MOD_OFF_COLOR})

        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT: return "QUIT_PROGRAM"
            if megahack.handle_event(event): continue
                
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    for item in mod_items:
                        item_rect = item["rect"].copy()
                        item_rect.centery = item["original_y"] + scroll_offset
                        if item_rect.collidepoint(mouse_pos):
                            if item["key"] in state.active_mods: state.active_mods.remove(item["key"])
                            else: state.active_mods.append(item["key"])
                            state.save_mod_config()
                            state.reload_mods()
                            sound_manager.play_sfx("hack_toggle")
                    if back_btn.collidepoint(mouse_pos): 
                        sound_manager.play_sfx("ui_click")
                        return "HOME"
                elif event.button == 4: scroll_offset = min(scroll_offset + 80, 0)
                elif event.button == 5:
                    if mod_items:
                        max_scroll = -((mod_items[-1]["original_y"] - start_y + 80) - (SCREEN_HEIGHT - (fixed_title_y + 120)))
                        scroll_offset = max(scroll_offset - 80, max_scroll) if max_scroll < 0 else 0
                        
            if event.type == pygame.KEYDOWN and event.key in [pygame.K_ESCAPE, pygame.K_h]: 
                sound_manager.play_sfx("ui_click")
                return "HOME"

        draw_scrollable_menu(screen, mod_items, scroll_offset, mouse_pos, "MOD LOADER", FONT_LARGE, MAGENTA, fixed_title_y)
        pygame.draw.rect(screen, BUTTON_HOVER_COLOR if back_btn.collidepoint(mouse_pos) else BUTTON_COLOR, back_btn, border_radius=10)
        draw_text("Back to Home", FONT_MEDIUM, WHITE, back_btn.centerx, back_btn.centery, screen)
        
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

def show_admin_options(screen, clock):
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: return "QUIT_PROGRAM"
            if megahack.handle_event(event): continue
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: return "HOME"
                if event.key == pygame.K_BACKQUOTE: state.ADMIN_GOD_MODE = not state.ADMIN_GOD_MODE
                if event.key == pygame.K_1:
                    state.all_player_data["P1"]["credits"] += 10000
                    state.save_game_progress()
                    
        screen.fill(BLACK)
        draw_stars(screen)
        draw_text("DEVELOPER CONSOLE", FONT_LARGE, RED, SCREEN_WIDTH // 2, 60, screen)
        draw_text(f"God Mode (In-Game ~ key): {'ENABLED' if state.ADMIN_GOD_MODE else 'OFF'}", FONT_MEDIUM, WHITE, SCREEN_WIDTH // 2, 160, screen)
        draw_text("1: Give 10,000 Credits to P1", FONT_MEDIUM, LIGHT_GRAY, SCREEN_WIDTH // 2, 220, screen)
        draw_text("Press ESC to return.", FONT_SMALL, YELLOW, SCREEN_WIDTH // 2, 540, screen)

        megahack.draw(screen)
        pygame.display.flip()
        clock.tick(int(FPS * state.GAME_SPEED))

def show_web_browser_screen(screen, clock):
    current_url = "http://galactic.net/home"

    while True:
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT: return "QUIT_PROGRAM"
            if megahack.handle_event(event): continue
            
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                bx, by = SCREEN_WIDTH // 2 - 450, SCREEN_HEIGHT // 2 - 325
                browser_w, browser_h = 900, 650
                
                if pygame.Rect(bx + browser_w - 40, by + 5, 30, 30).collidepoint(mouse_pos): return "HOME"
                if pygame.Rect(bx + 10, by + 5, 60, 30).collidepoint(mouse_pos): current_url = "http://galactic.net/home"
                
                if current_url == "http://galactic.net/home":
                    if pygame.Rect(bx+250, by+250, 400, 50).collidepoint(mouse_pos): current_url = "http://darknet.galactic/megahack"
                    if pygame.Rect(bx+250, by+320, 400, 50).collidepoint(mouse_pos): current_url = "http://galactic.net/shipyard"
                    if pygame.Rect(bx+250, by+390, 400, 50).collidepoint(mouse_pos): current_url = "http://galactic.net/bounties"
                        
                elif current_url == "http://darknet.galactic/megahack":
                    # Instant download bypass because we removed the restriction!
                    if pygame.Rect(bx+300, by+350, 300, 60).collidepoint(mouse_pos): 
                        state.all_player_data["P1"]["has_downloaded_cheat_menu"] = True
                        state.save_game_progress()
                        
                elif current_url == "http://galactic.net/shipyard":
                    if pygame.Rect(bx+250, by+300, 400, 80).collidepoint(mouse_pos) and state.all_player_data["P1"]["credits"] >= 8000:
                        state.all_player_data["P1"]["credits"] -= 8000
                        state.all_player_data["P1"]["owned_ships"].append("shadow_wraith")
                        state.save_game_progress()
            
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE: return "HOME"

        screen.fill((20, 40, 60))
        bx, by = SCREEN_WIDTH // 2 - 450, SCREEN_HEIGHT // 2 - 325
        browser_w, browser_h = 900, 650
        
        # Browser Frame
        pygame.draw.rect(screen, (200, 200, 200), (bx, by, browser_w, browser_h), border_radius=8)
        pygame.draw.rect(screen, (150, 150, 150), (bx, by, browser_w, 40), border_radius=8)
        pygame.draw.rect(screen, (10, 15, 20), (bx, by + 40, browser_w, browser_h - 40), border_bottom_left_radius=8, border_bottom_right_radius=8)
        
        # Address Bar
        pygame.draw.rect(screen, DARK_GRAY, pygame.Rect(bx + 10, by + 5, 60, 30), border_radius=4)
        draw_text("HOME", FONT_SMALL, WHITE, bx + 40, by + 20, screen)
        
        url_bar_rect = pygame.Rect(bx + 80, by + 5, browser_w - 130, 30)
        pygame.draw.rect(screen, WHITE, url_bar_rect, border_radius=4)
        draw_text(current_url, FONT_SMALL, BLACK, url_bar_rect.left + 10, url_bar_rect.centery, screen, align="left")
        
        pygame.draw.rect(screen, RED, pygame.Rect(bx + browser_w - 40, by + 5, 30, 30), border_radius=4)
        draw_text("X", FONT_SMALL, WHITE, bx + browser_w - 25, by + 20, screen)
        
        # Page Content
        if current_url == "http://galactic.net/home":
            draw_text("GALACTIC WEB PORTAL", FONT_LARGE, CYAN, bx + browser_w//2, by + 120, screen)
            link1, link2, link3 = pygame.Rect(bx+250, by+230, 400, 50), pygame.Rect(bx+250, by+300, 400, 50), pygame.Rect(bx+250, by+370, 400, 50)
            for r, t, col in [(link1, "▶ Darknet: MegaHack v7", MAGENTA), (link2, "▶ Black Market Shipyard", ORANGE), (link3, "▶ Bounty Board", YELLOW)]:
                pygame.draw.rect(screen, (50, 50, 80), r, border_radius=8)
                pygame.draw.rect(screen, (80, 80, 120), r, 2, border_radius=8)
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
            
        elif current_url == "http://galactic.net/bounties":
            draw_text("BOUNTY BOARD", FONT_LARGE, YELLOW, bx + browser_w//2, by + 150, screen)
            draw_text("Bounties currently disabled by Galactic Federation.", FONT_MEDIUM, RED, bx + browser_w//2, by + 300, screen)

        megahack.draw(screen)
        pygame.display.flip()
        clock.tick(int(FPS * state.GAME_SPEED))

def show_audio_settings_screen(screen, clock):
    """Full Audio and Music Settings Control Center."""
    back_btn = pygame.Rect(SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT - 70, 300, 50)
    
    # Volume control buttons
    vol_types = ["master_volume", "sfx_volume", "music_volume"]
    labels = ["Master Volume", "Sound Effects (SFX)", "Music Volume"]
    
    test_sfx = [
        ("Laser", "laser"),
        ("Heavy Blast", "heavy_laser"),
        ("Explosion", "explosion_medium"),
        ("Boss Boom", "explosion_boss"),
        ("Powerup", "powerup_collect"),
        ("Shield Hit", "shield_hit"),
        ("Level Up", "level_up"),
        ("Alarm", "alarm_boss")
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
        y_cursor = 140
        
        vol_rects = {}
        for idx, vkey in enumerate(vol_types):
            minus_rect = pygame.Rect(center_x - 190, y_cursor, 40, 36)
            bar_rect = pygame.Rect(center_x - 140, y_cursor, 280, 36)
            plus_rect = pygame.Rect(center_x + 150, y_cursor, 40, 36)
            vol_rects[vkey] = (minus_rect, bar_rect, plus_rect)
            y_cursor += 55
            
        # Mute toggle rects
        sfx_mute_rect = pygame.Rect(center_x - 180, y_cursor + 10, 170, 40)
        music_mute_rect = pygame.Rect(center_x + 10, y_cursor + 10, 170, 40)
        y_cursor += 75
        
        # SFX test rects
        sfx_btn_rects = []
        for i, (label, sound_id) in enumerate(test_sfx):
            col = i % 4
            row = i // 4
            r = pygame.Rect(center_x - 260 + (col * 135), y_cursor + (row * 42), 125, 34)
            sfx_btn_rects.append((r, label, sound_id))
            
        y_cursor += 105
        
        # Music test rects
        music_btn_rects = []
        for i, (label, track_id) in enumerate(test_music):
            r = pygame.Rect(center_x - 325 + (i * 132), y_cursor, 125, 34)
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
        draw_text("🔊 AUDIO & MUSIC CONTROLS", FONT_LARGE, CYAN, center_x, 60, screen)
        draw_text("Customize sound levels, test stereo sound effects, and switch music tracks.", FONT_SMALL, LIGHT_GRAY, center_x, 100, screen)
        
        # Draw Volume Sliders
        for idx, vkey in enumerate(vol_types):
            minus_r, bar_r, plus_r = vol_rects[vkey]
            cur_val = state.audio_settings.get(vkey, 1.0)
            
            # Label (using align='right' correctly!)
            draw_text(labels[idx], FONT_MEDIUM, WHITE, minus_r.left - 20, minus_r.centery, screen, align="right")
            
            # Minus button
            pygame.draw.rect(screen, BUTTON_HOVER_COLOR if minus_r.collidepoint(mouse_pos) else BUTTON_COLOR, minus_r, border_radius=6)
            draw_text("-", FONT_MEDIUM, WHITE, minus_r.centerx, minus_r.centery, screen)
            
            # Bar background & Fill
            pygame.draw.rect(screen, DARK_GRAY, bar_r, border_radius=6)
            fill_w = int(bar_r.width * cur_val)
            if fill_w > 0:
                bar_color = CYAN if "master" in vkey else (YELLOW if "sfx" in vkey else MAGENTA)
                pygame.draw.rect(screen, bar_color, (bar_r.x, bar_r.y, fill_w, bar_r.height), border_radius=6)
            draw_text(f"{int(cur_val * 100)}%", FONT_SMALL, WHITE, bar_r.centerx, bar_r.centery, screen)
            
            # Plus button
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
        
        # Draw SFX Test Section
        draw_text("─── Test Sound Effects ───", FONT_SMALL, YELLOW, center_x, sfx_btn_rects[0][0].top - 18, screen)
        for r, label, _ in sfx_btn_rects:
            c = BUTTON_HOVER_COLOR if r.collidepoint(mouse_pos) else (50, 60, 90)
            pygame.draw.rect(screen, c, r, border_radius=6)
            draw_text(label, FONT_SMALL, WHITE, r.centerx, r.centery, screen)
            
        # Draw Music Test Section
        draw_text("─── Switch Music Soundtrack ───", FONT_SMALL, MAGENTA, center_x, music_btn_rects[0][0].top - 18, screen)
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