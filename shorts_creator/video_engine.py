"""
FFmpeg Video Compositor for YouTube Shorts (9:16 1080x1920).
Combines background video or procedural motion graphics, burnt ASS subtitles,
studio broadcast vocal mastering (EBU R128 loudness normalization), and ducked BGM.
"""

import os
import subprocess
from typing import Optional


def build_procedural_background_filter(bg_type: str, duration: float) -> str:
    """Generate FFmpeg filtergraph for vertical 1080x1920 procedural motion background."""
    if bg_type == "cyber":
        c0 = "0x090d16"
        c1 = "0x2563eb"
    elif bg_type == "fire":
        c0 = "0x1a0505"
        c1 = "0x991b1b"
    elif bg_type == "emerald":
        c0 = "0x022c22"
        c1 = "0x059669"
    else:  # cosmic / default
        c0 = "0x0a0f1d"
        c1 = "0x1e1b4b"

    # Animated gradient filter with vignette shading
    return f"gradients=s=1080x1920:d={duration}:r=30:c0={c0}:c1={c1}:x0=0:y0=0:x1=1080:y1=1920,vignette=PI/3.2"


def assemble_shorts_video(
    voiceover_path: str,
    subtitle_ass_path: str,
    duration: float,
    output_path: str,
    bg_video_path: Optional[str] = None,
    bg_type: str = "cosmic",
    bgm_path: Optional[str] = None
) -> str:
    """
    Assemble the complete YouTube Short video using FFmpeg with Studio Broadcast Audio.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    ass_escaped = subtitle_ass_path.replace("\\", "/").replace(":", "\\:")

    cmd = ["ffmpeg", "-y"]

    # 1. Video Input
    if bg_video_path and os.path.isfile(bg_video_path):
        cmd.extend([
            "-stream_loop", "-1",
            "-i", bg_video_path,
            "-t", str(duration)
        ])
        video_filter = f"scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,subtitles={ass_escaped}:fontsdir=/system/fonts"
    else:
        bg_filter = build_procedural_background_filter(bg_type, duration)
        cmd.extend([
            "-f", "lavfi",
            "-i", bg_filter
        ])
        video_filter = f"subtitles={ass_escaped}:fontsdir=/system/fonts"

    # 2. Audio Inputs
    cmd.extend(["-i", voiceover_path])
    has_bgm = bgm_path and os.path.isfile(bgm_path)
    if has_bgm:
        cmd.extend(["-i", bgm_path])

    # 3. Studio High-Quality Audio Mastering Filter Complex
    # Voice: High-pass 80Hz (remove mud) + 3.2kHz vocal presence EQ + EBU R128 Loudness Normalization (-16 LUFS)
    # BGM: Smooth 4kHz low-pass + ducking (-18dB / volume=0.14)
    # Master: 48,000Hz 320kbps Studio Master
    if has_bgm:
        filter_complex = (
            f"[0:v]{video_filter}[vout];"
            f"[1:a]highpass=f=80,equalizer=f=3200:t=q:w=1.2:g=2.5,loudnorm=I=-16:TP=-1.5:LRA=10[voice];"
            f"[2:a]lowpass=f=4000,volume=0.14[bgm];"
            f"[voice][bgm]amix=inputs=2:duration=first:dropout_transition=2[aout]"
        )
        cmd.extend([
            "-filter_complex", filter_complex,
            "-map", "[vout]",
            "-map", "[aout]"
        ])
    else:
        filter_complex = (
            f"[0:v]{video_filter}[vout];"
            f"[1:a]highpass=f=80,equalizer=f=3200:t=q:w=1.2:g=2.5,loudnorm=I=-16:TP=-1.5:LRA=10[aout]"
        )
        cmd.extend([
            "-filter_complex", filter_complex,
            "-map", "[vout]",
            "-map", "[aout]"
        ])

    # 4. Encoders & High Fidelity Broadcast Settings
    cmd.extend([
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "21",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "320k",
        "-ar", "48000",
        "-t", str(duration),
        output_path
    ])

    print(f"🎬 Rendering YouTube Short ({duration:.1f}s) to {output_path}...")
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    return output_path
