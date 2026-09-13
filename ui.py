import pygame
import random
import os
import sys
from settings import *
import state
import megahack

stars = [[random.randint(0, SCREEN_WIDTH), random.randint(0, SCREEN_HEIGHT), random.uniform(1, 4)] for _ in range(100)]

def draw_text(text, font, color, x, y, surface, align="center"):
    text_surface = font.render(text, True, color)
    rect = text_surface.get_rect()
    if align == "center":
        rect.center = (x, y)
    elif align == "left":
        rect.midleft = (x, y)
    surface.blit(text_surface, rect)

def draw_stars(surface):
    for s in stars:
        s[1] += s[2] * state.GAME_SPEED
        if s[1] > SCREEN_HEIGHT:
            s[1] = 0
            s[0] = random.randint(0, SCREEN_WIDTH)
        pygame.draw.circle(surface, WHITE if s[2] > 2.5 else LIGHT_GRAY, (int(s[0]), int(s[1])), int(s[2]))

def draw_scrollable_menu(screen, options, offset, mouse_pos, title, font_t, color_t, y_t, currency=None):
    screen.fill(BLACK)
    draw_text(title, font_t, color_t, SCREEN_WIDTH // 2, y_t, screen)
    if currency:
        draw_text(currency, FONT_MEDIUM, WHITE, SCREEN_WIDTH - 250, 40, screen)
        
    for opt in options:
        r = opt["rect"].copy()
        r.centery = opt["original_y"] + offset
        
        if r.bottom > y_t + 50 and r.top < SCREEN_HEIGHT - 120:
            color = opt.get("override_color", BUTTON_COLOR)
            if r.collidepoint(mouse_pos) and not opt.get("is_owned", False):
                color = BUTTON_HOVER_COLOR
            if opt.get("is_owned", False):
                color = BUTTON_DISABLED_COLOR
                
            pygame.draw.rect(screen, color, r, border_radius=10)
            draw_text(opt["text"], FONT_MEDIUM, WHITE, r.centerx, r.centery, screen)
            if "desc" in opt:
                draw_text(opt["desc"], FONT_SMALL, LIGHT_GRAY, r.centerx, r.centery + 20, screen)

def show_home_screen(screen, clock):
    selected_p1 = state.SHIP_TYPES.get(state.all_player_data["P1"]["selected_ship"], BASE_SHIP_TYPES["default_jet"])["name"]
    
    button_options = [
        {"text": "Single Player (Classic)", "action": "PLAYING_SINGLE_CLASSIC", "rect": None},
        {"text": "Single Player (Boss Mode)", "action": "PLAYING_SINGLE_BOSS", "rect": None},
        {"text": "Local Multiplayer", "action": "PLAYING_MULTI_CLASSIC", "rect": None},
        {"text": "Local Multiplayer (Boss Mode)", "action": "PLAYING_MULTI_BOSS", "rect": None},
        {"text": "??? PLAY STORY CAMPAIGN ???", "action": "PLAYING_SPINOFF", "rect": None, "override_color": (180, 0, 80)},
        {"text": "ENTER SECRET PROTOCOL", "action": "PASSWORD_SCREEN", "rect": None, "override_color": (100, 0, 0)},
        {"text": "Host LAN Game", "action": "HOST_LAN_MENU", "rect": None},
        {"text": "Join LAN Game", "action": "JOIN_LAN_MENU", "rect": None},
        {"text": "Host GLOBAL Cloud Game", "action": "HOST_CLOUD", "rect": None, "override_color": (100, 0, 150)},
        {"text": "Join GLOBAL Cloud Game", "action": "JOIN_CLOUD", "rect": None, "override_color": (100, 0, 150)},
        {"text": "Galactic Web Browser", "action": "WEB_BROWSER", "rect": None, "override_color": (0, 100, 100)},
        {"text": "Store / Armory (P1)", "action": "STORE_P1", "rect": None},
        {"text": "Select Ship (P1)", "action": "SELECT_SHIP_P1", "rect": None},
        {"text": "Datapack Mod Loader", "action": "MOD_LOADER", "rect": None},
        {"text": "GUI Level Architect", "action": "LEVEL_EDITOR", "rect": None, "override_color": (0, 120, 60)},
        {"text": "Quit Game", "action": "QUIT_PROGRAM", "rect": None},
    ]

    button_w, button_h, pad = 340, 35, 6
    y_start = SCREEN_HEIGHT // 2 - (len(button_options) * (button_h + pad)) // 2 + 30

    for i, opt in enumerate(button_options): 
        opt["rect"] = pygame.Rect(SCREEN_WIDTH // 2 - button_w // 2, y_start + i * (button_h + pad), button_w, button_h)

    while True:
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT: return "QUIT_PROGRAM"
            if megahack.handle_event(event): continue
            
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for opt in button_options:
                    if opt["rect"].collidepoint(mouse_pos): return opt["action"]
            if event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_q, pygame.K_ESCAPE]: return "QUIT_PROGRAM"
                if event.key in [pygame.K_BACKQUOTE, pygame.K_F12]: return "ADMIN_PANEL"

        screen.fill(BLACK)
        draw_stars(screen)
        
        draw_text("GALACTIC DEFENDER", FONT_XLARGE, CYAN, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4 - 60, screen)
        draw_text(f"P1 Credits: {state.all_player_data['P1']['credits']} | Ship: {selected_p1}", FONT_MEDIUM, YELLOW, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4 + 20, screen)
        
        for opt in button_options:
            c = BUTTON_HOVER_COLOR if opt["rect"].collidepoint(mouse_pos) else opt.get("override_color", BUTTON_COLOR)
            pygame.draw.rect(screen, c, opt["rect"], border_radius=10)
            draw_text(opt["text"], FONT_MEDIUM, WHITE, opt["rect"].centerx, opt["rect"].centery, screen)

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
                    if back_btn.collidepoint(mouse_pos): return "HOME"
                elif event.button == 4: scroll_offset = min(scroll_offset + 80, 0)
                elif event.button == 5:
                    if store_items:
                        max_scroll = -((store_items[-1]["original_y"] - start_y + btn_h + 20) - (SCREEN_HEIGHT - (fixed_title_y + 120)))
                        scroll_offset = max(scroll_offset - 80, max_scroll) if max_scroll < 0 else 0
                        
            if event.type == pygame.KEYDOWN and event.key in [pygame.K_ESCAPE, pygame.K_h]: return "HOME"

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
                            return "HOME"
                    if back_btn.collidepoint(mouse_pos): return "HOME"
                elif event.button == 4: scroll_offset = min(scroll_offset + 85, 0)
                elif event.button == 5:
                    if selectable_ships:
                        max_scroll = -((selectable_ships[-1]["original_y"] - start_y + 70) - (SCREEN_HEIGHT - (fixed_title_y + 120)))
                        scroll_offset = max(scroll_offset - 85, max_scroll) if max_scroll < 0 else 0
                        
            if event.type == pygame.KEYDOWN and event.key in [pygame.K_ESCAPE, pygame.K_h]: return "HOME"

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
                    if back_btn.collidepoint(mouse_pos): return "HOME"
                elif event.button == 4: scroll_offset = min(scroll_offset + 80, 0)
                elif event.button == 5:
                    if mod_items:
                        max_scroll = -((mod_items[-1]["original_y"] - start_y + 80) - (SCREEN_HEIGHT - (fixed_title_y + 120)))
                        scroll_offset = max(scroll_offset - 80, max_scroll) if max_scroll < 0 else 0
                        
            if event.type == pygame.KEYDOWN and event.key in [pygame.K_ESCAPE, pygame.K_h]: return "HOME"

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
                if event.key == pygame.K_ESCAPE: return "HOME"
                elif event.key == pygame.K_RETURN:
                    if input_text.strip().upper() == "OMEGA": return "PLAYING_ULTIMATE_BOSS"
                    else: error_msg, error_time, input_text = "ACCESS DENIED.", pygame.time.get_ticks(), ""
                elif event.key == pygame.K_BACKSPACE: input_text = input_text[:-1]
                elif event.unicode.isprintable(): input_text += event.unicode
        
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
        
        pygame.draw.rect(screen, WHITE, (bx + 80, by + 5, browser_w - 130, 30), border_radius=4)
        draw_text(current_url, FONT_SMALL, BLACK, bx + 100 + len(current_url)*4, by + 20, screen)
        
        pygame.draw.rect(screen, RED, pygame.Rect(bx + browser_w - 40, by + 5, 30, 30), border_radius=4)
        draw_text("X", FONT_SMALL, WHITE, bx + browser_w - 25, by + 20, screen)
        
        # Page Content
        if current_url == "http://galactic.net/home":
            draw_text("GALACTIC WEB PORTAL", FONT_LARGE, CYAN, bx + browser_w//2, by + 120, screen)
            link1, link2, link3 = pygame.Rect(bx+250, by+250, 400, 50), pygame.Rect(bx+250, by+320, 400, 50), pygame.Rect(bx+250, by+390, 400, 50)
            for r, t, col in [(link1, "▶ Darknet: MegaHack v7", MAGENTA), (link2, "▶ Black Market Shipyard", ORANGE), (link3, "▶ Bounty Board", YELLOW)]:
                pygame.draw.rect(screen, (50, 50, 80), r, border_radius=8)
                draw_text(t, FONT_MEDIUM, col, r.centerx, r.centery, screen)
                
        elif current_url == "http://darknet.galactic/megahack":
            draw_text("◆ MEGAHACK RUNTIME INJECTOR ◆", FONT_LARGE, MAGENTA, bx + browser_w//2, by + 150, screen)
            dl_btn = pygame.Rect(bx+300, by+350, 300, 60)
            pygame.draw.rect(screen, BUTTON_DISABLED_COLOR, dl_btn, border_radius=10)
            draw_text("UNLOCKED BY DEFAULT - Press TAB", FONT_MEDIUM, WIN_GREEN, dl_btn.centerx, dl_btn.centery, screen)
                
        elif current_url == "http://galactic.net/shipyard":
            draw_text("BLACK MARKET SHIPYARD", FONT_LARGE, ORANGE, bx + browser_w//2, by + 150, screen)
            buy_btn = pygame.Rect(bx+250, by+300, 400, 80)
            pygame.draw.rect(screen, BUTTON_COLOR, buy_btn, border_radius=10)
            msg = "OWNED" if "shadow_wraith" in state.all_player_data["P1"]["owned_ships"] else "BUY 'SHADOW WRAITH' - 8000 Cr"
            draw_text(msg, FONT_MEDIUM, WHITE, buy_btn.centerx, buy_btn.centery, screen)
            
        elif current_url == "http://galactic.net/bounties":
            draw_text("BOUNTY BOARD", FONT_LARGE, YELLOW, bx + browser_w//2, by + 150, screen)
            draw_text("Bounties currently disabled by Galactic Police.", FONT_MEDIUM, RED, bx + browser_w//2, by + 300, screen)

        megahack.draw(screen)
        pygame.display.flip()
        clock.tick(int(FPS * state.GAME_SPEED))

def show_instructions_screen(screen, clock, mode):
    screen.fill(BLACK)
    draw_stars(screen)
    draw_text("MISSION BRIEFING", FONT_LARGE, YELLOW, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4, screen)
    draw_text("Player 1: WASD Move, SPACE Shoot", FONT_MEDIUM, WHITE, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 60, screen)
    if "MULTI" in mode or "LAN" in mode or "CLOUD" in mode:
        draw_text("Player 2: Arrows Move, ENTER Shoot", FONT_MEDIUM, WHITE, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20, screen)
    draw_text("Press any key to start.", FONT_SMALL, LIGHT_GRAY, SCREEN_WIDTH // 2, SCREEN_HEIGHT * 0.85, screen)
    pygame.display.flip()
    
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: sys.exit()
            if event.type == pygame.KEYDOWN: waiting = False
        clock.tick(FPS)

def show_game_over_screen(screen, clock, did_win_game, winner_id=0):
    screen.fill(BLACK)
    draw_stars(screen)
    draw_text("Victory!" if did_win_game else "Game Over", FONT_XLARGE, WIN_GREEN if did_win_game else LOSE_RED, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3, screen)
    draw_text(f"P1 Score: {state.score_p1}", FONT_MEDIUM, YELLOW, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20, screen)
    draw_text("Press 'H' to go Home or 'Q' to Quit", FONT_MEDIUM, WHITE, SCREEN_WIDTH // 2, SCREEN_HEIGHT * 0.85, screen)
    pygame.display.flip()
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: return "QUIT_PROGRAM"
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_h: return "HOME"
                elif event.key == pygame.K_q: return "QUIT_PROGRAM"
        clock.tick(FPS)