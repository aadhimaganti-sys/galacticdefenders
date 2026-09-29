import math
import random
import pygame
from settings import SCREEN_WIDTH, SCREEN_HEIGHT, FONT_SMALL, FONT_MEDIUM, CYAN, YELLOW, RED, WIN_GREEN, WHITE, LIGHT_GRAY

class AIAgentState:
    MODES = ["BALANCED", "COMBAT", "SURVIVAL"]
    
    def __init__(self):
        self.mode_index = 0
        self.mode = "BALANCED"
        self.goal = "SCANNING SECTOR"
        self.locked_target = None
        self.danger_level = 0.0
        self.locked_target_rect = None
        self.reticle_angle = 0
        self.stats = {
            "dodges": 0,
            "powerups_collected": 0,
            "shots_fired": 0,
        }

    def cycle_mode(self):
        self.mode_index = (self.mode_index + 1) % len(self.MODES)
        self.mode = self.MODES[self.mode_index]
        return self.mode

# Global AI state instance for telemetry and HUD rendering
ai_state = AIAgentState()

class AdvancedAutoPilot:
    @staticmethod
    def get_state():
        return ai_state

    @staticmethod
    def cycle_mode():
        return ai_state.cycle_mode()

    @staticmethod
    def run(player, all_sprites, player_bullets, asteroids=None, drones=None, powerups=None, enemy_bullets=None, boss=None):
        """
        Handbuilt AI Flight Controller & Tactical Combat Engine.
        Uses multi-vector threat raycasting, predictive lead shooting,
        potential field evasive steering, and priority goal selection.
        """
        if not player or not hasattr(player, 'rect'):
            return

        asts = list(asteroids) if asteroids else []
        drns = list(drones) if drones else []
        pwrs = list(powerups) if powerups else []
        ebullets = list(enemy_bullets) if enemy_bullets else []
        
        px = player.rect.centerx
        py = player.rect.centery
        base_speed = getattr(player, 'base_speed', 7)

        # --- 1. MULTI-FRAME HAZARD VECTOR TRAJECTORY PREDICTION ---
        hazards = asts + drns + ebullets
        if boss and getattr(boss, 'alive', lambda: True)():
            hazards.append(boss)

        repulsion_x = 0.0
        total_threat = 0.0
        closest_hazard = None
        closest_hazard_dist = 9999.0

        for h in hazards:
            if not hasattr(h, 'rect'):
                continue
            hx = h.rect.centerx
            hy = h.rect.centery

            vx = getattr(h, 'speed_x', 0)
            vy = getattr(h, 'speed_y', 5)
            if vy == 0 and hx == px and hy == py:
                vy = 5

            # Forecast future positions over t = 1..15 frames
            for t in range(1, 16):
                future_hx = hx + vx * t
                future_hy = hy + vy * t

                dx = px - future_hx
                dy = py - future_hy
                dist = math.hypot(dx, dy)

                if dist < closest_hazard_dist:
                    closest_hazard_dist = dist
                    closest_hazard = h

                # Threat zone check
                if dist < 180 and -150 < (future_hy - py) < 150:
                    weight = (180 - dist) / 180.0
                    total_threat += weight * 0.15
                    direction = 1.0 if dx >= 0 else -1.0
                    repulsion_x += direction * (weight ** 1.5) * base_speed * 3.0

        ai_state.danger_level = min(1.0, total_threat)

        # --- 2. PRIORITY TARGET SELECTION ENGINE ---
        target_obj = None
        target_goal = "SCANNING SECTOR"
        
        if ai_state.mode == "SURVIVAL":
            if pwrs:
                target_obj = min(pwrs, key=lambda p: math.hypot(p.rect.centerx - px, p.rect.centery - py))
                target_goal = "COLLECTING POWERUP (SURVIVAL)"
            elif asts:
                target_obj = min(asts, key=lambda a: math.hypot(a.rect.centerx - px, a.rect.centery - py))
                target_goal = "CLEARING ASTEROID PATH"
        elif ai_state.mode == "COMBAT":
            if boss and getattr(boss, 'alive', lambda: True)():
                target_obj = boss
                target_goal = "HUNTER LOCK: BOSS"
            elif drns:
                target_obj = min(drns, key=lambda d: math.hypot(d.rect.centerx - px, d.rect.centery - py))
                target_goal = "HUNTER LOCK: DRONE"
            elif asts:
                target_obj = min(asts, key=lambda a: math.hypot(a.rect.centerx - px, a.rect.centery - py))
                target_goal = "TARGETING ASTEROIDS"
            elif pwrs:
                target_obj = min(pwrs, key=lambda p: math.hypot(p.rect.centerx - px, p.rect.centery - py))
                target_goal = "RECOVERY: POWERUP"
        else: # BALANCED
            if pwrs:
                target_obj = min(pwrs, key=lambda p: math.hypot(p.rect.centerx - px, p.rect.centery - py))
                target_goal = "COLLECTING POWERUP"
            elif boss and getattr(boss, 'alive', lambda: True)():
                target_obj = boss
                target_goal = "TARGETING BOSS"
            elif drns:
                target_obj = min(drns, key=lambda d: math.hypot(d.rect.centerx - px, d.rect.centery - py))
                target_goal = "TARGETING DRONE"
            elif asts:
                in_front = [a for a in asts if a.rect.bottom < player.rect.top + 100]
                if in_front:
                    target_obj = min(in_front, key=lambda a: math.hypot(a.rect.centerx - px, a.rect.centery - py))
                    target_goal = "CLEARING FRONT PATH"

        # --- 3. PREDICTIVE AIMING & SMOOTH STEERING ---
        target_x = px
        if target_obj and hasattr(target_obj, 'rect'):
            ai_state.locked_target = target_obj
            ai_state.locked_target_rect = target_obj.rect.copy()
            target_vx = getattr(target_obj, 'speed_x', 0)
            lead_frames = min(10, abs(target_obj.rect.centery - py) / 15.0)
            target_x = target_obj.rect.centerx + target_vx * lead_frames
        else:
            ai_state.locked_target = None
            ai_state.locked_target_rect = None

        if ai_state.danger_level > 0.35:
            target_goal = f"🚨 EVADING HAZARDS ({int(ai_state.danger_level*100)}% Threat)"
            ai_state.stats["dodges"] += 1

        ai_state.goal = target_goal

        # Combine Target Pull + Evasive Push Forces
        if abs(repulsion_x) > 0.1:
            desired_speed_x = max(-base_speed * 1.8, min(base_speed * 1.8, repulsion_x))
        else:
            diff_x = target_x - px
            desired_speed_x = max(-base_speed * 1.4, min(base_speed * 1.4, diff_x * 0.12))

        player.speed_x = desired_speed_x
        player.speed_y = 0

        # Boundary enforcement
        if px < 40 and player.speed_x < 0:
            player.speed_x = base_speed * 0.8
        elif px > SCREEN_WIDTH - 40 and player.speed_x > 0:
            player.speed_x = -base_speed * 0.8

        # --- 4. TACTICAL AUTO-FIRING ---
        align_diff = abs((target_obj.rect.centerx if target_obj else px) - px)
        if target_obj or closest_hazard or align_diff < 120:
            player.shoot(all_sprites, player_bullets)
            ai_state.stats["shots_fired"] += 1

    @staticmethod
    def draw_hud(surface):
        """Renders Handbuilt AI Autopilot HUD badges and target lock reticles."""
        state = ai_state
        state.reticle_angle = (state.reticle_angle + 4) % 360

        # Draw AI Status Banner
        badge_w, badge_h = 460, 30
        bx = SCREEN_WIDTH // 2 - badge_w // 2
        by = 8

        s = pygame.Surface((badge_w, badge_h), pygame.SRCALPHA)
        s.fill((10, 20, 35, 210))
        surface.blit(s, (bx, by))

        mode_col = CYAN if state.mode == "BALANCED" else (RED if state.mode == "COMBAT" else WIN_GREEN)
        pygame.draw.rect(surface, mode_col, (bx, by, badge_w, badge_h), 2, border_radius=6)

        status_text = f"🤖 HANDBUILT AI AUTOPILOT [{state.mode}] | {state.goal}"
        text_surf = FONT_SMALL.render(status_text, True, WHITE)
        surface.blit(text_surf, (bx + 10, by + 6))

        # Draw Lock-On Reticle over target
        if state.locked_target_rect:
            tr = state.locked_target_rect
            cx, cy = tr.centerx, tr.centery
            r_size = max(tr.width, tr.height) // 2 + 10

            c_col = RED if state.mode == "COMBAT" else CYAN
            pygame.draw.circle(surface, c_col, (cx, cy), r_size, 1)
            pygame.draw.line(surface, c_col, (cx - r_size - 6, cy), (cx + r_size + 6, cy), 1)
            pygame.draw.line(surface, c_col, (cx, cy - r_size - 6), (cx, cy + r_size + 6), 1)