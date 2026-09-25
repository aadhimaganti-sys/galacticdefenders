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
    
    current_user_display = state.current_user if state.current_user else "Guest (P1)"
    is_adm = state.current_user and account.is_admin(state.current_user)
    is_p = state.current_user and account.is_primary_admin(state.current_user)
    admin_tag = " [PRIMARY ADMIN]" if is_p else (" [ADMIN]" if is_adm else "")
    
    card_w = 320
    card_h = 490
    card_gap = 25
    
    center_x = SCREEN_WIDTH // 2
    total_w = 3 * card_w + 2 * card_gap
    start_x = center_x - total_w // 2
    y_cards = 150

    card1_x = start_x
    card2_x = start_x + card_w + card_gap
    card3_x = start_x + 2 * (card_w + card_gap)

    card1_options = [
        {"text": "Single Player (Classic)", "action": "PLAYING_SINGLE_CLASSIC", "color": (30, 80, 140)},
        {"text": "Single Player (Boss Mode)", "action": "PLAYING_SINGLE_BOSS", "color": (140, 40, 60)},
        {"text": "Local Co-op (Classic)", "action": "PLAYING_MULTI_CLASSIC", "color": (40, 100, 120)},
        {"text": "Local Co-op (Boss Mode)", "action": "PLAYING_MULTI_BOSS", "color": (120, 40, 90)},
        {"text": "⚙️ Engine Room", "action": "ENGINE_ROOM", "color": (150, 100, 20)},
        {"text": "📖 STORY CAMPAIGN", "action": "PLAYING_SPINOFF", "color": (180, 0, 80)},
        {"text": "🔒 SECRET PROTOCOL", "action": "PASSWORD_SCREEN", "color": (100, 0, 0)},
    ]

    card2_options = [
        {"text": "Host LAN Game", "action": "HOST_LAN_MENU", "color": (40, 90, 130)},
        {"text": "Join LAN Game", "action": "JOIN_LAN_MENU", "color": (40, 90, 130)},
        {"text": "Host GLOBAL Cloud", "action": "HOST_CLOUD", "color": (100, 0, 150)},
        {"text": "Join GLOBAL Cloud", "action": "JOIN_CLOUD", "color": (100, 0, 150)},
        {"text": "Galactic Web Browser", "action": "WEB_BROWSER", "color": (0, 100, 100)},
    ]

    card3_options = [
        {"text": "Store / Armory (P1)", "action": "STORE_P1", "color": (60, 110, 50)},
        {"text": "Select Ship (P1)", "action": "SELECT_SHIP_P1", "color": (70, 90, 120)},
        {"text": "🔊 Audio Settings", "action": "AUDIO_SETTINGS", "color": (30, 80, 140)},
        {"text": "Datapack Mod Loader", "action": "MOD_LOADER", "color": (110, 60, 120)},
        {"text": "GUI Level Architect", "action": "LEVEL_EDITOR", "color": (0, 120, 60)},
        {"text": "Quit Game", "action": "QUIT_PROGRAM", "color": (120, 30, 30)},
    ]

    btn_w = card_w - 30
    btn_h = 44
    pad_y = 10

    for i, opt in enumerate(card1_options):
        opt["rect"] = pygame.Rect(card1_x + 15, y_cards + 55 + i * (btn_h + pad_y), btn_w, btn_h)

    for i, opt in enumerate(card2_options):
        opt["rect"] = pygame.Rect(card2_x + 15, y_cards + 55 + i * (btn_h + pad_y + 8), btn_w, btn_h)

    for i, opt in enumerate(card3_options):
        opt["rect"] = pygame.Rect(card3_x + 15, y_cards + 55 + i * (btn_h + pad_y + 4), btn_w, btn_h)

    all_buttons = card1_options + card2_options + card3_options

    header_account_btn = pygame.Rect(center_x + total_w // 2 - 230, 92, 110, 30)
    header_admin_btn = pygame.Rect(center_x + total_w // 2 - 110, 92, 100, 30)

    while True:
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT: 
                return "QUIT_PROGRAM"
            if megahack.handle_event(event): 
                continue
            
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if header_account_btn.collidepoint(mouse_pos):
                    sound_manager.play_sfx("ui_click")
                    return "ACCOUNT_SCREEN"
                elif header_admin_btn.collidepoint(mouse_pos):
                    sound_manager.play_sfx("ui_click")
                    return "ADMIN_PANEL"
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
        
        # Pulsating Title Glow
        pulse = (math.sin(pygame.time.get_ticks() * 0.003) + 1.0) / 2.0
        glow_cyan = (int(0 + pulse * 50), int(200 + pulse * 55), 255)
        
        draw_text("GALACTIC DEFENDERS", FONT_XLARGE, (0, 80, 140), center_x + 2, 47, screen)
        draw_text("GALACTIC DEFENDERS", FONT_XLARGE, glow_cyan, center_x, 45, screen)

        # Top Navigation Bar Card
        bar_w = total_w
        bar_rect = pygame.Rect(center_x - bar_w // 2, 85, bar_w, 44)
        pygame.draw.rect(screen, (18, 24, 40), bar_rect, border_radius=12)
        pygame.draw.rect(screen, (50, 80, 130), bar_rect, 2, border_radius=12)
        
        user_col = YELLOW if is_p else (CYAN if is_adm else WHITE)
        draw_text(f"PILOT: {current_user_display}{admin_tag}", FONT_SMALL, user_col, bar_rect.x + 15, bar_rect.centery, screen, align="left")
        draw_text(f"CREDITS: {credits_p1} Cr   |   SHIP: {selected_p1}", FONT_SMALL, LIGHT_GRAY, center_x - 40, bar_rect.centery, screen, align="center")

        h_acc = header_account_btn.collidepoint(mouse_pos)
        pygame.draw.rect(screen, BUTTON_HOVER_COLOR if h_acc else (30, 60, 100), header_account_btn, border_radius=8)
        pygame.draw.rect(screen, CYAN if h_acc else (60, 90, 130), header_account_btn, 1, border_radius=8)
        draw_text("👤 Account", FONT_SMALL, WHITE, header_account_btn.centerx, header_account_btn.centery, screen)

        h_adm = header_admin_btn.collidepoint(mouse_pos)
        pygame.draw.rect(screen, (140, 40, 40) if h_adm else (100, 30, 30), header_admin_btn, border_radius=8)
        pygame.draw.rect(screen, RED if h_adm else (140, 60, 60), header_admin_btn, 1, border_radius=8)
        draw_text("⚙️ Admin", FONT_SMALL, WHITE, header_admin_btn.centerx, header_admin_btn.centery, screen)

        cards_info = [
            {"x": card1_x, "title": "🚀 MISSION SELECT", "color": (0, 180, 220), "options": card1_options},
            {"x": card2_x, "title": "🌐 MULTIPLAYER & CLOUD", "color": (160, 80, 220), "options": card2_options},
            {"x": card3_x, "title": "🛸 HANGAR & SYSTEM", "color": (60, 200, 120), "options": card3_options},
        ]

        for c_info in cards_info:
            c_rect = pygame.Rect(c_info["x"], y_cards, card_w, card_h)
            pygame.draw.rect(screen, (14, 18, 30), c_rect, border_radius=12)
            pygame.draw.rect(screen, (40, 60, 90), c_rect, 2, border_radius=12)

            header_rect = pygame.Rect(c_info["x"] + 10, y_cards + 10, card_w - 20, 34)
            pygame.draw.rect(screen, (22, 32, 50), header_rect, border_radius=8)
            draw_text(c_info["title"], FONT_SMALL, c_info["color"], header_rect.centerx, header_rect.centery, screen)

            for opt in c_info["options"]:
                is_hover = opt["rect"].collidepoint(mouse_pos)
                b_rect = opt["rect"].copy()
                if is_hover:
                    b_rect.inflate_ip(4, 2)
                
                base_col = opt.get("color", BUTTON_COLOR)
                c_fill = BUTTON_HOVER_COLOR if is_hover else base_col
                c_border = (0, 220, 255) if is_hover else (60, 75, 100)
                
                pygame.draw.rect(screen, c_fill, b_rect, border_radius=8)
                pygame.draw.rect(screen, c_border, b_rect, 2 if is_hover else 1, border_radius=8)
                draw_text(opt["text"], FONT_MEDIUM if len(opt["text"]) < 24 else FONT_SMALL, WHITE, b_rect.centerx, b_rect.centery, screen)

        draw_text("Press TAB for MegaHack Menu  |  F12 Admin Controls  |  ESC Quit", FONT_SMALL, (130, 140, 160), center_x, SCREEN_HEIGHT - 22, screen)

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


def show_admin_options(screen, clock):
    if not state.current_user or not account.is_admin(state.current_user):
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
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    return "HOME"

            screen.fill(BLACK)
            draw_stars(screen)
            draw_text("ACCESS RESTRICTED", FONT_LARGE, RED, center_x, SCREEN_HEIGHT // 3 - 30, screen)
            draw_text("Admin privileges required to access Admin Controls.", FONT_MEDIUM, WHITE, center_x, SCREEN_HEIGHT // 3 + 30, screen)
            draw_text("Please log in with an account that has admin rights.", FONT_SMALL, LIGHT_GRAY, center_x, SCREEN_HEIGHT // 3 + 65, screen)

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
        cli_admin_rect = pygame.Rect(rx, ry + 280, 430, 38)
        home_rect = pygame.Rect(center_x - 180, 545, 360, 42)

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

                elif cli_admin_rect.collidepoint(mouse_pos):
                    sound_manager.play_sfx("ui_click")
                    screen.fill(BLACK)
                    draw_stars(screen)
                    draw_text("CLI TERMINAL ADMIN PANEL ACTIVE", FONT_LARGE, CYAN, center_x, SCREEN_HEIGHT // 2 - 20, screen)
                    draw_text("Check your console terminal window to interact.", FONT_MEDIUM, YELLOW, center_x, SCREEN_HEIGHT // 2 + 30, screen)
                    pygame.display.flip()

                    print("\n" + "=" * 50)
                    print(" === GALACTIC DEFENDERS TERMINAL ADMIN PANEL ===")
                    print("=" * 50)
                    admin_panel.run_admin_menu()
                    pygame.event.pump()

                    status_msg = "Returned from CLI Admin Panel."
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
        list_bg = pygame.Rect(center_x - 390, 165, 280, 360)
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
        right_bg = pygame.Rect(center_x - 90, 165, 470, 360)
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

        h_cli = cli_admin_rect.collidepoint(mouse_pos)
        pygame.draw.rect(screen, (100, 40, 120) if h_cli else (70, 20, 90), cli_admin_rect, border_radius=6)
        draw_text("💻 Launch CLI Console Admin Panel (Terminal)", FONT_SMALL, WHITE, cli_admin_rect.centerx, cli_admin_rect.centery, screen)

        h_home = home_rect.collidepoint(mouse_pos)
        pygame.draw.rect(screen, BUTTON_HOVER_COLOR if h_home else (40, 50, 70), home_rect, border_radius=8)
        draw_text("⬅ Return to Main Menu", FONT_MEDIUM, WHITE, home_rect.centerx, home_rect.centery, screen)

        if status_msg and pygame.time.get_ticks() - status_time < 3500:
            draw_text(status_msg, FONT_SMALL, status_color, center_x, SCREEN_HEIGHT - 35, screen)

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