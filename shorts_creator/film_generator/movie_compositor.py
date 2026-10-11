"""
Movie Compositor & Multi-Scene Assembler.
Combines animated scene shots, sequences character/narrator voiceovers,
generates cinematic orchestral BGM score, and burns subtitles into a finished film.
"""

import os
import subprocess
from typing import List, Dict, Any, Optional

ASSETS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "assets"))
FONTS_DIR = os.path.join(ASSETS_DIR, "fonts")


def format_ass_time(seconds: float) -> str:
    """Format seconds into ASS timestamp format: H:MM:SS.cs"""
    hrs = int(seconds // 3600)
    mins = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    centis = int(round((seconds - int(seconds)) * 100))
    if centis >= 100:
        centis = 99
    return f"{hrs}:{mins:02d}:{secs:02d}.{centis:02d}"


def create_movie_subtitles(
    scene_timings: List[Dict[str, Any]],
    output_ass_path: str,
    aspect_ratio: str = "16:9"
) -> str:
    """
    Generate clean, cinematic movie subtitle file.
    """
    font_name = "Mukta Malar"
    if aspect_ratio == "9:16":
        res_x, res_y = 1080, 1920
        font_size = 72
        margin_v = 480
        outline = 7
    else:
        res_x, res_y = 1920, 1080
        font_size = 54
        margin_v = 85
        outline = 4

    header = f"""[Script Info]
Title: Cinematic Animated Movie Subtitles
ScriptType: v4.00+
WrapStyle: 0
ScaledBorderAndShadow: yes
YCbCr Matrix: None
PlayResX: {res_x}
PlayResY: {res_y}

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,{font_name},{font_size},&H0000FFFF,&H000000FF,&H00000000,&H90000000,1,0,0,0,100,100,0,0,1,{outline},2,2,60,60,{margin_v},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    events = []
    for item in scene_timings:
        start_str = format_ass_time(item["start"])
        end_str = format_ass_time(item["end"])
        text = item["text"].strip()
        if text:
            events.append(f"Dialogue: 0,{start_str},{end_str},Default,,0,0,0,,{text}")

    os.makedirs(os.path.dirname(output_ass_path), exist_ok=True)
    with open(output_ass_path, "w", encoding="utf-8") as f:
        f.write(header + "\n".join(events) + "\n")

    return output_ass_path


def assemble_animated_movie(
    scene_video_paths: List[str],
    scene_audio_paths: List[str],
    scene_timings: List[Dict[str, Any]],
    output_movie_path: str,
    total_duration: float,
    bgm_path: Optional[str] = None,
    aspect_ratio: str = "16:9"
) -> str:
    """
    Stitch scenes, combine audio dialogue track, mix background music, and render final film.
    """
    os.makedirs(os.path.dirname(output_movie_path), exist_ok=True)
    session_dir = os.path.dirname(scene_video_paths[0])

    # 1. Concat Video Clips
    concat_txt_path = os.path.join(session_dir, "concat_videos.txt")
    with open(concat_txt_path, "w") as f:
        for p in scene_video_paths:
            f.write(f"file '{p}'\n")

    raw_video_path = os.path.join(session_dir, "stitched_video.mp4")
    cmd_concat_v = [
        "ffmpeg", "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", concat_txt_path,
        "-c", "copy",
        raw_video_path
    ]
    subprocess.run(cmd_concat_v, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

    # 2. Concat Scene Voiceovers
    concat_audio_txt = os.path.join(session_dir, "concat_audios.txt")
    with open(concat_audio_txt, "w") as f:
        for a in scene_audio_paths:
            f.write(f"file '{a}'\n")

    raw_audio_path = os.path.join(session_dir, "stitched_dialogue.mp3")
    cmd_concat_a = [
        "ffmpeg", "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", concat_audio_txt,
        "-c:a", "libmp3lame",
        "-b:a", "320k",
        "-ar", "48000",
        raw_audio_path
    ]
    subprocess.run(cmd_concat_a, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

    # 3. Create Subtitle Track
    sub_path = os.path.join(session_dir, "movie_subs.ass")
    create_movie_subtitles(scene_timings, sub_path, aspect_ratio=aspect_ratio)

    ass_escaped = sub_path.replace("\\", "/").replace(":", "\\:")
    fonts_dir_escaped = FONTS_DIR.replace("\\", "/").replace(":", "\\:")
    ass_filter = f"ass=filename={ass_escaped}:fontsdir={fonts_dir_escaped}:shaping=1"

    # 4. Final Compositing Pass with BGM Ducking & Subtitles
    cmd = ["ffmpeg", "-y"]
    cmd.extend(["-i", raw_video_path])
    cmd.extend(["-i", raw_audio_path])

    has_bgm = bgm_path and os.path.isfile(bgm_path)
    if has_bgm:
        cmd.extend(["-i", bgm_path])
        filter_complex = (
            f"[0:v]{ass_filter}[vout];"
            f"[1:a]highpass=f=75,equalizer=f=3000:t=q:w=1.2:g=2.2,loudnorm=I=-16:TP=-1.5:LRA=10[dialogue];"
            f"[2:a]lowpass=f=4500,volume=0.15[bgm];"
            f"[dialogue][bgm]amix=inputs=2:duration=first:dropout_transition=2[aout]"
        )
        cmd.extend([
            "-filter_complex", filter_complex,
            "-map", "[vout]",
            "-map", "[aout]"
        ])
    else:
        filter_complex = (
            f"[0:v]{ass_filter}[vout];"
            f"[1:a]highpass=f=75,equalizer=f=3000:t=q:w=1.2:g=2.2,loudnorm=I=-16:TP=-1.5:LRA=10[aout]"
        )
        cmd.extend([
            "-filter_complex", filter_complex,
            "-map", "[vout]",
            "-map", "[aout]"
        ])

    cmd.extend([
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "19",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "320k",
        "-ar", "48000",
        "-t", str(total_duration),
        output_movie_path
    ])

    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    return output_movie_path
