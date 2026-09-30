import pygame
import math
import state


# Initialize astronaut position to center of Bridge if not set
if not hasattr(state, "astronaut_x"):
    state.astronaut_x = 400
    state.astronaut_y = 500

# Secret Konami Code: Up Up Down Down Left Right Left Right B A
_SECRET_CODE = [
    pygame.K_UP, pygame.K_UP, pygame.K_DOWN, pygame.K_DOWN,
    pygame.K_LEFT, pygame.K_RIGHT, pygame.K_LEFT, pygame.K_RIGHT,
    pygame.K_b, pygame.K_a,
]
_code_progress = []
_prev_keys = set()

if not hasattr(state, "dev_unlocked"):
    state.dev_unlocked = False
if not hasattr(state, "dev_reward_claimed"):
    state.dev_reward_claimed = False


def update_and_draw_interior(screen):
    cw, ch = screen.get_width(), screen.get_height()

    NPCs = [
        {"name": "Co-Pilot", "room": (0, 0), "x": cw * 0.5, "y": ch * 0.78, "color": (100, 200, 100)},
        {"name": "Doctor", "room": (0, 1), "x": cw * 0.5, "y": ch * 0.5, "color": (255, 100, 100)},
        {"name": "Engineer", "room": (1, 0), "x": cw * 0.85, "y": ch * 0.5, "color": (200, 150, 50)},
        {"name": "Creator", "room": (-1, 0), "x": cw * 0.5, "y": ch * 0.5, "color": (255, 255, 255)},
    ]

    # Update initial position if it's the first time we know the screen size
    if getattr(state, "_init_astro", True):
        state.astronaut_x = cw // 2
        state.astronaut_y = int(ch * 0.85)
        state._init_astro = False

    keys = pygame.key.get_pressed()
    speed = 8

    # --- Secret code detection (track key PRESSES, not holds) ---
    global _code_progress, _prev_keys
    current_keys = set()
    for k in [pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT,
              pygame.K_a, pygame.K_b]:
        if keys[k]:
            current_keys.add(k)

    # Detect newly pressed keys (not held from last frame)
    new_presses = current_keys - _prev_keys
    _prev_keys = current_keys.copy()

    for k in new_presses:
        if len(_code_progress) < len(_SECRET_CODE):
            expected = _SECRET_CODE[len(_code_progress)]
            if k == expected:
                _code_progress.append(k)
                # Check if complete
                if len(_code_progress) == len(_SECRET_CODE):
                    state.dev_unlocked = True
                    state._dev_unlock_time = pygame.time.get_ticks()
            else:
                _code_progress = []

    # Movement
    if keys[pygame.K_LEFT] or keys[pygame.K_a]:
        state.astronaut_x -= speed
    if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
        state.astronaut_x += speed
    if keys[pygame.K_UP] or keys[pygame.K_w]:
        state.astronaut_y -= speed
    if keys[pygame.K_DOWN] or keys[pygame.K_s]:
        state.astronaut_y += speed

    # --- Compute room and local coords ---
    ax = state.astronaut_x
    ay = state.astronaut_y

    room_x = ax // cw
    room_y = ay // ch
    local_x = ax % cw
    local_y = ay % ch

    # --- Interaction logic ---
    if keys[pygame.K_RETURN] or keys[pygame.K_SPACE]:
        for npc in NPCs:
            if npc["room"] == (room_x, room_y):
                dist = ((local_x - npc["x"])**2 + (local_y - npc["y"])**2)**0.5
                if dist < 100:
                    if npc["name"] == "Co-Pilot":
                        if not getattr(state, "copilot_debounce", False):
                            state.ACTIVE_HACKS["Auto Pilot"] = not state.ACTIVE_HACKS.get("Auto Pilot", False)
                            state.copilot_debounce = True
    else:
        state.copilot_debounce = False

    # === WORLD BOUNDARIES ===
    # The valid rooms form an L-shape:
    #   (-1,0)  (0,0)  (1,0)
    #           (0,1)
    #
    # Dev lounge (-1,0) is secret — only accessible while holding tilde key.

    dev_access = state.dev_unlocked

    # Top boundary: no rooms above row 0
    if ay < 0:
        state.astronaut_y = 0

    # Bottom boundary: only (0,1) exists in row 1
    if room_y > 1:
        state.astronaut_y = 2 * ch - 1
    # If in row 1 but not column 0, push back
    if room_y == 1 and room_x != 0:
        if room_x > 0:
            state.astronaut_x = cw - 1
        else:
            state.astronaut_x = 0

    # Right boundary: no rooms past column 1
    if room_x > 1:
        state.astronaut_x = 2 * cw - 1
    # If in column 1 but row != 0, push back
    if room_x == 1 and room_y != 0:
        state.astronaut_y = ch - 1

    # Left boundary: column -1 is dev lounge (secret, requires Konami code)
    if not dev_access:
        # Not unlocked — hard wall at x=0
        if state.astronaut_x < 0:
            state.astronaut_x = 0
    else:
        # Unlocked — allow dev lounge but not further left
        if room_x < -1:
            state.astronaut_x = -cw
        # Dev lounge only exists at row 0
        if room_x == -1 and room_y != 0:
            state.astronaut_y = ch - 1 if room_y > 0 else 0

    # --- Recompute after boundary clamping ---
    ax = state.astronaut_x
    ay = state.astronaut_y
    room_x = ax // cw
    room_y = ay // ch
    local_x = ax % cw
    local_y = ay % ch

    # === ROOM-SPECIFIC COLLISION ===

    # Bridge (0,0): can't walk onto the viewport window (top portion)
    if room_x == 0 and room_y == 0:
        # The viewport + console occupies the top 75% of the room
        # Player is restricted to below the console
        min_y = ch * 0.75
        if local_y < min_y:
            local_y = min_y
            state.astronaut_y = room_y * ch + local_y

    # Engine Room (1,0): can't walk into the engine core
    if room_x == 1 and room_y == 0:
        cx, cy = cw / 2, ch / 2
        dist_to_engine = ((local_x - cx)**2 + (local_y - cy)**2)**0.5
        if dist_to_engine < 140:
            angle = math.atan2(local_y - cy, local_x - cx)
            local_x = cx + math.cos(angle) * 140
            local_y = cy + math.sin(angle) * 140
            state.astronaut_x = room_x * cw + local_x
            state.astronaut_y = room_y * ch + local_y

    # Recompute one more time for rendering
    ax = state.astronaut_x
    ay = state.astronaut_y
    room_x = ax // cw
    room_y = ay // ch
    local_x = ax % cw
    local_y = ay % ch

    # === RENDER ROOM ===

    if room_x == 0 and room_y == 0:
        # --- BRIDGE ---
        ccolor = (70, 80, 100)
        floor_color = (40, 45, 55)
        vp_left, vp_right = cw * 0.1, cw * 0.9
        vp_top, vp_bottom = cw * 0.05, ch * 0.55

        # Floor (bottom portion)
        pygame.draw.rect(screen, floor_color, (0, ch * 0.55, cw, ch * 0.45))

        # Walls around viewport
        pygame.draw.rect(screen, ccolor, (0, 0, cw, vp_top))                          # Top wall
        pygame.draw.rect(screen, ccolor, (0, vp_top, vp_left, vp_bottom - vp_top))    # Left wall
        pygame.draw.rect(screen, ccolor, (vp_right, vp_top, cw - vp_right, vp_bottom - vp_top))  # Right wall

        # Console panel below viewport
        pygame.draw.rect(screen, (50, 60, 80), (vp_left, vp_bottom, vp_right - vp_left, ch * 0.2))

        # Viewport frame
        pygame.draw.rect(screen, (200, 220, 240), (vp_left, vp_top, vp_right - vp_left, vp_bottom - vp_top), 8)

        # Side consoles
        pygame.draw.rect(screen, (40, 50, 70), (0, ch * 0.8, cw * 0.15, ch * 0.2))
        pygame.draw.rect(screen, (40, 50, 70), (cw * 0.85, ch * 0.8, cw * 0.15, ch * 0.2))

        # Door markers
        pygame.draw.rect(screen, (100, 255, 100), (cw // 2 - 50, ch - 10, 100, 10))    # South -> Medbay
        pygame.draw.rect(screen, (255, 200, 100), (cw - 10, ch // 2 + 60, 10, 100))     # East -> Engine

        font = pygame.font.SysFont("Arial", 20, bold=True)
        screen.blit(font.render("BRIDGE", True, (200, 255, 200)), (cw // 2 - 35, vp_top - 2))

        # Door labels
        font_sm = pygame.font.SysFont("Arial", 14)
        t1 = font_sm.render("v MEDBAY v", True, (100, 255, 100))
        screen.blit(t1, (cw // 2 - t1.get_width() // 2, ch - 25))
        t2 = font_sm.render("ENGINE >", True, (255, 200, 100))
        screen.blit(t2, (cw - t2.get_width() - 15, ch // 2 + 50))

    elif room_x == 0 and room_y == 1:
        # --- MEDICAL BAY ---
        screen.fill((220, 240, 255))
        pygame.draw.rect(screen, (180, 210, 230), (0, ch // 2, cw, ch // 2))

        # Med bed
        pygame.draw.rect(screen, (255, 255, 255), (cw // 2 - 120, ch // 2 - 60, 240, 120), border_radius=15)
        pygame.draw.rect(screen, (200, 200, 200), (cw // 2 - 110, ch // 2 - 50, 80, 100), border_radius=10)

        # Red Cross Monitor
        pygame.draw.rect(screen, (50, 50, 50), (int(cw * 0.2), int(ch * 0.3), 100, 80), border_radius=5)
        pygame.draw.rect(screen, (255, 50, 50), (int(cw * 0.2) + 40, int(ch * 0.3) + 20, 20, 40))
        pygame.draw.rect(screen, (255, 50, 50), (int(cw * 0.2) + 30, int(ch * 0.3) + 30, 40, 20))

        # Door North
        pygame.draw.rect(screen, (100, 255, 100), (cw // 2 - 50, 0, 100, 10))

        font = pygame.font.SysFont("Arial", 20, bold=True)
        screen.blit(font.render("MEDICAL BAY", True, (100, 150, 200)), (cw // 2 - 60, 15))

        font_sm = pygame.font.SysFont("Arial", 14)
        t1 = font_sm.render("^ BRIDGE ^", True, (100, 255, 100))
        screen.blit(t1, (cw // 2 - t1.get_width() // 2, 12))

    elif room_x == 1 and room_y == 0:
        # --- ENGINE ROOM ---
        screen.fill((70, 50, 50))
        pygame.draw.rect(screen, (50, 30, 30), (0, ch // 2, cw, ch // 2))

        # Engine core (pulsing)
        pulse = abs(math.sin(pygame.time.get_ticks() / 500.0))
        pygame.draw.circle(screen, (200 + int(55 * pulse), 100, 0), (cw // 2, ch // 2), 120)
        pygame.draw.circle(screen, (255, 200 + int(55 * pulse), 0), (cw // 2, ch // 2), 90)
        pygame.draw.circle(screen, (255, 255, 255), (cw // 2, ch // 2), 40)

        # Machinery
        pygame.draw.rect(screen, (40, 40, 40), (int(cw * 0.8), int(ch * 0.2), int(cw * 0.2), int(ch * 0.6)))

        # Door West
        pygame.draw.rect(screen, (100, 255, 100), (0, ch // 2 - 50, 10, 100))

        font = pygame.font.SysFont("Arial", 20, bold=True)
        screen.blit(font.render("ENGINE ROOM", True, (255, 200, 100)), (cw // 2 - 60, 10))

        font_sm = pygame.font.SysFont("Arial", 14)
        t1 = font_sm.render("< BRIDGE", True, (100, 255, 100))
        screen.blit(t1, (15, ch // 2 - 60))

    elif room_x == -1 and room_y == 0:
        # --- DEVELOPER LOUNGE (SECRET) ---

        # Grant reward on first visit!
        if not state.dev_reward_claimed:
            state.dev_reward_claimed = True
            state.SCORE = getattr(state, "SCORE", 0) + 5000
            state.LIVES = getattr(state, "LIVES", 3) + 3
            state.ACTIVE_HACKS["Infinite Ammo"] = True
            state._reward_time = pygame.time.get_ticks()

        screen.fill((20, 10, 30))
        pygame.draw.rect(screen, (40, 20, 60), (0, ch // 2, cw, ch // 2))

        # Starry ceiling effect
        import random
        rng = random.Random(42)  # fixed seed so stars don't flicker
        for _ in range(50):
            sx = rng.randint(0, cw)
            sy = rng.randint(0, ch // 2)
            brightness = rng.randint(150, 255)
            pygame.draw.circle(screen, (brightness, brightness, brightness), (sx, sy), rng.randint(1, 3))

        font = pygame.font.SysFont("Arial", 36, bold=True)
        # Rainbow pulsing title
        t = pygame.time.get_ticks() / 1000.0
        r = int(127 + 128 * math.sin(t * 2))
        g = int(127 + 128 * math.sin(t * 2 + 2))
        b = int(127 + 128 * math.sin(t * 2 + 4))
        txt = font.render("SECRET DEVELOPER LOUNGE", True, (r, g, b))
        screen.blit(txt, (cw // 2 - txt.get_width() // 2, 50))

        font2 = pygame.font.SysFont("Arial", 20)
        txt2 = font2.render("Thank you for helping develop Galactic Defenders!", True, (200, 255, 200))
        screen.blit(txt2, (cw // 2 - txt2.get_width() // 2, 110))

        # Reward display
        font3 = pygame.font.SysFont("Arial", 18, bold=True)
        rewards = [
            "REWARDS CLAIMED:",
            "+5000 Score",
            "+3 Extra Lives",
            "Infinite Ammo Unlocked!",
        ]
        for i, line in enumerate(rewards):
            color = (255, 215, 0) if i == 0 else (200, 255, 200)
            rt = font3.render(line, True, color)
            screen.blit(rt, (cw // 2 - rt.get_width() // 2, 155 + i * 25))

        # Golden Arcade Cabinet
        pygame.draw.rect(screen, (200, 150, 0), (cw // 2 - 40, ch // 2 + 20, 80, 120), border_radius=5)
        pygame.draw.rect(screen, (0, 0, 0), (cw // 2 - 30, ch // 2 + 30, 60, 40))
        pygame.draw.circle(screen, (255, 0, 0), (cw // 2 - 10, ch // 2 + 90), 10)
        pygame.draw.circle(screen, (0, 255, 0), (cw // 2 + 20, ch // 2 + 95), 5)

        # Door East (back to Bridge)
        pygame.draw.rect(screen, (100, 255, 100), (cw - 10, ch // 2 - 50, 10, 100))

        font_sm = pygame.font.SysFont("Arial", 14)
        t1 = font_sm.render("BRIDGE >", True, (100, 255, 100))
        screen.blit(t1, (cw - t1.get_width() - 15, ch // 2 - 60))

    else:
        screen.fill((0, 0, 0))

    # === DRAW NPCs ===
    for npc in NPCs:
        if npc["room"] == (room_x, room_y):
            nx = int(npc["x"])
            ny = int(npc["y"])
            pygame.draw.rect(screen, npc["color"], (nx - 15, ny, 30, 40), border_radius=10)
            pygame.draw.circle(screen, (255, 220, 180), (nx, ny - 10), 20)

            font = pygame.font.SysFont("Arial", 16, bold=True)
            txt = font.render(npc["name"], True, (255, 255, 255))
            screen.blit(txt, (nx - txt.get_width() // 2, ny - 45))

            if npc["name"] == "Co-Pilot":
                active = state.ACTIVE_HACKS.get("Auto Pilot", False)
                status = "AUTO-PILOT ACTIVE" if active else "Press SPACE to takeover"
                scolor = (100, 255, 100) if active else (200, 200, 200)
                txt2 = font.render(status, True, scolor)
                screen.blit(txt2, (nx - txt2.get_width() // 2, ny + 45))

    # === DRAW ASTRONAUT (Player) ===
    px = int(local_x)
    py = int(local_y)
    pygame.draw.rect(screen, (220, 220, 220), (px - 15, py, 30, 40), border_radius=10)
    pygame.draw.circle(screen, (255, 255, 255), (px, py - 10), 20)
    pygame.draw.rect(screen, (0, 200, 255), (px - 10, py - 20, 20, 15), border_radius=5)

    # Set flag for main.py to show ship in viewport
    if room_x == 0 and room_y == 0 and local_y < ch * 0.85:
        state.astronaut_near_window = True
    else:
        state.astronaut_near_window = False

    # === HUD: Secret code unlock notification ===
    unlock_time = getattr(state, "_dev_unlock_time", 0)
    if unlock_time and pygame.time.get_ticks() - unlock_time < 3000:
        # Golden flash notification
        alpha = max(0, 255 - int((pygame.time.get_ticks() - unlock_time) / 3000 * 255))
        overlay = pygame.Surface((cw, 60), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, min(180, alpha)))
        screen.blit(overlay, (0, ch // 2 - 30))

        font_big = pygame.font.SysFont("Arial", 28, bold=True)
        msg = font_big.render("SECRET PASSAGE UNLOCKED!", True, (255, 215, 0))
        screen.blit(msg, (cw // 2 - msg.get_width() // 2, ch // 2 - 25))

        font_hint = pygame.font.SysFont("Arial", 16)
        hint = font_hint.render("Walk through the left wall of the Bridge...", True, (200, 200, 200))
        screen.blit(hint, (cw // 2 - hint.get_width() // 2, ch // 2 + 5))

    # === HUD: Code progress indicator (subtle) ===
    progress = len(_code_progress)
    if 0 < progress < len(_SECRET_CODE) and not state.dev_unlocked:
        for i in range(progress):
            pygame.draw.circle(screen, (255, 215, 0), (cw - 20 - i * 15, 20), 5)

