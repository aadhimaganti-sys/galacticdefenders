import pygame
import random
import sys
import json
import socket

from settings import *
import state
import network
from sprites import Player, Asteroid, Boss, SpinoffDrone, Explosion, PowerUp
from autopilot import AdvancedAutoPilot
from level_editor import run_level_editor, process_active_hacks
import ui
import megahack
import sound_manager

pygame.init()
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
# --- 2.2 VIRTUAL CAMERA CANVAS ---
VIRTUAL_SURFACE = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Galactic Defender - 2.2 Cinematic Engine")
CLOCK = pygame.time.Clock()

ASTEROID_SPAWN_RATE_INITIAL = 60
ASTEROID_BASE_SPEED_INITIAL = 2
SCORE_TO_WIN = 5000

def spinoff_game_loop():
    sound_manager.play_music("story_theme")
    player = Player(player_id=1, ship_type_key=state.all_player_data["P1"]["selected_ship"])
    all_sprites = pygame.sprite.Group()
    player_bullets = pygame.sprite.Group()
    enemy_bullets = pygame.sprite.Group()
    asteroids = pygame.sprite.Group()
    drones = pygame.sprite.Group()
    
    all_sprites.add(player)
    
    levels = [
        {"title": "CHAPTER 1: THE RIFT", "text": ["Dodge the anomaly rocks for 10 seconds!"], "goal_type": "time", "goal_val": 10 * FPS, "bg_color": (25, 0, 40)},
        {"title": "CHAPTER 2: THE ARCHITECTS", "text": ["Destroy 8 Architect Drones to open the path!"], "goal_type": "kill", "goal_val": 8, "bg_color": (0, 30, 30)},
        {"title": "CHAPTER 3: THE OMEGA PROTOCOL", "text": ["Defeat the Omega Core to escape!"], "goal_type": "boss", "goal_val": 1, "bg_color": (40, 0, 0)}
    ]
    
    c_level = 0
    story_state = "DIALOGUE"
    dialogue_idx = 0
    level_timer = 0
    level_progress = 0
    the_boss = None

    running = True
    while running:
        if c_level >= len(levels): 
            return "HOME"
        lvl_data = levels[c_level]
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT: 
                return "QUIT_PROGRAM"
            if megahack.handle_event(event): 
                continue
            
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
                state.ACTIVE_HACKS["Auto Pilot"] = not state.ACTIVE_HACKS.get("Auto Pilot", False)
                
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: 
                    return "HOME"
                if event.key == pygame.K_p: 
                    state.ACTIVE_HACKS["Auto Pilot"] = not state.ACTIVE_HACKS.get("Auto Pilot", False)
                if story_state == "DIALOGUE" and event.key == pygame.K_SPACE:
                    dialogue_idx += 1
                    sound_manager.play_sfx("dialogue_beep", 0.6)
                    if dialogue_idx >= len(lvl_data["text"]):
                        story_state = "PLAYING"
                        level_timer = 0
                        level_progress = 0
                        for s in asteroids: s.kill()
                        for d in drones: d.kill()
                elif story_state == "PLAYING" and event.key == pygame.K_SPACE and not state.CHEAT_MENU_VISIBLE: 
                    player.shoot(all_sprites, player_bullets)

        if story_state == "PLAYING":
            if state.ACTIVE_HACKS.get("Auto Pilot", False):
                AdvancedAutoPilot.run(player, all_sprites, player_bullets, asteroids=asteroids, drones=drones, enemy_bullets=enemy_bullets, boss=the_boss)
            
            process_active_hacks({1:player}, all_sprites, asteroids, drones, None, pygame.sprite.GroupSingle(the_boss) if the_boss else None)
            
            # --- REVERSE TIME ENGINE ---
            if state.ACTIVE_HACKS.get("Reverse Time", False):
                for sprite in all_sprites:
                    if not isinstance(sprite, Player):
                        if hasattr(sprite, 'speed_x'): sprite.rect.x -= sprite.speed_x * 2
                        if hasattr(sprite, 'speed_y'): sprite.rect.y -= sprite.speed_y * 2
                        if isinstance(sprite, Boss): sprite.rect.x -= (sprite.speed_x * sprite.direction_x) * 2
            else:
                all_sprites.update()
            
            if not state.ACTIVE_HACKS.get("Reverse Time", False):
                if lvl_data["goal_type"] == "time":
                    level_timer += 1
                    if level_timer % 40 == 0: 
                        ast = Asteroid(1.5, True)
                        all_sprites.add(ast)
                        asteroids.add(ast)
                    if level_timer >= lvl_data["goal_val"]: 
                        story_state = "LEVEL_CLEAR"
                        sound_manager.play_sfx("level_up", 0.9)
                        
                elif lvl_data["goal_type"] == "kill":
                    level_timer += 1
                    if level_timer % 80 == 0 and len(drones) < 3: 
                        drone = SpinoffDrone()
                        all_sprites.add(drone)
                        drones.add(drone)
                    for d in drones: 
                        d.shoot(all_sprites, enemy_bullets)
                    if level_progress >= lvl_data["goal_val"]: 
                        story_state = "LEVEL_CLEAR"
                        sound_manager.play_sfx("level_up", 0.9)
                        
                elif lvl_data["goal_type"] == "boss":
                    if not the_boss or not the_boss.alive():
                        if level_timer == 0: 
                            the_boss = Boss(800, MAGENTA)
                            all_sprites.add(the_boss)
                            level_timer = 1
                        else: 
                            story_state = "LEVEL_CLEAR"
                            sound_manager.play_sfx("level_up", 0.9)
                    else: 
                        the_boss.shoot(all_sprites, enemy_bullets, 600)

                for b in list(player_bullets):
                    for ast in pygame.sprite.spritecollide(b, asteroids, True): 
                        b.kill()
                        all_sprites.add(Explosion(ast.rect.center, size="small"))
                    for drn in pygame.sprite.spritecollide(b, drones, True): 
                        b.kill()
                        all_sprites.add(Explosion(drn.rect.center, size="medium"))
                        level_progress += 1
                    if the_boss and the_boss.alive() and pygame.sprite.collide_rect(b, the_boss):
                        b.kill()
                        the_boss.health -= 20
                        if the_boss.health <= 0: 
                            the_boss.kill()
                            all_sprites.add(Explosion(the_boss.rect.center, size="boss"))

                if pygame.sprite.spritecollide(player, asteroids, True) or pygame.sprite.spritecollide(player, drones, True) or pygame.sprite.spritecollide(player, enemy_bullets, True):
                    if not player.take_hit(): 
                        all_sprites.add(Explosion(player.rect.center, size="medium"))
                        player.kill()
                        story_state = "GAME_OVER"
                        sound_manager.play_sfx("game_over", 0.9)

        # --- 2.2 CYBERPUNK BACKGROUND ENGINE ---
        if state.ACTIVE_HACKS.get("Cyberpunk BG", False):
            VIRTUAL_SURFACE.fill((10, 0, 30))
            offset = (pygame.time.get_ticks() // 15) % 50
            for y in range(0, SCREEN_HEIGHT, 50):
                pygame.draw.line(VIRTUAL_SURFACE, (255, 0, 255), (0, y + offset), (SCREEN_WIDTH, y + offset), 1)
            for x in range(0, SCREEN_WIDTH, 50):
                pygame.draw.line(VIRTUAL_SURFACE, (0, 255, 255), (x, 0), (x, SCREEN_HEIGHT), 1)
        else:
            VIRTUAL_SURFACE.fill(lvl_data["bg_color"])
            ui.draw_stars(VIRTUAL_SURFACE) 
        
        # --- PARTICLE RENDERER ---
        for p in reversed(state.particle_list):
            if not state.ACTIVE_HACKS.get("Freeze Time", False) and not state.ACTIVE_HACKS.get("Reverse Time", False):
                p[0] += p[2]
                p[1] += p[3]
                p[4] -= 1
            elif state.ACTIVE_HACKS.get("Reverse Time", False):
                p[0] -= p[2]
                p[1] -= p[3]
                p[4] += 1
                if p[4] > p[5]: p[4] = p[5]
                
            if p[4] <= 0:
                state.particle_list.remove(p)
            else:
                alpha = int((p[4] / p[5]) * 255)
                s = pygame.Surface((6, 6), pygame.SRCALPHA)
                pygame.draw.circle(s, (*p[6][:3], alpha), (3, 3), 3)
                VIRTUAL_SURFACE.blit(s, (int(p[0]) - 3, int(p[1]) - 3))

        for sprite in all_sprites:
            if isinstance(sprite, Player): 
                sprite.draw(VIRTUAL_SURFACE)
            else: 
                VIRTUAL_SURFACE.blit(sprite.image, sprite.rect)
                
            if state.ACTIVE_HACKS.get("Show Hitboxes", False):
                pygame.draw.rect(VIRTUAL_SURFACE, RED, sprite.rect, 2)
                pygame.draw.circle(VIRTUAL_SURFACE, YELLOW, sprite.rect.center, 3)

        if story_state == "DIALOGUE":
            ui.draw_text(lvl_data["title"], FONT_LARGE, CYAN, SCREEN_WIDTH//2, 75, VIRTUAL_SURFACE)
            if dialogue_idx < len(lvl_data["text"]):
                ui.draw_text(lvl_data["text"][dialogue_idx], FONT_MEDIUM, WHITE, SCREEN_WIDTH//2, SCREEN_HEIGHT - 75, VIRTUAL_SURFACE)
        elif story_state == "LEVEL_CLEAR":
            ui.draw_text("SECTOR CLEARED", FONT_XLARGE, WIN_GREEN, SCREEN_WIDTH//2, SCREEN_HEIGHT//2, VIRTUAL_SURFACE)
            level_timer += 1
            if level_timer > 90: 
                c_level += 1
                story_state = "DIALOGUE"
                dialogue_idx = 0
                level_timer = 0
        elif story_state == "GAME_OVER":
            ui.draw_text("SYSTEM FAILURE", FONT_XLARGE, LOSE_RED, SCREEN_WIDTH//2, SCREEN_HEIGHT//2, VIRTUAL_SURFACE)

        # --- 2.2 CAMERA RENDER PIPELINE ---
        if state.ACTIVE_HACKS.get("Force Screen Shake", False):
            state.CAMERA_SHAKE = 20
            state.ACTIVE_HACKS["Force Screen Shake"] = False

        if state.ACTIVE_HACKS.get("Cinematic Zoom", False):
            state.CAMERA_ZOOM = min(1.5, state.CAMERA_ZOOM + 0.01)
        else:
            state.CAMERA_ZOOM = max(1.0, state.CAMERA_ZOOM - 0.05)

        if state.ACTIVE_HACKS.get("Rotate Screen", False):
            state.CAMERA_ANGLE = (state.CAMERA_ANGLE + 1) % 360
        else:
            state.CAMERA_ANGLE = 0

        if state.CAMERA_SHAKE > 0:
            state.CAMERA_SHAKE -= 1

        shake_x = random.randint(-state.CAMERA_SHAKE, state.CAMERA_SHAKE) if state.CAMERA_SHAKE > 0 else 0
        shake_y = random.randint(-state.CAMERA_SHAKE, state.CAMERA_SHAKE) if state.CAMERA_SHAKE > 0 else 0

        # CHROMATIC ABERRATION (RGB SPLIT)
        if state.ACTIVE_HACKS.get("Chromatic Aberration", False):
            surf_r = VIRTUAL_SURFACE.copy()
            surf_r.fill((255, 0, 0), special_flags=pygame.BLEND_RGB_MULT)
            surf_b = VIRTUAL_SURFACE.copy()
            surf_b.fill((0, 0, 255), special_flags=pygame.BLEND_RGB_MULT)
            surf_g = VIRTUAL_SURFACE.copy()
            surf_g.fill((0, 255, 0), special_flags=pygame.BLEND_RGB_MULT)

            VIRTUAL_SURFACE.fill(BLACK)
            VIRTUAL_SURFACE.blit(surf_r, (-6, 0), special_flags=pygame.BLEND_RGB_ADD)
            VIRTUAL_SURFACE.blit(surf_g, (0, 0), special_flags=pygame.BLEND_RGB_ADD)
            VIRTUAL_SURFACE.blit(surf_b, (6, 0), special_flags=pygame.BLEND_RGB_ADD)

        # APPLY ZOOM AND ROTATION TO FINAL CANVAS
        final_surf = VIRTUAL_SURFACE
        if state.CAMERA_ZOOM != 1.0 or state.CAMERA_ANGLE != 0:
            zoomed_w = int(SCREEN_WIDTH * state.CAMERA_ZOOM)
            zoomed_h = int(SCREEN_HEIGHT * state.CAMERA_ZOOM)
            final_surf = pygame.transform.scale(final_surf, (zoomed_w, zoomed_h))
            if state.CAMERA_ANGLE != 0:
                final_surf = pygame.transform.rotate(final_surf, state.CAMERA_ANGLE)

        offset_x = (SCREEN_WIDTH - final_surf.get_width()) // 2
        offset_y = (SCREEN_HEIGHT - final_surf.get_height()) // 2
        SCREEN.blit(final_surf, (offset_x + shake_x, offset_y + shake_y))

        megahack.draw(SCREEN)
        pygame.display.flip()
        CLOCK.tick(int(FPS * state.GAME_SPEED))
        
    return "HOME"

def ultimate_boss_loop():
    sound_manager.play_music("boss_theme")
    state.CHEAT_MENU_VISIBLE = False
    player = Player(1, "default_jet")
    all_sprites = pygame.sprite.Group()
    p_bullets = pygame.sprite.Group()
    e_bullets = pygame.sprite.Group()
    asteroids = pygame.sprite.Group()
    
    all_sprites.add(player)
    
    the_boss = Boss(2000, (150, 0, 0))
    the_boss.speed_x = 5 
    all_sprites.add(the_boss)

    running = True
    b_state = "PLAYING"
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: 
                return "QUIT_PROGRAM"
            if megahack.handle_event(event): 
                continue
            
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3: 
                state.ACTIVE_HACKS["Auto Pilot"] = not state.ACTIVE_HACKS.get("Auto Pilot", False)
                
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: 
                    return "HOME"
                if event.key == pygame.K_p: 
                    state.ACTIVE_HACKS["Auto Pilot"] = not state.ACTIVE_HACKS.get("Auto Pilot", False)
                if b_state == "PLAYING" and event.key == pygame.K_SPACE and not state.CHEAT_MENU_VISIBLE: 
                    player.shoot(all_sprites, p_bullets)

        if b_state == "PLAYING":
            if state.ACTIVE_HACKS.get("Auto Pilot", False):
                AdvancedAutoPilot.run(player, all_sprites, p_bullets, asteroids=asteroids, enemy_bullets=e_bullets, boss=the_boss)

            process_active_hacks({1:player}, all_sprites, asteroids, None, None, pygame.sprite.GroupSingle(the_boss))
            
            # --- 2.2 REVERSE TIME ENGINE INJECTION ---
            if state.ACTIVE_HACKS.get("Reverse Time", False):
                for sprite in all_sprites:
                    if not isinstance(sprite, Player):
                        if hasattr(sprite, 'speed_x'): sprite.rect.x -= sprite.speed_x * 2
                        if hasattr(sprite, 'speed_y'): sprite.rect.y -= sprite.speed_y * 2
                        if isinstance(sprite, Boss): sprite.rect.x -= (sprite.speed_x * sprite.direction_x) * 2
            else:
                all_sprites.update()
            
            if state.ACTIVE_HACKS.get("Level Up", False):
                the_boss.health -= 500
                state.ACTIVE_HACKS["Level Up"] = False

            if not state.ACTIVE_HACKS.get("Reverse Time", False):
                if the_boss.alive():
                    the_boss.shoot(all_sprites, e_bullets, 250) 
                else: 
                    b_state = "LEVEL_CLEAR"
                    sound_manager.play_sfx("victory", 1.0)

                if random.randint(1, 45) == 1: 
                    ast = Asteroid(2.5, True)
                    all_sprites.add(ast)
                    asteroids.add(ast)

                for b in list(p_bullets):
                    for ast in pygame.sprite.spritecollide(b, asteroids, True): 
                        b.kill()
                        all_sprites.add(Explosion(ast.rect.center, size="small"))
                        
                    if the_boss.alive() and pygame.sprite.collide_rect(b, the_boss):
                        b.kill()
                        the_boss.health -= 15
                        if the_boss.health <= 0: 
                            the_boss.kill()
                            all_sprites.add(Explosion(the_boss.rect.center, size="boss"))
                            b_state = "LEVEL_CLEAR"
                            sound_manager.play_sfx("victory", 1.0)

                if pygame.sprite.spritecollide(player, asteroids, True) or pygame.sprite.spritecollide(player, e_bullets, True):
                    if not player.take_hit(): 
                        all_sprites.add(Explosion(player.rect.center, size="medium"))
                        player.kill()
                        b_state = "GAME_OVER"
                        sound_manager.play_sfx("game_over", 1.0)

        # --- 2.2 CYBERPUNK BACKGROUND ENGINE ---
        if state.ACTIVE_HACKS.get("Cyberpunk BG", False):
            VIRTUAL_SURFACE.fill((20, 0, 0))
            offset = (pygame.time.get_ticks() // 15) % 50
            for y in range(0, SCREEN_HEIGHT, 50):
                pygame.draw.line(VIRTUAL_SURFACE, (255, 0, 0), (0, y + offset), (SCREEN_WIDTH, y + offset), 1)
            for x in range(0, SCREEN_WIDTH, 50):
                pygame.draw.line(VIRTUAL_SURFACE, (255, 100, 0), (x, 0), (x, SCREEN_HEIGHT), 1)
        else:
            VIRTUAL_SURFACE.fill((30, 0, 0)) 
            ui.draw_stars(VIRTUAL_SURFACE)

        if state.TON_618_ACTIVE: 
            pygame.draw.circle(VIRTUAL_SURFACE, (50, 0, 100), (SCREEN_WIDTH//2, SCREEN_HEIGHT//2), 80)

        # --- PARTICLE RENDERER ---
        for p in reversed(state.particle_list):
            if not state.ACTIVE_HACKS.get("Freeze Time", False) and not state.ACTIVE_HACKS.get("Reverse Time", False):
                p[0] += p[2]
                p[1] += p[3]
                p[4] -= 1
            elif state.ACTIVE_HACKS.get("Reverse Time", False):
                p[0] -= p[2]
                p[1] -= p[3]
                p[4] += 1
                if p[4] > p[5]: p[4] = p[5]
                
            if p[4] <= 0:
                state.particle_list.remove(p)
            else:
                alpha = int((p[4] / p[5]) * 255)
                s = pygame.Surface((6, 6), pygame.SRCALPHA)
                pygame.draw.circle(s, (*p[6][:3], alpha), (3, 3), 3)
                VIRTUAL_SURFACE.blit(s, (int(p[0]) - 3, int(p[1]) - 3))

        for sprite in all_sprites:
            if isinstance(sprite, Player): 
                sprite.draw(VIRTUAL_SURFACE)
            else: 
                VIRTUAL_SURFACE.blit(sprite.image, sprite.rect)
                
            if state.ACTIVE_HACKS.get("Show Hitboxes", False):
                pygame.draw.rect(VIRTUAL_SURFACE, RED, sprite.rect, 2)
                pygame.draw.circle(VIRTUAL_SURFACE, YELLOW, sprite.rect.center, 3)

        if the_boss.alive():
            pygame.draw.rect(VIRTUAL_SURFACE, RED, (SCREEN_WIDTH//2 - 300, 40, 600, 20))
            pygame.draw.rect(VIRTUAL_SURFACE, WIN_GREEN, (SCREEN_WIDTH//2 - 300, 40, int(max(0, the_boss.health)/the_boss.max_health * 600), 20))
                    
        if b_state == "LEVEL_CLEAR": 
            ui.draw_text("OMEGA DEFEATED. YOU ARE A TRUE PILOT.", FONT_LARGE, WIN_GREEN, SCREEN_WIDTH//2, SCREEN_HEIGHT//2, VIRTUAL_SURFACE)
        elif b_state == "GAME_OVER": 
            ui.draw_text("SYSTEM FAILURE", FONT_LARGE, LOSE_RED, SCREEN_WIDTH//2, SCREEN_HEIGHT//2, VIRTUAL_SURFACE)

        # --- 2.2 CAMERA RENDER PIPELINE ---
        if state.ACTIVE_HACKS.get("Force Screen Shake", False):
            state.CAMERA_SHAKE = 20
            state.ACTIVE_HACKS["Force Screen Shake"] = False

        if state.ACTIVE_HACKS.get("Cinematic Zoom", False):
            state.CAMERA_ZOOM = min(1.5, state.CAMERA_ZOOM + 0.01)
        else:
            state.CAMERA_ZOOM = max(1.0, state.CAMERA_ZOOM - 0.05)

        if state.ACTIVE_HACKS.get("Rotate Screen", False):
            state.CAMERA_ANGLE = (state.CAMERA_ANGLE + 1) % 360
        else:
            state.CAMERA_ANGLE = 0

        if state.CAMERA_SHAKE > 0:
            state.CAMERA_SHAKE -= 1

        shake_x = random.randint(-state.CAMERA_SHAKE, state.CAMERA_SHAKE) if state.CAMERA_SHAKE > 0 else 0
        shake_y = random.randint(-state.CAMERA_SHAKE, state.CAMERA_SHAKE) if state.CAMERA_SHAKE > 0 else 0

        # CHROMATIC ABERRATION (RGB SPLIT)
        if state.ACTIVE_HACKS.get("Chromatic Aberration", False):
            surf_r = VIRTUAL_SURFACE.copy()
            surf_r.fill((255, 0, 0), special_flags=pygame.BLEND_RGB_MULT)
            surf_b = VIRTUAL_SURFACE.copy()
            surf_b.fill((0, 0, 255), special_flags=pygame.BLEND_RGB_MULT)
            surf_g = VIRTUAL_SURFACE.copy()
            surf_g.fill((0, 255, 0), special_flags=pygame.BLEND_RGB_MULT)

            VIRTUAL_SURFACE.fill(BLACK)
            VIRTUAL_SURFACE.blit(surf_r, (-6, 0), special_flags=pygame.BLEND_RGB_ADD)
            VIRTUAL_SURFACE.blit(surf_g, (0, 0), special_flags=pygame.BLEND_RGB_ADD)
            VIRTUAL_SURFACE.blit(surf_b, (6, 0), special_flags=pygame.BLEND_RGB_ADD)

        # APPLY ZOOM AND ROTATION TO FINAL CANVAS
        final_surf = VIRTUAL_SURFACE
        if state.CAMERA_ZOOM != 1.0 or state.CAMERA_ANGLE != 0:
            zoomed_w = int(SCREEN_WIDTH * state.CAMERA_ZOOM)
            zoomed_h = int(SCREEN_HEIGHT * state.CAMERA_ZOOM)
            final_surf = pygame.transform.scale(final_surf, (zoomed_w, zoomed_h))
            if state.CAMERA_ANGLE != 0:
                final_surf = pygame.transform.rotate(final_surf, state.CAMERA_ANGLE)

        offset_x = (SCREEN_WIDTH - final_surf.get_width()) // 2
        offset_y = (SCREEN_HEIGHT - final_surf.get_height()) // 2
        SCREEN.blit(final_surf, (offset_x + shake_x, offset_y + shake_y))

        megahack.draw(SCREEN)
        pygame.display.flip()
        CLOCK.tick(int(FPS * state.GAME_SPEED))
        
    return "HOME"

def game_loop(current_mode):
    is_host = current_mode.startswith("LAN_HOST") or current_mode in ["MULTI_CLASSIC", "SINGLE_CLASSIC", "HOST_CLOUD", "SINGLE_BOSS", "MULTI_BOSS"]
    is_client = current_mode in ["LAN_JOIN", "JOIN_CLOUD"]
    BOSS_MODE_ACTIVE = "BOSS" in current_mode

    if is_client:
        client_cache = {}
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT: return "QUIT_PROGRAM"
                if megahack.handle_event(event): continue

            keys = pygame.key.get_pressed()
            my_keys = {
                "l": keys[pygame.K_a] or keys[pygame.K_LEFT], 
                "r": keys[pygame.K_d] or keys[pygame.K_RIGHT], 
                "u": keys[pygame.K_w] or keys[pygame.K_UP], 
                "d": keys[pygame.K_s] or keys[pygame.K_DOWN], 
                "sh": keys[pygame.K_SPACE] or keys[pygame.K_RETURN]
            }
            
            try: network.udp_sock.sendto(json.dumps(my_keys).encode(), network.network_target)
            except Exception: pass

            net_state = None
            try:
                while True: 
                    data, _ = network.udp_sock.recvfrom(65535)
                    net_state = json.loads(data.decode())
            except Exception: pass

            if net_state:
                if net_state.get("win") is not None:
                    state.win_status = net_state["win"]
                    state.score_p1 = net_state.get("p1", {}).get("s", 0)
                    state.score_p2 = net_state.get("p2", {}).get("s", 0)
                    return "GAME_OVER"

                VIRTUAL_SURFACE.fill(BLACK)
                ui.draw_stars(VIRTUAL_SURFACE)

                for p_data in net_state.get("players", []):
                    pid = p_data["id"]
                    if pid not in client_cache: client_cache[pid] = Player(pid)
                    cp = client_cache[pid]
                    cp.rect.x, cp.rect.y = p_data["x"], p_data["y"]
                    cp.draw(VIRTUAL_SURFACE)

                for a in net_state.get("a", []): pygame.draw.circle(VIRTUAL_SURFACE, (80, 80, 80), (a[0] + a[2]//2, a[1] + a[2]//2), a[2]//2)
                for pu in net_state.get("pu", []): pygame.draw.circle(VIRTUAL_SURFACE, MAGENTA if pu[2] == "triple_shot" else CYAN, (pu[0], pu[1]), 15)
                for pb in net_state.get("pb", []): pygame.draw.ellipse(VIRTUAL_SURFACE, BULLET_YELLOW, [pb[0]-3, pb[1]-20, 6, 16])
                
                if net_state.get("bo"):
                    bo = net_state["bo"]
                    pygame.draw.rect(VIRTUAL_SURFACE, BOSS_COLOR, (bo["x"], bo["y"], 200, 150), border_radius=15)
                    pygame.draw.rect(VIRTUAL_SURFACE, RED, (SCREEN_WIDTH//2 - 100, 20, 200, 20))
                    pygame.draw.rect(VIRTUAL_SURFACE, WIN_GREEN, (SCREEN_WIDTH//2 - 100, 20, int(max(0, bo["h"])/bo["m"] * 200), 20))

                ui.draw_text(f"Level: {net_state.get('l', 1)}", FONT_MEDIUM, YELLOW, SCREEN_WIDTH//2, 55, VIRTUAL_SURFACE)

                if state.ACTIVE_HACKS.get("Force Screen Shake", False):
                    state.CAMERA_SHAKE = 20
                    state.ACTIVE_HACKS["Force Screen Shake"] = False
                if state.ACTIVE_HACKS.get("Cinematic Zoom", False):
                    state.CAMERA_ZOOM = min(1.5, state.CAMERA_ZOOM + 0.01)
                else:
                    state.CAMERA_ZOOM = max(1.0, state.CAMERA_ZOOM - 0.05)
                if state.CAMERA_SHAKE > 0: state.CAMERA_SHAKE -= 1

                shake_x = random.randint(-state.CAMERA_SHAKE, state.CAMERA_SHAKE) if state.CAMERA_SHAKE > 0 else 0
                shake_y = random.randint(-state.CAMERA_SHAKE, state.CAMERA_SHAKE) if state.CAMERA_SHAKE > 0 else 0

                if state.CAMERA_ZOOM != 1.0:
                    zoomed_w = int(SCREEN_WIDTH * state.CAMERA_ZOOM)
                    zoomed_h = int(SCREEN_HEIGHT * state.CAMERA_ZOOM)
                    zoomed_surface = pygame.transform.scale(VIRTUAL_SURFACE, (zoomed_w, zoomed_h))
                    offset_x = (SCREEN_WIDTH - zoomed_w) // 2
                    offset_y = (SCREEN_HEIGHT - zoomed_h) // 2
                    SCREEN.blit(zoomed_surface, (offset_x + shake_x, offset_y + shake_y))
                else:
                    SCREEN.blit(VIRTUAL_SURFACE, (shake_x, shake_y))

                megahack.draw(SCREEN)
                pygame.display.flip()
                
            CLOCK.tick(int(FPS * state.GAME_SPEED))

    if BOSS_MODE_ACTIVE:
        sound_manager.play_music("boss_theme")
    else:
        sound_manager.play_music("battle_theme")

    # Host & Offline Setup
    players = {1: Player(1, state.all_player_data["P1"]["selected_ship"])}
    if "MULTI" in current_mode: 
        players[2] = Player(2, state.all_player_data["P2"]["selected_ship"])
    
    all_sprites = pygame.sprite.Group()
    asteroids = pygame.sprite.Group()
    p_bullets = pygame.sprite.Group()
    powerups = pygame.sprite.Group()
    
    all_sprites.add(players[1])
    if 2 in players: 
        all_sprites.add(players[2])

    boss = Boss() if BOSS_MODE_ACTIVE else None
    if boss: 
        all_sprites.add(boss)
    boss_bullets = pygame.sprite.Group()

    state.level = 1
    state.score_p1 = 0
    state.score_p2 = 0
    ast_timer = 0
    pu_timer = 0
    
    if not BOSS_MODE_ACTIVE:
        for _ in range(10): 
            ast = Asteroid(1)
            all_sprites.add(ast)
            asteroids.add(ast)

    connected_clients = {}
    next_client_id = 2 if "HOST" in current_mode else 1
    running = True

    while running:
        if current_mode.startswith("LAN_HOST") or current_mode == "HOST_CLOUD":
            try:
                while True:
                    data, addr = network.udp_sock.recvfrom(65535)
                    raw_data = json.loads(data.decode())
                    client_id = raw_data.get("client_addr", str(addr))
                    client_keys = raw_data.get("keys", raw_data)
                    
                    if client_id not in connected_clients:
                        connected_clients[client_id] = next_client_id
                        new_p = Player(player_id=next_client_id)
                        new_p.is_network_client = True
                        players[next_client_id] = new_p
                        all_sprites.add(new_p)
                        next_client_id += 1
                        
                    pid = connected_clients[client_id]
                    if pid in players:
                        players[pid].network_keys = client_keys
                        if client_keys.get("sh"): 
                            players[pid].shoot(all_sprites, p_bullets)
            except Exception: 
                pass

        for event in pygame.event.get():
            if event.type == pygame.QUIT: 
                return "QUIT_PROGRAM"
            if megahack.handle_event(event): 
                continue
            
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3: 
                state.ACTIVE_HACKS["Auto Pilot"] = not state.ACTIVE_HACKS.get("Auto Pilot", False)
                
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p: 
                    state.ACTIVE_HACKS["Auto Pilot"] = not state.ACTIVE_HACKS.get("Auto Pilot", False)
                if event.key == pygame.K_SPACE and not state.CHEAT_MENU_VISIBLE: 
                    players[1].shoot(all_sprites, p_bullets)
                if 2 in players and not current_mode.startswith("LAN_HOST") and not current_mode == "HOST_CLOUD":
                    if event.key in [pygame.K_RSHIFT, pygame.K_RETURN]: 
                        players[2].shoot(all_sprites, p_bullets)

        if state.ACTIVE_HACKS.get("Auto Pilot", False):
            AdvancedAutoPilot.run(players[1], all_sprites, p_bullets, asteroids=asteroids, powerups=powerups, enemy_bullets=boss_bullets, boss=boss)

        process_active_hacks(players, all_sprites, asteroids, None, powerups, pygame.sprite.GroupSingle(boss) if boss else None)
        
        if state.ACTIVE_HACKS.get("Level Up", False):
            state.level += 1
            sound_manager.play_sfx("level_up", 0.9)
            if boss: boss.health -= 200
            state.ACTIVE_HACKS["Level Up"] = False
        if state.ACTIVE_HACKS.get("Level Down", False):
            state.level = max(1, state.level - 1)
            state.ACTIVE_HACKS["Level Down"] = False

        # --- REVERSE TIME ENGINE ---
        if state.ACTIVE_HACKS.get("Reverse Time", False):
            for sprite in all_sprites:
                if not isinstance(sprite, Player):
                    if hasattr(sprite, 'speed_x'): sprite.rect.x -= sprite.speed_x * 2
                    if hasattr(sprite, 'speed_y'): sprite.rect.y -= sprite.speed_y * 2
                    if isinstance(sprite, Boss): sprite.rect.x -= (sprite.speed_x * sprite.direction_x) * 2
        else:
            all_sprites.update()

        if not state.ACTIVE_HACKS.get("Reverse Time", False):
            if boss: 
                boss.shoot(all_sprites, boss_bullets)

            if not BOSS_MODE_ACTIVE:
                ast_timer += 1
                if ast_timer >= max(10, 60 - (state.level * 5)):
                    ast = Asteroid(1 + (state.level * 0.02))
                    all_sprites.add(ast)
                    asteroids.add(ast)
                    ast_timer = 0
                
                pu_timer += 1
                if pu_timer >= 600:
                    pu = PowerUp((random.randint(50, SCREEN_WIDTH - 50), -50), random.choice(["triple_shot", "shield"]))
                    all_sprites.add(pu)
                    powerups.add(pu)
                    pu_timer = 0

            for b in list(p_bullets):
                for ast in pygame.sprite.spritecollide(b, asteroids, True):
                    b.kill()
                    all_sprites.add(Explosion(ast.rect.center, size="small"))
                    if b.owner_id in players:
                        players[b.owner_id].add_score(10)
                        
                if boss and pygame.sprite.collide_rect(b, boss):
                    b.kill()
                    boss.health -= 10
                    if boss.health <= 0: 
                        boss.kill()
                        all_sprites.add(Explosion(boss.rect.center, size="boss"))
                        running = False
                        state.win_status = True
                        sound_manager.play_sfx("victory", 1.0)

            for p in players.values():
                for ast in pygame.sprite.spritecollide(p, asteroids, True):
                    if not p.take_hit(): 
                        all_sprites.add(Explosion(p.rect.center, size="medium"))
                        running = False
                        state.win_status = False
                        sound_manager.play_sfx("game_over", 1.0)
                    else: 
                        all_sprites.add(Explosion(ast.rect.center, size="small"))
                        new_ast = Asteroid(1)
                        all_sprites.add(new_ast)
                        asteroids.add(new_ast)
                        
                if boss_bullets:
                    for bb in pygame.sprite.spritecollide(p, boss_bullets, True):
                        if not p.take_hit(): 
                            all_sprites.add(Explosion(p.rect.center, size="medium"))
                            running = False
                            state.win_status = False
                            sound_manager.play_sfx("game_over", 1.0)
                            
                for pu in pygame.sprite.spritecollide(p, powerups, True):
                    if pu.power_type == "triple_shot": 
                        p.activate_triple_shot()
                    elif pu.power_type == "shield": 
                        p.activate_shield()

            if not BOSS_MODE_ACTIVE and running:
                state.score_p1 = players[1].score
                state.score_p2 = players[2].score if 2 in players else 0
                max_score = max([p.score for p in players.values()])
                if max_score >= SCORE_TO_WIN: 
                    state.win_status = True
                    running = False
                    sound_manager.play_sfx("victory", 1.0)
                elif max_score >= state.level * 1000: 
                    state.level += 1
                    sound_manager.play_sfx("level_up", 0.9)

        if current_mode.startswith("LAN_HOST") or current_mode == "HOST_CLOUD":
            payload = {
                "players": [{"id": p.player_id, "x": p.rect.x, "y": p.rect.y, "s": p.score, "b": p.num_blasters} for p in players.values()],
                "a": [[a.rect.x, a.rect.y, a.size] for a in asteroids],
                "pu": [[pu.rect.centerx, pu.rect.centery, pu.power_type] for pu in powerups],
                "pb": [[b.rect.centerx, b.rect.bottom, b.owner_id] for b in p_bullets],
                "bo": {"x": boss.rect.x, "y": boss.rect.y, "h": boss.health, "m": boss.max_health} if boss else None,
                "l": state.level, 
                "win": state.win_status if not running else None,
                "p1": {"s": state.score_p1}, 
                "p2": {"s": state.score_p2}
            }
            if current_mode == "HOST_CLOUD":
                try: 
                    network.udp_sock.sendto(json.dumps({"action": "HOST_LOBBY", "lobby": network.GLOBAL_LOBBY_CODE, "state": payload}).encode(), (CLOUD_SERVER_IP, NETWORK_PORT))
                except Exception: 
                    pass
            else:
                for c_addr in [k for k in connected_clients.keys() if isinstance(k, str)]:
                    parts = c_addr.strip("()").split(", ")
                    network.udp_sock.sendto(json.dumps(payload).encode(), (parts[0].strip("'"), int(parts[1])))

        # --- 2.2 CYBERPUNK BACKGROUND ENGINE ---
        if state.ACTIVE_HACKS.get("Cyberpunk BG", False):
            VIRTUAL_SURFACE.fill((10, 0, 30))
            offset = (pygame.time.get_ticks() // 15) % 50
            for y in range(0, SCREEN_HEIGHT, 50):
                pygame.draw.line(VIRTUAL_SURFACE, (255, 0, 255), (0, y + offset), (SCREEN_WIDTH, y + offset), 1)
            for x in range(0, SCREEN_WIDTH, 50):
                pygame.draw.line(VIRTUAL_SURFACE, (0, 255, 255), (x, 0), (x, SCREEN_HEIGHT), 1)
        else:
            VIRTUAL_SURFACE.fill(BLACK)
            ui.draw_stars(VIRTUAL_SURFACE) 
        
        # --- PARTICLE RENDERER ---
        for p in reversed(state.particle_list):
            if not state.ACTIVE_HACKS.get("Freeze Time", False) and not state.ACTIVE_HACKS.get("Reverse Time", False):
                p[0] += p[2]
                p[1] += p[3]
                p[4] -= 1
            elif state.ACTIVE_HACKS.get("Reverse Time", False):
                p[0] -= p[2]
                p[1] -= p[3]
                p[4] += 1
                if p[4] > p[5]: p[4] = p[5]
                
            if p[4] <= 0:
                state.particle_list.remove(p)
            else:
                alpha = int((p[4] / p[5]) * 255)
                s = pygame.Surface((6, 6), pygame.SRCALPHA)
                pygame.draw.circle(s, (*p[6][:3], alpha), (3, 3), 3)
                VIRTUAL_SURFACE.blit(s, (int(p[0]) - 3, int(p[1]) - 3))

        for sprite in all_sprites:
            if isinstance(sprite, Player): 
                sprite.draw(VIRTUAL_SURFACE)
            else: 
                VIRTUAL_SURFACE.blit(sprite.image, sprite.rect)
                
            if state.ACTIVE_HACKS.get("Show Hitboxes", False):
                pygame.draw.rect(VIRTUAL_SURFACE, RED, sprite.rect, 2)
                pygame.draw.circle(VIRTUAL_SURFACE, YELLOW, sprite.rect.center, 3)

        if boss:
            pygame.draw.rect(VIRTUAL_SURFACE, RED, (SCREEN_WIDTH//2 - 100, 20, 200, 20))
            pygame.draw.rect(VIRTUAL_SURFACE, WIN_GREEN, (SCREEN_WIDTH//2 - 100, 20, int(max(0, boss.health)/boss.max_health * 200), 20))

        ui.draw_text(f"P1 Score: {players[1].score}", FONT_MEDIUM, PLAYER_COLORS[0], 120, 20, VIRTUAL_SURFACE)
        ui.draw_text(f"Level: {state.level}", FONT_MEDIUM, YELLOW, SCREEN_WIDTH // 2, 55, VIRTUAL_SURFACE)
        
        # --- 2.2 CAMERA RENDER PIPELINE ---
        if state.ACTIVE_HACKS.get("Force Screen Shake", False):
            state.CAMERA_SHAKE = 20
            state.ACTIVE_HACKS["Force Screen Shake"] = False

        if state.ACTIVE_HACKS.get("Cinematic Zoom", False):
            state.CAMERA_ZOOM = min(1.5, state.CAMERA_ZOOM + 0.01)
        else:
            state.CAMERA_ZOOM = max(1.0, state.CAMERA_ZOOM - 0.05)

        if state.ACTIVE_HACKS.get("Rotate Screen", False):
            state.CAMERA_ANGLE = (state.CAMERA_ANGLE + 1) % 360
        else:
            state.CAMERA_ANGLE = 0

        if state.CAMERA_SHAKE > 0:
            state.CAMERA_SHAKE -= 1

        shake_x = random.randint(-state.CAMERA_SHAKE, state.CAMERA_SHAKE) if state.CAMERA_SHAKE > 0 else 0
        shake_y = random.randint(-state.CAMERA_SHAKE, state.CAMERA_SHAKE) if state.CAMERA_SHAKE > 0 else 0

        # CHROMATIC ABERRATION (RGB SPLIT)
        if state.ACTIVE_HACKS.get("Chromatic Aberration", False):
            surf_r = VIRTUAL_SURFACE.copy()
            surf_r.fill((255, 0, 0), special_flags=pygame.BLEND_RGB_MULT)
            surf_b = VIRTUAL_SURFACE.copy()
            surf_b.fill((0, 0, 255), special_flags=pygame.BLEND_RGB_MULT)
            surf_g = VIRTUAL_SURFACE.copy()
            surf_g.fill((0, 255, 0), special_flags=pygame.BLEND_RGB_MULT)

            VIRTUAL_SURFACE.fill(BLACK)
            VIRTUAL_SURFACE.blit(surf_r, (-6, 0), special_flags=pygame.BLEND_RGB_ADD)
            VIRTUAL_SURFACE.blit(surf_g, (0, 0), special_flags=pygame.BLEND_RGB_ADD)
            VIRTUAL_SURFACE.blit(surf_b, (6, 0), special_flags=pygame.BLEND_RGB_ADD)

        # APPLY ZOOM AND ROTATION TO FINAL CANVAS
        final_surf = VIRTUAL_SURFACE
        if state.CAMERA_ZOOM != 1.0 or state.CAMERA_ANGLE != 0:
            zoomed_w = int(SCREEN_WIDTH * state.CAMERA_ZOOM)
            zoomed_h = int(SCREEN_HEIGHT * state.CAMERA_ZOOM)
            final_surf = pygame.transform.scale(final_surf, (zoomed_w, zoomed_h))
            if state.CAMERA_ANGLE != 0:
                final_surf = pygame.transform.rotate(final_surf, state.CAMERA_ANGLE)

        offset_x = (SCREEN_WIDTH - final_surf.get_width()) // 2
        offset_y = (SCREEN_HEIGHT - final_surf.get_height()) // 2
        SCREEN.blit(final_surf, (offset_x + shake_x, offset_y + shake_y))

        megahack.draw(SCREEN)
        pygame.display.flip()
        CLOCK.tick(int(FPS * state.GAME_SPEED))
        
    return "GAME_OVER"

def main():
    state.load_game_progress()
    state.load_mod_config()
    state.load_audio_config()
    state.reload_mods()
    sound_manager.SoundManager.get_instance()
    sound_manager.play_music("menu_theme")
    
    while True:
        if state.game_state == "HOME":
            sound_manager.play_music("menu_theme")
            action = ui.show_home_screen(SCREEN, CLOCK)
            if action == "QUIT_PROGRAM": 
                break
            elif action == "PLAYING_SPINOFF": 
                state.game_state = "SPINOFF"
            elif action == "PASSWORD_SCREEN":
                if ui.show_password_screen(SCREEN, CLOCK) == "PLAYING_ULTIMATE_BOSS": 
                    state.game_state = "ULTIMATE_BOSS"
            elif action == "HOST_LAN_MENU":
                state.game_mode = network.host_infinite_lan(SCREEN, CLOCK, "MULTI_CLASSIC")
                if state.game_mode.startswith("LAN_HOST"): 
                    ui.show_instructions_screen(SCREEN, CLOCK, state.game_mode)
                    state.game_state = "PLAYING"
            elif action == "JOIN_LAN_MENU":
                state.game_mode = network.join_infinite_lan(SCREEN, CLOCK)
                if state.game_mode == "LAN_JOIN": 
                    ui.show_instructions_screen(SCREEN, CLOCK, state.game_mode)
                    state.game_state = "PLAYING"
            elif action == "HOST_CLOUD":
                network.udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                network.udp_sock.setblocking(False)
                state.game_mode = "HOST_CLOUD"
                ui.show_instructions_screen(SCREEN, CLOCK, state.game_mode)
                state.game_state = "PLAYING"
            elif action == "JOIN_CLOUD":
                state.game_mode = network.join_global_cloud(SCREEN, CLOCK)
                if state.game_mode == "JOIN_CLOUD": 
                    ui.show_instructions_screen(SCREEN, CLOCK, state.game_mode)
                    state.game_state = "PLAYING"
            elif action == "WEB_BROWSER": 
                ui.show_web_browser_screen(SCREEN, CLOCK)
            elif action == "STORE_P1": 
                ui.show_store_screen(SCREEN, CLOCK, "P1")
            elif action == "SELECT_SHIP_P1": 
                ui.show_ship_selection_screen(SCREEN, CLOCK, "P1")
            elif action == "STORE_P2": 
                ui.show_store_screen(SCREEN, CLOCK, "P2")
            elif action == "SELECT_SHIP_P2": 
                ui.show_ship_selection_screen(SCREEN, CLOCK, "P2")
            elif action == "AUDIO_SETTINGS":
                ui.show_audio_settings_screen(SCREEN, CLOCK)
            elif action == "MOD_LOADER": 
                ui.show_mod_loader_screen(SCREEN, CLOCK)
            elif action == "LEVEL_EDITOR": 
                run_level_editor(SCREEN)
            elif action == "ADMIN_PANEL": 
                ui.show_admin_options(SCREEN, CLOCK)
            elif action and action.startswith("PLAYING_"):
                state.game_mode = action.replace("PLAYING_", "")
                ui.show_instructions_screen(SCREEN, CLOCK, state.game_mode)
                state.game_state = "PLAYING"
                
        elif state.game_state == "PLAYING":
            if game_loop(state.game_mode) == "QUIT_PROGRAM": 
                break
            state.game_state = "GAME_OVER"
            
        elif state.game_state == "SPINOFF":
            if spinoff_game_loop() == "QUIT_PROGRAM": 
                break
            state.game_state = "HOME"
            
        elif state.game_state == "ULTIMATE_BOSS":
            if ultimate_boss_loop() == "QUIT_PROGRAM": 
                break
            state.game_state = "HOME"
            
        elif state.game_state == "GAME_OVER":
            if ui.show_game_over_screen(SCREEN, CLOCK, state.win_status, state.winning_player) == "HOME": 
                state.game_state = "HOME"
            else: 
                break
                
    pygame.quit()
    sys.exit()

if __name__ == "__main__": 
    main()