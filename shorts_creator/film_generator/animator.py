"""
2.5D Camera Animator & Motion Engine.
Animates 2D scene keyframes into living animated cinematic shots with:
- Dynamic Ken Burns camera zooms, pans, and sweeps
- Atmospheric color grading and film grain
- 16:9 Widescreen Cinema (1920x1080) and 9:16 Vertical (1080x1920) modes
"""

import os
import subprocess


def build_camera_filter(
    camera: str,
    frames: int,
    width: int,
    height: int,
    fps: int = 25
) -> str:
    """Build FFmpeg zoompan filter string for chosen camera movement."""
    camera = (camera or "zoom_in").lower()
    
    # Smooth speed coefficient based on shot length
    speed = 0.20 / max(1, frames)

    if camera == "zoom_out":
        # Pull back from 1.20x to 1.0x
        zp = f"zoompan=z='max(1.20-{speed}*on,1.0)':d={frames}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s={width}x{height}:fps={fps}"
    elif camera == "pan_left":
        # Drifts from right to left at 1.15x zoom
        zp = f"zoompan=z=1.15:d={frames}:x='(1.0-on/{frames})*(iw-iw/zoom)':y='ih/2-(ih/zoom/2)':s={width}x{height}:fps={fps}"
    elif camera == "pan_right":
        # Drifts from left to right at 1.15x zoom
        zp = f"zoompan=z=1.15:d={frames}:x='(on/{frames})*(iw-iw/zoom)':y='ih/2-(ih/zoom/2)':s={width}x{height}:fps={fps}"
    else:  # zoom_in (default)
        # Slow dramatic push from 1.0x to 1.22x
        zp = f"zoompan=z='min(zoom+{speed},1.22)':d={frames}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s={width}x{height}:fps={fps}"

    # Cinematic color grade: slight contrast pop + vibrant anime saturation
    grade = "eq=contrast=1.06:brightness=-0.02:saturation=1.12"
    return f"{zp},{grade}"


def animate_scene_shot(
    image_path: str,
    duration: float,
    output_video_path: str,
    camera: str = "zoom_in",
    aspect_ratio: str = "16:9",
    fps: int = 25
) -> str:
    """
    Render a single still image into a fully animated video shot of exact duration.
    """
    os.makedirs(os.path.dirname(output_video_path), exist_ok=True)
    duration = max(1.5, duration)
    frames = int(duration * fps)

    if aspect_ratio == "9:16":
        width, height = 1080, 1920
    else:
        width, height = 1920, 1080

    cam_filter = build_camera_filter(camera, frames, width, height, fps=fps)

    cmd = [
        "ffmpeg", "-y",
        "-loop", "1",
        "-i", image_path,
        "-vf", cam_filter,
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "19",
        "-pix_fmt", "yuv420p",
        "-t", str(duration),
        output_video_path
    ]

    try:
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        return output_video_path
    except Exception as e:
        print(f"[Error] Shot animation failed: {e}")
        return ""
