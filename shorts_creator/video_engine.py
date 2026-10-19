"""
FFmpeg Video Compositor for ShortsCreator AI (YouTube Shorts 9:16 & Cinema 2.39:1 / 16:9).
Combines vertical background video footage, burnt ASS subtitles with HarfBuzz complex shaping,
Shotcraft recipe optical filters, digital human talking avatar PiP, and multi-track audio
soundscapes with dynamic sidechain ducking and EBU R128 loudness normalization.
"""

import os
import subprocess
from pathlib import Path
from typing import Optional, List, Dict, Any

from .bg_manager import resolve_background_video
from .shotcraft import build_recipe_filter
from .soundscape import SoundscapeEngine
from .avatar import AvatarEngine
from .b_roll_engine import build_multi_beat_montage

ASSETS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "assets"))
FONTS_DIR = os.path.join(ASSETS_DIR, "fonts")


def build_procedural_background_filter(bg_type: str, duration: float, width: int = 1080, height: int = 1920) -> str:
    """Fallback FFmpeg filtergraph for procedural motion background."""
    if bg_type in ("cyber", "tech"):
        c0 = "0x090d16"
        c1 = "0x2563eb"
    elif bg_type == "fire":
        c0 = "0x1a0505"
        c1 = "0x991b1b"
    elif bg_type == "emerald":
        c0 = "0x022c22"
        c1 = "0x059669"
    elif bg_type == "gold":
        c0 = "0x1a1505"
        c1 = "0xd97706"
    else:  # cosmic / default
        c0 = "0x0a0f1d"
        c1 = "0x1e1b4b"

    return f"gradients=s={width}x{height}:d={duration}:r=30:c0={c0}:c1={c1}:x0=0:y0=0:x1={width}:y1={height},vignette=PI/3.2"


def assemble_shorts_video(
    voiceover_path: str,
    subtitle_ass_path: str,
    duration: float,
    output_path: str,
    topic: Optional[str] = None,
    sentences: Optional[List[str]] = None,
    boundaries: Optional[List[Dict[str, Any]]] = None,
    bg_video_path: Optional[str] = None,
    bg_type: str = "cosmic",
    bgm_path: Optional[str] = None,
    progress_bar: bool = True,
    progress_color: str = "0x00FFFF",
    recipe: Optional[str] = None,
    avatar_img: Optional[str] = None,
    is_cinema: bool = False,
    ambient_vibe: Optional[str] = None,
    sfx_cue: Optional[str] = None,
    visual_mode: str = "auto"
) -> str:
    """
    Assemble the complete short video with studio-grade audio mastering,
    cinematic optical grading, talking avatar PiP, and HarfBuzz typography.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    temp_dir = os.path.join(os.path.dirname(output_path), "temp_assembly")
    os.makedirs(temp_dir, exist_ok=True)

    width = 1080
    height = 1920
    fps = 30

    # 1. Master Audio with Multi-Layer Soundscape & Sidechain Ducking
    master_audio_path = os.path.join(temp_dir, "master_audio.aac")
    SoundscapeEngine.mix_master_soundscape(
        narration_path=voiceover_path,
        bg_music_path=bgm_path,
        output_path=master_audio_path,
        duration=duration,
        ambient_vibe=ambient_vibe,
        sfx_cue=sfx_cue,
        music_volume=0.16,
        ambient_volume=0.10,
        work_dir=temp_dir,
        use_sidechain=True
    )

    # 2. Build or resolve background video
    # If sentences are provided and no custom video is forced, build dynamic multi-beat B-roll montage!
    selected_bg_video = None
    if bg_video_path and os.path.isfile(bg_video_path):
        selected_bg_video = bg_video_path
    elif sentences and len(sentences) >= 1:
        stitched_montage = Path(temp_dir) / "stitched_broll_montage.mp4"
        try:
            build_multi_beat_montage(
                sentences=sentences,
                total_duration=duration,
                workspace_dir=Path(temp_dir),
                out_stitched_video=stitched_montage,
                global_topic=topic or "viral short",
                boundaries=boundaries,
                width=width,
                height=height,
                visual_mode=visual_mode
            )
            if stitched_montage.exists() and stitched_montage.stat().st_size > 10000:
                selected_bg_video = str(stitched_montage)
        except Exception as e:
            print(f"[Warning] Multi-beat montage fallback: {e}")

    if not selected_bg_video:
        selected_bg_video = resolve_background_video(
            topic=topic,
            custom_video=bg_video_path,
            theme_hint=bg_type
        )

    # 3. Subtitle filter with HarfBuzz complex shaping
    ass_escaped = subtitle_ass_path.replace("\\", "/").replace(":", "\\:")
    fonts_dir_escaped = FONTS_DIR.replace("\\", "/").replace(":", "\\:")
    ass_filter = f"ass=filename={ass_escaped}:fontsdir={fonts_dir_escaped}:shaping=1"

    # 4. Filters & Retention laser progress bar
    extra_filters = []

    # Apply Shotcraft recipe filter if selected (with video-stream safety)
    is_video_input = bool(selected_bg_video and os.path.isfile(selected_bg_video))
    recipe_filter = build_recipe_filter(
        recipe,
        width=width,
        height=height,
        fps=fps,
        duration=duration,
        for_video=is_video_input
    ) if recipe else None

    # Retention progress bar along bottom
    if progress_bar and duration > 0:
        bar_y = height - 16
        bar_filter = (
            f"drawbox=x=0:y={bar_y}:w=iw:h=16:color=black@0.45:t=fill,"
            f"drawbox=x=0:y={bar_y}:w='min(iw,iw*(t/{duration}))':h=16:color={progress_color}@0.95:t=fill"
        )
        extra_filters.append(bar_filter)

    # Cinema 2.39:1 scope overlay if requested
    if is_cinema:
        letterbox_h = int((height - (width * 16 / 9)) / 2) if height > width else int((height - (width / 2.39)) / 2)
        if letterbox_h > 0:
            extra_filters.append(f"drawbox=x=0:y=0:w=iw:h={letterbox_h}:color=black:t=fill")
            extra_filters.append(f"drawbox=x=0:y=ih-{letterbox_h}:w=iw:h={letterbox_h}:color=black:t=fill")

    extra_str = ("," + ",".join(extra_filters)) if extra_filters else ""

    cmd = ["ffmpeg", "-y"]

    # Video input
    if is_video_input:
        cmd.extend([
            "-stream_loop", "-1",
            "-i", selected_bg_video,
            "-t", str(duration)
        ])
        base_vfilter = (
            f"scale={width}:{height}:force_original_aspect_ratio=increase,"
            f"crop={width}:{height},setsar=1,"
            f"eq=brightness=-0.02:contrast=1.03"
        )
        if recipe_filter:
            video_filter = f"{base_vfilter},{recipe_filter},{ass_filter}{extra_str}"
        else:
            video_filter = f"{base_vfilter},{ass_filter}{extra_str}"
    else:
        bg_filter = build_procedural_background_filter(bg_type, duration, width, height)
        cmd.extend([
            "-f", "lavfi",
            "-i", bg_filter
        ])
        if recipe_filter:
            video_filter = f"{recipe_filter},{ass_filter}{extra_str}"
        else:
            video_filter = f"{ass_filter}{extra_str}"

    # Master audio input
    cmd.extend(["-i", master_audio_path])

    # Video & Audio mapping
    temp_rendered = os.path.join(temp_dir, "base_rendered.mp4") if avatar_img else output_path

    cmd.extend([
        "-vf", video_filter,
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "19",
        "-pix_fmt", "yuv420p",
        "-c:a", "copy",
        "-t", str(duration),
        temp_rendered
    ])

    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

    # 5. Composite talking avatar PiP if requested
    if avatar_img and os.path.isfile(avatar_img):
        avatar_vid = os.path.join(temp_dir, "avatar_talking.mp4")
        AvatarEngine.create_talking_avatar_video(
            avatar_img_path=avatar_img,
            speech_audio_path=voiceover_path,
            out_video_path=avatar_vid,
            duration=duration,
            width=540,
            height=540,
            fps=fps
        )
        AvatarEngine.overlay_presenter_pip(
            main_video_path=temp_rendered,
            avatar_video_path=avatar_vid,
            output_video_path=output_path,
            position="bottom_right",
            pip_size=340
        )

    return output_path
