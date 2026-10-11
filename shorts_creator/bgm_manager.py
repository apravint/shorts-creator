"""
Background Music (BGM) Manager & Synthesizer.
Supports custom audio files or generates procedural atmospheric lo-fi backing tracks via FFmpeg.
"""

import os
import subprocess
from typing import Optional


def generate_procedural_ambient_bgm(output_path: str, duration: float) -> str:
    """
    Generate a warm, cinematic ambient drone backing track using FFmpeg.
    Uses gentle harmonic chords and lowpass filtering.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Soft harmonic ambient synth chord (Root, Fifth, Octave at 110Hz, 165Hz, 220Hz)
    audio_expr = (
        "0.08*sin(2*PI*110*t) + 0.05*sin(2*PI*164.81*t) + "
        "0.04*sin(2*PI*220*t) + 0.03*sin(2*PI*329.63*t)"
    )
    
    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi",
        "-i", f"aevalsrc={audio_expr}:d={int(duration + 4)}:s=48000",
        "-af", f"lowpass=f=900,afade=t=in:ss=0:d=1.5,afade=t=out:st={duration - 1}:d=1.5",
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
    custom_bgm: Optional[str] = None
) -> Optional[str]:
    """
    Get or create background music track.
    """
    if custom_bgm and os.path.isfile(custom_bgm):
        return custom_bgm

    # Check assets/bgm for existing presets
    assets_bgm_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "bgm")
    if os.path.isdir(assets_bgm_dir):
        files = [os.path.join(assets_bgm_dir, f) for f in os.listdir(assets_bgm_dir) if f.endswith((".mp3", ".wav"))]
        if files:
            return files[0]

    # Generate procedural backing track
    bgm_file = os.path.join(output_dir, "ambient_bgm.mp3")
    return generate_procedural_ambient_bgm(bgm_file, duration)
