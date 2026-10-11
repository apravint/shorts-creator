"""
Background Music (BGM) Manager & Procedural Synthesizer.
Supports custom audio tracks, pre-packaged asset tracks, and procedural cinematic vibes via FFmpeg.
"""

import os
import subprocess
from typing import Optional

ASSETS_BGM_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "assets", "bgm"))


def generate_procedural_bgm(output_path: str, duration: float, vibe: str = "ambient") -> str:
    """
    Generate a high-production ambient drone backing track using FFmpeg.
    Vibe options: 'ambient', 'suspense', 'cyber'
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    vibe = (vibe or "ambient").lower().strip()

    if vibe == "suspense":
        # Deep cinematic tension with dark sub-pulse
        audio_expr = (
            "0.08*sin(2*PI*55*t) + 0.05*sin(2*PI*77.78*t) + "
            "0.03*sin(2*PI*110*t*(1+0.004*sin(2*PI*1.2*t)))"
        )
        filter_str = f"lowpass=f=650,afade=t=in:ss=0:d=1.5,afade=t=out:st={max(0.1, duration - 1.5)}:d=1.5"
    elif vibe == "cyber":
        # Futuristic synth pulse
        audio_expr = (
            "0.05*sin(2*PI*130.81*t) + 0.04*sin(2*PI*196*t) + "
            "0.03*sin(2*PI*261.63*t) + 0.02*sin(2*PI*392*t)"
        )
        filter_str = f"lowpass=f=1200,afade=t=in:ss=0:d=1.5,afade=t=out:st={max(0.1, duration - 1.5)}:d=1.5"
    else:  # ambient default
        # Soft harmonic ambient synth chord (Root, Fifth, Octave at 110Hz, 165Hz, 220Hz, 330Hz)
        audio_expr = (
            "0.07*sin(2*PI*110*t) + 0.04*sin(2*PI*164.81*t) + "
            "0.03*sin(2*PI*220*t) + 0.02*sin(2*PI*329.63*t)"
        )
        filter_str = f"lowpass=f=850,afade=t=in:ss=0:d=1.5,afade=t=out:st={max(0.1, duration - 1.5)}:d=1.5"

    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi",
        "-i", f"aevalsrc={audio_expr}:d={int(duration + 4)}:s=48000",
        "-af", filter_str,
        "-c:a", "libmp3lame",
        "-b:a", "320k",
        "-ar", "48000",
        output_path
    ]

    try:
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        return output_path
    except Exception as e:
        print(f"[Warning] Failed to generate procedural BGM: {e}")
        return ""


def prepare_bgm_track(
    output_dir: str,
    duration: float,
    custom_bgm: Optional[str] = None,
    vibe: str = "ambient"
) -> Optional[str]:
    """
    Get or create background music track.
    1. Check for custom user-provided audio file
    2. Check assets/bgm folder for matched preset tracks
    3. Synthesize procedural atmospheric backing track
    """
    if custom_bgm and os.path.isfile(custom_bgm):
        return custom_bgm

    # Check assets/bgm for existing presets
    if os.path.isdir(ASSETS_BGM_DIR):
        files = [
            os.path.join(ASSETS_BGM_DIR, f)
            for f in os.listdir(ASSETS_BGM_DIR)
            if f.lower().endswith((".mp3", ".wav", ".m4a", ".aac"))
        ]
        if files:
            return files[0]

    # Generate procedural backing track
    bgm_file = os.path.join(output_dir, f"{vibe}_bgm.mp3")
    return generate_procedural_bgm(bgm_file, duration, vibe=vibe)
