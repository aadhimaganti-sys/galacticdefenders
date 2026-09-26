import os
import sys
import pygame
from settings import BASE_DIR, ASSETS_DIR, SOUNDS_DIR, MUSIC_DIR
import state

class SoundManager:
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = SoundManager()
        return cls._instance

    def __init__(self):
        self.mixer_initialized = False
        self.sounds = {}
        self.current_music_track = None
        self.music_paused = False
        self._init_mixer()
        self.load_all_sounds()

    def _init_mixer(self):
        """Safely initializes pygame.mixer."""
        try:
            if not pygame.mixer.get_init():
                # 44.1kHz, 16-bit signed, 2 channels (stereo), 1024 buffer size for low latency
                pygame.mixer.pre_init(44100, -16, 2, 1024)
                pygame.mixer.init()
            pygame.mixer.set_num_channels(24) # allocate 24 channels for rich concurrent audio
            self.mixer_initialized = True
        except Exception as e:
            print(f"[SoundManager] Warning: Audio mixer could not be initialized: {e}")
            self.mixer_initialized = False

    def load_all_sounds(self):
        if not self.mixer_initialized:
            return

        # Ensure assets exist; if not, generate them
        if not os.path.exists(SOUNDS_DIR) or not os.path.exists(MUSIC_DIR):
            try:
                import assets_generator
                assets_generator.generate_all_assets(BASE_DIR)
            except Exception as e:
                print(f"[SoundManager] Error auto-generating assets: {e}")

        sfx_names = [
            "laser", "heavy_laser", "enemy_laser",
            "explosion_small", "explosion_medium", "explosion_boss",
            "powerup_spawn", "powerup_collect",
            "shield_hit", "shield_down",
            "level_up", "alarm_boss",
            "ui_click", "ui_hover", "dialogue_beep", "hack_toggle",
            "game_over", "victory",
            "warp_speed", "virus_laser", "plasma_cannon", "coin_pickup", "glitch_burst"
        ]

        pack = state.audio_settings.get("sound_pack", "classic")
        cyber_dir = os.path.join(SOUNDS_DIR, "cyber")

        for name in sfx_names:
            wav_path = None
            if pack == "cyber" and os.path.exists(cyber_dir):
                cand = os.path.join(cyber_dir, f"{name}.wav")
                if os.path.exists(cand):
                    wav_path = cand
            if not wav_path or not os.path.exists(wav_path):
                wav_path = os.path.join(SOUNDS_DIR, f"{name}.wav")

            if os.path.exists(wav_path):
                try:
                    snd = pygame.mixer.Sound(wav_path)
                    self.sounds[name] = snd
                except Exception as e:
                    print(f"[SoundManager] Failed to load sound {name}: {e}")

        self.update_volumes()

    def set_sound_pack(self, pack_name):
        """Switches active sound pack ('classic' or 'cyber') and reloads."""
        state.audio_settings["sound_pack"] = pack_name
        state.save_audio_config()
        self.load_all_sounds()
        self.play_sound("ui_click")
        self.play_sound("laser", 0.7)

    def update_volumes(self):
        """Updates SFX and Music volume based on global state settings."""
        if not self.mixer_initialized:
            return

        master = state.audio_settings.get("master_volume", 1.0)
        sfx_vol = state.audio_settings.get("sfx_volume", 0.8)
        music_vol = state.audio_settings.get("music_volume", 0.7)
        sfx_muted = state.audio_settings.get("sfx_muted", False)
        music_muted = state.audio_settings.get("music_muted", False)

        effective_sfx = 0.0 if sfx_muted else max(0.0, min(1.0, master * sfx_vol))
        effective_music = 0.0 if music_muted else max(0.0, min(1.0, master * music_vol))

        for snd in self.sounds.values():
            snd.set_volume(effective_sfx)

        try:
            pygame.mixer.music.set_volume(effective_music)
        except Exception:
            pass

    def play_sound(self, sound_name, volume_scale=1.0):
        """Plays a sound effect by name."""
        if not self.mixer_initialized:
            return None
        if state.audio_settings.get("sfx_muted", False):
            return None

        snd = self.sounds.get(sound_name)
        if snd:
            try:
                master = state.audio_settings.get("master_volume", 1.0)
                sfx_vol = state.audio_settings.get("sfx_volume", 0.8)
                vol = max(0.0, min(1.0, master * sfx_vol * volume_scale))
                snd.set_volume(vol)
                return snd.play()
            except Exception as e:
                print(f"[SoundManager] Error playing sound {sound_name}: {e}")
        return None

    def play_music(self, track_name, loop=True, fade_ms=300):
        """Plays a music track (e.g. 'menu_theme', 'battle_theme', 'boss_theme', 'story_theme', 'victory_theme')."""
        if not self.mixer_initialized:
            return

        if self.current_music_track == track_name and pygame.mixer.music.get_busy():
            return

        track_file = f"{track_name}.wav" if not track_name.endswith(".wav") else track_name
        track_path = os.path.join(MUSIC_DIR, track_file)

        if not os.path.exists(track_path):
            # Check if assets need generating
            try:
                import assets_generator
                assets_generator.generate_all_assets(BASE_DIR)
            except Exception:
                pass

        if os.path.exists(track_path):
            try:
                pygame.mixer.music.fadeout(fade_ms)
                pygame.mixer.music.load(track_path)
                self.update_volumes()
                loops = -1 if loop else 0
                pygame.mixer.music.play(loops=loops, fade_ms=fade_ms)
                self.current_music_track = track_name
                self.music_paused = False
            except Exception as e:
                print(f"[SoundManager] Error playing music track {track_name}: {e}")

    def stop_music(self, fade_ms=300):
        if not self.mixer_initialized:
            return
        try:
            pygame.mixer.music.fadeout(fade_ms)
            self.current_music_track = None
            self.music_paused = False
        except Exception:
            pass

    def pause_music(self):
        if not self.mixer_initialized:
            return
        try:
            pygame.mixer.music.pause()
            self.music_paused = True
        except Exception:
            pass

    def unpause_music(self):
        if not self.mixer_initialized:
            return
        try:
            pygame.mixer.music.unpause()
            self.music_paused = False
        except Exception:
            pass

# Global Sound Manager Helper Functions for clean imports
def play_sfx(name, volume_scale=1.0):
    return SoundManager.get_instance().play_sound(name, volume_scale)

def play_music(track_name, loop=True, fade_ms=300):
    SoundManager.get_instance().play_music(track_name, loop, fade_ms)

def stop_music(fade_ms=300):
    SoundManager.get_instance().stop_music(fade_ms)

def update_audio_volumes():
    SoundManager.get_instance().update_volumes()

def set_sound_pack(pack_name):
    SoundManager.get_instance().set_sound_pack(pack_name)
