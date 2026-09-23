import pygame
from settings import *
import state
import sound_manager

def draw_text(text, font, color, x, y, surface, align="center"):
    text_surface = font.render(text, True, color)
    rect = text_surface.get_rect()
    if align == "center":
        rect.center = (x, y)
    elif align == "left":
        rect.midleft = (x, y)
    surface.blit(text_surface, rect)

def apply_instant_hacks(hack):
    if hack == "Infinite Credits":
        state.all_player_data["P1"]["credits"] = 999999
    elif hack == "Unlock All Ships":
        for k in state.SHIP_TYPES:
            if k not in state.all_player_data["P1"]["owned_ships"]:
                state.all_player_data["P1"]["owned_ships"].append(k)
    elif hack == "Unlock All Helpers":
        for k in state.HELPER_TYPES:
            if k not in state.all_player_data["P1"]["unlocked_powers"]:
                state.all_player_data["P1"]["unlocked_powers"].append(k)

def handle_event(event):
    """GLOBAL HOOK: Call this first in EVERY event loop!"""
    if event.type == pygame.KEYDOWN and event.key == pygame.K_TAB:
        state.CHEAT_MENU_VISIBLE = not state.CHEAT_MENU_VISIBLE
        sound_manager.play_sfx("hack_toggle")
        return True 

    if not state.CHEAT_MENU_VISIBLE: 
        return False

    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
        mouse_pos = pygame.mouse.get_pos()
        menu_w, menu_h = 700, 500
        menu_x = SCREEN_WIDTH // 2 - menu_w // 2
        menu_y = SCREEN_HEIGHT // 2 - menu_h // 2
        
        # Clicked Tabs?
        tab_w = 180
        for i, category in enumerate(state.MEGAHACK_CATEGORIES.keys()):
            tab_rect = pygame.Rect(menu_x, menu_y + 50 + (i * 50), tab_w, 50)
            if tab_rect.collidepoint(mouse_pos):
                state.MH_ACTIVE_TAB = category
                sound_manager.play_sfx("ui_click")
                return True
                
        # Clicked Hacks?
        hack_x = menu_x + tab_w + 30
        hacks = state.MEGAHACK_CATEGORIES[state.MH_ACTIVE_TAB]
        for i, hack in enumerate(hacks):
            row = i % 8
            col = i // 8
            hack_rect = pygame.Rect(hack_x + (col * 240), menu_y + 60 + (row * 50), 200, 30)
            if hack_rect.collidepoint(mouse_pos):
                # Handle Speedhack exclusivity
                if "Speedhack" in hack:
                    for sh in state.MEGAHACK_CATEGORIES["Variables"]: 
                        state.ACTIVE_HACKS[sh] = False
                    
                    if "x0.5" in hack: state.GAME_SPEED = 0.5
                    elif "x1.0" in hack: state.GAME_SPEED = 1.0
                    elif "x2.0" in hack: state.GAME_SPEED = 2.0
                    elif "x5.0" in hack: state.GAME_SPEED = 5.0
                    
                    state.ACTIVE_HACKS[hack] = True
                else:
                    state.ACTIVE_HACKS[hack] = not state.ACTIVE_HACKS[hack]
                    apply_instant_hacks(hack)
                sound_manager.play_sfx("hack_toggle")
                return True
        return True 
    return False

def draw(screen):
    if not state.CHEAT_MENU_VISIBLE: 
        return
        
    bg_color = (25, 25, 25, 240)
    panel_color = (40, 40, 40, 255)
    accent_color = (0, 168, 243) # GD Mega Hack Blue
    text_off = (150, 150, 150)
    
    menu_w, menu_h = 700, 500
    menu_x = SCREEN_WIDTH // 2 - menu_w // 2
    menu_y = SCREEN_HEIGHT // 2 - menu_h // 2
    
    # Dim screen
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 150))
    screen.blit(overlay, (0, 0))
    
    # Main Panel
    panel = pygame.Surface((menu_w, menu_h), pygame.SRCALPHA)
    panel.fill(bg_color)
    screen.blit(panel, (menu_x, menu_y))
    
    # Top Bar
    pygame.draw.rect(screen, accent_color, (menu_x, menu_y, menu_w, 40))
    draw_text("Mega Hack v7.1", FONT_MEDIUM, WHITE, menu_x + 10, menu_y + 20, screen, align="left")
    
    # Draw Tabs (Left Column)
    tab_w = 180
    pygame.draw.rect(screen, panel_color, (menu_x, menu_y + 40, tab_w, menu_h - 40))
    
    for i, category in enumerate(state.MEGAHACK_CATEGORIES.keys()):
        tab_y = menu_y + 50 + (i * 50)
        is_active = (state.MH_ACTIVE_TAB == category)
        if is_active:
            pygame.draw.rect(screen, (50, 50, 50), (menu_x, tab_y, tab_w, 50))
            pygame.draw.rect(screen, accent_color, (menu_x, tab_y, 4, 50))
        draw_text(category, FONT_MEDIUM, WHITE if is_active else text_off, menu_x + 20, tab_y + 25, screen, align="left")

    # Draw Hacks (Right Column)
    hack_x = menu_x + tab_w + 30
    hacks = state.MEGAHACK_CATEGORIES[state.MH_ACTIVE_TAB]
    
    for i, hack in enumerate(hacks):
        row = i % 8
        col = i // 8
        hx = hack_x + (col * 240)
        hy = menu_y + 60 + (row * 50)
        
        is_on = state.ACTIVE_HACKS[hack]
        
        # Modern Checkbox
        box_rect = pygame.Rect(hx, hy, 24, 24)
        pygame.draw.rect(screen, accent_color if is_on else (60, 60, 60), box_rect, border_radius=4)
        if is_on: 
            draw_text("✓", FONT_SMALL, WHITE, box_rect.centerx, box_rect.centery, screen)
        
        draw_text(hack, FONT_SMALL, WHITE if is_on else text_off, hx + 35, hy + 12, screen, align="left")