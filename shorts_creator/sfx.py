"""
Hollywood Procedural Sound Effects Synthesizer for ShortsCreator AI.
Generates cinematic impacts, sub-bass drops, whoosh sweeps, telemetry beeps,
and dramatic risers using pure mathematical waveforms without external audio files.
"""

import math
import wave
import struct
import random
from pathlib import Path
from typing import Union


class SoundEffectsSynthesizer:
    """Procedurally synthesizes studio Hollywood SFX directly into WAV files."""

    @staticmethod
    def generate_impact(out_path: Union[str, Path], duration: float = 2.5, sample_rate: int = 44100) -> Path:
        """Cinematic cinematic sub-bass thud and cinematic impact."""
        out_path = Path(out_path)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        total_samples = int(sample_rate * duration)

        with wave.open(str(out_path), "wb") as wf:
            wf.setnchannels(2)
            wf.setsampwidth(2)
            wf.setframerate(sample_rate)

            for i in range(total_samples):
                t = i / sample_rate
                # Pitch drops from 120Hz to 32Hz
                freq = max(32.0, 120.0 * math.exp(-t * 6.5))
                env = math.exp(-t * 2.8)

                # Sub-bass fundamental + 2nd harmonic
                sub = math.sin(2 * math.pi * freq * t) * env * 0.75
                sub2 = math.sin(2 * math.pi * (freq * 0.5) * t) * env * 0.45

                # Initial acoustic transient punch
                transient = (random.random() * 2.0 - 1.0) * math.exp(-t * 35.0) * 0.35

                val = max(-1.0, min(1.0, sub + sub2 + transient))
                ival = int(val * 32767)
                wf.writeframes(struct.pack("<hh", ival, ival))

        return out_path

    @staticmethod
    def generate_whoosh(out_path: Union[str, Path], duration: float = 1.2, sample_rate: int = 44100) -> Path:
        """Fast dynamic camera whoosh sweep."""
        out_path = Path(out_path)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        total_samples = int(sample_rate * duration)

        with wave.open(str(out_path), "wb") as wf:
            wf.setnchannels(2)
            wf.setsampwidth(2)
            wf.setframerate(sample_rate)

            last_sample = 0.0
            for i in range(total_samples):
                t = i / sample_rate
                # Bell-shaped amplitude envelope
                progress = t / duration
                env = math.sin(math.pi * progress) ** 2

                # Center frequency sweeps up then down
                center_freq = 250.0 + 1600.0 * math.sin(math.pi * progress)
                alpha = max(0.01, min(0.9, (2.0 * math.pi * center_freq) / sample_rate))

                white = (random.random() * 2.0 - 1.0)
                last_sample = (1.0 - alpha) * last_sample + alpha * white

                val = max(-1.0, min(1.0, last_sample * env * 0.8))
                ival = int(val * 32767)
                wf.writeframes(struct.pack("<hh", ival, ival))

        return out_path

    @staticmethod
    def generate_telemetry(out_path: Union[str, Path], duration: float = 3.0, sample_rate: int = 44100) -> Path:
        """Subtle futuristic tech HUD telemetry and glitch beeps."""
        out_path = Path(out_path)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        total_samples = int(sample_rate * duration)

        with wave.open(str(out_path), "wb") as wf:
            wf.setnchannels(2)
            wf.setsampwidth(2)
            wf.setframerate(sample_rate)

            beep_timer = 0
            beep_duration = int(sample_rate * 0.04)
            current_freq = 1200.0
            next_beep = random.randint(int(sample_rate * 0.15), int(sample_rate * 0.45))

            for i in range(total_samples):
                val = 0.0
                if beep_timer < beep_duration:
                    env = math.sin(math.pi * (beep_timer / beep_duration))
                    val = math.sin(2 * math.pi * current_freq * (beep_timer / sample_rate)) * env * 0.22
                    beep_timer += 1
                else:
                    if i >= next_beep:
                        beep_timer = 0
                        current_freq = random.choice([880.0, 1100.0, 1320.0, 1760.0, 2200.0])
                        next_beep = i + random.randint(int(sample_rate * 0.15), int(sample_rate * 0.5))

                ival = int(max(-1.0, min(1.0, val)) * 32767)
                wf.writeframes(struct.pack("<hh", ival, ival))

        return out_path

    @staticmethod
    def generate_riser(out_path: Union[str, Path], duration: float = 3.5, sample_rate: int = 44100) -> Path:
        """Dramatically escalating cinematic tension riser build-up."""
        out_path = Path(out_path)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        total_samples = int(sample_rate * duration)

        with wave.open(str(out_path), "wb") as wf:
            wf.setnchannels(2)
            wf.setsampwidth(2)
            wf.setframerate(sample_rate)

            for i in range(total_samples):
                t = i / sample_rate
                norm_t = t / duration
                freq = 80.0 + 800.0 * (norm_t ** 2.2)
                env = (norm_t ** 1.8) * 0.65

                pulse = math.sin(2 * math.pi * (freq * 0.5) * t)
                harm = math.sin(2 * math.pi * freq * t) * 0.6
                shepard = math.sin(2 * math.pi * (freq * 1.5) * t) * 0.3

                val = max(-1.0, min(1.0, (pulse + harm + shepard) * env))
                ival = int(val * 32767)
                wf.writeframes(struct.pack("<hh", ival, ival))

        return out_path
