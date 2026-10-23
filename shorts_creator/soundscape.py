"""
Multi-Layer Semantic Soundscape & Audio Mastering Engine for ShortsCreator.
Downmixes Voiceover + Background Music + Ambient Soundscapes + Hollywood SFX
with intelligent audio sidechain ducking and EBU R128 loudness normalization.
"""

import os
import math
import wave
import struct
import random
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional, Union

from .sfx import SoundEffectsSynthesizer


class SoundscapeEngine:
    """
    Synthesizes environmental room tone/atmospheres and downmixes multi-layered
    audio tracks into broadcast-ready studio soundscapes using FFmpeg.
    """

    @staticmethod
    def generate_procedural_ambient(ambient_type: str, duration: float, out_path: Union[str, Path]) -> Path:
        """
        Synthesizes procedural ambient acoustic textures without external audio files.
        Supported vibes: 'rain', 'keyboard', 'server_room', 'wind', 'room_tone'
        """
        out_path = Path(out_path)
        sample_rate = 44100
        total_samples = int(sample_rate * duration)
        out_path.parent.mkdir(parents=True, exist_ok=True)

        ambient_type = (ambient_type or "room_tone").lower().replace("-", "_").strip()

        with wave.open(str(out_path), "wb") as wf:
            wf.setnchannels(2)
            wf.setsampwidth(2)
            wf.setframerate(sample_rate)

            # 1. Rain / Storm Atmosphere (gentle low-pass noise with drops)
            if "rain" in ambient_type or "storm" in ambient_type:
                last_sample = 0.0
                for i in range(total_samples):
                    white = (random.random() * 2.0 - 1.0) * 0.16
                    last_sample = 0.94 * last_sample + 0.06 * white
                    tap = 0.22 * math.sin(i * 0.08) if random.random() < 0.0003 else 0.0
                    val = max(-1.0, min(1.0, last_sample + tap))
                    ival = int(val * 32767 * 0.5)
                    wf.writeframes(struct.pack("<hh", ival, ival))

            # 2. Developer Keyboard Clicks (rhythmic mechanical impulses)
            elif "typing" in ambient_type or "keyboard" in ambient_type or "code" in ambient_type:
                click_timer = 0
                click_duration = int(sample_rate * 0.015)
                next_click = random.randint(int(sample_rate * 0.08), int(sample_rate * 0.22))
                for i in range(total_samples):
                    sample = 0.0
                    if click_timer < click_duration:
                        env = 1.0 - (click_timer / click_duration)
                        freq = 2400 + (click_timer % 300) * 4
                        sample = math.sin(click_timer * freq * 2 * math.pi / sample_rate) * env * 0.32
                        click_timer += 1
                    else:
                        if i >= next_click:
                            click_timer = 0
                            next_click = i + random.randint(int(sample_rate * 0.07), int(sample_rate * 0.26))
                    val = max(-1.0, min(1.0, sample))
                    ival = int(val * 32767)
                    wf.writeframes(struct.pack("<hh", ival, ival))

            # 3. Server Room / Tech Datacenter (60Hz & 120Hz hum + cooling fans)
            elif "server" in ambient_type or "tech" in ambient_type or "cyber" in ambient_type:
                for i in range(total_samples):
                    t = i / sample_rate
                    hum60 = math.sin(2 * math.pi * 60 * t) * 0.07
                    hum120 = math.sin(2 * math.pi * 120 * t) * 0.035
                    air = (random.random() * 2.0 - 1.0) * 0.025
                    val = hum60 + hum120 + air
                    ival = int(val * 32767)
                    wf.writeframes(struct.pack("<hh", ival, ival))

            # 4. Subtle Wind / Atmospheric Room Tone
            else:
                for i in range(total_samples):
                    t = i / sample_rate
                    undulation = 0.5 + 0.5 * math.sin(2 * math.pi * 0.25 * t)
                    air = (random.random() * 2.0 - 1.0) * 0.035 * undulation
                    val = max(-1.0, min(1.0, air))
                    ival = int(val * 32767)
                    wf.writeframes(struct.pack("<hh", ival, ival))

        return out_path

    @staticmethod
    def mix_master_soundscape(
        narration_path: Union[str, Path],
        bg_music_path: Optional[Union[str, Path]],
        output_path: Union[str, Path],
        duration: float,
        ambient_vibe: Optional[str] = None,
        sfx_cue: Optional[str] = None,
        cut_timestamps: Optional[List[float]] = None,
        music_volume: float = 0.16,
        ambient_volume: float = 0.10,
        work_dir: Optional[Union[str, Path]] = None,
        use_sidechain: bool = True
    ) -> Path:
        """
        Downmixes Voiceover + BGM + Ambient Soundscape + Foley cues with FFmpeg.
        Applies sidechain compression ducking so speech stays crystal clear,
        and finalizes with EBU R128 loudness normalization.
        """
        output_path = Path(output_path)
        work_dir = Path(work_dir or output_path.parent)
        work_dir.mkdir(parents=True, exist_ok=True)

        inputs = ["-i", str(narration_path)]
        filter_inputs = ["[0:a]"]

        has_music = bg_music_path and os.path.isfile(str(bg_music_path))
        music_idx = None
        if has_music:
            inputs.extend(["-stream_loop", "-1", "-i", str(bg_music_path)])
            music_idx = len(inputs) // 2 - 1

        # Synthesize ambient layer if requested
        ambient_idx = None
        if ambient_vibe and ambient_vibe.lower() not in ("none", "off", "false"):
            amb_path = work_dir / f"ambient_{ambient_vibe}.wav"
            SoundscapeEngine.generate_procedural_ambient(ambient_vibe, duration + 2.0, amb_path)
            inputs.extend(["-stream_loop", "-1", "-i", str(amb_path)])
            ambient_idx = len(inputs) // 2 - 1

        # Synthesize montage sfx (whooshes on cuts + hook impact) or specific sfx cue
        sfx_idx = None
        if cut_timestamps and len(cut_timestamps) > 0:
            sfx_file = work_dir / "cue_montage.wav"
            SoundEffectsSynthesizer.generate_montage_sfx(
                sfx_file, cut_times=cut_timestamps, total_duration=duration
            )
            inputs.extend(["-i", str(sfx_file)])
            sfx_idx = len(inputs) // 2 - 1
        elif sfx_cue and sfx_cue.lower() in ("impact", "whoosh", "telemetry", "riser"):
            sfx_file = work_dir / f"cue_{sfx_cue}.wav"
            if sfx_cue == "impact":
                SoundEffectsSynthesizer.generate_impact(sfx_file, duration=min(2.5, duration))
            elif sfx_cue == "whoosh":
                SoundEffectsSynthesizer.generate_whoosh(sfx_file, duration=min(1.2, duration))
            elif sfx_cue == "telemetry":
                SoundEffectsSynthesizer.generate_telemetry(sfx_file, duration=min(3.0, duration))
            elif sfx_cue == "riser":
                SoundEffectsSynthesizer.generate_riser(sfx_file, duration=min(3.5, duration))
            inputs.extend(["-i", str(sfx_file)])
            sfx_idx = len(inputs) // 2 - 1

        # Construct FFmpeg audio filtergraph
        fc_parts = []
        mix_sources = []

        # Master Voiceover processing: 80Hz rumble cut + 3.2kHz presence
        fc_parts.append("[0:a]highpass=f=80,equalizer=f=3200:t=q:w=1.2:g=2.5[voice_eq]")

        if has_music and use_sidechain:
            fc_parts.append("[voice_eq]asplit=2[voice_main][voice_sc]")
            mix_sources.append("[voice_main]")
            # Sidechain compressor ducks music under voiceover
            fc_parts.append(
                f"[{music_idx}:a]volume={music_volume * 1.5:.2f}[music_pre];"
                f"[music_pre][voice_sc]sidechaincompress=threshold=0.03:ratio=12:attack=80:release=700[music]"
            )
            mix_sources.append("[music]")
        else:
            mix_sources.append("[voice_eq]")
            if has_music:
                fc_parts.append(f"[{music_idx}:a]volume={music_volume:.2f}[music]")
                mix_sources.append("[music]")

        if ambient_idx is not None:
            fc_parts.append(f"[{ambient_idx}:a]volume={ambient_volume:.2f}[amb]")
            mix_sources.append("[amb]")

        if sfx_idx is not None:
            fc_parts.append(f"[{sfx_idx}:a]volume=0.28[sfx]")
            mix_sources.append("[sfx]")

        fc_parts.append(
            f"{''.join(mix_sources)}amix=inputs={len(mix_sources)}:duration=first:dropout_transition=2,"
            f"loudnorm=I=-16:TP=-1.5:LRA=10[outa]"
        )

        filter_complex = ";".join(fc_parts)
        cmd = [
            "ffmpeg", "-y",
            *inputs,
            "-filter_complex", filter_complex,
            "-map", "[outa]",
            "-t", f"{duration:.3f}",
            "-c:a", "aac",
            "-b:a", "320k",
            "-ar", "48000",
            str(output_path)
        ]

        try:
            subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return output_path
        except Exception:
            # Fallback direct voice copy if complex mixing encounters edge case
            import shutil
            shutil.copyfile(str(narration_path), str(output_path))
            return output_path
