"""
FFmpeg Video Compositor for YouTube Shorts (9:16 1080x1920).
Combines vertical background video footage, burnt ASS subtitles with HarfBuzz complex shaping,
studio broadcast vocal mastering (EBU R128 loudness normalization), and ducked BGM.
"""

import os
import subprocess
from typing import Optional
from .bg_manager import resolve_background_video

ASSETS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "assets"))
FONTS_DIR = os.path.join(ASSETS_DIR, "fonts")


def build_procedural_background_filter(bg_type: str, duration: float) -> str:
    """Fallback FFmpeg filtergraph for vertical 1080x1920 procedural motion background."""
    if bg_type in ("cyber", "tech"):
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

    return f"gradients=s=1080x1920:d={duration}:r=30:c0={c0}:c1={c1}:x0=0:y0=0:x1=1080:y1=1920,vignette=PI/3.2"


def assemble_shorts_video(
    voiceover_path: str,
    subtitle_ass_path: str,
    duration: float,
    output_path: str,
    topic: Optional[str] = None,
    bg_video_path: Optional[str] = None,
    bg_type: str = "cosmic",
    bgm_path: Optional[str] = None
) -> str:
    """
    Assemble the complete YouTube Short video using FFmpeg with Studio Broadcast Audio.
    Includes automatic background video matching and HarfBuzz complex typography shaping.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Resolve background video (e.g. NASA space galaxy or FPV drone loop)
    selected_bg_video = resolve_background_video(
        topic=topic,
        custom_video=bg_video_path,
        theme_hint=bg_type
    )

    # Prepare escaped paths for FFmpeg filtergraph
    ass_escaped = subtitle_ass_path.replace("\\", "/").replace(":", "\\:")
    fonts_dir_escaped = FONTS_DIR.replace("\\", "/").replace(":", "\\:")

    # ass filter with HarfBuzz complex shaping (shaping=1) and custom fontsdir
    ass_filter = f"ass=filename={ass_escaped}:fontsdir={fonts_dir_escaped}:shaping=1"

    cmd = ["ffmpeg", "-y"]

    # 1. Video Input: Real vertical background video with loop
    if selected_bg_video and os.path.isfile(selected_bg_video):
        cmd.extend([
            "-stream_loop", "-1",
            "-i", selected_bg_video,
            "-t", str(duration)
        ])
        # Auto-center crop to 9:16 vertical 1080x1920 + subtle contrast enhancement + burn subtitles
        video_filter = (
            f"scale=1080:1920:force_original_aspect_ratio=increase,"
            f"crop=1080:1920,setsar=1,"
            f"eq=brightness=-0.06:contrast=1.04,"
            f"{ass_filter}"
        )
    else:
        bg_filter = build_procedural_background_filter(bg_type, duration)
        cmd.extend([
            "-f", "lavfi",
            "-i", bg_filter
        ])
        video_filter = f"{ass_filter}"

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
        "-crf", "20",
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
