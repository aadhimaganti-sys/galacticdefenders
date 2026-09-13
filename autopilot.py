import math
from sprites import PowerUp # needed for isinstance check later if you want, but simple targeting works too.

class AdvancedAutoPilot:
    @staticmethod
    def run(player, all_sprites, player_bullets, asteroids=None, drones=None, powerups=None, enemy_bullets=None, boss=None):
        """
        An advanced AI wingman that handles smooth steering, priority targeting, and hazard evasion.
        """
        # Safely gather all objects currently on screen
        asts = asteroids if asteroids else []
        drns = drones if drones else []
        pwrs = powerups if powerups else []
        ebullets = enemy_bullets if enemy_bullets else []
        
        target_x = player.rect.centerx
        danger_x_offset = 0

        # --- SMART EVASION (Highest Priority) ---
        hazards = list(asts) + list(drns) + list(ebullets)
        if boss and getattr(boss, 'alive', lambda: False)():
            hazards.append(boss)

        closest_hazard = None
        min_dist = 200  # The AI's "Threat Detection" radius

        for h in hazards:
            dx = h.rect.centerx - player.rect.centerx
            dy = h.rect.centery - player.rect.centery
            dist = math.hypot(dx, dy)
            
            # If a hazard is close and positioned above us (falling towards us)
            if dist < min_dist and -200 < dy < 100: 
                min_dist = dist
                closest_hazard = h

        if closest_hazard:
            # Evasive Maneuver! Steer hard in the opposite direction
            if closest_hazard.rect.centerx >= player.rect.centerx:
                danger_x_offset = -player.base_speed * 3.5
            else:
                danger_x_offset = player.base_speed * 3.5
        
        # --- PRIORITY TARGETING ---
        target_obj = None
        if pwrs:
            target_obj = min(pwrs, key=lambda p: math.hypot(p.rect.centerx - player.rect.centerx, p.rect.centery - player.rect.centery))
        elif boss and getattr(boss, 'alive', lambda: False)():
            target_obj = boss
        elif drns:
            target_obj = min(drns, key=lambda d: math.hypot(d.rect.centerx - player.rect.centerx, d.rect.centery - player.rect.centery))
        elif asts:
            # Only target asteroids that are generally in front of us
            in_front = [a for a in asts if a.rect.bottom < player.rect.top + 50]
            if in_front:
                target_obj = min(in_front, key=lambda a: math.hypot(a.rect.centerx - player.rect.centerx, a.rect.centery - player.rect.centery))

        # If we have a target and aren't dodging, aim at it
        if target_obj and not closest_hazard:
            target_x = target_obj.rect.centerx

        # --- SMOOTH AUTONOMOUS MOVEMENT ---
        desired_x = target_x + danger_x_offset
        diff_x = desired_x - player.rect.centerx
        
        if abs(diff_x) > 5:
            # Physics-based smoothing (Lerp)
            speed = max(-player.base_speed * 1.5, min(player.base_speed * 1.5, diff_x * 0.15))
            player.speed_x = speed
        else:
            player.speed_x = 0

        # Lock Y to bottom to prevent the AI from drifting upward
        player.speed_y = 0

        # --- AUTO-FIRE ---
        if target_obj or closest_hazard:
            player.shoot(all_sprites, player_bullets)