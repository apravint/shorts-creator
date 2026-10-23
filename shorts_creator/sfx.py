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

    @staticmethod
    def generate_servo_motor(out_path: Union[str, Path], duration: float = 1.8, sample_rate: int = 44100) -> Path:
        """High-precision electric stepper motor and robotic servo hum."""
        out_path = Path(out_path)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        total_samples = int(sample_rate * duration)

        with wave.open(str(out_path), "wb") as wf:
            wf.setnchannels(2)
            wf.setsampwidth(2)
            wf.setframerate(sample_rate)

            for i in range(total_samples):
                t = i / sample_rate
                progress = t / duration
                env = math.sin(math.pi * progress) ** 0.5

                # Stepper motor dual harmonics with PWM frequency modulation
                base_freq = 190.0 + 35.0 * math.sin(2 * math.pi * 7.0 * t)
                harm1 = math.sin(2 * math.pi * base_freq * t)
                harm2 = math.sin(2 * math.pi * (base_freq * 2.8) * t) * 0.35
                whir = math.sin(2 * math.pi * 1420.0 * t) * 0.12

                val = max(-1.0, min(1.0, (harm1 + harm2 + whir) * env * 0.45))
                ival = int(val * 32767)
                wf.writeframes(struct.pack("<hh", ival, ival))

        return out_path

    @staticmethod
    def generate_pneumatic_slide(out_path: Union[str, Path], duration: float = 2.2, sample_rate: int = 44100) -> Path:
        """Pressurized pneumatic air release and mechanical piston slide."""
        out_path = Path(out_path)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        total_samples = int(sample_rate * duration)

        with wave.open(str(out_path), "wb") as wf:
            wf.setnchannels(2)
            wf.setsampwidth(2)
            wf.setframerate(sample_rate)

            last_noise = 0.0
            for i in range(total_samples):
                t = i / sample_rate
                progress = t / duration
                env = math.sin(math.pi * progress) ** 1.5

                # Air hiss filtered noise
                cutoff_freq = 800.0 + 1200.0 * (1.0 - progress)
                alpha = max(0.01, min(0.9, (2.0 * math.pi * cutoff_freq) / sample_rate))
                white = (random.random() * 2.0 - 1.0)
                last_noise = (1.0 - alpha) * last_noise + alpha * white

                # Low resonance slide tone
                slide_tone = math.sin(2 * math.pi * (85.0 - 25.0 * progress) * t) * 0.25

                val = max(-1.0, min(1.0, (last_noise * 0.4 + slide_tone) * env * 0.55))
                ival = int(val * 32767)
                wf.writeframes(struct.pack("<hh", ival, ival))

        return out_path

    @staticmethod
    def generate_magnetic_latch(out_path: Union[str, Path], duration: float = 0.6, sample_rate: int = 44100) -> Path:
        """Crisp high-tolerance mechanical magnetic latch snap and chassis lock."""
        out_path = Path(out_path)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        total_samples = int(sample_rate * duration)

        with wave.open(str(out_path), "wb") as wf:
            wf.setnchannels(2)
            wf.setsampwidth(2)
            wf.setframerate(sample_rate)

            for i in range(total_samples):
                t = i / sample_rate
                # High-frequency transient snap decaying in ~15ms
                click_env = math.exp(-t * 120.0)
                click = math.sin(2 * math.pi * 2400.0 * t) * click_env * 0.85

                # Metallic body ring decaying in ~120ms
                ring_env = math.exp(-t * 22.0)
                ring = (
                    math.sin(2 * math.pi * 920.0 * t) * 0.45
                    + math.sin(2 * math.pi * 1840.0 * t) * 0.25
                ) * ring_env

                # Sub-thud contact
                thud_env = math.exp(-t * 40.0)
                thud = math.sin(2 * math.pi * 65.0 * t) * thud_env * 0.5

                val = max(-1.0, min(1.0, click + ring + thud))
                ival = int(val * 32767)
                wf.writeframes(struct.pack("<hh", ival, ival))

        return out_path

    @classmethod
    def generate_mechanical_exploded_soundtrack(cls, out_path: Union[str, Path], total_duration: float = 19.0, sample_rate: int = 44100) -> Path:
        """Full choreographed multi-layer mechanical Foley soundtrack for CAD exploded view animations."""
        out_path = Path(out_path)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        total_samples = int(sample_rate * total_duration)

        # Buffer of mixed stereo samples
        left_buf = [0.0] * total_samples
        right_buf = [0.0] * total_samples

        def overlay_samples(samples_l, samples_r, start_sec, gain=1.0):
            start_idx = int(start_sec * sample_rate)
            for k in range(len(samples_l)):
                idx = start_idx + k
                if idx < total_samples:
                    left_buf[idx] += samples_l[k] * gain
                    right_buf[idx] += samples_r[k] * gain

        # 1. Subtle deep ambient drone throughout
        for i in range(total_samples):
            t = i / sample_rate
            # 48Hz / 96Hz sub drone
            drone = (math.sin(2 * math.pi * 48.0 * t) * 0.12 + math.sin(2 * math.pi * 96.0 * t) * 0.06)
            left_buf[i] += drone
            right_buf[i] += drone

        # Proportional timing across total_duration:
        # Phase 1: Expansion (0.05 to 0.25 of duration)
        # Phase 2: Telemetry / Inspection (0.20 to 0.70 of duration)
        # Phase 3: Contraction & Latching (0.65 to 0.88 of duration)
        # Phase 4: Final Hero Lock Impact (0.85 to 1.0 of duration)
        import tempfile
        with tempfile.TemporaryDirectory() as td:
            tmp_dir = Path(td)
            
            pneu_dur = max(1.0, total_duration * 0.25)
            pneu_path = cls.generate_pneumatic_slide(tmp_dir / "pneu.wav", duration=pneu_dur, sample_rate=sample_rate)
            with wave.open(str(pneu_path), "rb") as wf:
                n = wf.getnframes()
                raw = wf.readframes(n)
                data = struct.unpack(f"<{n*2}h", raw)
                overlay_samples([d / 32768.0 for d in data[0::2]], [d / 32768.0 for d in data[1::2]], total_duration * 0.04, gain=0.85)

            servo_dur = max(1.0, total_duration * 0.22)
            servo_path = cls.generate_servo_motor(tmp_dir / "servo1.wav", duration=servo_dur, sample_rate=sample_rate)
            with wave.open(str(servo_path), "rb") as wf:
                n = wf.getnframes()
                raw = wf.readframes(n)
                data = struct.unpack(f"<{n*2}h", raw)
                overlay_samples([d / 32768.0 for d in data[0::2]], [d / 32768.0 for d in data[1::2]], total_duration * 0.08, gain=0.65)

            telem_dur = max(1.5, total_duration * 0.50)
            telem_path = cls.generate_telemetry(tmp_dir / "telem.wav", duration=telem_dur, sample_rate=sample_rate)
            with wave.open(str(telem_path), "rb") as wf:
                n = wf.getnframes()
                raw = wf.readframes(n)
                data = struct.unpack(f"<{n*2}h", raw)
                overlay_samples([d / 32768.0 for d in data[0::2]], [d / 32768.0 for d in data[1::2]], total_duration * 0.22, gain=0.55)

            servo_rev_dur = max(1.0, total_duration * 0.20)
            servo_rev = cls.generate_servo_motor(tmp_dir / "servo_rev.wav", duration=servo_rev_dur, sample_rate=sample_rate)
            with wave.open(str(servo_rev), "rb") as wf:
                n = wf.getnframes()
                raw = wf.readframes(n)
                data = struct.unpack(f"<{n*2}h", raw)
                overlay_samples([d / 32768.0 for d in data[0::2]], [d / 32768.0 for d in data[1::2]], total_duration * 0.68, gain=0.7)

            latch_times = [total_duration * 0.74, total_duration * 0.79, total_duration * 0.84]
            for idx, latch_t in enumerate(latch_times):
                latch_path = cls.generate_magnetic_latch(tmp_dir / f"latch_{idx}.wav", duration=0.45, sample_rate=sample_rate)
                with wave.open(str(latch_path), "rb") as wf:
                    n = wf.getnframes()
                    raw = wf.readframes(n)
                    data = struct.unpack(f"<{n*2}h", raw)
                    overlay_samples([d / 32768.0 for d in data[0::2]], [d / 32768.0 for d in data[1::2]], latch_t, gain=0.9)

            impact_path = cls.generate_impact(tmp_dir / "impact.wav", duration=min(2.5, total_duration * 0.18), sample_rate=sample_rate)
            with wave.open(str(impact_path), "rb") as wf:
                n = wf.getnframes()
                raw = wf.readframes(n)
                data = struct.unpack(f"<{n*2}h", raw)
                overlay_samples([d / 32768.0 for d in data[0::2]], [d / 32768.0 for d in data[1::2]], total_duration * 0.86, gain=0.95)

        # Write final mastered 16-bit stereo WAV with soft limiter
        with wave.open(str(out_path), "wb") as wf:
            wf.setnchannels(2)
            wf.setsampwidth(2)
            wf.setframerate(sample_rate)

            # Soft clip / master normalize
            max_peak = max(max(abs(x) for x in left_buf), max(abs(y) for y in right_buf), 0.001)
            norm_mult = min(1.0, 0.92 / max_peak)

            packed = bytearray()
            for l_s, r_s in zip(left_buf, right_buf):
                # Soft tanh saturation
                l_clamped = math.tanh(l_s * norm_mult)
                r_clamped = math.tanh(r_s * norm_mult)
                packed.extend(struct.pack("<hh", int(l_clamped * 32767), int(r_clamped * 32767)))
            wf.writeframes(packed)

        return out_path

    @classmethod
    def generate_montage_sfx(
        cls,
        out_path: Union[str, Path],
        cut_times: List[float],
        total_duration: float,
        sample_rate: int = 44100
    ) -> Path:
        """
        Synthesizes a unified, multi-event Foley soundtrack synchronized to scene cuts:
        1. Sub-bass cinematic impact on the opening hook (t=0.0).
        2. Micro-whoosh camera transitions centered precisely on each B-roll cut point.
        3. Subtle riser escalation before the final climax if duration permits.
        """
        out_path = Path(out_path)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        total_samples = int(sample_rate * total_duration)

        left_buf = [0.0] * total_samples
        right_buf = [0.0] * total_samples

        def overlay_samples(samples_l, samples_r, start_sec, gain=1.0):
            start_idx = int(start_sec * sample_rate)
            for k in range(len(samples_l)):
                idx = start_idx + k
                if 0 <= idx < total_samples:
                    left_buf[idx] += samples_l[k] * gain
                    right_buf[idx] += samples_r[k] * gain

        import tempfile
        with tempfile.TemporaryDirectory() as td:
            tmp_dir = Path(td)

            # 1. Opening Hook Impact (t = 0.0s)
            hook_impact_dur = min(2.0, total_duration * 0.4)
            impact_file = cls.generate_impact(tmp_dir / "hook_impact.wav", duration=hook_impact_dur, sample_rate=sample_rate)
            with wave.open(str(impact_file), "rb") as wf:
                n = wf.getnframes()
                raw = wf.readframes(n)
                data = struct.unpack(f"<{n*2}h", raw)
                overlay_samples([d / 32768.0 for d in data[0::2]], [d / 32768.0 for d in data[1::2]], 0.0, gain=0.9)

            # 2. Dynamic Whooshes on every Cut Point
            whoosh_dur = 0.55
            whoosh_half = whoosh_dur / 2.0
            whoosh_file = cls.generate_whoosh(tmp_dir / "cut_whoosh.wav", duration=whoosh_dur, sample_rate=sample_rate)
            with wave.open(str(whoosh_file), "rb") as wf:
                n = wf.getnframes()
                raw = wf.readframes(n)
                data = struct.unpack(f"<{n*2}h", raw)
                whoosh_l = [d / 32768.0 for d in data[0::2]]
                whoosh_r = [d / 32768.0 for d in data[1::2]]

                for t_cut in cut_times:
                    # Only insert whoosh if cut is far enough from start and end
                    if 0.8 <= t_cut <= (total_duration - 0.6):
                        start_t = max(0.0, t_cut - whoosh_half)
                        overlay_samples(whoosh_l, whoosh_r, start_t, gain=0.65)

            # 3. Optional Tension Riser before climax / loop outro
            if total_duration >= 14.0:
                riser_dur = min(3.2, total_duration * 0.22)
                riser_start = max(1.0, total_duration - riser_dur - 0.8)
                riser_file = cls.generate_riser(tmp_dir / "climax_riser.wav", duration=riser_dur, sample_rate=sample_rate)
                with wave.open(str(riser_file), "rb") as wf:
                    n = wf.getnframes()
                    raw = wf.readframes(n)
                    data = struct.unpack(f"<{n*2}h", raw)
                    overlay_samples([d / 32768.0 for d in data[0::2]], [d / 32768.0 for d in data[1::2]], riser_start, gain=0.45)

        # Master normalize with soft limiter
        with wave.open(str(out_path), "wb") as wf:
            wf.setnchannels(2)
            wf.setsampwidth(2)
            wf.setframerate(sample_rate)

            max_peak = max(max(abs(x) for x in left_buf), max(abs(y) for y in right_buf), 0.001)
            norm_mult = min(1.0, 0.90 / max_peak)

            packed = bytearray()
            for l_s, r_s in zip(left_buf, right_buf):
                l_clamped = math.tanh(l_s * norm_mult)
                r_clamped = math.tanh(r_s * norm_mult)
                packed.extend(struct.pack("<hh", int(l_clamped * 32767), int(r_clamped * 32767)))
            wf.writeframes(packed)

        return out_path

