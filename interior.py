import pygame
import state


# Initialize astronaut position to center of Bridge if not set
if not hasattr(state, "astronaut_x"):
    state.astronaut_x = 400 # Will be updated dynamically based on screen width
    state.astronaut_y = 500

def update_and_draw_interior(screen):
    cw, ch = screen.get_width(), screen.get_height()
    
    NPCs = [
        {"name": "Co-Pilot", "room": (0, 0), "x": cw * 0.5, "y": ch * 0.65, "color": (100, 200, 100)},
        {"name": "Doctor", "room": (0, 1), "x": cw * 0.5, "y": ch * 0.5, "color": (255, 100, 100)},
        {"name": "Engineer", "room": (1, 0), "x": cw * 0.85, "y": ch * 0.5, "color": (200, 150, 50)},
    ]
    
    # Update initial position if it's the first time we know the screen size
    if getattr(state, "_init_astro", True):
        state.astronaut_x = cw // 2
        state.astronaut_y = int(ch * 0.8)
        state._init_astro = False

    keys = pygame.key.get_pressed()
    speed = 8
    
    if keys[pygame.K_LEFT] or keys[pygame.K_a]: state.astronaut_x -= speed
    if keys[pygame.K_RIGHT] or keys[pygame.K_d]: state.astronaut_x += speed
    if keys[pygame.K_UP] or keys[pygame.K_w]: state.astronaut_y -= speed
    if keys[pygame.K_DOWN] or keys[pygame.K_s]: state.astronaut_y += speed
    
    ax = state.astronaut_x
    ay = state.astronaut_y
    
    room_x = ax // cw
    room_y = ay // ch
    
    local_x = ax % cw
    local_y = ay % ch
    
    # Interaction logic
    if keys[pygame.K_RETURN] or keys[pygame.K_SPACE]:
        for npc in NPCs:
            if npc["room"] == (room_x, room_y):
                dist = ((local_x - npc["x"])**2 + (local_y - npc["y"])**2)**0.5
                if dist < 100:
                    if npc["name"] == "Co-Pilot":
                        # Toggle auto-pilot, with a debounce
                        if not getattr(state, "copilot_debounce", False):
                            state.ACTIVE_HACKS["Auto Pilot"] = not state.ACTIVE_HACKS.get("Auto Pilot", False)
                            state.copilot_debounce = True
                    # other interactions can go here
    else:
        state.copilot_debounce = False
    
    # Room boundaries enforcement
    if room_x < 0: state.astronaut_x = 0
    if room_x > 1: state.astronaut_x = 2 * cw - 1
    if room_y < 0: state.astronaut_y = 0
    if room_y > 1: state.astronaut_y = 2 * ch - 1
    
    ax = state.astronaut_x
    ay = state.astronaut_y
    room_x = ax // cw
    room_y = ay // ch
    local_x = ax % cw
    local_y = ay % ch

    # --- Physical Limitations ---
    # "you cant get on the screen" -> In Bridge, y must be >= ch * 0.6
    if room_x == 0 and room_y == 0:
        if local_y < ch * 0.6:
            state.astronaut_y = (ay // ch) * ch + ch * 0.6
            local_y = ch * 0.6
            
    # "cant get close to the engine" -> In Engine room, dist from center > 130
    if room_x == 1 and room_y == 0:
        dist_to_engine = ((local_x - cw/2)**2 + (local_y - ch/2)**2)**0.5
        if dist_to_engine < 140:
            # push out
            import math
            angle = math.atan2(local_y - ch/2, local_x - cw/2)
            local_x = cw/2 + math.cos(angle) * 140
            local_y = ch/2 + math.sin(angle) * 140
            state.astronaut_x = (ax // cw) * cw + local_x
            state.astronaut_y = (ay // ch) * ch + local_y

    # --- Render Room ---
    if room_x == 0 and room_y == 0:
        # BRIDGE
        # The game world (stars/enemies) is already rendered on `screen` beneath us.
        # We draw the interior walls over it, leaving a viewport hole.
        ccolor = (70, 80, 100) # More welcoming blue-grey metallic
        border_left, border_right = cw * 0.1, cw * 0.9
        border_top, border_bottom = ch * 0.1, ch * 0.6
        
        pygame.draw.rect(screen, ccolor, (0, 0, cw, border_top))
        pygame.draw.rect(screen, ccolor, (0, border_bottom, cw, ch - border_bottom))
        pygame.draw.rect(screen, ccolor, (0, border_top, border_left, border_bottom - border_top))
        pygame.draw.rect(screen, ccolor, (border_right, border_top, cw - border_right, border_bottom - border_top))
        
        # Viewport Frame
        pygame.draw.rect(screen, (200, 220, 240), (border_left, border_top, border_right - border_left, border_bottom - border_top), 8)
        
        # Consoles
        pygame.draw.rect(screen, (50, 60, 80), (border_left, border_bottom, border_right - border_left, ch * 0.15))
        pygame.draw.rect(screen, (40, 50, 70), (0, ch * 0.8, cw * 0.2, ch * 0.2)) # Left console
        pygame.draw.rect(screen, (40, 50, 70), (cw * 0.8, ch * 0.8, cw * 0.2, ch * 0.2)) # Right console
        
        # Doors
        pygame.draw.rect(screen, (30, 40, 50), (cw//2 - 80, ch - 20, 160, 20)) # South door to Medbay
        pygame.draw.rect(screen, (30, 40, 50), (cw - 20, ch//2 - 80, 20, 160)) # East door to Engine
        
        # Labels
        font = pygame.font.SysFont("Arial", 20, bold=True)
        txt = font.render("BRIDGE", True, (200, 255, 200))
        screen.blit(txt, (cw//2 - txt.get_width()//2, 10))

    elif room_x == 0 and room_y == 1:
        # MEDICAL BAY
        # Fill the whole screen so we don't see "the thing" (game viewport)
        screen.fill((220, 240, 255)) # Welcoming hospital white-blue
        pygame.draw.rect(screen, (180, 210, 230), (0, ch//2, cw, ch//2)) # Floor
        
        # Med bed
        pygame.draw.rect(screen, (255, 255, 255), (cw//2 - 120, ch//2 - 60, 240, 120), border_radius=15)
        pygame.draw.rect(screen, (200, 200, 200), (cw//2 - 110, ch//2 - 50, 80, 100), border_radius=10) # Pillow area
        
        # Red Cross Monitor
        pygame.draw.rect(screen, (50, 50, 50), (cw * 0.2, ch * 0.3, 100, 80), border_radius=5)
        pygame.draw.rect(screen, (255, 50, 50), (cw * 0.2 + 40, ch * 0.3 + 20, 20, 40))
        pygame.draw.rect(screen, (255, 50, 50), (cw * 0.2 + 30, ch * 0.3 + 30, 40, 20))
        
        # Door North
        pygame.draw.rect(screen, (150, 170, 190), (cw//2 - 80, 0, 160, 20))
        
        font = pygame.font.SysFont("Arial", 20, bold=True)
        txt = font.render("MEDICAL BAY", True, (100, 150, 200))
        screen.blit(txt, (cw//2 - txt.get_width()//2, 10))

    elif room_x == 1 and room_y == 0:
        # ENGINE ROOM
        screen.fill((70, 50, 50)) # Warm industrial
        pygame.draw.rect(screen, (50, 30, 30), (0, ch//2, cw, ch//2)) # Floor
        
        # Engine core
        import math
        pulse = abs(math.sin(pygame.time.get_ticks() / 500.0))
        pygame.draw.circle(screen, (200 + int(55 * pulse), 100, 0), (cw//2, ch//2), 120)
        pygame.draw.circle(screen, (255, 200 + int(55 * pulse), 0), (cw//2, ch//2), 90)
        pygame.draw.circle(screen, (255, 255, 255), (cw//2, ch//2), 40)
        
        # Machinery
        pygame.draw.rect(screen, (40, 40, 40), (cw * 0.8, ch * 0.2, cw * 0.2, ch * 0.6))
        
        # Door West
        pygame.draw.rect(screen, (30, 20, 20), (0, ch//2 - 80, 20, 160))
        
        font = pygame.font.SysFont("Arial", 20, bold=True)
        txt = font.render("ENGINE ROOM", True, (255, 200, 100))
        screen.blit(txt, (cw//2 - txt.get_width()//2, 10))

    else:
        screen.fill((0, 0, 0))

    # --- Draw NPCs ---
    for npc in NPCs:
        if npc["room"] == (room_x, room_y):
            nx = npc["x"]
            ny = npc["y"]
            pygame.draw.rect(screen, npc["color"], (nx - 15, ny, 30, 40), border_radius=10) # Body
            pygame.draw.circle(screen, (255, 220, 180), (nx, ny - 10), 20) # Head
            
            font = pygame.font.SysFont("Arial", 16, bold=True)
            txt = font.render(npc["name"], True, (255, 255, 255))
            screen.blit(txt, (nx - txt.get_width()//2, ny - 45))
            
            if npc["name"] == "Co-Pilot":
                status = "AUTO-PILOT ACTIVE" if state.ACTIVE_HACKS.get("Auto Pilot", False) else "Press SPACE to takeover"
                scolor = (100, 255, 100) if state.ACTIVE_HACKS.get("Auto Pilot", False) else (200, 200, 200)
                txt2 = font.render(status, True, scolor)
                screen.blit(txt2, (nx - txt2.get_width()//2, ny + 45))

    # --- Draw Astronaut (Player) ---
    px = local_x
    py = local_y
    pygame.draw.rect(screen, (220, 220, 220), (px - 15, py, 30, 40), border_radius=10) # Body
    pygame.draw.circle(screen, (255, 255, 255), (px, py - 10), 20) # Head
    pygame.draw.rect(screen, (0, 200, 255), (px - 10, py - 20, 20, 15), border_radius=5) # Visor

    # "if i go forwrd enogh isee my ship"
    # If in the Bridge and walking close to the window (y < ch * 0.6)
    if room_x == 0 and room_y == 0 and local_y < ch * 0.65:
        state.astronaut_near_window = True
    else:
        state.astronaut_near_window = False
