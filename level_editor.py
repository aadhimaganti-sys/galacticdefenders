import pygame
import json
import os
import random
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
    
    # Hide hack menu while starting test
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

        for b in bosses: 
            b.shoot(all_sprites, enemy_bullets, fire_rate=400)
        for d in drones: 
            d.shoot(all_sprites, enemy_bullets)

        for b in list(player_bullets):
            for ast in pygame.sprite.spritecollide(b, asteroids, True): 
                b.kill(); all_sprites.add(Explosion(ast.rect.center))
            for drn in pygame.sprite.spritecollide(b, drones, True): 
                b.kill(); all_sprites.add(Explosion(drn.rect.center))
            for bss in bosses:
                if pygame.sprite.collide_rect(b, bss):
                    b.kill()
                    bss.health -= 15
                    if bss.health <= 0: 
                        bss.kill(); all_sprites.add(Explosion(bss.rect.center))

        for pu in pygame.sprite.spritecollide(player, powerups, True):
            if pu.power_type == "triple_shot": player.activate_triple_shot()
            elif pu.power_type == "shield": player.activate_shield()

        if pygame.sprite.spritecollide(player, asteroids, True) or pygame.sprite.spritecollide(player, drones, True) or pygame.sprite.spritecollide(player, enemy_bullets, True):
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

def run_level_editor(screen):
    clock = pygame.time.Clock()
    pygame.display.set_caption("Galactic Defender - Level Architect Studio")
    
    cell_size = 50
    grid_w = 14
    grid_h = 200 
    offset_x = SCREEN_WIDTH // 2 - (grid_w * cell_size) // 2
    
    grid = [[0 for _ in range(grid_w)] for _ in range(grid_h)]
    current_tool = 1
    camera_y = (grid_h * cell_size) - SCREEN_HEIGHT + 150 
    
    tools = [
        {"id": 1, "name": "Asteroid", "color": LIGHT_GRAY}, 
        {"id": 2, "name": "Drone", "color": RED},
        {"id": 3, "name": "Powerup", "color": MAGENTA}, 
        {"id": 4, "name": "Boss", "color": ORANGE},
        {"id": 0, "name": "Eraser", "color": DARK_GRAY}
    ]

    ui_panel = pygame.Rect(0, SCREEN_HEIGHT - 110, SCREEN_WIDTH, 110)
    exit_btn = pygame.Rect(15, SCREEN_HEIGHT - 95, 100, 80)
    play_btn = pygame.Rect(SCREEN_WIDTH - 360, SCREEN_HEIGHT - 95, 160, 80)
    save_btn = pygame.Rect(SCREEN_WIDTH - 180, SCREEN_HEIGHT - 95, 165, 36)
    load_btn = pygame.Rect(SCREEN_WIDTH - 180, SCREEN_HEIGHT - 52, 165, 36)
    msg, msg_timer = "", 0

    tool_w = 80
    tool_h = 70
    tool_gap = 10
    tool_start_x = 130

    while True:
        mouse_pos = pygame.mouse.get_pos()
        mouse_click = pygame.mouse.get_pressed()

        for event in pygame.event.get():
            if event.type == pygame.QUIT: 
                return
            if megahack.handle_event(event): 
                continue
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: 
                    sound_manager.play_sfx("ui_click")
                    return
                if event.key == pygame.K_1: current_tool = 1; sound_manager.play_sfx("ui_hover")
                if event.key == pygame.K_2: current_tool = 2; sound_manager.play_sfx("ui_hover")
                if event.key == pygame.K_3: current_tool = 3; sound_manager.play_sfx("ui_hover")
                if event.key == pygame.K_4: current_tool = 4; sound_manager.play_sfx("ui_hover")
                if event.key == pygame.K_0: current_tool = 0; sound_manager.play_sfx("ui_hover")
            
            if event.type == pygame.MOUSEWHEEL:
                camera_y = max(0, min(camera_y - event.y * cell_size, (grid_h * cell_size) - SCREEN_HEIGHT + 150))
            
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
                        msg, msg_timer = "SAVED!", pygame.time.get_ticks()
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
                        msg, msg_timer = "LOADED!", pygame.time.get_ticks()
                        sound_manager.play_sfx("hack_toggle")
                    except Exception: 
                        msg, msg_timer = "NO SAVE FOUND", pygame.time.get_ticks()
                        sound_manager.play_sfx("game_over", 0.4)
                        
                for i, t in enumerate(tools):
                    tr = pygame.Rect(tool_start_x + (i * (tool_w + tool_gap)), SCREEN_HEIGHT - 90, tool_w, tool_h)
                    if tr.collidepoint(mouse_pos): 
                        current_tool = t["id"]
                        sound_manager.play_sfx("ui_click")

        if (mouse_click[0] or mouse_click[2]) and not ui_panel.collidepoint(mouse_pos) and not state.CHEAT_MENU_VISIBLE:
            gx = (mouse_pos[0] - offset_x) // cell_size
            gy = (mouse_pos[1] + camera_y) // cell_size
            if 0 <= gx < grid_w and 0 <= gy < grid_h: 
                grid[gy][gx] = 0 if mouse_click[2] else current_tool

        screen.fill((10, 15, 25))
        
        for row in range(grid_h):
            y_pos = (row * cell_size) - camera_y
            if -cell_size <= y_pos <= SCREEN_HEIGHT:
                if row % 10 == 0: 
                    ui.draw_text(f"Row {row}", FONT_SMALL, (100, 100, 100), offset_x - 50, y_pos + cell_size//2, screen)
                
                for col in range(grid_w):
                    r = pygame.Rect(offset_x + col * cell_size, y_pos, cell_size, cell_size)
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

        # Bottom UI
        pygame.draw.rect(screen, (20, 20, 30), ui_panel)
        pygame.draw.line(screen, CYAN, (0, ui_panel.top), (SCREEN_WIDTH, ui_panel.top), 2)
        
        pygame.draw.rect(screen, (150, 0, 0), exit_btn, border_radius=8)
        ui.draw_text("EXIT", FONT_LARGE, WHITE, exit_btn.centerx, exit_btn.centery, screen)
        
        pygame.draw.rect(screen, WIN_GREEN, play_btn, border_radius=8)
        ui.draw_text("▶ TEST", FONT_LARGE, BLACK, play_btn.centerx, play_btn.centery, screen)
        
        pygame.draw.rect(screen, BUTTON_COLOR, save_btn, border_radius=5)
        ui.draw_text("SAVE LEVEL", FONT_SMALL, WHITE, save_btn.centerx, save_btn.centery, screen)
        
        pygame.draw.rect(screen, BUTTON_COLOR, load_btn, border_radius=5)
        ui.draw_text("LOAD LEVEL", FONT_SMALL, WHITE, load_btn.centerx, load_btn.centery, screen)

        for i, t in enumerate(tools):
            tr = pygame.Rect(tool_start_x + (i * (tool_w + tool_gap)), SCREEN_HEIGHT - 90, tool_w, tool_h)
            is_active = (current_tool == t["id"])
            col = t["color"] if is_active else (t["color"][0]//3, t["color"][1]//3, t["color"][2]//3)
            pygame.draw.rect(screen, col, tr, border_radius=6)
            pygame.draw.rect(screen, WHITE if is_active else (60, 70, 90), tr, 2 if is_active else 1, border_radius=6)
            ui.draw_text(t["name"], FONT_SMALL, WHITE, tr.centerx, tr.centery, screen)

        if msg and pygame.time.get_ticks() - msg_timer < 2000: 
            ui.draw_text(msg, FONT_SMALL, WIN_GREEN if "!" in msg else RED, save_btn.centerx, save_btn.top - 12, screen)
            
        megahack.draw(screen)
        pygame.display.flip()
        clock.tick(int(FPS * state.GAME_SPEED))