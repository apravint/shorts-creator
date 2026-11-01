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

_DETECTED_ENCODER_INFO: Optional[tuple] = None


def probe_hardware_encoder(encoder_name: str) -> bool:
    """Dry-run probe to test if an FFmpeg encoder works on this specific hardware."""
    try:
        cmd = [
            "ffmpeg", "-nostdin", "-y", "-v", "quiet",
            "-f", "lavfi", "-i", "color=c=black:s=64x64:d=0.05",
            "-c:v", encoder_name,
            "-f", "null", "-"
        ]
        res = subprocess.run(cmd, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=1.5)
        return res.returncode == 0
    except Exception:
        return False


def detect_optimal_video_encoder(preferred: str = "auto") -> tuple:
    """
    Detects hardware video encoders (NVIDIA NVENC, Apple VideoToolbox, Intel/AMD VAAPI, QSV)
    with seamless fallback to CPU libx264.
    Returns: (encoder_name, list_of_ffmpeg_flags)
    """
    global _DETECTED_ENCODER_INFO
    if preferred == "auto" and _DETECTED_ENCODER_INFO is not None:
        return _DETECTED_ENCODER_INFO

    pref = preferred.lower().strip() if preferred else "auto"

    if pref in ("nvenc", "h264_nvenc") or (pref == "auto" and probe_hardware_encoder("h264_nvenc")):
        info = ("h264_nvenc", ["-c:v", "h264_nvenc", "-preset", "p4", "-cq", "20", "-pix_fmt", "yuv420p"])
    elif pref in ("videotoolbox", "h264_videotoolbox") or (pref == "auto" and probe_hardware_encoder("h264_videotoolbox")):
        info = ("h264_videotoolbox", ["-c:v", "h264_videotoolbox", "-q:v", "65", "-pix_fmt", "yuv420p"])
    elif pref in ("vaapi", "h264_vaapi") or (pref == "auto" and probe_hardware_encoder("h264_vaapi")):
        info = ("h264_vaapi", ["-c:v", "h264_vaapi", "-qp", "20"])
    elif pref in ("qsv", "h264_qsv") or (pref == "auto" and probe_hardware_encoder("h264_qsv")):
        info = ("h264_qsv", ["-c:v", "h264_qsv", "-global_quality", "20", "-pix_fmt", "yuv420p"])
    else:
        info = ("libx264", ["-c:v", "libx264", "-preset", "fast", "-crf", "19", "-pix_fmt", "yuv420p"])

    if preferred == "auto":
        _DETECTED_ENCODER_INFO = info
    return info


def run_ffmpeg(cmd: List[str]) -> None:
    """Run FFmpeg, raising with its own error text instead of a bare exit code."""
    res = subprocess.run(cmd, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
    if res.returncode != 0:
        raise RuntimeError(f"FFmpeg failed: {res.stderr.strip()[-800:]}")


def build_progress_bar_graph(chain: str, duration: float, color: str, fps: int, width: int, thickness: int = 12) -> str:
    """
    Wrap a filter chain with a progress bar that grows across the video.
    drawbox evaluates its size only once, so the bar slides in as an overlay driven by per-frame time.
    """
    return (
        f"[in]{chain}[base];"
        f"color=c={color}@0.95:s={width}x{thickness}:r={fps},format=rgba[bar];"
        f"[base][bar]overlay=x='-W+W*t/{duration}':y=H-{thickness}:shortest=1[out]"
    )


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
    visual_mode: str = "auto",
    encoder: str = "auto",
    visual_queries: Optional[List[str]] = None
) -> str:
    """
    Assemble the complete short video with studio-grade audio mastering,
    cinematic optical grading, talking avatar PiP, and HarfBuzz typography.
    """
    output_path = os.path.abspath(output_path)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    temp_dir = os.path.join(os.path.dirname(output_path), "temp_assembly")
    os.makedirs(temp_dir, exist_ok=True)

    width = 1080
    height = 1920
    fps = 30

    # 1. Build or resolve background video & discover scene cut timestamps
    selected_bg_video = None
    cut_timestamps: List[float] = []

    if bg_video_path and os.path.isfile(bg_video_path):
        selected_bg_video = bg_video_path
    elif sentences and len(sentences) >= 1:
        stitched_montage = Path(temp_dir) / "stitched_broll_montage.mp4"
        try:
            montage_res = build_multi_beat_montage(
                sentences=sentences,
                total_duration=duration,
                workspace_dir=Path(temp_dir),
                out_stitched_video=stitched_montage,
                global_topic=topic or "viral short",
                boundaries=boundaries,
                width=width,
                height=height,
                visual_mode=visual_mode,
                visual_queries=visual_queries
            )
            if isinstance(montage_res, tuple):
                m_path, cuts = montage_res
                cut_timestamps = cuts or []
            else:
                m_path = montage_res
            if Path(m_path).exists() and Path(m_path).stat().st_size > 10000:
                selected_bg_video = str(m_path)
        except Exception as e:
            print(f"[Warning] Multi-beat montage fallback: {e}")

    if not selected_bg_video:
        selected_bg_video = resolve_background_video(
            topic=topic,
            custom_video=bg_video_path,
            theme_hint=bg_type
        )

    # 2. Master Audio with Multi-Layer Soundscape, Synchronized Transition SFX & Sidechain Ducking
    master_audio_path = os.path.join(temp_dir, "master_audio.aac")
    SoundscapeEngine.mix_master_soundscape(
        narration_path=voiceover_path,
        bg_music_path=bgm_path,
        output_path=master_audio_path,
        duration=duration,
        ambient_vibe=ambient_vibe,
        sfx_cue=sfx_cue,
        cut_timestamps=cut_timestamps,
        music_volume=0.16,
        ambient_volume=0.10,
        work_dir=temp_dir,
        use_sidechain=True
    )

    # 3. Subtitle filter with HarfBuzz complex shaping
    ass_escaped = subtitle_ass_path.replace("\\", "/").replace(":", "\\:")
    fonts_dir_escaped = FONTS_DIR.replace("\\", "/").replace(":", "\\:")
    ass_filter = f"ass=filename={ass_escaped}:fontsdir={fonts_dir_escaped}:shaping=1"

    # 4. Filters
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

    # Cinema 2.39:1 scope overlay if requested
    if is_cinema:
        letterbox_h = int((height - (width / 2.39)) / 2)
        if letterbox_h > 0:
            extra_filters.append(f"drawbox=x=0:y=0:w=iw:h={letterbox_h}:color=black:t=fill")
            extra_filters.append(f"drawbox=x=0:y=ih-{letterbox_h}:w=iw:h={letterbox_h}:color=black:t=fill")

    # Captions go last so they sit above the letterbox and any recipe grading
    overlay_chain = ",".join([*extra_filters, ass_filter])

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
            f"eq=contrast=1.06:saturation=1.12,vignette=PI/5"
        )
        if recipe_filter:
            video_filter = f"{base_vfilter},{recipe_filter},{overlay_chain}"
        else:
            video_filter = f"{base_vfilter},{overlay_chain}"
    else:
        bg_filter = build_procedural_background_filter(bg_type, duration, width, height)
        cmd.extend([
            "-f", "lavfi",
            "-i", bg_filter
        ])
        if recipe_filter:
            video_filter = f"{recipe_filter},{overlay_chain}"
        else:
            video_filter = overlay_chain

    # Retention progress bar along bottom
    if progress_bar and duration > 0:
        video_filter = build_progress_bar_graph(video_filter, duration, progress_color, fps, width)

    # Master audio input
    cmd.extend(["-i", master_audio_path])

    # Video & Audio mapping
    has_avatar = bool(avatar_img and os.path.isfile(avatar_img))
    if avatar_img and not has_avatar:
        print(f"[Warning] Avatar image not found, rendering without presenter: {avatar_img}")
    temp_rendered = os.path.join(temp_dir, "base_rendered.mp4") if has_avatar else output_path

    enc_name, enc_flags = detect_optimal_video_encoder(encoder)
    output_args = [
        "-vf", video_filter,
        "-c:a", "copy",
        "-movflags", "+faststart",
        "-t", str(duration),
        temp_rendered
    ]

    try:
        run_ffmpeg([*cmd, *enc_flags, *output_args])
    except RuntimeError as e:
        if enc_name == "libx264":
            raise
        print(f"[Warning] {enc_name} failed, retrying on CPU: {e}")
        _, cpu_flags = detect_optimal_video_encoder("cpu")
        run_ffmpeg([*cmd, *cpu_flags, *output_args])

    # 5. Composite talking avatar PiP if requested
    if has_avatar:
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
