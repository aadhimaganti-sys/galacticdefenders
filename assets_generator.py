import os
import math
import struct
import wave
import random

SAMPLE_RATE = 44100

def create_wave_file(filepath, frames, sample_rate=SAMPLE_RATE, channels=2):
    """Writes 16-bit PCM WAV file."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with wave.open(filepath, 'wb') as wav_file:
        wav_file.setnchannels(channels)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        
        # Pack frames into 16-bit signed integers
        raw_bytes = bytearray()
        for frame in frames:
            if channels == 1:
                val = max(-32767, min(32767, int(frame * 32767)))
                raw_bytes.extend(struct.pack('<h', val))
            elif channels == 2:
                if isinstance(frame, (tuple, list)):
                    left = max(-32767, min(32767, int(frame[0] * 32767)))
                    right = max(-32767, min(32767, int(frame[1] * 32767)))
                else:
                    val = max(-32767, min(32767, int(frame * 32767)))
                    left = right = val
                raw_bytes.extend(struct.pack('<hh', left, right))
        wav_file.writeframes(raw_bytes)

# --- Waveform Generators ---
def osc_sine(phase):
    return math.sin(phase)

def osc_square(phase, duty=0.5):
    return 1.0 if (phase % (2 * math.pi)) < (2 * math.pi * duty) else -1.0

def osc_saw(phase):
    normalized = (phase % (2 * math.pi)) / (2 * math.pi)
    return 2.0 * normalized - 1.0

def osc_triangle(phase):
    normalized = (phase % (2 * math.pi)) / (2 * math.pi)
    return 4.0 * abs(normalized - 0.5) - 1.0

def osc_noise():
    return random.uniform(-1.0, 1.0)

# --- SFX Synthesizers ---
def gen_laser(duration=0.18, start_freq=950, end_freq=180, sweep_curve=3.0, waveform='square'):
    total_samples = int(SAMPLE_RATE * duration)
    frames = []
    phase = 0.0
    for i in range(total_samples):
        t = i / total_samples
        freq = start_freq - (start_freq - end_freq) * (t ** sweep_curve)
        phase += 2 * math.pi * freq / SAMPLE_RATE
        
        # Envelope: sharp attack, linear decay
        env = max(0.0, 1.0 - t)
        if waveform == 'square':
            val = (osc_square(phase, 0.4) * 0.7 + osc_saw(phase) * 0.3) * env * 0.8
        elif waveform == 'saw':
            val = osc_saw(phase) * env * 0.8
        else:
            val = osc_sine(phase) * env * 0.8
            
        frames.append((val, val))
    return frames

def gen_heavy_laser(duration=0.28):
    total_samples = int(SAMPLE_RATE * duration)
    frames = []
    phase1 = 0.0
    phase2 = 0.0
    for i in range(total_samples):
        t = i / total_samples
        freq1 = 580 * math.exp(-6.0 * t) + 90
        freq2 = 420 * math.exp(-5.0 * t) + 60
        phase1 += 2 * math.pi * freq1 / SAMPLE_RATE
        phase2 += 2 * math.pi * freq2 / SAMPLE_RATE
        
        env = (1.0 - t) ** 1.5
        val = (osc_saw(phase1) * 0.5 + osc_square(phase2, 0.6) * 0.4 + osc_noise() * 0.15) * env * 0.9
        frames.append((val, val))
    return frames

def gen_enemy_laser(duration=0.22):
    total_samples = int(SAMPLE_RATE * duration)
    frames = []
    phase = 0.0
    for i in range(total_samples):
        t = i / total_samples
        # FM modulation
        mod_freq = 60 + 20 * math.sin(2 * math.pi * 35 * (i / SAMPLE_RATE))
        carrier_freq = 750 * (1.0 - t * 0.6) + mod_freq
        phase += 2 * math.pi * carrier_freq / SAMPLE_RATE
        env = (1.0 - t) ** 1.2
        val = osc_saw(phase) * env * 0.75
        frames.append((val, val))
    return frames

def gen_explosion(duration=0.4, low_freq=120, noise_mix=0.85):
    total_samples = int(SAMPLE_RATE * duration)
    frames = []
    phase = 0.0
    # simple 1-pole lowpass filter memory
    lp = 0.0
    for i in range(total_samples):
        t = i / total_samples
        freq = low_freq * (1.0 - t * 0.75) + 30
        phase += 2 * math.pi * freq / SAMPLE_RATE
        
        noise = osc_noise()
        lp += 0.25 * (noise - lp)
        
        env = (1.0 - t) ** 2.0
        sub_bass = osc_sine(phase) * 0.5
        val = (lp * noise_mix + sub_bass * (1.0 - noise_mix)) * env * 0.9
        # stereo panning variance
        pan_l = 0.8 + 0.2 * math.sin(t * 10)
        pan_r = 0.8 - 0.2 * math.sin(t * 10)
        frames.append((val * pan_l, val * pan_r))
    return frames

def gen_boss_explosion(duration=1.2):
    total_samples = int(SAMPLE_RATE * duration)
    frames = []
    phase = 0.0
    phase2 = 0.0
    lp = 0.0
    for i in range(total_samples):
        t = i / total_samples
        freq = 80 * math.exp(-3.0 * t) + 25
        phase += 2 * math.pi * freq / SAMPLE_RATE
        phase2 += 2 * math.pi * (freq * 1.5) / SAMPLE_RATE
        
        noise = osc_noise()
        lp += 0.18 * (noise - lp)
        
        env = (1.0 - t) ** 1.8
        rumble = (osc_triangle(phase) * 0.6 + osc_sine(phase2) * 0.4)
        val = (lp * 0.7 + rumble * 0.6) * env
        frames.append((val * 0.95, val * 0.95))
    return frames

def gen_powerup_spawn(duration=0.35):
    total_samples = int(SAMPLE_RATE * duration)
    frames = []
    phase = 0.0
    for i in range(total_samples):
        t = i / total_samples
        freq = 300 + 700 * (t ** 0.5)
        phase += 2 * math.pi * freq / SAMPLE_RATE
        env = math.sin(math.pi * t)
        val = (osc_sine(phase) * 0.7 + osc_triangle(phase * 2) * 0.3) * env * 0.8
        frames.append((val, val))
    return frames

def gen_powerup_collect(duration=0.45):
    # Ascending triad arpeggio (C5 -> E5 -> G5 -> C6)
    notes = [523.25, 659.25, 783.99, 1046.50]
    total_samples = int(SAMPLE_RATE * duration)
    samples_per_note = total_samples // len(notes)
    frames = []
    
    for note_idx, freq in enumerate(notes):
        phase = 0.0
        for i in range(samples_per_note):
            t = i / samples_per_note
            phase += 2 * math.pi * freq / SAMPLE_RATE
            env = (1.0 - t) ** 1.1
            val = (osc_square(phase, 0.3) * 0.5 + osc_sine(phase) * 0.5) * env * 0.75
            frames.append((val, val))
            
    while len(frames) < total_samples:
        frames.append((0.0, 0.0))
    return frames

def gen_shield_hit(duration=0.25):
    total_samples = int(SAMPLE_RATE * duration)
    frames = []
    phase = 0.0
    for i in range(total_samples):
        t = i / total_samples
        freq = 400 + 250 * math.sin(2 * math.pi * 40 * (i / SAMPLE_RATE))
        phase += 2 * math.pi * freq / SAMPLE_RATE
        env = (1.0 - t) ** 2.0
        val = (osc_sine(phase) * 0.7 + osc_noise() * 0.3) * env * 0.85
        frames.append((val, val))
    return frames

def gen_shield_down(duration=0.4):
    total_samples = int(SAMPLE_RATE * duration)
    frames = []
    phase = 0.0
    for i in range(total_samples):
        t = i / total_samples
        freq = 600 * (1.0 - t) + 80
        phase += 2 * math.pi * freq / SAMPLE_RATE
        env = (1.0 - t) ** 1.3
        val = osc_saw(phase) * env * 0.7
        frames.append((val, val))
    return frames

def gen_level_up(duration=0.6):
    # Fanfare: G4, C5, E5, G5
    notes = [392.00, 523.25, 659.25, 783.99]
    total_samples = int(SAMPLE_RATE * duration)
    samples_per_note = total_samples // len(notes)
    frames = []
    for note_idx, freq in enumerate(notes):
        phase1 = 0.0
        phase2 = 0.0
        for i in range(samples_per_note):
            t = i / samples_per_note
            phase1 += 2 * math.pi * freq / SAMPLE_RATE
            phase2 += 2 * math.pi * (freq * 1.005) / SAMPLE_RATE # chorus
            env = 1.0 - (t * 0.7) if note_idx == len(notes)-1 else (1.0 - t)
            val = (osc_square(phase1, 0.5) * 0.4 + osc_saw(phase2) * 0.4) * env * 0.75
            frames.append((val, val))
    while len(frames) < total_samples:
        frames.append((0.0, 0.0))
    return frames

def gen_alarm_boss(duration=0.5):
    total_samples = int(SAMPLE_RATE * duration)
    frames = []
    phase = 0.0
    for i in range(total_samples):
        t = i / total_samples
        freq = 440 + 330 * math.sin(2 * math.pi * 4 * t)
        phase += 2 * math.pi * freq / SAMPLE_RATE
        env = 0.85 if t < 0.85 else (1.0 - t) / 0.15
        val = osc_saw(phase) * env * 0.75
        frames.append((val, val))
    return frames

def gen_ui_click(duration=0.06):
    total_samples = int(SAMPLE_RATE * duration)
    frames = []
    phase = 0.0
    for i in range(total_samples):
        t = i / total_samples
        freq = 1200 * math.exp(-15.0 * t) + 200
        phase += 2 * math.pi * freq / SAMPLE_RATE
        env = (1.0 - t) ** 3.0
        val = (osc_triangle(phase) * 0.7 + osc_noise() * 0.3) * env * 0.8
        frames.append((val, val))
    return frames

def gen_ui_hover(duration=0.04):
    total_samples = int(SAMPLE_RATE * duration)
    frames = []
    phase = 0.0
    for i in range(total_samples):
        t = i / total_samples
        freq = 800 + 400 * t
        phase += 2 * math.pi * freq / SAMPLE_RATE
        env = math.sin(math.pi * t)
        val = osc_sine(phase) * env * 0.35
        frames.append((val, val))
    return frames

def gen_dialogue_beep(duration=0.05):
    total_samples = int(SAMPLE_RATE * duration)
    frames = []
    phase = 0.0
    freq = 700 + random.randint(-50, 50)
    for i in range(total_samples):
        t = i / total_samples
        phase += 2 * math.pi * freq / SAMPLE_RATE
        env = (1.0 - t) ** 2.0
        val = (osc_square(phase, 0.3) * 0.6) * env * 0.5
        frames.append((val, val))
    return frames

def gen_hack_toggle(duration=0.08):
    total_samples = int(SAMPLE_RATE * duration)
    frames = []
    phase = 0.0
    for i in range(total_samples):
        t = i / total_samples
        freq = 600 + 600 * (t ** 2)
        phase += 2 * math.pi * freq / SAMPLE_RATE
        env = (1.0 - t) ** 1.5
        val = osc_square(phase, 0.25) * env * 0.6
        frames.append((val, val))
    return frames

def gen_game_over(duration=1.4):
    # Sad descending minor tones: E4 -> D4 -> C4 -> B3
    notes = [329.63, 293.66, 261.63, 246.94]
    total_samples = int(SAMPLE_RATE * duration)
    samples_per_note = total_samples // len(notes)
    frames = []
    for note_idx, freq in enumerate(notes):
        phase = 0.0
        for i in range(samples_per_note):
            t = i / samples_per_note
            phase += 2 * math.pi * freq / SAMPLE_RATE
            env = (1.0 - t * 0.9)
            val = (osc_saw(phase) * 0.4 + osc_triangle(phase) * 0.4) * env * 0.75
            frames.append((val, val))
    while len(frames) < total_samples:
        frames.append((0.0, 0.0))
    return frames

def gen_victory(duration=1.6):
    # Triumphant chords arpeggio: C4 -> E4 -> G4 -> C5 -> G4 -> C5 (sustained)
    notes = [261.63, 329.63, 392.00, 523.25, 392.00, 523.25]
    total_samples = int(SAMPLE_RATE * duration)
    samples_per_note = total_samples // len(notes)
    frames = []
    for note_idx, freq in enumerate(notes):
        phase1 = 0.0
        phase2 = 0.0
        for i in range(samples_per_note):
            t = i / samples_per_note
            phase1 += 2 * math.pi * freq / SAMPLE_RATE
            phase2 += 2 * math.pi * (freq * 1.008) / SAMPLE_RATE
            env = (1.0 - (t * 0.5)) if note_idx == len(notes)-1 else (1.0 - t * 0.8)
            val = (osc_square(phase1, 0.5) * 0.4 + osc_saw(phase2) * 0.4) * env * 0.8
            frames.append((val, val))
    while len(frames) < total_samples:
        frames.append((0.0, 0.0))
    return frames

# --- Multi-track Music Track Generators ---

def note_to_freq(note_str):
    """Parses note name like C4, D#3, Ab4, or REST."""
    if note_str == "---" or note_str == "REST" or not note_str:
        return 0.0
    names = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
    alt_names = {"Db": "C#", "Eb": "D#", "Gb": "F#", "Ab": "G#", "Bb": "A#"}
    note = note_str[:-1]
    octave = int(note_str[-1])
    if note in alt_names:
        note = alt_names[note]
    semitone = names.index(note)
    midi_num = 12 + octave * 12 + semitone # C4 is 60
    return 440.0 * (2.0 ** ((midi_num - 69) / 12.0))

def render_sequence_music(bpm, pattern_bars, loop_count=2):
    """
    Renders multi-channel synthwave music:
    pattern_bars: list of dicts with keys 'bass', 'lead', 'chords', 'drums'
    Each is a list of 16-step notes per bar (16th notes).
    """
    beat_sec = 60.0 / bpm
    step_sec = beat_sec / 4.0
    step_samples = int(SAMPLE_RATE * step_sec)
    
    total_bars = len(pattern_bars) * loop_count
    total_samples = total_bars * 16 * step_samples
    left_channel = [0.0] * total_samples
    right_channel = [0.0] * total_samples
    
    # Delay line buffer for stereo echo
    delay_samples = int(SAMPLE_RATE * (beat_sec * 0.75)) # Dotted 8th delay
    echo_buffer = [0.0] * (total_samples + delay_samples)
    
    current_sample = 0
    
    for loop in range(loop_count):
        for bar in pattern_bars:
            bass_seq = bar.get('bass', ['---'] * 16)
            lead_seq = bar.get('lead', ['---'] * 16)
            chords_seq = bar.get('chords', ['---'] * 16)
            drum_seq = bar.get('drums', ['---'] * 16)
            
            for step in range(16):
                s_start = current_sample
                s_end = s_start + step_samples
                
                # --- 1. DRUMS CHANNEL ---
                drum_hit = drum_seq[step]
                if drum_hit == 'K': # Kick
                    for i in range(min(step_samples * 2, total_samples - s_start)):
                        t = i / (SAMPLE_RATE * 0.18)
                        if t < 1.0:
                            f = 140 * math.exp(-18.0 * t) + 40
                            k_val = osc_sine(2 * math.pi * f * (i / SAMPLE_RATE)) * ((1.0 - t) ** 2) * 0.7
                            idx = s_start + i
                            if idx < total_samples:
                                left_channel[idx] += k_val
                                right_channel[idx] += k_val
                elif drum_hit == 'S': # Snare
                    for i in range(min(step_samples * 2, total_samples - s_start)):
                        t = i / (SAMPLE_RATE * 0.16)
                        if t < 1.0:
                            s_noise = osc_noise() * ((1.0 - t) ** 1.8) * 0.45
                            s_tone = osc_triangle(2 * math.pi * 180 * (i / SAMPLE_RATE)) * ((1.0 - t) ** 3) * 0.35
                            val = s_noise + s_tone
                            idx = s_start + i
                            if idx < total_samples:
                                left_channel[idx] += val
                                right_channel[idx] += val
                elif drum_hit == 'H': # Hi-hat
                    for i in range(min(step_samples, total_samples - s_start)):
                        t = i / (SAMPLE_RATE * 0.04)
                        if t < 1.0:
                            h_val = (osc_noise() - 0.5 * osc_square(2 * math.pi * 6000 * (i / SAMPLE_RATE))) * (1.0 - t) * 0.22
                            idx = s_start + i
                            if idx < total_samples:
                                left_channel[idx] += h_val * 0.8
                                right_channel[idx] += h_val * 1.2
                elif drum_hit == 'O': # Open Hat
                    for i in range(min(step_samples * 2, total_samples - s_start)):
                        t = i / (SAMPLE_RATE * 0.12)
                        if t < 1.0:
                            h_val = osc_noise() * (1.0 - t) * 0.25
                            idx = s_start + i
                            if idx < total_samples:
                                left_channel[idx] += h_val
                                right_channel[idx] += h_val
                                
                # --- 2. BASS CHANNEL (Pulsing Saw/Triangle) ---
                bass_note = bass_seq[step]
                if bass_note != '---':
                    bfreq = note_to_freq(bass_note)
                    if bfreq > 0:
                        b_len = int(step_samples * 1.2)
                        phase = 0.0
                        for i in range(min(b_len, total_samples - s_start)):
                            t = i / b_len
                            phase += 2 * math.pi * bfreq / SAMPLE_RATE
                            env = (1.0 - t) ** 1.2
                            # Punchy bass with sub-bass
                            b_val = (osc_saw(phase) * 0.45 + osc_triangle(phase) * 0.45) * env * 0.5
                            idx = s_start + i
                            if idx < total_samples:
                                left_channel[idx] += b_val
                                right_channel[idx] += b_val

                # --- 3. CHORDS / PAD CHANNEL ---
                chord_note = chords_seq[step]
                if chord_note != '---':
                    c_freqs = [note_to_freq(n) for n in chord_note.split('+')]
                    c_len = int(step_samples * 3.8) # Sustain across steps
                    phases = [0.0] * len(c_freqs)
                    for i in range(min(c_len, total_samples - s_start)):
                        t = i / c_len
                        env = math.sin(math.pi * min(1.0, t * 1.2)) * (1.0 - t * 0.5)
                        c_val = 0.0
                        for c_idx, cf in enumerate(c_freqs):
                            if cf > 0:
                                phases[c_idx] += 2 * math.pi * cf / SAMPLE_RATE
                                c_val += (osc_saw(phases[c_idx]) * 0.5 + osc_sine(phases[c_idx] * 2) * 0.5)
                        c_val = (c_val / len(c_freqs)) * env * 0.22
                        idx = s_start + i
                        if idx < total_samples:
                            left_channel[idx] += c_val * 0.7
                            right_channel[idx] += c_val * 1.1

                # --- 4. LEAD MELODY CHANNEL (Vibrant Pulse with Vibrato) ---
                lead_note = lead_seq[step]
                if lead_note != '---':
                    lfreq = note_to_freq(lead_note)
                    if lfreq > 0:
                        l_len = int(step_samples * 1.8)
                        phase = 0.0
                        for i in range(min(l_len, total_samples - s_start)):
                            t = i / l_len
                            # Subtle vibrato
                            vib = 1.0 + 0.012 * math.sin(2 * math.pi * 6.0 * (i / SAMPLE_RATE))
                            phase += 2 * math.pi * (lfreq * vib) / SAMPLE_RATE
                            env = (1.0 - t * 0.7) ** 1.1
                            l_val = (osc_square(phase, 0.4) * 0.4 + osc_saw(phase) * 0.4) * env * 0.35
                            idx = s_start + i
                            if idx < total_samples:
                                left_channel[idx] += l_val
                                right_channel[idx] += l_val
                                # Send to echo delay buffer
                                echo_buffer[idx + delay_samples] += l_val * 0.35

                current_sample += step_samples

    # Mix echo buffer with feedback
    for i in range(total_samples):
        echo_val = echo_buffer[i]
        left_channel[i] += echo_val * 0.85
        right_channel[i] += echo_val * 0.65
        if i + delay_samples < len(echo_buffer):
            echo_buffer[i + delay_samples] += echo_val * 0.35 # Feedback

    # Master Normalization / Limiting
    frames = []
    for l, r in zip(left_channel, right_channel):
        # Soft-clip tanh limiting
        cl_l = math.tanh(l * 0.95)
        cl_r = math.tanh(r * 0.95)
        frames.append((cl_l, cl_r))
    return frames

def gen_menu_theme():
    # Ambient space synthwave at 116 BPM
    # Bar 1: Am (A2/C4/E4), Bar 2: F (F2/A3/C4), Bar 3: C (C3/G3/E4), Bar 4: G (G2/B3/D4)
    bpm = 116
    bars = [
        {
            'drums':  ['K','---','H','---','S','---','H','---','K','---','H','---','S','---','H','O'],
            'bass':   ['A2','---','A2','---','A2','---','A2','---','A2','---','A2','---','A2','---','G2','---'],
            'chords': ['A3+C4+E4','---','---','---','---','---','---','---','A3+C4+E4','---','---','---','---','---','---','---'],
            'lead':   ['E5','---','A5','---','B5','---','C6','---','B5','---','A5','---','E5','---','---','---']
        },
        {
            'drums':  ['K','---','H','---','S','---','H','---','K','---','H','---','S','---','H','O'],
            'bass':   ['F2','---','F2','---','F2','---','F2','---','F2','---','F2','---','F2','---','E2','---'],
            'chords': ['F3+A3+C4','---','---','---','---','---','---','---','F3+A3+C4','---','---','---','---','---','---','---'],
            'lead':   ['D5','---','F5','---','A5','---','C6','---','B5','---','A5','---','F5','---','---','---']
        },
        {
            'drums':  ['K','---','H','---','S','---','H','---','K','---','H','---','S','---','H','O'],
            'bass':   ['C3','---','C3','---','C3','---','C3','---','C3','---','C3','---','C3','---','B2','---'],
            'chords': ['C4+E4+G4','---','---','---','---','---','---','---','C4+E4+G4','---','---','---','---','---','---','---'],
            'lead':   ['G5','---','E5','---','C5','---','D5','---','E5','---','G5','---','A5','---','---','---']
        },
        {
            'drums':  ['K','---','H','---','S','---','H','---','K','---','H','K','S','---','H','O'],
            'bass':   ['G2','---','G2','---','G2','---','G2','---','G2','---','G2','---','G2','---','G2','---'],
            'chords': ['G3+B3+D4','---','---','---','---','---','---','---','G3+B3+D4','---','---','---','---','---','---','---'],
            'lead':   ['B5','---','A5','---','G5','---','D5','---','E5','---','G5','---','B5','---','---','---']
        }
    ]
    return render_sequence_music(bpm, bars, loop_count=2)

def gen_battle_theme():
    # Driving fast-paced battle action at 138 BPM in D Minor
    bpm = 138
    bars = [
        {
            'drums':  ['K','H','S','H','K','K','S','H','K','H','S','H','K','K','S','O'],
            'bass':   ['D2','D2','D2','D2','D2','D2','D2','D2','F2','F2','F2','F2','G2','G2','A2','A2'],
            'chords': ['D3+F3+A3','---','---','---','---','---','---','---','D3+F3+A3','---','---','---','---','---','---','---'],
            'lead':   ['D5','---','F5','---','A5','---','D6','---','C6','---','A5','---','F5','---','G5','A5']
        },
        {
            'drums':  ['K','H','S','H','K','K','S','H','K','H','S','H','K','K','S','O'],
            'bass':   ['Bb2','Bb2','Bb2','Bb2','Bb2','Bb2','Bb2','Bb2','C3','C3','C3','C3','A2','A2','A2','A2'],
            'chords': ['Bb3+D4+F4','---','---','---','---','---','---','---','C4+E4+G4','---','---','---','---','---','---','---'],
            'lead':   ['Bb5','---','D6','---','C6','---','A5','---','F5','---','E5','---','D5','---','E5','F5']
        },
        {
            'drums':  ['K','H','S','H','K','K','S','H','K','H','S','H','K','K','S','O'],
            'bass':   ['D2','D2','D2','D2','D2','D2','D2','D2','C3','C3','C3','C3','Bb2','Bb2','Bb2','Bb2'],
            'chords': ['D3+F3+A3','---','---','---','---','---','---','---','D3+F3+A3','---','---','---','---','---','---','---'],
            'lead':   ['A5','---','D6','---','E6','---','F6','---','E6','---','D6','---','C6','---','A5','---']
        },
        {
            'drums':  ['K','H','S','H','K','K','S','H','K','K','S','K','S','S','S','O'],
            'bass':   ['G2','G2','G2','G2','A2','A2','A2','A2','Bb2','Bb2','C3','C3','C#3','C#3','C#3','C#3'],
            'chords': ['G3+Bb3+D4','---','---','---','A3+C#4+E4','---','---','---','---','---','---','---','---','---','---','---'],
            'lead':   ['G5','---','Bb5','---','A5','---','C#6','---','D6','---','E6','---','F6','---','E6','---']
        }
    ]
    return render_sequence_music(bpm, bars, loop_count=2)

def gen_boss_theme():
    # Intense, alarming cyber boss track at 145 BPM in C Minor
    bpm = 145
    bars = [
        {
            'drums':  ['K','K','S','H','K','K','S','K','K','K','S','H','K','K','S','O'],
            'bass':   ['C2','C2','C2','C2','Eb2','Eb2','C2','C2','F#2','F#2','F#2','F#2','G2','G2','G2','G2'],
            'chords': ['C3+Eb3+G3','---','---','---','---','---','---','---','C3+Eb3+G3','---','---','---','---','---','---','---'],
            'lead':   ['C5','---','C5','---','Eb5','---','C5','---','F#5','---','F#5','---','G5','---','Eb5','---']
        },
        {
            'drums':  ['K','K','S','H','K','K','S','K','K','K','S','H','K','K','S','O'],
            'bass':   ['Ab2','Ab2','Ab2','Ab2','G2','G2','G2','G2','F2','F2','F2','F2','Eb2','Eb2','D2','D2'],
            'chords': ['Ab3+C4+Eb4','---','---','---','---','---','---','---','G3+B3+D4','---','---','---','---','---','---','---'],
            'lead':   ['Ab5','---','C6','---','B5','---','G5','---','F5','---','Eb5','---','D5','---','Eb5','D5']
        },
        {
            'drums':  ['K','K','S','H','K','K','S','K','K','K','S','H','K','K','S','O'],
            'bass':   ['C2','C2','Eb2','Eb2','F2','F2','F#2','F#2','G2','G2','Bb2','Bb2','C3','C3','C3','C3'],
            'chords': ['C3+Eb3+G3','---','---','---','---','---','---','---','C3+Eb3+G3','---','---','---','---','---','---','---'],
            'lead':   ['C6','---','Bb5','---','G5','---','F#5','---','F5','---','Eb5','---','C5','---','Eb5','F5']
        },
        {
            'drums':  ['K','K','S','K','K','K','S','K','K','S','K','S','K','S','S','O'],
            'bass':   ['B2','B2','B2','B2','B2','B2','B2','B2','B2','B2','B2','B2','B2','B2','B2','B2'],
            'chords': ['B3+D#4+F#4','---','---','---','---','---','---','---','B3+D#4+F#4','---','---','---','---','---','---','---'],
            'lead':   ['F#5','---','G5','---','A5','---','B5','---','C6','---','B5','---','D#6','---','C6','B5']
        }
    ]
    return render_sequence_music(bpm, bars, loop_count=2)

def gen_story_theme():
    # Mysterious cinematic sci-fi narrative theme at 105 BPM in E Minor
    bpm = 105
    bars = [
        {
            'drums':  ['K','---','---','---','S','---','---','---','K','---','---','---','S','---','---','H'],
            'bass':   ['E2','---','---','---','E2','---','---','---','E2','---','---','---','E2','---','---','---'],
            'chords': ['E3+G3+B3','---','---','---','---','---','---','---','E3+G3+B3','---','---','---','---','---','---','---'],
            'lead':   ['B4','---','E5','---','G5','---','F#5','---','E5','---','D5','---','B4','---','---','---']
        },
        {
            'drums':  ['K','---','---','---','S','---','---','---','K','---','---','---','S','---','---','H'],
            'bass':   ['C2','---','---','---','C2','---','---','---','C2','---','---','---','C2','---','---','---'],
            'chords': ['C3+E3+G3','---','---','---','---','---','---','---','C3+E3+G3','---','---','---','---','---','---','---'],
            'lead':   ['G4','---','C5','---','E5','---','D5','---','C5','---','B4','---','A4','---','---','---']
        },
        {
            'drums':  ['K','---','---','---','S','---','---','---','K','---','---','---','S','---','---','H'],
            'bass':   ['A2','---','---','---','A2','---','---','---','B2','---','---','---','B2','---','---','---'],
            'chords': ['A3+C4+E4','---','---','---','---','---','---','---','B3+D#4+F#4','---','---','---','---','---','---','---'],
            'lead':   ['E5','---','A5','---','C6','---','B5','---','A5','---','F#5','---','D#5','---','---','---']
        },
        {
            'drums':  ['K','---','---','---','S','---','---','---','K','---','K','---','S','---','H','O'],
            'bass':   ['E2','---','---','---','E2','---','---','---','E2','---','---','---','E2','---','---','---'],
            'chords': ['E3+G3+B3','---','---','---','---','---','---','---','E3+G3+B3','---','---','---','---','---','---','---'],
            'lead':   ['G5','---','F#5','---','E5','---','B4','---','E5','---','---','---','---','---','---','---']
        }
    ]
    return render_sequence_music(bpm, bars, loop_count=2)

def gen_victory_theme():
    # Grand celebratory victory track at 128 BPM in C Major
    bpm = 128
    bars = [
        {
            'drums':  ['K','H','S','H','K','H','S','H','K','H','S','H','K','K','S','O'],
            'bass':   ['C3','---','C3','---','E3','---','E3','---','G3','---','G3','---','C4','---','C4','---'],
            'chords': ['C4+E4+G4','---','---','---','---','---','---','---','C4+E4+G4','---','---','---','---','---','---','---'],
            'lead':   ['C5','---','E5','---','G5','---','C6','---','B5','---','G5','---','A5','---','B5','---']
        },
        {
            'drums':  ['K','H','S','H','K','H','S','H','K','H','S','H','K','K','S','O'],
            'bass':   ['F2','---','F2','---','A2','---','A2','---','G2','---','G2','---','B2','---','B2','---'],
            'chords': ['F3+A3+C4','---','---','---','---','---','---','---','G3+B3+D4','---','---','---','---','---','---','---'],
            'lead':   ['C6','---','D6','---','C6','---','B5','---','G5','---','E5','---','C5','---','---','---']
        }
    ]
    return render_sequence_music(bpm, bars, loop_count=2)

def generate_all_assets(base_dir=None):
    if base_dir is None:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        
    sounds_dir = os.path.join(base_dir, "assets", "sounds")
    music_dir = os.path.join(base_dir, "assets", "music")
    
    os.makedirs(sounds_dir, exist_ok=True)
    os.makedirs(music_dir, exist_ok=True)
    
    print(f"Generating SFX assets in {sounds_dir}...")
    sfx_manifest = {
        "laser.wav": gen_laser(),
        "heavy_laser.wav": gen_heavy_laser(),
        "enemy_laser.wav": gen_enemy_laser(),
        "explosion_small.wav": gen_explosion(0.25, 140, 0.9),
        "explosion_medium.wav": gen_explosion(0.45, 100, 0.8),
        "explosion_boss.wav": gen_boss_explosion(1.2),
        "powerup_spawn.wav": gen_powerup_spawn(),
        "powerup_collect.wav": gen_powerup_collect(),
        "shield_hit.wav": gen_shield_hit(),
        "shield_down.wav": gen_shield_down(),
        "level_up.wav": gen_level_up(),
        "alarm_boss.wav": gen_alarm_boss(),
        "ui_click.wav": gen_ui_click(),
        "ui_hover.wav": gen_ui_hover(),
        "dialogue_beep.wav": gen_dialogue_beep(),
        "hack_toggle.wav": gen_hack_toggle(),
        "game_over.wav": gen_game_over(),
        "victory.wav": gen_victory()
    }
    
    for filename, frames in sfx_manifest.items():
        filepath = os.path.join(sounds_dir, filename)
        create_wave_file(filepath, frames)
        print(f"  [+] Created sound effect: {filename}")
        
    print(f"Generating Music assets in {music_dir}...")
    music_manifest = {
        "menu_theme.wav": gen_menu_theme(),
        "battle_theme.wav": gen_battle_theme(),
        "boss_theme.wav": gen_boss_theme(),
        "story_theme.wav": gen_story_theme(),
        "victory_theme.wav": gen_victory_theme()
    }
    
    for filename, frames in music_manifest.items():
        filepath = os.path.join(music_dir, filename)
        create_wave_file(filepath, frames)
        print(f"  [+] Created music track: {filename}")
        
    print("All audio assets generated successfully!")

if __name__ == "__main__":
    generate_all_assets()
