import pygame
import random
import math
from settings import *
import state

class Player(pygame.sprite.Sprite):
    def __init__(self, player_id=1, ship_type_key="default_jet"):
        super().__init__()
        self.player_id = player_id
        self.is_network_client = False
        self.network_keys = {}
        self.flame_flicker = 0

        self.ship_data = state.SHIP_TYPES.get(ship_type_key, state.SHIP_TYPES.get("default_jet", BASE_SHIP_TYPES["default_jet"]))
        self.core_body_width, self.core_body_height = 40, 60
        self.display_width, self.display_height = 80, 80
        self.image = pygame.Surface([self.display_width, self.display_height], pygame.SRCALPHA)
        self.rect = self.image.get_rect()

        self.jet_color = self.ship_data.get("color", PLAYER_COLORS[(self.player_id - 1) % len(PLAYER_COLORS)])
        self.wing_color = self.ship_data.get("wing_color", (max(0, self.jet_color[0] - 50), max(0, self.jet_color[1] - 50), max(0, self.jet_color[2] - 50)))

        self.rect.centerx = max(200, (SCREEN_WIDTH / 6) * (self.player_id % 6))
        self.rect.bottom = SCREEN_HEIGHT - 30

        self.speed_x, self.speed_y = 0, 0
        self.base_speed = self.ship_data.get("speed", 7)
        self.shoot_delay = 200

        my_unlocked = state.all_player_data.get(f"P{self.player_id}", {}).get("unlocked_powers", [])
        if "power_technic_servo" in my_unlocked and "power_technic_servo" in state.HELPER_TYPES: 
            self.shoot_delay = 100
        if "power_mbot_logic" in my_unlocked and "power_mbot_logic" in state.HELPER_TYPES: 
            self.base_speed += 3
        if "power_void_drive" in my_unlocked and "power_void_drive" in state.HELPER_TYPES: 
            self.base_speed += 2

        self.last_shot_time = pygame.time.get_ticks()
        self.num_blasters = self.ship_data.get("start_blasters", 1)
        self.score = 0
        self.next_powerup_trigger_score = 10
        self._update_appearance()
        
        self.power_up_active = False
        self.power_up_timer = 0
        self.power_up_duration = 5000
        
        self.shield_active = False
        self.shield_health = 0
        self.shield_timer = 0
        self.shield_duration = 10000

    def _update_appearance(self):
        self.image.fill((0, 0, 0, 0))
        img_center_x = self.display_width // 2
        body_top_y, body_bottom_y = 10, 70
        flame_len = 15 + self.flame_flicker
        
        pygame.draw.polygon(self.image, (255, 100, 0), [(img_center_x - 10, body_bottom_y), (img_center_x + 10, body_bottom_y), (img_center_x, body_bottom_y + flame_len)])
        pygame.draw.polygon(self.image, (255, 200, 0), [(img_center_x - 5, body_bottom_y), (img_center_x + 5, body_bottom_y), (img_center_x, body_bottom_y + flame_len - 5)])
        
        body_points = [(img_center_x, body_top_y), (img_center_x + self.core_body_width // 2, body_bottom_y), (img_center_x - self.core_body_width // 2, body_bottom_y)]
        pygame.draw.polygon(self.image, self.jet_color, body_points)
        pygame.draw.polygon(self.image, (min(255, self.jet_color[0] + 30), min(255, self.jet_color[1] + 30), min(255, self.jet_color[2] + 30)), body_points, 2)
        
        cockpit_points = [(img_center_x, body_top_y + 15), (img_center_x + 8, body_bottom_y - 25), (img_center_x - 8, body_bottom_y - 25)]
        pygame.draw.polygon(self.image, COCKPIT_GLASS, cockpit_points)
        pygame.draw.polygon(self.image, WHITE, cockpit_points, 1)

        if self.num_blasters > 1:
            pygame.draw.polygon(self.image, self.wing_color, [(img_center_x - 15, 30), (5, 40), (5, 60), (img_center_x - 15, 55)])
            pygame.draw.polygon(self.image, self.wing_color, [(img_center_x + 15, 30), (75, 40), (75, 60), (img_center_x + 15, 55)])

        offsets = {
            1: [0], 
            2: [-13, 13], 
            3: [-13, 0, 13], 
            4: [-15, -8, 8, 15], 
            5: [-17, -10, 0, 10, 17]
        }.get(self.num_blasters, [-17, -10, 0, 10, 17])
        
        for offset in offsets:
            blaster_rect = pygame.Rect(0, 0, 6, 12)
            blaster_rect.center = (img_center_x + offset, 18 if offset == 0 else 32)
            pygame.draw.rect(self.image, JET_BLASTER_COLOR, blaster_rect)
            pygame.draw.rect(self.image, DARK_GRAY, blaster_rect, 1)

    def update(self):
        self.flame_flicker = random.randint(-4, 4)
        self._update_appearance()

        # Keyboard Lock if Auto Pilot is steering
        if not state.ACTIVE_HACKS.get("Auto Pilot", False):
            keys = pygame.key.get_pressed()
            
            # --- 2.2 PLATFORMER MODE PHYSICS ---
            if state.ACTIVE_HACKS.get("Toggle Platformer", False):
                self.speed_x = self.base_speed if keys[pygame.K_d] else -self.base_speed if keys[pygame.K_a] else 0
                self.speed_y += state.GRAVITY 
                if keys[pygame.K_w] and self.rect.bottom >= SCREEN_HEIGHT - 30:
                    self.speed_y = state.JUMP_POWER
            else:
                self.speed_x, self.speed_y = 0, 0
                if self.is_network_client:
                    if self.network_keys.get("l"): self.speed_x = -self.base_speed
                    if self.network_keys.get("r"): self.speed_x = self.base_speed
                    if self.network_keys.get("u"): self.speed_y = -self.base_speed
                    if self.network_keys.get("d"): self.speed_y = self.base_speed
                elif not state.CHEAT_MENU_VISIBLE:
                    if self.player_id == 1:
                        if keys[pygame.K_a]: self.speed_x = -self.base_speed
                        if keys[pygame.K_d]: self.speed_x = self.base_speed
                        if keys[pygame.K_w]: self.speed_y = -self.base_speed
                        if keys[pygame.K_s]: self.speed_y = self.base_speed
                    elif self.player_id == 2:
                        if keys[pygame.K_LEFT]: self.speed_x = -self.base_speed
                        if keys[pygame.K_RIGHT]: self.speed_x = self.base_speed
                        if keys[pygame.K_UP]: self.speed_y = -self.base_speed
                        if keys[pygame.K_DOWN]: self.speed_y = self.base_speed

        self.rect.x += self.speed_x
        self.rect.y += self.speed_y
        
        if state.ACTIVE_HACKS.get("Toggle Platformer", False):
            if self.rect.bottom >= SCREEN_HEIGHT - 30:
                self.rect.bottom = SCREEN_HEIGHT - 30
                if self.speed_y > 0: self.speed_y = 0
            if self.rect.left < 0: self.rect.left = 0
            if self.rect.right > SCREEN_WIDTH: self.rect.right = SCREEN_WIDTH
        else:
            self.rect.clamp_ip(pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))

        # --- 2.2 ENGINE: ENGINE TRAIL PARTICLES ---
        if not state.ACTIVE_HACKS.get("Freeze Time", False):
            if self.speed_y < 0 or self.speed_x != 0 or not state.ACTIVE_HACKS.get("Toggle Platformer", False):
                if random.random() < 0.4:
                    # [x, y, dx, dy, life, max_life, color]
                    state.particle_list.append([
                        self.rect.centerx + random.uniform(-10, 10), 
                        self.rect.bottom, 
                        random.uniform(-0.5, 0.5), random.uniform(2, 5), 
                        20, 20, random.choice([(255, 100, 0), (255, 200, 0)])
                    ])

        now = pygame.time.get_ticks()
        if self.power_up_active and (now - self.power_up_timer > self.power_up_duration): 
            self.power_up_active = False
        if self.shield_active and (now - self.shield_timer > self.shield_duration): 
            self.shield_active = False

    def draw(self, surface):
        surface.blit(self.image, self.rect)
        if self.shield_active:
            sr = max(self.rect.width, self.rect.height) // 2 + 15
            ss = pygame.Surface((sr * 2, sr * 2), pygame.SRCALPHA)
            pygame.draw.circle(ss, SHIELD_COLOR, (sr, sr), sr)
            pygame.draw.circle(ss, WHITE, (sr, sr), sr, 2)
            surface.blit(ss, ss.get_rect(center=self.rect.center))

    def shoot(self, all_sprites_group, bullet_group):
        now = pygame.time.get_ticks()
        delay = self.shoot_delay / 2 if self.power_up_active else self.shoot_delay
        if now - self.last_shot_time > delay:
            self.last_shot_time = now
            offsets = [-15, 0, 15] if self.power_up_active else {
                1: [0], 2: [-13, 13], 3: [-13, 0, 13], 4: [-15, -8, 8, 15], 5: [-17, -10, 0, 10, 17]
            }.get(self.num_blasters, [0])
            
            for offset in offsets:
                b = Bullet(self.rect.centerx + offset, self.rect.top, self.player_id)
                all_sprites_group.add(b)
                bullet_group.add(b)

    def add_score(self, points):
        self.score += points
        while self.score >= self.next_powerup_trigger_score:
            self.num_blasters += 1
            self._update_appearance()
            self.next_powerup_trigger_score += 10

    def activate_triple_shot(self):
        self.power_up_active = True
        self.power_up_timer = pygame.time.get_ticks()

    def activate_shield(self):
        self.shield_active = True
        self.shield_health = 3
        self.shield_timer = pygame.time.get_ticks()

    def take_hit(self):
        if state.ACTIVE_HACKS.get("Noclip", False) or state.ACTIVE_HACKS.get("God Mode", False) or getattr(state, "ADMIN_GOD_MODE", False):
            return True
        if self.shield_active:
            self.shield_health -= 1
            if self.shield_health <= 0: 
                self.shield_active = False
            return True
        return False

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, owner_id):
        super().__init__()
        self.owner_id = owner_id
        self.image = pygame.Surface([12, 24], pygame.SRCALPHA)
        pygame.draw.ellipse(self.image, (255, 255, 100, 150), [0, 0, 12, 24])
        pygame.draw.ellipse(self.image, BULLET_YELLOW, [3, 4, 6, 16])
        self.rect = self.image.get_rect(centerx=x, bottom=y)
        self.speed_y = -15

    def update(self):
        self.rect.y += self.speed_y
        if self.rect.bottom < 0 or self.rect.top > SCREEN_HEIGHT: 
            self.kill()

class Asteroid(pygame.sprite.Sprite):
    def __init__(self, speed_multiplier=1.0, is_anomaly=False):
        super().__init__()
        self.size = random.choice([30, 40, 50, 60, 70])
        self.image = pygame.Surface([self.size, self.size], pygame.SRCALPHA)
        
        c = (255, 50, 150) if is_anomaly else (random.randint(60, 100),) * 3
        pygame.draw.circle(self.image, c, (self.size // 2, self.size // 2), self.size // 2 - 2)
        pygame.draw.circle(self.image, (40, 40, 40), (self.size // 2, self.size // 2), self.size // 2 - 2, 2)
        
        self.rect = self.image.get_rect(x=random.randint(0, SCREEN_WIDTH - self.size), y=random.randint(-150, -50))
        self.speed_x = random.choice([-2, -1, 0, 1, 2])
        self.speed_y = random.randint(2, 5) * speed_multiplier

    def update(self):
        if state.ACTIVE_HACKS.get("Freeze Time", False): 
            return
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y
        if self.rect.top > SCREEN_HEIGHT + 10: 
            self.rect.x = random.randint(0, SCREEN_WIDTH - self.size)
            self.rect.y = random.randint(-150, -50)

class SpinoffDrone(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface([40, 40], pygame.SRCALPHA)
        pygame.draw.polygon(self.image, CYAN, [(20, 40), (0, 0), (40, 0)])
        pygame.draw.polygon(self.image, WHITE, [(20, 40), (0, 0), (40, 0)], 2)
        
        self.rect = self.image.get_rect(x=random.randint(50, SCREEN_WIDTH - 50), y=random.randint(-100, -50))
        self.speed_y = random.randint(2, 4)
        self.speed_x = random.choice([-3, 3])
        self.last_shot = pygame.time.get_ticks()

    def update(self):
        if state.ACTIVE_HACKS.get("Freeze Time", False): 
            return
        self.rect.y += self.speed_y
        self.rect.x += self.speed_x
        if self.rect.left < 0 or self.rect.right > SCREEN_WIDTH: 
            self.speed_x *= -1
        if self.rect.top > SCREEN_HEIGHT: 
            self.kill()

    def shoot(self, all_sprites_group, enemy_bullet_group):
        if state.ACTIVE_HACKS.get("Freeze Time", False): 
            return
        now = pygame.time.get_ticks()
        if now - self.last_shot > 1500:
            self.last_shot = now
            b = Bullet(self.rect.centerx, self.rect.bottom, owner_id=99)
            b.speed_y = 6
            b.image = pygame.Surface([12, 24], pygame.SRCALPHA)
            b.image.fill(CYAN)
            all_sprites_group.add(b)
            enemy_bullet_group.add(b)

class Explosion(pygame.sprite.Sprite):
    def __init__(self, center):
        super().__init__()
        self.frame = 0
        self.image = pygame.Surface([80, 80], pygame.SRCALPHA)
        self.last_update = pygame.time.get_ticks()
        self.rect = self.image.get_rect(center=center)
        
        state.CAMERA_SHAKE = min(30, getattr(state, 'CAMERA_SHAKE', 0) + 8)
        
        # --- 2.2 ENGINE: SHATTER PARTICLES! ---
        for _ in range(25):
            state.particle_list.append([
                center[0], center[1], 
                random.uniform(-8, 8), random.uniform(-8, 8), 
                30, 30, random.choice([ORANGE, YELLOW, RED, WHITE])
            ])

    def update(self):
        if pygame.time.get_ticks() - self.last_update > 70:
            self.frame += 1
            self.image.fill((0, 0, 0, 0))
            if self.frame == 1: 
                pygame.draw.circle(self.image, ORANGE, (40, 40), 35)
                pygame.draw.circle(self.image, YELLOW, (40, 40), 20)
            elif self.frame == 2: 
                pygame.draw.circle(self.image, LOSE_RED, (40, 40), 20)
            elif self.frame > 2: 
                self.kill()

class PowerUp(pygame.sprite.Sprite):
    def __init__(self, center, power_type):
        super().__init__()
        self.power_type = power_type
        self.image = pygame.Surface([30, 30], pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=center)
        
        pygame.draw.circle(self.image, MAGENTA if power_type == "triple_shot" else CYAN, (15, 15), 15)
        pygame.draw.circle(self.image, WHITE, (15, 15), 15, 2)

    def update(self):
        self.rect.y += 3
        if self.rect.top > SCREEN_HEIGHT: 
            self.kill()

class Boss(pygame.sprite.Sprite):
    def __init__(self, health_override=500, color=BOSS_COLOR):
        super().__init__()
        self.health = health_override
        self.max_health = health_override
        self.boss_color = color
        
        self.image = pygame.Surface([200, 150], pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(SCREEN_WIDTH // 2, 100))
        self.speed_x = 3
        self.direction_x = 1
        self.last_shot_time = pygame.time.get_ticks()
        
        pygame.draw.rect(self.image, self.boss_color, (0, 0, 200, 150), border_radius=15)
        pygame.draw.rect(self.image, (150, 0, 0), (10, 10, 180, 130), border_radius=10)
        pygame.draw.circle(self.image, RED, (100, 75), 20)

    def update(self):
        if state.ACTIVE_HACKS.get("Freeze Time", False): 
            return
        self.rect.x += self.speed_x * self.direction_x
        if self.rect.left < 0 or self.rect.right > SCREEN_WIDTH: 
            self.direction_x *= -1

    def shoot(self, group, bullets, fire_rate=500):
        if state.ACTIVE_HACKS.get("Freeze Time", False): 
            return
        if pygame.time.get_ticks() - self.last_shot_time > fire_rate:
            self.last_shot_time = pygame.time.get_ticks()
            for offset in [-60, -20, 20, 60]:
                b = Bullet(self.rect.centerx + offset, self.rect.bottom, 0)
                b.speed_y = 7
                b.image = pygame.Surface([12, 24], pygame.SRCALPHA)
                b.image.fill(ORANGE)
                group.add(b)
                bullets.add(b)