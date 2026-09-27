import pygame
import json
import os
import random
import urllib.request
import urllib.parse
from settings import *
import state
from sprites import Player, Asteroid, Boss, SpinoffDrone, Explosion, PowerUp
from autopilot import AdvancedAutoPilot
import ui
import megahack
import sound_manager

def process_active_hacks(players_dict, all_sprites, asteroids, enemies, powerups, bosses):
    """Processes dynamic hack effects inside gameplay loops."""
    if state.ACTIVE_HACKS.get("Spawn Asteroid"):
        if asteroids is not None:
            ast = Asteroid(1)
            all_sprites.add(ast)
            asteroids.add(ast)
        state.ACTIVE_HACKS["Spawn Asteroid"] = False
        
    if state.ACTIVE_HACKS.get("Spawn Boss") or state.ACTIVE_HACKS.get("Spawn Drone"):
        if enemies is not None:
            drone = SpinoffDrone()
            drone.rect.center = (SCREEN_WIDTH // 2, 100)
            all_sprites.add(drone)
            enemies.add(drone)
        state.ACTIVE_HACKS["Spawn Boss"] = False
        state.ACTIVE_HACKS["Spawn Drone"] = False
        
    if state.ACTIVE_HACKS.get("Clear Screen"):
        for s in list(all_sprites):
            if not isinstance(s, Player): 
                s.kill()
        state.ACTIVE_HACKS["Clear Screen"] = False
        
    if state.ACTIVE_HACKS.get("Shield Burst") or state.ACTIVE_HACKS.get("Full Heal"):
        for p in players_dict.values():
            p.activate_shield()
            p.shield_health = 999 if state.ACTIVE_HACKS.get("Shield Burst") else 3
        state.ACTIVE_HACKS["Shield Burst"] = False
        state.ACTIVE_HACKS["Full Heal"] = False

def playtest_level(screen, grid_data, grid_w, grid_h, cell_size):
    sound_manager.play_music("battle_theme")
    clock = pygame.time.Clock()
    
    temp_cheat = state.CHEAT_MENU_VISIBLE
    state.CHEAT_MENU_VISIBLE = False

    player = Player(player_id=1, ship_type_key=state.all_player_data["P1"]["selected_ship"])
    player.rect.centerx = SCREEN_WIDTH // 2
    player.rect.bottom = SCREEN_HEIGHT - 50

    all_sprites = pygame.sprite.Group()
    player_bullets = pygame.sprite.Group()
    enemy_bullets = pygame.sprite.Group()
    asteroids = pygame.sprite.Group()
    drones = pygame.sprite.Group()
    powerups = pygame.sprite.Group()
    bosses = pygame.sprite.Group()
    barriers = pygame.sprite.Group()
    
    all_sprites.add(player)

    virtual_y = grid_h * cell_size
    scroll_speed = 3
    spawned_rows = set()
    
    running = True
    test_message = "TESTING MODE - PRESS ESC TO ABORT"
    msg_color = YELLOW

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: 
                return
            if megahack.handle_event(event): 
                continue
            
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
                state.ACTIVE_HACKS["Auto Pilot"] = not state.ACTIVE_HACKS.get("Auto Pilot", False)
                
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: 
                    return 
                if event.key == pygame.K_p: 
                    state.ACTIVE_HACKS["Auto Pilot"] = not state.ACTIVE_HACKS.get("Auto Pilot", False)
                if event.key == pygame.K_SPACE and not state.CHEAT_MENU_VISIBLE: 
                    player.shoot(all_sprites, player_bullets)

        if state.ACTIVE_HACKS.get("Auto Pilot", False):
            boss_obj = bosses.sprites()[0] if bosses else None
            AdvancedAutoPilot.run(player, all_sprites, player_bullets, asteroids=asteroids, drones=drones, powerups=powerups, enemy_bullets=enemy_bullets, boss=boss_obj)
        else:
            keys = pygame.key.get_pressed()
            player.speed_x = player.base_speed if keys[pygame.K_d] else -player.base_speed if keys[pygame.K_a] else 0
            player.speed_y = player.base_speed if keys[pygame.K_s] else -player.base_speed if keys[pygame.K_w] else 0

        process_active_hacks({1: player}, all_sprites, asteroids, drones, powerups, bosses)
        all_sprites.update()

        virtual_y -= scroll_speed
        current_row = int(virtual_y // cell_size)

        if current_row not in spawned_rows and 0 <= current_row < grid_h:
            spawned_rows.add(current_row)
            offset_x = SCREEN_WIDTH // 2 - (grid_w * cell_size) // 2
            for col in range(grid_w):
                val = grid_data[current_row][col]
                sx = offset_x + (col * cell_size) + (cell_size // 2)
                sy = -50
                
                if val == 1: 
                    ast = Asteroid(1.5); ast.rect.center = (sx, sy); all_sprites.add(ast); asteroids.add(ast)
                elif val == 2: 
                    drone = SpinoffDrone(); drone.rect.center = (sx, sy); all_sprites.add(drone); drones.add(drone)
                elif val == 3: 
                    pu = PowerUp((sx, sy), random.choice(["triple_shot", "shield"])); all_sprites.add(pu); powerups.add(pu)
                elif val == 4: 
                    boss = Boss(800, ORANGE); boss.rect.center = (SCREEN_WIDTH // 2, sy); all_sprites.add(boss); bosses.add(boss)
                elif val == 5:
                    barr = Asteroid(0.8); barr.color = CYAN; barr.rect.center = (sx, sy); all_sprites.add(barr); barriers.add(barr)
                elif val == 6:
                    pu = PowerUp((sx, sy), "coins"); all_sprites.add(pu); powerups.add(pu)
                elif val == 7:
                    pu = PowerUp((sx, sy), "speed_boost"); all_sprites.add(pu); powerups.add(pu)

        for b in bosses: 
            b.shoot(all_sprites, enemy_bullets, fire_rate=400)
        for d in drones: 
            d.shoot(all_sprites, enemy_bullets)

        for b in list(player_bullets):
            for ast in pygame.sprite.spritecollide(b, asteroids, True): 
                b.kill(); all_sprites.add(Explosion(ast.rect.center))
            for barr in pygame.sprite.spritecollide(b, barriers, True):
                b.kill(); all_sprites.add(Explosion(barr.rect.center))
            for drn in pygame.sprite.spritecollide(b, drones, True): 
                b.kill(); all_sprites.add(Explosion(drn.rect.center))
            for bss in bosses:
                if pygame.sprite.collide_rect(b, bss):
                    b.kill()
                    bss.health -= 15
                    if bss.health <= 0: 
                        bss.kill(); all_sprites.add(Explosion(bss.rect.center))

        for pu in pygame.sprite.spritecollide(player, powerups, True):
            if pu.power_type == "triple_shot": 
                player.activate_triple_shot()
            elif pu.power_type == "shield": 
                player.activate_shield()
            elif pu.power_type == "coins": 
                state.all_player_data["P1"]["credits"] += 250
                state.save_game_progress()
                sound_manager.play_sfx("powerup_collect")
            elif pu.power_type == "speed_boost":
                player.base_speed = int(player.base_speed * 1.5)
                sound_manager.play_sfx("level_up")

        if pygame.sprite.spritecollide(player, asteroids, True) or pygame.sprite.spritecollide(player, barriers, True) or pygame.sprite.spritecollide(player, drones, True) or pygame.sprite.spritecollide(player, enemy_bullets, True):
            if not player.take_hit(): 
                all_sprites.add(Explosion(player.rect.center, size="medium")); player.kill()
                test_message = "TEST FAILED! (Press ESC)"
                msg_color = RED
                scroll_speed = 0
                sound_manager.play_sfx("game_over", 0.8)

        if virtual_y <= 0 and len(bosses) == 0 and len(drones) == 0 and len(asteroids) == 0: 
            test_message = "TEST PASSED! (Press ESC)"
            msg_color = WIN_GREEN
            scroll_speed = 0
            sound_manager.play_sfx("victory", 0.9)

        screen.fill((15, 15, 25))
        ui.draw_stars(screen)

        for sprite in all_sprites:
            if isinstance(sprite, Player): 
                sprite.draw(screen)
            else: 
                screen.blit(sprite.image, sprite.rect)
                
            if state.ACTIVE_HACKS.get("Show Hitboxes", False):
                pygame.draw.rect(screen, RED, sprite.rect, 2)
                pygame.draw.circle(screen, YELLOW, sprite.rect.center, 3)

        ui.draw_text(test_message, FONT_MEDIUM, msg_color, SCREEN_WIDTH // 2, 40, screen)
        megahack.draw(screen)
        
        pygame.display.flip()
        clock.tick(int(FPS * state.GAME_SPEED))

    state.CHEAT_MENU_VISIBLE = temp_cheat
    sound_manager.play_music("menu_theme")

def browse_web_levels(screen):
    clock = pygame.time.Clock()
    search_query = ""
    results = []
    status_msg = "Type to search and press ENTER"
    
    def fetch_search(q):
        try:
            url = f"{CLOUD_LEVEL_SERVER}/search?q={urllib.parse.quote(q)}"
            with urllib.request.urlopen(url, timeout=3) as resp:
                return json.loads(resp.read().decode())
        except Exception:
            return None

    results = fetch_search("") or []
    
    back_btn = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 60, 200, 50)
    scroll_offset = 0

    while True:
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return None
                elif event.key == pygame.K_RETURN:
                    res = fetch_search(search_query)
                    if res is not None:
                        results = res
                        status_msg = f"Found {len(results)} levels"
                    else:
                        status_msg = "Search failed (Server Offline?)"
                    scroll_offset = 0
                elif event.key == pygame.K_BACKSPACE:
                    search_query = search_query[:-1]
                elif event.unicode.isprintable():
                    search_query += event.unicode
                    
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if back_btn.collidepoint(mouse_pos):
                        return None
                    
                    for i, r in enumerate(results):
                        item_rect = pygame.Rect(SCREEN_WIDTH // 2 - 300, 150 + i * 60 + scroll_offset, 600, 50)
                        if item_rect.collidepoint(mouse_pos):
                            try:
                                url = f"{CLOUD_LEVEL_SERVER}/download/{r['id']}"
                                with urllib.request.urlopen(url, timeout=3) as resp:
                                    data = json.loads(resp.read().decode())
                                    return data.get("custom_waves")
                            except Exception:
                                status_msg = "Failed to download!"
                elif event.button == 4:
                    scroll_offset = min(scroll_offset + 40, 0)
                elif event.button == 5:
                    scroll_offset -= 40

        screen.fill(BLACK)
        ui.draw_stars(screen)
        ui.draw_text("WEB LEVEL BROWSER", FONT_LARGE, CYAN, SCREEN_WIDTH // 2, 50, screen, drop_shadow=True)
        ui.draw_text(f"Search: {search_query}_", FONT_MEDIUM, YELLOW, SCREEN_WIDTH // 2, 100, screen)
        ui.draw_text(status_msg, FONT_SMALL, LIGHT_GRAY, SCREEN_WIDTH // 2, 130, screen)
        
        for i, r in enumerate(results):
            y_pos = 150 + i * 60 + scroll_offset
            if y_pos > 100 and y_pos < SCREEN_HEIGHT - 80:
                item_rect = pygame.Rect(SCREEN_WIDTH // 2 - 300, y_pos, 600, 50)
                is_hover = item_rect.collidepoint(mouse_pos)
                pygame.draw.rect(screen, (100, 150, 255) if is_hover else BUTTON_COLOR, item_rect, border_radius=8)
                ui.draw_text(f"{r['name']} (ID: {r['id']})", FONT_MEDIUM, WHITE, item_rect.centerx, item_rect.centery, screen)
                
        pygame.draw.rect(screen, BUTTON_HOVER_COLOR if back_btn.collidepoint(mouse_pos) else BUTTON_COLOR, back_btn, border_radius=10)
        ui.draw_text("BACK", FONT_MEDIUM, WHITE, back_btn.centerx, back_btn.centery, screen)
        
        pygame.display.flip()
        clock.tick(FPS)

def run_level_editor(screen):
    clock = pygame.time.Clock()
    pygame.display.set_caption("Galactic Defender - Level Architect Studio")
    
    cell_size = 50
    grid_w = 14
    grid_h = 200 
    offset_x = SCREEN_WIDTH // 2 - (grid_w * cell_size) // 2
    
    grid = [[0 for _ in range(grid_w)] for _ in range(grid_h)]
    current_tool = 1
    show_gridlines = True
    camera_y = (grid_h * cell_size) - SCREEN_HEIGHT + 150 
    
    tools = [
        {"id": 1, "name": "Asteroid", "color": LIGHT_GRAY}, 
        {"id": 2, "name": "Drone", "color": RED},
        {"id": 3, "name": "Powerup", "color": MAGENTA}, 
        {"id": 4, "name": "Boss", "color": ORANGE},
        {"id": 5, "name": "Barrier", "color": CYAN},
        {"id": 6, "name": "Coins", "color": YELLOW},
        {"id": 7, "name": "SpeedPad", "color": WIN_GREEN},
        {"id": 0, "name": "Eraser", "color": DARK_GRAY}
    ]

    top_panel = pygame.Rect(0, 0, SCREEN_WIDTH, 45)
    ui_panel = pygame.Rect(0, SCREEN_HEIGHT - 150, SCREEN_WIDTH, 150)
    
    exit_btn = pygame.Rect(15, SCREEN_HEIGHT - 135, 90, 120)
    
    play_btn = pygame.Rect(SCREEN_WIDTH - 360, SCREEN_HEIGHT - 95, 160, 80)
    save_btn = pygame.Rect(SCREEN_WIDTH - 185, SCREEN_HEIGHT - 95, 170, 36)
    load_btn = pygame.Rect(SCREEN_WIDTH - 185, SCREEN_HEIGHT - 52, 80, 36)
    clear_btn = pygame.Rect(SCREEN_WIDTH - 95, SCREEN_HEIGHT - 52, 80, 36)
    
    publish_btn = pygame.Rect(SCREEN_WIDTH - 360, SCREEN_HEIGHT - 140, 160, 36)
    browse_btn = pygame.Rect(SCREEN_WIDTH - 185, SCREEN_HEIGHT - 140, 170, 36)
    
    msg, msg_timer = "", 0

    tool_w = 72
    tool_h = 70
    tool_gap = 6
    tool_start_x = 115

    max_camera_y = (grid_h * cell_size) - SCREEN_HEIGHT + 150

    while True:
        mouse_pos = pygame.mouse.get_pos()
        mouse_click = pygame.mouse.get_pressed()

        # Calculate statistics
        total_placed = sum(val != 0 for row in grid for val in row)
        ast_cnt = sum(val == 1 for row in grid for val in row)
        drone_cnt = sum(val == 2 for row in grid for val in row)
        boss_cnt = sum(val == 4 for row in grid for val in row)

        for event in pygame.event.get():
            if event.type == pygame.QUIT: 
                return
            if megahack.handle_event(event): 
                continue
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: 
                    sound_manager.play_sfx("ui_click")
                    return
                if event.key in [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5, pygame.K_6, pygame.K_7]:
                    current_tool = int(event.unicode)
                    sound_manager.play_sfx("ui_hover")
                if event.key == pygame.K_0: 
                    current_tool = 0
                    sound_manager.play_sfx("ui_hover")
                if event.key == pygame.K_g:
                    show_gridlines = not show_gridlines
                    sound_manager.play_sfx("ui_click")
                if event.key == pygame.K_c:
                    grid = [[0 for _ in range(grid_w)] for _ in range(grid_h)]
                    msg, msg_timer = "GRID CLEARED!", pygame.time.get_ticks()
                    sound_manager.play_sfx("hack_toggle")
            
            if event.type == pygame.MOUSEWHEEL:
                camera_y = max(0, min(camera_y - event.y * cell_size, max_camera_y))
            
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if exit_btn.collidepoint(mouse_pos): 
                    sound_manager.play_sfx("ui_click")
                    return
                if play_btn.collidepoint(mouse_pos): 
                    sound_manager.play_sfx("ui_click")
                    playtest_level(screen, grid, grid_w, grid_h, cell_size)
                    
                if save_btn.collidepoint(mouse_pos):
                    try:
                        with open(os.path.join(BASE_DIR, "custom_level.json"), "w") as f: 
                            json.dump({"custom_waves": grid}, f)
                        msg, msg_timer = "SAVED LEVEL!", pygame.time.get_ticks()
                        sound_manager.play_sfx("hack_toggle")
                    except Exception: 
                        msg, msg_timer = "SAVE FAILED", pygame.time.get_ticks()
                        sound_manager.play_sfx("game_over", 0.4)
                        
                if load_btn.collidepoint(mouse_pos):
                    try:
                        with open(os.path.join(BASE_DIR, "custom_level.json"), "r") as f:
                            d = json.load(f).get("custom_waves", [])
                            for r in range(min(grid_h, len(d))):
                                for c in range(min(grid_w, len(d[r]))): 
                                    grid[r][c] = d[r][c]
                        msg, msg_timer = "LOADED LEVEL!", pygame.time.get_ticks()
                        sound_manager.play_sfx("hack_toggle")
                    except Exception: 
                        msg, msg_timer = "NO SAVE FOUND", pygame.time.get_ticks()
                        sound_manager.play_sfx("game_over", 0.4)

                if publish_btn.collidepoint(mouse_pos):
                    try:
                        author = state.current_user if getattr(state, 'current_user', None) else "Anonymous"
                        level_data = {"custom_waves": grid, "name": f"{author}'s Level"}
                        req = urllib.request.Request(f"{CLOUD_LEVEL_SERVER}/publish", data=json.dumps(level_data).encode(), headers={'Content-Type': 'application/json'})
                        with urllib.request.urlopen(req, timeout=3) as response:
                            res = json.loads(response.read().decode())
                            msg, msg_timer = f"PUBLISHED! (ID: {res.get('id', '???')})", pygame.time.get_ticks()
                            sound_manager.play_sfx("hack_toggle")
                    except Exception as e:
                        msg, msg_timer = "PUBLISH FAILED (Server offline?)", pygame.time.get_ticks()
                        sound_manager.play_sfx("game_over", 0.4)
                        
                if browse_btn.collidepoint(mouse_pos):
                    downloaded_grid = browse_web_levels(screen)
                    if downloaded_grid:
                        # Copy downloaded grid over the current one
                        for r in range(min(grid_h, len(downloaded_grid))):
                            for c in range(min(grid_w, len(downloaded_grid[r]))): 
                                grid[r][c] = downloaded_grid[r][c]
                        msg, msg_timer = "LOADED FROM WEB!", pygame.time.get_ticks()
                        sound_manager.play_sfx("hack_toggle")
                    pygame.display.set_caption("Galactic Defender - Level Architect Studio")

                if clear_btn.collidepoint(mouse_pos):
                    grid = [[0 for _ in range(grid_w)] for _ in range(grid_h)]
                    msg, msg_timer = "GRID CLEARED!", pygame.time.get_ticks()
                    sound_manager.play_sfx("hack_toggle")

                # Minimap scrollbar track click navigation
                track_x = offset_x + grid_w * cell_size + 15
                track_rect = pygame.Rect(track_x, 55, 20, SCREEN_HEIGHT - 175)
                if track_rect.collidepoint(mouse_pos):
                    rel_y = (mouse_pos[1] - track_rect.y) / track_rect.height
                    camera_y = max(0, min(int(rel_y * max_camera_y), max_camera_y))

                for i, t in enumerate(tools):
                    tr = pygame.Rect(tool_start_x + (i * (tool_w + tool_gap)), SCREEN_HEIGHT - 130, tool_w, tool_h)
                    if tr.collidepoint(mouse_pos): 
                        current_tool = t["id"]
                        sound_manager.play_sfx("ui_click")

        # Smooth drag-painting
        if (mouse_click[0] or mouse_click[2]) and not ui_panel.collidepoint(mouse_pos) and not top_panel.collidepoint(mouse_pos) and not state.CHEAT_MENU_VISIBLE:
            gx = (mouse_pos[0] - offset_x) // cell_size
            gy = (mouse_pos[1] + camera_y) // cell_size
            if 0 <= gx < grid_w and 0 <= gy < grid_h: 
                grid[gy][gx] = 0 if mouse_click[2] else current_tool

        screen.fill((10, 15, 25))
        
        # Grid rendering
        for row in range(grid_h):
            y_pos = (row * cell_size) - camera_y
            if -cell_size <= y_pos <= SCREEN_HEIGHT:
                if row % 10 == 0: 
                    ui.draw_text(f"R{row}", FONT_SMALL, (100, 100, 100), offset_x - 30, y_pos + cell_size//2, screen)
                
                for col in range(grid_w):
                    r = pygame.Rect(offset_x + col * cell_size, y_pos, cell_size, cell_size)
                    if show_gridlines:
                        pygame.draw.rect(screen, (30, 35, 45), r, 1)
                    
                    val = grid[row][col]
                    if val == 1: 
                        pygame.draw.circle(screen, LIGHT_GRAY, r.center, cell_size//3)
                    elif val == 2: 
                        pygame.draw.polygon(screen, RED, [(r.centerx, r.top+10), (r.left+10, r.bottom-10), (r.right-10, r.bottom-10)])
                    elif val == 3: 
                        pygame.draw.rect(screen, MAGENTA, (r.centerx-10, r.centery-10, 20, 20))
                    elif val == 4: 
                        pygame.draw.rect(screen, ORANGE, (r.left+5, r.top+5, cell_size-10, cell_size-10))
                    elif val == 5:
                        pygame.draw.rect(screen, CYAN, r.inflate(-8, -8), border_radius=4)
                    elif val == 6:
                        pygame.draw.circle(screen, YELLOW, r.center, cell_size//4)
                        pygame.draw.circle(screen, (200, 180, 0), r.center, cell_size//6)
                    elif val == 7:
                        pygame.draw.polygon(screen, WIN_GREEN, [(r.centerx, r.top+12), (r.right-12, r.bottom-12), (r.left+12, r.bottom-12)])

        # Minimap Scrollbar
        track_x = offset_x + grid_w * cell_size + 15
        track_rect = pygame.Rect(track_x, 55, 18, SCREEN_HEIGHT - 175)
        pygame.draw.rect(screen, (20, 25, 35), track_rect, border_radius=6)
        pygame.draw.rect(screen, (40, 50, 70), track_rect, 1, border_radius=6)
        
        thumb_height = max(20, int((SCREEN_HEIGHT / (grid_h * cell_size)) * track_rect.height))
        thumb_y = track_rect.y + (camera_y / max_camera_y) * (track_rect.height - thumb_height)
        thumb_rect = pygame.Rect(track_x + 2, thumb_y, 14, thumb_height)
        pygame.draw.rect(screen, CYAN, thumb_rect, border_radius=4)

        # Top Bar (Metrics HUD)
        pygame.draw.rect(screen, (15, 22, 35), top_panel)
        pygame.draw.line(screen, (50, 80, 120), (0, top_panel.bottom), (SCREEN_WIDTH, top_panel.bottom), 2)
        cur_row = int(camera_y // cell_size)
        ui.draw_text(f"LEVEL ARCHITECT STUDIO  |  OBJECTS: {total_placed}  (Asteroids: {ast_cnt}, Drones: {drone_cnt}, Bosses: {boss_cnt})  |  VIEW: Row {cur_row}/{grid_h}", FONT_SMALL, CYAN, SCREEN_WIDTH // 2, top_panel.centery, screen)

        # Bottom UI
        pygame.draw.rect(screen, (20, 20, 30), ui_panel)
        pygame.draw.line(screen, CYAN, (0, ui_panel.top), (SCREEN_WIDTH, ui_panel.top), 2)
        
        pygame.draw.rect(screen, (150, 0, 0), exit_btn, border_radius=8)
        ui.draw_text("EXIT", FONT_MEDIUM, WHITE, exit_btn.centerx, exit_btn.centery, screen)
        
        pygame.draw.rect(screen, WIN_GREEN, play_btn, border_radius=8)
        ui.draw_text("▶ TEST", FONT_LARGE, BLACK, play_btn.centerx, play_btn.centery, screen)
        
        pygame.draw.rect(screen, BUTTON_COLOR, save_btn, border_radius=5)
        ui.draw_text("SAVE LOCAL", FONT_SMALL, WHITE, save_btn.centerx, save_btn.centery, screen)
        
        pygame.draw.rect(screen, BUTTON_COLOR, load_btn, border_radius=5)
        ui.draw_text("LOAD", FONT_SMALL, WHITE, load_btn.centerx, load_btn.centery, screen)

        pygame.draw.rect(screen, (120, 40, 40), clear_btn, border_radius=5)
        ui.draw_text("CLEAR", FONT_SMALL, WHITE, clear_btn.centerx, clear_btn.centery, screen)
        
        pygame.draw.rect(screen, (100, 50, 150), publish_btn, border_radius=5)
        ui.draw_text("☁ PUBLISH", FONT_SMALL, WHITE, publish_btn.centerx, publish_btn.centery, screen)
        
        pygame.draw.rect(screen, (0, 100, 150), browse_btn, border_radius=5)
        ui.draw_text("☁ BROWSE WEB", FONT_SMALL, WHITE, browse_btn.centerx, browse_btn.centery, screen)

        for i, t in enumerate(tools):
            tr = pygame.Rect(tool_start_x + (i * (tool_w + tool_gap)), SCREEN_HEIGHT - 130, tool_w, tool_h)
            is_active = (current_tool == t["id"])
            col = t["color"] if is_active else (t["color"][0]//3, t["color"][1]//3, t["color"][2]//3)
            pygame.draw.rect(screen, col, tr, border_radius=6)
            pygame.draw.rect(screen, WHITE if is_active else (60, 70, 90), tr, 2 if is_active else 1, border_radius=6)
            ui.draw_text(t["name"], FONT_SMALL, WHITE, tr.centerx, tr.centery, screen)

        if msg and pygame.time.get_ticks() - msg_timer < 2500: 
            ui.draw_text(msg, FONT_SMALL, WIN_GREEN if "!" in msg else RED, save_btn.centerx, save_btn.top - 12, screen)
            
        megahack.draw(screen)
        pygame.display.flip()
        clock.tick(int(FPS * state.GAME_SPEED))